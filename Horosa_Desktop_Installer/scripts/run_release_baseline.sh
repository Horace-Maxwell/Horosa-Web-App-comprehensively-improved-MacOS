#!/usr/bin/env bash
# run_release_baseline.sh —— 本机发版基线一键跑 + 落戳(替代已删除的 GitHub CI 门;preflight [6] 认戳)。
# 套件(串行,互斥于全量 preflight):cargo_fmt · cargo_test · pytest · mvn(四模块带测,含四柱全年份域矩阵,需本仓的排盘服务在 :8899)· jest_full
# 用法: run_release_baseline.sh [--only cargo_fmt,cargo_test,pytest,mvn,jest_full]
#   日志 build/release-baseline/<套件>.log;戳 build/release-baseline.json(每条套件各自落,HEAD 变了自动重开)。
# 环境:HOROSA_BASELINE_JEST_WORKERS(缺省 8)· HOROSA_BASELINE_PYTHON(缺省内嵌 runtime/mac/python,无则 python3)
set -uo pipefail
INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "${INSTALLER_ROOT}/.." && pwd)"
STAMP="${INSTALLER_ROOT}/scripts/release_baseline_stamp.py"
LOGDIR="${INSTALLER_ROOT}/build/release-baseline"; mkdir -p "${LOGDIR}"
ONLY="cargo_fmt,cargo_test,pytest,mvn,jest_full"
case "${1:-}" in --only=*) ONLY="${1#--only=}";; --only) ONLY="${2:-$ONLY}";; "") ;; *) echo "用法: $0 [--only a,b,c]" >&2; exit 2;; esac
want(){ case ",${ONLY}," in *",$1,"*) return 0;; *) return 1;; esac; }
export PATH="${HOME}/.cargo/bin:${PATH}"
if ! command -v node >/dev/null 2>&1; then
  _FNM="$(ls -d "${HOME}"/.local/share/fnm/node-versions/*/installation/bin 2>/dev/null | sort -V | tail -n 1)"
  [ -n "${_FNM}" ] && export PATH="${_FNM}:${PATH}"
fi
PY="${HOROSA_BASELINE_PYTHON:-${REPO_ROOT}/runtime/mac/python/bin/python3}"; [ -x "${PY}" ] || PY="python3"
# 没有私有不变量文件的检出:全量 jest 走离线差分网
[ -f "${INSTALLER_ROOT}/scripts/private_invariants.sh" ] || export HOROSA_DIFFNET_OFFLINE="${HOROSA_DIFFNET_OFFLINE:-1}"
stamp(){ /usr/bin/python3 "${STAMP}" write --repo "${REPO_ROOT}" --suite "$1" --rc "$2" --summary "$3" --log "$4"; }
echo "== 本机发版基线 @ $(git -C "${REPO_ROOT}" rev-parse --short HEAD)(dirty=$(git -C "${REPO_ROOT}" status --porcelain | grep -vc SELFCHECK_LOG.md))  套件: ${ONLY}"
if want cargo_fmt; then
  L="${LOGDIR}/cargo_fmt.log"; cargo fmt --manifest-path "${INSTALLER_ROOT}/src-tauri/Cargo.toml" --check > "${L}" 2>&1; RC=$?
  stamp cargo_fmt "${RC}" "$([ "${RC}" = 0 ] && echo '0 差' || echo "有未格式化改动(见日志)")" "${L}"
fi
if want cargo_test; then
  L="${LOGDIR}/cargo_test.log"; cargo test --manifest-path "${INSTALLER_ROOT}/src-tauri/Cargo.toml" > "${L}" 2>&1; RC=$?
  stamp cargo_test "${RC}" "$(grep -a -E '^test result' "${L}" | tail -n 1)" "${L}"
fi
if want pytest; then
  L="${LOGDIR}/pytest.log"
  ( cd "${REPO_ROOT}/Horosa-Web/astropy" && PYTHONPATH=.:../flatlib-ctrad2:../vendor "${PY}" -m pytest -q tests/ -p no:cacheprovider ) > "${L}" 2>&1; RC=$?
  stamp pytest "${RC}" "$(tail -n 1 "${L}")" "${L}"
fi
if want mvn; then
  L="${LOGDIR}/mvn.log"; : > "${L}"
  # 四柱全年份域矩阵打 :8899 —— 必须是本仓的排盘服务(别的项目 / 装好的运行时也会占这个口,算出来的不是本仓的引擎)
  _PID="$(lsof -nP -iTCP:8899 -sTCP:LISTEN -t 2>/dev/null | head -n 1)"
  _CMD="$( [ -n "${_PID}" ] && ps -o command= -p "${_PID}" 2>/dev/null || true)"
  if [ -z "${_PID}" ]; then
    echo "mvn 跳过::8899 没有排盘服务(先 cd Horosa-Web && HOROSA_SKIP_UI_BUILD=1 ./start_horosa_local.sh)" | tee -a "${L}"; stamp mvn 75 ":8899 无排盘服务,四柱矩阵没法打" "${L}"
  elif ! printf '%s' "${_CMD}" | grep -qF -- "${REPO_ROOT}/Horosa-Web/astropy"; then
    echo "mvn 跳过::8899 上跑的不是本仓的排盘服务(pid ${_PID}: ${_CMD:0:120})" | tee -a "${L}"; stamp mvn 75 ":8899 被别的排盘服务占用(pid ${_PID}),四柱矩阵不能打外来引擎" "${L}"
  else
    export JAVA_HOME="$(/usr/libexec/java_home -v 17 2>/dev/null || true)"; [ -n "${JAVA_HOME}" ] && export PATH="${JAVA_HOME}/bin:${PATH}"
    RC=0; SUM=""
    for m in boundless basecomm astrostudy astrostudycn; do
      ( cd "${REPO_ROOT}/Horosa-Web/astrostudysrv/${m}" && mvn -o test ) >> "${L}" 2>&1 || RC=1
      SUM="${SUM}${m}:$(grep -a -E 'Tests run:.*Fail' "${L}" | tail -n 1 | sed -E 's/.*Tests run: ([0-9]+), Failures: ([0-9]+), Errors: ([0-9]+).*/\1\/\2\/\3/') "
    done
    stamp mvn "${RC}" "${SUM}" "${L}"
  fi
fi
if want jest_full; then
  L="${LOGDIR}/jest_full.log"
  ( cd "${REPO_ROOT}/Horosa-Web/astrostudyui" && ./node_modules/.bin/umi-test --maxWorkers="${HOROSA_BASELINE_JEST_WORKERS:-8}" ) > "${L}" 2>&1; RC=$?
  stamp jest_full "${RC}" "$(grep -a -E '^(Test Suites|Tests):' "${L}" | tr '\n' ' ')" "${L}"
fi
echo "== 基线戳:"; /usr/bin/python3 "${STAMP}" check --repo "${REPO_ROOT}"; exit $?
