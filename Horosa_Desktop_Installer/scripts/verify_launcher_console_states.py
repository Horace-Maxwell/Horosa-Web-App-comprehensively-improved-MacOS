#!/usr/bin/env python3
"""Verify the desktop launcher console state skeleton.

The launcher is a release surface. This check keeps the default, dynamic
progress, ready, and failed states tied to the same UI skeleton.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import pathlib
import socket
import sys
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable

from playwright.sync_api import sync_playwright


ROOT = pathlib.Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@contextlib.contextmanager
def serve_web() -> str:
    port = free_port()

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

        def log_message(self, *_args: Any) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}/index.html"
    finally:
        server.shutdown()
        server.server_close()


COLLECT_JS = r"""(label) => ({
  label,
  tone: document.body.dataset.launcherTone,
  title: document.querySelector('#heroTitle')?.textContent || '',
  heroCopy: document.querySelector('#heroCopy')?.textContent || '',
  modeTag: document.querySelector('#heroModeTag')?.textContent?.trim() || '',
  pct: document.querySelector('#progressPct')?.textContent || '',
  fillWidth: document.querySelector('#progressFill')?.style.width || '',
  status: document.querySelector('#heroBadgeTertiary')?.textContent?.trim() || '',
  ctaHidden: document.querySelector('#primaryCtaBtn')?.classList.contains('hidden'),
  cta: document.querySelector('#primaryCtaLabel')?.textContent || '',
  copy: document.querySelector('#progressSubtitle')?.textContent?.trim() || '',
  session: [...document.querySelectorAll('.summary-list div:not(.summary-row--hidden)')]
    .map((node) => node.textContent.trim().replace(/\s+/g, ' ')),
  steps: [...document.querySelectorAll('[data-step]')].map((node) => ({
    step: node.dataset.step,
    cls: node.className,
    text: node.textContent.trim().replace(/\s+/g, ' ')
  })),
  phases: [...document.querySelectorAll('[data-phase-step]')].map((node) => ({
    step: node.dataset.phaseStep,
    cls: node.className,
    text: node.textContent
  })),
  logs: [...document.querySelectorAll('.log-row')]
    .map((node) => node.textContent.trim().replace(/\s+/g, ' ')),
  iconCount: document.querySelectorAll('img[src="./horosa-icon.png"]').length,
  recoveryVisible: !document.querySelector('#recoveryPanel')?.classList.contains('hidden'),
  overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  overflowY: document.documentElement.scrollHeight > document.documentElement.clientHeight
})"""


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def require_common(data: dict[str, Any], errors: list[str]) -> None:
    if data["iconCount"] < 2:
        fail(errors, f"{data['label']}: final Xingque icon is not used in both required positions")
    if data["overflowX"] or data["overflowY"]:
        fail(errors, f"{data['label']}: viewport overflows at 1280x800")
    if data["recoveryVisible"]:
        fail(errors, f"{data['label']}: legacy recovery panel is visible over the shared skeleton")
    if len(data["logs"]) < 3:
        fail(errors, f"{data['label']}: expected at least 3 log rows")


def step(data: dict[str, Any], step_no: int) -> dict[str, str]:
    return next(item for item in data["steps"] if item["step"] == str(step_no))


def check_default(data: dict[str, Any], errors: list[str]) -> None:
    require_common(data, errors)
    if data["tone"] != "launch" or data["pct"] != "8%" or data["status"] != "Live":
        fail(errors, f"default state mismatch: {data}")
    if not data["ctaHidden"]:
        fail(errors, "default state must hide the primary CTA")
    if "检查本机环境" not in data["title"]:
        fail(errors, "default title must remain in-progress")
    if "is-active" not in step(data, 1)["cls"] or any(
        "is-active" in step(data, no)["cls"] for no in (2, 3, 4)
    ):
        fail(errors, "default pipeline must only activate step 1")


def check_dynamic(data: dict[str, Any], expected_pct: str, active_step: int, errors: list[str]) -> None:
    require_common(data, errors)
    if data["pct"] != expected_pct or data["fillWidth"] != expected_pct:
        fail(errors, f"{data['label']}: progress did not track real backend value")
    if data["status"] != "Live" or not data["ctaHidden"]:
        fail(errors, f"{data['label']}: dynamic progress must stay live and CTA-free")
    if "is-active" not in step(data, active_step)["cls"]:
        fail(errors, f"{data['label']}: expected pipeline step {active_step} active")


def check_ready(data: dict[str, Any], errors: list[str]) -> None:
    require_common(data, errors)
    if data["tone"] != "ready" or data["pct"] != "100%" or data["status"] != "Ready":
        fail(errors, f"ready state mismatch: {data}")
    if data["ctaHidden"] or data["cta"] != "进入主界面":
        fail(errors, "ready state must expose the enter-main-window CTA")
    if not all("is-complete" in step(data, no)["cls"] for no in (1, 2, 3, 4)):
        fail(errors, "ready state must mark every pipeline step complete")
    if "is-highlight" not in step(data, 4)["cls"]:
        fail(errors, "ready state must lightly highlight handoff step 4")
    if "来源 pkg 2.5.2" not in data["session"]:
        fail(errors, "ready state must keep offline package source/version")


def check_error(data: dict[str, Any], errors: list[str]) -> None:
    require_common(data, errors)
    if data["tone"] != "error" or data["pct"] != "26%" or data["status"] != "Failed":
        fail(errors, f"failed state mismatch: {data}")
    if data["ctaHidden"] or data["cta"] != "重建 Runtime":
        fail(errors, "failed state must show the green rebuild Runtime CTA")
    if "is-failed" not in step(data, 2)["cls"]:
        fail(errors, "failed state must mark pipeline step 2 as failed")
    if "is-active" in step(data, 3)["cls"] or "is-active" in step(data, 4)["cls"]:
        fail(errors, "failed state must not keep future pipeline steps active")
    if not any("error" in row and "runtime jar 哈希不符" in row for row in data["logs"]):
        fail(errors, "failed state must show highlighted runtime mismatch evidence")


def run(url: str, screenshot_dir: pathlib.Path | None) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    states: list[tuple[str, str, Callable[[dict[str, Any], list[str]], None]]] = [
        ("default", "", check_default),
        (
            "dynamic-42",
            "window.__horosaProgress(42, '检查 runtime jar', false)",
            lambda data, errs: check_dynamic(data, "42%", 2, errs),
        ),
        (
            "dynamic-73",
            "window.__horosaProgress(73, '启动本地服务', false)",
            lambda data, errs: check_dynamic(data, "73%", 3, errs),
        ),
        (
            "offline-ready",
            "window.__horosaState({ kind: 'offline_ready', installSource: 'pkg_offline', detail: '当前安装来源：离线安装包。本机组件版本 2.5.2 已可直接使用。' })",
            check_ready,
        ),
        ("runtime-error", "window.__horosaError('runtime jar 哈希不符')", check_error),
    ]

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for name, setup, checker in states:
            page = browser.new_page(viewport={"width": 1280, "height": 800}, device_scale_factor=1)
            page.goto(f"{url}?launcher-check={name}", wait_until="domcontentloaded")
            page.wait_for_timeout(160)
            if setup:
                page.evaluate(setup)
                page.wait_for_timeout(80)
            data = page.evaluate(COLLECT_JS, name)
            if screenshot_dir:
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = screenshot_dir / f"launcher-{name}.png"
                page.screenshot(path=str(screenshot_path), full_page=False)
                data["screenshot"] = str(screenshot_path)
            checker(data, errors)
            results.append(data)
            page.close()
        browser.close()

    if errors:
        print(json.dumps({"status": "failed", "errors": errors, "states": results}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Existing launcher URL to test")
    parser.add_argument("--screenshot-dir", type=pathlib.Path, help="Optional screenshot output directory")
    args = parser.parse_args()

    if args.url:
        results = run(args.url, args.screenshot_dir)
    else:
        with serve_web() as local_url:
            results = run(local_url, args.screenshot_dir)
    print(json.dumps({"status": "ok", "states": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
