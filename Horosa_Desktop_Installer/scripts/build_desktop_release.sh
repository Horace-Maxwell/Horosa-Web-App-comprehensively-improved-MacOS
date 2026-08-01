#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_ROOT="${INSTALLER_ROOT}/dist"
BUILD_ROOT="${INSTALLER_ROOT}/build"
TARGET_ROOT="${INSTALLER_ROOT}/src-tauri/target-user"
OFFLINE_SCRIPTS_RENDERED_DIR="${BUILD_ROOT}/installer-scripts-rendered-offline"
NOTARY_BUILD_ROOT="${BUILD_ROOT}/notary"
POSTINSTALL_TEMPLATE="${INSTALLER_ROOT}/installer-scripts/postinstall.template"
RELEASE_CONFIG="${INSTALLER_ROOT}/config/release_config.json"
APPLE_SIGNING_IDENTITY="${APPLE_SIGNING_IDENTITY:-}"
APPLE_INSTALLER_IDENTITY="${APPLE_INSTALLER_IDENTITY:-}"
# 默认带防御性 entitlements(JIT/可执行内存/库校验豁免,内嵌 Java/Python 子进程在
# hardened runtime 下的最小集);显式置空 APPLE_ENTITLEMENTS_PATH="" 可退回无 entitlements。
APPLE_ENTITLEMENTS_PATH="${APPLE_ENTITLEMENTS_PATH-${INSTALLER_ROOT}/installer-scripts/horosa.entitlements}"
APPLE_SIGNING_KEYCHAIN="${APPLE_SIGNING_KEYCHAIN:-${HOME}/Library/Keychains/login.keychain-db}"
NOTARYTOOL_KEYCHAIN_PROFILE="${NOTARYTOOL_KEYCHAIN_PROFILE:-horosa-notary}"
HOROSA_PUBLIC_DISTRIBUTION_RAW="${HOROSA_PUBLIC_DISTRIBUTION:-auto}"
HOROSA_PUBLIC_DISTRIBUTION="${HOROSA_PUBLIC_DISTRIBUTION_RAW}"

pick_single_identity_hash() {
  local profile="$1"
  local label="$2"
  local raw_matches unique_labels hashes
  raw_matches="$(security find-identity -v -p "${profile}" 2>/dev/null | rg "Developer ID ${label}: " || true)"
  unique_labels="$(printf '%s\n' "${raw_matches}" | sed -En 's/^ *[0-9]+\) [0-9A-F]+ "(.*)"$/\1/p' | sort -u)"
  hashes="$(printf '%s\n' "${raw_matches}" | sed -En 's/^ *[0-9]+\) ([0-9A-F]+) ".*$/\1/p')"
  local label_count hash_count
  label_count="$(printf '%s\n' "${unique_labels}" | sed '/^$/d' | wc -l | tr -d ' ')"
  hash_count="$(printf '%s\n' "${hashes}" | sed '/^$/d' | wc -l | tr -d ' ')"
  if [ "${label_count}" = "1" ] && [ "${hash_count}" -ge "1" ]; then
    printf '%s' "$(printf '%s\n' "${hashes}" | sed '/^$/d' | tail -n 1)"
    return 0
  fi
  return 1
}

if [ -z "${APPLE_SIGNING_IDENTITY:-}" ] && APPLE_SIGNING_IDENTITY_AUTO="$(pick_single_identity_hash codesigning Application)"; then
  APPLE_SIGNING_IDENTITY="${APPLE_SIGNING_IDENTITY_AUTO}"
fi
if [ -z "${APPLE_INSTALLER_IDENTITY:-}" ] && APPLE_INSTALLER_IDENTITY_AUTO="$(pick_single_identity_hash basic Installer)"; then
  APPLE_INSTALLER_IDENTITY="${APPLE_INSTALLER_IDENTITY_AUTO}"
fi

PUBLIC_SIGNING_INPUTS=0
if [ -n "${APPLE_SIGNING_IDENTITY:-}" ] || [ -n "${APPLE_INSTALLER_IDENTITY:-}" ] || [ -n "${NOTARYTOOL_KEYCHAIN_PROFILE:-}" ]; then
  PUBLIC_SIGNING_INPUTS=1
fi
PUBLIC_SIGNING_READY=0
if [ -n "${APPLE_SIGNING_IDENTITY:-}" ] && [ -n "${APPLE_INSTALLER_IDENTITY:-}" ] && [ -n "${NOTARYTOOL_KEYCHAIN_PROFILE:-}" ]; then
  PUBLIC_SIGNING_READY=1
fi

