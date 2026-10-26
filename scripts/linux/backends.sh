#!/usr/bin/env bash
# 星阙本机计算服务(Python 排盘服务 + Java 后端)的极简起停:给批量验证(./horosa batch)和无图形界面的机器用。
# 只用 bash / curl(没有就用 python3 探测)/ ps / kill,Linux(x86_64 / arm64)与 macOS 都能跑;不碰端口以外的任何进程。
#
#   bash scripts/linux/backends.sh start [--pairs N] [--python-only]   起服务(已在跑的复用;--python-only 只起 Python,只算不需要 Java 的技法)
#   bash scripts/linux/backends.sh stop [--pairs N]                    停本脚本起的服务(按 pid 文件,且命令行核对是星阙的服务)
#   bash scripts/linux/backends.sh status [--pairs N]                  看端口在不在
# --pairs N:起 N 套(第 i 套端口 = 基准端口 + i)。Python 排盘服务一个进程只吃满一个核,批量要提速就多起几套,
#   再把打印出的 --backends 串交给 ./horosa batch(每套约 1 GB 内存:Java 堆上限 512 MB + Python 约 0.4 GB)。
#
# 端口:HOROSA_SERVER_PORT(Java,缺省 9999)· HOROSA_CHART_PORT(Python,缺省 8899)—— 与 ./horosa 同一对变量。
# 程序:HOROSA_PYTHON(缺省 python3,要 3.11+ 且装好依赖)· HOROSA_JAVA_BIN(缺省 java,要 17+)· HOROSA_JAR(后端 jar;缺省按下面顺序找)。
# 状态目录:HOROSA_BACKENDS_DIR(缺省 $HOROSA_HOME/backends,HOROSA_HOME 缺省 ~/.horosa):pid 文件与两份日志。
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 仓库检出:scripts/linux/ → 仓库根;批量运行包:包根下同样有 scripts/linux/
ROOT="$(cd "${HERE}/../.." && pwd)"
WEB="${ROOT}/Horosa-Web"

CHART_PORT="${HOROSA_CHART_PORT:-8899}"
SERVER_PORT="${HOROSA_SERVER_PORT:-9999}"
PY_BIN="${HOROSA_PYTHON:-python3}"
JAVA_BIN="${HOROSA_JAVA_BIN:-java}"
HOME_DIR="${HOROSA_HOME:-${HOME}/.horosa}"
STATE_DIR="${HOROSA_BACKENDS_DIR:-${HOME_DIR}/backends}"
WAIT_SECONDS="${HOROSA_BACKENDS_WAIT:-180}"

valid_port(){ case "$1" in ''|*[!0-9]*) return 1 ;; esac; [ "$1" -ge 1 ] && [ "$1" -le 65535 ]; }
valid_port "${CHART_PORT}" || { echo "HOROSA_CHART_PORT 不是 1–65535 的整数:${CHART_PORT}" >&2; exit 2; }
valid_port "${SERVER_PORT}" || { echo "HOROSA_SERVER_PORT 不是 1–65535 的整数:${SERVER_PORT}" >&2; exit 2; }
[ "${CHART_PORT}" != "${SERVER_PORT}" ] || { echo "两个端口不能相同:${CHART_PORT}" >&2; exit 2; }

BASE_CHART_PORT="${CHART_PORT}"
BASE_SERVER_PORT="${SERVER_PORT}"
# 第 i 套的端口与 pid / 日志文件(start / stop / status 都按它)
set_pair(){
  CHART_PORT=$((BASE_CHART_PORT + $1)); SERVER_PORT=$((BASE_SERVER_PORT + $1))
  PY_PID="${STATE_DIR}/python.${CHART_PORT}.pid"
  JAVA_PID="${STATE_DIR}/java.${SERVER_PORT}.pid"
  PY_LOG="${STATE_DIR}/python.${CHART_PORT}.log"
  JAVA_LOG="${STATE_DIR}/java.${SERVER_PORT}.log"
}

