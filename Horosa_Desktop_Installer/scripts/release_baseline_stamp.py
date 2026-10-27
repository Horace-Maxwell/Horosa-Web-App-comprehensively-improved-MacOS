#!/usr/bin/env python3
"""本机发版基线戳(替代已删除的 GitHub CI 门)。

CI 工作流 2026-05-31 已随「精简仓库附属目录」删除,preflight 原 [6]「CI 对 HEAD 成功」只剩「没有运行记录 → 告警」
的空门。发版基线(SOP):前端 jest 全量 / Python pytest / Java mvn 四模块(含四柱全年份域矩阵)/ cargo fmt --check + cargo test
—— 由 `run_release_baseline.sh` 在本机跑完后经本模块落戳 `build/release-baseline.json`(gitignored),preflight [6] 认戳:
  · 戳记的 HEAD == 当前 HEAD,或两个提交的树之间只差非源码路径(docs / *.md / .claude / CITATION / README)→ 有效;
    直接比两棵树、不要求戳 HEAD 是祖先 —— 改写提交(amend / 压单条)后源码没变,戳照样作数;戳记的提交在本仓找不到 → 按过期算;
    但「非源码」路径只要被测试读到(测试代码里出现它的文件名或所在目录)就按源码算 —— 例如 jest 合同测试会读
    docs/ 下的说明文档、scripts/ 下的脚本与用例数据,改它们可能让套件变红;
  · 套件跑在未提交改动上(写戳时工作区不干净,不计 SELFCHECK_LOG.md)→ 发布时红(证明的不是这个提交);
  · 五个必跑套件都在且 rc 全 0 → 过;任一套件真红 → 永远红;
  · 没有戳 / 戳过期(源码已变)/ 缺套件 → 日常只告警(不拦日常 preflight),`--require`(发布脚本设 HOROSA_REQUIRE_BASELINE=1)时 → 红。
用法:
  release_baseline_stamp.py write --repo <仓根> --suite <名> --rc <n> --summary <文> [--log <路径>]
  release_baseline_stamp.py check --repo <仓根> [--require]       退出码 0 过 / 2 无戳(告警) / 1 红
  release_baseline_stamp.py engine-fresh --repo <仓根> --pid <:8899 的进程号>
      四柱矩阵经 :8899 打 Python 引擎:服务若在引擎源码(astropy / flatlib-ctrad2 / vendor)最近一次改动之前启动,
      进程里加载的是旧引擎,跑出来的绿证明不了当前代码 → 退出码 75(跳过,提示重启服务);新于最近改动 → 0
  release_baseline_stamp.py --self-test
"""
import argparse, datetime, json, os, pathlib, re, subprocess, sys, tempfile

STAMP_REL = "Horosa_Desktop_Installer/build/release-baseline.json"
REQUIRED = ("cargo_fmt", "cargo_test", "pytest", "mvn", "jest_full")
# 与五个套件无关的路径:这些路径之间的提交不作废戳(文档 / 说明文件 / 引用信息 / 日志 / 发布工具与发布说明 —— 发布脚本有自己的
# 自证与哨兵,不在 jest / pytest / mvn / cargo 的覆盖面里)
NON_SOURCE = (re.compile(r"^docs/"), re.compile(r"\.md$"), re.compile(r"^\.claude/"), re.compile(r"^CITATION\.cff$"),
              re.compile(r"^README"), re.compile(r"^UPGRADE_LOG"),
              re.compile(r"^Horosa_Desktop_Installer/scripts/"), re.compile(r"^Horosa_Desktop_Installer/config/release_notes/"))


def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def head_of(repo):
    return _git(repo, "rev-parse", "HEAD")[1]


def changed_between(repo, a, b):
    """提交 a 与 b 两棵树之间的改动路径:不转义中文(core.quotepath=false)、不合并改名(改名 = 删旧 + 加新,两边都算)、NUL 分隔。
    任一提交在本仓找不到(或 diff 失败)→ None(不能当「没改动」)。"""
    for c in (a, b):
        if _git(repo, "cat-file", "-e", f"{c}^{{commit}}")[0] != 0:
            return None
    r = subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=false", "diff", "--name-only", "--no-renames", "-z", a, b],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return [x for x in r.stdout.split("\0") if x.strip()]


