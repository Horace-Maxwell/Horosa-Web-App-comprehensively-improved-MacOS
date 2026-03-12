#!/usr/bin/env python3
"""Enumerate top-bar chart display / planet / aspect selectors on release builds."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except Exception as exc:  # pragma: no cover
    print(json.dumps({"status": "skipped", "reason": f"playwright unavailable: {exc}"}, ensure_ascii=False))
    raise SystemExit(0)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime"
JSON_PATH = RUNTIME_DIR / "browser_topbar_full_enumeration_check.json"

CHART_DISPLAY_3D_PREFIX = "三维盘"
CHART_DISPLAY_PD_ONLY = "主/界限法显示界限法"
IGNORED_REMOTE_URL_SNIPPETS = (
    "jsapi-data",
    "amap.com/tile/",
    "chart3d.horosa.com/gltf/",
)


def click_visible_text(page, label: str, *, exact: bool = True, timeout_ms: int = 12_000) -> bool:
    locator = page.get_by_text(label, exact=exact)
    for idx in range(locator.count()):
        item = locator.nth(idx)
        try:
            if not item.is_visible():
                continue
            item.scroll_into_view_if_needed(timeout=timeout_ms)
            try:
                item.click(timeout=timeout_ms)
            except Exception:
                item.click(timeout=timeout_ms, force=True)
            page.wait_for_timeout(500)
            return True
        except Exception:
            continue
    return False


def click_top_button(page, label: str) -> None:
    clicked = page.evaluate(
        """
        (targetLabel) => {
          const normalize = (txt) => (txt || '').replace(/\\s+/g, '');
          const visible = (el) => {
            if (!el) return false;
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
          };
          const target = Array.from(document.querySelectorAll('button')).find((btn) => visible(btn) && normalize(btn.innerText) === targetLabel);
          if (!target) {
            return false;
          }
          target.click();
          return true;
        }
        """,
        label,
    )
    if not clicked:
        raise AssertionError(f"top button not clickable: {label}")
    page.wait_for_timeout(700)


def close_top_drawer(page) -> None:
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)


def visible_drawer(page, title: str):
    return page.locator(".ant-drawer.ant-drawer-open").filter(has=page.locator(".ant-drawer-title", has_text=title)).first


def click_drawer_tab(drawer, label: str) -> None:
    clicked = drawer.evaluate(
        """
        (el, targetLabel) => {
          const normalize = (txt) => (txt || '').replace(/\\s+/g, '');
          const visible = (node) => {
            if (!node) return false;
            const rect = node.getBoundingClientRect();
            const style = window.getComputedStyle(node);
            return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
          };
          const tabs = Array.from(el.querySelectorAll('.ant-tabs-tab'));
          const target = tabs.find((tab) => visible(tab) && normalize(tab.innerText) === targetLabel);
          if (!target) {
            return false;
          }
          target.click();
          return true;
        }
        """,
        label,
    )
    if not clicked:
        raise AssertionError(f"drawer tab not clickable: {label}")


def normalize_global_setup(page) -> dict:
    return page.evaluate(
        """
        () => {
          try {
            const raw = localStorage.getItem('globalSetup');
            return raw ? JSON.parse(raw) : {};
          } catch (err) {
            return {};
          }
        }
        """
    ) or {}


def normalize_aspects(page) -> list:
    return page.evaluate(
        """
        () => {
          try {
            const raw = localStorage.getItem('aspects');
            return raw ? JSON.parse(raw) : [];
          } catch (err) {
            return [];
          }
        }
        """
    ) or []


def svg_metrics(page) -> dict:
    return page.evaluate(
        """
        () => {
          const visible = (el) => {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
          };
          const svgs = Array.from(document.querySelectorAll('svg')).filter(visible);
          if (!svgs.length) {
            return { markupLength: 0, pathCount: 0, textCount: 0 };
          }
          svgs.sort((a, b) => {
            const ra = a.getBoundingClientRect();
            const rb = b.getBoundingClientRect();
            return (rb.width * rb.height) - (ra.width * ra.height);
          });
          const best = svgs[0];
          return {
            markupLength: (best.innerHTML || '').length,
            pathCount: best.querySelectorAll('path,line,polyline').length,
            textCount: best.querySelectorAll('text').length,
          };
        }
        """
    )


def screenshot_hash(page) -> str:
    shot = page.screenshot(full_page=False)
    return hashlib.sha256(shot).hexdigest()


def ensure_chart_context(page, context_key: str) -> None:
    if context_key == "astro":
        if not click_visible_text(page, "星盘"):
            raise AssertionError("cannot open 星盘")
        if not click_visible_text(page, "信息"):
            raise AssertionError("cannot open 星盘 -> 信息")
        page.wait_for_timeout(1_000)
        return
    if context_key == "3d":
        if not click_visible_text(page, "三维盘"):
            raise AssertionError("cannot open 三维盘")
        if not click_visible_text(page, "信息"):
            raise AssertionError("cannot open 三维盘 -> 信息")
        page.wait_for_timeout(1_500)
        return
    if context_key == "pd":
        if not click_visible_text(page, "推运盘"):
            raise AssertionError("cannot open 推运盘")
        if not click_visible_text(page, "主/界限法"):
            raise AssertionError("cannot open 主/界限法")
        page.wait_for_timeout(1_500)
        return
    raise AssertionError(f"unknown context: {context_key}")


def enumerate_chart_display(page, result: dict) -> None:
    ensure_chart_context(page, "astro")
    click_top_button(page, "星盘组件")
    drawer = visible_drawer(page, "星盘组件")
    labels = []
    wrappers = drawer.locator(".ant-checkbox-wrapper")
    for idx in range(wrappers.count()):
        txt = " ".join(wrappers.nth(idx).inner_text().split())
        if txt:
            labels.append(txt)
    close_top_drawer(page)

    items = []
    for idx, label in enumerate(labels, start=1):
        if label.startswith(CHART_DISPLAY_3D_PREFIX):
            context_key = "3d"
        elif label == CHART_DISPLAY_PD_ONLY:
            context_key = "pd"
        else:
            context_key = "astro"

        print(f"topbar chart-display {idx}/{len(labels)}: {label} [{context_key}]")
        ensure_chart_context(page, context_key)
        before_setup = normalize_global_setup(page)
        before_metrics = svg_metrics(page)
        before_hash = screenshot_hash(page)

        click_top_button(page, "星盘组件")
        drawer = visible_drawer(page, "星盘组件")
        target = drawer.get_by_text(label, exact=True)
        if target.count() == 0:
            raise AssertionError(f"chart display item missing: {label}")
        target.first.click(force=True)
        page.wait_for_timeout(900)
        close_top_drawer(page)
        page.wait_for_timeout(1_000)

        after_setup = normalize_global_setup(page)
        after_metrics = svg_metrics(page)
        after_hash = screenshot_hash(page)

        if label == CHART_DISPLAY_PD_ONLY:
            state_changed = (before_setup.get("showPdBounds", 1) != after_setup.get("showPdBounds", 1))
        elif label == "星曜附带后天宫信息":
            state_changed = (before_setup.get("showPlanetHouseInfo", 0) != after_setup.get("showPlanetHouseInfo", 0))
        elif label == "是否显示星/宫/座/相释义":
            state_changed = (before_setup.get("showAstroMeaning", 0) != after_setup.get("showAstroMeaning", 0))
        elif label == "仅按照本垣擢升计算互容接纳":
            state_changed = (before_setup.get("showOnlyRulExaltReception", 0) != after_setup.get("showOnlyRulExaltReception", 0))
        else:
            before_list = before_setup.get("chartDisplay") or []
            after_list = after_setup.get("chartDisplay") or []
            state_changed = before_list != after_list

        visual_changed = after_hash != before_hash or after_metrics != before_metrics

        items.append(
            {
                "label": label,
                "context": context_key,
                "stateChanged": state_changed,
                "visualChanged": visual_changed,
                "beforeMetrics": before_metrics,
                "afterMetrics": after_metrics,
                "beforeHash": before_hash,
                "afterHash": after_hash,
            }
        )

        click_top_button(page, "星盘组件")
        drawer = visible_drawer(page, "星盘组件")
        drawer.get_by_text(label, exact=True).first.click(force=True)
        page.wait_for_timeout(500)
        close_top_drawer(page)
        page.wait_for_timeout(800)

        if not state_changed:
            raise AssertionError(f"chart display item did not update state: {label}")

    result["checks"]["chart_display_all"] = {"count": len(items), "items": items}


def enumerate_planets(page, result: dict) -> None:
    ensure_chart_context(page, "astro")
    click_top_button(page, "行星选择")
    drawer = visible_drawer(page, "行星选择")
    rows = drawer.locator(".ant-tabs-tabpane-active .ant-checkbox-wrapper")
    planet_labels = []
    for idx in range(rows.count()):
        txt = " ".join(rows.nth(idx).inner_text().split())
        if txt:
            planet_labels.append(txt)
    close_top_drawer(page)

    items = []
    for idx, label in enumerate(planet_labels, start=1):
        print(f"topbar planet {idx}/{len(planet_labels)}: {label}")
        ensure_chart_context(page, "astro")
        before_setup = normalize_global_setup(page)
        before_metrics = svg_metrics(page)
        before_hash = screenshot_hash(page)

        click_top_button(page, "行星选择")
        drawer = visible_drawer(page, "行星选择")
        rows = drawer.locator(".ant-tabs-tabpane-active .ant-checkbox-wrapper")
        rows.nth(idx - 1).click(force=True)
        page.wait_for_timeout(900)
        close_top_drawer(page)
        page.wait_for_timeout(1_000)

        after_setup = normalize_global_setup(page)
        after_metrics = svg_metrics(page)
        after_hash = screenshot_hash(page)
        state_changed = (before_setup.get("planetDisplay") or []) != (after_setup.get("planetDisplay") or [])
        visual_changed = after_hash != before_hash or after_metrics != before_metrics
        items.append(
            {
                "label": label,
                "stateChanged": state_changed,
                "visualChanged": visual_changed,
                "beforeMetrics": before_metrics,
                "afterMetrics": after_metrics,
                "beforeHash": before_hash,
                "afterHash": after_hash,
            }
        )

        click_top_button(page, "行星选择")
        drawer = visible_drawer(page, "行星选择")
        drawer.locator(".ant-tabs-tabpane-active .ant-checkbox-wrapper").nth(idx - 1).click(force=True)
        page.wait_for_timeout(500)
        close_top_drawer(page)
        page.wait_for_timeout(800)

        if not state_changed:
            raise AssertionError(f"planet selector item did not update state: {label}")

    result["checks"]["planet_selector_planets"] = {"count": len(items), "items": items}


def enumerate_lots(page, result: dict) -> None:
    ensure_chart_context(page, "astro")
    click_top_button(page, "行星选择")
    drawer = visible_drawer(page, "行星选择")
    click_drawer_tab(drawer, "希腊点")
    page.wait_for_timeout(700)
    rows = drawer.locator(".ant-tabs-tabpane-active .ant-checkbox-wrapper")
    lot_labels = []
    for idx in range(rows.count()):
        txt = " ".join(rows.nth(idx).inner_text().split())
        if txt:
            lot_labels.append(txt)
    close_top_drawer(page)

    items = []
    for idx, label in enumerate(lot_labels, start=1):
        print(f"topbar lot {idx}/{len(lot_labels)}: {label}")
        ensure_chart_context(page, "astro")
        before_setup = normalize_global_setup(page)
        before_metrics = svg_metrics(page)
        before_hash = screenshot_hash(page)

        click_top_button(page, "行星选择")
        drawer = visible_drawer(page, "行星选择")
        click_drawer_tab(drawer, "希腊点")
        page.wait_for_timeout(500)
        drawer.locator(".ant-tabs-tabpane-active .ant-checkbox-wrapper").nth(idx - 1).click(force=True)
        page.wait_for_timeout(900)
        close_top_drawer(page)
        page.wait_for_timeout(1_000)

        after_setup = normalize_global_setup(page)
        after_metrics = svg_metrics(page)
        after_hash = screenshot_hash(page)
        state_changed = (before_setup.get("lotsDisplay") or []) != (after_setup.get("lotsDisplay") or [])
        visual_changed = after_hash != before_hash or after_metrics != before_metrics
        items.append(
            {
                "label": label,
                "stateChanged": state_changed,
                "visualChanged": visual_changed,
                "beforeMetrics": before_metrics,
                "afterMetrics": after_metrics,
                "beforeHash": before_hash,
                "afterHash": after_hash,
            }
        )

        click_top_button(page, "行星选择")
        drawer = visible_drawer(page, "行星选择")
        click_drawer_tab(drawer, "希腊点")
        page.wait_for_timeout(500)
        drawer.locator(".ant-tabs-tabpane-active .ant-checkbox-wrapper").nth(idx - 1).click(force=True)
        page.wait_for_timeout(500)
        close_top_drawer(page)
        page.wait_for_timeout(800)

        if not state_changed:
            raise AssertionError(f"lot selector item did not update state: {label}")

    result["checks"]["planet_selector_lots"] = {"count": len(items), "items": items}


def enumerate_aspects(page, result: dict) -> None:
    ensure_chart_context(page, "astro")
    click_top_button(page, "相位选择")
    drawer = visible_drawer(page, "相位选择")
    rows = drawer.locator(".ant-checkbox-wrapper")
    labels = []
    for idx in range(rows.count()):
        txt = " ".join(rows.nth(idx).inner_text().split())
        if txt:
            labels.append(txt)
    close_top_drawer(page)

    items = []
    for idx, label in enumerate(labels, start=1):
        print(f"topbar aspect {idx}/{len(labels)}: {label}")
        ensure_chart_context(page, "astro")
        before_aspects = normalize_aspects(page)
        before_metrics = svg_metrics(page)
        before_hash = screenshot_hash(page)

        click_top_button(page, "相位选择")
        drawer = visible_drawer(page, "相位选择")
        drawer.locator(".ant-checkbox-wrapper").nth(idx - 1).click(force=True)
        page.wait_for_timeout(900)
        close_top_drawer(page)
        page.wait_for_timeout(1_000)

        after_aspects = normalize_aspects(page)
        after_metrics = svg_metrics(page)
        after_hash = screenshot_hash(page)
        state_changed = before_aspects != after_aspects
        visual_changed = after_hash != before_hash or after_metrics != before_metrics
        items.append(
            {
                "label": label,
                "stateChanged": state_changed,
                "visualChanged": visual_changed,
                "beforeAspects": before_aspects,
                "afterAspects": after_aspects,
                "beforeMetrics": before_metrics,
                "afterMetrics": after_metrics,
                "beforeHash": before_hash,
                "afterHash": after_hash,
            }
        )

        click_top_button(page, "相位选择")
        drawer = visible_drawer(page, "相位选择")
        drawer.locator(".ant-checkbox-wrapper").nth(idx - 1).click(force=True)
        page.wait_for_timeout(500)
        close_top_drawer(page)
        page.wait_for_timeout(800)

        if not state_changed:
            raise AssertionError(f"aspect selector item did not update state: {label}")

    result["checks"]["aspect_selector_all"] = {"count": len(items), "items": items}


def main() -> None:
    web_port = os.environ.get("HOROSA_WEB_PORT", "8000")
    server_root = os.environ.get("HOROSA_SERVER_ROOT", f"http://127.0.0.1:{os.environ.get('HOROSA_SERVER_PORT', '9999')}")
    base_url = os.environ.get(
        "HOROSA_WEB_ROOT",
        f"http://127.0.0.1:{web_port}/index.html?srv={server_root.replace(':', '%3A').replace('/', '%2F')}&v={int(time.time())}",
    )

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    result = {
        "status": "ok",
        "base_url": base_url,
        "server_root": server_root,
        "checks": {},
        "dialogs": [],
        "pageErrors": [],
        "consoleErrors": [],
        "requestFailures": [],
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1720, "height": 1184})
            page.on("dialog", lambda dialog: (result["dialogs"].append(dialog.message), dialog.dismiss()))
            page.on("pageerror", lambda exc: result["pageErrors"].append(str(exc)))
            page.on("console", lambda msg: result["consoleErrors"].append(msg.text) if msg.type == "error" else None)
            page.on("requestfailed", lambda req: result["requestFailures"].append({"url": req.url, "failure": req.failure}))

            page.goto(base_url, wait_until="domcontentloaded", timeout=120_000)
            page.wait_for_timeout(5_000)

            enumerate_chart_display(page, result)
            enumerate_planets(page, result)
            enumerate_lots(page, result)
            enumerate_aspects(page, result)

            browser.close()
    except Exception as exc:
        result["status"] = "error"
        result["fatalError"] = str(exc)

    local_request_failures = []
    remote_request_warnings = []
    for failure in result["requestFailures"]:
        url = failure.get("url", "")
        if any(snippet in url for snippet in IGNORED_REMOTE_URL_SNIPPETS):
            remote_request_warnings.append(failure)
        else:
            local_request_failures.append(failure)
    result["requestFailures"] = local_request_failures
    if remote_request_warnings:
        result.setdefault("warnings", []).append(
            {
                "type": "remote_request_failures",
                "count": len(remote_request_warnings),
                "samples": remote_request_warnings[:10],
            }
        )

    fatal_console_errors = []
    ignored_console_errors = []
    for message in result["consoleErrors"]:
        normalized = f"{message or ''}"
        if "Failed to load resource" in normalized and (
            "ERR_CONNECTION_TIMED_OUT" in normalized
            or "ERR_TIMED_OUT" in normalized
        ):
            ignored_console_errors.append(normalized)
        else:
            fatal_console_errors.append(normalized)
    result["consoleErrors"] = fatal_console_errors
    if ignored_console_errors:
        result.setdefault("warnings", []).append(
            {
                "type": "remote_console_errors",
                "count": len(ignored_console_errors),
                "samples": ignored_console_errors[:10],
            }
        )

    result["status"] = "ok"
    if result["dialogs"] or result["pageErrors"] or result["consoleErrors"] or result["requestFailures"]:
        result["status"] = "error"

    JSON_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["status"] != "ok" else 0)


if __name__ == "__main__":
    main()
