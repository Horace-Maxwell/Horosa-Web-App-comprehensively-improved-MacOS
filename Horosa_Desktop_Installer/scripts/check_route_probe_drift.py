#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_route_probe_drift.py — 路由挂载 ↔ 冒烟探针 漂移比对器(静态,秒级,preflight 可跑)。

三个真源双向核对探针清单(config/route_smoke_probes.jsonc):
  ① kentang registry.KENTANG_SERVICE_SPECS(import 读)
  ② webchartsrv.py __main__ 的 tree.mount(...,'/xxx')(正则提取)
  ③(附带)KENTANG_ADAPTERS(tests/test_runtime_deps_slim.py) ⊇ 静态扫描出的全部
     kinastro_common importer——封 adapter 覆盖名单漂移

规则(违反即 exit 1,发布拦截):
  - 挂载无探针 → FAIL(新增技法漏配探针);
  - 探针无挂载 → FAIL(僵尸探针,cetian 教训);
历史铁证:v3.2.x 前 geomancy/xuanshi 挂载无探针、cetian 迁出 registry 后探针残留。

用法: check_route_probe_drift.py [--web-root <Horosa-Web>] [--manifest <jsonc>]
"""
import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INSTALLER_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DEFAULT_WEB_ROOT = os.path.abspath(os.path.join(INSTALLER_ROOT, "..", "Horosa-Web"))
DEFAULT_MANIFEST = os.path.join(INSTALLER_ROOT, "config", "route_smoke_probes.jsonc")

sys.path.insert(0, SCRIPT_DIR)
from verify_full_route_smoke import load_manifest  # noqa: E402  复用 JSONC 加载器


def registry_mounts(web_root):
    astropy_root = os.path.join(web_root, "astropy")
    sys.path.insert(0, astropy_root)
    try:
        from websrv.kentang.registry import KENTANG_SERVICE_SPECS
        return {spec["mount"] for spec in KENTANG_SERVICE_SPECS}
    finally:
        sys.path.remove(astropy_root)


def webchartsrv_direct_mounts(web_root):
    src_path = os.path.join(web_root, "astropy", "websrv", "webchartsrv.py")
    src = open(src_path, encoding="utf-8").read()
    mounts = set(re.findall(r"tree\.mount\([^,]+,\s*'(/[^']*)'", src))
    # [B5] 核心服务惰性挂载后,14 路由从字面 tree.mount(...) 移进 CORE_SERVICE_SPECS
    # 表(循环挂 spec["mount"]),字面正则看不见 → 这里把表里的 mount 一并计入,
    # 语义仍是「webchartsrv 实际会挂什么」。
    spec_block = re.search(r"CORE_SERVICE_SPECS\s*=\s*\[(.*?)\n\]", src, re.S)
    if spec_block:
        mounts |= set(re.findall(r'"mount":\s*"(/[^"]*)"', spec_block.group(1)))
    return mounts


def kinastro_importers(web_root):
    """静态扫描:哪些 websrv 适配器 import kinastro_common(即依赖 streamlit 桩)。"""
    websrv_dir = os.path.join(web_root, "astropy", "websrv")
    hits = set()
    for fn in os.listdir(websrv_dir):
        if not fn.endswith(".py"):
            continue
        path = os.path.join(websrv_dir, fn)
        try:
            src = open(path, encoding="utf-8").read()
        except Exception:
            continue
        if re.search(r"from\s+websrv\.kentang\.kinastro_common\s+import|import\s+websrv\.kentang\.kinastro_common", src):
            hits.add("websrv." + fn[:-3])
    return hits


def declared_adapters(web_root):
    test_path = os.path.join(web_root, "astropy", "tests", "test_runtime_deps_slim.py")
    src = open(test_path, encoding="utf-8").read()
    m = re.search(r"KENTANG_ADAPTERS\s*=\s*\[(.*?)\]", src, re.S)
    if not m:
        return set()
    return set(re.findall(r"'([\w.]+)'", m.group(1)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--web-root", default=DEFAULT_WEB_ROOT)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    probes = manifest.get("python") or []
    probe_mounts = {p["mount"] for p in probes}

    mounts = registry_mounts(args.web_root) | webchartsrv_direct_mounts(args.web_root)

    problems = []
    missing_probe = sorted(mounts - probe_mounts)
    if missing_probe:
        problems.append("挂载无探针(新增技法漏配): %s" % ", ".join(missing_probe))
    zombie_probe = sorted(probe_mounts - mounts)
    if zombie_probe:
        problems.append("探针无挂载(僵尸探针): %s" % ", ".join(zombie_probe))

    importers = kinastro_importers(args.web_root)
    declared = declared_adapters(args.web_root)
    undeclared = sorted(importers - declared)
    if undeclared:
        problems.append("kinastro importer 未入 KENTANG_ADAPTERS 覆盖名单: %s" % ", ".join(undeclared))

    if problems:
        for p in problems:
            print("[probe-drift] FAIL:", p, file=sys.stderr)
        return 1
    print("[probe-drift] OK: %d 挂载 × %d 探针 双向一致;kinastro importer %d/%d 全在覆盖名单"
          % (len(mounts), len(probe_mounts), len(importers), len(importers)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
