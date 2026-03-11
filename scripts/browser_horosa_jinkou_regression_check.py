#!/usr/bin/env python3
"""Browser regression check for Horosa 金口诀月将/将神 rendering."""

from __future__ import annotations

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


def set_visible_datetime_selector(page, year: int, month: int, day: int, hour: int, minute: int, second: int, zone: str = "+08:00", visible_index: int = 0, confirm: bool = False) -> None:
    page.evaluate(
        """
        ([visibleIndex, year, month, day, hour, minute, second, zone, confirm]) => {
          const yearInputs = Array.from(document.querySelectorAll('input[placeholder="年"]')).filter((el) => {
            const style = window.getComputedStyle(el);
            return style && style.display !== 'none' && style.visibility !== 'hidden' && el.offsetParent !== null;
          });
          const target = yearInputs[visibleIndex];
          if (!target) {
            throw new Error(`visible year input ${visibleIndex} not found`);
          }
          const fiberKey = Object.keys(target).find((k) => k.startsWith('__reactFiber$'));
          let fiber = fiberKey ? target[fiberKey] : null;
          let inst = null;
          while (fiber) {
            if (fiber.stateNode && typeof fiber.stateNode.changeYear === 'function' && typeof fiber.stateNode.changeSecond === 'function') {
              inst = fiber.stateNode;
              break;
            }
            fiber = fiber.return;
          }
          if (!inst) {
            throw new Error('DateTimeSelector instance not found');
          }
          inst.changeZone(zone);
          inst.changeYear(year);
          inst.changeMonth(month);
          inst.changeDate(day);
          inst.changeHour(hour);
          inst.changeMinute(minute);
          inst.changeSecond(second);
          if (confirm && typeof inst.clickOk === 'function') {
            inst.clickOk();
          }
        }
        """,
        [visible_index, year, month, day, hour, minute, second, zone, confirm],
    )
    page.wait_for_timeout(1200)


def select_visible_dropdown_by_prefix(page, prefix: str, option_label: str) -> None:
    selectors = page.locator(".ant-select-selector")
    target = None
    for idx in range(selectors.count()):
        item = selectors.nth(idx)
        try:
            if not item.is_visible():
                continue
            txt = " ".join(item.inner_text().split())
            if txt.startswith(prefix):
                target = item
                break
        except Exception:
            continue
    if target is None:
        raise AssertionError(f"找不到前缀为 {prefix!r} 的可见下拉框")
    target.click(force=True)
    page.wait_for_timeout(300)
    option = page.locator(".ant-select-dropdown:visible").get_by_text(option_label, exact=True)
    option.first.click(force=True, timeout=10_000)
    page.wait_for_timeout(800)


def get_jinkou_state(page) -> dict:
    return page.evaluate(
        """
        () => {
          const seenNodes = new Set();
          const seenStates = new Set();

          function snapshotState(state) {
            const liureng = state.liureng || {};
            const nongli = liureng.nongli || {};
            const runyear = state.runyear || {};
            return {
              diFen: state.diFen || '',
              diFenAuto: state.diFenAuto === true,
              rightTab: state.rightTab || '',
              nongli: {
                time: nongli.time || '',
                dayGanZi: nongli.dayGanZi || '',
                monthGanZi: nongli.monthGanZi || '',
                jieqi: nongli.jieqi || '',
                jiedelta: nongli.jiedelta || '',
              },
              runyear: {
                year: runyear.year || '',
                age: runyear.age,
                ageCycle: runyear.ageCycle,
              },
            };
          }

          function walk(node) {
            if (!node || seenNodes.has(node)) {
              return null;
            }
            seenNodes.add(node);
            const fiberKeys = Object.keys(node).filter((k) => k.startsWith('__reactFiber$'));
            for (const key of fiberKeys) {
              let fiber = node[key];
              let steps = 0;
              while (fiber && steps < 60) {
                const inst = fiber.stateNode;
                if (inst && inst.state && !seenStates.has(inst)) {
                  seenStates.add(inst);
                  const state = inst.state;
                  if (
                    Object.prototype.hasOwnProperty.call(state, 'diFen')
                    && Object.prototype.hasOwnProperty.call(state, 'liureng')
                    && Object.prototype.hasOwnProperty.call(state, 'runyear')
                  ) {
                    return snapshotState(state);
                  }
                }
                fiber = fiber.return;
                steps += 1;
              }
            }
            for (const child of node.children || []) {
              const found = walk(child);
              if (found) {
                return found;
              }
            }
            return null;
          }

          return walk(document.body) || {};
        }
        """
    ) or {}


