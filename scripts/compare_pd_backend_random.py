#!/usr/bin/env python3
"""Random-case backend validation: local Horosa PD vs AstroApp dirs.csv.

Compares arc rows on the same key:
  (promissor_id, significator_id, signed_aspect)

Focuses on non-node planetary rows by default (IDs 0..9).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import swisseph


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_import_paths() -> None:
    root = _repo_root()
    import sys

    astropy_root = root / "Horosa-Web" / "astropy"
    flatlib_root = root / "Horosa-Web" / "flatlib-ctrad2"
    for p in [astropy_root, flatlib_root]:
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))


_ensure_import_paths()

from astrostudy.perchart import PerChart  # noqa: E402


OBJ2ID = {
    "Sun": 0,
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Mars": 4,
    "Jupiter": 5,
    "Saturn": 6,
    "Uranus": 7,
    "Neptune": 8,
    "Pluto": 9,
    "North Node": 10,
    "South Node": 23,
    "Asc": 24,
    "MC": 25,
    "Pars Fortuna": 28,
}

ID2NAME = {v: k for k, v in OBJ2ID.items()}


def _as_float(x: Any, default: float = float("nan")) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _norm_asp(x: float) -> float:
    if not math.isfinite(x):
        return x
    r = round(x)
    if abs(x - r) < 1e-9:
        return float(r)
    return float(x)


def _jd_to_utc_date_time(jd: float) -> tuple[str, str]:
    y, m, d, ut = swisseph.revjul(jd, swisseph.GREG_CAL)
    base = datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=float(ut))
    base = (base + timedelta(microseconds=500000)).replace(microsecond=0)
    return base.strftime("%Y/%m/%d"), base.strftime("%H:%M:%S")


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _parse_prom_key(prom: str) -> tuple[int, float] | None:
    parts = str(prom or "").split("_")
    if len(parts) < 3:
        return None
    kind = parts[0]
    obj = "_".join(parts[1:-1]).strip()
    asp = _as_float(parts[-1])
    if obj not in OBJ2ID or not math.isfinite(asp):
        return None
    p_id = OBJ2ID[obj]
    if kind == "D":
        asp = -abs(asp)
    elif kind == "S":
        asp = abs(asp)
    elif kind == "N":
        asp = float(asp)
    else:
        return None
    return p_id, _norm_asp(asp)


def _parse_sig_key(sig: str) -> int | None:
    parts = str(sig or "").split("_")
    if len(parts) < 3:
        return None
    kind = parts[0]
    obj = "_".join(parts[1:-1]).strip()
    asp = _as_float(parts[-1])
    if kind != "N" or not math.isfinite(asp) or abs(asp) > 1e-9:
        return None
    return OBJ2ID.get(obj)


def _astro_key(row: dict[str, str]) -> tuple[int, int, float] | None:
    p = row.get("pID")
    s = row.get("sID")
    a = row.get("asp")
    try:
        p_id = int(float(p))
        s_id = int(float(s))
        asp = _norm_asp(float(a))
    except Exception:
        return None
    return p_id, s_id, asp


@dataclass
class CaseStats:
    case: str
    city: str
    rows_astro: int
    rows_local: int
    rows_matched: int
    mae: float
    median: float
    p95: float
    max: float


def _mean(vals: list[float]) -> float:
    return float(statistics.mean(vals)) if vals else float("nan")


def _median(vals: list[float]) -> float:
    return float(statistics.median(vals)) if vals else float("nan")


def _p95(vals: list[float]) -> float:
    if not vals:
        return float("nan")
    s = sorted(vals)
    idx = max(0, min(len(s) - 1, int(len(s) * 0.95) - 1))
    return float(s[idx])


def compare_case(case_dir: Path, planet_only: bool = True) -> tuple[CaseStats, list[dict[str, Any]], list[float]]:
    meta = json.loads((case_dir / "meta.json").read_text(encoding="utf-8"))
    astro_rows = _load_csv(case_dir / "dirs.csv")

    source_jd = float(meta["sourceJD"])
    date_str, time_str = _jd_to_utc_date_time(source_jd)
    hsys = int(float(meta.get("th_payload", {}).get("house_system_id", 1)))
    zodiacal = 1 if str(meta.get("th_payload", {}).get("zodiac_id", "100")) == "101" else 0

    local_payload = {
        "date": date_str,
        "time": time_str,
        "zone": "+00:00",
        "lat": meta["birth_lat"],
        "lon": meta["birth_long"],
        "hsys": hsys,
        "zodiacal": zodiacal,
        "tradition": False,
        "predictive": True,
        "pdtype": 0,
        "pdaspects": [0, 60, 90, 120, 180],
    }

    perchart = PerChart(local_payload)
    local_pd = perchart.getPredict().getPrimaryDirection()

    astro_map: dict[tuple[int, int, float], dict[str, Any]] = {}
    for row in astro_rows:
        k = _astro_key(row)
        if k is None:
            continue
        p_id, s_id, asp = k
        if planet_only and (p_id not in range(0, 10) or s_id not in range(0, 10)):
            continue
        arc = _as_float(row.get("arc"))
        if not math.isfinite(arc):
            continue
        astro_map[k] = {
            "arc": arc,
            "date": row.get("dirDate", ""),
        }

    local_map: dict[tuple[int, int, float], dict[str, Any]] = {}
    for row in local_pd:
        if not isinstance(row, list) or len(row) < 5:
            continue
        arc = _as_float(row[0])
        if not math.isfinite(arc):
            continue
        prom = str(row[1])
        sig = str(row[2])
        prom_parsed = _parse_prom_key(prom)
        sig_id = _parse_sig_key(sig)
        if prom_parsed is None or sig_id is None:
            continue
        p_id, asp = prom_parsed
        if planet_only and (p_id not in range(0, 10) or sig_id not in range(0, 10)):
            continue
        k = (p_id, sig_id, asp)
        local_map[k] = {
            "arc": arc,
            "date": str(row[4]),
            "prom": prom,
            "sig": sig,
        }

    keys = sorted(set(astro_map.keys()) & set(local_map.keys()), key=lambda x: (abs(astro_map[x]["arc"]), astro_map[x]["arc"]))
    rows_out: list[dict[str, Any]] = []
    errs: list[float] = []
    for k in keys:
        astro = astro_map[k]
        local = local_map[k]
        err = abs(local["arc"] - astro["arc"])
        errs.append(err)
        p_id, s_id, asp = k
        rows_out.append(
            {
                "case": case_dir.name,
                "city": meta.get("city_name", ""),
                "pID": p_id,
                "promissor": ID2NAME.get(p_id, str(p_id)),
                "asp": asp,
                "sID": s_id,
                "significator": ID2NAME.get(s_id, str(s_id)),
                "astro_arc": astro["arc"],
                "horosa_arc": local["arc"],
                "abs_err": err,
                "astro_date": astro["date"],
                "horosa_date": local["date"],
            }
        )

    stats = CaseStats(
        case=case_dir.name,
        city=meta.get("city_name", ""),
        rows_astro=len(astro_map),
        rows_local=len(local_map),
        rows_matched=len(keys),
        mae=_mean(errs),
        median=_median(errs),
        p95=_p95(errs),
        max=max(errs) if errs else float("nan"),
    )
    return stats, rows_out, errs


def write_markdown(
    out_md: Path,
    sample_dirs: list[Path],
    case_stats: list[CaseStats],
    rows: list[dict[str, Any]],
    overall_errs: list[float],
) -> None:
    lines: list[str] = []
    lines.append("# Horosa 本地后端 vs AstroApp 随机样本对照")
    lines.append("")
    lines.append("- 对照口径: `Alcabitius + Ptolemy + In Zodiaco`，非Node行星方向 (`pID/sID: 0..9`)。")
    lines.append("- 行匹配键: `(迫星ID, 应星ID, 带符号相位asp)`。")
    lines.append(f"- 随机样本数: **{len(sample_dirs)}**")
    lines.append(f"- 样本: {', '.join(p.name for p in sample_dirs)}")
    lines.append("")

    lines.append("## 总体统计")
    lines.append("")
    lines.append(f"- matched rows: **{len(overall_errs)}**")
    lines.append(f"- MAE: **{_mean(overall_errs):.9f}°**")
    lines.append(f"- Median: **{_median(overall_errs):.9f}°**")
    lines.append(f"- P95: **{_p95(overall_errs):.9f}°**")
    lines.append(f"- Max: **{(max(overall_errs) if overall_errs else float('nan')):.9f}°**")
    if overall_errs:
        for t in [0.01, 0.005, 0.001]:
            hit = sum(1 for e in overall_errs if e <= t)
            ratio = hit / len(overall_errs)
            lines.append(f"- |err| <= {t:.3f}°: **{hit}/{len(overall_errs)} ({ratio:.4%})**")
    lines.append("")

    lines.append("## 分案例统计")
    lines.append("")
    lines.append("| Case | 城市 | Astro行数 | Horosa行数 | 匹配行数 | MAE(°) | P95(°) | Max(°) |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for s in case_stats:
        lines.append(
            f"| {s.case} | {s.city} | {s.rows_astro} | {s.rows_local} | {s.rows_matched} | "
            f"{s.mae:.9f} | {s.p95:.9f} | {s.max:.9f} |"
        )
    lines.append("")

    lines.append("## 直观对照表（同一行=同一迫星/相位/应星）")
    lines.append("")
    lines.append("| Case | 迫星 | 相位asp | 应星 | AstroApp Arc | Horosa Arc | |ΔArc| | Astro 日期 | Horosa 日期 |")
    lines.append("| --- | --- | ---: | --- | ---: | ---: | ---: | --- | --- |")
    for r in rows:
        lines.append(
            f"| {r['case']} | {r['promissor']} | {r['asp']:.0f} | {r['significator']} | "
            f"{r['astro_arc']:.9f} | {r['horosa_arc']:.9f} | {r['abs_err']:.9f} | "
            f"{r['astro_date']} | {r['horosa_date']} |"
        )
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Random local-backend vs AstroApp PD comparison")
    ap.add_argument("--cases-root", required=True, help="Root containing case_*/meta.json + dirs.csv")
    ap.add_argument("--sample-size", type=int, default=8, help="Number of random cases to sample")
    ap.add_argument("--seed", type=int, default=20260305, help="Random seed")
    ap.add_argument("--rows-per-case", type=int, default=10, help="Rows to keep per case for human-readable table")
    ap.add_argument("--out-csv", required=True, help="Detailed row comparison CSV")
    ap.add_argument("--out-json", required=True, help="Summary JSON")
    ap.add_argument("--out-md", required=True, help="Markdown report")
    args = ap.parse_args()

    root = Path(args.cases_root)
    case_dirs = sorted([p for p in root.iterdir() if p.is_dir() and p.name.startswith("case_")])
    if not case_dirs:
        raise RuntimeError(f"no case_* in {root}")

    rng = random.Random(args.seed)
    k = min(args.sample_size, len(case_dirs))
    sample_dirs = sorted(rng.sample(case_dirs, k=k), key=lambda p: p.name)

    all_stats: list[CaseStats] = []
    all_errs: list[float] = []
    all_rows: list[dict[str, Any]] = []
    for c in sample_dirs:
        stats, rows, errs = compare_case(c, planet_only=True)
        all_stats.append(stats)
        all_errs.extend(errs)
        rows_sorted = sorted(rows, key=lambda x: (abs(float(x["astro_arc"])), float(x["astro_arc"])))
        all_rows.extend(rows_sorted[: args.rows_per_case])

    out_csv = Path(args.out_csv)
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    # CSV
    fieldnames = [
        "case",
        "city",
        "pID",
        "promissor",
        "asp",
        "sID",
        "significator",
        "astro_arc",
        "horosa_arc",
        "abs_err",
        "astro_date",
        "horosa_date",
    ]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in all_rows:
            w.writerow(row)

    # JSON summary
    summary = {
        "cases_root": str(root),
        "sample_size": k,
        "seed": args.seed,
        "rows_total_matched": len(all_errs),
        "mae": _mean(all_errs),
        "median": _median(all_errs),
        "p95": _p95(all_errs),
        "max": max(all_errs) if all_errs else float("nan"),
        "hit_ratio": {
            "<=0.010000": (sum(1 for e in all_errs if e <= 0.01) / len(all_errs)) if all_errs else float("nan"),
            "<=0.005000": (sum(1 for e in all_errs if e <= 0.005) / len(all_errs)) if all_errs else float("nan"),
            "<=0.001000": (sum(1 for e in all_errs if e <= 0.001) / len(all_errs)) if all_errs else float("nan"),
        },
        "cases": [
            {
                "case": s.case,
                "city": s.city,
                "rows_astro": s.rows_astro,
                "rows_local": s.rows_local,
                "rows_matched": s.rows_matched,
                "mae": s.mae,
                "median": s.median,
                "p95": s.p95,
                "max": s.max,
            }
            for s in all_stats
        ],
    }
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown report
    write_markdown(out_md, sample_dirs, all_stats, all_rows, all_errs)

    print(f"sample_cases: {k}")
    print(f"matched_rows: {len(all_errs)}")
    print(f"mae: {summary['mae']:.12f}")
    print(f"p95: {summary['p95']:.12f}")
    print(f"max: {summary['max']:.12f}")
    print(f"csv:  {out_csv}")
    print(f"json: {out_json}")
    print(f"md:   {out_md}")


if __name__ == "__main__":
    main()
