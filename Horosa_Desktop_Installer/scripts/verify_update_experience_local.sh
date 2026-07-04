#!/usr/bin/env bash
# ============================================================================
# 假 release 全链路验证编排器(WS-1f)
#
# 用 dist/ 已产出的【真产物】制备一个「高版本假 release」,由本机 python http.server
# 供片;壳以 `--features update-url-override` 构建(发布二进制无此代码路径,
# 「出站仅 GitHub」铁律不破),HOROSA_UPDATE_BASE_OVERRIDE 把 manifest/runtime/部件
# 全部指到本机 → 四剧本在完全真实的 增量 diff/下载续传/解压应用 链路上跑。
# 断言依据 = updater 事件镜像日志(logs/updater-events.log,壳侧无条件落盘)。
#
# 用法:
#   bash scripts/verify_update_experience_local.sh            # 制备+起服务+打印剧本卡
#   bash scripts/verify_update_experience_local.sh --tamper   # 剧本 S2:篡改一个部件(sha 失配)
#   bash scripts/verify_update_experience_local.sh --restore  # 撤销篡改(恢复原部件)
#   bash scripts/verify_update_experience_local.sh --assert s1|s2|s3|s4   # 剧本断言(读事件日志)
#   bash scripts/verify_update_experience_local.sh --stop     # 停掉本机假 release 服务
# ============================================================================
set -euo pipefail
INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="${INSTALLER_ROOT}/dist"
FAKE="${INSTALLER_ROOT}/build/fake-release"
PORT="${HOROSA_FAKE_RELEASE_PORT:-8765}"
PID_FILE="${FAKE}/.http-server.pid"
BUNDLE_ID="$(python3 -c "import json;print(json.load(open('${INSTALLER_ROOT}/src-tauri/tauri.conf.json'))['identifier'])")"
EVENT_LOG="${HOME}/Library/Application Support/${BUNDLE_ID}/logs/updater-events.log"
MANIFEST_NAME="$(python3 -c "import json;print(json.load(open('${INSTALLER_ROOT}/config/release_config.json'))['updateManifestName'])")"

stop_server() {
  if [ -f "${PID_FILE}" ]; then
    kill "$(cat "${PID_FILE}")" 2>/dev/null || true
    rm -f "${PID_FILE}"
    echo "假 release 服务已停止"
  fi
}

assert_scenario() {
  local scen="$1"
  [ -f "${EVENT_LOG}" ] || { echo "FAIL: 事件日志不存在 ${EVENT_LOG}(壳没跑过更新?)" >&2; exit 1; }
  case "${scen}" in
    s1) # 增量命中:planning 带 incremental,最终 ready
      grep -q '"mode":"incremental"' "${EVENT_LOG}" || { echo "FAIL[s1]: 未见 incremental 计划事件" >&2; exit 1; }
      grep -q '"phase":"ready"' "${EVENT_LOG}" || { echo "FAIL[s1]: 未见 ready 事件" >&2; exit 1; }
      echo "PASS[s1] 增量命中:planning(incremental)→…→ready" ;;
    s2) # 篡改 sha → 增量失败降级全量:先 incremental 后出现 mode:full 的下载
      grep -q '"mode":"incremental"' "${EVENT_LOG}" || { echo "FAIL[s2]: 未见增量计划(先跑 --tamper 再在 app 里更新)" >&2; exit 1; }
      grep -q '"mode":"full"' "${EVENT_LOG}" || { echo "FAIL[s2]: 未见降级全量事件" >&2; exit 1; }
      echo "PASS[s2] 篡改部件 → 增量校验失败自动降级全量" ;;
    s3) # 下载中 kill -9 → 重启续传:事件带 resumedFrom
      grep -q '"resumedFrom"' "${EVENT_LOG}" || { echo "FAIL[s3]: 未见 resumedFrom 续传事件" >&2; exit 1; }
      echo "PASS[s3] kill -9 后断点续传(resumedFrom)" ;;
    s4) # FULL_ONLY:计划即全量
      grep -q '"mode":"full"' "${EVENT_LOG}" || { echo "FAIL[s4]: 未见全量模式事件" >&2; exit 1; }
      echo "PASS[s4] HOROSA_UPDATE_FULL_ONLY 强制全量" ;;
    *) echo "未知剧本: ${scen}(可选 s1|s2|s3|s4)" >&2; exit 1 ;;
  esac
}

