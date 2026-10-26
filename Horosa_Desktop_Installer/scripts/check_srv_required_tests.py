#!/usr/bin/env python3
"""「需本机 :8899 排盘服务」的 pytest 金标:登记一致性 + 实跑不许被 skip。

病理:这类金标在服务不在线时整模块 skip,pytest 仍退 0;闸门只看退出码就记绿(假绿)。
清单不手写:凡测试文件 `from srv_gate import …`(单源判据 tests/srv_gate.py)即为「需服务」。

子命令:
  list  --tests DIR              列出需服务的测试文件(每行一个文件名)。
  lint  --tests DIR              登记一致性:
          ① 测试里出现 :8899 的地址(去掉文档串 / 注释后)却不经 srv_gate → 红(新加需服务的测试漏登记);
          ② 经 srv_gate 却没写 `pytestmark = require_srv_mark()` → 红(判据没接上);
          ③ 除 srv_gate.py 外有文件自己读 HOROSA_REQUIRE_SRV → 红(判据分叉)。
  junit --tests DIR --xml FILE   读 pytest --junitxml 的结果:每个需服务文件必须有用例、且 skipped = 0,否则红。
  --self-test                    判别向量自证。
退出码:0 通过 · 1 不通过 · 2 用法错 / 读不到。
"""
import argparse
import ast
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET

GATE_MODULE = "srv_gate"
URL_RE = re.compile(r"(?:127\.0\.0\.1|localhost|\[::1\]):8899\b")
ENV_RE = re.compile(r"HOROSA_REQUIRE_SRV")


def _docstring_nodes(tree):
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", None) or []
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                out.add(id(body[0].value))
    return out


