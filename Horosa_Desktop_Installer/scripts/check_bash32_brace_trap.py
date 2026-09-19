#!/usr/bin/env python3
"""bash 3.2 花括号展开陷阱检查器(2026-09-08 preflight「发送前成本确认门」哨兵假红根因)。

macOS 自带 /bin/bash 是 3.2.57:它的花括号展开(brace expansion)扫描器**不认识 $( … ) 命令替换**,
只按「见到引号就翻转」的朴素规则数引号。于是形如
    [ "$(grep -acF "foo({ a, b })" "$F")" = "1" ]
的哨兵行里,第二个 `"`(命令替换内部的引号)被当成「关引号」,后面的 `{ a, b }` 处于「未加引号」态,
被展开成两个词 `foo( a)` 与 `foo( b )` —— grep 各数出 0,哨兵永远红;而同一行在 zsh / bash 4+ 下正常。
只有「花括号两侧都是空白」的 `{` 会被 bash 忽略(`{ name: 'x', y }` 安全),`(`/`]`/`"` 紧贴的 `{` 必炸
(`foo({ a, b })`、`[0-9]{2,3}`)。变量赋值右侧不做花括号展开,所以修法=先 `PAT="…{ a, b }…"` 再 `grep -F "$PAT"`。

本检查器逐行模拟 bash 3.2 的扫描规则(朴素引号翻转 + 空白包围忽略 + 顶层逗号判定),
只审「非赋值词」里带 `$(` 的行;命中即红。`--self-test` 用七个判别向量自证(含必红/必绿)。
用法:check_bash32_brace_trap.py [--self-test] <script.sh>...
"""
import re
import sys

ASSIGN_RE = re.compile(r'^\s*(?:local\s+|export\s+|readonly\s+)?[A-Za-z_][A-Za-z0-9_]*\+?=')


def _words(line):
    """按 bash 真规则(引号 + $( … ) 嵌套)把一行切成词;花括号展开是逐词进行的。"""
    words = []
    cur = []
    q = ''
    depth = 0
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c == '\\':
            cur.append(line[i:i + 2])
            i += 2
            continue
        if q == "'":
            cur.append(c)
            if c == "'":
                q = ''
            i += 1
            continue
        if c == '$' and i + 1 < n and line[i + 1] == '(':
            depth += 1
            cur.append('$(')
            i += 2
            continue
        if depth and c == ')':
            depth -= 1
            cur.append(c)
            i += 1
            continue
        if q == '"':
            cur.append(c)
            if c == '"' and depth == 0:
                q = ''
            elif c == '"':
                # $( ) 内部的引号:真 bash 视为内层词的引号,不改变外层状态
                pass
            i += 1
            continue
        if c in ('"', "'"):
            if depth == 0:
                q = c
            cur.append(c)
            i += 1
            continue
        if c.isspace() and depth == 0:
            if cur:
                words.append(''.join(cur))
                cur = []
            i += 1
            continue
        if c == '#' and depth == 0 and not cur:
            break
        cur.append(c)
        i += 1
    if cur:
        words.append(''.join(cur))
    return words


def _naive_hits(word):
    """模拟 bash 3.2 brace_gobbler:朴素引号翻转(不认识 $( … )),空白包围的 { 忽略,顶层逗号才展开。"""
    hits = []
    quoted = ''
    i = 0
    n = len(word)
    while i < n:
        c = word[i]
        if c == '\\':
            i += 2
            continue
        if quoted:
            if c == quoted:
                quoted = ''
            i += 1
            continue
        if c in ('"', "'", '`'):
            quoted = c
            i += 1
            continue
        if c == '{' and i > 0 and word[i - 1] == '$':
            i += 1
            continue
        if c == '{':
            prev_ws = (i == 0) or word[i - 1].isspace()
            next_ws = (i + 1 < n) and word[i + 1].isspace()
            if prev_ws and next_ws:
                i += 1
                continue
            level = 0
            q2 = ''
            j = i
            comma = False
            closed = -1
            while j < n:
                d = word[j]
                if d == '\\':
                    j += 2
                    continue
                if q2:
                    if d == q2:
                        q2 = ''
                    j += 1
                    continue
                if d in ('"', "'", '`'):
                    q2 = d
                    j += 1
                    continue
                if d == '{':
                    level += 1
                elif d == '}':
                    level -= 1
                    if level == 0:
                        closed = j
                        break
                elif d == ',' and level == 1:
                    comma = True
                j += 1
            if closed > 0 and comma:
                hits.append(word[i:closed + 1])
                i = closed + 1
                continue
        i += 1
    return hits


