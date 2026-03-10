#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_APP="$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PYAPP'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
print(root / 'src-tauri/target-user/release/bundle/macos' / f"{config['appName']}.app")
PYAPP
)"
PKG_PATH="$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PYPKG'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
print(root / 'dist' / config['desktopPkgName'])
PYPKG
)"
ZIP_PATH="$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PYZIP'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
print(root / 'dist' / config['desktopAssetName'])
PYZIP
)"

for path in "$TARGET_APP" "$PKG_PATH" "$ZIP_PATH"; do
  [ -e "$path" ] || {
    echo "missing artifact: $path" >&2
    exit 1
  }
done

APP_SIG_OUTPUT="$(codesign -dv --verbose=4 "$TARGET_APP" 2>&1)"
PKG_SIG_OUTPUT="$(pkgutil --check-signature "$PKG_PATH" 2>&1 || true)"
SPCTL_OUTPUT="$(spctl -a -vv "$TARGET_APP" 2>&1 || true)"

printf '%s
' "$APP_SIG_OUTPUT" | rg 'Authority=Developer ID Application' >/dev/null || {
  echo 'app is not signed with Developer ID Application' >&2
  exit 1
}
printf '%s
' "$APP_SIG_OUTPUT" | rg 'TeamIdentifier=' >/dev/null || {
  echo 'app TeamIdentifier missing' >&2
  exit 1
}
printf '%s
' "$PKG_SIG_OUTPUT" | rg 'Developer ID Installer' >/dev/null || {
  echo 'pkg is not signed with Developer ID Installer' >&2
  exit 1
}
printf '%s
' "$SPCTL_OUTPUT" | rg 'accepted' >/dev/null || {
  echo 'Gatekeeper does not accept app bundle' >&2
  printf '%s
' "$SPCTL_OUTPUT" >&2
  exit 1
}

echo 'public distribution readiness passed'
