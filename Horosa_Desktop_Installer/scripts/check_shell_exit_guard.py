#!/usr/bin/env python3
"""仓里 shell 脚本的「出口」两条机检(预检 [324] 每轮跑)。

   python3 check_shell_exit_guard.py              # 查本仓全部受控 .sh / .command(预检自己的段文件除外,它们由 check_preflight_structure 管)
   python3 check_shell_exit_guard.py --self-test  # 判别力自证(构造坏样本 + 用 /bin/bash 真跑守卫片段)
   python3 check_shell_exit_guard.py --root <仓根>

① 开着 set -u、又挂了 EXIT trap 的脚本,必须带出口守卫片段(下面 GUARD_LINES 三行原样):
   bash 3.2(macOS 自带)下,set -u 因未赋值变量中止时,EXIT trap 里拿到的 $? 是 0 —— 不加守卫,脚本以 0 退出,
   发布 / 验收脚本的失败被报成成功(假绿)。守卫做法:显式 exit 都经同名函数记一笔,EXIT 时没记过 = 中止,改判 1;
   所以 EXIT trap 一律写成 trap 'hx_on_exit <原处理>' EXIT,脚本最后一行代码必须是显式 exit。
   同名函数里先存 $? 再记那一笔:不带参数的 exit 按「上一条命令的状态」退出,若先赋值再 builtin exit,
   上一条命令就成了赋值(状态 0),`cmd || exit` 会以 0 退出 —— 与守卫本意相反(自证组 orexit 向量真跑锁住)。
② 用了 mktemp 的脚本必须挂 EXIT trap 收临时文件(中途 set -e / set -u 中止或 Ctrl-C 时不漏;下载目录一漏几百 MB)。
③ 开着 pipefail 的脚本(含预检段文件:它们在入口的 pipefail 下执行)代码行里不许「管道接 grep -q」:grep -q 命中即退,
   上游还没写完(多行、超过管道缓冲 64KB)就吃 SIGPIPE,整条管道按失败计 —— 「命中 → 报红」的判据假绿、「命中 → 过」的假红。
   改写成 here-string(grep -q 模式 <<< "$变量")、进程替换(grep -q 模式 < <(命令))或计数(grep -c)。
不能照做的登记进 EXEMPT 并写理由(登记了却不再需要 = 过期,同样报红)。
"""
import os
import re
import subprocess
import sys
import tempfile
import shutil

GUARD_LINES = [
    'HX_EXITED=0; exit(){ local _hx_s=$?; HX_EXITED=1; if [ "$#" -eq 0 ]; then builtin exit "${_hx_s}"; fi; builtin exit "$@"; }',
    'hx_status(){ return "$1"; }',
    'hx_on_exit(){ local _hx_r=$?; if [ "${_hx_r}" = "0" ] && [ "${HX_EXITED}" != "1" ]; then _hx_r=1; fi; set +e; hx_status "${_hx_r}"; "$@"; builtin exit "${_hx_r}"; }',
]

# 路径 → {规则: 理由}
EXEMPT = {
    'Horosa-Web/start_horosa_local.sh': {
        'guard': '起服务脚本:中止路径的 EXIT 处理会按退出码去停 pid 文件里的进程,改判退出码可能停掉用户在跑的服务;'
                 '壳侧按就绪探测 + 超时判失败,不靠它的退出码',
    },
}

SET_U = re.compile(r'^\s*set\s+-[A-Za-z]*u[A-Za-z]*\b|^\s*set\s+-o\s+nounset\b', re.M)
TRAP_EXIT = re.compile(r'(?:^|[;&|\s])trap\s+(\'[^\']*\'|"[^"]*"|[^\s;]+)\s+([^\n;#]*)')
PIPE_GREP_Q = re.compile(r'(?:^|[^|])\|\s*grep\s+-[A-Za-z]*q')
PIPEFAIL = re.compile(r'\bpipefail\b')
MKTEMP = re.compile(r'(?:\$\(|^|[;&|]|\b(?:then|do|else))\s*mktemp\b', re.M)


def code_of(text):
    """去掉整行注释(shebang 一并去掉);保留行号。"""
    return '\n'.join('' if l.lstrip().startswith('#') else l for l in text.split('\n'))