if [ "${PUBLIC_SIGNING_INPUTS}" = "1" ] && [ "${PUBLIC_SIGNING_READY}" != "1" ]; then
  echo "partial public distribution configuration detected." >&2
  echo "APPLE_SIGNING_IDENTITY=${APPLE_SIGNING_IDENTITY:-<missing>}" >&2
  echo "APPLE_INSTALLER_IDENTITY=${APPLE_INSTALLER_IDENTITY:-<missing>}" >&2
  echo "NOTARYTOOL_KEYCHAIN_PROFILE=${NOTARYTOOL_KEYCHAIN_PROFILE:-<missing>}" >&2
  echo "either provide all three values, or unset them for ad-hoc local builds." >&2
  exit 1
fi

if [ "${HOROSA_PUBLIC_DISTRIBUTION_RAW}" = "auto" ]; then
  if [ "${PUBLIC_SIGNING_READY}" = "1" ]; then
    HOROSA_PUBLIC_DISTRIBUTION=1
  else
    HOROSA_PUBLIC_DISTRIBUTION=0
  fi
fi

if [ "${HOROSA_PUBLIC_DISTRIBUTION}" = "1" ] && [ "${PUBLIC_SIGNING_READY}" != "1" ]; then
  echo "HOROSA_PUBLIC_DISTRIBUTION=1 requires Developer ID Application, Developer ID Installer, and a notarytool keychain profile." >&2
  exit 1
fi

# ad-hoc 降档显式化:签名三件套缺失时产物只有 ad-hoc 签名(他机 Gatekeeper 拦),
# 在 dist/ 落 UNSIGNED-DEV-BUILD.txt 标记 + 显眼警告;publish 的装订硬门([134])见此标记
# 或 stapler validate 不过即拒绝上传——「本地误建版流入 release」这条路从两头堵死。
if [ "${HOROSA_PUBLIC_DISTRIBUTION}" = "0" ]; then
  mkdir -p "${DIST_ROOT}"
  printf 'ad-hoc build (no Developer ID / notarization). NOT for distribution.\nbuilt_at=%s\n' "$(date '+%Y-%m-%d %H:%M:%S')" > "${DIST_ROOT}/UNSIGNED-DEV-BUILD.txt"
  echo "⚠️⚠️  ad-hoc 构建(未签名/未公证):产物仅限本机测试,publish 装订门会拒绝上传。" >&2
else
  rm -f "${DIST_ROOT}/UNSIGNED-DEV-BUILD.txt" 2>/dev/null || true
fi

if [ "${HOROSA_PUBLIC_DISTRIBUTION}" = "1" ] && [ "${PUBLIC_SIGNING_READY}" = "1" ] && ! xcrun notarytool history --keychain-profile "${NOTARYTOOL_KEYCHAIN_PROFILE}" >/dev/null 2>&1; then
  echo "notarytool keychain profile is unavailable: ${NOTARYTOOL_KEYCHAIN_PROFILE}" >&2
  exit 1
fi

# TAB 分隔交接:appName 可含空格,空格分词会让全部字段右移一位
# (RUNTIME_ASSET 变成名字后半截 → "missing runtime archive" 假报)。
IFS=$'\t' read -r APP_NAME RUNTIME_ASSET DESKTOP_ASSET DESKTOP_PKG DESKTOP_PKG_ZIP DESKTOP_OFFLINE_PKG DESKTOP_OFFLINE_PKG_ZIP UPDATE_MANIFEST_NAME APP_RELEASE_TAG RUNTIME_VERSION RUNTIME_RELEASE_TAG SUPPORTED_ARCH <<EOF
$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PYCONF'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
version = json.loads((root / 'package.json').read_text())['version']
runtime_version = str(config.get('runtimeVersion') or '').strip()
if runtime_version.lower() in ('', 'auto', 'same-as-app'):
    runtime_version = version
