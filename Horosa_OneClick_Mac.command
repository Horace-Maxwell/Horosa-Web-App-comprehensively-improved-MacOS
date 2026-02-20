#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "${ROOT}/scripts/mac/bootstrap_and_run.sh" "$@"
