#!/usr/bin/env python3
"""打包内「稳定部件 ↔ 上一版逐条目头部对拍」:在 components 刚打出来、还没到包后核验之前,就把
py-runtime / jdk-runtime / ephe-data / xuanshi-data / java-lib 五个稳定部件与上一版(prepare_sign_seed.py 留档的
build/.sign-seed/prev-parts-headers.json + prev-components-lock.json)逐条目比 tar 头(名 / 类型 / 大小 / 权限 / mtime /
链接目标)与部件 sha,当场打印「哪个部件、哪些条目、差在哪个字段」。

判读(每个部件一行):
  · sha 同                     → 恒等 ✓(增量更新可复用)
  · sha 异、头部逐条目全同     → 只有内容变了:签名时间戳 / pyc 字节漂移 → 查签名种子是否命中(v3.11.2 实抓形态)
  · sha 异、头部有差           → 列前 N 条:新增 / 消失 / 大小 / 权限 / mtime(权限差 = 种子解包没带 -p 的形态)
  · 本版部件带扩展属性 / ACL 头 → 一律判红(exit 4,不看 strict):部件 tar 必须 --no-xattrs --no-acls 打,
                                 xattr(com.apple.provenance / macl …)随打包进程环境来去,写进头 = sha 随环境漂
缺留档(首发 / dist 已清)只提示不判。缺省只报告(exit 0);HOROSA_STABLE_PARTS_STRICT=1 时任一稳定部件不恒等 → exit 3
(内容确有改动的版本别开 strict,拿这里的逐条目输出去证明差异恰为改动文件即可)。

用法: verify_stable_parts_headers.py <installer_root> [--strict] [--limit N]
自证: verify_stable_parts_headers.py --self-test
"""
import hashlib
import json
import os
import pathlib
import sys
import tarfile
import tempfile

STABLE_PARTS = ("py-runtime", "jdk-runtime", "ephe-data", "xuanshi-data", "java-lib")
FIELDS = ("type", "size", "mode", "mtime", "linkname")


def part_tar_name(part: str) -> str:
    return f"horosa-comp-{part}-macos-arm64.tar.gz"


def tar_headers(tar_path: pathlib.Path) -> list:
    out = []
    with tarfile.open(tar_path, "r:gz") as tf:
        for m in tf:
            out.append([m.name, m.type.decode("latin-1") if isinstance(m.type, bytes) else str(m.type),
                        int(m.size), int(m.mode & 0o7777), int(m.mtime), m.linkname or ""])
    return out


def xattr_entries(tar_path: pathlib.Path) -> int:
    """部件里带扩展属性 / ACL pax 头(LIBARCHIVE.xattr.* / SCHILY.xattr.* / SCHILY.acl.*)的条目数。"""
    n = 0
    with tarfile.open(tar_path, "r:gz") as tf:
        for m in tf:
            if any(".xattr." in k or k.startswith("SCHILY.acl") for k in m.pax_headers):
                n += 1
    return n