print(
    config['appName'],
    config['runtimeAssetName'],
    config['desktopAssetName'],
    config['desktopPkgName'],
    config['desktopPkgZipName'],
    config['desktopOfflinePkgName'],
    config['desktopOfflinePkgZipName'],
    config['updateManifestName'],
    f"{config['releaseTagPrefix']}{version}",
    runtime_version,
    f"{config['releaseTagPrefix']}{runtime_version}",
    config.get('supportedArch', 'arm64'),
    sep='\t',
)
PYCONF
)
EOF
TARGET_APP="${TARGET_ROOT}/release/bundle/macos/${APP_NAME}.app"
COMPONENT_PKG="${BUILD_ROOT}/pkg/desktop.component.pkg"
OFFLINE_COMPONENT_PKG="${BUILD_ROOT}/pkg/desktop-offline.component.pkg"
COMPONENT_PLIST="${BUILD_ROOT}/pkg/component.plist"
PKG_STAGE_ROOT="${BUILD_ROOT}/pkg-root"
APP_BUNDLE_ZIP="${DIST_ROOT}/${DESKTOP_ASSET}"
INSTALLER_PKG="${DIST_ROOT}/${DESKTOP_PKG}"
INSTALLER_PKG_ZIP="${DIST_ROOT}/${DESKTOP_PKG_ZIP}"
OFFLINE_INSTALLER_PKG="${DIST_ROOT}/${DESKTOP_OFFLINE_PKG}"
OFFLINE_INSTALLER_PKG_ZIP="${DIST_ROOT}/${DESKTOP_OFFLINE_PKG_ZIP}"
UPDATE_MANIFEST="${DIST_ROOT}/${UPDATE_MANIFEST_NAME}"
RUNTIME_ARCHIVE="${DIST_ROOT}/${RUNTIME_ASSET}"
LEGACY_DMG="${DIST_ROOT}/Horosa-Desktop-macos-arm64.dmg"
NOTARY_APP_ZIP="${NOTARY_BUILD_ROOT}/${APP_NAME}.notary.zip"
REPO_SLUG="$(
INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PY'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
print(f"{config['repoOwner']}/{config['repoName']}")
PY
)"

mkdir -p "${DIST_ROOT}" "${BUILD_ROOT}/pkg" "${OFFLINE_SCRIPTS_RENDERED_DIR}" "${NOTARY_BUILD_ROOT}"
"${INSTALLER_ROOT}/scripts/generate_icon.sh"
if [ "${HOROSA_REUSE_REMOTE_RUNTIME:-0}" = "1" ] && [ "${RUNTIME_RELEASE_TAG}" != "${APP_RELEASE_TAG}" ]; then
  if ! command -v gh >/dev/null 2>&1; then
    echo "HOROSA_REUSE_REMOTE_RUNTIME=1 requires gh to download ${RUNTIME_ASSET} from ${RUNTIME_RELEASE_TAG}." >&2
    exit 1
  fi
  rm -f "${RUNTIME_ARCHIVE}"
  gh release download "${RUNTIME_RELEASE_TAG}" --repo "${REPO_SLUG}" --pattern "${RUNTIME_ASSET}" --dir "${DIST_ROOT}" --clobber
else
  APPLE_SIGNING_IDENTITY="${APPLE_SIGNING_IDENTITY}" APPLE_SIGNING_KEYCHAIN="${APPLE_SIGNING_KEYCHAIN}" HOROSA_PUBLIC_DISTRIBUTION="${HOROSA_PUBLIC_DISTRIBUTION}" "${INSTALLER_ROOT}/scripts/package_runtime_payload.sh"
fi

if [ ! -f "${RUNTIME_ARCHIVE}" ]; then
  echo "missing runtime archive: ${RUNTIME_ARCHIVE}" >&2
  exit 1
fi

# ── 全路由真实冒烟门(发布强制,fail fast 于签名/公证之前)────────────────────────
# 对本次归档真启动内嵌 Python+Java,Python 面挂载 + Java 面路由逐条真实请求断言真实计算;
# 含 slim 自证(桩激活环境)与挂载↔探针漂移比对。构建 +3~6 分钟。
# 逃生阀:HOROSA_SKIP_RUNTIME_SMOKE=1(仅救急,发布前必须补跑,preflight[79] 会拦)。
if [ "${HOROSA_SKIP_RUNTIME_SMOKE:-0}" = "1" ]; then
  echo "⚠️  HOROSA_SKIP_RUNTIME_SMOKE=1:跳过全路由冒烟门(preflight[79] 将要求补跑)。"
else
  bash "${INSTALLER_ROOT}/scripts/verify_runtime_smoke.sh" "${RUNTIME_ARCHIVE}"
fi

LOCAL_RUNTIME_SHA256="$(shasum -a 256 "${RUNTIME_ARCHIVE}" | awk '{print $1}')"
RUNTIME_SHA256="${LOCAL_RUNTIME_SHA256}"
if [ "${RUNTIME_RELEASE_TAG}" != "${APP_RELEASE_TAG}" ] && [ "${HOROSA_FORCE_RUNTIME_UPLOAD:-0}" != "1" ] && command -v gh >/dev/null 2>&1; then
  REMOTE_RUNTIME_JSON="$(gh release view "${RUNTIME_RELEASE_TAG}" --repo "${REPO_SLUG}" --json assets 2>/dev/null || true)"
  REMOTE_RUNTIME_SHA="$(python3 - <<'PY' "${RUNTIME_ASSET}" "${REMOTE_RUNTIME_JSON}"
