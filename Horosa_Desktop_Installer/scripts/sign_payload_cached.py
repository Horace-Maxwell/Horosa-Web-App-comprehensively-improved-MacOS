#!/usr/bin/env python3
"""[FL-20260804-1 修三] 签名产物缓存层(horosa_repro_sign_cache_v1)。

问题:`sign_runtime_payload.py` 用 `codesign --force --timestamp --options runtime`,
`--timestamp` 每次向 Apple 时间戳服务器请求 ⇒ **同一份字节、同一身份,签出来也每次不同**。
实测:py-runtime 两次打包 219 个文件内容变(187 .so + 26 .dylib + Python 主程序 +
bin/python3.12* + _CodeSignature/CodeResources),导致 113MB 部件每版被判「变了」全量重下。
`--timestamp` 不能去掉——公证强制要求安全时间戳,去掉必然公证失败。

做法:本脚本包在原签名脚本外面(原脚本一行不改),
  ① 签名前给待签树做文件级 sha 快照(排除 java/ —— 原脚本 SKIP_DIR_NAMES 跳过它);
  ② 用「快照 + 签名身份 + 原脚本自身 sha + 本脚本自身 sha」算缓存键;
  ③ 命中 ⇒ 把缓存里的签名后文件逐一拷回,跳过 codesign(省数分钟且产物字节恒等);
  ④ 未命中 ⇒ 调原脚本真签,再对比签名前后快照、把**发生变化的文件**存进缓存。

安全性:复用的签名与重签的唯一差别只是时间戳时刻——同身份、同参数、对同一字节内容签出。
任一输入变化(树内容/身份/任一脚本)都会改变缓存键而不命中。Apple 时间戳证书有效期很长,
且公证针对的是每次新产出的 .pkg;Gatekeeper 校验签名有效性而非新鲜度。发布链的
`stapler validate` + `spctl` + 离线 pkg 真装 e2e 三道门是这条的实测背书。

kill-switch:HOROSA_SIGN_CACHE=0 ⇒ 完全旁路(每次真签,行为与本脚本引入前逐字节一致)。
"""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys

SKIP_DIR_NAMES = {"java"}  # 与 sign_runtime_payload.py 的 SKIP_DIR_NAMES 保持一致
CACHE_KEEP = 2             # 只保留最近 N 个键的缓存(构建机磁盘友好)

# 🔴 缓存键只能纳入「签名真会碰的文件」。任何与签名结果无关、又本身不可复现的文件混进键,
# 都会让键每次都变、缓存永不命中。实测连踩两次:
#   ① `.app-cds.jsa`(CDS 预置档,在签名前落进待签树)每次 dump 都不同;
#   ② 打包现场 precompile 的 `.pyc` 里也有内容会变的个例。
# 两次都表现为「键 A→B 每次不同、py-runtime 照旧每版重下」。
# 正解不是逐类拉黑,而是**白名单**:键只纳入原签名脚本三个枚举器会选中的对象
# (Mach-O 文件 + .jar/.zip 归档)。判定直接从原脚本动态 import,永远同源不漂。
KEY_EXCLUDE_SUFFIXES = (".jsa",)  # 保留:即便未来白名单放宽,这类档也永不入键


def _sha_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _skipped(rel: pathlib.PurePath) -> bool:
    return any(part in SKIP_DIR_NAMES for part in rel.parts)


def snapshot(root: pathlib.Path) -> dict:
    """待签树的文件级快照:{相对路径: sha}。符号链接按其目标路径字符串记账(签名不改链接)。"""
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            p = pathlib.Path(dirpath) / fn
            rel = p.relative_to(root)
            if _skipped(rel):
                continue
            try:
                if p.is_symlink():
                    out[str(rel)] = "L:" + os.readlink(p)
                elif p.is_file():
                    out[str(rel)] = _sha_file(p)
            except OSError:
                pass
    return out


