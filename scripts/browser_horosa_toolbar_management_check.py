#!/usr/bin/env python3
"""Deeper browser-level UI verification for Horosa toolbar, drawers, and local management flows."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
except Exception as exc:  # pragma: no cover - optional dependency path
    print(json.dumps({"status": "skipped", "reason": f"playwright unavailable: {exc}"}, ensure_ascii=False))
    raise SystemExit(0)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime"
JSON_PATH = RUNTIME_DIR / "browser_horosa_toolbar_management_check.json"
SCREENSHOT_PATH = RUNTIME_DIR / "browser_horosa_toolbar_management_check.png"

SEED_CHARTS = [
    {
        "cid": "local-codex-seed-a",
        "name": "Codex Seed Alpha",
        "birth": "1992-06-15 08:30:00",
        "zone": "+08:00",
        "lat": "31n13",
        "lon": "121e28",
        "gpsLat": 31.216667,
        "gpsLon": 121.466667,
        "pos": "Shanghai",
        "gender": 1,
        "isPub": 0,
        "group": "[\"codex\"]",
        "creator": "local",
        "updateTime": "2026-03-09 22:00:00",
    },
    {
        "cid": "local-codex-seed-b",
        "name": "Codex Seed Beta",
        "birth": "1994-11-20 14:10:00",
        "zone": "+00:00",
        "lat": "51n30",
        "lon": "0w07",
        "gpsLat": 51.5,
        "gpsLon": -0.116667,
        "pos": "London",
        "gender": 0,
        "isPub": 0,
        "group": "[\"codex\"]",
        "creator": "local",
        "updateTime": "2026-03-09 22:05:00",
    },
]

SEED_CASES = [
    {
        "cid": "local-codex-case-a",
        "event": "Codex Seed Case",
        "caseType": "liuyao",
        "divTime": "2026-03-09 10:10:00",
        "zone": "+08:00",
        "lat": "31n13",
        "lon": "121e28",
        "gpsLat": 31.216667,
        "gpsLon": 121.466667,
        "pos": "Shanghai",
        "isPub": 0,
        "group": "[\"codex\"]",
        "creator": "local",
        "updateTime": "2026-03-09 22:10:00",
    }
]

TOOL_TABS = [
    "纳音五行",
    "计算器",
    "日期计算",
    "地平坐标",
    "黄赤坐标",
    "八字反查",
    "八字格局",
    "八卦类象",
    "十二串宫",
    "八字规则",
]

RELATIVE_TABS = ["比较盘", "组合盘", "影响盘", "时空中点盘", "马克斯盘"]

IGNORED_REMOTE_URL_SNIPPETS = (
    "jsapi-data",
    "amap.com/tile/",
    "chart3d.horosa.com/gltf/",
)


def click_visible_text(page, label: str, *, exact: bool = True, timeout_ms: int = 10_000) -> bool:
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


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def visible_drawer(page, title: str):
    return page.locator(".ant-drawer.ant-drawer-open").filter(has=page.locator(".ant-drawer-title", has_text=title)).first


def close_top_visible_drawer(page) -> None:
    before = page.locator(".ant-drawer.ant-drawer-open").count()
    ensure(before > 0, "no visible drawer to close")
    page.keyboard.press("Escape")
    page.wait_for_timeout(400)
    after = page.locator(".ant-drawer.ant-drawer-open").count()
    if after < before:
        return
    drawer = page.locator(".ant-drawer.ant-drawer-open").nth(before - 1)
    clicked = drawer.evaluate(
        """
        (el) => {
          const btn = el.querySelector('.ant-drawer-close');
          if (!btn) {
            return false;
          }
          btn.click();
          return true;
        }
        """
    )
    ensure(clicked, "no visible drawer close button")
    page.wait_for_timeout(400)


def open_manage_menu(page) -> None:
    ensure(click_visible_text(page, "管理"), "cannot open 管理 dropdown")
    page.wait_for_timeout(400)
    ensure(page.locator(".ant-dropdown:visible").count() > 0, "manage dropdown not visible")


def open_dropdown_button(page, label: str) -> None:
    button = page.get_by_role("button", name=label)
    ensure(button.count() > 0, f"missing top button: {label}")
    button.first.click(force=True)
    page.wait_for_timeout(400)


def click_manage_item(page, label: str) -> None:
    open_manage_menu(page)
    menu = page.locator(".ant-dropdown:visible").first
    menu.get_by_text(label, exact=True).click(force=True)
    page.wait_for_timeout(700)


def get_ai_snapshot(page) -> dict:
    return page.evaluate(
        """
        () => {
          const raw = localStorage.getItem('horosa.ai.snapshot.astro.v1');
          if (!raw) {
            return {};
          }
          try {
            return JSON.parse(raw);
          } catch (err) {
            return { raw };
          }
        }
        """
    ) or {}


def get_current_theme_text(page) -> str:
    locator = page.locator(".ant-select-selection-item").filter(has_text="主题").first
    ensure(locator.count() > 0, "theme selection item missing")
    return " ".join(locator.inner_text().split())


def checked_checkbox_count(container) -> int:
    return container.locator("input[type='checkbox']:checked").count()


def get_visible_table_row_count(page) -> int:
    return int(
        page.evaluate(
            """
            () => Array.from(document.querySelectorAll('tbody tr')).filter((row) => {
              const rect = row.getBoundingClientRect();
              const style = window.getComputedStyle(row);
              return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
            }).length
            """
        )
    )


def get_visible_svg_metrics(page) -> dict:
    return page.evaluate(
        """
        () => {
          const svgs = Array.from(document.querySelectorAll('svg')).filter((el) => {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
          });
          if (!svgs.length) {
            return { markupLength: 0, pathCount: 0, textCount: 0 };
          }
          let best = svgs[0];
          let area = 0;
          svgs.forEach((el) => {
            const rect = el.getBoundingClientRect();
            const currentArea = rect.width * rect.height;
            if (currentArea > area) {
              best = el;
              area = currentArea;
            }
          });
          return {
            markupLength: (best.innerHTML || '').length,
            pathCount: best.querySelectorAll('path,line,polyline').length,
            textCount: best.querySelectorAll('text').length,
          };
        }
        """
    )


def search_in_visible_input(page, placeholder: str, value: str) -> None:
    locator = page.get_by_placeholder(placeholder)
    ensure(locator.count() > 0, f"missing input: {placeholder}")
    locator.first.fill(value)
    locator.first.press("Enter")
    page.wait_for_timeout(800)


def select_chart_from_modal(page, placeholder: str, chart_name: str) -> None:
    input_box = page.get_by_placeholder(placeholder)
    ensure(input_box.count() > 0, f"missing relation input: {placeholder}")
    input_box.first.click(force=True)
    modal = page.locator(".ant-modal:visible").filter(has=page.get_by_text("星盘查找", exact=True)).first
    ensure(modal.count() > 0, "chart search modal not visible")
    modal.get_by_placeholder("星盘名称").fill(chart_name)
    modal.get_by_placeholder("星盘名称").press("Enter")
    page.wait_for_timeout(900)
    row = modal.locator("tbody tr").filter(has=page.get_by_text(chart_name, exact=True)).first
    ensure(row.count() > 0, f"chart row missing: {chart_name}")
    row.click(force=True)
    page.wait_for_timeout(300)
    click_normalized_modal_button(page, "确定")
    page.wait_for_timeout(800)


def click_row_action(row_locator, index: int) -> None:
    links = row_locator.locator("a")
    ensure(links.count() > index, f"missing row action index={index}")
    links.nth(index).click(force=True)


def click_normalized_button(container, label: str) -> None:
    clicked = container.evaluate(
        """
        (el, targetLabel) => {
          const buttons = Array.from(el.querySelectorAll('button'));
          const normalized = (txt) => (txt || '').replace(/\\s+/g, '');
          const target = buttons.find((btn) => normalized(btn.innerText) === targetLabel);
          if (!target) {
            return false;
          }
          target.click();
          return true;
        }
        """,
        label,
    )
    ensure(clicked, f"button not clickable: {label}")


def click_normalized_page_button(page, label: str) -> None:
    clicked = page.evaluate(
        """
        (targetLabel) => {
          const buttons = Array.from(document.querySelectorAll('button'));
          const normalized = (txt) => (txt || '').replace(/\\s+/g, '');
          const visible = (el) => {
            if (!el) return false;
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
          };
          const target = buttons.find((btn) => visible(btn) && normalized(btn.innerText) === targetLabel);
          if (!target) {
            return false;
          }
          target.click();
          return true;
        }
        """,
        label,
    )
    ensure(clicked, f"top button not clickable: {label}")


def click_normalized_modal_button(page, label: str) -> None:
    clicked = page.evaluate(
        """
        (targetLabel) => {
          const normalized = (txt) => (txt || '').replace(/\\s+/g, '');
          const visible = (el) => {
            if (!el) return false;
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
          };
          const modals = Array.from(document.querySelectorAll('.ant-modal')).filter(visible);
          const modal = modals[modals.length - 1];
          if (!modal) {
            return false;
          }
          const buttons = Array.from(modal.querySelectorAll('button'));
          const target = buttons.find((btn) => normalized(btn.innerText) === targetLabel);
          if (!target) {
            return false;
          }
          target.click();
          return true;
        }
        """,
        label,
    )
    ensure(clicked, f"modal button not clickable: {label}")


def add_init_storage(context) -> None:
    payload = json.dumps({"charts": SEED_CHARTS, "cases": SEED_CASES}, ensure_ascii=False)
    context.add_init_script(
        f"""
        (() => {{
          const payload = {payload};
          localStorage.clear();
          localStorage.setItem('horosa.localCharts.v1', JSON.stringify(payload.charts));
          localStorage.setItem('horosa.localCases.v1', JSON.stringify(payload.cases));
        }})();
        """
    )


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
        "dialogs": [],
        "pageErrors": [],
        "consoleErrors": [],
        "requestFailures": [],
        "warnings": [],
        "checks": {},
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1720, "height": 1184}, accept_downloads=True)
        add_init_storage(context)
        page = context.new_page()

        page.on("dialog", lambda dialog: (result["dialogs"].append(dialog.message), dialog.dismiss()))
        page.on("pageerror", lambda exc: result["pageErrors"].append(str(exc)))

        def on_console(msg):
            if msg.type == "error":
                result["consoleErrors"].append(msg.text)

        page.on("console", on_console)

        def on_request_failed(req):
            result["requestFailures"].append({"url": req.url, "failure": req.failure})

        page.on("requestfailed", on_request_failed)

        page.goto(base_url, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(5_000)

        # Top search/config drawer.
        search_icon = page.locator(".anticon-search").first
        ensure(search_icon.count() > 0, "top search icon missing")
        search_icon.click(force=True)
        page.wait_for_timeout(700)
        ensure(visible_drawer(page, "星盘配置").count() > 0, "星盘配置 drawer not visible")
        ensure(page.locator(".ant-drawer:visible").get_by_text("经纬度选择", exact=True).count() > 0, "星盘配置缺少经纬度选择")
        result["checks"]["query_drawer"] = {"ok": True}
        close_top_visible_drawer(page)

        # Theme switch.
        before_theme = get_current_theme_text(page)
        theme_selector = page.locator(".ant-select").filter(has=page.get_by_text(before_theme, exact=True)).first.locator(".ant-select-selector")
        theme_selector.click(force=True)
        page.wait_for_timeout(400)
        target_theme = "主题银河" if before_theme != "主题银河" else "主题和睿"
        page.locator(".ant-select-dropdown:visible").get_by_text(target_theme, exact=True).click(force=True)
        page.wait_for_timeout(600)
        after_theme = get_current_theme_text(page)
        ensure(after_theme != before_theme, "theme selector did not update app state")
        result["checks"]["theme_switch"] = {"before": before_theme, "after": after_theme, "targetTheme": target_theme}

        # AI export settings modal.
        click_normalized_page_button(page, "AI导出设置")
        page.wait_for_timeout(700)
        modal = page.locator(".ant-modal:visible").filter(has=page.get_by_text("AI导出设置", exact=True)).first
        ensure(modal.count() > 0, "AI导出设置 modal not visible")
        modal_text = "".join(modal.inner_text().split())
        for label in ["全选", "清空", "恢复默认"]:
            ensure(label in modal_text, f"AI导出设置缺少操作项: {label}")
        page.keyboard.press("Escape")
        page.wait_for_timeout(600)
        ensure(page.locator(".ant-modal:visible").count() == 0, "AI导出设置 modal did not close")
        result["checks"]["ai_export_settings"] = {"ok": True}

        # AI export dropdown items.
        open_dropdown_button(page, "AI导出")
        dropdown = page.locator(".ant-dropdown:visible").first
        ai_items = ["一键复制+导出全部", "复制AI纯文字", "导出TXT", "导出Word", "导出PDF"]
        for item in ai_items:
            ensure(dropdown.get_by_text(item, exact=True).count() > 0, f"missing AI export item: {item}")
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        result["checks"]["ai_export_menu"] = {"items": ai_items}

        # Chart management add/edit/select.
        click_manage_item(page, "管理命盘")
        ensure(visible_drawer(page, "星盘列表").count() > 0, "星盘列表 drawer not visible")
        chart_list_drawer = visible_drawer(page, "星盘列表")
        ensure(chart_list_drawer.get_by_text("Codex Seed Alpha", exact=True).count() > 0, "seed chart A missing")
        ensure(chart_list_drawer.get_by_text("Codex Seed Beta", exact=True).count() > 0, "seed chart B missing")

        chart_add_name = "Codex UI Added Chart"
        chart_edit_name = "Codex UI Edited Chart"
        chart_list_drawer.get_by_role("button", name="添加星盘").click(force=True)
        page.wait_for_timeout(700)
        chart_add_drawer = visible_drawer(page, "添加星盘")
        ensure(chart_add_drawer.count() > 0, "添加星盘 drawer not visible")
        chart_add_drawer.get_by_placeholder("姓名").fill(chart_add_name)
        chart_add_drawer.get_by_placeholder("出生地").fill("Codex Birth Place")
        click_normalized_button(chart_add_drawer, "提交")
        page.wait_for_timeout(1_200)
        ensure(visible_drawer(page, "星盘列表").count() > 0, "did not return to 星盘列表 after adding chart")
        ensure(page.get_by_text(chart_add_name, exact=True).count() > 0, "added chart missing in list")
        search_in_visible_input(page, "以姓名进行检索", chart_add_name)
        row = page.locator("tbody tr").filter(has=page.get_by_text(chart_add_name, exact=True)).first
        ensure(row.count() > 0, "cannot find added chart row for edit")
        click_row_action(row, 1)
        page.wait_for_timeout(700)
        chart_edit_drawer = visible_drawer(page, "编辑星盘")
        ensure(chart_edit_drawer.count() > 0, "编辑星盘 drawer not visible")
        name_input = chart_edit_drawer.get_by_placeholder("姓名")
        name_input.fill("")
        name_input.fill(chart_edit_name)
        click_normalized_button(chart_edit_drawer, "提交")
        page.wait_for_timeout(1_200)
        search_in_visible_input(page, "以姓名进行检索", chart_edit_name)
        row = page.locator("tbody tr").filter(has=page.get_by_text(chart_edit_name, exact=True)).first
        ensure(row.count() > 0, "edited chart missing in list")
        click_row_action(row, 0)
        page.wait_for_timeout(800)
        result["checks"]["chart_management"] = {
            "added": chart_add_name,
            "edited": chart_edit_name,
            "selected": chart_edit_name,
        }
        close_top_visible_drawer(page)

        # Memo drawer should be writable after selecting a local chart.
        click_normalized_page_button(page, "批注")
        page.wait_for_timeout(700)
        memo_drawer = visible_drawer(page, "命盘批注")
        ensure(memo_drawer.count() > 0, "命盘批注 drawer not visible")
        memo_text = "".join(memo_drawer.inner_text().split())
        ensure("保存" in memo_text, "memo save button missing after selecting local chart")
        ensure(memo_drawer.get_by_text(chart_edit_name, exact=True).count() > 0, "memo drawer did not bind selected chart name")
        result["checks"]["memo_drawer"] = {"ok": True, "chart": chart_edit_name}
        close_top_visible_drawer(page)

        # Tool drawer tabs.
        click_normalized_page_button(page, "小工具")
        page.wait_for_timeout(700)
        ensure(visible_drawer(page, "小工具").count() > 0, "小工具 drawer not visible")
        clicked_tool_tabs = []
        for label in TOOL_TABS:
            ensure(click_visible_text(page, label), f"cannot open tool tab: {label}")
            clicked_tool_tabs.append(label)
        result["checks"]["tool_tabs"] = {"clicked": clicked_tool_tabs}
        close_top_visible_drawer(page)

        # New chart action should rebuild chart state.
        chart_snapshot_before = get_ai_snapshot(page)
        click_normalized_page_button(page, "新命盘")
        page.wait_for_function(
            """
            (beforeId) => {
              const raw = localStorage.getItem('horosa.ai.snapshot.astro.v1');
              if (!raw) return false;
              try {
                const parsed = JSON.parse(raw);
                return !!(parsed.chartId && parsed.chartId !== beforeId);
              } catch (err) {
                return false;
              }
            }
            """,
            arg=chart_snapshot_before.get("chartId"),
            timeout=120_000,
        )
        chart_snapshot_after = get_ai_snapshot(page)
        ensure(chart_snapshot_after.get("chartId") != chart_snapshot_before.get("chartId"), "新命盘 did not refresh AI snapshot chartId")
        result["checks"]["new_chart"] = {"before": chart_snapshot_before.get("chartId"), "after": chart_snapshot_after.get("chartId")}

        # Chart display selector should change chart SVG metrics.
        ensure(click_visible_text(page, "星盘"), "cannot switch to 星盘 before chart display test")
        ensure(click_visible_text(page, "信息"), "cannot switch 星盘 to 信息")
        page.wait_for_timeout(1_000)
        svg_before = get_visible_svg_metrics(page)
        click_normalized_page_button(page, "星盘组件")
        page.wait_for_timeout(700)
        chart_display_drawer = visible_drawer(page, "星盘组件")
        ensure(chart_display_drawer.count() > 0, "星盘组件 drawer not visible")
        checkbox_count_before = checked_checkbox_count(chart_display_drawer)
        chart_display_drawer.get_by_text("相位线", exact=True).click(force=True)
        page.wait_for_timeout(500)
        close_top_visible_drawer(page)
        page.wait_for_timeout(1_000)
        svg_after = get_visible_svg_metrics(page)
        ensure(svg_after != svg_before, "chart SVG metrics did not change after toggling 相位线")
        click_normalized_page_button(page, "星盘组件")
        page.wait_for_timeout(700)
        chart_display_drawer = visible_drawer(page, "星盘组件")
        ensure(checked_checkbox_count(chart_display_drawer) == checkbox_count_before - 1, "chart display checkbox count did not decrease")
        chart_display_drawer.get_by_text("相位线", exact=True).click(force=True)
        page.wait_for_timeout(300)
        close_top_visible_drawer(page)
        result["checks"]["chart_display_toggle"] = {"before": svg_before, "after": svg_after}

        # Planet selector should affect 星盘 -> 行星 list.
        ensure(click_visible_text(page, "信息"), "cannot switch 星盘 to 信息 before planet selector test")
        page.wait_for_timeout(800)
        planet_svg_before = get_visible_svg_metrics(page)
        click_normalized_page_button(page, "行星选择")
        page.wait_for_timeout(700)
        planet_drawer = visible_drawer(page, "行星选择")
        ensure(planet_drawer.count() > 0, "行星选择 drawer not visible")
        planet_checkboxes = planet_drawer.locator(".ant-tabs-tabpane-active input[type='checkbox']")
        ensure(planet_checkboxes.count() > 0, "planet checkboxes missing")
        planet_checked_before = checked_checkbox_count(planet_drawer.locator(".ant-tabs-tabpane-active"))
        planet_checkboxes.nth(0).click(force=True)
        page.wait_for_timeout(300)
        close_top_visible_drawer(page)
        page.wait_for_timeout(800)
        planet_svg_after = get_visible_svg_metrics(page)
        ensure(planet_svg_after != planet_svg_before, "planet selector did not change chart SVG metrics")
        click_normalized_page_button(page, "行星选择")
        page.wait_for_timeout(700)
        planet_drawer = visible_drawer(page, "行星选择")
        ensure(checked_checkbox_count(planet_drawer.locator(".ant-tabs-tabpane-active")) == planet_checked_before - 1, "planet checkbox count did not decrease")
        planet_drawer.locator(".ant-tabs-tabpane-active input[type='checkbox']").nth(0).click(force=True)
        page.wait_for_timeout(300)
        close_top_visible_drawer(page)
        result["checks"]["planet_selector"] = {"before": planet_svg_before, "after": planet_svg_after}

        # Aspect selector should affect 星盘 -> 相位 list.
        ensure(click_visible_text(page, "信息"), "cannot switch 星盘 to 信息 before aspect selector test")
        page.wait_for_timeout(800)
        aspect_svg_before = get_visible_svg_metrics(page)
        click_normalized_page_button(page, "相位选择")
        page.wait_for_timeout(700)
        aspect_drawer = visible_drawer(page, "相位选择")
        ensure(aspect_drawer.count() > 0, "相位选择 drawer not visible")
        aspect_checkboxes = aspect_drawer.locator("input[type='checkbox']")
        ensure(aspect_checkboxes.count() > 0, "aspect checkboxes missing")
        aspect_checked_before = checked_checkbox_count(aspect_drawer)
        aspect_checkboxes.nth(0).click(force=True)
        page.wait_for_timeout(300)
        close_top_visible_drawer(page)
        page.wait_for_timeout(800)
        aspect_svg_after = get_visible_svg_metrics(page)
        ensure(aspect_svg_after != aspect_svg_before, "aspect selector did not change chart SVG metrics")
        click_normalized_page_button(page, "相位选择")
        page.wait_for_timeout(700)
        aspect_drawer = visible_drawer(page, "相位选择")
        ensure(checked_checkbox_count(aspect_drawer) == aspect_checked_before - 1, "aspect checkbox count did not decrease")
        aspect_drawer.locator("input[type='checkbox']").nth(0).click(force=True)
        page.wait_for_timeout(300)
        close_top_visible_drawer(page)
        result["checks"]["aspect_selector"] = {"before": aspect_svg_before, "after": aspect_svg_after}

        # Case management add/edit.
        click_manage_item(page, "管理事盘")
        ensure(visible_drawer(page, "起课列表").count() > 0, "起课列表 drawer not visible")
        ensure(page.get_by_text("Codex Seed Case", exact=True).count() > 0, "seed case missing")
        case_add_event = "Codex UI Added Case"
        case_edit_event = "Codex UI Edited Case"
        visible_drawer(page, "起课列表").get_by_role("button", name="添加起课").click(force=True)
        page.wait_for_timeout(700)
        case_add_drawer = visible_drawer(page, "添加起课")
        ensure(case_add_drawer.count() > 0, "添加起课 drawer not visible")
        case_add_drawer.get_by_placeholder("事件").fill(case_add_event)
        case_add_drawer.get_by_placeholder("起课地").fill("Codex Case Place")
        click_normalized_button(case_add_drawer, "提交")
        page.wait_for_timeout(1_200)
        ensure(visible_drawer(page, "起课列表").count() > 0, "did not return to 起课列表 after adding case")
        ensure(page.get_by_text(case_add_event, exact=True).count() > 0, "added case missing in list")
        search_in_visible_input(page, "以事件进行检索", case_add_event)
        case_row = page.locator("tbody tr").filter(has=page.get_by_text(case_add_event, exact=True)).first
        ensure(case_row.count() > 0, "cannot find added case row for edit")
        click_row_action(case_row, 1)
        page.wait_for_timeout(700)
        case_edit_drawer = visible_drawer(page, "编辑起课")
        ensure(case_edit_drawer.count() > 0, "编辑起课 drawer not visible")
        event_input = case_edit_drawer.get_by_placeholder("事件")
        event_input.fill("")
        event_input.fill(case_edit_event)
        click_normalized_button(case_edit_drawer, "提交")
        page.wait_for_timeout(1_200)
        search_in_visible_input(page, "以事件进行检索", case_edit_event)
        case_row = page.locator("tbody tr").filter(has=page.get_by_text(case_edit_event, exact=True)).first
        ensure(case_row.count() > 0, "edited case missing in list")
        click_row_action(case_row, 0)
        page.wait_for_timeout(1_000)
        ensure(page.locator(".ant-drawer.ant-drawer-open").count() == 0, "case select did not close drawer")
        result["checks"]["case_management"] = {
            "added": case_add_event,
            "edited": case_edit_event,
            "selected": case_edit_event,
        }

        # Relationship chart end-to-end tab smoke.
        ensure(click_visible_text(page, "关系盘"), "cannot open 关系盘")
        page.wait_for_timeout(800)
        select_chart_from_modal(page, "星盘A", "Codex Seed Alpha")
        select_chart_from_modal(page, "星盘B", "Codex Seed Beta")
        with page.expect_response(lambda resp: "/modern/relative" in resp.url and resp.request.method == "POST" and resp.status == 200, timeout=120_000):
            click_normalized_page_button(page, "排盘")
        page.wait_for_timeout(1_500)
        relative_results = {}
        for label in RELATIVE_TABS:
            ensure(click_visible_text(page, label), f"cannot open relation subtab: {label}")
            page.wait_for_timeout(700)
            body = " ".join(page.locator("body").inner_text().split())
            ensure("请先选择星盘A和星盘B" not in body, f"relation subtab still shows empty-state: {label}")
            relative_results[label] = get_visible_svg_metrics(page)
        result["checks"]["relative_chart"] = relative_results

        page.screenshot(path=str(SCREENSHOT_PATH), full_page=True)
        context.close()
        browser.close()

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
        result["warnings"].append(
            {
                "type": "remote_request_failures",
                "count": len(remote_request_warnings),
                "samples": remote_request_warnings[:10],
            }
        )

    fatal_console_errors = []
    ignored_console_errors = []
    for message in result["consoleErrors"]:
        if "Failed to load resource" in message and "ERR_CONNECTION_TIMED_OUT" in message:
            ignored_console_errors.append(message)
        elif "DOMNodeInserted" in message:
            ignored_console_errors.append(message)
        else:
            fatal_console_errors.append(message)
    result["consoleErrors"] = fatal_console_errors
    if ignored_console_errors:
        result["warnings"].append(
            {
                "type": "remote_console_errors",
                "count": len(ignored_console_errors),
                "samples": ignored_console_errors[:10],
            }
        )

    if result["dialogs"] or result["pageErrors"] or result["consoleErrors"] or result["requestFailures"]:
        result["status"] = "error"

    JSON_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(1 if result["status"] != "ok" else 0)


if __name__ == "__main__":
    main()
