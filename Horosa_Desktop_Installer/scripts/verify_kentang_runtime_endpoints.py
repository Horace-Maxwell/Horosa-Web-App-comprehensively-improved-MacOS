#!/usr/bin/env python3
"""Smoke-test every bundled kentang/kin runtime endpoint."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


ENDPOINTS = [
    "taiyi",
    "jinkou",
    "qimen",
    "wangji",
    "wuzhao",
    "taixuan",
    "jingjue",
    "shenyishu",
    "shaozi",
    "tieban",
    "fendjing",
    "beiji",
    "nanji",
    "chunzi",
    "xianqin",
    "cetian",
    "qizhengkin",
]

SMOKE_PAYLOAD = {
    "year": 2026,
    "month": 5,
    "day": 24,
    "hour": 9,
    "minute": 30,
    "date": "2026/05/24",
    "time": "09:30:00",
    "zone": "+08:00",
    "timezone": 8,
    "lat": "31n14",
    "lon": "121e28",
    "gpsLat": 31.2304,
    "gpsLon": 121.4737,
    "pos": "上海",
    "location": "上海",
    "locationName": "上海",
    "gender": "male",
    "sex": "男",
    "question": "测试",
    "seed": 123456,
    "style": 3,
    "tn": 0,
    "method": "auto",
}


def post_json(url: str, payload: dict, timeout: float) -> tuple[int, dict]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", "replace")
        return response.status, json.loads(body)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Chart service root, for example http://127.0.0.1:8899")
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()

    root = args.root.rstrip("/")
    failures = []
    for endpoint in ENDPOINTS:
        url = f"{root}/{endpoint}/pan"
        try:
            status, payload = post_json(url, SMOKE_PAYLOAD, args.timeout)
            result_code = payload.get("ResultCode")
            result = payload.get("Result")
            ok = status < 500 and result_code in (0, "0") and result is not None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            failures.append((endpoint, repr(exc)))
            print(f"kentang endpoint FAIL {endpoint}: {exc}", file=sys.stderr)
            continue

        result_type = type(result).__name__
        print(f"kentang endpoint OK {endpoint}: http={status} resultCode={result_code} resultType={result_type}")
        if not ok:
            failures.append((endpoint, json.dumps(payload, ensure_ascii=False)[:500]))

    if failures:
        print("kentang endpoint smoke failed:", failures[:5], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
