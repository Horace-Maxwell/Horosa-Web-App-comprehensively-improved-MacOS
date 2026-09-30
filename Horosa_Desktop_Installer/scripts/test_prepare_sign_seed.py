#!/usr/bin/env python3
"""签名种子自动准备的判别向量:① 0775 / 0444 / 0755 三种权限位解出来逐一保留(umask 不介入);
② 输出两个种子目录(python 域根 = …/runtime/mac;java-lib = …/BOOT-INF/lib);③ 没有上一版部件 → 两行都是 `-`;
④ 重复运行清旧种子;⑤ 上一版稳定部件的 tar 头与 lock 留档到 build/.sign-seed。"""
import io
import os
import pathlib
import stat
import subprocess
import sys
import tarfile
import tempfile

HERE = pathlib.Path(__file__).resolve().parent


def add(tf, name, data, mode):
    ti = tarfile.TarInfo(name)
    ti.size = len(data)
    ti.mode = mode
    ti.mtime = 1700000000
    tf.addfile(ti, io.BytesIO(data))


def run():
    old_umask = os.umask(0o022)   # 让「解包丢权限」在本机也复现得出来
    try:
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "dist" / "components").mkdir(parents=True)
            with tarfile.open(root / "dist" / "components" / "horosa-comp-py-runtime-macos-arm64.tar.gz", "w:gz") as tf:
                add(tf, "runtime-payload/runtime/mac/python/lib/_struct.so", b"MACHO", 0o775)
                add(tf, "runtime-payload/runtime/mac/python/lib/libtcl.dylib", b"MACHO", 0o444)
                add(tf, "runtime-payload/runtime/mac/python/bin/python3", b"MACHO", 0o755)
            with tarfile.open(root / "dist" / "components" / "horosa-comp-java-lib-macos-arm64.tar.gz", "w:gz") as tf:
                add(tf, "runtime-payload/runtime/mac/bundle/boot-exploded/BOOT-INF/lib/jna-5.jar", b"PK", 0o664)
            (root / "dist" / "components" / "components-lock.json").write_text('{"components":[]}')
            r = subprocess.run([sys.executable, str(HERE / "prepare_sign_seed.py"), str(root)], capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            lines = dict(l.split("=", 1) for l in r.stdout.strip().splitlines())
            py = pathlib.Path(lines["python_seed"]); lib = pathlib.Path(lines["javalib_seed"])
            assert py.name == "mac" and (py / "python").is_dir(), lines
            assert lib.name == "lib" and (lib / "jna-5.jar").is_file(), lines
            for rel, mode in (("python/lib/_struct.so", 0o775), ("python/lib/libtcl.dylib", 0o444), ("python/bin/python3", 0o755)):
                got = stat.S_IMODE((py / rel).stat().st_mode)
                assert got == mode, f"① {rel} 权限位应为 {oct(mode)},实得 {oct(got)}"
            assert stat.S_IMODE((lib / "jna-5.jar").stat().st_mode) == 0o664
            # ⑤ 上一版稳定部件头部 + lock 留档(供打包末尾 verify_stable_parts_headers.py 包内对拍)
            import json
            ph = pathlib.Path(lines["prev_headers"])
            assert ph.is_file() and ph.name == "prev-parts-headers.json", lines
            hdr = json.loads(ph.read_text())
            assert set(hdr) == {"py-runtime", "java-lib"} and len(hdr["py-runtime"]) == 3 and len(hdr["java-lib"]) == 1, hdr
            assert hdr["py-runtime"][0][0].endswith("_struct.so") and hdr["py-runtime"][0][3] == 0o775, hdr["py-runtime"][0]
            assert (ph.parent / "prev-components-lock.json").read_text() == '{"components":[]}', "lock 应原样留档"
            # ④ 重复运行:旧种子清掉重解(留一个脏文件验证)
            junk = py / "python" / "junk"; junk.write_text("x")
            r = subprocess.run([sys.executable, str(HERE / "prepare_sign_seed.py"), str(root)], capture_output=True, text=True)
            assert r.returncode == 0 and not junk.exists(), "重复运行必须清掉旧种子"
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d); (root / "dist" / "components").mkdir(parents=True)
            r = subprocess.run([sys.executable, str(HERE / "prepare_sign_seed.py"), str(root)], capture_output=True, text=True)
            assert r.returncode == 0 and r.stdout.strip() == "python_seed=-\njavalib_seed=-\nprev_headers=-", r.stdout
    finally:
        os.umask(old_umask)
    print("prepare-sign-seed self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(run())
