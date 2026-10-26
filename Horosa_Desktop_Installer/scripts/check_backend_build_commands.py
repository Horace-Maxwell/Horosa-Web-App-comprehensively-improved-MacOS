#!/usr/bin/env python3
"""后端(Maven 多模块)构建命令的全仓检查。

   python3 check_backend_build_commands.py              # 查本仓
   python3 check_backend_build_commands.py --root <仓根> # 查另一个仓
   python3 check_backend_build_commands.py --self-test  # 判别力自证(构造坏样本,检查必须报出来)

为什么要查:后端 Horosa-Web/astrostudysrv 是聚合 pom 管着的多模块工程,模块清单唯一的真值是它的 <modules>。
  ① 逐模块 `cd 模块 && mvn install` / `mvn -f 模块/pom.xml install`:新机器的本地仓库里没有父 pom 与兄弟模块,
     第二个模块就解析失败(源码一键部署链曾因此在新机上必然失败);旧机器上则悄悄链接本地仓库里的旧件
     (发版基线的 mvn 绿,证明的可能是另一份代码)。
  ② 脚本里手抄一份模块清单:下架一个模块后清单没跟着改,构建当场中止。
规则:
  R1 仓内脚本 / 文档 / Eclipse 工程文件里写到的后端模块名(`astrostudysrv/<名>`、`-pl <名,…>`、`<project><名></project>`)
     必须都在聚合 pom 的 <modules> 里。
  R2 凡调用 Maven 构建 / 测试(mvn / run_maven / mvnw 带 clean·install·package·test·compile·verify 或 -f / -pl),
     必须带 `-f …/astrostudysrv/pom.xml`(聚合 pom;脚本里也可以是赋值为它的变量);只跑某几个模块用 `-pl 模块 -am`。
  R3 带 `-pl` 必须同时带 `-am`(兄弟模块在同一个 reactor 里引用当次编译的产物,不吃本地仓库)。
  另做两个零副作用的「干跑」:把 scripts/mac/bootstrap_and_run.sh 的 build_backend_if_needed 与
  tools/mac/Prepare_Runtime_Mac.command 的 prepare_backend_bundle 原样摘出来,Maven 打桩,
  断言恰好调用一次、带聚合 pom;Maven 失败时不许被吞(要返回非零)。
历史记录类文档(发布记录、归档、对拍报告)不核:见 HISTORY_PREFIXES;单个文件首 5 行写 `backend-build-lint: history` 也跳过。
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRV = 'Horosa-Web/astrostudysrv'
SCRIPT_EXT = ('.sh', '.command', '.py', '.js', '.mjs', '.cjs', '.ts')
SCRIPT_NAMES = ('horosa',)
SKIP_PREFIXES = ('Horosa-Web/vendor/', 'Horosa-Web/flatlib-ctrad2/', 'Horosa-Web/astrostudyui/src/', 'build/',
                 'runtime/', 'Horosa-Web/astrostudyui/dist', 'Horosa_Desktop_Installer/web/')
HISTORY_PREFIXES = ('docs/archive/', 'docs/perf/', 'Horosa-Web/docs/', 'UPGRADE_LOG.md')
HISTORY_MARK = 'backend-build-lint: history'
PHASES = ('clean', 'install', 'package', 'test', 'compile', 'verify', 'deploy', 'dependency:', 'spring-boot:')
SELF = 'Horosa_Desktop_Installer/scripts/check_backend_build_commands.py'

NAME = r'[A-Za-z_][A-Za-z0-9_]*'
INVOKE = re.compile(r'(?<![\w/.-])(?:\./)?(mvnw|mvn|run_maven|"\$\{MAVEN_CMD\[@\]\}")[ \t]+(?=[-A-Za-z"$])')
CMD_END = re.compile(r'(&&|\|\||[;|`\n)]|\(JDK|\s→|\s->)')
MOD_TOKEN = re.compile(r'astrostudysrv/([A-Za-z][A-Za-z0-9_-]*)(?=[/\s"\'`)\]:,;|*]|$)')
PROJECT_TAG = re.compile(r'<project>\s*([^<\s]+)\s*</project>')


def modules_of(root):
    pom = os.path.join(root, SRV, 'pom.xml')
    s = open(pom, encoding='utf-8').read()
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    return set(re.findall(r'<module>\s*([^<\s]+)\s*</module>', s))


def tracked(root):
    try:
        out = subprocess.run(['git', '-C', root, '-c', 'core.quotepath=false', 'ls-files', '-z'],
                             capture_output=True, check=True).stdout.decode('utf-8', 'replace')
        files = [p for p in out.split('\0') if p]
        if files:
            return files
    except Exception:
        pass
    # 不在 git 里(或一个跟踪文件都没有):按目录走,别「一个文件都没扫」就报零问题
    res = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in ('.git', 'node_modules', 'target')]
        for f in fs:
            res.append(os.path.relpath(os.path.join(d, f), root))
    return res


def kind_of(rel):
    if rel == SELF or '/node_modules/' in rel or rel.startswith(SKIP_PREFIXES):
        return None
    base = os.path.basename(rel)
    if base == '.project' and rel.startswith(SRV + '/'):
        return 'eclipse'
    if rel.endswith('.md'):
        return None if rel.startswith(HISTORY_PREFIXES) else 'doc'
    if rel.endswith(SCRIPT_EXT) or base in SCRIPT_NAMES:
        return 'script'
    return None


def var_values(text):
    """脚本里 `名=值` 的值(去引号),给 -f "${名}/pom.xml" 这类写法解引用。"""
    vals = {}
    for m in re.finditer(r'(?m)^\s*(?:local\s+|export\s+|readonly\s+)?(' + NAME + r')=("[^"\n]*"|\'[^\'\n]*\'|\S+)', text):
        vals[m.group(1)] = m.group(2).strip('"\'')
    return vals


def f_arg_ok(arg, vals):
    a = arg.strip('"\'')
    if re.search(r'(^|/)astrostudysrv/pom\.xml$', a):
        return True
    m = re.fullmatch(r'\$\{?(' + NAME + r')\}?(/pom\.xml)?', a)
    if m:
        v = vals.get(m.group(1), '')
        if m.group(2):
            return bool(re.search(r'(^|/)astrostudysrv/?$', v))
        return bool(re.search(r'(^|/)astrostudysrv/pom\.xml$', v))
    return False


def check_invocations(rel, text, vals, mods, problems):
    for m in INVOKE.finditer(text):
        tail = text[m.end():]
        e = CMD_END.search(tail)
        cmd = tail[:e.start()] if e else tail
        toks = re.findall(r'"[^"]*"|\'[^\']*\'|\S+', cmd)
        if not toks or toks[0] in ('-v', '--version', '-version', '-h', '--help'):
            continue
        has_phase = any(t.strip('"\'').startswith(PHASES) for t in toks)
        has_f = '-f' in toks or '--file' in toks
        has_pl = any(t in ('-pl', '--projects') for t in toks)
        if not (has_phase or has_f or has_pl):
            continue
        line = text.count('\n', 0, m.start()) + 1
        shown = (m.group(1) + ' ' + cmd.strip())[:120]
        if has_f:
            i = toks.index('-f') if '-f' in toks else toks.index('--file')
            arg = toks[i + 1] if i + 1 < len(toks) else ''
            if not f_arg_ok(arg, vals):
                problems.append((rel, line, 'R2', '构建命令 -f 指向的不是聚合 pom(%s/pom.xml):`%s` —— 改成 `mvn -f %s/pom.xml …`,'
                                 '只跑某几个模块用 `-pl 模块 -am`' % (SRV, shown, SRV)))
        else:
            problems.append((rel, line, 'R2', '构建命令没带 `-f …/astrostudysrv/pom.xml`(逐模块 / 当前目录构建):`%s` —— 改成 `mvn -f %s/pom.xml …`'
                             % (shown, SRV)))
        if has_pl:
            if '-am' not in toks and '--also-make' not in toks:
                problems.append((rel, line, 'R3', '带 -pl 却没带 -am:`%s` —— 兄弟模块会去本地仓库取旧件' % shown))
            i = toks.index('-pl') if '-pl' in toks else toks.index('--projects')
            for name in (toks[i + 1].strip('"\'').split(',') if i + 1 < len(toks) else []):
                if re.fullmatch(r':?[A-Za-z][A-Za-z0-9_-]*', name) and name.lstrip(':') not in mods:
                    problems.append((rel, line, 'R1', '-pl 写了聚合 pom 里没有的模块「%s」' % name))


def check_text(rel, kind, text, mods, problems):
    if kind == 'eclipse':
        for m in PROJECT_TAG.finditer(text):
            if m.group(1) not in mods:
                problems.append((rel, text.count('\n', 0, m.start()) + 1, 'R1',
                                 'Eclipse 工程引用了聚合 pom 里没有的模块「%s」' % m.group(1)))
        return
    if kind == 'doc' and HISTORY_MARK in '\n'.join(text.split('\n')[:5]):
        return
    for m in MOD_TOKEN.finditer(text):
        name = m.group(1)
        if name not in mods and name != 'pom':
            problems.append((rel, text.count('\n', 0, m.start()) + 1, 'R1',
                             '写到了聚合 pom 里没有的后端模块「%s/%s」(模块清单唯一真值 = %s/pom.xml 的 <modules>)' % (SRV, name, SRV)))
    check_invocations(rel, text, var_values(text) if kind == 'script' else {}, mods, problems)


def extract_fn(text, name):
    m = re.search(r'(?ms)^' + re.escape(name) + r'\(\) \{\n.*?^\}\n', text)
    return m.group(0) if m else None


def dry_runs(root, problems):
    """零副作用干跑:Maven / 打印 / 失败函数全打桩,只看调用形状与失败是否外传。"""
    bash = shutil.which('bash')
    if not bash:
        return
    boot = os.path.join(root, 'scripts/mac/bootstrap_and_run.sh')
    if os.path.isfile(boot):
        t = open(boot, encoding='utf-8').read()
        fn = extract_fn(t, 'build_backend_if_needed')
        if not fn:
            problems.append(('scripts/mac/bootstrap_and_run.sh', 0, 'DRY', '找不到 build_backend_if_needed() —— 干跑核不了(改了函数名要同步本检查)'))
        else:
            d = tempfile.mkdtemp(prefix='bbc-dry.')
            try:
                srv = os.path.join(d, 'astrostudysrv')
                os.makedirs(srv)
                open(os.path.join(srv, 'pom.xml'), 'w').write('<project/>')
                prog = ('set -euo pipefail\nSERVER_DIR=%s\nLOG=%s\nbackend_needs_build(){ return 0; }\n'
                        'say(){ :; }\nfail(){ echo "FAIL $*" >> "$LOG"; exit 9; }\n'
                        'run_maven(){ printf "CALL"; printf " <%%s>" "$@"; echo; } >> %s\n%s\nbuild_backend_if_needed\n'
                        % (sh_q(srv), sh_q(os.path.join(d, 'log')), sh_q(os.path.join(d, 'log')), fn))
                r = subprocess.run([bash, '-c', prog], capture_output=True, text=True)
                log = open(os.path.join(d, 'log')).read() if os.path.exists(os.path.join(d, 'log')) else ''
                calls = [ln for ln in log.split('\n') if ln.startswith('CALL')]
                want = '<-f> <%s/pom.xml>' % srv
                if r.returncode != 0 or len(calls) != 1 or want not in calls[0] or '<install>' not in calls[0]:
                    problems.append(('scripts/mac/bootstrap_and_run.sh', 0, 'DRY',
                                     'build_backend_if_needed 干跑:应恰好调用一次 run_maven -f <聚合 pom> … install;实得 rc=%d、%d 次:%s'
                                     % (r.returncode, len(calls), ' | '.join(calls)[:300] or log[:200])))
            finally:
                shutil.rmtree(d, ignore_errors=True)
    prep = os.path.join(root, 'tools/mac/Prepare_Runtime_Mac.command')
    if os.path.isfile(prep):
        t = open(prep, encoding='utf-8').read()
        fn = extract_fn(t, 'prepare_backend_bundle')
        if not fn:
            problems.append(('tools/mac/Prepare_Runtime_Mac.command', 0, 'DRY', '找不到 prepare_backend_bundle() —— 干跑核不了'))
            return
        for mvn_rc in (0, 3):
            d = tempfile.mkdtemp(prefix='bbc-dry.')
            try:
                pom = os.path.join(d, 'astrostudysrv', 'pom.xml')
                os.makedirs(os.path.dirname(pom))
                open(pom, 'w').write('<project/>')
                log = os.path.join(d, 'log')
                boot = os.path.join(d, 'bootstrap_stub.sh')
                open(boot, 'w').write('#!/bin/sh\necho BOOT >> %s\nexit 0\n' % sh_q(log))
                os.chmod(boot, 0o755)
                prog = ('set +e\nSERVER_POM=%s\nIMAGE_DIR=%s\nBOOT_DIR=%s\nJAR_PATH=%s\nBUNDLE_DIR=%s\nBOOTSTRAP_SH=%s\n'
                        'mvn(){ printf "CALL"; printf " <%%s>" "$@"; echo; return %d; } >> %s\n%s\n'
                        'prepare_backend_bundle >/dev/null 2>&1; echo "RC $?" >> %s\n'
                        % (sh_q(pom), sh_q(os.path.join(d, 'astrostudysrv', 'image')), sh_q(os.path.join(d, 'astrostudysrv', 'astrostudyboot')),
                           sh_q(os.path.join(d, 'none.jar')), sh_q(d), sh_q(boot), mvn_rc, sh_q(log), fn, sh_q(log)))
                os.makedirs(os.path.join(d, 'astrostudysrv', 'image'))
                os.makedirs(os.path.join(d, 'astrostudysrv', 'astrostudyboot'))
                subprocess.run([bash, '-c', prog], capture_output=True, text=True)
                out = open(log).read() if os.path.exists(log) else ''
                calls = [ln for ln in out.split('\n') if ln.startswith('CALL')]
                rc = re.search(r'RC (\d+)', out)
                rc = int(rc.group(1)) if rc else -1
                booted = 'BOOT' in out.split('\n')
                # Maven 失败时:要如实返回非零,且不许再拿一键部署脚本兜底把失败盖掉(那等于把错误吞了);Maven 成功却没出 jar 时兜底可以
                good = len(calls) == 1 and ('<-f> <%s>' % pom) in calls[0] and '<install>' in calls[0] and rc != 0 and not (mvn_rc and booted)
                if not good:
                    problems.append(('tools/mac/Prepare_Runtime_Mac.command', 0, 'DRY',
                                     'prepare_backend_bundle 干跑(Maven 返回 %d、没产出 jar):应恰好调用一次 mvn -f <聚合 pom> … install、函数返回非零,'
                                     'Maven 失败时不许再调一键部署脚本兜底;实得 %d 次、返回 %d、兜底 %s:%s' % (mvn_rc, len(calls), rc, booted, ' | '.join(calls)[:300])))
            finally:
                shutil.rmtree(d, ignore_errors=True)


def sh_q(s):
    return "'" + s.replace("'", "'\\''") + "'"


def scan(root, with_dry=True):
    mods = modules_of(root)
    problems = []
    for rel in tracked(root):
        kind = kind_of(rel)
        if not kind:
            continue
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            continue
        try:
            text = open(p, encoding='utf-8').read()
        except (UnicodeDecodeError, OSError):
            continue
        if kind != 'eclipse' and 'mvn' not in text and 'maven' not in text.lower() and 'astrostudysrv/' not in text:
            continue
        check_text(rel, kind, text, mods, problems)
    if with_dry:
        dry_runs(root, problems)
    return mods, problems


def self_test():
    mods = {'boundless', 'basecomm', 'image', 'astrostudy', 'astrostudycn', 'astrostudyboot'}

    def probs(kind, text):
        p = []
        check_text('x', kind, text, mods, p)
        return sorted({r[2] for r in p})

    cases = [
        ('script', 'cd "${SERVER_DIR}/${module}" && run_maven -DskipTests install\n', ['R2'], '逐模块 cd && run_maven'),
        ('script', 'cd astrostudysrv/boundless && mvn -DskipTests install\n', ['R2'], '逐模块 cd && mvn'),
        ('script', 'mvn -q -f boundless/pom.xml test -Dtest=X\n', ['R2'], '-f 指向模块 pom'),
        ('script', 'mvn -f Horosa-Web/astrostudysrv/astrostudyboot clean package\n', ['R2'], '-f 指向模块目录'),
        ('script', 'modules=("astrostudysrv/astroreader")\n', ['R1'], '下架模块名'),
        ('script', 'mvn -o -f "${SRV}/pom.xml" test -pl boundless,astroesp -am\nSRV="${R}/Horosa-Web/astrostudysrv"\n', ['R1'], '-pl 写了不存在的模块'),
        ('script', 'mvn -o -f "${SRV}/pom.xml" test -pl boundless\nSRV="${R}/Horosa-Web/astrostudysrv"\n', ['R3'], '-pl 缺 -am'),
        ('script', 'SERVER_DIR="${P}/astrostudysrv"\nrun_maven -f "${SERVER_DIR}/pom.xml" -DskipTests clean install\n', [], '聚合 pom(变量)'),
        ('script', 'mvn -o -f "${REPO_ROOT}/Horosa-Web/astrostudysrv/pom.xml" test -pl boundless,astrostudy -am -Dsurefire.failIfNoSpecifiedTests=false\n', [], '聚合 pom + -pl -am'),
        ('script', 'command -v mvn >/dev/null\nmvn -v\necho "mvn 跳过:无服务"\n', [], '非构建调用不报'),
        ('doc', '改了 Java 用 `mvn -f astrostudy install && mvn -f astrostudyboot clean package`\n', ['R2'], '文档里的逐模块命令'),
        ('doc', '`mvn -f Horosa-Web/astrostudysrv/pom.xml clean install -DskipTests`(JDK17)\nJava mvn 矩阵\n', [], '文档里的聚合命令 / 散文提到 mvn'),
        ('doc', '<!-- backend-build-lint: history -->\n`cd astrostudy && mvn install`\n', [], '历史标记的文档跳过'),
        ('eclipse', '<projects><project>basecomm</project><project>astroreader</project></projects>', ['R1'], 'Eclipse 残留引用'),
    ]
    for kind, text, want, label in cases:
        got = probs(kind, text)
        assert got == want, '%s:期望 %s,实得 %s' % (label, want, got)
    # 干跑:摘出的函数若退回逐模块 / 吞失败,必须报出来
    d = tempfile.mkdtemp(prefix='bbc-self.')
    try:
        for sub in ('scripts/mac', 'tools/mac', SRV):
            os.makedirs(os.path.join(d, sub))
        open(os.path.join(d, SRV, 'pom.xml'), 'w').write('<modules><module>boundless</module></modules>')

        def dry(boot_fn, prep_fn):
            open(os.path.join(d, 'scripts/mac/bootstrap_and_run.sh'), 'w').write(boot_fn)
            open(os.path.join(d, 'tools/mac/Prepare_Runtime_Mac.command'), 'w').write(prep_fn)
            p = []
            dry_runs(d, p)
            return [x[0] for x in p]

        good_boot = 'build_backend_if_needed() {\n  run_maven -f "${SERVER_DIR}/pom.xml" -DskipTests clean install\n}\n'
        bad_boot = 'build_backend_if_needed() {\n  for m in boundless basecomm; do (cd "${SERVER_DIR}/$m" && run_maven -DskipTests install); done\n}\n'
        good_prep = ('prepare_backend_bundle() {\n  local rc=0\n  mvn -f "${SERVER_POM}" -DskipTests clean install || rc=$?\n'
                     '  [ "$rc" -eq 0 ] || return 1\n  [ -f "${JAR_PATH}" ] || return 1\n}\n')
        swallow_prep = ('prepare_backend_bundle() {\n  ( mvn -f "${SERVER_POM}" -DskipTests clean install ) || true\n  return 0\n}\n')
        mask_prep = ('prepare_backend_bundle() {\n  ( mvn -f "${SERVER_POM}" -DskipTests clean install ) || true\n'
                     '  [ -f "${JAR_PATH}" ] || "${BOOTSTRAP_SH}" || true\n  [ -f "${JAR_PATH}" ] || return 1\n}\n')
        assert dry(good_boot, good_prep) == [], '干跑:正确形状不报'
        assert dry(bad_boot, good_prep) == ['scripts/mac/bootstrap_and_run.sh'], '干跑:逐模块必须报'
        assert dry(good_boot, swallow_prep) == ['tools/mac/Prepare_Runtime_Mac.command'] * 2, '干跑:吞掉失败必须报'
        assert dry(good_boot, mask_prep) == ['tools/mac/Prepare_Runtime_Mac.command'], '干跑:失败后拿一键部署兜底盖掉必须报'
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print('check_backend_build_commands 自证 %d 向全过' % (len(cases) + 4))
    return 0


def main(argv):
    if '--self-test' in argv:
        return self_test()
    root = os.path.abspath(argv[argv.index('--root') + 1]) if '--root' in argv else os.path.dirname(os.path.dirname(HERE))
    mods, problems = scan(root)
    for rel, line, rule, msg in problems:
        print('%s:%s [%s] %s' % (rel, line, rule, msg))
    print('后端模块(聚合 pom)%d 个:%s;问题 %d 处' % (len(mods), ' '.join(sorted(mods)), len(problems)))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