# 测试代码所在(jest / 无头 node --test / pytest / Java 单测 / Rust 单测):非源码路径被这里的文本点名 = 测试会读它 = 算源码
TEST_ROOTS = ("Horosa-Web/astrostudyui/src", "Horosa-Web/astrostudyui/headless/test", "Horosa-Web/astrostudyui/jest.config.js",
              "Horosa-Web/astropy/tests", "Horosa-Web/astrostudysrv", "Horosa_Desktop_Installer/src-tauri/src")
TEST_FILE_RX = re.compile(r"(__tests__/|/src/test/|\.test\.[jt]sx?$|/tests/.*\.py$|/src/test/.*\.java$|\.rs$|jest\.config\.js$|headless/test/)")


def _test_corpus(repo):
    repo = pathlib.Path(repo)
    texts = []
    for root in TEST_ROOTS:
        base = repo / root
        files = [base] if base.is_file() else (base.rglob("*") if base.is_dir() else [])
        for f in files:
            rel = str(f.relative_to(repo))
            if not f.is_file() or "node_modules" in rel or "/target/" in rel or not TEST_FILE_RX.search(rel):
                continue
            try:
                texts.append(f.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    return "\n".join(texts)


def read_by_tests(path, corpus):
    """测试文本里出现该路径的文件名(或「目录/文件名」),或把它所在目录(末两级)当整目录读(目录名后紧跟引号)→ 视为被测试读到。"""
    if not corpus:
        return False
    parts = path.split("/")
    if len(parts[-1]) >= 6 and parts[-1] in corpus:
        return True
    if len(parts) >= 2:
        d = "/".join(parts[-3:-1]) if len(parts) >= 3 else parts[-2]
        if len(d) >= 6 and re.search(re.escape(d) + r"/?['\"`]", corpus):
            return True
    return False


def blocking_paths(repo, changed, corpus=None):
    """改动里会作废戳的路径:源码,或被测试读到的「非源码」。"""
    corpus = _test_corpus(repo) if corpus is None else corpus
    return [p for p in changed if not is_non_source(p) or read_by_tests(p, corpus)]


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


def write(repo, suite, rc, summary, log="", started_head=""):
    repo = pathlib.Path(repo).resolve()
    head = head_of(repo)
    if started_head and started_head != head:
        # 套件开跑后 HEAD 变了:结果证明的是开跑时那个提交,不能记到现在这个 HEAD 名下
        raise SystemExit(f"[baseline-stamp] {suite}:开跑时 HEAD {started_head[:8]},现在 {head[:8]} —— 跑的途中有新提交,本套件不落戳(重跑)")
    st = load(repo)
    if st and st.get("head") and st.get("head") != head:
        # 戳 HEAD 与当前 HEAD 的树之间只差非源码路径(且没被测试读到)→ 已记套件仍有效,把戳挪到当前 HEAD
        changed = changed_between(repo, st["head"], head)
        if changed is not None and not blocking_paths(repo, changed):
            st["carried_from"] = st.get("head_short"); st["head"] = head; st["head_short"] = head[:8]
        else:
            st = None
    if not st:
        st = {"schema": 1, "head": head, "head_short": head[:8], "created_at": _now(), "suites": {}}
    dirty = dirty_count(repo)
    st["dirty"] = dirty
    st["updated_at"] = _now()
    st["suites"][suite] = {"rc": int(rc), "summary": (summary or "").strip()[:400], "at": _now(), "log": log or "", "dirty": dirty}
    p = stamp_path(repo); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp"); tmp.write_text(json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"); tmp.replace(p)
    return st


# 四柱全年份域矩阵(mvn)经 :8899 调 Python:这几个目录里的改动要重启服务才生效
ENGINE_DIRS = ("Horosa-Web/astropy", "Horosa-Web/flatlib-ctrad2", "Horosa-Web/vendor")
# 测试、缓存、说明文件的改动不影响在跑的引擎
ENGINE_SKIP_RX = re.compile(r"(^|/)(tests?|__pycache__|\.pytest_cache)/|\.pyc$|\.md$")