case "${1:-}" in
  --stop) stop_server; exit 0 ;;
  --assert) assert_scenario "${2:?用法: --assert s1|s2|s3|s4}"; exit 0 ;;
  --tamper)
    COMP_TAR="$(ls "${FAKE}/components"/comp-web-app.tar.gz 2>/dev/null || ls "${FAKE}/components"/comp-*.tar.gz 2>/dev/null | head -1)"
    [ -n "${COMP_TAR}" ] || { echo "先跑默认模式制备假 release" >&2; exit 1; }
    cp "${COMP_TAR}" "${COMP_TAR}.orig"
    printf 'tampered' >> "${COMP_TAR}"
    echo "已篡改 $(basename "${COMP_TAR}")(sha 失配)——app 里触发更新应走: 增量下载→部件校验失败→自动降级全量"
    exit 0 ;;
  --restore)
    for f in "${FAKE}/components"/*.orig; do
      [ -f "$f" ] && mv "$f" "${f%.orig}" && echo "已恢复 $(basename "${f%.orig}")"
    done
    exit 0 ;;
esac

# ── 制备假 release ──────────────────────────────────────────────────────────
for need in "${DIST}/${MANIFEST_NAME}" "${DIST}/components/components-lock.json"; do
  [ -e "${need}" ] || { echo "缺 ${need}:先跑 build_desktop_release.sh 产出 dist" >&2; exit 1; }
done
rm -rf "${FAKE}"
mkdir -p "${FAKE}/components"
cp "${DIST}/${MANIFEST_NAME}" "${FAKE}/"
cp "${DIST}/components/"* "${FAKE}/components/"
# 大件按需:runtime tar / app zip 在剧本 S2 降级全量、app 更新时才被拉
for big in "${DIST}"/horosa-runtime-*.tar.gz "${DIST}"/*.zip; do
  [ -f "${big}" ] && ln -f "${big}" "${FAKE}/$(basename "${big}")" 2>/dev/null || true
done

# manifest 抬版本 + 全部 URL 指回本机(components url 保相对文件名)
FAKE_ENV="${FAKE}" PORT_ENV="${PORT}" MANIFEST_ENV="${MANIFEST_NAME}" python3 - <<'PYFAKE'
import json, os, pathlib
fake = pathlib.Path(os.environ['FAKE_ENV'])
port = os.environ['PORT_ENV']
manifest_path = fake / os.environ['MANIFEST_ENV']
manifest = json.loads(manifest_path.read_text())
manifest['version'] = '99.0.0'
manifest['tag'] = 'v99.0.0'
base = f'http://127.0.0.1:{port}'
for entry in (manifest.get('platforms') or {}).values():
    for key in ('pkgUrl', 'appUrl', 'runtimeUrl'):
        if entry.get(key):
            entry[key] = f"{base}/{entry[key].rsplit('/', 1)[-1]}"
    entry['runtimeVersion'] = '99.0.0-runtime1'
    if entry.get('componentsLockUrl'):
        entry['componentsLockUrl'] = f"{base}/components/components-lock.json"
    for c in entry.get('components') or []:
        c['url'] = f"{base}/components/{c['file']}"
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
# lock 的 runtimeVersion 同步抬(客户端身份一致性闸)
lock_path = fake / 'components' / 'components-lock.json'
lock = json.loads(lock_path.read_text())
lock['runtimeVersion'] = '99.0.0-runtime1'
lock_path.write_text(json.dumps(lock, ensure_ascii=False) + '\n')
print('fake manifest ready: v99.0.0')
PYFAKE

# (manifest 分离签名机制已整体移除——假 release 无需重签)

# ── 起本机服务 ──────────────────────────────────────────────────────────────
stop_server
(cd "${FAKE}" && python3 -m http.server "${PORT}" --bind 127.0.0.1 >/dev/null 2>&1 &
 echo $! > "${PID_FILE}")
sleep 0.5
curl -sf "http://127.0.0.1:${PORT}/${MANIFEST_NAME}" >/dev/null || { echo "假 release 服务未起来" >&2; exit 1; }
echo "假 release 服务: http://127.0.0.1:${PORT}(pid $(cat "${PID_FILE}"))"

# ── 构建 override 壳(debug,发布链绝不带此 feature) ─────────────────────────
echo "构建 override 壳(--features update-url-override)…"
cargo build --manifest-path "${INSTALLER_ROOT}/src-tauri/Cargo.toml" --features update-url-override 2>&1 | tail -2
BIN="${INSTALLER_ROOT}/src-tauri/target/debug/horosa-desktop-installer"

cat <<CARD

══════════════ 四剧本操作卡(断言=事件镜像日志) ══════════════
事件日志: ${EVENT_LOG}
启动命令: HOROSA_UPDATE_BASE_OVERRIDE=http://127.0.0.1:${PORT} "${BIN}"
(每个剧本前建议清空事件日志: rm -f "\${EVENT_LOG}")

S1 增量命中: 启动→菜单「检查更新」→立即更新→等 ready。
   验: bash scripts/verify_update_experience_local.sh --assert s1
S2 篡改降级: 先 --tamper,再触发更新(增量校验失败→自动降级全量)。
   验: --assert s2;完了 --restore
S3 断点续传: 触发更新,下载中 kill -9 \$(pgrep -f horosa-desktop-installer);
   重启再更新,应从断点继续。验: --assert s3
S4 强制全量: HOROSA_UPDATE_FULL_ONLY=1 加启动命令再更新。验: --assert s4

收尾: bash scripts/verify_update_experience_local.sh --stop
════════════════════════════════════════════════════════════
CARD