def exit_traps(code):
    """EXIT trap 的处理串列表(`trap - EXIT` / `trap '' EXIT` 是撤掉,不算)。"""
    out = []
    for m in TRAP_EXIT.finditer(code):
        handler, sigs = m.group(1), m.group(2)
        if not re.search(r'\bEXIT\b', sigs):
            continue
        h = handler.strip('\'"')
        if handler == '-' or h == '':
            continue
        out.append(h)
    return out


def last_code_line(code):
    for l in reversed(code.rstrip('\n').split('\n')):
        if l.strip():
            return l.strip()
    return ''


def pipe_grep_q_lines(code):
    return [i + 1 for i, l in enumerate(code.split('\n')) if PIPE_GREP_Q.search(l)]


def check_text(rel, text, exempt=None, pipefail_ctx=False):
    ex = (EXEMPT if exempt is None else exempt).get(rel, {})
    code = code_of(text)
    probs = []
    if (pipefail_ctx or PIPEFAIL.search(code)) and 'pipe' not in ex:
        for ln in pipe_grep_q_lines(code):
            probs.append('第 %d 行「管道接 grep -q」(pipefail 下大输入假绿 / 假红):改成 grep -q … <<< "$变量" / grep -q … < <(命令) / grep -c' % ln)
    traps = exit_traps(code)
    if SET_U.search(code) and traps and 'guard' not in ex:
        if not all(g in text for g in GUARD_LINES):
            probs.append('开着 set -u 又挂了 EXIT trap,缺出口守卫片段(bash 3.2 下未赋值变量中止会以 0 退出 = 失败报成成功)')
        else:
            for h in traps:
                if not h.startswith('hx_on_exit'):
                    probs.append("EXIT trap 没经 hx_on_exit(写成 trap 'hx_on_exit %s' EXIT)" % h)
            if not re.match(r'^exit\b', last_code_line(code)):
                probs.append('最后一行代码不是显式 exit(带守卫时走到文件末尾会被当成中止改判 1)')
    if MKTEMP.search(code) and not traps and 'mktemp' not in ex:
        probs.append('用了 mktemp 却没挂 EXIT trap 收临时文件(中途中止 / Ctrl-C 即漏)')
    return probs


def tracked_scripts(root):
    try:
        out = subprocess.run(['git', '-C', root, 'ls-files', '-z', '--', '*.sh', '*.command', 'horosa'],
                             capture_output=True, check=True).stdout.decode('utf-8', 'replace')
    except Exception:
        return []
    files = []
    for rel in out.split('\0'):
        if not rel or '/vendor/' in rel or rel.startswith('vendor/') or 'node_modules/' in rel:
            continue
        files.append(rel)
    return files


def run(root):
    problems = []
    files = tracked_scripts(root)
    present = set()
    for rel in files:
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            continue
        present.add(rel)
        text = open(p, encoding='utf-8', errors='replace').read()
        if rel.startswith('Horosa_Desktop_Installer/scripts/preflight/'):
            # 预检段文件 / 公共库:出口与临时目录由 check_preflight_structure 管;这里只核 ③(它们在入口的 pipefail 下执行)
            msgs = [m for m in check_text(rel, text, pipefail_ctx=True) if '管道接 grep -q' in m]
        else:
            msgs = check_text(rel, text)
        for msg in msgs:
            problems.append('%s:%s' % (rel, msg))
    for rel, rules in EXEMPT.items():
        p = os.path.join(root, rel)
        if rel not in present:
            continue   # 这份检出里没有(另一仓 / 精简检出)不算过期
        text = open(p, encoding='utf-8', errors='replace').read()
        code = code_of(text)
        if 'guard' in rules and not (SET_U.search(code) and exit_traps(code)):
            problems.append('%s:EXEMPT 里的 guard 豁免已不需要(不再同时开 set -u 与 EXIT trap)—— 删掉这一条' % rel)
        if 'mktemp' in rules and (not MKTEMP.search(code) or exit_traps(code)):
            problems.append('%s:EXEMPT 里的 mktemp 豁免已不需要 —— 删掉这一条' % rel)
    for msg in problems:
        print('❌ ' + msg)
    print('脚本出口检查:%d 个脚本,问题 %d 处' % (len(present), len(problems)))
    return 1 if problems else 0