def engine_latest_change(repo):
    """引擎源码最近一次改动的时刻(epoch 秒)与路径。
    工作区里被跟踪或未被忽略的文件取 mtime 最大者(运行期生成、被忽略的文件不算);已提交的删除取那次提交的时间。"""
    repo = pathlib.Path(repo)
    r = subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=false", "ls-files", "-z", "-co", "--exclude-standard", "--"]
                       + list(ENGINE_DIRS), capture_output=True, text=True)
    latest, where = 0.0, ""
    for rel in r.stdout.split("\0"):
        if not rel or ENGINE_SKIP_RX.search(rel):
            continue
        try:
            m = (repo / rel).stat().st_mtime
        except OSError:
            continue
        if m > latest:
            latest, where = m, rel
    rc, out = _git(repo, "log", "-1", "--diff-filter=D", "--format=%ct", "--", *ENGINE_DIRS)
    if rc == 0 and out.strip().isdigit() and int(out.strip()) > latest:
        latest, where = float(out.strip()), "(已提交的删除)"
    return latest, where


def service_start_epoch(pid):
    """进程启动时刻(epoch 秒,秒级);取不到回 None。"""
    r = subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)], capture_output=True, text=True,
                       env=dict(os.environ, LC_ALL="C", LANG="C"))
    s = r.stdout.strip()
    if r.returncode != 0 or not s:
        return None
    try:
        return datetime.datetime.strptime(s, "%a %b %d %H:%M:%S %Y").timestamp()
    except ValueError:
        return None


def engine_service_fresh(service_start, latest_change):
    """服务启动不早于引擎源码最近一次改动(秒级比较)→ True。"""
    if service_start is None:
        return False
    return int(latest_change) <= int(service_start)


def engine_fresh(repo, pid):
    """→ (退出码, 一行文案):0 服务新于引擎最近改动;75 服务更旧或取不到启动时刻。"""
    start = service_start_epoch(pid)
    latest, where = engine_latest_change(repo)
    if start is None:
        return 75, f":8899 服务(pid {pid})取不到启动时刻,无法确认它加载的是当前引擎:重启排盘服务后再跑"
    if engine_service_fresh(start, latest):
        return 0, f":8899 服务(pid {pid})启动于引擎最近一次改动之后"
    fmt = lambda e: datetime.datetime.fromtimestamp(e).strftime("%Y-%m-%d %H:%M:%S")
    return 75, (f":8899 服务(pid {pid})启动于 {fmt(start)},早于引擎源码最近一次改动 {fmt(latest)}({where}):"
                f"进程里还是旧引擎,重启排盘服务后再跑 mvn")


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def is_non_source(path):
    return any(rx.search(path) for rx in NON_SOURCE)


def evaluate(st, head, changed_paths, require, corpus=""):
    """纯逻辑(可自证):回 (退出码, 一行文案)。changed_paths = 戳 HEAD 与当前 HEAD 两棵树之间的改动路径
    (None = 戳记的提交在本仓找不到);corpus = 测试文本(非源码路径被它点名即按源码算)。
    口径:无戳 / 戳过期 / 套件不全 / 套件跑在未提交改动上 → 日常只告警(2),发布(require)才红(1);套件真红 → 永远红。"""
    soft = 1 if require else 2
    if st is None:
        return soft, "没有本机发版基线戳(build/release-baseline.json):发版前跑 scripts/run_release_baseline.sh 落戳"
    if st.get("head") != head:
        if changed_paths is None:
            return soft, f"基线戳记的提交 {str(st.get('head',''))[:8]} 在本仓找不到:发版前重跑 run_release_baseline.sh"
        src = [p for p in changed_paths if not is_non_source(p) or read_by_tests(p, corpus)]
        if src:
            return soft, f"基线戳 {str(st.get('head',''))[:8]} 之后源码(或测试会读的文件)又改了 {len(src)} 处(如 {src[0]}):发版前重跑 run_release_baseline.sh"
    dirty = [s for s in REQUIRED if int((st.get("suites", {}).get(s) or {}).get("dirty", 0) or 0) > 0]
    if dirty:
        return soft, f"基线套件 {', '.join(dirty)} 是在未提交改动上跑的(证明的不是这个提交):提交后重跑 run_release_baseline.sh --only {','.join(dirty)}"
    red = [s for s in REQUIRED if s in st.get("suites", {}) and int(st["suites"][s].get("rc", 1)) != 0]
    if red:
        return 1, "基线套件有红:" + "; ".join(f"{s} rc={st['suites'][s].get('rc')} {st['suites'][s].get('summary','')[:80]}" for s in red)
    missing = [s for s in REQUIRED if s not in st.get("suites", {})]
    if missing:
        return soft, f"基线戳缺套件 {', '.join(missing)}(run_release_baseline.sh --only {','.join(missing)})"
    drift = "" if st.get("head") == head else f"(戳 {str(st.get('head'))[:8]} 与当前 HEAD 只差非源码路径,仍有效)"
    return 0, f"本机发版基线对 HEAD {head[:8]} 全绿{drift}:" + " · ".join(f"{s} {st['suites'][s].get('summary','ok')[:60]}" for s in REQUIRED)


