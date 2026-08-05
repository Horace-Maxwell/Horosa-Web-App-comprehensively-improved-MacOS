#!/usr/bin/env bash
# [FL-20260804-1] 增量部件可复现性自证门(horosa_repro_verify_v1)。
#
# 判据:**同一份源连打两次 payload,四个稳定部件的 sha 必须两两相同**。
#   稳定部件 = py-runtime / jdk-runtime / xuanshi-data / ephe-data
#   (web-app、java-lib、java-app 随本轮源码改动而变属正常,不在判据内。)
#
# 为什么需要它:增量更新的复用判据是「本地部件 sha == 新 manifest 部件 sha」。打包一旦
# 不可复现,内容一字未改的部件也会被判「变了」,每版每个用户全量重下。历史两层病根:
#   第一层(v3.6.2 已修) gzip 头 MTIME + 目录 mtime;
#   第二层(v3.7.3 本轮修) .pyc 文件 mtime / codesign --timestamp / CDS dump。
# 这两层都属于「肉眼看不出、只有比 sha 才现形」的病——故必须留成可执行护栏。
#
# 用法:bash scripts/verify_component_reproducibility.sh
#   耗时约 2×payload 打包(~20 分钟,第二轮因签名缓存命中会明显更快)。
#   需要 APPLE_SIGNING_IDENTITY(与真实发布同条件);缺失时签名段会被跳过,判据仍有效但
#   覆盖面变小(测不到签名缓存),此时脚本会显式提示。
set -uo pipefail
INSTALLER_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STABLE_PARTS=(py-runtime jdk-runtime xuanshi-data ephe-data)
WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT

read_shas() {
  /usr/bin/python3 - "$1" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
cs = d['components']
if isinstance(cs, dict):
    cs = [dict(name=k, **v) for k, v in cs.items()]
for c in cs:
    print(f"{c['name']}\t{c['sha256']}")
PY
}

if [ -z "${APPLE_SIGNING_IDENTITY:-}" ]; then
  echo "⚠️  APPLE_SIGNING_IDENTITY 未设置:签名段将被跳过,本次判据覆盖不到签名缓存。" >&2
fi

for round in A B; do
  echo "===== 第 ${round} 轮 payload 打包 ====="
  if ! bash "${INSTALLER_ROOT}/scripts/package_runtime_payload.sh" > "${WORK}/${round}.log" 2>&1; then
    echo "❌ 第 ${round} 轮打包失败,尾部日志:" >&2
    tail -20 "${WORK}/${round}.log" >&2
    exit 1
  fi
  cp "${INSTALLER_ROOT}/build/runtime/runtime-payload/components-lock.json" "${WORK}/lock-${round}.json"
done

read_shas "${WORK}/lock-A.json" | sort > "${WORK}/A.txt"
read_shas "${WORK}/lock-B.json" | sort > "${WORK}/B.txt"

RC=0
echo
echo "== 稳定部件可复现性判定 =="
for p in "${STABLE_PARTS[@]}"; do
  a="$(awk -F'\t' -v n="$p" '$1==n{print $2}' "${WORK}/A.txt")"
  b="$(awk -F'\t' -v n="$p" '$1==n{print $2}' "${WORK}/B.txt")"
  if [ -z "$a" ] || [ -z "$b" ]; then
    echo "  ❌ ${p}: 部件缺席(A=${a:0:12} B=${b:0:12})"; RC=1; continue
  fi
  if [ "$a" = "$b" ]; then
    echo "  ✅ ${p}: ${a:0:16} 恒等"
  else
    echo "  ❌ ${p}: A=${a:0:16} B=${b:0:16} —— 不可复现,该部件每版都会被全量重下"; RC=1
  fi
done

echo
if [ "$RC" = "0" ]; then
  echo "✅ 可复现性自证通过:四个稳定部件连打两次 sha 全部恒等。"
else
  echo "❌ 可复现性自证失败。排查顺序(按历史病根)：" >&2
  echo "   1) 该部件树里哪些文件两次内容不同 —— 解开两次部件包 diff -rq,看差异集形状;" >&2
  echo "   2) 内容全同却 sha 变 ⇒ 是 mtime 进了 tar 头(查是否有新的「打包时重新生成」的文件类型);" >&2
  echo "   3) 内容真变 ⇒ 找那一步后处理(签名/dump/编译),它必然落在部件 tar 之前。" >&2
fi
exit "${RC}"
