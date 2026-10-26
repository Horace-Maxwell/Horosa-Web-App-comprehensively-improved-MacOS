#!/usr/bin/env bash
# run_release_baseline.sh —— 本机发版基线一键跑 + 落戳(替代已删除的 GitHub CI 门;preflight [6] 认戳)。
# 套件(串行,互斥于全量 preflight):cargo_fmt · cargo_test · pytest(HOROSA_REQUIRE_SRV=1,需服务金标逐文件核 0 skip)· mvn(四模块带测,聚合 pom 同一 reactor,含四柱全年份域矩阵,需本仓的排盘服务在 :8899,且启动于引擎源码最近一次改动之后)· jest_full
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
# 全量 jest 的差分网缺省走离线(环境里显式给了就按给的)
DIFFNET_OFFLINE_DEFAULT=1
if [ -n "${DIFFNET_OFFLINE_DEFAULT}" ]; then export HOROSA_DIFFNET_OFFLINE="${HOROSA_DIFFNET_OFFLINE:-${DIFFNET_OFFLINE_DEFAULT}}"; fi
# 套件结果只记在「开跑时的 HEAD」名下:跑的途中有新提交 → 该套件不落戳(戳本身也记每个套件跑时工作区干不干净)
START_HEAD="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
stamp(){ /usr/bin/python3 "${STAMP}" write --repo "${REPO_ROOT}" --suite "$1" --rc "$2" --summary "$3" --log "$4" --head "${START_HEAD}"; }
DIRTY_N="$(git -C "${REPO_ROOT}" status --porcelain | grep -vc SELFCHECK_LOG.md || true)"
echo "== 本机发版基线 @ ${START_HEAD:0:8}(dirty=${DIRTY_N})  套件: ${ONLY}"
[ "${DIRTY_N:-0}" = "0" ] || echo "⚠️  工作区有未提交改动:本次结果会标成「跑在未提交改动上」,发布时不认(先提交再跑)"
if want cargo_fmt; then
  L="${LOGDIR}/cargo_fmt.log"; cargo fmt --manifest-path "${INSTALLER_ROOT}/src-tauri/Cargo.toml" --check > "${L}" 2>&1; RC=$?
  stamp cargo_fmt "${RC}" "$([ "${RC}" = 0 ] && echo '0 差' || echo "有未格式化改动(见日志)")" "${L}"
fi
if want cargo_test; then
  L="${LOGDIR}/cargo_test.log"; cargo test --manifest-path "${INSTALLER_ROOT}/src-tauri/Cargo.toml" > "${L}" 2>&1; RC=$?
  stamp cargo_test "${RC}" "$(grep -a -E '^test result' "${L}" | tail -n 1)" "${L}"
fi
# srv8899_gate —— pytest 与 mvn 两套件共用的「:8899 是本仓的、够新的、真就绪的排盘服务」判据。
#   不满足时 SRV_GATE_MSG 写原因并返回 1(调用方记 75 = 没法判,不是绿)。
#   ① 有进程在听 :8899;② 那是本仓 astropy 起的(别的项目 / 装好的运行时也会占这个口);③ 启动晚于引擎源码最近一次改动
#   (否则进程里是旧引擎);④ POST /healthz 回 ok —— 与需服务的金标同一判据(tests/srv_gate.py,同超时),
#   两边口径不同时金标会整模块 skip 而这里照样放行。
SRV_GATE_MSG=""
srv8899_gate(){
  local _pid _cmd _fresh _hz
  _pid="$(lsof -nP -iTCP:8899 -sTCP:LISTEN -t 2>/dev/null | head -n 1)"
  _cmd="$( [ -n "${_pid}" ] && ps -o command= -p "${_pid}" 2>/dev/null || true)"
  if [ -z "${_pid}" ]; then
    SRV_GATE_MSG=":8899 没有排盘服务(先 cd Horosa-Web && HOROSA_SKIP_UI_BUILD=1 ./start_horosa_local.sh)"; return 1
  fi
  if ! grep -qF -- "${REPO_ROOT}/Horosa-Web/astropy" <<< "${_cmd}"; then
    SRV_GATE_MSG=":8899 上跑的不是本仓的排盘服务(pid ${_pid}: ${_cmd:0:120}),不能拿外来引擎判本仓代码"; return 1
  fi
  if ! _fresh="$(/usr/bin/python3 "${STAMP}" engine-fresh --repo "${REPO_ROOT}" --pid "${_pid}" 2>&1)"; then
    SRV_GATE_MSG="${_fresh}"; return 1
  fi
  if ! _hz="$("${PY}" "${REPO_ROOT}/Horosa-Web/astropy/tests/srv_gate.py" 2>&1)"; then
    SRV_GATE_MSG=":8899 本仓服务未就绪(${_hz})"; return 1
  fi
  return 0
}
SRV_TESTS_CHECK="${INSTALLER_ROOT}/scripts/check_srv_required_tests.py"
if want pytest; then
  L="${LOGDIR}/pytest.log"; X="${LOGDIR}/pytest.junit.xml"; : > "${L}"; rm -f "${X}"
  # 需服务的金标(tests/ 里经 srv_gate 的文件)在服务不在线时会整模块 skip 而 pytest 照样退 0 —— 所以:
  #   先过服务门(过不了记 75);跑时 HOROSA_REQUIRE_SRV=1(不许 skip,离线即红);跑完按 junit 结果逐文件核「有用例且 0 skip」。
  if ! srv8899_gate; then
    echo "pytest 跳过:${SRV_GATE_MSG}" | tee -a "${L}"; stamp pytest 75 "${SRV_GATE_MSG}" "${L}"
  else
    ( cd "${REPO_ROOT}/Horosa-Web/astropy" && HOROSA_REQUIRE_SRV=1 PYTHONPATH=.:../flatlib-ctrad2:../vendor "${PY}" -m pytest -q tests/ -p no:cacheprovider -rs --junitxml="${X}" ) >> "${L}" 2>&1; RC=$?
    SUM="$(tail -n 1 "${L}")"
    if ! _SRVCHK="$(/usr/bin/python3 "${SRV_TESTS_CHECK}" junit --tests "${REPO_ROOT}/Horosa-Web/astropy/tests" --xml "${X}" 2>&1)"; then
      [ "${RC}" = 0 ] && RC=1
      SUM="${SUM} · 需服务金标没真跑:$(tr '\n' ' ' <<< "${_SRVCHK}")"
    fi
    echo "${_SRVCHK}" >> "${L}"
    stamp pytest "${RC}" "${SUM}" "${L}"
  fi
