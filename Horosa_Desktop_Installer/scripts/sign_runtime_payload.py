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
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import prev_parts_modes   # 权限位单一来源

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

# 签名产物缓存的两个显式键输入(域级 sign_payload_cached.py 与下方单文件缓存共用):
#   · CODESIGN_ARGS_TEMPLATE —— codesign 的参数模板(身份之外的全部参数)。参数一变(加 entitlements / 改 options)缓存键自动变,
#     同内容文件不会再「命中」回放旧参数签出的字节;
#   · SIGNER_CACHE_EPOCH —— 签名语义代次。只在「签哪些文件 / 怎么签」的语义变化时手动升(纯重构、加注释、加日志不升);
#     此前键里掺的是本脚本全文 sha,任何一处改动都作废全部缓存 ⇒ 内容未变的 py-runtime(118 MB)整版重签重下(v3.11.2 实抓)。
CODESIGN_ARGS_TEMPLATE = ("codesign", "--force", "--timestamp", "--options", "runtime")
SIGNER_CACHE_EPOCH = "2"


def signer_cache_salt() -> str:
    """缓存键里代表「签名器」的那一份:参数模板 + 语义代次(不含脚本文本)。"""
    return " ".join(CODESIGN_ARGS_TEMPLATE) + "|epoch=" + SIGNER_CACHE_EPOCH


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


# ── 原生库签名按内容缓存 ────────────────────────────────────────────────
# codesign --timestamp 每次向 Apple 取时间戳 ⇒ 同字节同身份签出不同结果。域级缓存(sign_payload_cached.py)只在整个域
# 未变时命中;bundle 域每版都变(自家 jar 版本号)⇒ 10 个含原生库的三方 jar 每版重签 ⇒ java-lib 298.7 MB 每版必变(v3.11.1 实测)。
# 这里对「单个 Mach-O 文件」按其未签名内容 sha256(+ 身份)缓存签名产物:内容未变 ⇒ 直接写回上次的签名字节,jar 重打后逐字节恒等。
# 只缓存单文件(jar 内成员 / 树内散 Mach-O),不缓存 bundle 目录(其签名涉及整目录)。HOROSA_SIGN_CACHE=0 与域级缓存同开关。
def native_cache_dir(identity: str, create: bool = True) -> Optional[pathlib.Path]:
    """单文件缓存目录:按「身份 + codesign 参数模板 + 签名语义代次」分目录 —— 参数或语义一变,旧条目自然不可见。"""
    if os.environ.get("HOROSA_SIGN_CACHE", "1") != "1":
        return None
    root = os.environ.get("HOROSA_NATIVE_SIGN_CACHE", "").strip()
    if not root:
        return None
    ident = hashlib.sha256((identity + "\n" + signer_cache_salt()).encode("utf-8")).hexdigest()[:16]
    d = pathlib.Path(root) / ident
    if create:
        d.mkdir(parents=True, exist_ok=True)
    return d


_native_cache_dir = native_cache_dir   # 旧名保留(测试 / 外部脚本)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def native_cache_key(data: bytes, name: str) -> str:
    """缓存键 = sha256(文件基名 \0 未签名字节)。基名必须入键:codesign 缺省 identifier = 基名,
    两份同字节不同名的 Mach-O 签出的 CodeDirectory 不同,只按内容会把第二份写成第一份的签名。"""
    h = hashlib.sha256()
    h.update(pathlib.PurePath(name).name.encode("utf-8"))
    h.update(b"\0")
    h.update(data)
    return h.hexdigest()


def verify_signature(path: pathlib.Path) -> bool:
    """命中回放后的签名自校验(毫秒级):codesign --verify --strict。校验不过 = 缓存条目坏了(播种中断留下的截断档、
    别的参数签出的旧条目),交给调用方删条目回真签。"""
    return run("codesign", "--verify", "--strict", str(path)).returncode == 0


