#!/usr/bin/env python3
"""签名种子自动准备:把上一版构建留在 dist/components/ 里的部件(发布后与线上逐字节相同)按原权限解到
build/.sign-seed/,供本次签名复用 —— 内容未变的部件当版即与线上恒等,不再靠人记「打包前手动设种子」。

  · py-runtime 部件 → build/.sign-seed/runtime-payload/runtime/mac/python(域级缓存 sign_payload_cached.py 的
    HOROSA_SIGN_SEED_DIR 指向 …/runtime/mac);
  · java-lib 部件 → build/.sign-seed/java-lib/BOOT-INF/lib/*.jar(单文件缓存播种 sign_runtime_payload.py --seed-native-from)。

🔴 必须按 tar 头里的权限位解(tarfile filter='fully_trusted';'tar' / 'data' 过滤器会清掉 group/other 写位):
v3.11.2 实抓:种子用 `tar -xzf`(不带 -p)解出,umask 把 74 个 .so 从 0775 降成 0755,种子「命中」了部件 sha 仍漂。
解完逐条目核对权限 / 大小,任一不符即整体拒用(exit 3),绝不半用。

同时把上一版全部「稳定部件」(py-runtime / jdk-runtime / ephe-data / xuanshi-data / java-lib)的 tar 头(名 / 类型 / 大小 /
权限 / mtime / 链接目标)与 components-lock.json 留档到 build/.sign-seed/prev-parts-headers.json / prev-components-lock.json,
供打包末尾 verify_stable_parts_headers.py 在包内就做「与上一版逐条目头部对拍」,不等包后核验才发现部件漂了。

用法: prepare_sign_seed.py <installer_root>   → 标准输出三行 `python_seed=<dir|->` / `javalib_seed=<dir|->` / `prev_headers=<file|->`
"""
import json
import os
import pathlib
import shutil
import stat
import sys
import tarfile

PY_RUNTIME_TAR = "horosa-comp-py-runtime-macos-arm64.tar.gz"
JAVA_LIB_TAR = "horosa-comp-java-lib-macos-arm64.tar.gz"
# 与 publish 差分门(I4)同一份「稳定部件」清单:内容未变时每版必须与上一版逐字节恒等
STABLE_PARTS = ("py-runtime", "jdk-runtime", "ephe-data", "xuanshi-data", "java-lib")
PREV_HEADERS_NAME = "prev-parts-headers.json"
PREV_LOCK_NAME = "prev-components-lock.json"


def part_tar_name(part: str) -> str:
    return f"horosa-comp-{part}-macos-arm64.tar.gz"


def tar_headers(tar_path: pathlib.Path) -> list:
    """tar 头逐条目 [name, type, size, mode, mtime, linkname](不读内容;gz 解压流一遍)。"""
    out = []
    with tarfile.open(tar_path, "r:gz") as tf:
        for m in tf:
            out.append([m.name, m.type.decode("latin-1") if isinstance(m.type, bytes) else str(m.type),
                        int(m.size), int(m.mode & 0o7777), int(m.mtime), m.linkname or ""])
    return out


def dump_prev_headers(comp_dir: pathlib.Path, seed_root: pathlib.Path) -> str:
    """上一版稳定部件的 tar 头 + components-lock 留档;没有任何部件回 '-'。"""
    headers = {}
    for part in STABLE_PARTS:
        t = comp_dir / part_tar_name(part)
        if t.is_file():
            headers[part] = tar_headers(t)
    if not headers:
        return "-"
    seed_root.mkdir(parents=True, exist_ok=True)
    out = seed_root / PREV_HEADERS_NAME
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(json.dumps(headers, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    tmp.replace(out)
    lock = comp_dir / "components-lock.json"
    if lock.is_file():
        shutil.copyfile(lock, seed_root / PREV_LOCK_NAME)
    print(f"[sign-seed] 上一版稳定部件头部留档:{', '.join(f'{k}={len(v)}' for k, v in headers.items())} 条目 → {out}",
          file=sys.stderr, flush=True)
    return str(out)


def _extract_preserving_modes(tar_path: pathlib.Path, dst: pathlib.Path) -> int:
    """解包并逐条目核对权限位 / 大小与 tar 头一致;回条目数。"""
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    with tarfile.open(tar_path, "r:gz") as tf:
        try:
            tf.extractall(dst, filter="fully_trusted")
        except TypeError:  # 旧 Python 无 filter 形参:缺省即 fully_trusted 语义
            tf.extractall(dst)
    n = 0
    with tarfile.open(tar_path, "r:gz") as tf:
        for m in tf:
            p = dst / m.name
            st = os.lstat(p)
            n += 1
            if stat.S_IMODE(st.st_mode) != (m.mode & 0o7777) and not m.issym():
                raise SystemExit(f"seed 权限位不符: {m.name} tar={oct(m.mode & 0o7777)} disk={oct(stat.S_IMODE(st.st_mode))}")
            if m.isreg() and st.st_size != m.size:
                raise SystemExit(f"seed 大小不符: {m.name}")
    return n


def prepare(installer_root: pathlib.Path) -> dict:
    comp = installer_root / "dist" / "components"
    seed_root = installer_root / "build" / ".sign-seed"
    out = {"python_seed": "-", "javalib_seed": "-", "prev_headers": "-"}
    try:
        out["prev_headers"] = dump_prev_headers(comp, seed_root)
    except (OSError, tarfile.TarError) as e:  # 留档失败只影响包内对拍,不影响种子
        print(f"[sign-seed] 上一版部件头部留档失败(忽略):{e}", file=sys.stderr, flush=True)
    py_tar = comp / PY_RUNTIME_TAR
    if py_tar.is_file():
        dst = seed_root / "py-runtime"
        n = _extract_preserving_modes(py_tar, dst)
        mac = dst / "runtime-payload" / "runtime" / "mac"
        if (mac / "python").is_dir():
            out["python_seed"] = str(mac)
            print(f"[sign-seed] py-runtime 种子就绪:{n} 条目,权限 / 大小逐条核对一致 → {mac}", file=sys.stderr, flush=True)
    lib_tar = comp / JAVA_LIB_TAR
    if lib_tar.is_file():
        dst = seed_root / "java-lib"
        n = _extract_preserving_modes(lib_tar, dst)
        libs = list(dst.rglob("BOOT-INF/lib"))
        if libs and libs[0].is_dir():
            out["javalib_seed"] = str(libs[0])
            print(f"[sign-seed] java-lib 种子就绪:{n} 条目 → {libs[0]}", file=sys.stderr, flush=True)
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: prepare_sign_seed.py <installer_root>", file=sys.stderr)
        return 2
    root = pathlib.Path(sys.argv[1]).resolve()
    if not (root / "dist").is_dir():
        print("python_seed=-\njavalib_seed=-\nprev_headers=-")
        return 0
    out = prepare(root)
    print(f"python_seed={out['python_seed']}\njavalib_seed={out['javalib_seed']}\nprev_headers={out['prev_headers']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
