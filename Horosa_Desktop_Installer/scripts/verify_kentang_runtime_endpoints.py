#!/usr/bin/env python3
"""Smoke-test every bundled kentang/kin runtime endpoint.

Release rule: every packaged technique exposed by the kentang/kin chart service
must be represented here before publishing. The installed-app release checks run
this before the generic chart smoke to catch shared runtime state pollution.
"""

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

# 地占冒烟:基准请求体照界面原样发 —— 经纬用**度分记法**、时区用偏移串,
# 因为「界面发什么形状」正是 v3.9.1 修的那条(按十进制度解读会静默回落成无真实盘)。
GEOMANCY_SMOKE_BASE = {
    "question": "",
    "questionType": "custom",
    "quesitedHouse": 1,
    "tradition": "european_classical",
    "readingScope": "L3",
    "seedMode": "manual",
    "seed": 4242,
    "date": "2026-05-01",
    "time": "12:00:00",
    "zone": "+08:00",
    "lon": "119e19",
    "lat": "26n04",
}
GEOMANCY_SMOKE_VARIANTS = [
    # ① 默认档:不选真实盘,证明基本判读链在打包运行时可用
    {"label": "default"},
    # ② 真实上升档:证明时地真的送达计算层且星历可用(打包后 ephem 惰性导入若失败,这条必红)
    {"label": "real-ascendant", "ascSource": "real_chart", "_expect_real_chart": True},
    # ③ 西经 + 西时区:覆盖度分记法的负号与偏移串两条解析路径。
    #    判据不能只看「起出来了」—— 还须与 ② 的上升**度数**不同,才证明经纬时区真的送达了计算层
    #    (只比星座不行:两地同为狮子,而度数 134.307 vs 129.314 才是判别力所在)。
    {"label": "west-lon-west-zone", "ascSource": "real_chart", "lon": "74w00", "lat": "40n42",
     "zone": "-04:00", "_expect_real_chart": True, "_differs_from": "real-ascendant"},
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

CHART_SMOKE_BASE_PAYLOAD = {
    "date": "2026/05/24",
    "time": "09:30:00",
    "zone": "+08:00",
    "lat": "31n14",
    "lon": "121e28",
    "gpsLat": 31.2304,
    "gpsLon": 121.4737,
    "pos": "上海",
    "hsys": 1,
    "tradition": False,
    "predictive": True,
    "zodiacal": 0,
    "simpleAsp": False,
    "strongRecption": False,
    "virtualPointReceiveAsp": False,
    "southchart": False,
    "ad": 1,
    "pdtype": 0,
    "pdMethod": "core_alchabitius",
    "pdTimeKey": "Ptolemy",
    "pdaspects": [0, 60, 90, 120, 180],
    "doubingSu28": 2,
}

CHART_SMOKE_VARIANTS = [
    {
        "label": "modern-shanghai",
        "date": "2026/05/24",
        "time": "09:30:00",
        "zone": "+08:00",
        "lat": "31n14",
        "lon": "121e28",
        "gpsLat": 31.2304,
        "gpsLon": 121.4737,
    },
    {
        "label": "past-fuzhou",
        "date": "2023/05/24",
        "time": "08:41:55",
        "zone": "+08:00",
        "lat": "26n04",
        "lon": "119e19",
        "gpsLat": 26.0666,
        "gpsLon": 119.3166,
    },
    {
        "label": "future-fuzhou",
        "date": "2027/05/24",
        "time": "20:41:55",
        "zone": "+08:00",
        "lat": "26n04",
        "lon": "119e19",
        "gpsLat": 26.0666,
        "gpsLon": 119.3166,
    },
    {
        "label": "utc-west",
        "date": "1994/01/17",
        "time": "23:15:00",
        "zone": "-08:00",
        "lat": "34n03",
        "lon": "118w15",
        "gpsLat": 34.05,
        "gpsLon": -118.25,
    },
]


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

    for variant in CHART_SMOKE_VARIANTS:
        label = variant["label"]
        payload_in = dict(CHART_SMOKE_BASE_PAYLOAD)
        payload_in.update(variant)
        payload_in.pop("label", None)
        try:
            status, payload = post_json(f"{root}/", payload_in, args.timeout)
            chart_ok = status < 500 and not payload.get("err") and payload.get("chart") and payload.get("params")
            print(
                "chart endpoint after kentang smoke "
                f"{'OK' if chart_ok else 'FAIL'} {label}: http={status} "
                f"birth={payload.get('params', {}).get('birth')}"
            )
            if not chart_ok:
                failures.append((f"chart-after-kentang:{label}", json.dumps(payload, ensure_ascii=False)[:500]))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            failures.append((f"chart-after-kentang:{label}", repr(exc)))
            print(f"chart endpoint after kentang smoke FAIL {label}: {exc}", file=sys.stderr)

    # ── 地占:走 /geomancy/reading(路径形状与上面 17 个 /{engine}/pan 不同,故此前一直不在冒烟面内)。
    #    v3.9.1 起地占的「据所选时地起真实上升」依赖两样在打包运行时才可能出问题的东西:
    #    ① websrv.horosa_engine_common 的跨模块 import;② astrostudy.geomancy.ephem 惰性导入星历。
    #    二者在 dev 下必然可用、打包后未必 —— 正是「preview 好用、APP 里不好用」的典型形态,故必须冒烟。
    geo_asc_lon = {}
    for variant in GEOMANCY_SMOKE_VARIANTS:
        label = variant.pop("label")
        payload_in = dict(GEOMANCY_SMOKE_BASE)
        payload_in.update(variant)
        expect_real = payload_in.pop("_expect_real_chart", False)
        differs_from = payload_in.pop("_differs_from", None)
        try:
            status, payload = post_json(f"{root}/geomancy/reading", payload_in, args.timeout)
            result = payload.get("Result") or {}
            reading = result.get("reading") or {}
            geo_ok = status < 500 and payload.get("ResultCode") in (0, "0") and len(reading.get("figures16") or []) == 16
            detail = f"http={status} judge={(reading.get('judge') or {}).get('nameEn')}"
            asc_lon = (reading.get("astroErection") or {}).get("asc_lon")
            if expect_real:
                # 真实盘必须真的起出来:available=False 即说明时地没送达计算层(度分记法解析失败等)
                avail = (reading.get("settings") or {}).get("real_chart_available")
                asc = (reading.get("astroErection") or {}).get("sign") or reading.get("ascendantSign")
                geo_ok = geo_ok and avail is True and bool(asc) and asc_lon is not None
                detail += f" realChart={avail} asc={asc} ascLon={asc_lon}"
                geo_asc_lon[label] = asc_lon
            if differs_from is not None:
                ref = geo_asc_lon.get(differs_from)
                moved = ref is not None and asc_lon is not None and abs(float(asc_lon) - float(ref)) > 0.01
                geo_ok = geo_ok and moved
                detail += f" vs {differs_from}: Δ={None if (ref is None or asc_lon is None) else round(float(asc_lon)-float(ref),3)}"
            print(f"geomancy endpoint {'OK' if geo_ok else 'FAIL'} {label}: {detail}")
            if not geo_ok:
                failures.append((f"geomancy:{label}", json.dumps(payload, ensure_ascii=False)[:500]))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            failures.append((f"geomancy:{label}", repr(exc)))
            print(f"geomancy endpoint FAIL {label}: {exc}", file=sys.stderr)

    if failures:
        print("kentang endpoint smoke failed:", failures[:5], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
