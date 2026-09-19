#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""浮层几何行为闸(headless Chromium × E2/E3 双引擎语义;屏幕零输出)。

为什么要有它:「补丁在不在 / 钩子装没装」这类静态检查,与用 `__HOROSA_ALIGN_SCALE__ = () => z` 打桩的对齐单测,
都绕开了真正决定浮层落点的链路:声明缩放 → 实测缓存 → dom-align 补偿除数。典型漏网形态:非 1 档启动后在页内调回 100%,
补偿除数仍是启动时的旧档,全站浮层错位 (1/z0−1)·(D+999),而静态检查与桩测试全绿。
本闸用**真页面、真 antd、真 dom-align 产物、壳里抽取的真换档脚本**把换档路径走一遍;判据体 popup_geometry.tpl.js 为单源。

引擎语义(与 audit_app_layout.py 同一对 shim):
  E3  画面缩放、rect 跟着缩放   —— Chromium / 较新的 macOS WebKit
  E2  画面缩放、rect **不**反映 —— 较旧的 macOS WebKit 实测语义;补偿必须自动静默(实测得 1)
两种语义下同一套判据都必须绿 = 跨系统版本的机械保证。

用法:
  python3 scripts/audit_popup_geometry.py              # 全量(2 引擎 × 页面 × 换档序列),有错位 exit 1
  python3 scripts/audit_popup_geometry.py --self-test  # 只验判据判别力:注入「旧档除数」必须判红、不注入必须判绿
  python3 scripts/audit_popup_geometry.py --quick      # 少量组合
