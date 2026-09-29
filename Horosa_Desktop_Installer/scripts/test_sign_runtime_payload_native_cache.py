#!/usr/bin/env python3
"""[#71 / FL-20260923-1] 单文件原生库签名按内容缓存的判别向量(不真签:把 sign_path 换成「追加伪签名字节」)。
① 同内容第二次 → hit,产物字节与第一次逐字节相同(时间戳漂移被缓存吸收);② 内容不同 → 各自真签,互不串;
③ HOROSA_SIGN_CACHE=0 → plain(不读不写缓存);④ 未设缓存目录 → plain;⑤ 不同身份不共用缓存。"""
import os, pathlib, sys, tempfile, importlib.util

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

def run():
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        os.environ["HOROSA_NATIVE_SIGN_CACHE"] = str(d / "cache")
        os.environ["HOROSA_SIGN_CACHE"] = "1"
        a1 = d / "a1.dylib"; a1.write_bytes(b"MACHO-A")
        assert mod.sign_file_cached(a1, "ID-1", None) == "signed"
        first = a1.read_bytes()
        a2 = d / "a2.dylib"; a2.write_bytes(b"MACHO-A")
        assert mod.sign_file_cached(a2, "ID-1", None) == "hit", "同内容第二次必须命中"
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
    print("native-sign-cache self-test OK")
    return 0

if __name__ == "__main__":
    sys.exit(run())