import json, sys
asset_name = sys.argv[1]
payload = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].strip() else {}
for asset in payload.get('assets', []):
    if asset.get('name') == asset_name:
        digest = str(asset.get('digest') or '')
        if digest.startswith('sha256:'):
            print(digest.split(':', 1)[1])
            break
PY
)"
  if [ -n "${REMOTE_RUNTIME_SHA}" ]; then
    if [ "${REMOTE_RUNTIME_SHA}" != "${LOCAL_RUNTIME_SHA256}" ]; then
      echo "runtime payload changed, but release_config.json still points to ${RUNTIME_RELEASE_TAG}." >&2
      echo "local runtime sha:  ${LOCAL_RUNTIME_SHA256}" >&2
      echo "remote runtime sha: ${REMOTE_RUNTIME_SHA}" >&2
      echo "bump runtimeVersion (or set HOROSA_FORCE_RUNTIME_UPLOAD=1) before publishing this release." >&2
      exit 1
    fi
    RUNTIME_SHA256="${REMOTE_RUNTIME_SHA}"
    echo "using remote runtime digest from ${RUNTIME_RELEASE_TAG}: ${RUNTIME_SHA256}"
  fi
fi

if [ ! -d "${INSTALLER_ROOT}/node_modules" ]; then
  (cd "${INSTALLER_ROOT}" && npm install)
fi

find "${TARGET_ROOT}/release/bundle" -type f -name '*.dmg' -delete 2>/dev/null || true
TAURI_BUILD_OK=1
# 隐去构建机器路径:Cargo 默认把构建机 $HOME 与 cargo registry 绝对路径嵌入二进制 panic-string
# 常量,strip 不能去。RUSTFLAGS --remap-path-prefix 在编译时把这些路径替换为占位符(user/cargo/rust/src),
# 二进制 strings 输出零开发机 PII。$HOME 在构建机 shell 现场展开,不写入任何 tracked 文件。
HOROSA_RUSTFLAGS_REMAP="--remap-path-prefix=${HOME}/.cargo/registry=cargo --remap-path-prefix=${HOME}/.rustup/toolchains=rust --remap-path-prefix=${INSTALLER_ROOT}/src-tauri=src --remap-path-prefix=${HOME}=user"
if ! (cd "${INSTALLER_ROOT}" && CARGO_TARGET_DIR="${TARGET_ROOT}" RUSTFLAGS="${HOROSA_RUSTFLAGS_REMAP} ${RUSTFLAGS:-}" npm run tauri:build -- --bundles app); then
  TAURI_BUILD_OK=0
  echo "tauri app bundling failed; checking for reusable app bundle..." >&2
fi

if [ ! -d "${TARGET_APP}" ]; then
  echo "missing built app bundle: ${TARGET_APP}" >&2
  exit 1
fi

CURRENT_ARCH="$(uname -m)"
if [ "${SUPPORTED_ARCH}" = "arm64" ] && [ "${CURRENT_ARCH}" != "arm64" ]; then
  echo "release_config.json is locked to arm64, but current builder is ${CURRENT_ARCH}" >&2
  exit 1
fi

if [ "${TAURI_BUILD_OK}" != "1" ]; then
  echo "tauri app bundling failed and no reusable app bundle fallback was requested" >&2
  exit 1
fi

# [2026-07-20 实案] 离线 pkg 内嵌档一律 gz —— zst 内嵌在真机安装 100% 必败的铁案:
# macOS 系统 /usr/bin/tar(libarchive 编译清单 zlib/liblzma/bz2lib,**无 zstd**)平时能解 .zst
# 全靠 PATH 里第三方 zstd 兜底;PKInstallSandbox 的 PATH 精简无此兜底 → postinstall 解压
# 即败 → 降级 pending → App 首启读到旧版缓存报「版本不符」。构建机满 PATH 探测是假绿。
# zst 仅限显式 HOROSA_OFFLINE_ZSTD=1 且**净化 PATH**探测通过(本机实验用;发布链禁用)。
RUNTIME_ARCHIVE_ZST="${RUNTIME_ARCHIVE%.tar.gz}.tar.zst"
OFFLINE_EMBED_ARCHIVE="${RUNTIME_ARCHIVE}"
OFFLINE_EMBED_ASSET="${RUNTIME_ASSET}"
if [ "${HOROSA_OFFLINE_ZSTD:-0}" = "1" ] && [ -s "${RUNTIME_ARCHIVE_ZST}" ] \
  && env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin /usr/bin/tar -tf "${RUNTIME_ARCHIVE_ZST}" >/dev/null 2>&1; then
  OFFLINE_EMBED_ARCHIVE="${RUNTIME_ARCHIVE_ZST}"
  OFFLINE_EMBED_ASSET="$(basename "${RUNTIME_ARCHIVE_ZST}")"
  echo "offline pkg embeds zst runtime archive: ${OFFLINE_EMBED_ASSET} (explicit HOROSA_OFFLINE_ZSTD=1)"
