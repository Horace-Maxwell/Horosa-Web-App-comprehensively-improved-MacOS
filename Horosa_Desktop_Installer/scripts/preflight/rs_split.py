#!/usr/bin/env python3
"""桌面壳 Rust 源码按「产品 / 测试」拆开(预检读壳源码的单一口径;preflight/lib.sh 的 pf_shell_rs_prod / pf_shell_rs_tests 调它)。

   python3 rs_split.py prod  <文件…>   # 产品代码:测试项所在的行换成空行(行数与原文相同,按行号比先后的检查不受影响)
   python3 rs_split.py tests <文件…>   # 只要测试项本身(各文件的测试项首尾相接)
   python3 rs_split.py --self-test     # 判别力自证

「测试项」= 紧跟在「只在测试构建里编译」的 cfg 属性之后的那一项。cfg 谓词按逻辑判:`test`、`all(…)` 里有一项只在测试里成立、
`any(…)` 里每一项都只在测试里成立 —— 才算(`#[cfg(test)]` / `#[cfg(all(test, target_os = "macos"))]` 算;
`#[cfg(not(test))]` / `#[cfg(not(all(test, …)))]` / `#[cfg(any(test, feature = "x"))]` 不算,它们在产品构建里也会编译)。
项的种类:`mod 名 { … }` 整块、`mod 名;`(外置测试文件的声明)、`fn …(…) { … }`(含方法)、`impl … { … }`、`trait` / `struct` /
`enum` / `union`(花括号体、元组体或单元写法)、`macro_rules! 名 { … }`、`use …;`、`const` / `static` / `type …;`。
属性与它之间可以夹别的属性、文档注释。结构体字段 / 表达式 / 语句上的 cfg 不拆(只有一行,不会是锚的来处)。
文件名以 `tests.rs` 结尾的整份算测试(tests 输出整份收,prod 输出整份不收)。
读不了的文件 / 拆分出错 = 退出码非 0(预检据此判红,不许把空输出当「产品里一处都没有」放行)。

按 Rust 词法走:字符串(含 r"…" / r#"…"# / b"…")、字符字面量('{' / '\\'' / '\\u{…}')、生命周期('a)、
行注释与可嵌套的块注释里的花括号都不算。注释或字符串里写的 `#[cfg(test)]` 也不算。
"""
import re
import sys

CFG_ATTR = re.compile(r'#\s*\[\s*cfg\s*\(')


def _cfg_args(s):
    """把 cfg 谓词参数串按顶层逗号切开(括号与字符串里的逗号不切)。"""
    out, depth, cur, i, n = [], 0, '', 0, len(s)
    while i < n:
        c = s[i]
        if c == '"':
            j = i + 1
            while j < n and s[j] != '"':
                j += 2 if s[j] == '\\' else 1
            cur += s[i:j + 1]
            i = j + 1
            continue
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        if c == ',' and depth == 0:
            out.append(cur.strip())
            cur = ''
        else:
            cur += c
        i += 1
    if cur.strip():
        out.append(cur.strip())
    return out


def cfg_test_only(pred):
    """cfg 谓词是否「只在测试构建里成立」:test;all(…) 里有一项是;any(…) 里每一项都是。not(…) 一律不是(产品构建里也编译)。"""
    pred = pred.strip()
    if pred == 'test':
        return True
    m = re.match(r'^(all|any|not)\s*\((.*)\)$', pred, re.S)
    if not m:
        return False
    args = _cfg_args(m.group(2))
    if m.group(1) == 'all':
        return any(cfg_test_only(a) for a in args)
    if m.group(1) == 'any':
        return bool(args) and all(cfg_test_only(a) for a in args)
    return False


