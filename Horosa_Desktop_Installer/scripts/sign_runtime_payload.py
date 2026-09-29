#!/usr/bin/env python3
import argparse
import os
import pathlib
import shutil
import struct
import subprocess
import tempfile
import zipfile
import hashlib

NATIVE_STATS: dict = {}
from typing import Optional


ARCHIVE_SUFFIXES = {".jar", ".zip"}
BUNDLE_SUFFIXES = {".app", ".framework", ".bundle"}
MACHO_MAGICS = {
    b"\xfe\xed\xfa\xce",
    b"\xce\xfa\xed\xfe",
    b"\xfe\xed\xfa\xcf",
    b"\xcf\xfa\xed\xfe",
}
FAT_MAGIC_BIG = b"\xca\xfe\xba\xbe"
FAT_MAGIC_LITTLE = b"\xbe\xba\xfe\xca"
SKIP_DIR_NAMES = {"java"}


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")


def run_checked(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)


def is_macho(path: pathlib.Path) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    try:
        with path.open("rb") as handle:
            header = handle.read(8)
    except OSError:
        return False
    if len(header) < 4:
        return False
    magic = header[:4]
    if magic in MACHO_MAGICS:
        return True
    if len(header) < 8:
        return False
    if magic == FAT_MAGIC_BIG:
        nfat_arch = struct.unpack(">I", header[4:8])[0]
        return 0 < nfat_arch <= 32
    if magic == FAT_MAGIC_LITTLE:
        nfat_arch = struct.unpack("<I", header[4:8])[0]
        return 0 < nfat_arch <= 32
    return False


# ── [FL-20260923-1 / #71] 原生库签名按内容缓存 ────────────────────────────────────────────────
# codesign --timestamp 每次向 Apple 取时间戳 ⇒ 同字节同身份签出不同结果。域级缓存(sign_payload_cached.py)只在整个域
# 未变时命中;bundle 域每版都变(自家 jar 版本号)⇒ 10 个含原生库的三方 jar 每版重签 ⇒ java-lib 298.7 MB 每版必变(v3.11.1 实测)。
# 这里对「单个 Mach-O 文件」按其未签名内容 sha256(+ 身份)缓存签名产物:内容未变 ⇒ 直接写回上次的签名字节,jar 重打后逐字节恒等。
# 只缓存单文件(jar 内成员 / 树内散 Mach-O),不缓存 bundle 目录(其签名涉及整目录)。HOROSA_SIGN_CACHE=0 与域级缓存同开关。
def _native_cache_dir(identity: str) -> Optional[pathlib.Path]:
    if os.environ.get("HOROSA_SIGN_CACHE", "1") != "1":
        return None
    root = os.environ.get("HOROSA_NATIVE_SIGN_CACHE", "").strip()
    if not root:
        return None
    ident = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    d = pathlib.Path(root) / ident
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sign_file_cached(path: pathlib.Path, identity: str, keychain: Optional[str]) -> str:
    """签单个 Mach-O 文件;回 'hit'(复用缓存字节)/ 'signed'(真签并入缓存)/ 'plain'(缓存未启用,真签)。"""
    cache = _native_cache_dir(identity)
    if cache is None:
        sign_path(path, identity, keychain)
        return "plain"
    key = _sha256_bytes(path.read_bytes())
    cached = cache / (key + ".signed")
    if cached.is_file():
        path.write_bytes(cached.read_bytes())
        return "hit"
    sign_path(path, identity, keychain)
    tmp = cached.with_suffix(".tmp")
    tmp.write_bytes(path.read_bytes())
    tmp.replace(cached)
    return "signed"


def sign_path(path: pathlib.Path, identity: str, keychain: Optional[str]) -> None:
    cmd = [
        "codesign",
        "--force",
        "--timestamp",
        "--options",
        "runtime",
        "--sign",
        identity,
    ]
    if keychain:
        cmd.extend(["--keychain", keychain])
    cmd.append(str(path))
    run_checked(*cmd)


