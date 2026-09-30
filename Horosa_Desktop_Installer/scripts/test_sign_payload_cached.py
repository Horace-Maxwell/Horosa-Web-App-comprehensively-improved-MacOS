#!/usr/bin/env python3
"""域级签名缓存层的判别向量(不真签):
① 缓存键不再含脚本全文:签名器脚本文本改动(加注释)而参数模板 / 语义代次不变 → 键不变;
② 参数模板或语义代次变 → 键变;签名器缺这两个量(旧版)→ 退回全文 sha;
③ 签名产物放回暂存树保留暂存树原有权限位(种子 / 缓存文件是 0755,暂存是 0775 → 结果 0775);
④ restore()/try_seed() 都走这条;store() 的 manifest 带键面快照、经 tmp+rename 落盘。"""
import os, pathlib, sys, tempfile, importlib.util, json, stat

HERE = pathlib.Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def run():
    cache = load(HERE / "sign_payload_cached.py", "sign_payload_cached")
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        signer_src = (HERE / "sign_runtime_payload.py").read_text(encoding="utf-8")
        s1 = d / "signer1.py"; s1.write_text(signer_src, encoding="utf-8")
        s2 = d / "signer2.py"; s2.write_text(signer_src + "\n# 纯注释改动:不许作废缓存\n", encoding="utf-8")
        m1, m2 = cache.load_signer_module(str(s1)), cache.load_signer_module(str(s2))
        assert m1 is not None and m2 is not None
        keyed = {"bin/python3": "aa" * 32, "lib/libx.dylib": "bb" * 32}
        k1 = cache.cache_key(keyed, "ID", cache.signer_salt(m1, str(s1)))
        k2 = cache.cache_key(keyed, "ID", cache.signer_salt(m2, str(s2)))
        assert k1 == k2, "① 签名器脚本文本改动(参数模板 / 代次不变)不得改变缓存键"
        assert cache.signer_salt(m1, str(s1)).startswith("salt:"), "签名器自报的盐必须被采用"
        m2.SIGNER_CACHE_EPOCH = m2.SIGNER_CACHE_EPOCH + "x"
        assert cache.cache_key(keyed, "ID", cache.signer_salt(m2, str(s2))) != k1, "② 语义代次变 → 键变"
        m2.SIGNER_CACHE_EPOCH = m1.SIGNER_CACHE_EPOCH
        m2.CODESIGN_ARGS_TEMPLATE = m2.CODESIGN_ARGS_TEMPLATE + ("--entitlements", "e.plist")
        assert cache.cache_key(keyed, "ID", cache.signer_salt(m2, str(s2))) != k1, "② 参数模板变 → 键变"
        assert cache.cache_key(dict(keyed, **{"lib/libx.dylib": "cc" * 32}), "ID", cache.signer_salt(m1, str(s1))) != k1, "内容变 → 键变"
        assert cache.cache_key(keyed, "ID-2", cache.signer_salt(m1, str(s1))) != k1, "身份变 → 键变"
        # 旧版签名器(没有 signer_cache_salt)→ 退回全文 sha
        class Old: pass
        old = Old(); old.is_macho = lambda p: False; old.ARCHIVE_SUFFIXES = {".jar"}
        assert cache.signer_salt(old, str(s1)).startswith("sha:"), "缺盐函数必须退回全文 sha(保守)"
        # ③ 权限位:目标 0775,源 0755 → 放回后仍 0775
        root = d / "stage"; (root / "lib").mkdir(parents=True)
        dst = root / "lib" / "a.so"; dst.write_bytes(b"UNSIGNED"); os.chmod(dst, 0o775)
        src = d / "a.so.signed"; src.write_bytes(b"SIGNED"); os.chmod(src, 0o755)
        cache._put_signed(src, dst)
        assert dst.read_bytes() == b"SIGNED" and stat.S_IMODE(dst.stat().st_mode) == 0o775, "③ 放回后必须保留暂存树的权限位"
        (d / "other").mkdir(); ro = d / "other" / "ro.so"; ro.write_bytes(b"X"); os.chmod(ro, 0o444)   # 暂存树之外,不进种子内容面
        cache._put_signed(src, ro)
        assert ro.read_bytes() == b"SIGNED" and stat.S_IMODE(ro.stat().st_mode) == 0o444, "只读目标也要能放回且保留 0444"
        # ④ restore() 走同一条:缓存里的文件 0755,暂存 0775 → 0775
        cdir = d / "cache" / "k1"; (cdir / "files" / "lib").mkdir(parents=True)
        (cdir / "files" / "lib" / "a.so").write_bytes(b"CACHED"); os.chmod(cdir / "files" / "lib" / "a.so", 0o755)
        (cdir / "manifest.json").write_text(json.dumps({"version": 2, "files": ["lib/a.so"]}))
        os.chmod(dst, 0o775)
        assert cache.restore(cdir, root) == 1 and dst.read_bytes() == b"CACHED" and stat.S_IMODE(dst.stat().st_mode) == 0o775
        # ④ try_seed():种子树 0755,暂存 0775 → 0775;内容面不一致 → 拒用
        seed = d / "seed" / "stage"; (seed / "lib").mkdir(parents=True)
        (seed / "lib" / "a.so").write_bytes(b"SEEDED"); os.chmod(seed / "lib" / "a.so", 0o755)
        (root / "README").write_text("same"); (seed / "README").write_text("same")
        dst.write_bytes(b"UNSIGNED"); os.chmod(dst, 0o775)
        before = cache.snapshot(root); keyed2 = {"lib/a.so": before["lib/a.so"]}
        assert cache.try_seed(seed, root, before, keyed2) == 1 and dst.read_bytes() == b"SEEDED" and stat.S_IMODE(dst.stat().st_mode) == 0o775, "种子放回必须保留暂存权限位"
        (seed / "README").write_text("different")
        dst.write_bytes(b"UNSIGNED"); before = cache.snapshot(root)
        assert cache.try_seed(seed, root, before, keyed2) == -1, "内容面不一致的种子必须整体拒用"
        # store():manifest 含键面快照,无 .tmp 残留
        sdir = d / "cache" / "k2"; sdir.mkdir(parents=True)
        cache.store(sdir, root, ["lib/a.so"], keyed2)
        man = json.loads((sdir / "manifest.json").read_text())
        assert man["files"] == ["lib/a.so"] and man.get("keyed") == keyed2 and not list(sdir.glob("*.tmp"))
    print("sign-payload-cached self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(run())
