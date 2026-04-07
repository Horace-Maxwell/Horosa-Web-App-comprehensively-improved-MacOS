#!/usr/bin/env python3
import argparse
import os
import pathlib
import shutil
import struct
import subprocess
import tempfile
import zipfile
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
            sign_path(macho, identity, keychain)
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
        sign_path(macho, args.identity, args.keychain or None)

    for bundle in iter_bundle_dirs(root):
        sign_path(bundle, args.identity, args.keychain or None)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