"""
import json
import sys
import threading
import http.server
import socketserver
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from audit_app_layout import DIST, E2_SHIM_JS, E3_SHIM_JS, extract_apply_zoom_js   # noqa: E402  单源:同一对引擎模型 + 同一段壳换档脚本

PORT = 8794
TPL = HERE / "popup_geometry.tpl.js"

PAGES = ["sanshiunited", "astrochart", "bazi", "ziwei", "liureng", "guazhan"]
# (加载定档, 运行时换档目标 | None)。第 1 条就是出事路径:非 1 档启动 → 页内调回 100%。
SEQS = [(0.8, 1.0), (1.2, 1.0), (1.0, 1.8), (1.8, 0.7), (0.7, None), (1.8, None)]

# 自证用的「病灶再现」:把补偿除数钉成启动旧档(= 声明缩放读回启动传输层、命中启动缓存时的效果)。
STALE_HOOK_JS = "() => { window.__HOROSA_ALIGN_SCALE__ = function(){ return 0.8; }; return true; }"


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(DIST), **kw)

    def log_message(self, *a):   # noqa: D401
        pass


def serve():
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), _Quiet)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def probe_body(key, rtz, scrolls="0,0.5,1", limit=4):
    if not TPL.exists():
        return None
    src = TPL.read_text(encoding="utf-8")
    for k, v in (("__KEY__", key), ("__RTZ__", "" if rtz is None else str(rtz)), ("__SCROLLS__", scrolls),
                 ("__LIMIT__", str(limit)), ("__CAST__", "0")):
        src = src.replace(k, v)
    return "async () => {\n" + src + "\n}"


def run_once(browser, shim, apply_src, key, lz, rtz, stale=False):
    ctx = browser.new_context(viewport={"width": 1728, "height": 1006})
    ctx.add_init_script(shim)
    # 壳的换档函数每个 document 必挂(与 APP 的 init script 同形)
    ctx.add_init_script(apply_src)
    page = ctx.new_page()
    try:
        page.goto(f"http://127.0.0.1:{PORT}/index.html?shellZoom={lz}", wait_until="load", timeout=60000)
        page.wait_for_selector("#mainContent", timeout=30000)
        if stale:
            page.evaluate(STALE_HOOK_JS)
        raw = page.evaluate(probe_body(key, rtz))
        return json.loads(raw)
    finally:
        ctx.close()


def verdict(d):
    s = d.get("summary") or {}
    ok = sum(v for k, v in s.items() if k.startswith("OK"))
    return ok, s.get("MISALIGNED", 0) + s.get("OVERFLOW-NOFLIP", 0), s.get("DIRTY", 0)


def main():
    self_test = "--self-test" in sys.argv
    quick = "--quick" in sys.argv
    if not (DIST / "index.html").exists():
        print(f"❌ 找不到前端产物 {DIST}/index.html —— 先 npm run build:file")
        return 2
    if not TPL.exists():
        print(f"❌ 判据体缺失 {TPL}")
        return 2
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 需要 playwright:python3 -m pip install playwright && python3 -m playwright install chromium")
        return 2
    apply_src = extract_apply_zoom_js()
    if apply_src is None:
        return 2

    httpd = serve()
    failures = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()   # headless:屏幕零输出
            if self_test:
                # 判别力:E3 语义、出事路径(0.8 → 1)。不注入必须全对齐;注入旧档除数必须判错位 —— 两臂都过才算这把尺有牙。
                good = run_once(browser, E3_SHIM_JS, apply_src, "sanshiunited", 0.8, 1.0, stale=False)
                ok, bad, dirty = verdict(good)
                print(f"  自证·健康臂  OK={ok} MISALIGNED={bad} DIRTY={dirty}")
                if not (ok >= 3 and bad == 0):
                    failures.append(f"健康臂应全对齐,实得 OK={ok} MISALIGNED={bad}")
                sick = run_once(browser, E3_SHIM_JS, apply_src, "sanshiunited", 0.8, 1.0, stale=True)
                ok2, bad2, dirty2 = verdict(sick)
                print(f"  自证·病灶臂  OK={ok2} MISALIGNED={bad2} DIRTY={dirty2}(注入旧档除数 0.8,真实缩放 1)")
                if bad2 < 3:
                    failures.append(f"病灶臂必须判出错位(≥3),实得 MISALIGNED={bad2} —— 判据无判别力")
            else:
                pages = PAGES[:2] if quick else PAGES
                seqs = SEQS[:3] if quick else SEQS
                for code, shim in (("E3", E3_SHIM_JS), ("E2", E2_SHIM_JS)):
                    for key in pages:
                        for lz, rtz in seqs:
                            try:
                                d = run_once(browser, shim, apply_src, key, lz, rtz)
                            except Exception as e:   # noqa: BLE001
                                failures.append(f"{code} {key} {lz}→{rtz}: 判据执行异常 {str(e)[:120]}")
                                continue
                            ok, bad, dirty = verdict(d)
                            tag = "✅" if (bad == 0 and ok > 0) else "❌"
                            print(f"  {tag} {code} {key:<13} {lz}→{rtz if rtz is not None else '-':<4} OK={ok:<3} MISALIGNED={bad} DIRTY={dirty} eff={(d.get('diag') or {}).get('effectiveScale')}")
                            if bad:
                                rows = [r for r in d.get("rows", []) if r.get("verdict") in ("MISALIGNED", "OVERFLOW-NOFLIP")][:3]
                                failures.append(f"{code} {key} {lz}→{rtz}: {bad} 处浮层错位,例 " + "; ".join(
                                    f"{r.get('label', '')[:10]} dx={r.get('dx')} dyB={r.get('dyBelow')}" for r in rows))
                            elif ok == 0:
                                failures.append(f"{code} {key} {lz}→{rtz}: 零成功样本 —— 先怀疑仪器(页面没渲染 / 没有可点中的控件)")
            browser.close()
    finally:
        httpd.shutdown()

    if failures:
        print("\n❌ 浮层几何行为闸:")
        for f in failures:
            print("   - " + f)
        return 1
    print("\n✅ 浮层几何行为闸通过" + ("(判据判别力自证:健康臂绿 / 病灶臂红)" if self_test else "(E2/E3 双引擎语义 × 页面 × 换档序列,零错位)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