find_jar(){
  local c
  for c in "${HOROSA_JAR:-}" "${WEB}/astrostudysrv/astrostudyboot/target/astrostudyboot.jar" "${ROOT}/astrostudyboot.jar" \
           "${ROOT}"/runtime/*/bundle/astrostudyboot.jar; do
    if [ -n "${c}" ] && [ -f "${c}" ]; then printf '%s\n' "${c}"; return 0; fi
  done
  return 1
}

# 任何 HTTP 回应(含 4xx)= 在听;连不上 / 超时 = 不在。回环探测一律不走代理
http_up(){
  local url="$1"
  if command -v curl >/dev/null 2>&1; then
    local code
    code="$(curl -s --noproxy '*' -o /dev/null -m 3 --connect-timeout 1 -w '%{http_code}' -H 'ClientChannel: 1' -H 'ClientApp: 1' -H 'ClientVer: 1.0' "${url}" || true)"
    [ -n "${code}" ] && [ "${code}" != "000" ]
    return
  fi
  "${PY_BIN}" - "${url}" <<'PY' >/dev/null 2>&1
import sys, urllib.request, urllib.error
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
try:
    opener.open(urllib.request.Request(sys.argv[1], headers={'ClientChannel': '1', 'ClientApp': '1', 'ClientVer': '1.0'}), timeout=2)
except urllib.error.HTTPError:
    pass
except Exception:
    raise SystemExit(1)
PY
}
py_up(){ http_up "http://127.0.0.1:${CHART_PORT}/"; }
java_up(){ http_up "http://127.0.0.1:${SERVER_PORT}/"; }

pid_of(){ local f="$1" p; [ -s "${f}" ] || return 1; p="$(head -n1 "${f}" 2>/dev/null || true)"; case "${p}" in ''|*[!0-9]*) return 1 ;; esac; printf '%s\n' "${p}"; }
# pid 还活着且命令行确实是这个服务(进程号被系统复用给别的程序时不认)
pid_is(){ local p="$1" pat="$2" cmd; kill -0 "${p}" 2>/dev/null || return 1; cmd="$(ps -p "${p}" -o command= 2>/dev/null || true)"; grep -Eq -e "${pat}" <<< "${cmd}"; }
# Java 按本套端口参数认(jar 文件名可由 HOROSA_JAR 任取,不能拿它认;端口参数还把多套之间区分开)
java_pat(){ printf -- '--server\\.port=%s( |$)' "${SERVER_PORT}"; }

# 后台起一个命令:新会话(有 setsid 用它;macOS 没有就用 nohup),标准输入关掉,输出进日志;回 pid
spawn_bg(){
  local log="$1"; shift
  if command -v setsid >/dev/null 2>&1; then
    setsid "$@" </dev/null >>"${log}" 2>&1 &
  else
    nohup "$@" </dev/null >>"${log}" 2>&1 &
  fi
  printf '%s\n' "$!"
}

wait_up(){
  local what="$1" fn="$2" pidf="$3" pat="$4" log="$5" i=0 p
  while [ "${i}" -lt "${WAIT_SECONDS}" ]; do
    if "${fn}"; then return 0; fi
    p="$(pid_of "${pidf}" || true)"
    if [ -z "${p}" ] || ! pid_is "${p}" "${pat}"; then
      echo "${what} 启动后退出了;日志 ${log} 最后几行:" >&2
      tail -n 20 "${log}" >&2 || true
      return 1
    fi
    sleep 1; i=$((i + 1))
  done
  echo "${what} ${WAIT_SECONDS} 秒内没就绪(日志 ${log});可设 HOROSA_BACKENDS_WAIT 加长" >&2
  return 1
}

start_python(){
  if py_up; then echo "Python 排盘服务已在 :${CHART_PORT}(复用)"; return 0; fi
  [ -f "${WEB}/astropy/websrv/webchartsrv.py" ] || { echo "找不到 ${WEB}/astropy/websrv/webchartsrv.py" >&2; return 1; }
  command -v "${PY_BIN}" >/dev/null 2>&1 || { echo "找不到 Python:${PY_BIN}(设 HOROSA_PYTHON)" >&2; return 1; }
  "${PY_BIN}" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' \
    || { echo "Python 要 3.11+(现在是 $("${PY_BIN}" -V 2>&1))" >&2; return 1; }
  local p
  p="$(cd "${WEB}" && spawn_bg "${PY_LOG}" env PYTHONPATH="${WEB}/flatlib-ctrad2:${WEB}/astropy:${WEB}/vendor" HOROSA_CHART_PORT="${CHART_PORT}" "${PY_BIN}" "${WEB}/astropy/websrv/webchartsrv.py")"
  printf '%s\n' "${p}" >"${PY_PID}"
  wait_up "Python 排盘服务" py_up "${PY_PID}" 'webchartsrv' "${PY_LOG}" || return 1
  echo "Python 排盘服务已起在 :${CHART_PORT}(pid ${p})"
}

start_java(){
  if java_up; then echo "Java 后端已在 :${SERVER_PORT}(复用)"; return 0; fi
  local jar p
  jar="$(find_jar)" || { echo "找不到后端 jar:先 mvn -f Horosa-Web/astrostudysrv/pom.xml clean install -DskipTests,或设 HOROSA_JAR" >&2; return 1; }
  command -v "${JAVA_BIN}" >/dev/null 2>&1 || { echo "找不到 Java:${JAVA_BIN}(设 HOROSA_JAVA_BIN,要 JDK 17+)" >&2; return 1; }
  mkdir -p "${STATE_DIR}/mongo-fallback"
  # 参数与桌面 / 本地网页版起后端同一组(不连 Mongo / Redis:连不上自动走本地文件缓存)
  p="$(spawn_bg "${JAVA_LOG}" env HOROSA_DESKTOP_MONGO_OPTIONAL=1 HOROSA_MONGO_FALLBACK_DIR="${STATE_DIR}/mongo-fallback" \
    HOROSA_ENABLE_STARTUP_CRON=0 HOROSA_ENABLE_STARTUP_TRANSGROUP_INIT=0 needtranslog=false SPRING_MAIN_LAZY_INITIALIZATION=true \
    "${JAVA_BIN}" ${HOROSA_JAVA_OPTS:--Xms128m -Xmx512m} -XX:+DisableExplicitGC -Djava.awt.headless=true -Duser.language=zh -Duser.country=CN \
    -Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8 -Dparamhash.cache.redis.enable=false -Dcachehelper.needcache=false -Dhorosa.cache.lazyinit=true \
    -Dspring.main.banner-mode=off -jar "${jar}" \
    --server.port="${SERVER_PORT}" --server.address=127.0.0.1 --astrosrv="http://127.0.0.1:${CHART_PORT}" \
    --mongodb.ip=127.0.0.1 --redis.ip=127.0.0.1 --paramhash.cache.redis.enable=false)"
  printf '%s\n' "${p}" >"${JAVA_PID}"
  wait_up "Java 后端" java_up "${JAVA_PID}" "$(java_pat)" "${JAVA_LOG}" || return 1
  echo "Java 后端已起在 :${SERVER_PORT}(pid ${p})"
}

stop_one(){
  local what="$1" pidf="$2" pat="$3" p i=0
  p="$(pid_of "${pidf}" || true)"
  if [ -z "${p}" ]; then echo "${what}:没有本脚本起的进程"; return 0; fi
  if ! pid_is "${p}" "${pat}"; then echo "${what}:pid ${p} 已不在(或已不是星阙服务),清掉 pid 文件"; mv -f "${pidf}" "${pidf}.stale" 2>/dev/null || true; return 0; fi
  kill "${p}" 2>/dev/null || true
  while pid_is "${p}" "${pat}" && [ "${i}" -lt 20 ]; do sleep 0.5; i=$((i + 1)); done
  if pid_is "${p}" "${pat}"; then kill -9 "${p}" 2>/dev/null || true; fi
  mv -f "${pidf}" "${pidf}.stopped" 2>/dev/null || true
  echo "${what}:已停(pid ${p})"
}

cmd="${1:-status}"
[ "$#" -gt 0 ] && shift
PAIRS=1; PYTHON_ONLY=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --pairs) PAIRS="${2:-}"; shift 2 || { echo "--pairs 后面要跟套数" >&2; exit 2; } ;;
    --python-only) PYTHON_ONLY=1; shift ;;
    *) echo "不认识的参数 $1" >&2; exit 2 ;;
  esac
done
case "${PAIRS}" in ''|*[!0-9]*) echo "--pairs 要 1–32 的整数" >&2; exit 2 ;; esac
{ [ "${PAIRS}" -ge 1 ] && [ "${PAIRS}" -le 32 ]; } || { echo "--pairs 要 1–32 的整数" >&2; exit 2; }
# 两组端口区间不能交叠(第 i 套的 Java 口撞上第 j 套的 Python 口)
lo_c="${BASE_CHART_PORT}"; hi_c=$((BASE_CHART_PORT + PAIRS - 1)); lo_s="${BASE_SERVER_PORT}"; hi_s=$((BASE_SERVER_PORT + PAIRS - 1))
if [ "${hi_c}" -gt 65535 ] || [ "${hi_s}" -gt 65535 ] || { [ "${lo_c}" -le "${hi_s}" ] && [ "${lo_s}" -le "${hi_c}" ]; }; then
  echo "端口区间交叠或越界:Python ${lo_c}–${hi_c} / Java ${lo_s}–${hi_s}(换基准端口或减少套数)" >&2; exit 2
fi
mkdir -p "${STATE_DIR}"
SPEC=""
i=0
while [ "${i}" -lt "${PAIRS}" ]; do
  set_pair "${i}"
  case "${cmd}" in
    start)
      start_python || exit 1
      if [ "${PYTHON_ONLY}" != "1" ]; then start_java || exit 1; fi
      ;;
    stop)
      stop_one "Java 后端 :${SERVER_PORT}" "${JAVA_PID}" "$(java_pat)"
      stop_one "Python 排盘服务 :${CHART_PORT}" "${PY_PID}" 'webchartsrv'
      ;;
    status)
      if py_up; then echo "Python 排盘服务 :${CHART_PORT} 在"; else echo "Python 排盘服务 :${CHART_PORT} 不在"; fi
      if java_up; then echo "Java 后端 :${SERVER_PORT} 在"; else echo "Java 后端 :${SERVER_PORT} 不在"; fi
      ;;
    *) echo "用法: bash scripts/linux/backends.sh start|stop|status [--pairs N] [--python-only]" >&2; exit 2 ;;
  esac
  SPEC="${SPEC}${SPEC:+,}${SERVER_PORT}:${CHART_PORT}"
  i=$((i + 1))
done
if [ "${cmd}" = "start" ] && [ "${PAIRS}" -gt 1 ]; then
  echo "批量用:./horosa batch … --backends ${SPEC}"
fi
exit 0