else
  echo "offline pkg embeds gz runtime archive: ${OFFLINE_EMBED_ASSET}"
fi
OFFLINE_EMBED_SHA256="$(shasum -a 256 "${OFFLINE_EMBED_ARCHIVE}" | awk '{print $1}')"

INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" RUNTIME_SHA256_ENV="${RUNTIME_SHA256}" LOCAL_RUNTIME_SHA256_ENV="${LOCAL_RUNTIME_SHA256}" OFFLINE_RUNTIME_ASSET_ENV="${OFFLINE_EMBED_ASSET}" OFFLINE_RUNTIME_SHA256_ENV="${OFFLINE_EMBED_SHA256}" RUNTIME_VERSION_ENV="${RUNTIME_VERSION}" RUNTIME_RELEASE_TAG_ENV="${RUNTIME_RELEASE_TAG}" python3 - <<'PYPOST'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
template = (root / 'installer-scripts/postinstall.template').read_text()

base_replacements = {
    '__APP_NAME__': config['appName'],
    '__REPO_OWNER__': config['repoOwner'],
    '__REPO_NAME__': config['repoName'],
    '__VERSION__': os.environ['RUNTIME_VERSION_ENV'],
    '__RUNTIME_ASSET__': config['runtimeAssetName'],
    # 离线内嵌档名 = 实际拷进 scripts 的归档名(见下方 cp 到 OFFLINE_SCRIPTS_RENDERED_DIR/${RUNTIME_ASSET})。
    # 缺此替换 → postinstall ARCHIVE_NAME 停留字面量 __OFFLINE_RUNTIME_ASSET__ → 找不到内嵌档
    # → 离线安装降级 first-launch pending → App 首启报「运行时损坏/旧版本」。zst 安装链 drift 坑。
    '__OFFLINE_RUNTIME_ASSET__': config['runtimeAssetName'],
    '__RUNTIME_RELEASE_TAG__': os.environ['RUNTIME_RELEASE_TAG_ENV'],
    # 共享目录名单源化:安装器与壳层必须看同一目录(配置缺省 Horosa)
    '__SHARED_ROOT_NAME__': config.get('sharedRootName', 'Horosa'),
}
offline_scripts_dir = root / 'build/installer-scripts-rendered-offline'
offline_scripts_dir.mkdir(parents=True, exist_ok=True)

offline_template = template
for key, value in {
    **base_replacements,
    # [2026-07-20 实案] 离线三键同源:内嵌档名/内嵌档 sha 由构建层实际选定的 OFFLINE_EMBED_* 传入,
    # 与「实际 cp 进 Scripts 的那份档」永远一致(dict 合并同键覆盖 base 缺省)。
    '__OFFLINE_RUNTIME_ASSET__': os.environ['OFFLINE_RUNTIME_ASSET_ENV'],
    '__RUNTIME_SHA256__': os.environ['OFFLINE_RUNTIME_SHA256_ENV'],
    '__INSTALL_MODE__': 'bootstrap-now',
}.items():
    offline_template = offline_template.replace(key, value)
offline_out = offline_scripts_dir / 'postinstall'
offline_out.write_text(offline_template)
offline_out.chmod(0o755)

PYPOST

rm -f "${OFFLINE_SCRIPTS_RENDERED_DIR}/${RUNTIME_ASSET}" "${OFFLINE_SCRIPTS_RENDERED_DIR}/$(basename "${RUNTIME_ARCHIVE_ZST}")"
cp -f "${OFFLINE_EMBED_ARCHIVE}" "${OFFLINE_SCRIPTS_RENDERED_DIR}/${OFFLINE_EMBED_ASSET}"

# ── [2026-07-20 实案] 渲染后硬断言(占位符漏替/内嵌档错位/沙盒不可解 任一命中 = 立即熔断,绝不出包) ──
if grep -nE '__[A-Z_]+__' "${OFFLINE_SCRIPTS_RENDERED_DIR}/postinstall"; then
  echo "ERROR: rendered postinstall 残留未替换占位符(见上行)—— 模板新增占位符必须同步渲染表" >&2
  exit 1
fi
RENDERED_ARCHIVE_NAME="$(sed -n 's/^ARCHIVE_NAME="\(.*\)"$/\1/p' "${OFFLINE_SCRIPTS_RENDERED_DIR}/postinstall" | head -n 1)"
if [ -z "${RENDERED_ARCHIVE_NAME}" ] || [ ! -s "${OFFLINE_SCRIPTS_RENDERED_DIR}/${RENDERED_ARCHIVE_NAME}" ]; then
  echo "ERROR: postinstall ARCHIVE_NAME(${RENDERED_ARCHIVE_NAME:-<空>})在 Scripts 目录无对应内嵌档" >&2
  exit 1