def normalized_body_text(page) -> str:
    body = page.locator("body").inner_text()
    return "".join(body.split())


def main() -> None:
    web_port = os.environ.get("HOROSA_WEB_PORT", "8000")
    server_root = os.environ.get("HOROSA_SERVER_ROOT", f"http://127.0.0.1:{os.environ.get('HOROSA_SERVER_PORT', '9999')}")
    base_url = os.environ.get(
        "HOROSA_WEB_ROOT",
        f"http://127.0.0.1:{web_port}/index.html?srv={server_root.replace(':', '%3A').replace('/', '%2F')}&v={int(time.time())}",
    )

    out_json = Path(os.environ.get("HOROSA_JINKOU_CHECK_JSON", str(RUNTIME_DIR / "browser_horosa_jinkou_regression_check.json")))
    out_png = Path(os.environ.get("HOROSA_JINKOU_CHECK_SCREENSHOT", str(RUNTIME_DIR / "browser_horosa_jinkou_regression_check.png")))
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_png.parent.mkdir(parents=True, exist_ok=True)

    result: dict = {
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
        page = browser.new_page(viewport={"width": 1720, "height": 1184})

        page.on("dialog", lambda dialog: (result["dialogs"].append(dialog.message), dialog.dismiss()))
        page.on("pageerror", lambda exc: result["pageErrors"].append(str(exc)))
        page.on("console", lambda msg: result["consoleErrors"].append(msg.text) if msg.type == "error" else None)
        page.on("requestfailed", lambda req: result["requestFailures"].append({"url": req.url, "failure": req.failure}))

        page.goto(base_url, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(5_000)

        if not click_visible_text(page, "易与三式"):
            raise AssertionError("无法点击左侧模块：易与三式")
        if not click_visible_text(page, "金口诀"):
            raise AssertionError("无法打开右侧页签：金口诀")
        page.wait_for_timeout(1_500)

        set_visible_datetime_selector(page, 2026, 3, 10, 21, 42, 0, "+08:00", visible_index=0, confirm=True)
        set_visible_datetime_selector(page, 2026, 3, 10, 21, 42, 0, "+08:00", visible_index=1, confirm=True)
        select_visible_dropdown_by_prefix(page, "地分：", "地分：亥")

        page.wait_for_function(
            """
            () => {
              const body = (document.body && document.body.innerText) ? document.body.innerText.replace(/\\s+/g, '') : '';
              return body.includes('将神癸亥登明') && body.includes('地分亥');
            }
            """,
            timeout=120_000,
        )
        page.wait_for_timeout(1_000)

        state = get_jinkou_state(page)
        compact = normalized_body_text(page)

        if state.get("diFen") != "亥":
            raise AssertionError(f"金口诀地分未保持为亥：{state.get('diFen')!r}")
        nongli = state.get("nongli") or {}
        if nongli.get("time") != "癸亥":
            raise AssertionError(f"金口诀起课时支未对齐到癸亥：{nongli.get('time')!r}")
        if "惊蛰" not in f"{nongli.get('jiedelta') or nongli.get('jieqi') or ''}":
            raise AssertionError(f"金口诀节气段未命中惊蛰：{nongli}")
        if "将神癸亥登明" not in compact:
            raise AssertionError("金口诀页面未渲染出 将神=癸亥登明")
        if "将神壬戌河魁" in compact:
            raise AssertionError("金口诀页面仍错误渲染为 壬戌河魁")

        result["checks"]["jinkou_regression"] = {
            "state": state,
            "contains_correct_render": "将神癸亥登明" in compact,
            "contains_wrong_render": "将神壬戌河魁" in compact,
        }

        page.screenshot(path=str(out_png), full_page=True)
        browser.close()

    if result["dialogs"] or result["pageErrors"] or result["consoleErrors"] or result["requestFailures"]:
        result["status"] = "error"

    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["status"] != "ok" else 0)


if __name__ == "__main__":
    main()
