#!/usr/bin/env bash
# release_lock.sh 自证(四向):① 并发第二条被拒(exit 75,报对方 pid)② 嵌套子脚本放行 ③ 残留锁(owner 已死)回收 ④ 退出即释放。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d "${TMPDIR:-/tmp}/horosa-lock-test.XXXXXX")"
trap 'rm -rf "${T}"' EXIT
export INSTALLER_ROOT="${T}/installer"; mkdir -p "${INSTALLER_ROOT}"
unset HOROSA_RELEASE_LOCK_OWNER HOROSA_RELEASE_LOCK_DIR
export HOROSA_RELEASE_LOCK=1
LOCK="${INSTALLER_ROOT}/build/.release.lock"
fail() { echo "❌ release_lock 自证:$*" >&2; exit 1; }

# ① 持锁者在跑时,第二条被拒且报对方 pid
( . "${HERE}/release_lock.sh"; horosa_release_lock "holder" || exit 9; echo "$$" > "${T}/holder.pid"; sleep 30 ) &
HOLDER=$!
for _ in $(seq 1 50); do [ -f "${T}/holder.pid" ] && break; sleep 0.1; done
[ -f "${LOCK}/owner" ] || fail "① 持锁者未建锁"
OUT="$( ( . "${HERE}/release_lock.sh"; horosa_release_lock "second" ) 2>&1 )"; RC=$?
[ "${RC}" = "75" ] || fail "① 第二条应 exit 75,实际 ${RC}"
printf '%s' "${OUT}" | grep -q "pid=$(cat "${T}/holder.pid")" || fail "① 拒绝信息未报对方 pid:${OUT}"
# ② 嵌套:导出 owner pid 的子脚本放行
( export HOROSA_RELEASE_LOCK_OWNER="$(cat "${T}/holder.pid")"; . "${HERE}/release_lock.sh"; horosa_release_lock "nested" ) || fail "② 嵌套子脚本应放行"
[ -f "${LOCK}/owner" ] || fail "② 嵌套放行不得动锁"
kill "${HOLDER}" 2>/dev/null; wait "${HOLDER}" 2>/dev/null
# ④ 持锁者退出(被 kill 时 trap 释放;若没释放则 ③ 负责回收)
# ③ 残留锁:owner 已死 → 回收并取到
mkdir -p "${LOCK}"; printf 'pid=%s\nlabel=dead\nat=x\n' "999999" > "${LOCK}/owner"
( . "${HERE}/release_lock.sh"; horosa_release_lock "reclaim" || exit 9; [ "$(sed -n 's/^pid=//p' "${LOCK}/owner")" = "$$" ] || exit 8 ) || fail "③ 残留锁未回收"
[ -d "${LOCK}" ] && fail "④ 子 shell 退出后锁应已释放"
# 开关:HOROSA_RELEASE_LOCK=0 跳过取锁(不建锁)
( export HOROSA_RELEASE_LOCK=0; . "${HERE}/release_lock.sh"; horosa_release_lock "off" 2>/dev/null ) || fail "开关 =0 应放行"
[ -d "${LOCK}" ] && fail "开关 =0 不应建锁"
echo "✅ release_lock 自证 4/4(并发拒 / 嵌套放行 / 残留回收 / 退出释放)+ 开关"