def write_cache_entry(dst: pathlib.Path, data: bytes) -> None:
    """缓存条目原子落盘(tmp + rename):中断不会留下半个 .signed 让后续命中写回坏字节。"""
    tmp = dst.with_name(dst.name + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(dst)


def sign_file_cached(path: pathlib.Path, identity: str, keychain: Optional[str]) -> str:
    """签单个 Mach-O 文件;回 'hit'(复用缓存字节)/ 'signed'(真签并入缓存)/ 'plain'(缓存未启用,真签)。
    命中产物必须过 verify_signature,不过则删条目、还原未签名字节、真签(计入 NATIVE_STATS['revoked'])。"""
    cache = native_cache_dir(identity)
    if cache is None:
        sign_path(path, identity, keychain)
        return "plain"
    raw = path.read_bytes()
    cached = cache / (native_cache_key(raw, path.name) + ".signed")
    if cached.is_file():
        path.write_bytes(cached.read_bytes())
        if verify_signature(path):
            return "hit"
        NATIVE_STATS["revoked"] = NATIVE_STATS.get("revoked", 0) + 1
        try:
            cached.unlink()
        except OSError:
            pass
        path.write_bytes(raw)
    sign_path(path, identity, keychain)
    write_cache_entry(cached, path.read_bytes())
    return "signed"


def seed_native_cache(unsigned_lib_dir: pathlib.Path, signed_lib_dir: pathlib.Path, identity: str) -> dict:
    """用已发布(已签名)的 jar 目录为单文件缓存播种:同名 jar 里同名 Mach-O 成员,键 = 未签名成员(基名 + 字节),
    值 = 已签名成员字节。签名器用同一个键函数,下次打包同内容成员直接命中 ⇒ java-lib 部件与已发布的逐字节恒等。
    回 {'pairs','seeded','skipped'};缓存未启用回 {'disabled': True}。"""
    cache = native_cache_dir(identity)
    if cache is None:
        return {"disabled": True}
    stats = {"pairs": 0, "seeded": 0, "skipped": 0}
    for unsigned_jar in sorted(pathlib.Path(unsigned_lib_dir).glob("*.jar")):
        signed_jar = pathlib.Path(signed_lib_dir) / unsigned_jar.name
        if not signed_jar.is_file():
            continue
        try:
            with zipfile.ZipFile(unsigned_jar) as uz, zipfile.ZipFile(signed_jar) as sz:
                snames = set(sz.namelist())
                for m in uz.namelist():
                    if m.endswith("/") or m not in snames:
                        continue
                    ub = uz.read(m)
                    if not _is_macho_bytes(ub, m):
                        continue
                    sb = sz.read(m)
                    if not _is_macho_bytes(sb, m):
                        stats["skipped"] += 1
                        continue
                    stats["pairs"] += 1
                    dst = cache / (native_cache_key(ub, m) + ".signed")
                    if not dst.exists():
                        write_cache_entry(dst, sb)
                        stats["seeded"] += 1
        except (OSError, zipfile.BadZipFile):
            stats["skipped"] += 1
    return stats


def _is_macho_bytes(b: bytes, name: str = "") -> bool:
    """与 is_macho 同判据的字节版(jar 成员在内存里判):thin 魔数;fat(CAFEBABE)与 Java .class 同魔数,只认 nfat_arch ≤ 32。"""
    if len(b) < 8 or name.endswith(".class"):
        return False
    if b[:4] in MACHO_MAGICS:
        return True
    if b[:4] == FAT_MAGIC_BIG:
        return 0 < struct.unpack(">I", b[4:8])[0] <= 32
    if b[:4] == FAT_MAGIC_LITTLE:
        return 0 < struct.unpack("<I", b[4:8])[0] <= 32
    return False


def sign_path(path: pathlib.Path, identity: str, keychain: Optional[str]) -> None:
    cmd = list(CODESIGN_ARGS_TEMPLATE) + ["--sign", identity]
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
    # 重建后的 jar 权限位按单一来源(prev_parts_modes):上一版部件 tar 头留档优先,留档没有的保留 jar 原有的位。
    # 此前 NamedTemporaryFile 建的临时档是 0600,replace 后 jar 就成 0600(与域级缓存命中保留的 0644 口径相反)。
    staged_mode = archive_path.stat().st_mode & 0o7777
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
        prev_parts_modes.apply_mode(archive_path, staged_mode)
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
    parser.add_argument("--seed-native-from", default="", help="只播种不签名:已签名的 BOOT-INF/lib 目录(上一版部件),root 须指向未签名的同名 jar 目录")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"runtime root not found: {root}")

    if args.seed_native_from:
        stats = seed_native_cache(root, pathlib.Path(args.seed_native_from).resolve(), args.identity)
        print("[native-sign-cache] 播种: %s" % (", ".join("%s=%s" % kv for kv in sorted(stats.items())) or "-"), flush=True)
        return 0

    for archive in iter_archive_files(root):
        process_archive(archive, args.identity, args.keychain or None)

    for macho in iter_macho_files(root):
        outcome = sign_file_cached(macho, args.identity, args.keychain or None)
        NATIVE_STATS[outcome] = NATIVE_STATS.get(outcome, 0) + 1

    for bundle in iter_bundle_dirs(root):
        sign_path(bundle, args.identity, args.keychain or None)

    if NATIVE_STATS:
        print("[native-sign-cache] 单文件 Mach-O:命中复用 %d · 真签入缓存 %d · 未启用缓存 %d · 命中校验失败回真签 %d" % (
            NATIVE_STATS.get("hit", 0), NATIVE_STATS.get("signed", 0), NATIVE_STATS.get("plain", 0), NATIVE_STATS.get("revoked", 0)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
