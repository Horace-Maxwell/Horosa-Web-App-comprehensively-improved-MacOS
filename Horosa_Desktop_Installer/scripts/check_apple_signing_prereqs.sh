#!/usr/bin/env bash
set -euo pipefail

NOTARYTOOL_KEYCHAIN_PROFILE="${NOTARYTOOL_KEYCHAIN_PROFILE:-horosa-notary}"
FAILURES=0

pick_single_identity_labels() {
  local profile="$1"
  local label="$2"
  security find-identity -v -p "${profile}" 2>/dev/null \
    | rg "Developer ID ${label}: " \
    | sed -E 's/^ *[0-9]+\) [0-9A-F]+ "(.*)"$/\1/' \
    | sort -u || true
}

pick_single_identity_hash() {
  local profile="$1"
  local label="$2"
  local raw_matches
  raw_matches="$(security find-identity -v -p "${profile}" 2>/dev/null | rg "Developer ID ${label}: " || true)"
  local unique_labels hashes label_count hash_count
  unique_labels="$(printf '%s\n' "${raw_matches}" | sed -En 's/^ *[0-9]+\) [0-9A-F]+ "(.*)"$/\1/p' | sort -u)"
  hashes="$(printf '%s\n' "${raw_matches}" | sed -En 's/^ *[0-9]+\) ([0-9A-F]+) ".*$/\1/p')"
  label_count="$(printf '%s\n' "${unique_labels}" | sed '/^$/d' | wc -l | tr -d ' ')"
  hash_count="$(printf '%s\n' "${hashes}" | sed '/^$/d' | wc -l | tr -d ' ')"
  if [ "${label_count}" = "1" ] && [ "${hash_count}" -ge "1" ]; then
    printf '%s' "$(printf '%s\n' "${hashes}" | sed '/^$/d' | tail -n 1)"
    return 0
  fi
  return 1
}

require_single_identity_label() {
  local profile="$1"
  local label="$2"
  local matches
  matches="$(pick_single_identity_labels "${profile}" "${label}")"
  local count
  count="$(printf '%s\n' "${matches}" | sed '/^$/d' | wc -l | tr -d ' ')"
  if [ "${count}" = "1" ]; then
    printf '%s' "${matches}"
    return 0
  fi
  return 1
}

if ! command -v xcrun >/dev/null 2>&1; then
  echo "missing xcrun (install Xcode command line tools first)." >&2
  exit 1
fi

APP_IDENTITY_LABEL="$(require_single_identity_label codesigning Application || true)"
INSTALLER_IDENTITY_LABEL="$(require_single_identity_label basic Installer || true)"
APP_IDENTITY_HASH="$(pick_single_identity_hash codesigning Application || true)"
INSTALLER_IDENTITY_HASH="$(pick_single_identity_hash basic Installer || true)"

if [ -n "${APP_IDENTITY_LABEL}" ] && [ -n "${APP_IDENTITY_HASH}" ]; then
  echo "Developer ID Application ready: ${APP_IDENTITY_LABEL}"
else
  echo "missing or ambiguous Developer ID Application identity" >&2
  FAILURES=1
fi

if [ -n "${INSTALLER_IDENTITY_LABEL}" ] && [ -n "${INSTALLER_IDENTITY_HASH}" ]; then
  echo "Developer ID Installer ready: ${INSTALLER_IDENTITY_LABEL}"
else
  echo "missing or ambiguous Developer ID Installer identity" >&2
  FAILURES=1
fi

if xcrun notarytool history --keychain-profile "${NOTARYTOOL_KEYCHAIN_PROFILE}" >/dev/null 2>&1; then
  echo "notarytool profile ready: ${NOTARYTOOL_KEYCHAIN_PROFILE}"
else
  echo "notarytool profile unavailable: ${NOTARYTOOL_KEYCHAIN_PROFILE}" >&2
  FAILURES=1
fi

if [ "${FAILURES}" != "0" ]; then
  echo >&2
  echo "public distribution prerequisites are incomplete." >&2
  exit 1
fi

echo
echo "export APPLE_SIGNING_IDENTITY='${APP_IDENTITY_HASH}'"
echo "export APPLE_INSTALLER_IDENTITY='${INSTALLER_IDENTITY_HASH}'"
echo "export NOTARYTOOL_KEYCHAIN_PROFILE='${NOTARYTOOL_KEYCHAIN_PROFILE}'"
echo "HOROSA_PUBLIC_DISTRIBUTION=1 ./scripts/build_desktop_release.sh"
