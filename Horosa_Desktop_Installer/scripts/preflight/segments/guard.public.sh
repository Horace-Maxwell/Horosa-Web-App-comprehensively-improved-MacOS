#!/usr/bin/env bash
# 发布前自检 · 保密与投影(续)
# 由 preflight/lib.sh 按登记表装载;只定义函数 seg_<id>(),不直接执行。

seg_307() {
# ── [287] 零事故台账号 / 零工单号标记(公开 issue 一律写作 [Windows #NN];十六进制颜色 [#6366f1] 一类不算)+ 禁词表含两模式 ──
echo "[287] 零台账号 / 零工单号标记 + 禁词表含两模式"
S287_BAD=0
S287_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E -e 'FL-[0-9]{8}' -e '\[#[0-9]{2,3}(\]|[^0-9A-Fa-f])' -- . ':(exclude)Horosa-Web/vendor/' ':(exclude)*.png' ':(exclude)*.icns' ':(exclude)*.jar' ':(exclude)*.gz' ':(exclude)*.zip' ':(exclude)*.woff' ':(exclude)*.woff2' ':(exclude)*.ttf' ':(exclude)*.sqlite' ':(exclude)*.se1' 2>/dev/null | head -5)"
[ -n "${S287_HITS}" ] && { printf '%s\n' "${S287_HITS}" | sed 's/^/    /'; bad "[287] 工作树含台账号 / 工单号标记"; S287_BAD=1; }
S287_PAT="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/.secrecy_patterns.sh"
if [ -f "${S287_PAT}" ]; then
  grep -qF "'FL-[0-9]{8}'" "${S287_PAT}" 2>/dev/null && grep -qF '#[0-9]{2,3}(' "${S287_PAT}" 2>/dev/null || { bad "[287] 本地禁词表缺台账号 / 工单号两模式"; S287_BAD=1; }
fi
[ "${S287_BAD}" = "0" ] && ok "[287] 零台账号 / 零工单号标记;禁词表含两模式"
}

seg_u40() {
# [40] 本地工作文件不入库
echo "[40] 本地工作文件未入库"
S40_BAD=0
for f in AGENTS.md CLAUDE.md Horosa-Web/AGENTS.md Horosa-Web/CLAUDE.md; do
  if git -C "${REPO_ROOT}" ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    bad "[40] ${f} 被 git 跟踪(应保持本地,见 .gitignore)"; S40_BAD=1
  fi
done
[ "${S40_BAD}" = "0" ] && ok "[40] 本地工作文件未入库"
}