def sha256_of(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def lock_shas(lock_path: pathlib.Path) -> dict:
    try:
        data = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    out = {}
    for c in data.get("components") or []:
        if isinstance(c, dict) and c.get("name") and c.get("sha256"):
            out[c["name"]] = c["sha256"]
    return out


def diff_headers(prev: list, cur: list, limit: int = 10) -> dict:
    """返回 {'added': [...], 'removed': [...], 'changed': [(name, field, prev, cur), ...], 'total': n}(截断到 limit)。"""
    pm = {r[0]: r for r in prev}
    cm = {r[0]: r for r in cur}
    added = [n for n in cm if n not in pm]
    removed = [n for n in pm if n not in cm]
    changed = []
    for n in cm:
        if n in pm and pm[n] != cm[n]:
            for i, f in enumerate(FIELDS, start=1):
                if pm[n][i] != cm[n][i]:
                    changed.append((n, f, pm[n][i], cm[n][i]))
    total = len(added) + len(removed) + len(changed)
    return {"added": added[:limit], "removed": removed[:limit], "changed": changed[:limit], "total": total}


def compare(installer_root: pathlib.Path, limit: int = 10) -> dict:
    """回 {part: {'status': 'identical'|'content-only'|'header-diff'|'no-prev'|'missing', ...}}"""
    comp = installer_root / "dist" / "components"
    seed_root = installer_root / "build" / ".sign-seed"
    prev_headers_path = seed_root / "prev-parts-headers.json"
    prev_lock = lock_shas(seed_root / "prev-components-lock.json")
    cur_lock = lock_shas(comp / "components-lock.json")
    try:
        prev_headers = json.loads(prev_headers_path.read_text(encoding="utf-8")) if prev_headers_path.is_file() else {}
    except (OSError, ValueError):
        prev_headers = {}
    result = {}
    for part in STABLE_PARTS:
        t = comp / part_tar_name(part)
        if not t.is_file():
            result[part] = {"status": "missing"}
            continue
        xa = xattr_entries(t)
        if xa:
            result[part] = {"status": "xattr", "xattr": xa}
            continue
        if part not in prev_headers:
            result[part] = {"status": "no-prev"}
            continue
        cur_sha = cur_lock.get(part) or sha256_of(t)
        prev_sha = prev_lock.get(part)
        if prev_sha and prev_sha == cur_sha:
            result[part] = {"status": "identical", "sha": cur_sha[:12]}
            continue
        d = diff_headers(prev_headers[part], tar_headers(t), limit)
        if d["total"] == 0:
            result[part] = {"status": "content-only", "sha": cur_sha[:12], "prev_sha": (prev_sha or "?")[:12]}
        else:
            result[part] = {"status": "header-diff", "sha": cur_sha[:12], "prev_sha": (prev_sha or "?")[:12], "diff": d}
    return result


def report(result: dict) -> int:
    bad = 0
    for part, r in result.items():
        st = r["status"]
        if st == "xattr":
            bad += 1
            print(f"[stable-parts] {part:13s} ❌ 部件带扩展属性 / ACL 头 {r['xattr']} 条:部件 tar 必须 --no-xattrs --no-acls 打"
                  f"(否则 sha 随打包进程环境漂)")
        elif st == "identical":
            print(f"[stable-parts] {part:13s} 与上一版恒等 ✓ ({r['sha']})")
        elif st == "no-prev":
            print(f"[stable-parts] {part:13s} 无上一版留档(首发 / dist 已清),不判")
        elif st == "missing":
            print(f"[stable-parts] {part:13s} 本次没有产出该部件")
        elif st == "content-only":
            bad += 1
            print(f"[stable-parts] {part:13s} ⚠ sha 变了({r['prev_sha']} → {r['sha']})但头部逐条目全同:只有内容变 —— "
                  f"签名时间戳 / pyc 字节漂移,查签名种子是否命中(sign-seed 行);上一版部件带扩展属性头时也是这一形态")
        else:
            bad += 1
            d = r["diff"]
            print(f"[stable-parts] {part:13s} ⚠ sha 变了({r['prev_sha']} → {r['sha']}),头部差异 {d['total']} 处:")
            for n in d["added"]:
                print(f"    + 新增 {n}")
            for n in d["removed"]:
                print(f"    - 消失 {n}")
            for n, f, a, b in d["changed"]:
                if f == "mode":
                    a, b = oct(a), oct(b)
                print(f"    ~ {n} {f}: {a} → {b}")
            if d["total"] > len(d["added"]) + len(d["removed"]) + len(d["changed"]):
                print("    …(已截断;--limit N 看更多)")
    return bad


def _mk_tar(path: pathlib.Path, entries: list, pax: dict = None) -> None:
    """entries: [(name, bytes, mode, mtime)];pax = 每条都带的 pax 头(模拟扩展属性头)"""
    with tarfile.open(path, "w:gz", format=tarfile.PAX_FORMAT) as tf:
        for name, data, mode, mtime in entries:
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            ti.mode = mode
            ti.mtime = mtime
            if pax:
                ti.pax_headers = dict(pax)
            import io
            tf.addfile(ti, io.BytesIO(data))


def self_test() -> int:
    problems = []
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        comp = root / "dist" / "components"
        seed = root / "build" / ".sign-seed"
        comp.mkdir(parents=True)
        seed.mkdir(parents=True)
        base = [("a/x.so", b"AAAA", 0o775, 1000), ("a/y.txt", b"BB", 0o644, 1000)]
        # 上一版:五个部件同一内容
        prev_headers, prev_lock = {}, {"components": []}
        for part in STABLE_PARTS:
            t = comp / part_tar_name(part)
            _mk_tar(t, base)
            prev_headers[part] = tar_headers(t)
            prev_lock["components"].append({"name": part, "sha256": sha256_of(t)})
        (seed / "prev-parts-headers.json").write_text(json.dumps(prev_headers))
        (seed / "prev-components-lock.json").write_text(json.dumps(prev_lock))
        # 本版:py-runtime 恒等;jdk-runtime 权限漂(0775→0755);ephe-data 内容变头不变;xuanshi-data 新增一条;java-lib 无部件
        _mk_tar(comp / part_tar_name("jdk-runtime"), [("a/x.so", b"AAAA", 0o755, 1000), ("a/y.txt", b"BB", 0o644, 1000)])
        _mk_tar(comp / part_tar_name("ephe-data"), [("a/x.so", b"CCCC", 0o775, 1000), ("a/y.txt", b"BB", 0o644, 1000)])
        _mk_tar(comp / part_tar_name("xuanshi-data"), base + [("a/z.sqlite-shm", b"Z", 0o644, 1000)])
        (comp / part_tar_name("java-lib")).unlink()
        cur_lock = {"components": [{"name": p, "sha256": sha256_of(comp / part_tar_name(p))}
                                   for p in STABLE_PARTS if (comp / part_tar_name(p)).is_file()]}
        (comp / "components-lock.json").write_text(json.dumps(cur_lock))
        r = compare(root)
        exp = {"py-runtime": "identical", "jdk-runtime": "header-diff", "ephe-data": "content-only",
               "xuanshi-data": "header-diff", "java-lib": "missing"}
        for part, st in exp.items():
            if r[part]["status"] != st:
                problems.append(f"{part}: 期望 {st} 实际 {r[part]['status']}")
        d = r["jdk-runtime"].get("diff", {})
        if not any(c[1] == "mode" and c[2] == 0o775 and c[3] == 0o755 for c in d.get("changed", [])):
            problems.append(f"jdk-runtime 应报 mode 0o775→0o755: {d}")
        if r["xuanshi-data"].get("diff", {}).get("added") != ["a/z.sqlite-shm"]:
            problems.append(f"xuanshi-data 应报新增 a/z.sqlite-shm: {r['xuanshi-data']}")
        # 本版部件带扩展属性头(内容 / 头部与上一版全同也判红)
        _mk_tar(comp / part_tar_name("py-runtime"), base, {"SCHILY.xattr.com.apple.provenance": "x"})
        r3 = compare(root)
        if r3["py-runtime"]["status"] != "xattr" or report({"py-runtime": r3["py-runtime"]}) != 1:
            problems.append(f"带扩展属性头应判 xattr: {r3['py-runtime']}")
        _mk_tar(comp / part_tar_name("py-runtime"), base)
        # 无留档:全部 no-prev
        (seed / "prev-parts-headers.json").unlink()
        r2 = compare(root)
        if any(v["status"] not in ("no-prev", "missing") for v in r2.values()):
            problems.append(f"无留档应全部 no-prev: {r2}")
    if problems:
        print("\n".join("  ❌ " + p for p in problems))
        print("❌ verify_stable_parts_headers 自证失败")
        return 1
    print("✅ verify_stable_parts_headers 自证通过(恒等 / 权限漂 / 只内容变 / 新增条目 / 缺部件 / 无留档 / 带扩展属性头 七形态各判对)")
    return 0


def main(argv: list) -> int:
    if "--self-test" in argv:
        return self_test()
    limit, skip = 10, set()
    if "--limit" in argv:
        i = argv.index("--limit")
        try:
            limit = int(argv[i + 1])
            skip.add(i + 1)
        except (IndexError, ValueError):
            pass
    args = [a for j, a in enumerate(argv) if not a.startswith("--") and j not in skip]
    if len(args) != 1:
        print("usage: verify_stable_parts_headers.py <installer_root> [--strict] [--limit N] | --self-test", file=sys.stderr)
        return 2
    root = pathlib.Path(args[0]).resolve()
    result = compare(root, limit)
    bad = report(result)
    strict = "--strict" in argv or os.environ.get("HOROSA_STABLE_PARTS_STRICT", "0") == "1"
    xa = [p for p, r in result.items() if r["status"] == "xattr"]
    if xa:
        print(f"[stable-parts] ❌ 部件带扩展属性 / ACL 头:{', '.join(xa)}", file=sys.stderr)
        return 4
    if bad and strict:
        print(f"[stable-parts] ❌ strict:{bad} 个稳定部件与上一版不恒等", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