def load_signer_module(signer_path: str):
    """动态载入原签名脚本,复用它的 is_macho / ARCHIVE_SUFFIXES —— 判定永远与真实签名同源。
    载入失败或符号缺失一律返回 None ⇒ 键退回「全量(除 .jsa)」的保守形态:可能少命中,
    但绝不误命中、更不会让打包崩。"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("horosa_signer", signer_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if callable(getattr(mod, "is_macho", None)) and getattr(mod, "ARCHIVE_SUFFIXES", None):
            return mod
    except Exception as exc:  # noqa: BLE001 —— 任何异常都退保守路径,不阻断打包
        print(f"[sign-cache] 载入签名脚本判定失败({exc!r}),键退回保守全量形态", flush=True)
        return None
    print("[sign-cache] 签名脚本缺 is_macho/ARCHIVE_SUFFIXES,键退回保守全量形态", flush=True)
    return None


def key_relevant(snap: dict, root: pathlib.Path, signer_mod) -> dict:
    """键只纳入签名真会碰的对象:Mach-O 文件 + .jar/.zip 归档(白名单,见上方注释)。
    signer_mod 为 None(判定不可用)时退回保守全量形态。"""
    out = {}
    for rel, val in snap.items():
        if rel.endswith(KEY_EXCLUDE_SUFFIXES) or val.startswith("L:"):
            continue
        if signer_mod is None:
            out[rel] = val
            continue
        p = root / rel
        if p.suffix.lower() in signer_mod.ARCHIVE_SUFFIXES or signer_mod.is_macho(p):
            out[rel] = val
    return out


def cache_key(snap: dict, identity: str, extra_files: list) -> str:
    h = hashlib.sha256()
    h.update(b"horosa_repro_sign_cache_v1\n")
    h.update(identity.encode("utf-8") + b"\n")
    for f in extra_files:
        try:
            h.update(_sha_file(pathlib.Path(f)).encode("ascii") + b"\n")
        except OSError:
            h.update(b"missing\n")
    for rel in sorted(snap):
        h.update(rel.encode("utf-8") + b"\0" + snap[rel].encode("utf-8") + b"\n")
    return h.hexdigest()


def _unlink_force(path: pathlib.Path) -> None:
    """摘掉目标档(含只读档);不存在则静默。"""
    try:
        if path.is_symlink() or path.exists():
            try:
                path.unlink()
            except PermissionError:
                os.chmod(path, 0o644)
                path.unlink()
    except OSError:
        pass


def restore(cache_dir: pathlib.Path, root: pathlib.Path) -> int:
    """把缓存里的签名后文件拷回原位。返回恢复文件数;任一缺失即返回 -1(视为未命中)。"""
    manifest = json.loads((cache_dir / "manifest.json").read_text())
    files = manifest["files"]
    for rel in files:
        src = cache_dir / "files" / rel
        if not src.is_file():
            return -1
    n = 0
    for rel in files:
        src = cache_dir / "files" / rel
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        # 🔴 目标可能是只读档(实测 libtcl8.6.dylib 等按 444 落盘),直接 open(dst,'wb') 会
        # PermissionError 崩掉整个打包。先摘掉旧档再拷(copy2 会带回源的权限位)。
        _unlink_force(dst)
        shutil.copy2(src, dst)
        n += 1
    return n


def store(cache_dir: pathlib.Path, root: pathlib.Path, changed: list) -> None:
    files_dir = cache_dir / "files"
    for rel in changed:
        src = root / rel
        if not src.is_file() or src.is_symlink():
            continue
        dst = files_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    (cache_dir / "manifest.json").write_text(
        json.dumps({"version": 1, "files": changed}, ensure_ascii=False, indent=1) + "\n")


def prune(cache_root: pathlib.Path, keep: int) -> None:
    try:
        dirs = [d for d in cache_root.iterdir() if d.is_dir() and (d / "manifest.json").is_file()]
    except OSError:
        return
    dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    for d in dirs[keep:]:
        shutil.rmtree(d, ignore_errors=True)


def main() -> int:
    if len(sys.argv) < 5:
        print("usage: sign_payload_cached.py <signer.py> <root> <identity> <keychain> <cache_root>", file=sys.stderr)
        return 2
    signer, root_s, identity, keychain, cache_root_s = sys.argv[1:6]
    root = pathlib.Path(root_s).resolve()
    cache_root = pathlib.Path(cache_root_s)

    def real_sign():
        cmd = ["/usr/bin/python3", signer, str(root), "--identity", identity]
        if keychain:
            cmd += ["--keychain", keychain]
        subprocess.run(cmd, check=True)

    if os.environ.get("HOROSA_SIGN_CACHE", "1") != "1":
        print("[sign-cache] 已关闭(HOROSA_SIGN_CACHE=0),走原始每次真签路径", flush=True)
        real_sign()
        return 0

    before = snapshot(root)
    signer_mod = load_signer_module(signer)
    keyed = key_relevant(before, root, signer_mod)
    key = cache_key(keyed, identity, [signer, __file__])
    cache_dir = cache_root / key
    print(f"[sign-cache] key={key[:16]} 签名面 {len(keyed)} 个 Mach-O/归档"
          f"(树内共 {len(before)} 文件,其余与签名无关不入键)", flush=True)

    if (cache_dir / "manifest.json").is_file():
        n = restore(cache_dir, root)
        if n >= 0:
            os.utime(cache_dir, None)  # 刷新 LRU 时间戳
            print(f"[sign-cache] ✅ 命中,复用签名产物 {n} 个文件(跳过 codesign;产物字节与上次恒等)", flush=True)
            return 0
        print("[sign-cache] 缓存残缺,回退真签", flush=True)

    print("[sign-cache] 未命中,执行真实签名…", flush=True)
    real_sign()
    after = snapshot(root)
    changed = sorted(rel for rel, sha in after.items()
                     if before.get(rel) != sha and not sha.startswith("L:"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    store(cache_dir, root, changed)
    prune(cache_root, CACHE_KEEP)
    print(f"[sign-cache] 已缓存签名产物 {len(changed)} 个文件 → {cache_dir.name[:16]}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