def self_test():
    V = []
    G = '\n'.join(GUARD_LINES) + '\n'
    V.append(('set -u + EXIT trap 不带守卫 → 红', check_text('a.sh', "set -euo pipefail\nT=$(mktemp -d)\ntrap 'rm -rf \"$T\"' EXIT\nexit 0\n", {}), True))
    V.append(('带守卫 + hx_on_exit + 末尾 exit → 过', check_text('a.sh', "set -euo pipefail\n" + G + "T=$(mktemp -d)\ntrap 'hx_on_exit rm -rf \"$T\"' EXIT\nexit 0\n", {}), False))
    V.append(('带守卫但 trap 没经 hx_on_exit → 红', check_text('a.sh', "set -u\n" + G + "trap cleanup EXIT INT\nexit 0\n", {}), True))
    V.append(('带守卫但末尾不是 exit → 红', check_text('a.sh', "set -u\n" + G + "trap 'hx_on_exit cleanup' EXIT\necho done\n", {}), True))
    V.append(('mktemp 没挂 EXIT trap → 红', check_text('a.sh', 'set -u\nT="$(mktemp -d)"\necho "$T"\n', {}), True))
    V.append(('mktemp 登记豁免 → 过', check_text('a.sh', 'set -u\nT="$(mktemp -d)"\n', {'a.sh': {'mktemp': '理由'}}), False))
    V.append(('不开 set -u 的普通 EXIT trap → 过', check_text('a.sh', "R=$(mktemp)\ntrap 'rm -f \"$R\"' EXIT\n", {}), False))
    V.append(('pipefail 下「echo 变量 | grep -q」→ 红', check_text('a.sh', 'set -o pipefail\necho "$x" | grep -q foo && echo y\n', {}), True))
    V.append(('here-string / 进程替换 / || grep -q 不算管道 → 过', check_text('a.sh', 'set -o pipefail\ngrep -q foo <<< "$x" && grep -q a < <(ls) || grep -q b f\n', {}), False))
    V.append(('没开 pipefail 的脚本不查 ③', check_text('a.sh', 'echo "$x" | grep -q foo\n', {}), False))
    V.append(("trap - EXIT(撤掉)不算挂 / 注释里的 mktemp 不算", check_text('a.sh', "set -u\n# T=$(mktemp)\ntrap - EXIT\necho x\n", {}), False))
    bad = 0
    for label, probs, want_red in V:
        ok = bool(probs) == want_red
        bad += 0 if ok else 1
        print('%s %s%s' % ('✅' if ok else '❌', label, '' if ok else ' → %s' % probs))
    # 守卫片段真跑(/bin/bash = macOS 自带 3.2):未赋值中止 / set -e 失败 / 显式 exit N / 正常结束,退出码与处理函数读到的 $? 都对
    d = tempfile.mkdtemp(prefix='exit-guard-selftest.')
    try:
        script = os.path.join(d, 'g.sh')
        open(script, 'w').write('set -euo pipefail\n' + G +
                                'cleanup(){ local code=$?; echo "saw=${code}" >&2; }\n'
                                "trap 'hx_on_exit cleanup' EXIT\n"
                                'case "${WHAT}" in unset) echo "${NOPE_UNSET_X}" ;; fail) false ;; exit3) exit 3 ;; ok) : ;;'
                                ' orexit) false || exit ;; bareok) true; exit ;; esac\n'
                                'exit 0\n')
        bash = '/bin/bash' if os.path.exists('/bin/bash') else 'bash'
        for what, want in (('unset', 1), ('fail', 1), ('exit3', 3), ('ok', 0), ('orexit', 1), ('bareok', 0)):
            r = subprocess.run([bash, script], env=dict(os.environ, WHAT=what), capture_output=True, text=True)
            ok = r.returncode == want and ('saw=%d' % want) in r.stderr
            bad += 0 if ok else 1
            print('%s 守卫真跑 %s → 退出码 %d、处理函数读到 %d%s' % ('✅' if ok else '❌', what, want, want, '' if ok else '(实得 %d / %s)' % (r.returncode, r.stderr.strip()[-120:])))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    n = len(V) + 6
    print('== 脚本出口检查器自证:%d/%d 按预期 ==' % (n - bad, n))
    return 1 if bad else 0


if __name__ == '__main__':
    args = sys.argv[1:]
    if '--self-test' in args:
        sys.exit(self_test())
    root = os.path.abspath(args[args.index('--root') + 1]) if '--root' in args else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.exit(run(root))