class _Lex:
    """在 text 上按 Rust 词法前进;skip_* 返回跳过之后的位置。"""

    def __init__(self, text):
        self.t = text
        self.n = len(text)

    def skip_trivia_or_literal(self, i):
        """i 处若是注释 / 字符串 / 字符字面量 / 生命周期,返回它之后的位置;否则返回 None。"""
        t, n = self.t, self.n
        c = t[i]
        if c == '/' and i + 1 < n and t[i + 1] == '/':
            j = t.find('\n', i)
            return n if j < 0 else j
        if c == '/' and i + 1 < n and t[i + 1] == '*':
            depth, j = 1, i + 2
            while j < n and depth:
                if t.startswith('/*', j):
                    depth += 1
                    j += 2
                elif t.startswith('*/', j):
                    depth -= 1
                    j += 2
                else:
                    j += 1
            return j
        # 原始串 r"…" / r#"…"# / br#"…"#(前一个字符不能是标识符字符,否则是 foo_r"… 之类,不存在于合法代码)
        m = re.match(r'b?r(#*)"', t[i:i + 300]) if c in 'br' and (i == 0 or not (t[i - 1].isalnum() or t[i - 1] == '_')) else None
        if m:
            close = '"' + m.group(1)
            j = t.find(close, i + m.end())
            return n if j < 0 else j + len(close)
        if c == '"' or (c == 'b' and i + 1 < n and t[i + 1] == '"' and (i == 0 or not (t[i - 1].isalnum() or t[i - 1] == '_'))):
            j = i + (2 if c == 'b' else 1)
            while j < n:
                if t[j] == '\\':
                    j += 2
                    continue
                if t[j] == '"':
                    return j + 1
                j += 1
            return n
        if c == "'":
            # 字符字面量:'\…' 或 'x'(x 后紧跟 ');否则是生命周期 / 标签,只跳过这个引号
            if i + 1 < n and t[i + 1] == '\\':
                j = i + 2
                while j < n and t[j] != "'":
                    j += 1
                return j + 1
            if i + 2 < n and t[i + 2] == "'":
                return i + 3
            return i + 1
        return None

    def match_close(self, i, open_ch, close_ch):
        """i 指向 open_ch;返回配对的 close_ch 之后的位置(到文件尾没配上 = 文件长度)。"""
        depth, j = 0, i
        while j < self.n:
            k = self.skip_trivia_or_literal(j)
            if k is not None:
                j = k
                continue
            ch = self.t[j]
            if ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return j + 1
            j += 1
        return self.n

    def item_end(self, i):
        """i 起是一项(可能先有属性 / 文档注释 / 空白);返回这一项结束的位置:mod / fn 到配对的 } 或 ;,其它返回 None(不拆)。"""
        t, n = self.t, self.n
        j = i
        while j < n:
            if t[j].isspace():
                j += 1
                continue
            k = self.skip_trivia_or_literal(j) if t[j] == '/' else None
            if k is not None:
                j = k
                continue
            if t[j] == '#':
                b = t.find('[', j)
                if b < 0:
                    return None
                j = self.match_close(b, '[', ']')
                continue
            break
        head = re.match(r'(?:pub(?:\s*\([^)]*\))?\s+)?(?:(?:const|async|unsafe|default|extern(?:\s+"[^"]*")?)\s+)*'
                        r'(mod|fn|impl|trait|struct|enum|union|macro_rules\s*!|use|const|static|type)(?![A-Za-z0-9_])', t[j:j + 200])
        if not head:
            return None
        kind = re.sub(r'\s+', '', head.group(1))
        k = j + head.end()
        if kind in ('use', 'const', 'static', 'type'):
            # 到顶层的 ; 为止(值 / 路径里的 {…} [..] (..) 都要配平:use a::{b, c}; / const X: S = S { a: 1 };)
            depth = 0
            while k < n:
                s = self.skip_trivia_or_literal(k)
                if s is not None:
                    k = s
                    continue
                ch = t[k]
                if ch in '([{':
                    depth += 1
                elif ch in ')]}':
                    depth -= 1
                elif depth == 0 and ch == ';':
                    return k + 1
                k += 1
            return n
        # 其余:找到这一项的 { 或 ;(签名里的括号 / 方括号里不会有顶层 ; 与 {;元组结构体 struct S(..); 到 ; 为止)
        paren = 0
        while k < n:
            s = self.skip_trivia_or_literal(k)
            if s is not None:
                k = s
                continue
            ch = t[k]
            if ch in '([':
                paren += 1
            elif ch in ')]':
                paren -= 1
                if paren == 0 and kind == 'macro_rules!' and ch == ')':
                    # macro_rules! m ( … ); 的写法:括号体之后到 ; 为止
                    e = t.find(';', k)
                    return n if e < 0 else e + 1
            elif paren == 0 and ch == ';':
                return k + 1
            elif paren == 0 and ch == '{':
                return self.match_close(k, '{', '}')
            k += 1
        return n


