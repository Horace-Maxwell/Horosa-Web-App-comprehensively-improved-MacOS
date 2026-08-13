#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_full_route_smoke.py — Python 服务面全路由真实请求冒烟探针器。

读 config/route_smoke_probes.jsonc(JSONC-lite:忽略 // 行),对目标 chart 服务逐条
发真实参数请求并三层断言:HTTP<500 且 JSON 可解析 → 业务码(result_code0/no_err)
→ 真实计算特征(expect_keys/numeric_keys/nonempty)。404/超时一律 FAIL。

用法:
  verify_full_route_smoke.py --root http://127.0.0.1:8899 [--manifest <jsonc>] [--out <json>]

退出码:0 全过 / 1 有失败 / 3 清单错误。
铁律:本地探测禁代理(ProxyHandler({}))。
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MANIFEST = os.path.join(SCRIPT_DIR, "..", "config", "route_smoke_probes.jsonc")

_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def load_manifest(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    # JSONC-lite:去掉整行 // 注释与 /* … */ 单行标记行(私有剥离标记形态)
    lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        if stripped.startswith("/*") and stripped.endswith("*/"):
            continue
        lines.append(line)
    text = "\n".join(lines)
    # 容忍剥离标记留下的悬挂逗号(私有条目被剥后可能出现 ",]" / ",}")
    text = re.sub(r",\s*([\]}])", r"\1", text)
    return json.loads(text)


def http_json(url, payload, method, timeout):
    data = None
    headers = {}
    if method == "POST":
        data = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with _OPENER.open(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", "replace")
        return response.status, json.loads(body)


def _dig(obj, dotted):
    """按点分路径取值(a.b.c);任一层缺失即回 None。"""
    cur = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def run_probe(root, probe, payloads, timeout):
    url = root.rstrip("/") + probe["path"]
    method = probe.get("method", "POST")
    payload = dict(payloads.get(probe.get("payload_ref") or "", {}) or {})
    payload.update(probe.get("payload_extra") or {})
    checks = probe.get("assert") or {}
    detail = {"id": probe["id"], "path": probe["path"], "ok": False}
    try:
        status, body = http_json(url, payload, method, timeout)
    except Exception as exc:  # URLError/timeout/JSONDecodeError/HTTPError 一律 FAIL
        detail["error"] = repr(exc)[:300]
        return detail
    detail["http"] = status
    problems = []
    if status >= 500:
        problems.append("http>=500")
    if status == 404:
        problems.append("http404")
    if checks.get("result_code0"):
        rc = body.get("ResultCode") if isinstance(body, dict) else None
        result = body.get("Result") if isinstance(body, dict) else None
        if rc not in (0, "0"):
            problems.append("ResultCode=%r" % (rc,))
        if result in (None, "", [], {}):
            problems.append("Result empty")
    if checks.get("no_err"):
        if isinstance(body, dict) and body.get("err"):
            problems.append("err=%r" % (body.get("err"),))
    if checks.get("nonempty"):
        if not body or (isinstance(body, (dict, list)) and len(body) == 0):
            problems.append("body empty")
    for key in checks.get("expect_keys") or []:
        val = body.get(key) if isinstance(body, dict) else None
        if val in (None, "", [], {}):
            problems.append("missing/empty key %r" % key)
    for key in checks.get("numeric_keys") or []:
        val = body.get(key) if isinstance(body, dict) else None
        if not isinstance(val, (int, float)):
            problems.append("key %r not numeric (%r)" % (key, type(val).__name__))
    # 嵌套判据:顶层键判不到「算没算对」——如地占真实盘的可用位埋在 Result.reading.settings 下,
    # 只断言 ResultCode==0 时,时地解析全盘失效(静默回落)照样是 200+0,探针形同虚设。
    for path in checks.get("expect_true_paths") or []:
        if _dig(body, path) is not True:
            problems.append("path %r != True (%r)" % (path, _dig(body, path)))
    for path in checks.get("numeric_paths") or []:
        if not isinstance(_dig(body, path), (int, float)):
            problems.append("path %r not numeric (%r)" % (path, _dig(body, path)))
    if problems:
        detail["problems"] = problems
        detail["body_head"] = json.dumps(body, ensure_ascii=False)[:400]
    else:
        detail["ok"] = True
    return detail


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="chart 服务根,如 http://127.0.0.1:8899")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--timeout", type=float, default=90)
    parser.add_argument("--out", default="", help="逐路由结果 JSON 输出路径(可选)")
    args = parser.parse_args()

    try:
        manifest = load_manifest(args.manifest)
    except Exception as exc:
        print("[route-smoke] manifest error: %r" % exc, file=sys.stderr)
        return 3

    payloads = manifest.get("payloads") or {}
    probes = manifest.get("python") or []
    if not probes:
        print("[route-smoke] manifest has no python probes", file=sys.stderr)
        return 3

    results = []
    failures = 0
    for probe in probes:
        detail = run_probe(args.root, probe, payloads, args.timeout)
        results.append(detail)
        if detail["ok"]:
            print("[route-smoke] OK   %-14s %s http=%s" % (detail["id"], detail["path"], detail.get("http")))
        else:
            failures += 1
            print("[route-smoke] FAIL %-14s %s %s" % (
                detail["id"], detail["path"],
                detail.get("error") or "; ".join(detail.get("problems") or [])), file=sys.stderr)

    summary = {"total": len(results), "failed": failures, "results": results}
    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as fh:
                json.dump(summary, fh, ensure_ascii=False, indent=1)
        except Exception as exc:
            print("[route-smoke] warn: cannot write out file: %r" % exc, file=sys.stderr)
    print("[route-smoke] %d/%d passed" % (len(results) - failures, len(results)))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
