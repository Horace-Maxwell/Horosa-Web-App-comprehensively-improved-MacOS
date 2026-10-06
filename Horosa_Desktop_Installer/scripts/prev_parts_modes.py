#!/usr/bin/env python3
"""签名产物放回暂存树时「权限位以谁为准」的单一来源(两层签名缓存共用)。

病理(v3.11.3 打包实抓):域级缓存命中时 `_put_signed` 保留的是**暂存文件**的位(Maven 产物
0644);单文件缓存播种 / 真签路径里 jar 经 `rebuild_archive_from_tree` 用 NamedTemporaryFile 重建 → 落成 0600。
哪层先命中决定 java-lib 里 10 个含原生库的 jar 是 0600 还是 0644 → 部件 sha 随缓存冷热漂,285 MB 时红时绿。

规则(裁决 A):放回时先查上一版稳定部件的 tar 头留档(`prepare_sign_seed.py` 写的
`build/.sign-seed/prev-parts-headers.json`,路径由环境 HOROSA_PREV_PARTS_HEADERS 给出)—— 留档里有这条路径就用留档的
权限位(内容未变 ⇒ 与线上逐字节同);留档里没有(新文件 / 非稳定部件)用暂存文件原有的位。开关 HOROSA_PREV_PARTS_MODES=0
退回「一律暂存文件位」。
tar 内条目名以 `runtime-payload/` 起头,暂存路径里从最后一个 `runtime-payload` 目录起截取即得。"""
import json
import os
import pathlib
import sys
from typing import Optional

RECORD_ENV = "HOROSA_PREV_PARTS_HEADERS"
SWITCH_ENV = "HOROSA_PREV_PARTS_MODES"
STAGE_DIR_NAME = "runtime-payload"
_RECORD_CACHE: dict = {}


def enabled() -> bool:
    return os.environ.get(SWITCH_ENV, "1") == "1"


def tar_name_of(path) -> Optional[str]:
    """暂存绝对路径 → tar 内条目名(从最后一个 runtime-payload 起);路径里没有该目录回 None。"""
    parts = pathlib.Path(path).parts
    idx = None
    for i, p in enumerate(parts):
        if p == STAGE_DIR_NAME:
            idx = i
    if idx is None:
        return None
    return "/".join(parts[idx:])


def load_record(record_path: Optional[str] = None) -> Optional[dict]:
    """读留档 → {tar 条目名: 权限位};未启用 / 未指定 / 读不到回 None(调用方按暂存位处理)。同一路径只读一次。"""
    if not enabled():
        return None
    p = record_path if record_path is not None else os.environ.get(RECORD_ENV, "")
    if not p:
        return None
    if p in _RECORD_CACHE:
        return _RECORD_CACHE[p]
    try:
        data = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        _RECORD_CACHE[p] = None
        return None
    modes: dict = {}
    for entries in data.values():
        for e in entries:
            # [name, type, size, mode, mtime, linkname](prepare_sign_seed.tar_headers 的列序)
            if isinstance(e, (list, tuple)) and len(e) >= 4 and isinstance(e[0], str):
                try:
                    modes[e[0]] = int(e[3]) & 0o7777
                except (TypeError, ValueError):
                    continue
    _RECORD_CACHE[p] = modes
    print(f"[sign-mode] 权限位来源 = 上一版部件 tar 头留档({len(modes)} 条目;{SWITCH_ENV}=0 退回暂存文件位)",
          file=sys.stderr, flush=True)
    return modes


def decide_mode(path, staged_mode: Optional[int], record: Optional[dict] = None):
    """回 (最终权限位 | None, 来源)。来源 'prev' = 留档;'staged' = 暂存文件原有位;None = 两者都没有(不改)。"""
    rec = record if record is not None else load_record()
    if rec:
        name = tar_name_of(path)
        if name is not None and name in rec:
            return rec[name], "prev"
    if staged_mode is not None:
        return staged_mode & 0o7777, "staged"
    return None, None


def apply_mode(path, staged_mode: Optional[int], record: Optional[dict] = None) -> Optional[str]:
    """按 decide_mode 给 path 设权限位;回来源字符串。"""
    mode, source = decide_mode(path, staged_mode, record)
    if mode is not None:
        try:
            os.chmod(path, mode)
        except OSError:
            return None
    return source