fi
if ! env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin /usr/bin/tar -tf "${OFFLINE_SCRIPTS_RENDERED_DIR}/${RENDERED_ARCHIVE_NAME}" >/dev/null 2>&1; then
  echo "ERROR: 内嵌档在净化 PATH(≈PKInstallSandbox)下不可解 —— 系统 tar 无此压缩滤器,禁止出包" >&2
  exit 1
fi
echo "offline embed asserts OK: ${RENDERED_ARCHIVE_NAME} (占位符零残留/档在位/净化 PATH 可解)"

APPLE_SIGNING_IDENTITY="${APPLE_SIGNING_IDENTITY}" APPLE_ENTITLEMENTS_PATH="${APPLE_ENTITLEMENTS_PATH}" APPLE_SIGNING_KEYCHAIN="${APPLE_SIGNING_KEYCHAIN}" "${INSTALLER_ROOT}/scripts/ad_hoc_sign_app.sh" "${TARGET_APP}"

if [ -n "${APPLE_SIGNING_IDENTITY:-}" ]; then
  spctl -a -vv "${TARGET_APP}" || true
fi

rm -rf "${PKG_STAGE_ROOT}"
mkdir -p "${PKG_STAGE_ROOT}/Applications"
rsync -a "${TARGET_APP}/" "${PKG_STAGE_ROOT}/Applications/${APP_NAME}.app/"

APP_INFO_PLIST="${PKG_STAGE_ROOT}/Applications/${APP_NAME}.app/Contents/Info.plist"
BUNDLE_ID="$(plutil -extract CFBundleIdentifier raw -o - "${APP_INFO_PLIST}")"
APP_VERSION="$(plutil -extract CFBundleShortVersionString raw -o - "${APP_INFO_PLIST}")"

rm -f "${APP_BUNDLE_ZIP}" "${INSTALLER_PKG}" "${INSTALLER_PKG_ZIP}" "${OFFLINE_INSTALLER_PKG}" "${OFFLINE_INSTALLER_PKG_ZIP}" "${COMPONENT_PKG}" "${OFFLINE_COMPONENT_PKG}" "${COMPONENT_PLIST}" "${UPDATE_MANIFEST}" "${LEGACY_DMG}" "${NOTARY_APP_ZIP}"

pkgbuild --analyze --root "${PKG_STAGE_ROOT}" "${COMPONENT_PLIST}"
COMPONENT_PLIST_ENV="${COMPONENT_PLIST}" APP_NAME_ENV="${APP_NAME}" python3 - <<'PYPLIST'
import os
import plistlib
from pathlib import Path
plist_path = Path(os.environ['COMPONENT_PLIST_ENV'])
app_name = os.environ['APP_NAME_ENV']
entries = plistlib.loads(plist_path.read_bytes())
expected = f'Applications/{app_name}.app'
for entry in entries:
    if entry.get('RootRelativeBundlePath') == expected:
        entry['BundleIsRelocatable'] = False
        entry['BundleHasStrictIdentifier'] = True
        entry['BundleIsVersionChecked'] = True
        entry['BundleOverwriteAction'] = 'upgrade'
        break
else:
    raise SystemExit(f'missing component plist entry for {expected}')
plist_path.write_bytes(plistlib.dumps(entries))
PYPLIST

build_component_pkg() {
  local scripts_dir="$1"
  local component_pkg="$2"
  pkgbuild \
    --root "${PKG_STAGE_ROOT}" \
    --component-plist "${COMPONENT_PLIST}" \
    --identifier "${BUNDLE_ID}" \
    --version "${APP_VERSION}" \
    --install-location / \
    --scripts "${scripts_dir}" \
    "${component_pkg}"
}

