#!/usr/bin/env python3
"""Batch collect AstroApp Primary Directions without UI macros.

The script replays the observed pair of requests:
1) POST /astro/chartSubmit.jsp
2) POST /astro/th.jsp

It uses a HAR file as a template for payload fields + auth headers.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs

import requests


SKIP_HEADERS = {
    "host",
    "content-length",
    "connection",
    "accept-encoding",
    "cookie",
    ":authority",
    ":method",
    ":path",
    ":scheme",
}


@dataclass
class TemplateReq:
    url: str
    headers: dict[str, str]
    payload: dict[str, str]


class CollectError(RuntimeError):
    pass


def _is_login_required(text: str) -> bool:
    t = text or ""
    return "isc_loginRequired" in t or "loginRequired" in t


def _load_har_entries(path: pathlib.Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    log = payload.get("log", {})
    entries = log.get("entries", [])
    if not isinstance(entries, list):
        raise CollectError("HAR missing log.entries")
    return [e for e in entries if isinstance(e, dict)]


def _req_headers(entry: dict[str, Any]) -> dict[str, str]:
    raw = entry.get("request", {}).get("headers", [])
    out: dict[str, str] = {}
    for item in raw:
        name = str(item.get("name", ""))
        value = str(item.get("value", ""))
        if not name:
            continue
        lname = name.lower()
        if lname in SKIP_HEADERS:
            continue
        out[name] = value
    return out


def _req_payload(entry: dict[str, Any]) -> dict[str, str]:
    text = (entry.get("request", {}).get("postData", {}) or {}).get("text", "")
    parsed = parse_qs(text, keep_blank_values=True)
    return {k: (v[0] if v else "") for k, v in parsed.items()}


def _pick_latest(entries: list[dict[str, Any]], url_substring: str) -> dict[str, Any]:
    matched = [
        e
        for e in entries
        if e.get("request", {}).get("method") == "POST"
        and url_substring in str(e.get("request", {}).get("url", ""))
    ]
    if not matched:
        raise CollectError(f"No POST request found for '{url_substring}'")
    return matched[-1]


def _build_templates(har_path: pathlib.Path) -> tuple[TemplateReq, TemplateReq]:
    entries = _load_har_entries(har_path)
    submit_entry = _pick_latest(entries, "/astro/chartSubmit.jsp")
    th_entry = _pick_latest(entries, "/astro/th.jsp")

    submit_tpl = TemplateReq(
        url=str(submit_entry["request"]["url"]).split("?")[0],
        headers=_req_headers(submit_entry),
        payload=_req_payload(submit_entry),
    )
    th_tpl = TemplateReq(
        url=str(th_entry["request"]["url"]).split("?")[0],
        headers=_req_headers(th_entry),
        payload=_req_payload(th_entry),
    )
    return submit_tpl, th_tpl


def _parse_xml(text: str) -> ET.Element:
    if _is_login_required(text):
        raise CollectError("Session is not authenticated (isc_loginRequired)")
    try:
        return ET.fromstring(text.strip())
    except Exception as exc:
        snippet = text[:300].replace("\n", " ")
        raise CollectError(f"Response is not valid XML. first300={snippet!r}") from exc


def _status_ok(root: ET.Element) -> bool:
    return (root.findtext("status") or "") == "0"


def _record_to_dict(root: ET.Element) -> dict[str, str]:
    record = root.find("./data/record")
    if record is None:
        return {}
    out: dict[str, str] = {}
    for child in record:
        out[child.tag] = child.text or ""
    return out


def _dirs_from_th(root: ET.Element) -> list[dict[str, str]]:
    data = root.find("data")
    if data is None:
        return []

    rows: list[dict[str, str]] = []
    for node in data.findall("dir"):
        rows.append(
            {
                "arc": (node.findtext("arc") or "").strip(),
                "conv": (node.findtext("conv") or "").strip(),
                "asp": (node.findtext("asp") or "").strip(),
                "pID": (node.findtext("pID") or "").strip(),
                "sID": (node.findtext("sID") or "").strip(),
                "dirDate": (node.findtext("dirDate") or "").strip(),
                "dirJD": (node.findtext("dirJD") or "").strip(),
            }
        )
    return rows


def _normalize_birth_time(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return raw
    if "." in raw:
        return raw

    parts = raw.split(":")
    if len(parts) == 2:
        return f"{parts[0]}:{parts[1]}:00.000"
    if len(parts) == 3:
        return f"{parts[0]}:{parts[1]}:{parts[2]}.000"
    return raw


def _plain_tz_name(value: str) -> str:
    value = value.strip()
    if " (" in value:
        return value.split(" (", 1)[0].strip()
    return value


def _load_plan(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise CollectError("Plan CSV is empty")
    required = ["birth_date", "birth_time", "country_id", "city_name", "birth_lat", "birth_long"]
    missing = [k for k in required if k not in rows[0]]
    if missing:
        raise CollectError(f"Plan CSV missing required columns: {missing}")
    return rows


def _apply_prefixed_overrides(payload: dict[str, str], row: dict[str, str], prefix: str) -> None:
    """Apply per-row overrides from CSV columns like th_dir_meth=7."""
    plen = len(prefix)
    for col, value in row.items():
        if not col.startswith(prefix):
            continue
        key = col[plen:]
        if not key:
            continue
        v = (value or "").strip()
        if v == "":
            continue
        payload[key] = v


def _post(session: requests.Session, url: str, headers: dict[str, str], payload: dict[str, str]) -> str:
    resp = session.post(url, headers=headers, data=payload, timeout=45)
    resp.raise_for_status()
    return resp.text


def _login_astroapp(session: requests.Session, username: str, password: str) -> None:
    login_url = "https://astroapp.com/astro/astro.jsp"
    r = session.get(login_url, timeout=45)
    r.raise_for_status()

    m = re.search(r'name="s"\s+value="([^"]+)"', r.text)
    if not m:
        raise CollectError("astro.jsp login token 's' not found")
    token_s = m.group(1)

    payload = {
        "s": token_s,
        "username": username,
        "password": password,
        "submit": "Login",
    }
    headers = {
        "origin": "https://astroapp.com",
        "referer": "https://astroapp.com/astro/astro.jsp",
        "content-type": "application/x-www-form-urlencoded",
    }

    r2 = session.post(login_url, headers=headers, data=payload, timeout=45)
    r2.raise_for_status()

    probe = session.post(
        "https://astroapp.com/astro/chartSubmit.jsp",
        headers={
            "origin": "https://astroapp.com",
            "referer": "https://astroapp.com/astro/astro.jsp",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        data={"actID": "1"},
        timeout=45,
    )
    probe.raise_for_status()
    if _is_login_required(probe.text):
        raise CollectError("AstroApp login failed: credentials rejected or session not established")


def _write_dirs_csv(path: pathlib.Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["arc", "conv", "asp", "pID", "sID", "dirDate", "dirJD"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    ap = argparse.ArgumentParser(description="Batch collect AstroApp Primary Directions without UI macros")
    ap.add_argument("--template-har", required=True, help="HAR path with valid logged-in requests")
    ap.add_argument("--plan-csv", required=True, help="CSV path of birth inputs")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--sleep", type=float, default=0.2, help="Sleep seconds between samples")
    ap.add_argument("--limit", type=int, help="Optional max rows from plan")
    ap.add_argument("--dry-run", action="store_true", help="Validate template+plan without network calls")
    ap.add_argument("--login-username", help="AstroApp username/email for /astro/astro.jsp login")
    ap.add_argument("--login-password", help="AstroApp password for /astro/astro.jsp login")
    args = ap.parse_args()

    template_har = pathlib.Path(args.template_har)
    plan_csv = pathlib.Path(args.plan_csv)
    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    submit_tpl, th_tpl = _build_templates(template_har)
    plan_rows = _load_plan(plan_csv)
    if args.limit is not None:
        plan_rows = plan_rows[: args.limit]

    submit_headers = dict(submit_tpl.headers)
    th_headers = dict(th_tpl.headers)
    current_chart_id = submit_tpl.payload.get("chart_id", "")

    log_rows: list[dict[str, Any]] = []

    if args.dry_run:
        print(f"template submit url: {submit_tpl.url}")
        print(f"template th url:     {th_tpl.url}")
        print(f"plan rows: {len(plan_rows)}")
        print("dry-run complete")
        return

    session = requests.Session()
    if args.login_username:
        if not args.login_password:
            raise CollectError("--login-password is required when --login-username is provided")
        _login_astroapp(session, args.login_username, args.login_password)

    for i, row in enumerate(plan_rows, start=1):
        case_dir = out_dir / f"case_{i:04d}"
        case_dir.mkdir(parents=True, exist_ok=True)

        birth_date = row["birth_date"].strip()
        birth_time = _normalize_birth_time(row["birth_time"])
        country_id = row["country_id"].strip()
        city_name = row["city_name"].strip()
        birth_lat = row["birth_lat"].strip()
        birth_long = row["birth_long"].strip()

        chart_tz = (
            row.get("chart_time_zone_name")
            or row.get("time_zone_name")
            or submit_tpl.payload.get("time_zone_name", "")
        ).strip()
        th_tz = (
            row.get("th_time_zone_name")
            or _plain_tz_name(chart_tz)
            or th_tpl.payload.get("time_zone_name", "")
        ).strip()

        chart_name = (row.get("chart_name") or f"Auto_{i:04d}").strip()

        submit_payload = dict(submit_tpl.payload)
        submit_payload.update(
            {
                "chart_id": current_chart_id,
                "actID": "1",
                "chart_name": chart_name,
                "birth_date": birth_date,
                "birth_time": birth_time,
                "country_id": country_id,
                "city_name": city_name,
                "birth_lat": birth_lat,
                "birth_long": birth_long,
                "time_zone_name": chart_tz,
            }
        )
        _apply_prefixed_overrides(submit_payload, row, "submit_")

        submit_variants: list[str] = []
        for candidate in [current_chart_id, "", "0"]:
            if candidate not in submit_variants:
                submit_variants.append(candidate)

        submit_root = None
        submit_raw = ""
        used_chart_id = ""
        for candidate in submit_variants:
            submit_payload["chart_id"] = candidate
            submit_raw = _post(session, submit_tpl.url, submit_headers, submit_payload)
            test_root = _parse_xml(submit_raw)
            if _status_ok(test_root):
                submit_root = test_root
                used_chart_id = candidate
                break

        if submit_root is None:
            (case_dir / "chartSubmit_response.xml").write_text(submit_raw, encoding="utf-8")
            raise CollectError(f"chartSubmit failed at row {i}")

        (case_dir / "chartSubmit_response.xml").write_text(submit_raw, encoding="utf-8")

        record = _record_to_dict(submit_root)
        new_chart_id = record.get("chart_id", "")
        source_jd = record.get("jDate", "")
        if not new_chart_id or not source_jd:
            raise CollectError(f"chartSubmit missing chart_id/jDate at row {i}")

        th_payload = dict(th_tpl.payload)
        th_payload.update(
            {
                "chart_id": new_chart_id,
                "sourceJD": source_jd,
                "birth_lat": birth_lat,
                "birth_long": birth_long,
                "source_lat": birth_lat,
                "source_long": birth_long,
                "country_id": country_id,
                "city_name": city_name,
                "time_zone_name": th_tz,
                "source_time_zone": th_tz,
                "isRedraw": "0",
                "actID": "0",
            }
        )
        _apply_prefixed_overrides(th_payload, row, "th_")

        th_raw = _post(session, th_tpl.url, th_headers, th_payload)
        (case_dir / "th_response.xml").write_text(th_raw, encoding="utf-8")
        th_root = _parse_xml(th_raw)
        if not _status_ok(th_root):
            raise CollectError(f"th.jsp failed at row {i}")

        dirs = _dirs_from_th(th_root)
        _write_dirs_csv(case_dir / "dirs.csv", dirs)

        meta = {
            "case": i,
            "submit_used_chart_id": used_chart_id,
            "chart_id": new_chart_id,
            "sourceJD": source_jd,
            "rows": len(dirs),
            "birth_date": birth_date,
            "birth_time": birth_time,
            "country_id": country_id,
            "city_name": city_name,
            "birth_lat": birth_lat,
            "birth_long": birth_long,
            "chart_time_zone_name": chart_tz,
            "th_time_zone_name": th_tz,
            "submit_payload": submit_payload,
            "th_payload": th_payload,
        }
        (case_dir / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        log_rows.append(
            {
                "case": i,
                "submit_used_chart_id": used_chart_id,
                "chart_id": new_chart_id,
                "sourceJD": source_jd,
                "rows": len(dirs),
                "birth_date": birth_date,
                "birth_time": birth_time,
                "country_id": country_id,
                "city_name": city_name,
                "birth_lat": birth_lat,
                "birth_long": birth_long,
                "chart_time_zone_name": chart_tz,
                "th_time_zone_name": th_tz,
            }
        )

        current_chart_id = new_chart_id

        if args.sleep > 0:
            time.sleep(args.sleep)

    log_csv = out_dir / "run_log.csv"
    with log_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "case",
                "submit_used_chart_id",
                "chart_id",
                "sourceJD",
                "rows",
                "birth_date",
                "birth_time",
                "country_id",
                "city_name",
                "birth_lat",
                "birth_long",
                "chart_time_zone_name",
                "th_time_zone_name",
            ],
        )
        writer.writeheader()
        for row in log_rows:
            writer.writerow(row)

    print(f"cases: {len(log_rows)}")
    print(f"out:   {out_dir}")
    print(f"log:   {log_csv}")


if __name__ == "__main__":
    main()
