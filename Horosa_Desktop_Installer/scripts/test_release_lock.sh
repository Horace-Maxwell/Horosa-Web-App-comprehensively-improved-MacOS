#!/usr/bin/env bash
# release_lock.sh 自证(全部用真独立进程,不用子 shell —— 子 shell 的 $$ 是父进程,测不到跨进程):
#  ① 持锁者在跑时,第二条被拒(exit 75,报对方 pid)
#  ② 嵌套:导出 HOROSA_RELEASE_LOCK_OWNER=<持锁 pid> 的子脚本放行
#  ③ 持锁者被 kill -9 → 锁随进程走,下一条几秒内取到
#  ④ 持锁者正常退出 → 下一条取到
#  ⑤ 持锁脚本在 set -euo pipefail 下碰到未绑定变量 → 退出码非 0(不被吞成 0)
#  ⑥ 十条同时起跑 → 任一时刻至多一条持锁
#  + 开关 HOROSA_RELEASE_LOCK=0 跳过取锁
set -u
# [exit-guard] bash 3.2:set -u 因未赋值变量中止时,EXIT trap 里拿到的 $? 是 0(失败会被报成成功)。显式 exit 都经下面的
#   exit 记一笔;进 EXIT 时没记过 = 中止,按失败计。EXIT trap 一律写成 trap 'hx_on_exit <原处理>' EXIT(处理函数里读到的 $?
#   已是改判后的值);脚本末尾必须显式 exit。检查器 check_shell_exit_guard.py 机检。
HX_EXITED=0; exit(){ local _hx_s=$?; HX_EXITED=1; if [ "$#" -eq 0 ]; then builtin exit "${_hx_s}"; fi; builtin exit "$@"; }
hx_status(){ return "$1"; }
hx_on_exit(){ local _hx_r=$?; if [ "${_hx_r}" = "0" ] && [ "${HX_EXITED}" != "1" ]; then _hx_r=1; fi; set +e; hx_status "${_hx_r}"; "$@"; builtin exit "${_hx_r}"; }
HERE="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d "${TMPDIR:-/tmp}/horosa-lock-test.XXXXXX")"
PIDS=""
cleanup() { for p in ${PIDS}; do kill -9 "${p}" 2>/dev/null; done; rm -rf "${T}"; }
trap 'hx_on_exit cleanup' EXIT
export INSTALLER_ROOT="${T}/installer"; mkdir -p "${INSTALLER_ROOT}"
unset HOROSA_RELEASE_LOCK_OWNER HOROSA_RELEASE_LOCK_DIR
export HOROSA_RELEASE_LOCK=1
LIB="${HERE}/release_lock.sh"
fail() { echo "❌ release_lock 自证:$*" >&2; exit 1; }
wait_file() { for _ in $(seq 1 100); do [ -f "$1" ] && return 0; sleep 0.1; done; return 1; }
acquire_once() { bash -c '. "$1"; horosa_release_lock "$2"' _ "${LIB}" "$1"; }

# ① 持锁者(独立 bash 进程)在跑 → 第二条被拒且报对方 pid
bash -c '. "$1"; horosa_release_lock holder || exit 9; echo "$$" > "$2"; sleep 60' _ "${LIB}" "${T}/holder.pid" &
HOLDER=$!; PIDS="${PIDS} ${HOLDER}"
wait_file "${T}/holder.pid" || fail "① 持锁者没取到锁"
OUT="$(acquire_once second 2>&1)"; RC=$?
[ "${RC}" = "75" ] || fail "① 第二条应 exit 75,实际 ${RC}"
grep -q "pid=$(cat "${T}/holder.pid")" <<< "${OUT}" || fail "① 拒绝信息未报对方 pid:${OUT}"
# ② 嵌套:导出持锁 pid 的子脚本放行
HOROSA_RELEASE_LOCK_OWNER="$(cat "${T}/holder.pid")" acquire_once nested >/dev/null 2>&1 || fail "② 嵌套子脚本应放行"
# ③ 持锁者被 kill -9 → 几秒内下一条取到
kill -9 "${HOLDER}" 2>/dev/null; wait "${HOLDER}" 2>/dev/null
GOT=0
for _ in $(seq 1 10); do if acquire_once after-kill >/dev/null 2>&1; then GOT=1; break; fi; sleep 0.5; done
[ "${GOT}" = "1" ] || fail "③ 持锁者被 kill -9 后锁没放开"
# ④ 持锁者正常退出 → 下一条取到(acquire_once 本身就是「取到即退出」,再取一次)
acquire_once again >/dev/null 2>&1 || fail "④ 持锁者正常退出后下一条没取到"
# ⑤ set -euo pipefail 下持锁后碰未绑定变量 → 退出码非 0
bash -c 'set -euo pipefail; . "$1"; horosa_release_lock strict || exit 9; echo "${NO_SUCH_VAR_FOR_LOCK_TEST}"; exit 0' _ "${LIB}" >/dev/null 2>&1; RC=$?
[ "${RC}" != "0" ] || fail "⑤ 未绑定变量的错误被吞成退出码 0"
# ⑥ 十条同时起跑:任一时刻至多一条持锁
: > "${T}/overlap.log"
for i in $(seq 1 10); do
  bash -c '. "$1"; horosa_release_lock "race$3" 2>/dev/null || exit 0; echo "in $$" >> "$2"; sleep 0.3; echo "out $$" >> "$2"' _ "${LIB}" "${T}/overlap.log" "${i}" &
  PIDS="${PIDS} $!"
done
wait
python3 - "${T}/overlap.log" <<'PY' || fail "⑥ 出现两条同时持锁:$(tr '\n' ' ' < "${T}/overlap.log")"
import sys
held = None
for line in open(sys.argv[1]):
    kind, pid = line.split()
    if kind == "in":
        if held is not None:
            sys.exit(1)
        held = pid
    else:
        if held != pid:
            sys.exit(1)
        held = None
PY
grep -q '^in ' "${T}/overlap.log" || fail "⑥ 十条里一条都没取到锁"
# 开关:HOROSA_RELEASE_LOCK=0 跳过取锁(不建锁文件)
rm -rf "${INSTALLER_ROOT}/build"
HOROSA_RELEASE_LOCK=0 acquire_once off >/dev/null 2>&1 || fail "开关 =0 应放行"
[ -e "${INSTALLER_ROOT}/build/.release.lock/lock" ] && fail "开关 =0 不应建锁"
echo "✅ release_lock 自证 6/6(并发拒 / 嵌套放行 / kill -9 后放开 / 退出放开 / 未绑定变量不吞退出码 / 十条同跑不重叠)+ 开关"
exit 0
