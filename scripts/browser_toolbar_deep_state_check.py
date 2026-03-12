#!/usr/bin/env python3
"""Deep stateful verification for toolbar memo and AI export settings on release builds."""

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
JSON_PATH = RUNTIME_DIR / "browser_toolbar_deep_state_check.json"

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
]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def visible_drawer(page, title: str):
    return page.locator(".ant-drawer.ant-drawer-open").filter(has=page.locator(".ant-drawer-title", has_text=title)).first


def visible_modal(page, title: str):
    return page.locator(".ant-modal:visible").filter(has=page.get_by_text(title, exact=True)).first


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
            page.wait_for_timeout(400)
            return True
        except Exception:
            continue
    return False


def click_page_button(page, label: str) -> None:
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
    ensure(clicked, f"button not clickable: {label}")
    page.wait_for_timeout(500)


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
          if (!btn) return false;
          btn.click();
          return true;
        }
        """
    )
    ensure(clicked, "drawer close button missing")
    page.wait_for_timeout(400)


def click_normalized_button(container, label: str) -> None:
    clicked = container.evaluate(
        """
        (el, targetLabel) => {
          const normalize = (txt) => (txt || '').replace(/\\s+/g, '');
          const target = Array.from(el.querySelectorAll('button')).find((btn) => normalize(btn.innerText) === targetLabel);
          if (!target) return false;
          target.click();
          return true;
        }
        """,
        label,
    )
    ensure(clicked, f"button not clickable: {label}")


def click_manage_item(page, label: str) -> None:
    ensure(click_visible_text(page, "管理"), "cannot open 管理 dropdown")
    page.wait_for_timeout(400)
    menu = page.locator(".ant-dropdown:visible").first
    ensure(menu.count() > 0, "manage dropdown missing")
    menu.get_by_text(label, exact=True).click(force=True)
    page.wait_for_timeout(700)


def search_in_visible_input(page, placeholder: str, value: str) -> None:
    locator = page.get_by_placeholder(placeholder)
    ensure(locator.count() > 0, f"missing input: {placeholder}")
    locator.first.fill(value)
    locator.first.press("Enter")
    page.wait_for_timeout(700)


def click_row_action(row_locator, index: int) -> None:
    links = row_locator.locator("a")
    ensure(links.count() > index, f"missing row action: {index}")
    links.nth(index).click(force=True)


def add_init_storage(context) -> None:
    payload = json.dumps(SEED_CHARTS, ensure_ascii=False)
    context.add_init_script(
        f"""
        (() => {{
          localStorage.clear();
          localStorage.setItem('horosa.localCharts.v1', JSON.stringify({payload}));
        }})();
        """
    )


def get_ai_settings(page) -> dict:
    return page.evaluate(
        """
        () => {
          try {
            const raw = localStorage.getItem('horosa.ai.export.settings.v1');
            return raw ? JSON.parse(raw) : {};
          } catch (err) {
            return {};
          }
        }
        """
    ) or {}


def checked_checkbox_count(scope) -> int:
    return scope.locator("input[type='checkbox']:checked").count()


def open_ai_settings(page):
    click_page_button(page, "AI导出设置")
    modal = visible_modal(page, "AI导出设置")
    ensure(modal.count() > 0, "AI导出设置 modal not visible")
    return modal


def select_ai_technique(page, modal, label: str) -> None:
    selector = modal.locator(".ant-select-selector").first
    selector.click(force=True)
    page.wait_for_timeout(300)
    dropdown = page.locator(".ant-select-dropdown:visible").last
    ensure(dropdown.count() > 0, "AI导出设置 technique dropdown missing")
    dropdown.get_by_text(label, exact=True).click(force=True)
    page.wait_for_timeout(500)


def current_checkbox_labels(group) -> list[str]:
    labels = []
    rows = group.locator(".ant-checkbox-wrapper")
    for idx in range(rows.count()):
        txt = " ".join(rows.nth(idx).inner_text().split())
        if txt:
            labels.append(txt)
    return labels


def check_ai_settings(page, result: dict) -> None:
    print("deep-check ai settings")
    modal = open_ai_settings(page)
    tech_selector = modal.locator(".ant-select-selector").first
    tech_text = " ".join(tech_selector.inner_text().split())
    ensure(tech_text, "AI导出设置 technique text missing")

    group = modal.locator(".ant-checkbox-group").first
    ensure(group.count() > 0, "AI导出设置 checkbox group missing")
    option_labels = current_checkbox_labels(group)
    ensure(option_labels, "AI导出设置 options missing")
    checked_before = checked_checkbox_count(group)

    click_normalized_button(modal, "清空")
    page.wait_for_timeout(300)
    checked_after_clear = checked_checkbox_count(group)
    ensure(checked_after_clear == 0, "AI导出设置 清空 did not clear all options")

    click_normalized_button(modal, "全选")
    page.wait_for_timeout(300)
    checked_after_all = checked_checkbox_count(group)
    ensure(checked_after_all == len(option_labels), "AI导出设置 全选 did not select all options")

    planet_info_labels = []
    for label in ["显示星曜宫位", "显示星曜主宰宫"]:
        locator = modal.get_by_text(label, exact=True)
        if locator.count() > 0:
            locator.first.click(force=True)
            page.wait_for_timeout(200)
            planet_info_labels.append(label)

    meaning_toggled = False
    meaning_locator = modal.get_by_text("在对应分段输出星/宫/座/相/希腊点释义", exact=True)
    if meaning_locator.count() > 0:
        meaning_locator.first.click(force=True)
        page.wait_for_timeout(200)
        meaning_toggled = True

    click_normalized_button(modal, "恢复默认")
    page.wait_for_timeout(400)
    checked_after_reset = checked_checkbox_count(group)
    ensure(checked_after_reset <= len(option_labels), "AI导出设置 恢复默认 produced invalid selection count")

    before_save = get_ai_settings(page)
    click_normalized_button(modal, "确定")
    page.wait_for_timeout(700)
    ensure(page.locator(".ant-modal:visible").count() == 0, "AI导出设置 modal did not close after save")
    after_save = get_ai_settings(page)
    ensure(after_save != before_save or after_save != {}, "AI导出设置 save did not persist any state")

    modal = open_ai_settings(page)
    group = modal.locator(".ant-checkbox-group").first
    reopened_checked = checked_checkbox_count(group)
    click_normalized_button(modal, "取消")
    page.wait_for_timeout(400)

    result["checks"]["ai_export_settings_deep"] = {
        "technique": tech_text,
        "optionCount": len(option_labels),
        "checkedBefore": checked_before,
        "checkedAfterClear": checked_after_clear,
        "checkedAfterAll": checked_after_all,
        "checkedAfterReset": checked_after_reset,
        "checkedAfterReopen": reopened_checked,
        "planetInfoToggled": planet_info_labels,
        "meaningToggled": meaning_toggled,
        "savedSettingsKeys": sorted(after_save.keys()),
    }


def set_quill_html(page, html: str) -> None:
    updated = page.evaluate(
        """
        (value) => {
          const editors = Array.from(document.querySelectorAll('.ql-editor'));
          const editor = editors.find((el) => {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
          });
          if (!editor) {
            return false;
          }
          editor.focus();
          editor.innerHTML = value;
          editor.dispatchEvent(new Event('input', { bubbles: true }));
          editor.dispatchEvent(new Event('blur', { bubbles: true }));
          return true;
        }
        """,
        html,
    )
    ensure(updated, "quill editor not writable")
    page.wait_for_timeout(600)


def get_quill_html(page) -> str:
    return page.evaluate(
        """
        () => {
          const editors = Array.from(document.querySelectorAll('.ql-editor'));
          const editor = editors.find((el) => {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
          });
          return editor ? editor.innerHTML : '';
        }
        """
    ) or ""


def select_chart(page, chart_name: str) -> None:
    click_manage_item(page, "管理命盘")
    ensure(visible_drawer(page, "星盘列表").count() > 0, "星盘列表 drawer not visible")
    search_in_visible_input(page, "以姓名进行检索", chart_name)
    row = page.locator("tbody tr").filter(has=page.get_by_text(chart_name, exact=True)).first
    ensure(row.count() > 0, f"cannot find chart row: {chart_name}")
    click_row_action(row, 0)
    page.wait_for_timeout(800)
    top_name = page.evaluate(
        """
        () => {
          const texts = Array.from(document.querySelectorAll('body *'))
            .filter((el) => {
              const rect = el.getBoundingClientRect();
              const style = window.getComputedStyle(el);
              return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
            })
            .map((el) => (el.innerText || '').trim())
            .filter(Boolean);
          return texts.join('\\n');
        }
        """
    )
    ensure(chart_name in top_name, f"selected chart name not visible after select: {chart_name}")
    while page.locator(".ant-drawer.ant-drawer-open").count() > 0:
        close_top_visible_drawer(page)


def check_memo(page, result: dict) -> None:
    print("deep-check memo save")
    select_chart(page, "Codex Seed Alpha")
    click_page_button(page, "批注")
    memo_drawer = visible_drawer(page, "命盘批注")
    ensure(memo_drawer.count() > 0, "命盘批注 drawer not visible")
    ensure(memo_drawer.get_by_text("Codex Seed Alpha", exact=True).count() > 0, "memo drawer missing selected chart")

    type_select = memo_drawer.locator(".ant-select-selector").first
    ensure(type_select.count() > 0, "memo type select missing")
    type_select.click(force=True)
    page.wait_for_timeout(300)
    dropdown = page.locator(".ant-select-dropdown:visible").last
    ensure(dropdown.count() > 0, "memo type dropdown missing")
    dropdown.get_by_text("八字", exact=True).click(force=True)
    page.wait_for_timeout(500)

    memo_html = "<p>Codex memo save check 2026-03-12 13:00</p>"
    set_quill_html(page, memo_html)
    before_save_html = get_quill_html(page)
    ensure("Codex memo save check" in before_save_html, "memo editor did not accept text")

    click_normalized_button(memo_drawer, "保存")
    page.wait_for_timeout(1800)

    reopened_before = get_quill_html(page)
    close_top_visible_drawer(page)
    click_page_button(page, "批注")
    memo_drawer = visible_drawer(page, "命盘批注")
    ensure(memo_drawer.count() > 0, "命盘批注 drawer not visible after reopen")
    type_select = memo_drawer.locator(".ant-select-selector").first
    type_value = " ".join(type_select.inner_text().split())
    reopened_html = get_quill_html(page)
    ensure("Codex memo save check" in reopened_html, "memo content did not persist after reopen")
    close_top_visible_drawer(page)

    result["checks"]["memo_save_deep"] = {
        "typeAfterReopen": type_value,
        "htmlBeforeSave": before_save_html,
        "htmlBeforeClose": reopened_before,
        "htmlAfterReopen": reopened_html,
    }


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
            context = browser.new_context(viewport={"width": 1720, "height": 1184})
            add_init_storage(context)
            page = context.new_page()
            page.on("dialog", lambda dialog: (result["dialogs"].append(dialog.message), dialog.dismiss()))
            page.on("pageerror", lambda exc: result["pageErrors"].append(str(exc)))
            page.on("console", lambda msg: result["consoleErrors"].append(msg.text) if msg.type == "error" else None)
            page.on("requestfailed", lambda req: result["requestFailures"].append({"url": req.url, "failure": req.failure}))

            page.goto(base_url, wait_until="domcontentloaded", timeout=120_000)
            page.wait_for_timeout(5_000)

            check_ai_settings(page, result)
            check_memo(page, result)

            context.close()
            browser.close()
    except Exception as exc:
        result["status"] = "error"
        result["fatalError"] = str(exc)

    JSON_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["status"] != "ok" else 0)


if __name__ == "__main__":
    main()
