#!/usr/bin/env bash
# release_lock.sh —— 打包链单飞锁(被 build_desktop_release.sh / package_runtime_payload.sh source)。
#
# 病理:两条打包流水线同时跑在同一个 build 目录里(两条同时起跑),各自对同一棵
#   build/runtime/runtime-payload 做重签 / 预编译 / 剥离,ad-hoc codesign 并发改写同一个 .so →
#   一条 rc=1、另一条产物不可信;日志里每个阶段行出现两次即是此病。
# 做法:目录锁 build/.release.lock(mkdir 原子建;owner 记 pid / 标签 / 时刻);退出 trap 释放。
#   · 锁在且 owner pid 还活着 → 拒跑(exit 75 = EX_TEMPFAIL),打印对方 pid / 标签 / 起跑时刻;
#   · 锁在但 owner pid 已死(上次被 kill -9 / 断电)→ 回收残留锁再取;
#   · 嵌套(build_desktop_release.sh 持锁后再调 package_runtime_payload.sh):父进程导出
#     HOROSA_RELEASE_LOCK_OWNER=<父 pid>,子脚本看到 owner 文件里的 pid 与之相同即视为同一条流水线,不再取锁、
#     也不装释放 trap(释放只认 pid == $$)。
# 开关:HOROSA_RELEASE_LOCK=0 跳过取锁(仅救急;自检 / 哨兵不认)。
# 用法:
#   . "${INSTALLER_ROOT}/scripts/release_lock.sh"
#   horosa_release_lock "<标签>" || exit $?
# 依赖调用方已定义 INSTALLER_ROOT(锁目录 = ${INSTALLER_ROOT}/build/.release.lock,可用 HOROSA_RELEASE_LOCK_DIR 覆盖,自检用)。

horosa_release_lock_release() {
  local lock="${HOROSA_RELEASE_LOCK_HELD_DIR:-}"
  [ -n "${lock}" ] || return 0
  if [ "$(sed -n 's/^pid=//p' "${lock}/owner" 2>/dev/null | head -n 1)" = "$$" ]; then
    rm -rf "${lock}"
  fi
  HOROSA_RELEASE_LOCK_HELD_DIR=""
  return 0
}

horosa_release_lock() {
  local label="${1:-release}"
  local lock="${HOROSA_RELEASE_LOCK_DIR:-${INSTALLER_ROOT:?INSTALLER_ROOT 未定义}/build/.release.lock}"
  if [ "${HOROSA_RELEASE_LOCK:-1}" != "1" ]; then
    echo "⚠️  HOROSA_RELEASE_LOCK=0:打包单飞锁已跳过(仅救急;同一 build 目录里绝不许第二条流水线)" >&2
    return 0
  fi
  local owner_pid
  owner_pid="$(sed -n 's/^pid=//p' "${lock}/owner" 2>/dev/null | head -n 1)"
  if [ -n "${HOROSA_RELEASE_LOCK_OWNER:-}" ] && [ -n "${owner_pid}" ] && [ "${owner_pid}" = "${HOROSA_RELEASE_LOCK_OWNER}" ]; then
    return 0   # 嵌套:同一条流水线的子脚本
  fi
  mkdir -p "$(dirname "${lock}")"
  local tries=0
  while ! mkdir "${lock}" 2>/dev/null; do
    owner_pid="$(sed -n 's/^pid=//p' "${lock}/owner" 2>/dev/null | head -n 1)"
    if [ -n "${owner_pid}" ] && kill -0 "${owner_pid}" 2>/dev/null; then
      echo "⛔ [release-lock] 另一条打包流水线正在跑:pid=${owner_pid} 标签=$(sed -n 's/^label=//p' "${lock}/owner" 2>/dev/null | head -n 1) 起于 $(sed -n 's/^at=//p' "${lock}/owner" 2>/dev/null | head -n 1)(锁 ${lock})。等它结束再跑;确认它已死后删掉锁目录即可。" >&2
      return 75
    fi
    tries=$((tries + 1))
    if [ "${tries}" -ge 3 ]; then
      echo "⛔ [release-lock] 锁目录残留且回收失败:${lock}" >&2
      return 75
    fi
    echo "⚠️  [release-lock] 回收残留锁(owner pid=${owner_pid:-?} 已不在):${lock}" >&2
    rm -rf "${lock}"
  done
  printf 'pid=%s\nlabel=%s\nat=%s\n' "$$" "${label}" "$(date '+%Y-%m-%d %H:%M:%S')" > "${lock}/owner"
  export HOROSA_RELEASE_LOCK_OWNER="$$"
  HOROSA_RELEASE_LOCK_HELD_DIR="${lock}"
  trap 'horosa_release_lock_release' EXIT
  return 0
}
