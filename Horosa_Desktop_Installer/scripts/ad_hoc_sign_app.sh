#!/usr/bin/env bash
set -euo pipefail

APP_PATH="$1"
APPLE_SIGNING_IDENTITY="${APPLE_SIGNING_IDENTITY:-}"
APPLE_ENTITLEMENTS_PATH="${APPLE_ENTITLEMENTS_PATH:-}"

/usr/bin/xattr -cr "$APP_PATH" >/dev/null 2>&1 || true

if [ -n "$APPLE_SIGNING_IDENTITY" ]; then
  SIGN_ARGS=(--force --deep --options runtime --timestamp --sign "$APPLE_SIGNING_IDENTITY")
  if [ -n "$APPLE_ENTITLEMENTS_PATH" ]; then
    SIGN_ARGS+=(--entitlements "$APPLE_ENTITLEMENTS_PATH")
  fi
  /usr/bin/codesign "${SIGN_ARGS[@]}" "$APP_PATH"
else
  /usr/bin/codesign --force --deep --sign - "$APP_PATH"
fi

/usr/bin/codesign --verify --deep --strict "$APP_PATH"
