#!/bin/bash
# 增量更新端到端验证:部件合成树 ≡ 全量 tar 树(字节级,symlink 感知)。
#
# 用法:
#   bash scripts/verify_component_release.sh            # 本地模式:验 dist/ 产物
#   bash scripts/verify_component_release.sh <manifest-url>  # 远端模式:验已发布 release
#
# 验证面:
#   1) components-lock.json 与部件 tar 逐一 sha256 一致
#   2) 全部部件解压合成树 与 全量 tar 解压树 逐条目等价(文件内容 sha/symlink 指向/无多无漏;
#      components-lock.json 本身只在全量 tar 中,预期差异,单列白名单)
#   3) 远端模式加验:manifest v2 结构 + componentsLockSha256 + 各部件 url 可达
# 任一不符 exit 1。发版 runbook 中在 publish 后必跑远端模式。
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_ROOT="${INSTALLER_ROOT}/dist"
WORK="$(mktemp -d /tmp/horosa-comp-verify.XXXXXX)"
trap 'rm -rf "${WORK}"' EXIT

MANIFEST_URL="${1:-}"

if [ -n "${MANIFEST_URL}" ]; then
  echo "== 远端模式:${MANIFEST_URL}"
  curl -fsSL -H 'Cache-Control: no-cache' "${MANIFEST_URL}" -o "${WORK}/manifest.json"
  COMP_DIR="${WORK}/components"
  mkdir -p "${COMP_DIR}"
  FULL_TAR="${WORK}/runtime-full.tar.gz"
  python3 - "${WORK}/manifest.json" <<'PYURLS' > "${WORK}/urls.txt"
import json, sys
manifest = json.loads(open(sys.argv[1], encoding='utf-8').read())
if manifest.get('manifestVersion') != 2:
    raise SystemExit(f"manifestVersion != 2: {manifest.get('manifestVersion')}")
entries = list(manifest['platforms'].values())
entry = entries[0]
comps = entry.get('components') or []
if not comps:
    raise SystemExit('manifest 无 components')
if not entry.get('componentsLockUrl') or not entry.get('componentsLockSha256'):
    raise SystemExit('manifest 缺 componentsLock 字段')
print('LOCK', entry['componentsLockUrl'], entry['componentsLockSha256'])
print('FULL', entry['runtimeUrl'], entry.get('runtimeSha256') or '-')
for c in comps:
    print('COMP', c['url'], c['sha256'], c['file'])
PYURLS
  while read -r kind url sha rest; do
    case "${kind}" in
      LOCK) curl -fsSL "${url}" -o "${COMP_DIR}/components-lock.json"
            echo "${sha}  ${COMP_DIR}/components-lock.json" | shasum -a 256 -c - >/dev/null ;;
      FULL) echo "下载全量 tar(对照基准)…"; curl -fsSL "${url}" -o "${FULL_TAR}"
            [ "${sha}" = "-" ] || echo "${sha}  ${FULL_TAR}" | shasum -a 256 -c - >/dev/null ;;
      COMP) file="${rest}"; echo "下载部件 ${file}…"; curl -fsSL "${url}" -o "${COMP_DIR}/${file}"
            echo "${sha}  ${COMP_DIR}/${file}" | shasum -a 256 -c - >/dev/null ;;
    esac
  done < "${WORK}/urls.txt"
else
  echo "== 本地模式:${DIST_ROOT}"
  COMP_DIR="${DIST_ROOT}/components"
  FULL_TAR="$(ls "${DIST_ROOT}"/horosa-*runtime*-macos-arm64.tar.gz 2>/dev/null | head -1)"
  [ -f "${COMP_DIR}/components-lock.json" ] || { echo "缺 ${COMP_DIR}/components-lock.json(先跑 package_runtime_payload.sh)" >&2; exit 1; }
  [ -n "${FULL_TAR}" ] && [ -f "${FULL_TAR}" ] || { echo "缺全量 runtime tar" >&2; exit 1; }
fi

echo "== 1/3 lock 与部件 tar sha 逐一核对"
python3 - "${COMP_DIR}/components-lock.json" <<'PYSHA'
import hashlib, json, pathlib, sys
lock_path = pathlib.Path(sys.argv[1])
lock = json.loads(lock_path.read_text())
for c in lock['components']:
    f = lock_path.parent / c['file']
    h = hashlib.sha256()
    with open(f, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    if h.hexdigest() != c['sha256']:
        raise SystemExit(f"sha 不一致: {c['name']}")
    print(f"  {c['name']:14s} {c['sha256'][:12]} ✓")
PYSHA

echo "== 2/3 解压(全量 vs 部件合成)"
mkdir -p "${WORK}/full" "${WORK}/comp"
tar -xzf "${FULL_TAR}" -C "${WORK}/full" &
for f in "${COMP_DIR}"/horosa-comp-*.tar.gz; do
  tar -xzf "${f}" -C "${WORK}/comp"
done
wait

echo "== 3/3 全树等价(内容 sha + symlink 指向 + 无多无漏)"
python3 - "${WORK}/full/runtime-payload" "${WORK}/comp/runtime-payload" <<'PYDIFF'
import hashlib, os, pathlib, sys
full_root, comp_root = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])

def scan(root):
    out = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for n in dirnames + filenames:
            p = pathlib.Path(dirpath) / n
            rel = str(p.relative_to(root))
            if p.is_symlink():
                out[rel] = ('L', os.readlink(p))
            elif p.is_file():
                h = hashlib.sha256()
                with open(p, 'rb') as f:
                    for chunk in iter(lambda: f.read(1 << 20), b''):
                        h.update(chunk)
                out[rel] = ('F', h.hexdigest())
    return out

full, comp = scan(full_root), scan(comp_root)
# 预期差异:lock 只随全量 tar(增量应用后由客户端写新 lock 补齐)
# 「只随全量、不进部件」豁免(三处 lockstep:打包端 java_app 排除 + 打包零遗漏校验豁免 + 本处):
#   components-lock.json —— 切分产物真值,增量应用成功后由客户端写新 lock;
#   .app-cds.jsa —— AppCDS 预置档(42MB):进部件会把每版增量撑大 ~67%;
#     增量更新后旧档对新 exploded 失配由 JVM 自动忽略,首启后台自训再生。
EXPECTED_ONLY_FULL = {'components-lock.json', 'runtime/mac/bundle/boot-exploded/.app-cds.jsa'}
only_full = set(full) - set(comp) - EXPECTED_ONLY_FULL
only_comp = set(comp) - set(full)
mismatch = [k for k in set(full) & set(comp) if full[k] != comp[k]]
if only_full or only_comp or mismatch:
    print(f"only_full={sorted(only_full)[:5]}")
    print(f"only_comp={sorted(only_comp)[:5]}")
    print(f"mismatch={mismatch[:5]}")
    raise SystemExit('部件合成树与全量树不等价')
print(f"  {len(full)} 条目全等价(含 symlink 指向)✓")
PYDIFF

echo "verify_component_release: ALL GREEN ✅"