def check(repo, require):
    repo = pathlib.Path(repo).resolve()
    st = load(repo); head = head_of(repo)
    changed, corpus = [], ""
    if st and st.get("head") and st.get("head") != head:
        changed = changed_between(repo, st["head"], head)
        if changed:
            corpus = _test_corpus(repo)
    return evaluate(st, head, changed, require, corpus)


def self_test():
    if not __debug__:
        print("release-baseline-stamp self-test:断言被 -O / PYTHONOPTIMIZE 关掉了,自证不作数", file=sys.stderr)
        return 1
    ok = {s: {"rc": 0, "summary": "ok"} for s in REQUIRED}
    st = {"schema": 1, "head": "a" * 40, "suites": dict(ok)}
    assert evaluate(None, "a" * 40, [], False)[0] == 2, "无戳 → 告警(2)"
    assert evaluate(None, "a" * 40, [], True)[0] == 1, "无戳 + require → 红"
    assert evaluate(st, "a" * 40, [], True)[0] == 0, "同 HEAD 全绿 → 过"
    assert evaluate(st, "b" * 40, ["docs/x.md", "UPGRADE_LOG.md", ".claude/META_GUIDE.md"], True)[0] == 0, "两树只差非源码 → 仍有效"
    assert evaluate(st, "b" * 40, ["docs/x.md", "Horosa-Web/astropy/websrv/webchartsrv.py"], False)[0] == 2, "两树差源码 → 日常告警"
    assert evaluate(st, "b" * 40, ["Horosa-Web/astropy/websrv/webchartsrv.py"], True)[0] == 1, "两树差源码 + require → 红"
    assert evaluate(st, "b" * 40, None, False)[0] == 2 and evaluate(st, "b" * 40, None, True)[0] == 1, "戳记的提交找不到 → 日常告警 / 发布红"
    partial = {"schema": 1, "head": "a" * 40, "suites": {k: v for k, v in ok.items() if k != "mvn"}}
    assert evaluate(partial, "a" * 40, [], False)[0] == 2 and "mvn" in evaluate(partial, "a" * 40, [], False)[1], "缺套件 → 日常告警并点名"
    assert evaluate(partial, "a" * 40, [], True)[0] == 1, "缺套件 + require → 红"
    corpus = "const doc = fs.readFileSync('docs/AI_AGENT_RUNTIME.md'); fs.readdirSync('scripts/fixtures/cases'); readJson('fixtures/x/ab.json')"
    assert evaluate(st, "b" * 40, ["docs/AI_AGENT_RUNTIME.md"], True, corpus)[0] == 1, "测试会读的文档改了 → 按源码算"
    assert evaluate(st, "b" * 40, ["Horosa_Desktop_Installer/scripts/fixtures/cases/new_case.json"], True, corpus)[0] == 1, "测试读整个目录 → 目录下改动按源码算"
    assert evaluate(st, "b" * 40, ["docs/archive/某次记录.md"], True, corpus)[0] == 0, "测试不读的文档 → 仍有效"
    assert evaluate(st, "b" * 40, ["Horosa_Desktop_Installer/scripts/fixtures/driver.py"], True, corpus)[0] == 0, "同级目录被读不等于本目录被读"
    dirty_st = {"schema": 1, "head": "a" * 40, "suites": dict(ok, jest_full={"rc": 0, "summary": "ok", "dirty": 3})}
    assert evaluate(dirty_st, "a" * 40, [], True)[0] == 1 and "jest_full" in evaluate(dirty_st, "a" * 40, [], True)[1], "套件跑在未提交改动上 → 发布红并点名"
    assert evaluate(dirty_st, "a" * 40, [], False)[0] == 2, "套件跑在未提交改动上 → 日常告警"
    red = {"schema": 1, "head": "a" * 40, "suites": dict(ok, pytest={"rc": 1, "summary": "3 failed"})}
    assert evaluate(red, "a" * 40, [], False)[0] == 1 and "pytest" in evaluate(red, "a" * 40, [], False)[1], "套件红 → 日常也红并点名"
    # 引擎新鲜度(:8899 服务启动时刻 vs 引擎源码最近改动)
    assert engine_service_fresh(100.0, 90.0) and engine_service_fresh(100.0, 100.4), "服务新于 / 同秒于最近改动 → 新鲜"
    assert not engine_service_fresh(100.0, 101.0), "最近改动晚于服务启动 → 旧引擎"
    assert not engine_service_fresh(None, 0.0), "取不到启动时刻 → 不认"
    me = service_start_epoch(os.getpid())
    assert me is not None and abs(me - datetime.datetime.now().timestamp()) < 600, "本进程启动时刻应可取且在近期"
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        subprocess.run(["git", "init", "-q", str(d)], check=True)
        eng = d / "Horosa-Web" / "astropy"; (eng / "tests").mkdir(parents=True)
        (d / ".gitignore").write_text("*.log\n")
        (eng / "core.py").write_text("x = 1\n")
        subprocess.run(["git", "-C", str(d), "add", "."], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "eng"], check=True)
        base = (eng / "core.py").stat().st_mtime
        assert engine_latest_change(d)[1] == "Horosa-Web/astropy/core.py", "被跟踪的引擎源码计入"
        future = base + 3600
        for rel in ("tests/test_x.py", "run.log", "README.md"):
            p = eng / rel; p.write_text("y"); os.utime(p, (future, future))
        assert int(engine_latest_change(d)[0]) == int(base), "测试 / 被忽略 / 说明文件的改动不计"
        assert engine_service_fresh(base + 5, engine_latest_change(d)[0]), "服务在最近改动之后启动 → 新鲜"
        os.utime(eng / "core.py", (future, future))
        assert not engine_service_fresh(base + 5, engine_latest_change(d)[0]), "服务启动后引擎源码又改了 → 旧引擎"
        newer = future + 60; (eng / "new_mod.py").write_text("z"); os.utime(eng / "new_mod.py", (newer, newer))
        assert engine_latest_change(d)[1] == "Horosa-Web/astropy/new_mod.py", "未跟踪但未被忽略的新文件计入"
    # 真 git:write → check 同 HEAD 过;加一条文档提交 → 仍过;加一条源码提交 → 发布红 / 日常告警
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        subprocess.run(["git", "init", "-q", str(d)], check=True)
        (d / ".gitignore").write_text("Horosa_Desktop_Installer/build/\n")   # 与真仓同:戳文件本身不算未提交改动
        subprocess.run(["git", "-C", str(d), "add", ".gitignore"], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base"], check=True)
        for s in REQUIRED:
            write(d, s, 0, f"{s} ok")
        assert check(d, True)[0] == 0, "真仓同 HEAD → 过"
        (d / "docs").mkdir(); (d / "docs" / "n.md").write_text("x")
        subprocess.run(["git", "-C", str(d), "add", "docs/n.md"], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "docs"], check=True)
        assert check(d, True)[0] == 0, "真仓文档提交后 → 仍过"
        write(d, "pytest", 0, "after docs commit")   # 文档提交后再落一个套件:已记套件必须保留(不重开)
        assert check(d, True)[0] == 0 and len(load(d)["suites"]) == len(REQUIRED), "真仓文档提交后再写戳 → 保留全部套件并挪到新 HEAD"
        (d / "src.py").write_text("x"); subprocess.run(["git", "-C", str(d), "add", "src.py"], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "src"], check=True)
        assert check(d, True)[0] == 1 and check(d, False)[0] == 2, "真仓源码提交后 → 发布红 / 日常告警"
        write(d, "pytest", 0, "again")   # 新 HEAD 上写戳 = 重开(旧套件作废)
        assert "缺套件" in check(d, False)[1], "新 HEAD 重开戳只含刚写的套件"
        for s_ in REQUIRED:
            write(d, s_, 0, "ok")
        # 中文路径的纯文档提交:不被转义成 "\345…" 当源码
        (d / "docs" / "记录.md").write_text("x"); subprocess.run(["git", "-C", str(d), "add", "docs/记录.md"], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "zh docs"], check=True)
        assert check(d, True)[0] == 0, "中文路径文档提交 → 仍有效"
        # 源码改名进 docs/:旧路径(源码)也算改动 → 作废
        subprocess.run(["git", "-C", str(d), "mv", "src.py", "docs/src.py.md"], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "mv"], check=True)
        assert check(d, True)[0] == 1, "源码改名成文档 → 旧路径算源码改动"
        # 改写提交(amend):旧戳提交不再是祖先,只比两棵树 —— 只差文档 → 仍有效;改写时动了源码 → 作废
        for s_ in REQUIRED:
            write(d, s_, 0, "ok")
        (d / "docs" / "amend.md").write_text("x"); subprocess.run(["git", "-C", str(d), "add", "docs/amend.md"], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--amend", "--no-edit"], check=True)
        assert _git(d, "merge-base", "--is-ancestor", load(d)["head"], head_of(d))[0] != 0, "前提:amend 后旧戳提交不是祖先"
        assert check(d, True)[0] == 0, "amend 只加文档 → 戳仍有效"
        write(d, "pytest", 0, "after amend")
        assert len(load(d)["suites"]) == len(REQUIRED) and load(d)["head"] == head_of(d), "amend 后再写戳 → 保留全部套件并挪到新 HEAD"
        (d / "src2.py").write_text("x"); subprocess.run(["git", "-C", str(d), "add", "src2.py"], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--amend", "--no-edit"], check=True)
        assert check(d, True)[0] == 1, "amend 带源码改动 → 作废"
        # 戳记的提交在本仓找不到 → 发布红 / 日常告警(不能当「没改动」)
        st_ = load(d); st_["head"] = "e" * 40; stamp_path(d).write_text(json.dumps(st_), encoding="utf-8")
        assert check(d, True)[0] == 1 and check(d, False)[0] == 2 and "找不到" in check(d, False)[1], "戳提交找不到 → 发布红 / 日常告警"
        # 开跑后 HEAD 变了 → 不落戳
        try:
            write(d, "pytest", 0, "x", started_head="f" * 40)
            raise AssertionError("开跑后 HEAD 变了应拒写")
        except SystemExit:
            pass
    print("release-baseline-stamp self-test OK(逻辑 16 向 + 真仓 12 向 + 引擎新鲜度 9 向)")
    return 0


def main(argv):
    if argv and argv[0] == "--self-test":
        return self_test()
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write"); w.add_argument("--repo", required=True); w.add_argument("--suite", required=True, choices=REQUIRED); w.add_argument("--rc", required=True, type=int); w.add_argument("--summary", default=""); w.add_argument("--log", default=""); w.add_argument("--head", default="")
    c = sub.add_parser("check"); c.add_argument("--repo", required=True); c.add_argument("--require", action="store_true")
    e = sub.add_parser("engine-fresh"); e.add_argument("--repo", required=True); e.add_argument("--pid", required=True, type=int)
    a = ap.parse_args(argv)
    if a.cmd == "engine-fresh":
        code, msg = engine_fresh(pathlib.Path(a.repo).resolve(), a.pid)
        print(msg)
        return code
    if a.cmd == "write":
        st = write(a.repo, a.suite, a.rc, a.summary, a.log, a.head)
        print(f"[baseline-stamp] {a.suite} rc={a.rc} → {stamp_path(a.repo)}(HEAD {st['head_short']},已记 {len(st['suites'])}/{len(REQUIRED)} 套件)")
        return 0
    code, msg = check(a.repo, a.require)
    print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
