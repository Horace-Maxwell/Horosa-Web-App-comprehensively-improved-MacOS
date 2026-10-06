#!/usr/bin/env python3
"""权限位单一来源(prev_parts_modes)的判别向量 —— 两层缓存同一口径的变异自证:
① tar 条目名从最后一个 runtime-payload 起截取;路径里没有该目录 → None;
② 留档有该条目 → 用留档位;没有 → 暂存位;HOROSA_PREV_PARTS_MODES=0 → 一律暂存位;留档路径缺失 / 坏 JSON → 暂存位;
③ 域级缓存层 `_put_signed`:暂存 0644、留档 0600 → 0600;无留档 → 0644(保留既有行为);
④ 单文件缓存层 `rebuild_archive_from_tree`:暂存 0644、留档 0600 → 0600;无留档 → 0644(不再落 NamedTemporaryFile 的 0600);
⑤ 跨层:同一条目 + 同一留档,③④ 两层放回的权限位相同(任一层绕过留档即红)。"""
import importlib.util, json, os, pathlib, stat, sys, tempfile, zipfile

HERE = pathlib.Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def mode_of(p):
    return stat.S_IMODE(p.stat().st_mode)


def run():
    ppm = load(HERE / "prev_parts_modes.py", "prev_parts_modes")
    cache = load(HERE / "sign_payload_cached.py", "sign_payload_cached")
    signer = load(HERE / "sign_runtime_payload.py", "sign_runtime_payload")
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        stage = d / "build" / "runtime" / "runtime-payload"
        lib = stage / "runtime" / "mac" / "bundle" / "boot-exploded" / "BOOT-INF" / "lib"
        lib.mkdir(parents=True)
        jar = lib / "jna-4.5.2.jar"
        with zipfile.ZipFile(jar, "w") as z:
            z.writestr("a.txt", b"hello")
        os.chmod(jar, 0o644)
        assert ppm.tar_name_of(jar) == "runtime-payload/runtime/mac/bundle/boot-exploded/BOOT-INF/lib/jna-4.5.2.jar", "① tar 条目名截取"
        assert ppm.tar_name_of(d / "x" / "y.jar") is None, "① 无 runtime-payload 目录 → None"
        rec = d / "prev-parts-headers.json"
        rec.write_text(json.dumps({"java-lib": [[ppm.tar_name_of(jar), "0", 123, 0o600, 0, ""],
                                               ["runtime-payload/other.so", "0", 1, 0o755, 0, ""]]}))
        os.environ["HOROSA_PREV_PARTS_HEADERS"] = str(rec)
        os.environ["HOROSA_PREV_PARTS_MODES"] = "1"
        ppm._RECORD_CACHE.clear()
        assert ppm.decide_mode(jar, 0o644) == (0o600, "prev"), "② 留档有 → 留档位"
        assert ppm.decide_mode(lib / "new.jar", 0o644) == (0o644, "staged"), "② 留档没有 → 暂存位"
        assert ppm.decide_mode(d / "nowhere.jar", None) == (None, None), "② 两者都没有 → 不改"
        os.environ["HOROSA_PREV_PARTS_MODES"] = "0"
        assert ppm.decide_mode(jar, 0o644) == (0o644, "staged"), "② 开关 =0 → 一律暂存位"
        os.environ["HOROSA_PREV_PARTS_MODES"] = "1"
        os.environ["HOROSA_PREV_PARTS_HEADERS"] = str(d / "missing.json")
        ppm._RECORD_CACHE.clear()
        assert ppm.decide_mode(jar, 0o644) == (0o644, "staged"), "② 留档缺失 → 暂存位"
        bad = d / "bad.json"; bad.write_text("{not json")
        os.environ["HOROSA_PREV_PARTS_HEADERS"] = str(bad); ppm._RECORD_CACHE.clear()
        assert ppm.decide_mode(jar, 0o644) == (0o644, "staged"), "② 坏 JSON → 暂存位"
        os.environ["HOROSA_PREV_PARTS_HEADERS"] = str(rec)
        for m in (cache, signer):
            m.prev_parts_modes._RECORD_CACHE.clear()
        src = d / "signed.jar"; src.write_bytes(b"SIGNED-JAR"); os.chmod(src, 0o755)
        cache._put_signed(src, jar)
        assert jar.read_bytes() == b"SIGNED-JAR" and mode_of(jar) == 0o600, "③ 域级放回应取留档 0600"
        os.environ["HOROSA_PREV_PARTS_MODES"] = "0"
        os.chmod(jar, 0o644); cache._put_signed(src, jar)
        assert mode_of(jar) == 0o644, "③ 无留档(开关关)→ 保留暂存 0644"
        os.environ["HOROSA_PREV_PARTS_MODES"] = "1"
        with zipfile.ZipFile(jar, "w") as z:
            z.writestr("lib.dylib", b"MACHO")
        os.chmod(jar, 0o644)
        tree = d / "tree"; tree.mkdir(); (tree / "lib.dylib").write_bytes(b"MACHO-SIGNED")
        signer.rebuild_archive_from_tree(jar, tree)
        with zipfile.ZipFile(jar) as z:
            assert z.read("lib.dylib") == b"MACHO-SIGNED", "④ 重建后成员应为签名字节"
        assert mode_of(jar) == 0o600, "④ 重建后应取留档 0600"
        os.environ["HOROSA_PREV_PARTS_MODES"] = "0"
        os.chmod(jar, 0o644); signer.rebuild_archive_from_tree(jar, tree)
        assert mode_of(jar) == 0o644, "④ 无留档 → 保留暂存 0644(不再落 tempfile 的 0600)"
        os.environ["HOROSA_PREV_PARTS_MODES"] = "1"
        os.chmod(jar, 0o644); cache._put_signed(src, jar); m_cache = mode_of(jar)
        with zipfile.ZipFile(jar, "w") as z:
            z.writestr("lib.dylib", b"MACHO")
        os.chmod(jar, 0o644); signer.rebuild_archive_from_tree(jar, tree); m_native = mode_of(jar)
        assert m_cache == m_native == 0o600, f"⑤ 两层放回权限位必须相同:域级 {oct(m_cache)} vs 单文件 {oct(m_native)}"
    print("prev-parts-modes self-test OK(①–⑤)")
    return 0


if __name__ == "__main__":
    sys.exit(run())
