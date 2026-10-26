#!/usr/bin/env bash
# release_lock.sh —— 打包链单飞锁(被 build_desktop_release.sh / package_runtime_payload.sh source)。
#
# 病理:两条打包流水线同时跑在同一个 build 目录里(两条同时起跑),各自对同一棵
#   build/runtime/runtime-payload 做重签 / 预编译 / 剥离,ad-hoc codesign 并发改写同一个 .so →
#   一条 rc=1、另一条产物不可信;日志里每个阶段行出现两次即是此病。
# 做法:内核文件锁(flock)。取锁时起一个小守锁进程(python3)对 build/.release.lock/lock 加排它锁、
#   把 pid / 标签 / 时刻写进锁文件,然后一直守着,直到持锁脚本($$)退出才放手 —— 锁随进程走:
#   · 原子:两条同时起跑,内核只放一条进来(目录锁「建目录 → 写 owner」之间的窗口没有了);
#   · 不挂 EXIT trap:持锁脚本正常结束 / 出错 / 被 kill -9,守锁进程看到它不在了就退出,内核自动放锁。
#     (bash 3.2 下 set -euo pipefail 的脚本一旦挂 EXIT trap,未绑定变量这类错误的退出码会变成 0 ——
#      打包脚本半途停下却报成功;所以这里绝不挂。)
#   · 没有残留锁要回收、也没有 pid 复用误判:锁是内核的,进程一死就没了。
#   · 锁被占 → 拒跑(exit 75 = EX_TEMPFAIL),打印对方 pid / 标签 / 起跑时刻;
#   · 嵌套(build_desktop_release.sh 持锁后再调 package_runtime_payload.sh):父进程导出
#     HOROSA_RELEASE_LOCK_OWNER=<父 pid>,子脚本取锁时若占锁的正是这个 pid,即视为同一条流水线,放行。
# 开关:HOROSA_RELEASE_LOCK=0 跳过取锁(仅救急;自检 / 哨兵不认)。
# 用法:
#   . "${INSTALLER_ROOT}/scripts/release_lock.sh"
#   horosa_release_lock "<标签>" || exit $?
# 依赖调用方已定义 INSTALLER_ROOT(锁目录 = ${INSTALLER_ROOT}/build/.release.lock,可用 HOROSA_RELEASE_LOCK_DIR 覆盖,自检用)。

RELEASE_LOCK_HOLDER_PID=""

# 提前放锁(可选;不调也行 —— 持锁脚本一退出守锁进程就自己走)
horosa_release_lock_release() {
  if [ -n "${RELEASE_LOCK_HOLDER_PID:-}" ]; then
    kill "${RELEASE_LOCK_HOLDER_PID}" 2>/dev/null || true
    RELEASE_LOCK_HOLDER_PID=""
  fi
  { exec 9<&-; } 2>/dev/null || true
  return 0
}

horosa_release_lock() {
  local label="${1:-release}"
  local lockdir="${HOROSA_RELEASE_LOCK_DIR:-${INSTALLER_ROOT:?INSTALLER_ROOT 未定义}/build/.release.lock}"
  if [ "${HOROSA_RELEASE_LOCK:-1}" != "1" ]; then
    echo "⚠️  HOROSA_RELEASE_LOCK=0:打包单飞锁已跳过(仅救急;同一 build 目录里绝不许第二条流水线)" >&2
    return 0
  fi
  mkdir -p "${lockdir}" || { echo "⛔ [release-lock] 建不了锁目录:${lockdir}" >&2; return 75; }
  local py="/usr/bin/python3"
  [ -x "${py}" ] || py="$(command -v python3 || true)"
  [ -n "${py}" ] || { echo "⛔ [release-lock] 找不到 python3(守锁进程要它)" >&2; return 75; }
  # 守锁进程:取到锁 → 打一行 ok <自己 pid>,守到持锁脚本退出;取不到 → 打一行 busy <锁文件里的 pid 标签 时刻> 后退出
  local attempt=0 status="" info="" other=""
  while :; do
    exec 9< <("${py}" -c '
import fcntl, os, sys, time
path, owner, label = sys.argv[1], int(sys.argv[2]), sys.argv[3]
f = open(path, "a+")
try:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError:
    f.seek(0)
    print("busy " + " ".join(f.read().split()), flush=True)
    sys.exit(0)
f.seek(0); f.truncate()
f.write("pid=%d\nlabel=%s\nat=%s\n" % (owner, label, time.strftime("%Y-%m-%d %H:%M:%S"))); f.flush()
print("ok %d" % os.getpid(), flush=True)
sys.stdout.close()
while True:
    try:
        os.kill(owner, 0)
    except ProcessLookupError:
        break
    except PermissionError:
        pass
    time.sleep(0.5)
' "${lockdir}/lock" "$$" "${label}" 2>/dev/null)
    status=""
    IFS= read -r -t 20 status <&9 || status=""
    case "${status}" in
      "ok "*)
        RELEASE_LOCK_HOLDER_PID="${status#ok }"
        export HOROSA_RELEASE_LOCK_OWNER="$$"
        return 0
        ;;
      "busy "*)
        { exec 9<&-; } 2>/dev/null || true
        info="${status#busy }"
        other="$(printf '%s\n' "${info}" | tr ' ' '\n' | sed -n 's/^pid=//p' | head -n 1)" || other=""
        if [ -n "${HOROSA_RELEASE_LOCK_OWNER:-}" ] && [ "${other}" = "${HOROSA_RELEASE_LOCK_OWNER}" ]; then
          return 0   # 嵌套:同一条流水线的子脚本
        fi
        # 占锁的进程刚退出、守锁进程还没来得及放手(至多半秒)→ 稍等再取
        if [ -n "${other}" ] && ! kill -0 "${other}" 2>/dev/null && [ "${attempt}" -lt 8 ]; then
          attempt=$((attempt + 1)); sleep 0.5; continue
        fi
        echo "⛔ [release-lock] 另一条打包流水线正在跑:${info:-(锁文件里没有信息)}(锁 ${lockdir}/lock)。等它结束再跑;锁随进程走,它一退出锁就自己放开。" >&2
        return 75
        ;;
      *)
        { exec 9<&-; } 2>/dev/null || true
        echo "⛔ [release-lock] 取锁失败(守锁进程没有回话):${lockdir}/lock" >&2
        return 75
        ;;
    esac
  done
}
