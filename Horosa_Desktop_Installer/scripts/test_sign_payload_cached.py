#!/usr/bin/env python3
"""签名缓存层单元自测:命中/恢复/键失效三态。"""
import os, pathlib, shutil, subprocess, sys

BASE = pathlib.Path(os.environ.get("TMPDIR", "/tmp")) / "horosa-signcache-selftest"
SCRIPTS = pathlib.Path(__file__).resolve().parent

def fresh_tree():
    if BASE.exists():
        shutil.rmtree(BASE)
    (BASE / "tree/python/bin").mkdir(parents=True)
    (BASE / "tree/java/bin").mkdir(parents=True)
    (BASE / "cache").mkdir(parents=True)
    (BASE / "tree/python/bin/prog").write_text("AAA")
    (BASE / "tree/python/lib.dylib").write_text("LIB")
    (BASE / "tree/java/bin/java").write_text("JAVA")
    signer = BASE / "fake_signer.py"
    # 假 signer 必须暴露 is_macho / ARCHIVE_SUFFIXES —— 缓存层用它们把「签名真会碰的对象」
    # 挑进缓存键(白名单)。这里把 .bin 当作「Mach-O」以模拟真实结构。
    signer.write_text(
        "import sys, pathlib, random\n"
        "ARCHIVE_SUFFIXES = {'.jar', '.zip'}\n"
        "def is_macho(path):\n"
        "    return path.is_file() and not path.is_symlink() and path.suffix in ('.dylib', '.bin', '')\n"
        "if __name__ == '__main__':\n"
        "    root = pathlib.Path(sys.argv[1])\n"
        "    for p in sorted(root.rglob('*')):\n"
        "        if p.is_file() and 'java' not in p.relative_to(root).parts:\n"
        "            p.write_text(p.read_text().split('|')[0] + '|SIG' + str(random.randint(10**9, 10**10)))\n"
        "    print('fake signed')\n")
    return signer

def run(signer, identity="ID123"):
    r = subprocess.run(["/usr/bin/python3", str(SCRIPTS / "sign_payload_cached.py"),
                        str(signer), str(BASE / "tree"), identity, "", str(BASE / "cache")],
                       capture_output=True, text=True)
    return r.stdout.strip().splitlines()

def content():
    return ((BASE / "tree/python/bin/prog").read_text(),
            (BASE / "tree/python/lib.dylib").read_text(),
            (BASE / "tree/java/bin/java").read_text())

signer = fresh_tree()
ok = True

out1 = run(signer)
c1 = content()
print("① 首次:", [l for l in out1 if "sign-cache" in l][-1] if any("sign-cache" in l for l in out1) else out1)
print("   签后 prog =", c1[0])
assert "|SIG" in c1[0], "首次应真签"

# 复原到签名前状态,再跑一次 —— 应命中缓存,产物字节与首次完全相同
(BASE / "tree/python/bin/prog").write_text("AAA")
(BASE / "tree/python/lib.dylib").write_text("LIB")
out2 = run(signer)
c2 = content()
hit = any("命中" in l for l in out2)
print("② 同输入重跑:", "命中缓存 ✓" if hit else "未命中 ❌")
print("   产物 prog =", c2[0])
if not hit or c1 != c2:
    ok = False
    print("   ❌ 期望命中且产物字节恒等")
else:
    print("   ✅ 产物与首次逐字节恒等(签名不可复现被缓存抹平)")

# java 目录不该被签名脚本碰
if c2[2] != "JAVA":
    ok = False; print("   ❌ java 目录被误动")
else:
    print("   ✅ java 目录未被触碰(与 SKIP_DIR_NAMES 一致)")

# 换身份 ⇒ 键必须失效
(BASE / "tree/python/bin/prog").write_text("AAA")
(BASE / "tree/python/lib.dylib").write_text("LIB")
out3 = run(signer, identity="OTHER_ID")
miss = any("未命中" in l for l in out3)
print("③ 换签名身份:", "键失效、重新真签 ✓" if miss else "仍命中 ❌(危险)")
if not miss: ok = False

# 树内容变 ⇒ 键必须失效
(BASE / "tree/python/bin/prog").write_text("BBB")
(BASE / "tree/python/lib.dylib").write_text("LIB")
out4 = run(signer)
miss4 = any("未命中" in l for l in out4)
print("④ 树内容变化:", "键失效、重新真签 ✓" if miss4 else "仍命中 ❌(危险)")
if not miss4: ok = False


# ⑥ 与签名无关的易变文件(.jsa/.pyc 类)变化 ⇒ 键**不得**变(否则缓存永不命中,实测踩过两次)
(BASE / "tree/python/bin/prog").write_text("BBB")
(BASE / "tree/python/lib.dylib").write_text("LIB")
run(signer)                                   # 建基线
(BASE / "tree/python/bin/prog").write_text("BBB")
(BASE / "tree/python/lib.dylib").write_text("LIB")
(BASE / "tree/python/noise.jsa").write_text("DUMP" + str(id(object())))   # 每次都不同的无关档
out6 = run(signer)
hit6 = any("命中" in l for l in out6)
print("⑥ 无关易变档(.jsa)变化:", "键不受影响、仍命中 ✓" if hit6 else "键被污染、未命中 ❌")
if not hit6: ok = False


# ⑧ 只读目标档:命中后 restore 必须能覆盖(实测 libtcl8.6.dylib 等按 444 落盘,直接写会崩)
(BASE / "tree/python/bin/prog").write_text("RO-TEST")
(BASE / "tree/python/lib.dylib").write_text("LIB")
run(signer)                                    # 建缓存
(BASE / "tree/python/bin/prog").write_text("RO-TEST")
(BASE / "tree/python/lib.dylib").write_text("LIB")
os.chmod(BASE / "tree/python/bin/prog", 0o444)  # 目标置为只读
os.chmod(BASE / "tree/python/lib.dylib", 0o444)
out8 = run(signer)
hit8 = any("命中" in l for l in out8)
print("⑧ 只读目标档:", "命中且成功覆盖 ✓" if hit8 else "崩溃/未命中 ❌")
if not hit8: ok = False

# ⑦ kill-switch
os.environ["HOROSA_SIGN_CACHE"] = "0"
r = subprocess.run(["/usr/bin/python3", str(SCRIPTS / "sign_payload_cached.py"),
                    str(signer), str(BASE / "tree"), "ID123", "", str(BASE / "cache")],
                   capture_output=True, text=True, env={**os.environ})
print("⑦ kill-switch:", "旁路生效 ✓" if "已关闭" in r.stdout else "未旁路 ❌")
if "已关闭" not in r.stdout: ok = False

shutil.rmtree(BASE, ignore_errors=True)
print()
print("总判定:", "全部通过 ✅" if ok else "有失败 ❌")
sys.exit(0 if ok else 1)