fi
if want mvn; then
  L="${LOGDIR}/mvn.log"; : > "${L}"
  # 四柱全年份域矩阵打 :8899 —— 必须是本仓的、够新的排盘服务(判据与 pytest 套件同一个 srv8899_gate)
  if ! srv8899_gate; then
    echo "mvn 跳过:${SRV_GATE_MSG}" | tee -a "${L}"; stamp mvn 75 "${SRV_GATE_MSG}" "${L}"
  else
    export JAVA_HOME="$(/usr/libexec/java_home -v 17 2>/dev/null || true)"; [ -n "${JAVA_HOME}" ] && export PATH="${JAVA_HOME}/bin:${PATH}"
    # 四个带测模块放进同一个 reactor 跑(聚合 pom + -pl … -am):兄弟模块引用当次从源码编译的产物,不吃 ~/.m2 里的件
    #   (逐个模块各自跑测试时 astrostudycn 链接的是本地仓库里的 astrostudy —— 可能是旧件,也可能是另一仓装进去的件,
    #   绿戳证明的就不是本仓 HEAD)。--fail-at-end:一个模块红了,不依赖它的模块照跑完。
    RC=0
    ( mvn -o -f "${REPO_ROOT}/Horosa-Web/astrostudysrv/pom.xml" test -pl boundless,basecomm,astrostudy,astrostudycn -am --fail-at-end ) >> "${L}" 2>&1 || RC=1
    # 摘要按模块取:reactor 日志里每个模块段以「--< 组:模块 >--」开头,取该段最后一行 surefire 汇总(Tests run: N, Failures: F, Errors: E)
    SUM="$(awk '
      /-< [^ :]+:[^ >]+ >-/ { if (match($0, /:[^ >]+ >/)) { m = substr($0, RSTART + 1, RLENGTH - 3); order[++n] = m } }
      /Tests run: [0-9]+, Failures: [0-9]+, Errors: [0-9]+/ && m != "" {
        match($0, /Tests run: [0-9]+, Failures: [0-9]+, Errors: [0-9]+/); t = substr($0, RSTART, RLENGTH)
        gsub(/Tests run: |Failures: |Errors: /, "", t); gsub(/, /, "/", t); last[m] = t }
      END { for (i = 1; i <= n; i++) if (order[i] != "astrostudysrv" && order[i] != "image") printf "%s:%s ", order[i], (order[i] in last ? last[order[i]] : "无测试") }
    ' "${L}")"
    stamp mvn "${RC}" "${SUM}" "${L}"
  fi
fi
if want jest_full; then
  L="${LOGDIR}/jest_full.log"
  ( cd "${REPO_ROOT}/Horosa-Web/astrostudyui" && ./node_modules/.bin/umi-test --maxWorkers="${HOROSA_BASELINE_JEST_WORKERS:-8}" ) > "${L}" 2>&1; RC=$?
  stamp jest_full "${RC}" "$(grep -a -E '^(Test Suites|Tests):' "${L}" | tr '\n' ' ')" "${L}"
fi
echo "== 基线戳:"; /usr/bin/python3 "${STAMP}" check --repo "${REPO_ROOT}"; exit $?