def _brace_trap_spans(line):
    """返回该行在 bash 3.2 下会被花括号展开的 `{…,…}` 片段列表(空=安全)。
    只审「含 $( 的非赋值词」:裸 `dir/{a,b}` 是有意的展开,不在本陷阱族内;赋值右侧 bash 不做花括号展开。"""
    if '$(' not in line or line.lstrip().startswith('#'):
        return []
    out = []
    for w in _words(line):
        if '$(' not in w or ASSIGN_RE.match(w):
            continue
        out.extend(_naive_hits(w))
    return out


def scan_file(path):
    out = []
    with open(path, 'r', encoding='utf-8', errors='replace') as fh:
        for no, raw in enumerate(fh, 1):
            line = raw.rstrip('\n')
            for h in _brace_trap_spans(line):
                out.append((path, no, h))
    return out


def self_test():
    vectors = [
        # (行, 期望命中)
        ('[ "$(s250_code "${S250_HK}" | grep -acF "if(typeof confirmCost === \'function\'){ const ok = await confirmCost({ candidates, est });")" = "1" ] || bad', True),
        ('[ "$(s250_code "${S250_HK}" | grep -acF "applyResponseSchema(opts, { name: \'bestof_judge\', schema: JUDGE_SCHEMA })")" = "1" ] || bad', False),
        ('[ "$(s247_code "${S247_AU}/engine.js" | grep -acF "if(!isAutomationEnabled()){ return { ...out, off: true }; }")" = "1" ] || bad', False),
        ('[ "$(grep -acE "sk-[A-Za-z0-9_-]{8,}" "$F")" = "0" ] || bad', True),
        ('S252_SK="$(grep -rlE "sk-[A-Za-z0-9_-]{8,}|Bearer [A-Za-z0-9._-]{8,}" "${D}" 2>/dev/null || true)"', False),
        ('S250_PAT="if(typeof confirmCost === \'function\'){ const ok = await confirmCost({ candidates, est });"', False),
        ('[ "$(s250_code "${S250_HK}" | grep -acF "${S250_PAT}")" = "1" ] || bad', False),
        ('echo "$(grep -c "x" "$F")" "{ a, b }"', False),
        ('[ "$(grep -c "x{1,2}" "$F")" = 1 ] || bad', True),
        ('[ "$(grep -c "x" "$F")" = 1 ] || bad "上限 {2,3} 档 $(date)"', False),
        ('[ "$(grep -c "x" "$F")" = 1 ] && ok "[1] 上限 {2,3} 档"', False),
    ]
    bad = 0
    for line, want in vectors:
        got = bool(_brace_trap_spans(line))
        flag = 'ok ' if got == want else 'BAD'
        if got != want:
            bad += 1
        print(f'  {flag} want={int(want)} got={int(got)} :: {line[:96]}')
    print(f'self-test: {len(vectors) - bad}/{len(vectors)}')
    return bad == 0


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    if '--self-test' in argv:
        ok = self_test()
        if not args:
            return 0 if ok else 2
        if not ok:
            return 2
    if not args:
        print(__doc__)
        return 1
    hits = []
    for p in args:
        hits.extend(scan_file(p))
    for path, no, h in hits:
        print(f'{path}:{no}: bash 3.2 花括号展开陷阱 → {h[:80]}')
    print(f'brace-trap: {len(hits)} 处命中 / {len(args)} 个脚本')
    return 1 if hits else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
