#!/usr/bin/env bash
# Release pre-flight self-check —— 在发布前运行,把历次流程复盘发现的漏洞编码成可执行检查。
# 任何一项失败即 exit 1。新检查项写成段函数,登记进登记表(见下「结构」)。
#
#   用法:  Horosa_Desktop_Installer/scripts/release_preflight.sh [--list | --only 段号[,段号…] | --from 段号]
#   跳过某项:对应 env(见各检查),仅在你确认无误时用。
#
# 设计原则:能强制的就强制(脚本),不要只写在文档里靠自觉。
#
# 结构:本文件是薄入口(装载公共库 → 按登记表依次执行各段 → 汇总),检查本体在 preflight/ 下:
#   preflight/lib.sh              公共变量与助手(ok / bad / warn / pipe_has / PF_STRIP_PRIVATE …)、登记表装载与执行
#   preflight/registry.tsv        段登记表:一行一段「id<TAB>段号<TAB>段文件」,按执行顺序排列
#   preflight/segments/<域>.sh    段函数 seg_<id>(),按域分文件
#   新增一段:在对应域文件里写 seg_<id>() { … },在登记表里按执行位置插一行;漏登记 / 登记了没定义都会报红。
#   段文件在开跑前一次装载进内存,跑的过程中改段文件不影响本轮;本入口仍是边读边跑,跑的时候别改它。
set -uo pipefail   # 故意不开 -e:要跑完所有检查再汇总

# 退出码:0 = 全过 · 1 = 有 ❌(或中途意外终止)· 2 = 参数错(段号不在登记表 / 缺值 / 一段都没选中)。
#   一律经 pf_exit 退出(lib.sh 的 EXIT trap 收拾本轮临时目录;没走 pf_exit 却以 0 退出的按 1 计)。
. "$(dirname "$0")/preflight/lib.sh"
pf_parse_args "$@" || pf_exit 2
if [ "${PF_MODE}" = "list" ]; then pf_list; pf_exit 0; fi
[ -n "${VERSION}" ] || { echo "无法读取 package.json version,终止" >&2; pf_exit 2; }
echo "== Release pre-flight: version ${VERSION} / runtime ${RUNTIME_VERSION} =="
pf_run || pf_exit 2

echo "== 结果 =="
if [ -n "${PF_ONLY}${PF_FROM}" ]; then echo "(按 --only / --from 筛选:本轮跑了 ${PF_RAN} 段)"; fi
if [ "${fail}" -ne 0 ]; then echo "pre-flight 有 ❌,先修再发。" >&2; pf_exit 1; fi
echo "pre-flight 全部通过 ✅(注意:功能层 e2e 仍需另测,如 AI 用真 key、八字切换显示)。"
pf_exit 0