def split_text(text):
    """返回 (prod, tests):prod 与原文同行数(测试项的字符换成空白、换行保留);tests 为各测试项原文首尾相接。"""
    lx = _Lex(text)
    spans = []
    i, n = 0, len(text)
    while i < n:
        k = lx.skip_trivia_or_literal(i)
        if k is not None:
            i = k
            continue
        if text[i] == '#':
            m = CFG_ATTR.match(text, i)
            if m:
                b = text.find('[', i)
                close = lx.match_close(b, '[', ']')
                inner = text[b + 1:close - 1].strip()
                pm = re.match(r'^cfg\s*\((.*)\)$', inner, re.S)
                if pm and cfg_test_only(pm.group(1)):
                    end = lx.item_end(close)
                    if end is not None:
                        spans.append((i, end))
                        i = end
                        continue
        i += 1
    if not spans:
        return text, ''
    prod, tests, last = [], [], 0
    for a, b in spans:
        prod.append(text[last:a])
        prod.append(re.sub(r'[^\n]', '', text[a:b]))
        tests.append(text[a:b] + '\n')
        last = b
    prod.append(text[last:])
    return ''.join(prod), ''.join(tests)


def split_file(path):
    text = open(path, encoding='utf-8', errors='surrogateescape').read()
    if path.endswith('tests.rs'):
        return '', text
    return split_text(text)


