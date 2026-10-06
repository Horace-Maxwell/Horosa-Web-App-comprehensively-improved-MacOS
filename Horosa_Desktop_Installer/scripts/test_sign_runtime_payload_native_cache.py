#!/usr/bin/env python3
"""单文件原生库签名按内容缓存的判别向量(不真签:把 sign_path 换成「追加伪签名字节」)。
① 同内容第二次 → hit,产物字节与第一次逐字节相同(时间戳漂移被缓存吸收);② 内容不同 → 各自真签,互不串;
③ HOROSA_SIGN_CACHE=0 → plain(不读不写缓存);④ 未设缓存目录 → plain;⑤ 不同身份不共用缓存。
⑥ 同内容不同基名各自条目(codesign identifier = 基名);⑦ 命中校验失败 → 删条目 + 还原字节 + 真签(revoked);
⑧ codesign 参数模板 / 语义代次变 → 缓存目录变、旧条目不可见;⑨ 播种:同名 jar 同名 Mach-O 成员按(基名 + 未签名字节)入缓存、
原子写、第二次不重写;⑩ 缓存条目落盘经 tmp + rename(目录里不留 .tmp)。"""
import os, pathlib, sys, tempfile, importlib.util, zipfile

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("sign_runtime_payload", HERE / "sign_runtime_payload.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

calls = {"n": 0}
def fake_sign(path, identity, keychain):
    calls["n"] += 1
    # 伪签名:追加「身份 + 单调计数」,模拟每次真签字节都不同(时间戳)
    with open(path, "ab") as f:
        f.write(("SIG:%s:%d" % (identity, calls["n"])).encode())
mod.sign_path = fake_sign
mod.verify_signature = lambda p: True   # 伪签名过不了真 codesign --verify;⑦ 单独把它换成 False 测回真签

def run():
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        os.environ["HOROSA_NATIVE_SIGN_CACHE"] = str(d / "cache")
        os.environ["HOROSA_SIGN_CACHE"] = "1"
        a1 = d / "a1.dylib"; a1.write_bytes(b"MACHO-A")
        assert mod.sign_file_cached(a1, "ID-1", None) == "signed"
        first = a1.read_bytes()
        (d / "sub").mkdir()
        a2 = d / "sub" / "a1.dylib"; a2.write_bytes(b"MACHO-A")   # 同基名同内容(不同目录)→ 命中;基名入键见 ⑥
        assert mod.sign_file_cached(a2, "ID-1", None) == "hit", "同基名同内容第二次必须命中"
        assert a2.read_bytes() == first, "命中产物必须与第一次逐字节相同"
        b = d / "b.dylib"; b.write_bytes(b"MACHO-B")
        assert mod.sign_file_cached(b, "ID-1", None) == "signed"
        assert b.read_bytes() != first, "不同内容不得串缓存"
        c = d / "c.dylib"; c.write_bytes(b"MACHO-A")
        assert mod.sign_file_cached(c, "ID-2", None) == "signed", "不同身份不共用缓存"
        n_before = calls["n"]
        os.environ["HOROSA_SIGN_CACHE"] = "0"
        e = d / "e.dylib"; e.write_bytes(b"MACHO-A")
        assert mod.sign_file_cached(e, "ID-1", None) == "plain" and calls["n"] == n_before + 1, "开关关闭必须真签且不读缓存"
        os.environ["HOROSA_SIGN_CACHE"] = "1"; os.environ.pop("HOROSA_NATIVE_SIGN_CACHE")
        f = d / "f.dylib"; f.write_bytes(b"MACHO-A")
        assert mod.sign_file_cached(f, "ID-1", None) == "plain", "未设缓存目录必须退回真签"
        # ⑥ 同内容、不同基名 → 各自条目(不共用)
        os.environ["HOROSA_NATIVE_SIGN_CACHE"] = str(d / "cache")
        g1 = d / "libfoo.dylib"; g1.write_bytes(b"MACHO-G")
        assert mod.sign_file_cached(g1, "ID-1", None) == "signed"
        g2 = d / "libbar.dylib"; g2.write_bytes(b"MACHO-G")
        assert mod.sign_file_cached(g2, "ID-1", None) == "signed", "同内容不同基名不得命中同一条目"
        g3 = d / "libfoo.dylib"; g3.write_bytes(b"MACHO-G")
        assert mod.sign_file_cached(g3, "ID-1", None) == "hit" and g3.read_bytes() == g1.read_bytes()
        # ⑦ 命中校验失败 → 删条目、还原未签名字节后真签
        mod.verify_signature = lambda p: False
        h = d / "libfoo.dylib"; h.write_bytes(b"MACHO-G")
        n0 = calls["n"]
        assert mod.sign_file_cached(h, "ID-1", None) == "signed" and calls["n"] == n0 + 1, "校验失败必须真签"
        assert h.read_bytes().startswith(b"MACHO-G") and h.read_bytes().count(b"SIG:") == 1, "真签前必须先还原未签名字节(不能在坏产物上再签)"
        assert mod.NATIVE_STATS.get("revoked", 0) >= 1
        mod.verify_signature = lambda p: True
        h2 = d / "libfoo.dylib"; h2.write_bytes(b"MACHO-G")
        assert mod.sign_file_cached(h2, "ID-1", None) == "hit" and h2.read_bytes() == h.read_bytes(), "重签后的条目再次可命中"
        # ⑧ 参数模板 / 语义代次变 → 目录变,旧条目不可见
        dir_a = mod.native_cache_dir("ID-1")
        saved = (mod.CODESIGN_ARGS_TEMPLATE, mod.SIGNER_CACHE_EPOCH)
        mod.CODESIGN_ARGS_TEMPLATE = saved[0] + ("--entitlements", "x.plist")
        assert mod.native_cache_dir("ID-1") != dir_a, "参数模板变了缓存目录必须变"
        k = d / "libfoo.dylib"; k.write_bytes(b"MACHO-G")
        assert mod.sign_file_cached(k, "ID-1", None) == "signed", "换参数模板后不得命中旧条目"
        mod.CODESIGN_ARGS_TEMPLATE = saved[0]; mod.SIGNER_CACHE_EPOCH = saved[1] + "x"
        assert mod.native_cache_dir("ID-1") != dir_a, "语义代次变了缓存目录必须变"
        mod.SIGNER_CACHE_EPOCH = saved[1]
        assert mod.native_cache_dir("ID-1") == dir_a
        # ⑩ 目录里不留 .tmp
        assert not list(dir_a.glob("*.tmp")), "缓存条目必须 tmp + rename 落盘"
        # ⑨ 播种:未签名 jar 目录 × 已签名 jar 目录 → 键(基名 + 未签名字节)= 签名器命中键
        macho = b"\xcf\xfa\xed\xfe" + b"\0" * 12 + b"NATIVE-1"
        signed = macho + b"SIG:published"
        u = d / "unsigned"; u.mkdir(); sdir = d / "signed"; sdir.mkdir()
        for jar_dir, member in ((u, macho), (sdir, signed)):
            with zipfile.ZipFile(jar_dir / "jna-5.jar", "w") as z:
                z.writestr("com/sun/jna/darwin-aarch64/libjnidispatch.jnilib", member)
                z.writestr("com/sun/jna/Native.class", b"\xca\xfe\xba\xbe\x00\x00\x00\x41" + b"\0" * 8)
                z.writestr("META-INF/MANIFEST.MF", b"Manifest-Version: 1.0\n")
        st = mod.seed_native_cache(u, sdir, "ID-1")
        assert st == {"pairs": 1, "seeded": 1, "skipped": 0}, st
        assert mod.seed_native_cache(u, sdir, "ID-1") == {"pairs": 1, "seeded": 0, "skipped": 0}, "第二次播种不重写"
        m = d / "libjnidispatch.jnilib"; m.write_bytes(macho)
        assert mod.sign_file_cached(m, "ID-1", None) == "hit" and m.read_bytes() == signed, "播种后签名器同键必命中、产物 = 已发布字节"
        os.environ["HOROSA_SIGN_CACHE"] = "0"
        assert mod.seed_native_cache(u, sdir, "ID-1") == {"disabled": True}
        os.environ["HOROSA_SIGN_CACHE"] = "1"
        # ⑪ jar 重建后的权限位:无留档 → 保留 jar 原有位(不再是 NamedTemporaryFile 的 0600);有留档 → 留档位
        os.environ.pop("HOROSA_PREV_PARTS_HEADERS", None); mod.prev_parts_modes._RECORD_CACHE.clear()
        stage = d / "runtime-payload" / "lib"; stage.mkdir(parents=True)
        j = stage / "n.jar"
        with zipfile.ZipFile(j, "w") as z:
            z.writestr("x.dylib", b"MACHO")
        os.chmod(j, 0o644); tree = d / "jtree"; tree.mkdir(); (tree / "x.dylib").write_bytes(b"MACHO-S")
        mod.rebuild_archive_from_tree(j, tree)
        assert (j.stat().st_mode & 0o7777) == 0o644, "⑪ 无留档:重建后必须保留 jar 原有权限位"
        rec = d / "prev.json"; rec.write_text('{"java-lib": [["runtime-payload/lib/n.jar", "0", 1, 384, 0, ""]]}')
        os.environ["HOROSA_PREV_PARTS_HEADERS"] = str(rec); mod.prev_parts_modes._RECORD_CACHE.clear()
        mod.rebuild_archive_from_tree(j, tree)
        assert (j.stat().st_mode & 0o7777) == 0o600, "⑪ 有留档:重建后必须取留档位(0600)"
        os.environ.pop("HOROSA_PREV_PARTS_HEADERS", None); mod.prev_parts_modes._RECORD_CACHE.clear()
    print("native-sign-cache self-test OK")
    return 0

if __name__ == "__main__":
    sys.exit(run())
