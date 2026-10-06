#!/usr/bin/env python3
"""本机发版基线戳(替代已删除的 GitHub CI 门)。

CI 工作流 2026-05-31 已随「精简仓库附属目录」删除,preflight 原 [6]「CI 对 HEAD 成功」只剩「没有运行记录 → 告警」
的空门。发版基线(SOP):前端 jest 全量 / Python pytest / Java mvn 四模块(含四柱全年份域矩阵)/ cargo fmt --check + cargo test
—— 由 `run_release_baseline.sh` 在本机跑完后经本模块落戳 `build/release-baseline.json`(gitignored),preflight [6] 认戳:
  · 戳记的 HEAD == 当前 HEAD,或戳 HEAD 是当前 HEAD 的祖先且两者之间只改了非源码路径(docs / *.md / .claude / CITATION / README)→ 有效;
  · 五个必跑套件都在且 rc 全 0 → 过;任一套件真红 → 永远红;
  · 没有戳 / 戳过期(源码已变)/ 缺套件 → 日常只告警(不拦日常 preflight),`--require`(发布脚本设 HOROSA_REQUIRE_BASELINE=1)时 → 红。
用法:
  release_baseline_stamp.py write --repo <仓根> --suite <名> --rc <n> --summary <文> [--log <路径>]
  release_baseline_stamp.py check --repo <仓根> [--require]       退出码 0 过 / 2 无戳(告警) / 1 红
  release_baseline_stamp.py --self-test
"""
import argparse, datetime, json, os, pathlib, re, subprocess, sys, tempfile

STAMP_REL = "Horosa_Desktop_Installer/build/release-baseline.json"
REQUIRED = ("cargo_fmt", "cargo_test", "pytest", "mvn", "jest_full")
# 与源码无关的路径:这些路径之间的提交不作废戳(文档 / 元文档 / 引用信息 / 日志)
NON_SOURCE = (re.compile(r"^docs/"), re.compile(r"\.md$"), re.compile(r"^\.claude/"), re.compile(r"^CITATION\.cff$"),
              re.compile(r"^README"), re.compile(r"^UPGRADE_LOG"))


def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def head_of(repo):
    return _git(repo, "rev-parse", "HEAD")[1]


def dirty_count(repo):
    out = _git(repo, "status", "--porcelain")[1]
    return sum(1 for l in out.splitlines() if l.strip() and "SELFCHECK_LOG.md" not in l)


def stamp_path(repo):
    return pathlib.Path(repo) / STAMP_REL


def load(repo):
    p = stamp_path(repo)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return None


def write(repo, suite, rc, summary, log=""):
    repo = pathlib.Path(repo).resolve()
    head = head_of(repo)
    st = load(repo)
    if not st or st.get("head") != head:
        st = {"schema": 1, "head": head, "head_short": head[:8], "created_at": _now(), "suites": {}}
    st["dirty"] = dirty_count(repo)
    st["updated_at"] = _now()
    st["suites"][suite] = {"rc": int(rc), "summary": (summary or "").strip()[:400], "at": _now(), "log": log or ""}
    p = stamp_path(repo); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp"); tmp.write_text(json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"); tmp.replace(p)
    return st


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def is_non_source(path):
    return any(rx.search(path) for rx in NON_SOURCE)


def evaluate(st, head, changed_paths, is_ancestor, require):
    """纯逻辑(可自证):回 (退出码, 一行文案)。changed_paths = 戳 HEAD..当前 HEAD 改动路径(戳 HEAD 不是祖先时无意义)。
    口径:无戳 / 戳过期 / 套件不全 → 日常只告警(2),发布(require)才红(1);套件真红 → 永远红(那是实打实的回归信号)。"""
    soft = 1 if require else 2
    if st is None:
        return soft, "没有本机发版基线戳(build/release-baseline.json):发版前跑 scripts/run_release_baseline.sh 落戳"
    if st.get("head") != head:
        if not is_ancestor:
            return soft, f"基线戳记的是别的提交 {str(st.get('head',''))[:8]}(不是当前 HEAD 的祖先):发版前重跑 run_release_baseline.sh"
        src = [p for p in changed_paths if not is_non_source(p)]
        if src:
            return soft, f"基线戳 {str(st.get('head',''))[:8]} 之后源码又改了 {len(src)} 处(如 {src[0]}):发版前重跑 run_release_baseline.sh"
    red = [s for s in REQUIRED if s in st.get("suites", {}) and int(st["suites"][s].get("rc", 1)) != 0]
    if red:
        return 1, "基线套件有红:" + "; ".join(f"{s} rc={st['suites'][s].get('rc')} {st['suites'][s].get('summary','')[:80]}" for s in red)
    missing = [s for s in REQUIRED if s not in st.get("suites", {})]
    if missing:
        return soft, f"基线戳缺套件 {', '.join(missing)}(run_release_baseline.sh --only {','.join(missing)})"
    drift = "" if st.get("head") == head else f"(戳 {str(st.get('head'))[:8]} 之后只改了非源码路径,仍有效)"
    return 0, f"本机发版基线对 HEAD {head[:8]} 全绿{drift}:" + " · ".join(f"{s} {st['suites'][s].get('summary','ok')[:60]}" for s in REQUIRED)


