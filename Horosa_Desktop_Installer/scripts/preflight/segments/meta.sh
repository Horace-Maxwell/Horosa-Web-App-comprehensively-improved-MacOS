#!/usr/bin/env bash
# 发布前自检 · 文档与自检
# 由 preflight/lib.sh 按登记表装载;只定义函数 seg_<id>(),不直接执行。段号用 ${PF_NO}(登记表第二列)。

seg_277() {
# ── [${PF_NO}] 本脚本自身:不许再出现「管道接 grep -q」(pipefail 下大输入靠前命中 = 缺席型检查假绿 / 存在型检查假红) ──
# 病症:本脚本开着 pipefail。`产生器 | grep -q 形态 && bad` 这类「旧坏形态回潮即报红」的缺席型检查,一旦回潮位置靠前、
#   产生器输出又超过管道缓冲(64KB),grep 命中即退、产生器吃 SIGPIPE、整条管道按失败计 → 走「未命中」= 回潮了却判通过。
#   同形态的存在型检查则会无故报红。全部改走顶部的 pipe_has(计数式,读完全部输入);此处锁死不许回潮,并用判别向量自证。
echo "[${PF_NO}] 发布自检自身:零「管道接 grep -q」+ pipe_has 判别向量"
S277_BAD=0
S277_SELF="$(pf_self)"
# (bash 3.2 解析不了「命令替换里套 heredoc、体内又有不成对引号 / 括号」,所以输出走临时文件,不包在 $( ) 里)
S277_TMP="$(mktemp "${PF_TMP}/s277_tmp.XXXXXX")"
python3 - "${PF_SELF_FILES[@]}" > "${S277_TMP}" <<'PY277'
import re, sys
rx = re.compile(r'(?<![|&])\|\s*(?:e|f)?grep\s+(?:-[A-Za-z]+\s+)*-[A-Za-z]*q')
hd = re.compile(r'<<-?\s*([\'"]?)([A-Za-z_][A-Za-z0-9_]*)\1')
bad = []
for path in sys.argv[1:]:   # 入口 + 公共库 + 登记表 + 本轮装载的全部段文件
    lines = open(path, encoding='utf-8').read().split('\n')
    rel = path.split('/scripts/', 1)[-1]
    tag = None
    for i, l in enumerate(lines):
        if tag is not None:
            if l.strip() == tag: tag = None
            continue
        if l.lstrip().startswith('#'): continue
        if rx.search(l): bad.append('%s:%d' % (rel, i + 1))
        m = hd.search(l)
        if m: tag = m.group(2)
print(','.join(bad[:12]) + ('…' if len(bad) > 12 else '') if bad else 'none')
PY277
S277_OUT="$(cat "${S277_TMP}" 2>/dev/null)"; rm -f "${S277_TMP}"
[ "${S277_OUT}" = "none" ] || { bad "[${PF_NO}] 🔴 代码行里又出现「管道接 grep -q」(行 ${S277_OUT});改用 pipe_has"; S277_BAD=1; }
grep -qF 'pipe_has(){ local n; n="$(grep -ac "$@" 2>/dev/null || true)"; [ "${n:-0}" -gt 0 ] 2>/dev/null; }' "${S277_SELF}" \
  || { bad "[${PF_NO}] 🔴 pipe_has 计数式定义丢失或被改回提前退出形态"; S277_BAD=1; }
# 判别向量:>64KB 的流、命中在第一行。pipe_has 必须命中;同一条流未命中的词必须不命中;带 -F / -v / -x 的参数形态同样成立。
S277_BIG="$(python3 -c "print('NEEDLE(x)'); print(('filler line ' * 8 + '\n') * 1400, end='')")"
printf '%s\n' "${S277_BIG}" | pipe_has "NEEDLE" || { bad "[${PF_NO}] 🔴 pipe_has 在大输入靠前命中上未命中"; S277_BAD=1; }
printf '%s\n' "${S277_BIG}" | pipe_has -F "NEEDLE(x)" || { bad "[${PF_NO}] 🔴 pipe_has -F 形态未命中"; S277_BAD=1; }
printf '%s\n' "${S277_BIG}" | pipe_has -x "NEEDLE(x)" || { bad "[${PF_NO}] 🔴 pipe_has -x 形态未命中"; S277_BAD=1; }
printf '%s\n' "${S277_BIG}" | pipe_has "ABSENT_TOKEN" && { bad "[${PF_NO}] 🔴 pipe_has 对不存在的词误命中"; S277_BAD=1; }
printf 'only\n' | pipe_has -v "only" && { bad "[${PF_NO}] 🔴 pipe_has -v 语义不对(全部行都匹配时应为未命中)"; S277_BAD=1; }
[ "${S277_BAD}" = "0" ] && ok "[${PF_NO}] 代码行零「管道接 grep -q」+ pipe_has 定义在位 + 判别向量五条(大输入靠前命中 / -F / -x / 不误命中 / -v)"
}
