#!/usr/bin/env python3
"""发布前自检(release_preflight.sh)自身结构的静态检查。

   python3 check_preflight_structure.py            # 查本仓执行用登记表涉及的全部段
   python3 check_preflight_structure.py --self-test # 判别力自证(构造坏样本,检查必须报出来)
   python3 check_preflight_structure.py --root <仓根> # 查另一个仓

查什么:段与段之间不许靠「别的段函数体里赋的全局变量」传值。
  全量按序跑时这类隐式传值看不出毛病;`--only` / `--from` 跳过赋值的那段,`set -u` 当场中止
  (unbound variable),一段没跑完也没有汇总行。所以每个段函数读到的变量必须是下面之一:
    ① 本段函数体里赋值的;② 文件顶层赋值的(公共库 / 入口 / 段文件顶层,装载期就有);
    ③ 公共库里的函数赋值的(登记表装载与执行,跑段之前已跑完);④ 本段调用的助手函数(直接或间接)里赋值的;
    ⑤ 带缺省值的展开(`${X:-…}` / `${X-…}` / `${X:+…}` / `${X+…}` / `${X:=…}`,set -u 下安全);
    ⑥ bash 自带 / 环境必有的变量(HOME / PATH / PWD / RANDOM / BASH_* …)与位置参数。
  不满足 = 报「seg_X 读 $V,但 $V 只在 seg_Y 里赋值」;修法 = 挪到段文件顶层当装载期常量,或在本段里自己算。

另查三条同类写法(都在段文件里,只看代码、不看注释与单引号串):
  ⑦ 算术上下文里的裸变量名(`$(( N + 1 ))` / `(( N++ ))` / `let N=N+1`)同样是读 —— set -u 下没赋值一样中止,按上面同一口径核;
  ⑧ 「测试被关掉」守卫只许调公共库的 pf_test_disabled(认 .skip / .only / .todo / xit / xdescribe / fit … 全部形态);
     段里自己写 `.skip` / `xdescribe` / `pytest.mark.skip` 这类正则 = 红(曾有两种口径、且都漏 .only);
  ⑨ 段里的 mktemp 必须建在本轮临时目录 `${PF_TMP}` 下(入口的 trap 统一收走;段中途 set -u 中止 / Ctrl-C 时不漏);
  ⑩ 段里拿 grep / pf_has / pf_need / pf_none / pf_once / pipe_has 按字面认一条 import 语句(`import { … }` / `… } from '…'`)= 红,
     改调公共库 pf_imports <文件> "<import 语句>"(按 AST 只认来源 + 名字;整行字面锚往同一条里加一个名字就假红)。
  ⑪ 读桌面壳 Rust 源码的锚(两张登记表引用的段文件都查;产品 / 测试按 preflight/rs_split.py 同一口径拆):
     R1 正锚读的面含测试、模式只在测试里命中(不是 fn 名 / #[test] / mod …tests 这类「测试在位」形状)= 红 —— 删掉产品代码照样绿;
        产品里也命中、测试里也命中 = 红(「测试在位」豁免只在产品零命中时成立;产品锚 `fn x` 恰是测试名前缀就是这类);
     R2 计数锚读的面含测试、模式在测试里也命中 = 红,不看眼下产品够不够数(测试已在替产品兜底,产品一退化就被盖住);
        `pf_code "<读面>" | grep -c …` 这类先剥注释再计数的管道写法同样认;
     R3 反锚读的面含测试 = 红(测试会故意造夹具),只扫壳层模块不扫独立子模块 = 红(改读 pf_shell_rs_prod_all);
     R4 段里拿 pf_shell_rs 全集当读面 = 红(产品锚 pf_shell_rs_prod / 反锚 pf_shell_rs_prod_all / 测试在位 pf_shell_rs_tests)。
  ⑫ 递归 grep 扫源码目录(反锚 / 正锚 / 计数都算)却不排除测试 = 红:改走 lib.sh 的 pf_prod_hits / pf_prod_grep / pf_prod_tree
     (去掉测试目录与测试文件);保密类(私有名 / 标记 / 密钥字面,测试也会同步出去)、构建产物 / 文档目录照旧扫整树,
     在行上或上一行写「# 全树:<理由>」;只点名文件的 grep -r 不在此列。
  ⑬ 段体里 echo / bad / ok / warn 打印的「[N]」开头,N 必须是本段段号 / ${PF_NO} / 登记表第四列登记的子段号(两张表都查,
     registry.tsv 按剥私有块后的投影读)—— 否则照输出里的号跑 `--only N` 退 2「本仓没有这些段号」。
  ⑭ 共享段文件(segments/*.sh 里非 .public.sh 的 + lib.sh,两张登记表都会执行;按投影读)注释里的「[N]」/ 段头「# N.」:
     两张表都在时 N 必须在两张表里指同一段(或在两张表里都是子段号);只有一张表时 N 必须在表里 ——
     否则总有一仓的读者照注释找到别的段。改写 seg_<id> / 「本段」/ 语义名。

读法:粗粒度的 bash 词法(去掉注释、单引号串、带引号定界符的 heredoc 正文、`\\$` 转义),
  只认 `$名` / `${名…}` 两种展开与常见赋值形状(`名=` / `local|export|declare|readonly 名` / `read … 名` /
  `for 名 in` / `printf -v 名`)。宁可多算「已赋值」(漏报一处)也不误报。
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PF_DIR = os.path.join(HERE, 'preflight')

SAFE_BUILTIN = {
    'HOME', 'PATH', 'PWD', 'OLDPWD', 'RANDOM', 'LINENO', 'SECONDS', 'IFS', 'PPID', 'UID', 'EUID', 'USER', 'SHELL',
    'OSTYPE', 'HOSTNAME', 'SHLVL', 'PIPESTATUS', 'FUNCNAME', 'BASH_SOURCE', 'BASH_LINENO', 'BASH_VERSION',
    'BASH_VERSINFO', 'BASH', 'BASHPID', 'REPLY', 'OPTARG', 'OPTIND', 'HOSTTYPE', 'MACHTYPE', 'TERM', 'LANG',
    'BASH_REMATCH', 'GROUPS', 'DIRSTACK', 'COLUMNS', 'LINES',
}
NAME = r'[A-Za-z_][A-Za-z0-9_]*'
FUNC_DEF = re.compile(r'^(?:function\s+)?(' + NAME + r')\s*\(\)\s*\{')
ASSIGN_RES = [
    re.compile(r'(?:^|[\s;&|({`!])(?:export\s+|local\s+|readonly\s+|declare\s+(?:-[A-Za-z]+\s+)*)?(' + NAME + r')(?:\[[^\]]*\])?\+?='),
    re.compile(r'(?:^|[\s;&|({`])(?:local|declare|export|readonly|typeset)\s+((?:-[A-Za-z]+\s+)*(?:' + NAME + r'(?:=\S*)?\s*)+)'),
    re.compile(r'\bread\s+((?:-[A-Za-z]*[dnNptu]\s+\S+\s+|-[A-Za-z]+\s+)*(?:' + NAME + r'(?=[\s;|&)]|$)\s*)+)'),
    re.compile(r'\bfor\s+(' + NAME + r')\s+in\b'),
    re.compile(r'\bprintf\s+-v\s+(' + NAME + r')'),
    re.compile(r'\b(?:mapfile|readarray)\s+(?:-[A-Za-z]*[dnOstuC]\s+\S+\s+|-[A-Za-z]+\s+)*(' + NAME + r')'),
]
EXPAND = re.compile(r'\$\{(#?)(' + NAME + r')([^}]*)\}|\$(' + NAME + r')')
HEREDOC = re.compile(r'<<(-?)\s*(\\?)([\'"]?)(' + NAME + r')\3')


def strip_code(text):
    """去掉注释 / 单引号串 / 带引号定界符的 heredoc 正文 / \\ 转义,返回逐行代码(行数与原文相同)。
       按字符流走,带一个上下文栈:顶层 / 双引号串 / 命令替换 $( … )(双引号里的 $( 重新开一层顶层语境)。"""
    out, n, i = [], len(text), 0
    stack = ['top']          # top / dq / cmd(cmd 记括号深度)
    depth = [0]
    pending = []             # 待读的 heredoc:(定界符, 正文要不要保留)
    line_start = True
    while i < n:
        c = text[i]
        ctx = stack[-1]
        if c == '\n':
            out.append('\n')
            i += 1
            line_start = True
            if pending and ctx != 'dq':
                while pending:
                    delim, keep = pending.pop(0)
                    while i < n:
                        j = text.find('\n', i)
                        j = n if j < 0 else j
                        ln = text[i:j]
                        i = j + 1 if j < n else n
                        if ln.lstrip('\t') == delim:
                            out.append('\n')
                            break
                        out.append((ln.replace('\\$', '') if keep else '') + '\n')
            continue
        if c == '\\':
            i += 2 if i + 1 < n and text[i + 1] != '\n' else 1
            continue
        if ctx == 'dq':
            if c == '"':
                stack.pop()
                depth.pop()
            elif text.startswith('$(', i) and not text.startswith('$((', i):
                stack.append('cmd')
                depth.append(0)
                out.append('$(')
                i += 2
                continue
            out.append(c)
            i += 1
            continue
        # 顶层 / 命令替换
        if c == "'":
            k = text.find("'", i + 1)
            k = n if k < 0 else k
            out.append("''" + '\n' * text.count('\n', i, k))
            i = k + 1
            continue
        if c == '#' and (line_start or (out and out[-1][-1:] in (' ', '\t', ';', '(', '|', '&'))):
            k = text.find('\n', i)
            i = n if k < 0 else k
            continue
        if c == '"':
            stack.append('dq')
            depth.append(0)
        elif text.startswith('$(', i) and not text.startswith('$((', i):
            stack.append('cmd')
            depth.append(0)
            out.append('$(')
            i += 2
            line_start = False
            continue
        elif ctx == 'cmd' and c == '(':
            depth[-1] += 1
        elif ctx == 'cmd' and c == ')':
            if depth[-1] == 0:
                stack.pop()
                depth.pop()
            else:
                depth[-1] -= 1
        elif c == '<' and text.startswith('<<', i) and not text.startswith('<<<', i):
            m = HEREDOC.match(text, i)
            if m:
                pending.append((m.group(4), not (m.group(2) or m.group(3))))
                out.append(m.group(0))
                i = m.end()
                line_start = False
                continue
        out.append(c)
        if c not in ' \t':
            line_start = False
        i += 1
    return ''.join(out).split('\n')


def parse_file(path):
    """返回 (顶层代码行, {函数名: [代码行]})。函数 = `名() {` 开头,同一行收尾或到第 0 列 `}` 为止。"""
    code = strip_code(open(path, encoding='utf-8').read())
    top, funcs, i = [], {}, 0
    while i < len(code):
        ln = code[i]
        m = FUNC_DEF.match(ln)
        if m:
            name = m.group(1)
            rest = ln[m.end():]
            if re.search(r'\}\s*;?\s*$', rest) and rest.count('{') < rest.count('}'):
                funcs[name] = [rest]
                i += 1
                continue
            body = [rest]
            i += 1
            depth = 0      # 段体里顶格定义的助手函数(s<id>_scan(){ … })按深度计:曾在它的「}」处就当段体收尾,后面的赋值 / 打印全被当成文件顶层
            while i < len(code):
                if re.match(r'^\}\s*$', code[i]):
                    if depth == 0:
                        break
                    depth -= 1
                else:
                    mm = FUNC_DEF.match(code[i])
                    if mm and not (re.search(r'\}\s*;?\s*$', code[i][mm.end():]) and code[i][mm.end():].count('{') < code[i][mm.end():].count('}')):
                        depth += 1
                body.append(code[i])
                i += 1
            funcs[name] = body
            i += 1
            continue
        top.append(ln)
        i += 1
    return top, funcs


def assigned(lines):
    s = set()
    for ln in lines:
        s |= arith_names(ln)[1]
        for rx in ASSIGN_RES:
            for m in rx.finditer(ln):
                for tok in re.split(r'\s+', m.group(1).strip()):
                    tok = tok.split('=')[0].split('[')[0]
                    if re.fullmatch(NAME, tok) and not tok.startswith('-'):
                        s.add(tok)
    return s


ARITH_OPEN = re.compile(r'\$\(\(|(?:^|(?<=[\s;&|{`!]))\(\(')
ARITH_LET = re.compile(r'(?:^|[\s;&|({`!])let\s+([^;&|)]*)')
ARITH_NAME = re.compile(r'(?<![A-Za-z0-9_#$.\[])(' + NAME + r')(?![A-Za-z0-9_\(])')


def _blank_nested(expr):
    """抹掉算术表达式里嵌套的命令替换 `$( … )`(按括号配平)与双引号串:那里面是命令,不是算术里的名字。"""
    out, i, n = [], 0, len(expr)
    while i < n:
        if expr.startswith('$(', i) and not expr.startswith('$((', i):
            depth, j = 0, i + 1
            while j < n:
                if expr[j] == '(':
                    depth += 1
                elif expr[j] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            out.append(' 0 ')
            i = j + 1
            continue
        if expr[i] == '"':
            j = expr.find('"', i + 1)
            j = n if j < 0 else j
            out.append(' 0 ')
            i = j + 1
            continue
        out.append(expr[i])
        i += 1
    return ''.join(out)


def arith_exprs(ln):
    """一行里算术上下文的表达式文本(`$(( … ))` / `(( … ))` 按括号配平取到收尾 / `let …`);
       嵌套命令替换、双引号串、`${…}` 与 `$名` 先抹掉(后两种由 EXPAND 管)。"""
    out = []
    for m in ARITH_OPEN.finditer(ln):
        depth, j = 2, m.end()
        while j < len(ln) and depth > 0:
            if ln[j] == '(':
                depth += 1
            elif ln[j] == ')':
                depth -= 1
            j += 1
        out.append(ln[m.end():max(m.end(), j - 2)])
    for m in ARITH_LET.finditer(ln):
        out.append(m.group(1))
    return [re.sub(r'\$\{[^}]*\}|\$' + NAME, ' 0 ', _blank_nested(x)) for x in out]


def arith_names(ln):
    """算术上下文里的裸名:(读, 赋值)两个集合。`N = …` / `N += …` 之类 —— `=` 前的名字算赋值(复合赋值同时算读)。"""
    rd, asg = set(), set()
    for expr in arith_exprs(ln):
        for m in ARITH_NAME.finditer(expr):
            name, rest = m.group(1), expr[m.end():]
            if re.match(r'\s*=(?!=)', rest):
                asg.add(name)
                continue
            if re.match(r'\s*(?:[-+*/%&|^]|<<|>>)=', rest):
                asg.add(name)
            rd.add(name)
    return rd, asg


def reads(lines):
    """不带缺省值的变量展开 + 算术上下文里的裸名:{名: 首个行号(相对函数体)}。"""
    r = {}
    for n, ln in enumerate(lines):
        for m in EXPAND.finditer(ln):
            if m.group(4):
                name = m.group(4)
            else:
                name, op = m.group(2), m.group(3)
                if m.group(1) == '' and re.match(r'^:?[-+=]', op):
                    continue
            r.setdefault(name, n + 1)
        for name in arith_names(ln)[0]:
            r.setdefault(name, n + 1)
    return r


SOURCE_RE = re.compile(r'(?:^|[\s;&|({])(?:\.|source)\s+"?([^"\s;]+)"?')
SIMPLE_ASSIGN = re.compile(r'^\s*(' + NAME + r')="([^"$`]*(?:\$\{' + NAME + r'\}[^"$`]*)*)"\s*$')


def sourced_assigned(lines, env):
    """本段 `. 文件` / `source 文件` 装进来的变量(路径里只认 ${已知变量} 与字面)。
       返回 (变量集, 有没有装不进来的文件) —— 文件不在本机(例:不入库的本地词表)时它定义了什么无从得知。"""
    env = dict(env)
    got, opaque = set(), False
    for ln in lines:
        m = SIMPLE_ASSIGN.match(ln)
        if m:
            env[m.group(1)] = re.sub(r'\$\{(' + NAME + r')\}', lambda x: env.get(x.group(1), '\0'), m.group(2))
        for m in SOURCE_RE.finditer(ln):
            path = re.sub(r'\$\{(' + NAME + r')\}', lambda x: env.get(x.group(1), '\0'), m.group(1))
            if '\0' not in path and os.path.isfile(path):
                t, fs = parse_file(path)
                got |= assigned(t)
                for body in fs.values():
                    got |= assigned(body)
            else:
                opaque = True
    return got, opaque


def calls(lines, names):
    s = set()
    for ln in lines:
        for tok in re.findall(NAME, ln):
            if tok in names:
                s.add(tok)
    return s


def registry_rows(pf_dir):
    reg = os.path.join(pf_dir, 'extra', 'registry.tsv')
    if not os.path.isfile(reg):
        reg = os.path.join(pf_dir, 'registry.tsv')
    rows = []
    for ln in open(reg, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln or ln.startswith('#'):
            continue
        p = ln.split('\t')
        if len(p) >= 3:
            rows.append((p[0], p[1], p[2]))
    return reg, rows


def analyze(pf_dir, entry, lib):
    reg, rows = registry_rows(pf_dir)
    installer = os.path.dirname(os.path.dirname(pf_dir))
    env = {'PF_DIR': pf_dir, 'INSTALLER_ROOT': installer, 'REPO_ROOT': os.path.dirname(installer)}
    files, seen = [], set()
    for _, _, rel in rows:
        if rel not in seen:
            seen.add(rel)
            files.append(rel)
    top_assigned = set()
    lib_funcs_assigned = set()
    helpers = {}       # 助手函数名 → 代码行(段文件里非 seg_ 的函数 + 公共库函数)
    segs = {}          # seg_x → (段文件, 代码行)
    for p in (entry, lib):
        t, fs = parse_file(p)
        top_assigned |= assigned(t)
        for name, body in fs.items():
            helpers[name] = body
            if p == lib:
                lib_funcs_assigned |= assigned(body)
    for rel in files:
        path = os.path.join(pf_dir, rel)
        if not os.path.isfile(path):
            continue
        t, fs = parse_file(path)
        top_assigned |= assigned(t)
        for name, body in fs.items():
            if name.startswith('seg_'):
                segs[name] = (rel, body)
            else:
                helpers[name] = body
    seg_assigned = {k: assigned(v[1]) for k, v in segs.items()}
    helper_assigned = {k: assigned(v) for k, v in helpers.items()}
    helper_calls = {k: calls(v, helpers) for k, v in helpers.items()}

    def closure(start):
        seen_h, stack = set(), list(start)
        while stack:
            h = stack.pop()
            if h in seen_h:
                continue
            seen_h.add(h)
            stack.extend(helper_calls.get(h, ()))
        return seen_h

    problems = []
    base = top_assigned | lib_funcs_assigned | SAFE_BUILTIN
    for sid, _, _ in rows:
        name = 'seg_' + sid
        if name not in segs:
            continue
        rel, body = segs[name]
        src_vars, opaque = sourced_assigned(body, env)
        avail = set(base) | seg_assigned[name] | src_vars
        for h in closure(calls(body, helpers)):
            avail |= helper_assigned.get(h, set())
        for var, ln in sorted(reads(body).items(), key=lambda kv: kv[1]):
            if var in avail or re.fullmatch(r'S' + re.escape(sid) + r'_BAD', var):
                continue
            owners = sorted(k for k, v in seg_assigned.items() if var in v and k != name)
            if opaque and not owners:  # 多半来自本段装进来、本机却没有的文件;跨段传值这一类才是本检查要抓的
                continue
            problems.append((name, rel, ln, var, owners))
    return reg, rows, problems


# 段里自己写「测试被关掉」的正则(而不是调 pf_test_disabled)
SKIP_LITERAL = re.compile(r'\.skip\b|\.only\b|\.todo\b|\bxdescribe\b|\bxit\b|\bxtest\b|\bfdescribe\b|pytest\.mark\.skip|pytest\.skip|unittest\.skip|SkipTest|importorskip|\.skipTest\b|pytestmark')
IMPORT_ANCHOR = re.compile(r'\b(?:grep|pf_has|pf_need|pf_none|pf_once|pipe_has)\b.*?["\'](?:import\s+\{|[^"\']*\}\s+from\s+\\?\')')
MKTEMP = re.compile(r'(?:\$\(|^|[;&|]|\b(?:then|do|else))\s*mktemp\b([^)\n]*)')


def segment_file_lint(pf_dir, rels):
    """⑧ skip 守卫只许 pf_test_disabled;⑨ mktemp 必须建在 ${PF_TMP} 下;⑩ 不按字面认 import 语句。返回 [(rel, 行号, 说明)]。"""
    out = []
    for rel in rels:
        path = os.path.join(pf_dir, rel)
        if not os.path.isfile(path):
            continue
        raw = open(path, encoding='utf-8').read().split('\n')
        code = strip_code('\n'.join(raw))
        for i, ln in enumerate(raw):
            src = ln.lstrip()
            if src.startswith('#'):
                continue
            if SKIP_LITERAL.search(ln) and 'pf_test_disabled' not in ln:
                out.append((rel, i + 1, '自己写了「测试被关掉」的正则:改调公共库 pf_test_disabled "<文件>"(认 .skip / .only / .todo / xit / xdescribe / fit 等全部形态)'))
            if IMPORT_ANCHOR.search(ln) and 'pf_imports' not in ln:
                out.append((rel, i + 1, '按字面认 import 语句:改调公共库 pf_imports <文件> "<import 语句>"(按 AST 只认来源 + 名字,与同一条里还有哪些名字、先后、换行无关)'))
            cl = code[i] if i < len(code) else ''
            for m in MKTEMP.finditer(cl):
                if 'PF_TMP' not in m.group(1):
                    out.append((rel, i + 1, 'mktemp 没建在本轮临时目录下:写成 mktemp [-d] "${PF_TMP}/<名>.XXXXXX"(入口的 trap 统一收走,段中途中止也不漏)'))
    return out



# ── ⑪ 读壳 Rust 源码的锚:产品锚不许被测试满足,反锚不许读到测试夹具(preflight/rs_split.py 同一口径拆产品 / 测试)──
RS_SRC_REL = os.path.join('Horosa_Desktop_Installer', 'src-tauri', 'src')
RS_SET_OF_FN = {'pf_shell_rs': 'full', 'pf_shell_rs_prod': 'prod', 'pf_shell_rs_prod_all': 'prodall', 'pf_shell_rs_tests': 'tests'}
_RS_FILEREF = (r'"(?:\$\{(?P<var>' + NAME + r')\}(?P<sub>/[A-Za-z0-9_.]+)?'
               r'|\$\((?P<fn>pf_shell_rs(?:_prod_all|_prod|_tests)?)(?:\s+"[^"]*")?\)'
               r'|\$\(pf_rs_prod\s+"(?P<rsprod>[^"]+)"\))"')
_RS_PAT = r"(?:'(?P<sq>[^']*)'|\"(?P<dq>(?:[^\"\\]|\\.)*)\")"
RS_GREP = re.compile(r'(?P<neg>!\s*)?\bgrep(?P<flags>(?:\s+-[A-Za-z]+)*)\s+(?:--\s+)?' + _RS_PAT + r'(?:\s+-[A-Za-z]+)*\s+' + _RS_FILEREF)
RS_PFHELP = re.compile(r'\b(?P<helper>pf_need|pf_none|pf_once|pf_has)\s+' + _RS_FILEREF + r'\s+' + _RS_PAT)
# 读面先经「剥注释」助手 / cat 再接 grep 计数或判有无:pf_code "<读面>" | grep -acF '…'(段内自定义的 sNNN_code 同形)
RS_PIPEGREP = re.compile(r'\b(?:pf_code(?:\s+-q|\s+--fullline)?|s[0-9]+_code|cat)\s+' + _RS_FILEREF + r'\s*\|\s*grep(?P<flags>(?:\s+-[A-Za-z]+)*)\s+(?:--\s+)?' + _RS_PAT)
RS_PIPEHAS = re.compile(r"\b(?:grep\s+-v\s+(?:'[^']*'|\"[^\"]*\")|cat)\s+" + _RS_FILEREF + r'\s*\|\s*pipe_has(?P<flags>(?:\s+-[A-Za-z]+)*)\s+(?:--\s+)?' + _RS_PAT)
RS_BIND = re.compile(r'^\s*(?:local\s+)?(' + NAME + r')="(?:\$\((pf_shell_rs(?:_prod_all|_prod|_tests)?)(?:\s+"[^"]*")?\)'
                     r'|\$\{(?:REPO_ROOT|INSTALLER_ROOT)\}(/(?:Horosa_Desktop_Installer/)?src-tauri/src)(/[A-Za-z0-9_.]+\.rs)?)"\s*$')
RS_COUNT_TAIL = re.compile(r'^\s*(?:2>/dev/null\s*)?(?:\|\|\s*true\s*)?\)"\s*(=|!=|-ge|-gt|-eq|-ne|-le|-lt)\s*"?(\d+)"?')
RS_TEST_SHAPE = re.compile(r'^(?:#\[test\]|(?:pub(?:\(crate\))?\s+)?fn\s+[A-Za-z0-9_]+(?:\(\)?)?|mod\s+[A-Za-z0-9_]*tests)$')


def _rs_lists(lib_path):
    t = open(lib_path, encoding='utf-8').read()
    f = re.search(r'^PF_SHELL_RS_FILES="([^"]*)"', t, re.M)
    s = re.search(r'^PF_SHELL_RS_STANDALONE="([^"]*)"', t, re.M)
    return (f.group(1).split() if f else []), (s.group(1).split() if s else [])


class RsParts:
    """壳源码各读面的(产品部分, 测试部分)。读面:full(壳层模块全集)/ prod / prodall / tests / file:X(单文件原样)/ fileprod:X。"""

    def __init__(self, repo_root, lib_path, pf_dir):
        sys.path.insert(0, pf_dir)
        try:
            import rs_split
        finally:
            sys.path.pop(0)
        self.src = os.path.join(repo_root, RS_SRC_REL)
        self.files, self.standalone = _rs_lists(lib_path)
        self.per = {}
        for f in self.files + self.standalone:
            p = os.path.join(self.src, f)
            if os.path.isfile(p):
                self.per[f] = rs_split.split_file(p)

        def j(names, k):
            return ''.join(self.per[x][k] for x in names if x in self.per)
        self.sets = {
            'full': (j(self.files, 0), j(self.files, 1)),
            'prod': (j(self.files, 0), ''),
            'prodall': (j(self.files + self.standalone, 0), ''),
            'tests': ('', j(self.files + self.standalone, 1)),
        }
        self.tmp = tempfile.mkdtemp(prefix='pfstruct-rs.')
        self.paths = {}

    def parts(self, ref):
        if ref in self.sets:
            return self.sets[ref]
        kind, _, name = ref.partition(':')
        if name not in self.per:
            return None
        prod, tests = self.per[name]
        return (prod, '') if kind == 'fileprod' else (prod, tests)

    def count(self, ref, which, flags, pat):
        """按 grep 原样的旗标(去掉 q / c 之外的输出类)数命中行。"""
        pt = self.parts(ref)
        if pt is None:
            return None
        key = (ref, which)
        if key not in self.paths:
            fp = os.path.join(self.tmp, '%d.txt' % len(self.paths))
            with open(fp, 'w', encoding='utf-8', errors='surrogateescape') as fh:
                fh.write(pt[which])
            self.paths[key] = fp
        keep = ''.join(ch for f in flags.split() for ch in f.lstrip('-') if ch in 'aFEiwx')
        r = subprocess.run(['grep', '-c'] + (['-' + keep] if keep else []) + ['--', pat, self.paths[key]], capture_output=True, text=True)
        try:
            return int((r.stdout or '0').strip() or 0)
        except ValueError:
            return None

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


def _rs_ref(m, binds):
    """匹配到的文件引用 → 读面名;认不出(不是壳源码)→ None。"""
    if m.group('fn'):
        return RS_SET_OF_FN[m.group('fn')]
    if m.group('rsprod'):
        arg = m.group('rsprod')
        vm = re.match(r'^\$\{(' + NAME + r')\}(/[A-Za-z0-9_.]+)?$', arg)
        if vm:
            # pf_rs_prod "${变量}" / "${目录变量}/x.rs":按变量绑定解析到那个文件的产品读面
            v = binds.get(vm.group(1))
            if v and v.startswith('file:') and not vm.group(2):
                return 'fileprod:' + v[5:]
            if v == 'dir' and vm.group(2) and vm.group(2).endswith('.rs') and vm.group(2).count('/') == 1:
                return 'fileprod:' + vm.group(2)[1:]
            return None
        b = os.path.basename(arg)
        return 'fileprod:' + b if b.endswith('.rs') else None
    v = binds.get(m.group('var'))
    if v is None:
        return None
    sub = m.group('sub')
    if v == 'dir':
        return ('file:' + sub[1:]) if sub and sub.endswith('.rs') and sub.count('/') == 1 else None
    return v if not sub else None


def _rs_pattern(m):
    if m.group('sq') is not None:
        return m.group('sq')
    pat = m.group('dq')
    if re.search(r'(?<!\\)\$', pat):
        return None   # 带展开的模式(循环变量等):静态取不到,跳过
    # bash 双引号里反斜杠只转义 $ ` " \ 与换行,其余原样留给 grep(例:"\[127" 到 grep 手里仍是 \[127,是字面方括号)
    return re.sub(r'\\([$`"\\\n])', r'\1', pat)


def _rs_polarity(kind, flags, inv, tail):
    """返回 (极性, 阈值):pos / neg / count((op, n))/ None(认不出,跳过)。"""
    if kind == 'pf_need':
        return 'pos', None
    if kind == 'pf_none':
        return 'neg', None
    if kind == 'pf_once':
        return 'count', ('=', 1)
    if kind == 'grep' and 'c' in flags.replace('-', ''):
        ct = RS_COUNT_TAIL.match(tail)
        if not ct:
            return None, None
        op, n = ct.group(1), int(ct.group(2))
        if (op in ('=', '-eq') and n == 0) or op in ('-le', '-lt'):
            return 'neg', None
        if op in ('!=', '-ne') and n == 0:
            return 'pos', None
        if op in ('-ge', '-gt', '=', '-eq'):
            return 'count', (op, n)
        return None, None
    t2 = re.sub(r'^\s*2>/dev/null', '', tail)
    pol = None
    if re.match(r'^\s*&&\s*\{\s*(?:bad|printf|echo|pf_seg_bad)\b', t2):
        pol = 'neg'
    elif re.match(r'^\s*(?:\|\||&&|\\\s*$|;\s*\}|\}|$)', t2):
        pol = 'pos'
    if inv and pol:
        pol = 'neg' if pol == 'pos' else 'pos'
    return pol, None


def rs_anchor_lint(pf_dir, rels, repo_root, lib_path):
    """返回 [(rel, 行号, 说明)]。规则:
       R1 正锚读的面含测试(full / file:X),模式在产品部分零命中、只在测试部分命中,且不是「测试在位」形状(fn 名 / #[test] / mod …tests)= 红;
       R2 计数锚读的面含测试,只数产品部分达不到阈值、连测试一起才达到 = 红(测试替产品凑数);
       R3 反锚读的面含测试(full / file:X / tests)= 红(测试会故意造夹具);读 pf_shell_rs_prod(只壳层模块)= 红(独立子模块漏扫,改读 pf_shell_rs_prod_all);
       R4 段里直接拿 pf_shell_rs 全集当读面 = 红(产品锚读 pf_shell_rs_prod、反锚读 pf_shell_rs_prod_all、测试在位读 pf_shell_rs_tests)。"""
    rp = RsParts(repo_root, lib_path, pf_dir)
    out = []
    try:
        for rel in rels:
            path = os.path.join(pf_dir, rel)
            if not os.path.isfile(path):
                continue
            raw = open(path, encoding='utf-8').read().split('\n')
            code = strip_code('\n'.join(raw))
            binds = {}
            for i, ln in enumerate(raw):
                if ln.lstrip().startswith('#'):
                    continue
                b = RS_BIND.match(ln)
                if b:
                    if b.group(2):
                        binds[b.group(1)] = RS_SET_OF_FN[b.group(2)]
                    elif b.group(4):
                        binds[b.group(1)] = 'file:' + b.group(4)[1:]
                    else:
                        binds[b.group(1)] = 'dir'
                cl = code[i] if i < len(code) else ''
                if re.search(r'\$\(pf_shell_rs(?:\s+"[^"]*")?\)', cl):
                    out.append((rel, i + 1, 'R4 拿 pf_shell_rs 全集当读面:产品锚 / 计数改读 pf_shell_rs_prod,「不许出现」改读 pf_shell_rs_prod_all,测试在位改读 pf_shell_rs_tests'))
                found = []
                for m in RS_GREP.finditer(ln):
                    if re.search(r'-[A-Za-z]*[vABCnolL]', m.group('flags') or ''):
                        continue
                    found.append(('grep', m, m.group('flags') or '', bool(m.group('neg'))))
                for m in RS_PFHELP.finditer(ln):
                    found.append((m.group('helper'), m, '-F', False))
                for m in RS_PIPEHAS.finditer(ln):
                    found.append(('pipe_has', m, m.group('flags') or '', False))
                for m in RS_PIPEGREP.finditer(ln):
                    if re.search(r'-[A-Za-z]*[vABCnolL]', m.group('flags') or ''):
                        continue
                    found.append(('grep', m, m.group('flags') or '', False))
                for kind, m, flags, inv in found:
                    ref = _rs_ref(m, binds)
                    pat = _rs_pattern(m)
                    if ref is None or pat is None:
                        continue
                    polarity, thr = _rs_polarity(kind, flags, inv, ln[m.end():])
                    if polarity is None:
                        continue
                    has_tests = ref in ('full', 'tests') or ref.startswith('file:')
                    if polarity == 'neg':
                        if has_tests:
                            out.append((rel, i + 1, 'R3 反锚「%s」读的面含测试(%s):测试为验证检测器会故意造这类夹具 —— 改读 pf_shell_rs_prod_all / pf_rs_prod <文件>' % (pat, ref)))
                        elif ref == 'prod':
                            out.append((rel, i + 1, 'R3 反锚「%s」只扫壳层模块:独立子模块(终端命令 / 本机服务 / REST)同样是产品代码 —— 改读 pf_shell_rs_prod_all' % pat))
                        continue
                    if not has_tests or ref == 'tests':
                        continue
                    pc = rp.count(ref, 0, flags, pat)
                    tc = rp.count(ref, 1, flags, pat)
                    if pc is None or tc is None:
                        continue
                    if polarity == 'pos':
                        test_shape = bool(RS_TEST_SHAPE.match(pat.strip()))
                        if pc == 0 and tc > 0 and not test_shape:
                            out.append((rel, i + 1, 'R1 正锚「%s」只被测试满足(产品代码 0 处、测试 %d 处):删掉产品代码照样绿 —— 产品锚改读 pf_shell_rs_prod / pf_rs_prod <文件>,确是测试在位锚改读 pf_shell_rs_tests' % (pat, tc)))
                        elif pc > 0 and tc > 0:
                            # 产品里也命中 = 产品锚(「测试在位」豁免只在产品零命中时成立);测试里也有同一字面,删掉产品那处照样绿
                            out.append((rel, i + 1, 'R1 正锚「%s」读的面含测试、测试里也命中(产品代码 %d 处、测试 %d 处):删掉产品那处照样绿 —— 改读 pf_shell_rs_prod / pf_rs_prod <文件>' % (pat, pc, tc)))
                        continue
                    op, n = thr
                    need = n + 1 if op == '-gt' else n
                    if tc > 0:
                        # 计数锚读的面含测试、测试里也命中:眼下产品够不够数都一样 —— 测试已在替产品兜底,产品一退化就被盖住
                        out.append((rel, i + 1, 'R2 计数锚「%s」%s %d 读的面含测试、测试里也命中(产品代码 %d 处、测试 %d 处):产品退化会被测试凑数盖住 —— 改读产品集计数' % (pat, '=' if op in ('=', '-eq') else '≥', n if op in ('=', '-eq') else need, pc, tc)))
    finally:
        rp.close()
    return out


# ── ⑫ 递归 grep 扫源码目录:只扫产品文件,或写明为什么扫整树 ──
RG_RECURSIVE = re.compile(r'\bgrep((?:\s+-[A-Za-z]+)*\s+-[A-Za-z]*r[A-Za-z]*(?:\s+-[A-Za-z]+)*)\s')
RG_TEST_EXCLUDED = re.compile(r'--exclude-dir=__tests__|\bgrep\s+-[A-Za-z]*v[A-Za-z]*\s+[^|]*__tests__|\bpf_prod_(?:tree|hits|grep)\b')
FULL_TREE_MARK = '# 全树:'
_RG_PATH = re.compile(r'"(\$\{?[A-Za-z0-9_]+\}?[^"]*|/[^"]*)"(\S*)|(\$\{?[A-Za-z0-9_]+\}?/\S*)')


def _logical_lines(raw):
    """[(首行号, 合并后的逻辑行)]:行尾反斜杠续行并进来。"""
    out, i = [], 0
    while i < len(raw):
        start, buf = i, raw[i]
        while buf.rstrip().endswith('\\') and i + 1 < len(raw):
            i += 1
            buf = buf.rstrip()[:-1] + ' ' + raw[i]
        out.append((start, buf))
        i += 1
    return out


def recursive_grep_lint(pf_dir, rels):
    """递归 grep 扫一个**目录**(读源码树)却既不排除测试、行上与上一行又没写「# 全树:<理由>」= 红。两个方向都假:
         反锚(命中 → 红):测试里拿被禁写法当夹具就假红,只能让测试改写法躲;
         正锚 / 计数(「至少 N 个文件接了线」):测试替产品作证 / 凑数,删掉产品接线照样绿(曾有一处 6 件里 3 件是测试)。
       改用 lib.sh 的 pf_prod_hits / pf_prod_grep / pf_prod_tree;保密类(私有名 / 标记 / 密钥字面,测试也会同步出去)、
       构建产物与文档目录(没有测试之说)扫整树并写理由。只点名文件(带扩展名 / 通配)的 grep -r 不在此列。"""
    out = []
    for rel in rels:
        path = os.path.join(pf_dir, rel)
        if not os.path.isfile(path):
            continue
        raw = open(path, encoding='utf-8').read().split('\n')
        for i, ln in _logical_lines(raw):
            if ln.lstrip().startswith('#'):
                continue
            for m in RG_RECURSIVE.finditer(ln):
                seg = re.split(r'\|\||&&|;|\|', ln[m.end():], maxsplit=1)[0]
                # 去掉模式本身(选项之后的第一个参数:单引号 / 双引号 / 裸词)
                seg = re.sub(r"""^\s*(?:--?[A-Za-z][-A-Za-z]*(?:=\S+)?\s+)*(?:'[^']*'|"(?:[^"\\]|\\.)*"|\S+)""", '', seg, count=1)
                paths = [(x[0] + x[1]) if x[0] else x[2] for x in _RG_PATH.findall(seg)]
                if not paths or all(re.search(r'\.[A-Za-z0-9]{1,6}$|\*', p.rstrip('/)"\'')) for p in paths):
                    continue
                if RG_TEST_EXCLUDED.search(ln) or FULL_TREE_MARK in ln or (i > 0 and FULL_TREE_MARK in raw[i - 1]):
                    continue
                out.append((rel, i + 1, '⑫ 递归 grep 扫源码目录不排除测试:反锚会被测试夹具假红、正锚 / 计数会被测试替产品作证 —— '
                            '改用 pf_prod_hits / pf_prod_grep <grep 选项> <模式> <根> [扩展名…];保密类、构建产物 / 文档目录扫整树并在行上或上一行写「# 全树:<理由>」'))
                break
    return out

# ── ⑬ 段打印的段号 / ⑭ 共享段注释里的段号 ──
_PRIV_MK = '@horosa-' + 'private'


def project_lines(lines):
    """剥掉私有块(与同步通道同一口径),被剥的行换成 None(行号不变)。"""
    out, f = [], False
    for ln in lines:
        if f:
            out.append(None)
            if _PRIV_MK + ':end' in ln:
                f = False
            continue
        if _PRIV_MK + ':' in ln:
            out.append(None)
            f = True
            continue
        out.append(ln)
    return out


def registry_table(reg_path):
    """[(id, 段号, 段文件, [子段号…])];第四列(可选)= 本段打印的子段号(逗号分隔),--only 子段号会映射到本段。"""
    rows = []
    for ln in open(reg_path, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln or ln.startswith('#'):
            continue
        p = ln.split('\t')
        if len(p) >= 3:
            al = [x for x in (p[3].split(',') if len(p) >= 4 else []) if x.strip()]
            rows.append((p[0], p[1], p[2], [x.strip() for x in al]))
    return rows


def _seg_bodies(lines):
    """{id: [(行号, 行)]}:seg_<id>() { 到它自己的行首 } 为止(None 行 = 被剥掉的私有块)。段体里顶格定义的助手函数按深度计、
    heredoc 正文(python 片段里顶格的「}」)跳过 —— 曾在第一个顶格「}」处收尾,后面的打印不受查。"""
    out, cur, depth, hd = {}, None, 0, None
    for i, ln in enumerate(lines):
        if ln is None:
            continue
        if hd is not None:
            if (ln.strip() if hd[1] else ln) == hd[0]:
                hd = None
            if cur is not None:
                out[cur].append((i + 1, ln))
            continue
        m = re.match(r'^seg_([A-Za-z0-9_]+)\(\)\s*\{', ln)
        if m and cur is None:
            cur, depth = m.group(1), 0
            out[cur] = []
            continue
        if cur is not None and re.match(r'^\}\s*$', ln):
            if depth == 0:
                cur = None
                continue
            depth -= 1
        elif cur is not None and re.match(r'^' + NAME + r'\s*\(\)\s*\{\s*(?:#.*)?$', ln):
            depth += 1
        if cur is not None:
            if not ln.lstrip().startswith('#') and '<<<' not in ln:
                mh = HEREDOC.search(ln)
                if mh:
                    hd = (mh.group(4), mh.group(1) == '-')
            out[cur].append((i + 1, ln))
    return out


SEG_PRINT_NO = re.compile(r'\b(?:echo|bad|ok|warn)\s+(?:-[en]+\s+)?["\']\[(\d+)\]')


def printed_number_lint(pf_dir, tables):
    """⑬ 段体里 echo / bad / ok / warn 打印的「[N]」开头,N 必须是本段段号或登记表第四列登记的子段号
       (写 ${PF_NO} 的不在此列)—— 否则照输出里的号跑 --only N 会退 2「本仓没有这些段号」。
       tables:[(登记表名, 行, 是否按投影读)];两张表都在时两张都查(共享段在两张表里号不同时,只有 ${PF_NO} 两边都对)。"""
    out = []
    for label, rows, projected in tables:
        cache = {}
        for sid, no, rel, aliases in rows:
            path = os.path.join(pf_dir, rel)
            if not os.path.isfile(path):
                continue
            if rel not in cache:
                lines = open(path, encoding='utf-8').read().split('\n')
                cache[rel] = _seg_bodies(project_lines(lines) if projected else lines)
            allowed = {no} | set(aliases)
            seen = set()
            for lno, ln in cache[rel].get(sid, []):
                if ln.lstrip().startswith('#'):
                    continue
                for m in SEG_PRINT_NO.finditer(ln):
                    n = m.group(1)
                    if n in allowed or (rel, lno, n) in seen:
                        continue
                    seen.add((rel, lno, n))
                    out.append((rel, lno, '⑬ seg_%s(%s 里是 [%s])打印「[%s]」:照输出里的号 --only %s 会退 2 —— 改写 ${PF_NO},或把 %s 登记成本段子段号(%s 第四列)' % (sid, label, no, n, n, n, label)))
    return out


SHARED_COMMENT_NO = re.compile(r'(?<![A-Za-z0-9_\]}])\[(\d{1,3})\]')   # 前面紧贴标识符 / ] / } 的是下标(arr[0]),不算段号
SEG_HEAD_NO = re.compile(r'^\s*#\s*(\d{1,3})[a-z]?\.\s')


def shared_comment_number_lint(pf_dir, tables):
    """⑭ 共享段文件(segments/*.sh 里非 .public.sh 的,外加 lib.sh;两张登记表都执行)按投影读,注释里写的「[N]」:
       两张登记表都在时,N 必须在两张表里指同一个 id;只有 registry.tsv 一张表时,N 必须在这张表里 —— 否则总有一张表的读者照注释找到别的段 / 不存在的段。
       段头注释写死段号(「# 114. …」)一律红(打印已用 ${PF_NO})。改法:写 seg_<id> / 「本段」/ 语义名,不写段号。"""
    maps = [{no: sid for sid, no, _, _ in rows} for _, rows, _ in tables]
    alias_sets = [{a for _, _, _, al in rows for a in al} for _, rows, _ in tables]
    rels = sorted(r for r in os.listdir(os.path.join(pf_dir, 'segments'))
                  if r.endswith('.sh') and not r.endswith('.public.sh'))
    out = []
    for rel in ['lib.sh'] + ['segments/' + r for r in rels]:
        path = os.path.join(pf_dir, rel)
        if not os.path.isfile(path):
            continue
        lines = project_lines(open(path, encoding='utf-8').read().split('\n'))
        for i, ln in enumerate(lines):
            if ln is None:
                continue
            k = ln.find('#')
            if k < 0 or not ln.lstrip().startswith('#'):
                continue
            hm = SEG_HEAD_NO.match(ln)
            nums = [hm.group(1)] if hm else [m.group(1) for m in SHARED_COMMENT_NO.finditer(ln)]
            for n in nums:
                ids = [mp.get(n) for mp in maps]
                if all(n in s for s in alias_sets):
                    continue   # 每张表里都是子段号:两边输出里都打这个号,照它 --only 都落在打印它的那段
                if hm and (any(x is None for x in ids) or len(set(ids)) != 1):
                    out.append((rel, i + 1, '⑭ 共享段文件的段头注释写死段号「%s」,两张登记表里不指同一段:打印已用 ${PF_NO} —— 去掉段号' % ln.strip()[:40]))
                    continue
                if any(x is None for x in ids) or len(set(ids)) != 1:
                    where = ' / '.join('%s 里%s' % (tables[j][0], ('是 seg_' + ids[j]) if ids[j] else '没有') for j in range(len(maps)))
                    out.append((rel, i + 1, '⑭ 共享段文件注释里的「[%s]」两张登记表里不指同一段(%s):改写 seg_<id> / 「本段」/ 语义名' % (n, where)))
    return out


def number_tables(pf_dir):
    """⑬ / ⑭ 用的表:registry.tsv 按投影读;extra/registry.tsv 在场时一并查。"""
    tables = []
    pub = os.path.join(pf_dir, 'registry.tsv')
    priv = os.path.join(pf_dir, 'extra', 'registry.tsv')
    if os.path.isfile(priv):
        tables.append(('extra/registry.tsv', registry_table(priv), False))
    if os.path.isfile(pub):
        tables.append(('registry.tsv', registry_table(pub), True))
    return tables


def run(pf_dir, entry, lib, quiet=False):
    reg, rows, problems = analyze(pf_dir, entry, lib)
    for name, rel, ln, var, owners in problems:
        where = ('只在 ' + ' / '.join(owners[:4]) + (' …' if len(owners) > 4 else '') + ' 里赋值') if owners else '哪里都没有赋值'
        print('%s(preflight/%s,函数体第 %d 行)读 $%s,但它%s —— `--only` / `--from` 跳过那段就 unbound variable;'
              '挪到段文件顶层当装载期常量,或在本段里自己算' % (name, rel, ln, var, where))
    rels = []
    for _, _, rel in rows:
        if rel not in rels:
            rels.append(rel)
    lint = segment_file_lint(pf_dir, rels)
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(pf_dir)))
    if os.path.isdir(os.path.join(repo_root, RS_SRC_REL)):
        # 两张登记表引用的段文件都查(本仓不执行的另一份也会进另一仓执行)
        rs_rels = list(rels)
        for reg_path in (os.path.join(pf_dir, 'registry.tsv'), os.path.join(pf_dir, 'extra', 'registry.tsv')):
            if os.path.isfile(reg_path):
                for ln in open(reg_path, encoding='utf-8'):
                    p = ln.rstrip('\n').split('\t')
                    if len(p) >= 3 and not ln.startswith('#') and p[2] not in rs_rels:
                        rs_rels.append(p[2])
        lint += rs_anchor_lint(pf_dir, rs_rels, repo_root, lib)
        lint += recursive_grep_lint(pf_dir, [r for r in rs_rels if r not in rels])
    lint += recursive_grep_lint(pf_dir, rels)
    tables = number_tables(pf_dir)
    lint += printed_number_lint(pf_dir, tables)
    lint += shared_comment_number_lint(pf_dir, tables)
    for rel, ln, msg in lint:
        print('preflight/%s 第 %d 行:%s' % (rel, ln, msg))
    if not quiet:
        print('段 %d 个(%s),跨段隐式传值 %d 处,写法问题 %d 处' % (len(rows), os.path.relpath(reg, pf_dir), len(problems), len(lint)))
    return 1 if (problems or lint) else 0


def self_test():
    d = tempfile.mkdtemp(prefix='pfstruct-selftest.')
    try:
        os.makedirs(os.path.join(d, 'segments'))
        entry = os.path.join(d, 'entry.sh')
        lib = os.path.join(d, 'lib.sh')
        open(entry, 'w').write('. lib.sh\npf_run\n')
        open(lib, 'w').write('REPO_ROOT=/x\nPF_DIR=/y\nPF_NO=""\npf_run(){ PF_LOADED=1; }\nok(){ :; }\n')

        def case(seg_text, want_vars, label):
            open(os.path.join(d, 'segments', 'a.sh'), 'w').write(seg_text)
            open(os.path.join(d, 'registry.tsv'), 'w').write('1\t1\tsegments/a.sh\n2\t2\tsegments/a.sh\n')
            got = sorted({p[3] for p in analyze(d, entry, lib)[2]})
            assert got == sorted(want_vars), '%s: 期望 %s,实得 %s' % (label, want_vars, got)

        case('seg_1() {\nX1="${REPO_ROOT}/a"\n}\nseg_2() {\nok "$X1"\n}\n', ['X1'], '后段读前段函数体里赋的变量必须报')
        case('X1="${REPO_ROOT}/a"\nseg_1() {\n:\n}\nseg_2() {\nok "$X1"\n}\n', [], '段文件顶层赋值 = 装载期常量,不报')
        case('seg_1() {\n:\n}\nseg_2() {\nX1=1\nok "${X1}"\n}\n', [], '本段自己赋值不报')
        case('seg_1() {\n:\n}\nseg_2() {\nok "${ENVX:-}" "${ENVY-d}" "${ENVZ:+z}"\n}\n', [], '带缺省值的展开不报')
        case('seg_1() {\n:\n}\nseg_2() {\nok "${ENVX}"\n}\n', ['ENVX'], '没缺省值的外来变量要报')
        case("seg_1() {\n:\n}\nseg_2() {\nawk '{print $NF; x=$UNSET}' f\n# $COMMENTED\n}\n", [], '单引号串与注释里的 $ 不算')
        case("seg_1() {\n:\n}\nseg_2() {\npython3 - <<'PY'\nprint('$X')\nPY\ncat <<EOF\n$Y\nEOF\n}\n", ['Y'], '带引号定界符的 heredoc 不展开,不带引号的展开')
        case('h(){ HX=1; }\nseg_1() {\n:\n}\nseg_2() {\nh\nok "$HX"\n}\n', [], '本段调用的助手里赋值不报')
        case('seg_1() {\n:\n}\nseg_2() {\nfor V in a b; do ok "$V"; done\nwhile read -r A B; do ok "$A$B"; done < f\nlocal L=1; ok "$L"\n}\n', [], 'for / read / local 都算赋值')
        case('seg_1() {\n:\n}\nseg_2() {\nok "$PF_LOADED" "$HOME" "$1"\n}\n', [], '公共库函数赋的 / bash 自带的不报')
        open(os.path.join(d, 'inv.sh'), 'w').write('INV_LIST=(a b)\n')
        case('seg_1() {\n:\n}\nseg_2() {\nS2_F="${PF_DIR}/inv.sh"\n. "${S2_F}"\nok "${INV_LIST[@]}"\nok "$NOT_THERE"\n}\n', ['NOT_THERE'], '本段装进来的文件里赋的变量算赋值')
        case('seg_1() {\n:\n}\nseg_2() {\nwhile IFS= read -r U; do ok "$U"; done < f\nwhile read -r b; do ok "$b"; done < f\n}\n', [], 'read -r 名 两种写法')
        case('seg_1() {\nFROM1=1\n}\nseg_2() {\n. "${PF_DIR}/absent.sh"\nok "$FROM_ABSENT" "$FROM1"\n}\n', ['FROM1'], '装不进来的文件:只放过哪里都没赋值的,跨段的照报')
        case('seg_1() {\nAR=1\n}\nseg_2() {\nok "$(( AR + 1 ))"\n}\n', ['AR'], '算术 $(( )) 里的裸名读前段函数体变量必须报')
        case('seg_1() {\nh1(){\n  :\n}\nX1=1\n}\nseg_2() {\nok "$X1"\n}\n', ['X1'], '段体里顶格定义的助手收尾之后的赋值仍属本段(跨段读必须报)')
        case('seg_1() {\nAR=1\n}\nseg_2() {\n(( AR++ ))\nlet BR=AR+1\n}\n', ['AR'], '(( )) / let 里的裸名同样算读;let 左值算本段赋值')
        case('seg_1() {\n:\n}\nseg_2() {\nN=0\n(( N += 1 ))\nok "$(( N * 2 + 10#${HOME:0:1} ))"\n(( M = 3 ))\nok "$(( M ))"\n}\n', [], '本段赋值 / 算术里赋值 / ${…} 与进制前缀不误报')

        def lint_case(seg_text, want, label):
            open(os.path.join(d, 'segments', 'a.sh'), 'w').write(seg_text)
            got = [x[1] for x in segment_file_lint(d, ['segments/a.sh'])]
            assert got == want, '%s: 期望行 %s,实得 %s' % (label, want, got)

        lint_case('seg_1() {\ngrep -aE "\\.skip|xdescribe|xit\\(" "$F" && bad x\n}\n', [2], '段里自写 skip 正则必须报')
        lint_case('seg_1() {\npf_test_disabled "$F" && bad "被 skip / only 旁路"\n# grep "\\.skip" 注释不算\n}\n', [], '调 pf_test_disabled 的行与注释不报')
        lint_case('seg_1() {\ngrep -cE "pytestmark|importorskip" "$F" && bad x\n}\n', [2], '段里自写整模块 skip / importorskip 正则必须报')
        lint_case('seg_1() {\nT="$(mktemp -d)"\nU="$(mktemp "${PF_TMP}/u.XXXXXX")"\nfor K in \'X="$(mktemp -d\'; do :; done\n}\n', [2], 'mktemp 不在 PF_TMP 下必须报;单引号串里的字面不算')
        lint_case('seg_1() {\ngrep -q "import { a, b } from \'./x\';" "$F" || bad x\n[ "$(pf_code "$F" | grep -acF "import { c } from \'./y\';")" != "0" ] || bad y\ngrep -q "Z } from \'./z\'" "$F" || bad z\n}\n', [2, 3, 4], '按字面认 import 语句必须报(整条 / 经 pf_code / 只写尾巴)')
        lint_case('seg_1() {\npf_imports "$F" "import { a } from \'./x\';" || bad x\ngrep -q "from \'./cityMatch\'" "$F" || bad y\n}\n', [], '调 pf_imports 的行、只认来源模块的不报')
        n_rs = rs_self_test()
        rn_cases = [
            ('grep -rq "bad_pattern" "${UI}" && { bad x; }\n', [2], '递归反锚扫整树、没排除测试 = 红'),
            ('[ -n "$(pf_prod_hits -a "bad_pattern" "${UI}" js)" ] && { bad x; }\n', [], '走 pf_prod_hits 不报'),
            ('grep -rq "x" "${UI}" --exclude-dir=__tests__ && { bad x; }\n', [], '显式排除测试目录不报'),
            ('# 全树:保密禁词,测试也会同步\nif grep -rnE "secret" "${UI}" >/dev/null; then\n  bad x\nfi\n', [], '上一行写了「# 全树:」理由不报'),
            ('if grep -rnE "secret" "${UI}" >/dev/null; then\n  bad x\nfi\n', [2], 'if grep -r … then bad(反锚)同样要排除测试或写理由'),
            ('N=$(grep -arl "registerX(" "${UI}/src/components" 2>/dev/null | wc -l)\n[ "$N" -ge 4 ] || bad x\n', [2], '递归计数(测试会替产品凑数)= 红'),
            ('grep -rq "must_have" "${UI}/src" || { bad x; }\n', [2], '递归正锚(测试会替产品作证)= 红'),
            ('L=$(grep -rnE "x" \\\n  "${UI}/a" \\\n  | grep -av __tests__ || true)\n', [], '续行里排除测试也算'),
            ('H=$(grep -rn "x" "${UI}/a.js" "${UI}/b/c.py" "${PY}/"*.py)\n', [], '只点名文件(带扩展名 / 通配)不在此列'),
        ]
        for text, want, label in rn_cases:
            open(os.path.join(d, 'segments', 'a.sh'), 'w').write('seg_1() {\n' + text + '}\n')
            got = [x[1] for x in recursive_grep_lint(d, ['segments/a.sh'])]
            assert got == want, '%s: 期望行 %s,实得 %s' % (label, want, got)
        n_no = number_self_test()
        print('check_preflight_structure 自证 %d 向全过' % (23 + n_rs + len(rn_cases) + n_no))
        return 0
    finally:
        shutil.rmtree(d, ignore_errors=True)


def number_self_test():
    """⑬ / ⑭ 判别力自证:临时 preflight 目录里两张登记表 + 共享段文件,逐向核报 / 不报。"""
    d = tempfile.mkdtemp(prefix='pfstruct-noself.')
    try:
        os.makedirs(os.path.join(d, 'segments'))
        os.makedirs(os.path.join(d, 'extra'))
        open(os.path.join(d, 'lib.sh'), 'w').write('# 公共库\n')
        # extra 表:x 段号 10、y 段号 20(子段号 21);registry.tsv:x 段号 30、y 段号 20(子段号 21)
        open(os.path.join(d, 'extra', 'registry.tsv'), 'w').write('x\t10\tsegments/a.sh\ny\t20\tsegments/a.sh\t21\n')
        open(os.path.join(d, 'registry.tsv'), 'w').write('x\t30\tsegments/a.sh\ny\t20\tsegments/a.sh\t21\n')
        mk = _PRIV_MK
        cases = [
            ('seg_x() {\necho "[${PF_NO}] x"\n}\nseg_y() {\necho "[20] y"\nok "[21] 子段"\n}\n', [], [], '本段号 / ${PF_NO} / 登记的子段号 不报'),
            ('seg_x() {\necho "[10] x"\n}\nseg_y() {\n:\n}\n', ['⑬'], [], '共享段打印字面段号、两张表里号不同 = ⑬(registry.tsv 里它是 30)'),
            ("seg_x() {\nh(){\n  :\n}\npython3 - <<'PY'\nd = {\n}\nPY\necho \"[10] x\"\n}\nseg_y() {\n:\n}\n", ['⑬'], [], '段体里顶格助手 / heredoc 里顶格「}」之后的打印仍属本段 = ⑬'),
            ('seg_x() {\n:\n}\nseg_y() {\nbad "[999] 合并进来的子检查"\n}\n', ['⑬', '⑬'], [], '打印没登记的子段号 = ⑬(两张表各报一次)'),
            ('seg_x() {\n:\n}\nseg_y() {\n# 注释里提 [20] / [21] 不报;下标 arr[0] 不算\n:\n}\n', [], [], '注释里指同一段的号 / 子段号 / 下标不报'),
            ('# ---- [10] x 段的说明\nseg_x() {\n:\n}\nseg_y() {\n:\n}\n', [], ['⑭'], '共享注释写的号在两张表里指不同段 = ⑭'),
            ('# 10. x 段头\nseg_x() {\n:\n}\nseg_y() {\n:\n}\n', [], ['⑭'], '段头注释写死两张表里不同的号 = ⑭'),
            ('# @@P:x\n# 另一份说明 [10]\n# @@P:end\nseg_x() {\n:\n}\nseg_y() {\n:\n}\n'.replace('@@P', mk), [], [], '私有块里的注释投影时剥掉,不报'),
        ]
        for text, want13, want14, label in cases:
            open(os.path.join(d, 'segments', 'a.sh'), 'w').write(text)
            tables = number_tables(d)
            got13 = [x[2][0] for x in printed_number_lint(d, tables)]
            got14 = [x[2][0] for x in shared_comment_number_lint(d, tables)]
            assert sorted(got13) == sorted(want13) and sorted(got14) == sorted(want14), '%s: 期望 ⑬%s ⑭%s,实得 ⑬%s ⑭%s' % (label, want13, want14, got13, got14)
        # 只有 registry.tsv 一张表:号必须在这张表里
        os.remove(os.path.join(d, 'extra', 'registry.tsv'))
        open(os.path.join(d, 'segments', 'a.sh'), 'w').write('# 见 [77]\nseg_x() {\n:\n}\nseg_y() {\n:\n}\n')
        assert [x[2][0] for x in shared_comment_number_lint(d, number_tables(d))] == ['⑭'], '只有一张表时,注释写表里没有的号 = ⑭'
        return len(cases) + 1
    finally:
        shutil.rmtree(d, ignore_errors=True)


def rs_self_test():
    """⑪ 判别力自证:在临时仓根里造壳源码(产品文件 + 测试文件 + 带同文件测试模块的独立子模块)与一个段文件,逐向核报 / 不报。"""
    root = tempfile.mkdtemp(prefix='pfstruct-rsself.')
    try:
        src = os.path.join(root, RS_SRC_REL)
        pf = os.path.join(root, 'Horosa_Desktop_Installer', 'scripts', 'preflight')
        os.makedirs(src)
        os.makedirs(os.path.join(pf, 'segments'))
        shutil.copy(os.path.join(PF_DIR, 'rs_split.py'), os.path.join(pf, 'rs_split.py'))
        lib = os.path.join(pf, 'lib.sh')
        open(lib, 'w').write('PF_SHELL_RS_FILES="main.rs tests.rs"\nPF_SHELL_RS_STANDALONE="mcp_server.rs"\n')
        open(os.path.join(src, 'main.rs'), 'w').write('fn prod_call() { seal(&a); }\nconst ONLY_PROD: u8 = 1;\n')
        open(os.path.join(src, 'tests.rs'), 'w').write('#[test]\nfn only_test_fn() { seal(&a); let k = "ONLY_TEST_LIT"; let m = from_mode(0o666); }\n')
        open(os.path.join(src, 'mcp_server.rs'), 'w').write(
            'pub fn serve() { bind([127, 0, 0, 1]); }\npub fn constant_time_eq(a: &[u8]) -> bool { a.len() < CAP_LIMIT || a.len() >= CAP_LIMIT }\n'
            '#[cfg(test)]\nmod tests {\n    fn inline_case() { let s = "INLINE_ONLY {"; bind([127, 0, 0, 1]); }\n'
            '    fn constant_time_eq_and_bearer() { CAP_LIMIT; CAP_LIMIT; CAP_LIMIT; CAP_LIMIT; }\n    fn caps() { CAP_LIMIT; CAP_LIMIT; CAP_LIMIT; }\n}\n')
        cases = [
            ('X="$(pf_shell_rs)"\ngrep -qF \'ONLY_TEST_LIT\' "${X}" || bad x\n', ['R4', 'R1'], '正锚读全集、只被测试文件满足 = R1(且读全集本身 = R4)'),
            ('X="$(pf_shell_rs_prod)"\ngrep -qF \'ONLY_PROD\' "${X}" || bad x\n', [], '产品锚读产品集不报'),
            ('M="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs"\ngrep -qF \'INLINE_ONLY\' "${M}" || bad x\n', ['R1'], '独立子模块的正锚只被同文件测试模块满足 = R1'),
            ('M="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs"\ngrep -q \'fn inline_case\' "${M}" || bad x\n', [], '「测试在位」形状(fn 名)读含测试的面不报'),
            ('M="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs"\n[ "$(grep -c \'127, 0, 0, 1\' "${M}")" -ge 2 ] || bad x\n', ['R2'], '计数阈值靠同文件测试凑数 = R2'),
            ('R="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src"\npf_need "${R}/mcp_server.rs" "INLINE_ONLY" "x"\n', ['R1'], 'pf_need 读独立子模块、只被同文件测试满足 = R1'),
            ('M="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs"\ngrep -qF \'0.0.0.0\' "${M}" && { bad x; }\n', ['R3'], '反锚读含测试的面 = R3(哪怕眼下零命中)'),
            ('X="$(pf_shell_rs_prod)"\ngrep -qF \'from_mode(0o666)\' "${X}" && { bad x; }\n', ['R3'], '反锚只扫壳层模块(漏独立子模块)= R3'),
            ('X="$(pf_shell_rs_prod_all)"\ngrep -qF \'from_mode(0o666)\' "${X}" && { bad x; }\n[ "$(grep -acF \'0o666\' "$(pf_shell_rs_prod_all)")" = "0" ] || bad y\n', [], '反锚读全部产品代码:测试夹具不算、不报'),
            ('T="$(pf_shell_rs_tests)"\ngrep -qF \'ONLY_TEST_LIT\' "${T}" || bad x\n', [], '测试在位锚读测试集不报'),
            ("bash -c '\n  cksum < \"$(pf_shell_rs)\"\n'\n", [], '单引号串里的 pf_shell_rs(拼接新鲜度自证)不算读面'),
            ('M="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs"\n[ "$(pf_code "${M}" | grep -acF \'CAP_LIMIT\')" -ge 2 ] || bad x\n', ['R2'],
             '计数锚读含测试的面、产品 2 处已够阈值 2、测试 7 处也命中 = R2(经 pf_code 管道的写法也认)'),
            ('M="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs"\n[ "$(pf_code "$(pf_rs_prod "${M}")" | grep -acF \'CAP_LIMIT\')" -ge 2 ] || bad x\n', [],
             '计数锚改读 pf_rs_prod "${变量}" 不报'),
            ('M="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs"\ngrep -aq "fn constant_time_eq" "${M}" || bad x\n', ['R1'],
             '产品锚「fn x」恰是测试名的前缀(产品 1 处、测试 1 处)= R1,「测试在位」豁免只在产品零命中时成立'),
            ('M="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs"\ngrep -aqF "pub fn constant_time_eq(" "$(pf_rs_prod "${M}")" || bad x\n', [],
             '产品锚读 pf_rs_prod 不报'),
        ]
        for text, want, label in cases:
            open(os.path.join(pf, 'segments', 'a.sh'), 'w').write('seg_1() {\n' + text + '}\n')
            got = sorted(x[2].split(' ', 1)[0] for x in rs_anchor_lint(pf, ['segments/a.sh'], root, lib))
            assert got == sorted(want), '%s: 期望 %s,实得 %s' % (label, want, got)
        return len(cases)
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == '__main__':
    if '--self-test' in sys.argv[1:]:
        sys.exit(self_test())
    args = sys.argv[1:]
    here = HERE
    if '--root' in args:  # 查另一个仓(例:对拍另一份工作树)
        here = os.path.join(os.path.abspath(args[args.index('--root') + 1]), 'Horosa_Desktop_Installer', 'scripts')
    pf = os.path.join(here, 'preflight')
    sys.exit(run(pf, os.path.join(here, 'release_preflight.sh'), os.path.join(pf, 'lib.sh'), quiet='-q' in args))