seg_u45() {
# [45] 发布敏感词扫描 (2026-06-11): 工作树全部 tracked 内容 + origin/main..HEAD 每个
#      commit 树 + 全部 commit message,逐一过本地敏感词模式表(token/调试标记/工作
#      笔记词汇等,表不入库)。模式表丢失 = 视为未审,直接红(fail-closed)。
echo "[45] 发布敏感词扫描(工作树 + 未推区间)"
S45_BAD=0
S45_PAT="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/.secrecy_patterns.sh"
if [ ! -f "${S45_PAT}" ]; then
  bad "[45] 本地敏感词模式表缺失(${S45_PAT} 不入库,换机/重 clone 后须先恢复) —— 缺表=未审,不放行"
else
  # shellcheck disable=SC1090
  . "${S45_PAT}"
  S45_A_ARGS=()
  for S45_P in "${HOROSA_FORBIDDEN_A[@]}"; do S45_A_ARGS+=(-e "${S45_P}"); done
  S45_VENDOR_EXCL=":(exclude)Horosa-Web/vendor/"
  # 玄学史(xuanshi)data 永久豁免本扫描(2026-06-28 用户拍板·制度化):公有古籍编纂模块,
  #   其历史名词经人工逐条核实纯属公有典籍引用、无任何受限内容 → 整 data 目录永不入扫描。
  #   (注:本注释刻意不写具体历史名词,以免本 preflight 文件自身命中扫描。)
  S45_XUANSHI_EXCL=":(exclude)Horosa-Web/astropy/astrostudy/xuanshi/data/"
  # -a 强制文本扫描(替换原 -I:它会静默跳过被判 binary 的 unicode 密集 JS,曾致盲漏过中文禁词);
  # 真二进制资产按扩展名排除,防随机字节伪命中。
  # 星历 .se1 / sqlite 是随机字节的二进制资产:按扩展名排除,否则任何短模式(如 [#NN)都会伪命中
  S45_BIN_EXCL=(":(exclude)*.png" ":(exclude)*.icns" ":(exclude)*.jar" ":(exclude)*.gz" ":(exclude)*.zip" ":(exclude)*.woff" ":(exclude)*.woff2" ":(exclude)*.ttf" ":(exclude)*.ico" ":(exclude)*.jpg" ":(exclude)*.dat" ":(exclude)*.se1" ":(exclude)*.sqlite")
  # ① 工作树 tracked 内容(含未提交修改)
  S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E "${S45_A_ARGS[@]}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | head -5)"
  [ -n "${S45_HITS}" ] && { bad "[45] 工作树命中敏感词:"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
  for S45_ROW in "${HOROSA_FORBIDDEN_B[@]}"; do
    S45_P="${S45_ROW%%$'\t'*}"; S45_ALLOW="${S45_ROW#*$'\t'}"
    S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E "${S45_P}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | grep -Ev "${S45_ALLOW}" | head -5)"
    [ -n "${S45_HITS}" ] && { bad "[45] 工作树命中敏感词(豁免外): ${S45_P}"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
  done
  # ①' W 组(机器路径/PII/内部代号):仅工作树查 —— 保证最新快照干净;旧历史 + tag
  #     已公开的同类痕迹归 filter-repo 全历史改写(碰 GitHub 决策),不在此误红历史。
  if [ "${#HOROSA_FORBIDDEN_W[@]}" -gt 0 ]; then
    S45_W_ARGS=()
    for S45_P in "${HOROSA_FORBIDDEN_W[@]}"; do S45_W_ARGS+=(-e "${S45_P}"); done
    S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -F "${S45_W_ARGS[@]}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | head -5)"
    [ -n "${S45_HITS}" ] && { bad "[45] 工作树命中机器路径/PII(W 组):"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
  fi
  # ② 未推区间每个 commit 的树(防「工作树已清但历史 blob 仍带」—— 推上去即留痕)
  for S45_C in $(git -C "${REPO_ROOT}" rev-list origin/main..HEAD 2>/dev/null); do
    S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E "${S45_A_ARGS[@]}" "${S45_C}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | head -5)"
    [ -n "${S45_HITS}" ] && { bad "[45] 未推 commit ${S45_C:0:9} 树内命中敏感词:"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
    for S45_ROW in "${HOROSA_FORBIDDEN_B[@]}"; do
      S45_P="${S45_ROW%%$'\t'*}"; S45_ALLOW="${S45_ROW#*$'\t'}"
      S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E "${S45_P}" "${S45_C}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | grep -Ev "${S45_ALLOW}" | head -5)"
      [ -n "${S45_HITS}" ] && { bad "[45] 未推 commit ${S45_C:0:9} 命中敏感词(豁免外): ${S45_P}"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
    done
  done
  # ②' 未推区间每个 commit 的新增行过 N 组(去空白字面,防换行拆词):只看这条提交新写的行 ——
  #     树里继承的旧文已公开,不在此误红;前面提交写进、后面提交才删掉的词照样拦(逐条提交的 diff 推上去即公开)
  S45_NARGS=()
  for S45_L in "${HOROSA_NORMALIZED_LITERALS[@]:-}"; do [ -n "${S45_L}" ] && S45_NARGS+=(-e "${S45_L}"); done
  # 去空白:ASCII 空白 + 按字节删 Unicode 空白与零宽字符(C locale 下 tr 不认全角空格 / NBSP / 零宽空格;与扫描器同一份)
  s45_strip_ws(){ LC_ALL=C tr -d '[:space:]' | LC_ALL=C sed -e $'s/\xe3\x80\x80//g; s/\xe3\x85\xa4//g; s/\xc2[\x85\xa0\xad]//g; s/\xcd\x8f//g; s/\xd8\x9c//g; s/\xe1\x85[\x9f\xa0]//g; s/\xe1\x9a\x80//g; s/\xe1\x9e[\xb4\xb5]//g; s/\xe1\xa0[\x8b-\x8f]//g; s/\xe2\x80[\x80-\x8f]//g; s/\xe2\x80[\xa8-\xaf]//g; s/\xe2\x81[\x9f-\xa4\xa6-\xaf]//g; s/\xef\xb8[\x80-\x8f]//g; s/\xef\xbb\xbf//g; s/\xef\xbe\xa0//g; s/\xf0\x9b\xb2[\xa0-\xa3]//g; s/\xf0\x9d\x85[\xb3-\xba]//g; s/\xf3\xa0[\x80-\x87][\x80-\xbf]//g'; }
  if [ "${#S45_NARGS[@]}" -gt 0 ]; then
    for S45_C in $(git -C "${REPO_ROOT}" rev-list origin/main..HEAD 2>/dev/null); do
      S45_HITS="$(git -C "${REPO_ROOT}" -c core.quotepath=false -c color.ui=never show --no-color --no-ext-diff --no-textconv --text --format= -U0 "${S45_C}" -- . "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | LC_ALL=C grep -a '^+' | LC_ALL=C grep -av '^+++' | s45_strip_ws | LC_ALL=C grep -aoF "${S45_NARGS[@]}" | sort -u | head -5 | tr '\n' ' ')"
      [ -n "${S45_HITS}" ] && { bad "[45] 未推 commit ${S45_C:0:9} 新增行命中去空白字面(N 组): ${S45_HITS}"; S45_BAD=1; }
    done
  fi
  # ③ 未推区间全部 commit message(A 组逐行 + N 组去空白)
  S45_HITS="$(git -C "${REPO_ROOT}" log --format='%h %B' origin/main..HEAD 2>/dev/null | grep -E "${S45_A_ARGS[@]}" | head -5)"
  [ -n "${S45_HITS}" ] && { bad "[45] 未推 commit message 命中敏感词:"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
  if [ "${#S45_NARGS[@]}" -gt 0 ]; then
    S45_HITS="$(git -C "${REPO_ROOT}" log --no-color --format='%B' origin/main..HEAD 2>/dev/null | s45_strip_ws | LC_ALL=C grep -aoF "${S45_NARGS[@]}" | sort -u | head -5 | tr '\n' ' ')"
    [ -n "${S45_HITS}" ] && { bad "[45] 未推 commit message 命中去空白字面(N 组): ${S45_HITS}"; S45_BAD=1; }
  fi
  [ "${S45_BAD}" = "0" ] && ok "[45] 工作树 + $(git -C "${REPO_ROOT}" rev-list --count origin/main..HEAD 2>/dev/null) 个未推 commit + message 敏感词零命中"
fi
}