def _code_strings(tree):
    docs = _docstring_nodes(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs:
            yield node.value


def _uses_gate(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == GATE_MODULE:
            return True
        if isinstance(node, ast.Import) and any(a.name == GATE_MODULE for a in node.names):
            return True
    return False


def _has_pytestmark(tree):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "pytestmark" for t in node.targets):
            v = node.value
            if isinstance(v, ast.Call) and getattr(v.func, "id", getattr(v.func, "attr", "")) == "require_srv_mark":
                return True
    return False


def _reads_env(tree):
    for s in _code_strings(tree):
        if ENV_RE.search(s):
            return True
    return False


def _test_files(tests_dir):
    for name in sorted(os.listdir(tests_dir)):
        if name.endswith(".py"):
            yield name, os.path.join(tests_dir, name)


def _parse(path):
    with open(path, encoding="utf-8") as fh:
        return ast.parse(fh.read(), filename=path)


def required(tests_dir):
    out = []
    for name, path in _test_files(tests_dir):
        if name.startswith("test_") and _uses_gate(_parse(path)):
            out.append(name)
    return out


def lint(tests_dir):
    problems = []
    for name, path in _test_files(tests_dir):
        if name == GATE_MODULE + ".py":
            continue
        try:
            tree = _parse(path)
        except SyntaxError as exc:
            problems.append("%s: 解析失败 %s" % (name, exc))
            continue
        gate = _uses_gate(tree)
        if any(URL_RE.search(s) for s in _code_strings(tree)) and not gate:
            problems.append("%s: 打 :8899 却不经 %s(新加的需服务测试要用单源判据)" % (name, GATE_MODULE))
        if gate and name.startswith("test_") and not _has_pytestmark(tree):
            problems.append("%s: 经 %s 但没写 pytestmark = require_srv_mark()" % (name, GATE_MODULE))
        if _reads_env(tree):
            problems.append("%s: 自己读 HOROSA_REQUIRE_SRV(判据只许在 %s.py)" % (name, GATE_MODULE))
    return problems


def junit(tests_dir, xml_path):
    names = required(tests_dir)
    if not names:
        return ["测试目录里没有任何需服务的测试(清单为空,判不了)"], {}
    try:
        root = ET.parse(xml_path).getroot()
    except (OSError, ET.ParseError) as exc:
        return ["读不到 junit 结果 %s:%s" % (xml_path, exc)], {}
    stats = {n[:-3]: [0, 0] for n in names}
    for case in root.iter("testcase"):
        cls = case.get("classname") or ""
        f = case.get("file") or ""
        mod = os.path.splitext(os.path.basename(f))[0] if f else cls.split(".")[-1]
        if mod not in stats:
            # classname 可能是 tests.test_x 或 test_x.TestCls
            parts = cls.split(".")
            hit = [p for p in parts if p in stats]
            if not hit:
                continue
            mod = hit[0]
        stats[mod][0] += 1
        if case.find("skipped") is not None:
            stats[mod][1] += 1
    problems = []
    for mod, (n, sk) in sorted(stats.items()):
        if n == 0:
            problems.append("%s.py: 一个用例都没跑到(收集失败或被整模块排除)" % mod)
        elif sk:
            problems.append("%s.py: %d/%d 例被 skip(需服务的金标在基线里必须真跑)" % (mod, sk, n))
    return problems, stats


def _self_test():
    fails = []
    with tempfile.TemporaryDirectory() as d:
        def w(name, body):
            with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
                fh.write(body)
        w("srv_gate.py", 'import os\nREQ = os.environ.get("HOROSA_REQUIRE_SRV")\nBASE="http://127.0.0.1:8899"\n')
        w("test_good.py", '"""需 127.0.0.1:8899。HOROSA_REQUIRE_SRV"""\nfrom srv_gate import post, require_srv_mark\npytestmark = require_srv_mark()\ndef test_a(): pass\n')
        w("test_doc_only.py", '"""不起 :8899,只在文档里提 127.0.0.1:8899"""\n# http://127.0.0.1:8899\ndef test_b(): pass\n')
        if lint(d):
            fails.append("干净目录被 lint 判红:%s" % lint(d))
        if required(d) != ["test_good.py"]:
            fails.append("需服务清单不对:%s" % required(d))
        w("test_raw.py", 'BASE = "http://127.0.0.1:8899"\ndef test_c(): pass\n')
        if not any("test_raw.py" in p for p in lint(d)):
            fails.append("裸打 :8899 未登记没被抓")
        os.remove(os.path.join(d, "test_raw.py"))
        w("test_nomark.py", 'from srv_gate import post\ndef test_d(): pass\n')
        if not any("test_nomark.py" in p for p in lint(d)):
            fails.append("经 srv_gate 却缺 pytestmark 没被抓")
        os.remove(os.path.join(d, "test_nomark.py"))
        w("test_env.py", 'import os\nX = os.environ.get("HOROSA_REQUIRE_SRV")\ndef test_e(): pass\n')
        if not any("test_env.py" in p for p in lint(d)):
            fails.append("自读 HOROSA_REQUIRE_SRV 没被抓")
        os.remove(os.path.join(d, "test_env.py"))

        def xml(cases):
            p = os.path.join(d, "r.xml")
            body = "".join('<testcase classname="tests.%s" name="t%d">%s</testcase>' % (m, i, "<skipped/>" if sk else "")
                           for i, (m, sk) in enumerate(cases))
            with open(p, "w") as fh:
                fh.write('<testsuites><testsuite>%s</testsuite></testsuites>' % body)
            return p
        if junit(d, xml([("test_good", False), ("test_good", False), ("test_doc_only", True)]))[0]:
            fails.append("全真跑被判红")
        if not junit(d, xml([("test_good", True), ("test_good", False)]))[0]:
            fails.append("需服务文件有 skip 没被抓")
        if not junit(d, xml([("test_doc_only", False)]))[0]:
            fails.append("需服务文件零用例没被抓")
        if not junit(d, os.path.join(d, "missing.xml"))[0]:
            fails.append("读不到 junit 没判红")
    for f in fails:
        print("✗ " + f)
    print("self-test %s" % ("通过" if not fails else "失败"))
    return 0 if not fails else 1


def main(argv):
    if argv[:1] == ["--self-test"]:
        return _self_test()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "lint", "junit"])
    ap.add_argument("--tests", required=True)
    ap.add_argument("--xml")
    a = ap.parse_args(argv)
    if not os.path.isdir(a.tests):
        print("测试目录不存在:%s" % a.tests)
        return 2
    if a.cmd == "list":
        print("\n".join(required(a.tests)))
        return 0
    if a.cmd == "lint":
        probs = lint(a.tests)
        for p in probs:
            print(p)
        if not probs:
            print("需服务测试登记一致(%d 份:%s)" % (len(required(a.tests)), " ".join(required(a.tests))))
        return 1 if probs else 0
    if not a.xml:
        print("junit 需要 --xml")
        return 2
    probs, stats = junit(a.tests, a.xml)
    for p in probs:
        print(p)
    if not probs:
        print("需服务金标全部真跑:" + " ".join("%s=%d" % (k, v[0]) for k, v in sorted(stats.items())))
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