def self_test():
    src = '''fn real() { let s = "#[cfg(test)] mod fake { 0o666 }"; let c = '{'; let q = '\\''; }
// #[cfg(test)] mod in_comment { }
/* nested /* #[cfg(test)] */ still comment */
struct S<'a> { r: &'a str,
    #[cfg(test)]
    skew: u64,
}
#[cfg(test)]
#[allow(dead_code)]
/// doc
mod tests {
    fn helper() { let raw = r#"}}}"#; let b = b"}"; let ch = '}'; let lt: &'static str = "x"; }
    #[test]
    fn fixture_0o666() { std::fs::Permissions::from_mode(0o666); }
}
#[cfg(test)]
mod outer_tests;
impl S<'_> {
    #[cfg(test)]
    fn only_in_tests(&self) -> u64 { 1 }
    #[cfg(not(test))]
    fn only_in_tests(&self) -> u64 { 2 }
}
fn after() { from_mode(0o600); }
'''
    prod, tests = split_text(src)
    checks = [
        (prod.count('\n') == src.count('\n'), 'prod 行数与原文相同'),
        ('fn real()' in prod and 'fn after()' in prod, '产品函数留在 prod'),
        ('fake { 0o666 }' in prod, '字符串里的 #[cfg(test)] 不算测试项'),
        ('mod in_comment' in prod, '注释里的 #[cfg(test)] 不算测试项'),
        ('skew: u64' in prod, '字段上的 #[cfg(test)] 不拆'),
        ('fixture_0o666' not in prod and 'fixture_0o666' in tests, '同文件测试模块整块进 tests(花括号在原始串 / 字节串 / 字符字面量里不乱配)'),
        ('mod outer_tests;' in tests and 'mod outer_tests;' not in prod, '外置测试文件声明进 tests'),
        ('{ 1 }' in tests and '{ 2 }' in prod, '方法上的 #[cfg(test)] 拆走、#[cfg(not(test))] 留下'),
        ('lt: &\'static' in tests, '生命周期不当字符字面量'),
    ]
    # cfg 谓词按逻辑判 + 项的种类不止 mod / fn
    src2 = '''#[cfg(all(test, target_os = "macos"))]
mod mac_tests { fn t_all() { let x = "ALL_TEST_MOD"; } }
#[cfg(test)]
impl S { fn t_impl() { let x = "IMPL_TEST"; } }
#[cfg(not(all(test, unix)))]
fn keep_not_all() { let x = "NOT_ALL_PROD"; }
#[cfg(any(test, feature = "x"))]
fn keep_any() { let x = "ANY_PROD"; }
#[cfg(any(test, all(test, unix)))]
fn drop_any_all() { let x = "ANY_ALL_TEST"; }
#[cfg(test)]
use crate::fixtures::{a, b};
fn after_use() { let x = "AFTER_USE_PROD"; }
#[cfg(test)]
const FIX: Cfg = Cfg { mode: 0o666, name: "CONST_TEST" };
#[cfg(test)]
static SEEN: AtomicU8 = AtomicU8::new(0); // STATIC_TEST
#[cfg(test)]
struct Probe { v: u8 } // STRUCT_TEST
#[cfg(test)]
struct Unit;
#[cfg(test)]
enum E { A, B } // ENUM_TEST
#[cfg(test)]
macro_rules! fixture { ($x:expr) => { $x }; } // MACRO_TEST
fn tail_prod() { let x = "TAIL_PROD"; }
'''
    prod2, tests2 = split_text(src2)
    checks += [
        ('ALL_TEST_MOD' in tests2 and 'ALL_TEST_MOD' not in prod2, 'cfg(all(test, …)) 的 mod 进 tests'),
        ('IMPL_TEST' in tests2 and 'IMPL_TEST' not in prod2, '#[cfg(test)] impl 整块进 tests'),
        ('NOT_ALL_PROD' in prod2 and 'NOT_ALL_PROD' not in tests2, 'cfg(not(all(test, …))) 留在产品'),
        ('ANY_PROD' in prod2, 'cfg(any(test, feature)) 产品构建里也编译,留在产品'),
        ('ANY_ALL_TEST' in tests2, 'cfg(any(test, all(test, …))) 每一支都只在测试里成立,进 tests'),
        ('crate::fixtures' in tests2 and 'AFTER_USE_PROD' in prod2, '#[cfg(test)] use a::{b, c}; 到顶层分号为止,后一项留在产品'),
        ('CONST_TEST' in tests2 and '0o666' not in prod2, '#[cfg(test)] const(值里有花括号)整项进 tests'),
        ('STATIC_TEST' in prod2 and 'AtomicU8::new' in tests2, '#[cfg(test)] static 进 tests(行尾注释在分号之后,留在原处)'),
        ('struct Probe' in tests2 and 'struct Unit;' in tests2, '#[cfg(test)] struct(花括号体 / 单元写法)进 tests'),
        ('enum E' in tests2, '#[cfg(test)] enum 进 tests'),
        ('$x:expr' in tests2 and 'TAIL_PROD' in prod2, '#[cfg(test)] macro_rules! 进 tests,后一项留在产品'),
        (prod2.count('\n') == src2.count('\n'), '扩展项种类后 prod 行数仍与原文相同'),
    ]
    # 读不了的文件 = 退非 0(不许静默跳过、输出空面)
    import io
    import contextlib
    with contextlib.redirect_stderr(io.StringIO()):
        rc = main(['prod', '/nonexistent/rs_split_selftest_missing.rs'])
    checks.append((rc != 0, '读不了的文件退非 0(预检据此判红)'))
    bad = [label for ok, label in checks if not ok]
    if bad:
        for label in bad:
            print('rs_split 自证失败:' + label)
        return 1
    print('rs_split 自证 %d 向全过' % len(checks))
    return 0


def main(argv):
    if argv[:1] == ['--self-test']:
        return self_test()
    if len(argv) < 1 or argv[0] not in ('prod', 'tests'):
        print(__doc__, file=sys.stderr)
        return 2
    out = sys.stdout
    for p in argv[1:]:
        # 读不了 / 拆不动 = 退非 0(调用方据此判红):静默跳过会让「产品里不许出现 X」的反锚读到空面、整类判绿
        try:
            prod, tests = split_file(p)
        except (OSError, UnicodeError) as e:
            print('rs_split: 读不了 %s(%s)' % (p, e), file=sys.stderr)
            return 3
        out.write(prod if argv[0] == 'prod' else tests)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