def should_skip(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    return any(part in SKIP_DIR_NAMES for part in relative.parts)


def iter_bundle_dirs(root: pathlib.Path) -> list[pathlib.Path]:
    bundles: list[pathlib.Path] = []
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        if should_skip(path, root):
            continue
        if any(part == "_CodeSignature" for part in path.parts):
            continue
        if path.suffix in BUNDLE_SUFFIXES or (path / "Contents/Info.plist").is_file() or (path / "Resources/Info.plist").is_file():
            bundles.append(path)
    # 域根自身也可能是框架内容根(如 python 域根带 Resources/Info.plist):整树调用时它作为
    # 子目录被枚举到,按域调用时 rglob 不含根自身 → 必须显式纳入,否则 bundle 级签名缺失,
    # 主二进制只剩裸文件签名 → 公证判 "signature of the binary is invalid"(v3.8.1 分域首打实案)。
    # 整树调用(root=runtime/mac 容器,无 Info.plist)不受影响。
    if root.suffix in BUNDLE_SUFFIXES or (root / "Contents/Info.plist").is_file() or (root / "Resources/Info.plist").is_file():
        bundles.append(root)
    bundles.sort(key=lambda item: (len(item.parts), str(item)), reverse=True)
    return bundles


def iter_archive_files(root: pathlib.Path) -> list[pathlib.Path]:
    archives: list[pathlib.Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        if should_skip(path, root):
            continue
        if any(part == "_CodeSignature" for part in path.parts):
            continue
        if path.suffix.lower() in ARCHIVE_SUFFIXES:
            archives.append(path)
    return sorted(archives)


def iter_macho_files(root: pathlib.Path) -> list[pathlib.Path]:
    machos: list[pathlib.Path] = []
    for path in root.rglob("*"):
        if should_skip(path, root):
            continue
        if any(part == "_CodeSignature" for part in path.parts):
            continue
        if path.suffix.lower() in ARCHIVE_SUFFIXES:
            continue
        if is_macho(path):
            machos.append(path)
    machos.sort(key=lambda item: (len(item.parts), str(item)), reverse=True)
    return machos


def rebuild_archive_from_tree(archive_path: pathlib.Path, tree_root: pathlib.Path) -> None:
    with zipfile.ZipFile(archive_path) as source:
        infos = source.infolist()
    with tempfile.NamedTemporaryFile(dir=str(archive_path.parent), delete=False) as tmp_file:
        tmp_name = pathlib.Path(tmp_file.name)
    try:
        with zipfile.ZipFile(tmp_name, "w") as target:
            for info in infos:
                new_info = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                new_info.compress_type = info.compress_type
                new_info.comment = info.comment
                new_info.create_system = info.create_system
                new_info.create_version = info.create_version
                new_info.extract_version = info.extract_version
                new_info.flag_bits = info.flag_bits
                new_info.volume = info.volume
                new_info.internal_attr = info.internal_attr
                new_info.external_attr = info.external_attr
                new_info.extra = info.extra
                extracted = tree_root / info.filename
                if info.is_dir():
                    target.writestr(new_info, b"")
                else:
                    target.writestr(new_info, extracted.read_bytes())
        tmp_name.replace(archive_path)
    finally:
        if tmp_name.exists():
            tmp_name.unlink()


def process_archive(archive_path: pathlib.Path, identity: str, keychain: Optional[str]) -> bool:
    changed = False
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = pathlib.Path(tmp_dir)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(tmp_root)

        for nested in iter_archive_files(tmp_root):
            if process_archive(nested, identity, keychain):
                changed = True

        for macho in iter_macho_files(tmp_root):
            outcome = sign_file_cached(macho, identity, keychain)
            NATIVE_STATS[outcome] = NATIVE_STATS.get(outcome, 0) + 1
            changed = True

        for bundle in iter_bundle_dirs(tmp_root):
            sign_path(bundle, identity, keychain)
            changed = True

        if changed:
            rebuild_archive_from_tree(archive_path, tmp_root)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Developer ID sign all macOS binaries inside the staged runtime payload.")
    parser.add_argument("root", help="Path to staged runtime/mac directory")
    parser.add_argument("--identity", required=True, help="Developer ID Application signing identity or certificate hash")
    parser.add_argument("--keychain", default=os.environ.get("APPLE_SIGNING_KEYCHAIN", ""), help="Keychain path for signing identity lookup")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"runtime root not found: {root}")

    for archive in iter_archive_files(root):
        process_archive(archive, args.identity, args.keychain or None)

    for macho in iter_macho_files(root):
        outcome = sign_file_cached(macho, args.identity, args.keychain or None)
        NATIVE_STATS[outcome] = NATIVE_STATS.get(outcome, 0) + 1

    for bundle in iter_bundle_dirs(root):
        sign_path(bundle, args.identity, args.keychain or None)

    if NATIVE_STATS:
        print("[native-sign-cache] 单文件 Mach-O:命中复用 %d · 真签入缓存 %d · 未启用缓存 %d" % (
            NATIVE_STATS.get("hit", 0), NATIVE_STATS.get("signed", 0), NATIVE_STATS.get("plain", 0)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
