#!/usr/bin/env python3
"""Ensure the desktop shell no longer produces an outer window scrollbar."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except Exception as exc:  # pragma: no cover
    print(json.dumps({"status": "skipped", "reason": f"playwright unavailable: {exc}"}, ensure_ascii=False))
    raise SystemExit(0)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime"


def click_visible_text(page, label: str, *, exact: bool = True, timeout_ms: int = 12000) -> bool:
    locator = page.get_by_text(label, exact=exact)
    count = locator.count()
    for idx in range(count):
        item = locator.nth(idx)
        try:
            if not item.is_visible():
                continue
            item.scroll_into_view_if_needed(timeout=timeout_ms)
            try:
                item.click(timeout=timeout_ms)
            except Exception:
                item.click(timeout=timeout_ms, force=True)
            page.wait_for_timeout(1200)
            return True
        except Exception:
            continue
    return False


def collect_shell_metrics(page) -> dict:
    return page.evaluate(
        """
        () => {
          const doc = document.documentElement;
          const body = document.body;
          const main = document.getElementById('mainContent');
          const footer = document.getElementById('globalFooter');
          window.scrollTo(0, 160);
          const attemptedScrollY = window.scrollY;
          window.scrollTo(0, 0);
          const toMetrics = (el) => el ? {
            clientHeight: el.clientHeight,
            scrollHeight: el.scrollHeight,
            clientWidth: el.clientWidth,
            scrollWidth: el.scrollWidth,
            overflowY: getComputedStyle(el).overflowY,
            overflowX: getComputedStyle(el).overflowX,
          } : null;
          return {
            viewport: {
              width: window.innerWidth,
              height: window.innerHeight,
            },
            documentElement: toMetrics(doc),
            body: toMetrics(body),
            mainContent: toMetrics(main),
            footerRect: footer ? footer.getBoundingClientRect().toJSON() : null,
            overflowDelta: {
              document: doc.scrollHeight - doc.clientHeight,
              body: body.scrollHeight - body.clientHeight,
            },
            canWindowScroll: attemptedScrollY > 0,
            windowScrollY: window.scrollY,
          };
        }
        """
    )


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_case(page, result: dict, key: str, first_label: str, second_label: str | None = None) -> None:
    ensure(click_visible_text(page, first_label), f"cannot open {first_label}")
    if second_label:
        ensure(click_visible_text(page, second_label, exact=False), f"cannot open {second_label}")
    metrics = collect_shell_metrics(page)
    result[key] = metrics
    ensure(not metrics["canWindowScroll"], f"outer shell still scrolls on {key}")
    ensure(metrics["windowScrollY"] == 0, f"window scrolled unexpectedly on {key}")


def main() -> None:
    web_port = os.environ.get("HOROSA_WEB_PORT", "8000")
    server_root = os.environ.get("HOROSA_SERVER_ROOT", f"http://127.0.0.1:{os.environ.get('HOROSA_SERVER_PORT', '9999')}")
    base_url = os.environ.get(
        "HOROSA_WEB_ROOT",
        f"http://127.0.0.1:{web_port}/index.html?srv={server_root.replace(':', '%3A').replace('/', '%2F')}&v={int(time.time())}",
    )
    json_path = Path(os.environ.get("HOROSA_OUTER_SHELL_SCROLL_JSON", str(RUNTIME_DIR / "browser_outer_shell_scroll_check.json")))
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    result: dict = {
        "status": "ok",
        "base_url": base_url,
        "checks": {},
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1720, "height": 1184})
            page.goto(base_url, wait_until="domcontentloaded", timeout=120000)
            page.wait_for_timeout(5000)

            result["checks"]["initial"] = collect_shell_metrics(page)
            ensure(not result["checks"]["initial"]["canWindowScroll"], "outer shell still scrolls on initial page")

            check_case(page, result["checks"], "solar_arc", "推运盘", "太阳弧")
            check_case(page, result["checks"], "jinkou", "易与三式", "金口诀")
            check_case(page, result["checks"], "bazi", "八字紫微", "八字")
            check_case(page, result["checks"], "fengshui", "风水")

            browser.close()
    except Exception as exc:
        result["status"] = "error"
        result["error"] = str(exc)

    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result.get("status") == "ok" else 1)


if __name__ == "__main__":
    main()