def check(repo, require):
    repo = pathlib.Path(repo).resolve()
    st = load(repo); head = head_of(repo)
    changed, anc = [], False
    if st and st.get("head") and st.get("head") != head:
        anc = _git(repo, "merge-base", "--is-ancestor", st["head"], head)[0] == 0
        if anc:
            changed = [l for l in _git(repo, "diff", "--name-only", st["head"], head)[1].splitlines() if l.strip()]
    return evaluate(st, head, changed, anc, require)


def self_test():
    ok = {s: {"rc": 0, "summary": "ok"} for s in REQUIRED}
    st = {"schema": 1, "head": "a" * 40, "suites": dict(ok)}
    assert evaluate(None, "a" * 40, [], False, False)[0] == 2, "无戳 → 告警(2)"
    assert evaluate(None, "a" * 40, [], False, True)[0] == 1, "无戳 + require → 红"
    assert evaluate(st, "a" * 40, [], False, True)[0] == 0, "同 HEAD 全绿 → 过"
    assert evaluate(st, "b" * 40, ["docs/x.md", "UPGRADE_LOG.md", ".claude/META_GUIDE.md"], True, True)[0] == 0, "祖先 + 只改非源码 → 仍有效"
    assert evaluate(st, "b" * 40, ["docs/x.md", "Horosa-Web/astropy/websrv/webchartsrv.py"], True, False)[0] == 2, "祖先 + 源码变 → 日常告警"
    assert evaluate(st, "b" * 40, ["Horosa-Web/astropy/websrv/webchartsrv.py"], True, True)[0] == 1, "祖先 + 源码变 + require → 红"
    assert evaluate(st, "b" * 40, [], False, False)[0] == 2 and evaluate(st, "b" * 40, [], False, True)[0] == 1, "非祖先 → 日常告警 / 发布红"
    partial = {"schema": 1, "head": "a" * 40, "suites": {k: v for k, v in ok.items() if k != "mvn"}}
    assert evaluate(partial, "a" * 40, [], False, False)[0] == 2 and "mvn" in evaluate(partial, "a" * 40, [], False, False)[1], "缺套件 → 日常告警并点名"
    assert evaluate(partial, "a" * 40, [], False, True)[0] == 1, "缺套件 + require → 红"
    red = {"schema": 1, "head": "a" * 40, "suites": dict(ok, pytest={"rc": 1, "summary": "3 failed"})}
    assert evaluate(red, "a" * 40, [], False, False)[0] == 1 and "pytest" in evaluate(red, "a" * 40, [], False, False)[1], "套件红 → 日常也红并点名"
    # 真 git:write → check 同 HEAD 过;加一条文档提交 → 仍过;加一条源码提交 → 发布红 / 日常告警
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        subprocess.run(["git", "init", "-q", str(d)], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "base"], check=True)
        for s in REQUIRED:
            write(d, s, 0, f"{s} ok")
        assert check(d, True)[0] == 0, "真仓同 HEAD → 过"
        (d / "docs").mkdir(); (d / "docs" / "n.md").write_text("x")
        subprocess.run(["git", "-C", str(d), "add", "docs/n.md"], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "docs"], check=True)
        assert check(d, True)[0] == 0, "真仓文档提交后 → 仍过"
        (d / "src.py").write_text("x"); subprocess.run(["git", "-C", str(d), "add", "src.py"], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "src"], check=True)
        assert check(d, True)[0] == 1 and check(d, False)[0] == 2, "真仓源码提交后 → 发布红 / 日常告警"
        write(d, "pytest", 0, "again")   # 新 HEAD 上写戳 = 重开(旧套件作废)
        assert "缺套件" in check(d, False)[1], "新 HEAD 重开戳只含刚写的套件"
    print("release-baseline-stamp self-test OK(逻辑 10 向 + 真仓 4 向)")
    return 0


def main(argv):
    if argv and argv[0] == "--self-test":
        return self_test()
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write"); w.add_argument("--repo", required=True); w.add_argument("--suite", required=True, choices=REQUIRED); w.add_argument("--rc", required=True, type=int); w.add_argument("--summary", default=""); w.add_argument("--log", default="")
    c = sub.add_parser("check"); c.add_argument("--repo", required=True); c.add_argument("--require", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "write":
        st = write(a.repo, a.suite, a.rc, a.summary, a.log)
        print(f"[baseline-stamp] {a.suite} rc={a.rc} → {stamp_path(a.repo)}(HEAD {st['head_short']},已记 {len(st['suites'])}/{len(REQUIRED)} 套件)")
        return 0
    code, msg = check(a.repo, a.require)
    print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