build_product_pkg() {
  local component_pkg="$1"
  local output_pkg="$2"
  # 分发守卫:不再让 productbuild 自动生成 Distribution(默认 hostArchitectures="x86_64,arm64"
  # 且无 OS 门,Intel/macOS 11.x 用户能装但首启崩)。用自定义模板钉 arm64-only + macOS 12+。
  local dist_xml="${BUILD_ROOT}/distribution-$(basename "${output_pkg}" .pkg).xml"
  DIST_TEMPLATE_ENV="${INSTALLER_ROOT}/installer-scripts/distribution.xml.template" \
  DIST_OUT_ENV="${dist_xml}" \
  DIST_APP_NAME_ENV="${APP_NAME}" \
  DIST_BUNDLE_ID_ENV="${BUNDLE_ID}" \
  DIST_APP_VERSION_ENV="${APP_VERSION}" \
  DIST_COMPONENT_ENV="$(basename "${component_pkg}")" \
  python3 - <<'PYDIST'
import os
template = open(os.environ['DIST_TEMPLATE_ENV'], encoding='utf-8').read()
for key, env in (('__APP_NAME__', 'DIST_APP_NAME_ENV'),
                 ('__BUNDLE_ID__', 'DIST_BUNDLE_ID_ENV'),
                 ('__APP_VERSION__', 'DIST_APP_VERSION_ENV'),
                 ('__COMPONENT_PKG_NAME__', 'DIST_COMPONENT_ENV')):
    template = template.replace(key, os.environ[env])
open(os.environ['DIST_OUT_ENV'], 'w', encoding='utf-8').write(template)
PYDIST
  PRODUCTBUILD_ARGS=(--distribution "${dist_xml}" --package-path "$(dirname "${component_pkg}")")
  if [ -n "${APPLE_INSTALLER_IDENTITY}" ]; then
    PRODUCTBUILD_ARGS+=(--sign "${APPLE_INSTALLER_IDENTITY}" --keychain "${APPLE_SIGNING_KEYCHAIN}")
  fi
  PRODUCTBUILD_ARGS+=("${output_pkg}")
  productbuild "${PRODUCTBUILD_ARGS[@]}"
}

build_component_pkg "${OFFLINE_SCRIPTS_RENDERED_DIR}" "${OFFLINE_COMPONENT_PKG}"
build_product_pkg "${OFFLINE_COMPONENT_PKG}" "${OFFLINE_INSTALLER_PKG}"

# ── [2026-07-20 实案] 离线 .pkg 真装 e2e 门(notarize 前拦截):展开成品包,在净化 PATH
# (≈PKInstallSandbox)下真跑 Scripts/postinstall(共享根重定向临时目录),断言运行时落位
# 且版本吻合。冒烟链只测过 runtime 归档本身,从未测过「安装沙盒里的 postinstall 全链」——
# v3.5.0 的离线包正是死在这段盲区。逃生阀 HOROSA_SKIP_PKG_E2E=1(仅救急;preflight 拦)。
if [ "${HOROSA_SKIP_PKG_E2E:-0}" = "1" ]; then
  echo "⚠️  HOROSA_SKIP_PKG_E2E=1:跳过离线 pkg 真装 e2e(preflight 将要求补跑)。"
else
  bash "${INSTALLER_ROOT}/scripts/verify_offline_pkg_install_e2e.sh" "${OFFLINE_INSTALLER_PKG}" "${RUNTIME_VERSION}"
fi

if [ "${HOROSA_PUBLIC_DISTRIBUTION}" = "1" ] && [ "${PUBLIC_SIGNING_READY}" = "1" ]; then
  (
    cd "$(dirname "${TARGET_APP}")"
    ditto -c -k --keepParent "${APP_NAME}.app" "${NOTARY_APP_ZIP}"
  )
  xcrun notarytool submit "${NOTARY_APP_ZIP}" --keychain-profile "${NOTARYTOOL_KEYCHAIN_PROFILE}" --wait
  xcrun stapler staple "${TARGET_APP}"
  xcrun notarytool submit "${OFFLINE_INSTALLER_PKG}" --keychain-profile "${NOTARYTOOL_KEYCHAIN_PROFILE}" --wait
  xcrun stapler staple "${OFFLINE_INSTALLER_PKG}"
  # [2026-07-20 实案] staple 会改 pkg 字节 → e2e stamp 的 sha 必须随之刷新(真装结论对 Scripts 不变,
  # 仅同步指纹;preflight [156]/[139] 按 sha 绑定成品,不刷新则永远红)。
  if [ -f "${INSTALLER_ROOT}/build/offline-pkg-e2e.stamp" ] && grep -q '^OK' "${INSTALLER_ROOT}/build/offline-pkg-e2e.stamp"; then
    printf 'OK\t%s\t%s\n' "$(shasum -a 256 "${OFFLINE_INSTALLER_PKG}" | awk '{print $1}')" "${RUNTIME_VERSION}" > "${INSTALLER_ROOT}/build/offline-pkg-e2e.stamp"
  fi
fi
(
  cd "$(dirname "${TARGET_APP}")"
  COPYFILE_DISABLE=1 ditto -c -k --keepParent --norsrc "${APP_NAME}.app" "${APP_BUNDLE_ZIP}"
)
rm -f "${INSTALLER_PKG_ZIP}" "${OFFLINE_INSTALLER_PKG_ZIP}"

echo "desktop app bundle ready: ${APP_BUNDLE_ZIP}"
echo "offline installer package ready: ${OFFLINE_INSTALLER_PKG}"
echo "component plist ready: ${COMPONENT_PLIST}"

INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" APP_RELEASE_TAG_ENV="${APP_RELEASE_TAG}" RUNTIME_RELEASE_TAG_ENV="${RUNTIME_RELEASE_TAG}" RUNTIME_VERSION_ENV="${RUNTIME_VERSION}" RUNTIME_SHA256_ENV="${RUNTIME_SHA256}" python3 - <<'PYMANIFEST'
import hashlib, json, os, pathlib, platform
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
app_release_tag = os.environ['APP_RELEASE_TAG_ENV']
runtime_release_tag = os.environ['RUNTIME_RELEASE_TAG_ENV']
runtime_version = os.environ['RUNTIME_VERSION_ENV']
runtime_sha256 = os.environ['RUNTIME_SHA256_ENV']
config = json.loads((root / 'config/release_config.json').read_text())
dist = root / 'dist'
arch = platform.machine().lower()
platform_key = 'darwin-aarch64' if arch in ('arm64', 'aarch64') else 'darwin-x86_64'
version = json.loads((root / 'package.json').read_text())['version']
app_base = f"https://github.com/{config['repoOwner']}/{config['repoName']}/releases/download/{app_release_tag}"
runtime_base = f"https://github.com/{config['repoOwner']}/{config['repoName']}/releases/download/{runtime_release_tag}"
platform_entry = {
  'appUrl': f"{app_base}/{config['desktopAssetName']}",
  'pkgUrl': f"{app_base}/{config['desktopOfflinePkgName']}",
  'runtimeUrl': f"{runtime_base}/{config['runtimeAssetName']}",
  'runtimeVersion': runtime_version,
  'appSha256': hashlib.sha256((dist / config['desktopAssetName']).read_bytes()).hexdigest(),
  'pkgSha256': hashlib.sha256((dist / config['desktopOfflinePkgName']).read_bytes()).hexdigest(),
  'runtimeSha256': runtime_sha256,
  # 进度可视化 v2:资产体积(客户端「提前显示要下多大」的数据源;老客户端 serde 忽略)
  'appSizeBytes': (dist / config['desktopAssetName']).stat().st_size,
  'pkgSizeBytes': (dist / config['desktopOfflinePkgName']).stat().st_size,
}
runtime_archive = dist / config['runtimeAssetName']
if runtime_archive.is_file():
    platform_entry['runtimeSizeBytes'] = runtime_archive.stat().st_size
# ── manifest v2:增量更新部件清单(v1 字段全保留——老客户端零影响;无 components
# 的 manifest 让新客户端自动走全量,天然降级)。lock 由 package_runtime_payload.sh
# 部件切分段产出;runtimeVersion/appName 不符 = 产物漂移(如旧打包残留),立即失败。
manifest_version = 1
lock_path = dist / 'components' / 'components-lock.json'
if lock_path.is_file():
    lock = json.loads(lock_path.read_text())
    if str(lock.get('runtimeVersion')) != str(runtime_version):
        raise SystemExit(f"components-lock runtimeVersion({lock.get('runtimeVersion')}) ≠ 本次构建({runtime_version}):部件产物漂移,请重跑 package_runtime_payload.sh 或清 dist/components")
    if str(lock.get('appName')) != str(config['appName']):
        raise SystemExit(f"components-lock appName({lock.get('appName')}) ≠ 本仓配置({config['appName']}):更新通道隔离,拒绝混装")
    manifest_version = 2
    # manifest 只带 diff 所需字段;应用细节(paths/files/preserve)在 lock asset 里,
    # 客户端经 componentsLockSha256 校验后读取(files 清单上千条,不进 manifest)。
    platform_entry['components'] = [
        {'name': c['name'], 'type': c['type'], 'sha256': c['sha256'], 'size': c['size'],
         'file': c['file'], 'url': f"{runtime_base}/{c['file']}"}
        for c in lock['components']
    ]
    platform_entry['componentsLockUrl'] = f"{runtime_base}/components-lock.json"
    platform_entry['componentsLockSha256'] = hashlib.sha256(lock_path.read_bytes()).hexdigest()
elif os.environ.get('HOROSA_REUSE_REMOTE_RUNTIME', '0') != '1':
    raise SystemExit('缺 dist/components/components-lock.json:本地打包路径必须产出部件(package_runtime_payload.sh 部件段被关?)')
manifest = {
  'version': version,
  'tag': app_release_tag,
  'notes': 'See GitHub release notes.',
  'manifestVersion': manifest_version,
  'platforms': {platform_key: platform_entry},
}
(dist / config['updateManifestName']).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
PYMANIFEST

echo "update manifest ready: ${UPDATE_MANIFEST}"
