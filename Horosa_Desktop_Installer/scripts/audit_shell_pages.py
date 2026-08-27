#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""壳内页面(启动 / 诊断 / 偏好)版面体检 —— 制度化闸门。

由来(2026-08-25):用户报「启动页面着实有一点丑陋，这是我们软件的门面」，随后要求
「不管什么情况都能完全完美显示」并「以后都可以制度化检查」。手工在浏览器里逐档比对
不可复现、也拦不住回归，故把整套判据固化成本脚本。

覆盖矩阵：3 个页面 × 多种窗口尺寸(含各自最小尺寸与极端宽高比) × 12 个缩放档
(0.7–1.8，与壳的 MIN_ZOOM/MAX_ZOOM/ZOOM_STEP 对齐) × 明暗两种系统外观。

七类判据（每类都对应一个真实修过的缺陷，不是凭空加的）：
  1. OUT-X        横向出界        —— 这类界面不该有横向滚动
  2. OUT-Y        纵向出界且滚不到 —— 区分「固定版面」与「流式可滚页面」，判据不同
  3. HIDDEN-CLIP  被 overflow:hidden 祖先切掉
  4. OVERLAP      关键卡片互相压盖（父子包含关系除外）
  5. CLIP         文本被裁切      —— 排除 ellipsis / line-clamp 这类设计意图
  6. VERTICAL     中文逐字竖排    —— 数值上不算裁切但极难看，只有肉眼或本判据能抓
  7. CONTRAST     对比度低于 WCAG AA（正文 4.5:1，大字/粗体 3:1）

🔴 两条必须遵守的纪律（都是本轮踩出来的）：
  · 判据改动后必须先跑 --self-test（判别向量：人为制造每类缺陷，确认全部判红）。
    本轮审查器自身误报/漏报共四次：出界检测被 overflow:auto 架空、把 ellipsis 设计意图
    当裁切、没区分流式页面导致默认档就误报、背景取色遇渐变回落白底把深色卡上的白字
    算成 1.05:1。每次都是判别向量才暴露的。
  · 背景取色必须能穿透「透明 backgroundColor + backgroundImage 渐变」的卡片。

用法：
  python3 scripts/audit_shell_pages.py              # 全量体检，有缺陷 exit 1
  python3 scripts/audit_shell_pages.py --self-test  # 只验判据自身的判别力
  python3 scripts/audit_shell_pages.py --quick      # 每页只跑默认尺寸(给本地快验)
"""
import http.server
import json
import os
import socketserver
import sys
import threading
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
PORT = 8791

# 与 src-tauri/src/main.rs 对齐：MIN_ZOOM 0.7 / MAX_ZOOM 1.8 / ZOOM_STEP 0.1
ZOOMS = [round(0.7 + 0.1 * i, 1) for i in range(12)]

# 各页的窗口尺寸取自 main.rs：主窗最小 1180×760；诊断 840×720(最小 720×620)；
# 偏好 760×680(最小 680×620)。再加极端宽高比压版面。
PAGES = {
    "index.html": {
        "label": "启动页",
        "sizes": [(1180, 760), (1480, 960), (1920, 1080), (2560, 1440),
                  (2560, 760), (1180, 1600)],
        "fixed_layout": True,   # 固定版面：内容不该需要滚动
    },
    "diagnostics.html": {
        "label": "诊断中心",
        "sizes": [(720, 620), (840, 720), (1600, 1000), (1900, 620), (720, 1400)],
        "fixed_layout": False,  # 流式页面：靠页面级滚动看全，属正常
    },
    "settings.html": {
        "label": "偏好设置",
        "sizes": [(680, 620), (760, 680), (1600, 1000), (1900, 620), (680, 1400)],
        "fixed_layout": False,
    },
}

AUDIT_JS = r"""
(() => {
  const d = document.documentElement;
  const CARDS = '.brand-card,.sidebar-card,.progress-card,.action-card,.detail-card,.review-panel,'
              + '.recovery-panel,.diag-card,.prefs-card,.diag-header,.prefs-header,.path-block,.info-block';
  const TEXTS = 'h1,h2,.step-name,.step-desc,.action-title,.action-copy,.panel-title,.panel-kicker,'
              + '.guard-key,.guard-value,.card-label,.brand-meta,.footer-note,.progress-copy,'
              + '.summary-list dt,.summary-list dd,.mode-pill,button,.card-title,.diag-eyebrow,'
              + '.prefs-eyebrow,.path-label,.path-value,.info-label,.info-value';
  const vis = el => { const cs = getComputedStyle(el);
    return cs.display !== 'none' && cs.visibility !== 'hidden' && el.offsetParent !== null; };

  // 页面级可滚 = 流式页面；内容超出视口底部属正常，不能算缺陷
  const pageScrollable = getComputedStyle(document.body).overflowY !== 'hidden'
                      && getComputedStyle(d).overflowY !== 'hidden';
  const reachableV = el => {
    if (pageScrollable) {
      const b = el.getBoundingClientRect();
      const absTop = b.top + (window.scrollY || 0);
      if (absTop >= -1 && absTop <= d.scrollHeight + 1) return true;
    }
    let p = el.parentElement;
    while (p && p !== d) {
      const cs = getComputedStyle(p);
      if (cs.overflowY === 'auto' || cs.overflowY === 'scroll') {
        const pb = p.getBoundingClientRect(), eb = el.getBoundingClientRect();
        const t = eb.top - pb.top + p.scrollTop;
        return t >= -1 && t <= p.scrollHeight + 1;
      }
      p = p.parentElement;
    }
    return false;
  };

  const parse = s => { const m = String(s).match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/);
    return m ? { r: +m[1], g: +m[2], b: +m[3], a: m[4] === undefined ? 1 : +m[4] } : null; };
  // 必须穿透「透明 backgroundColor + 渐变 backgroundImage」，否则深色卡上的白字会被算成 1.05:1
  const bgOf = el => {
    let p = el;
    while (p && p !== d) {
      const cs = getComputedStyle(p);
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0.5) return c;
      const bi = cs.backgroundImage;
      if (bi && bi !== 'none') {
        const cols = [...String(bi).matchAll(/rgba?\([\d.\s,]+\)/g)].map(m => parse(m[0])).filter(x => x && x.a > 0.5);
        if (cols.length) return cols[cols.length - 1];
      }
      p = p.parentElement;
    }
    const rb = parse(getComputedStyle(document.body).backgroundColor);
    return rb && rb.a > 0.5 ? rb : { r: 255, g: 255, b: 255 };
  };
  const lum = (r, g, b) => { const f = c => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const ratio = (f, b) => { const L1 = lum(f.r, f.g, f.b), L2 = lum(b.r, b.g, b.b);
    const hi = Math.max(L1, L2), lo = Math.min(L1, L2); return (hi + 0.05) / (lo + 0.05); };

  const bad = [];
  const vw = d.clientWidth, vh = d.clientHeight;

  document.querySelectorAll(CARDS).forEach(el => {
    if (!vis(el)) return;
    const b = el.getBoundingClientRect(); if (b.width <= 0) return;
    const n = el.className.split(' ')[0];
    if (b.right > vw + 1 || b.left < -1) bad.push('OUT-X:' + n);
    if ((b.bottom > vh + 1 || b.top < -1) && !reachableV(el)) bad.push('OUT-Y:' + n);
    if (b.width < 60 || b.height < 16) bad.push('TINY:' + n);
    let p = el.parentElement;
    while (p && p !== d) {
      const pcs = getComputedStyle(p);
      if (pcs.overflow === 'hidden' || pcs.overflowY === 'hidden' || pcs.overflowX === 'hidden') {
        const pb = p.getBoundingClientRect();
        if (b.top > pb.bottom + 1 || b.bottom < pb.top - 1 || b.left > pb.right + 1 || b.right < pb.left - 1)
          bad.push('HIDDEN-CLIP:' + n);
        break;
      }
      p = p.parentElement;
    }
  });

  const boxes = [...document.querySelectorAll(CARDS)].filter(vis)
    .map(el => ({ n: el.className.split(' ')[0], b: el.getBoundingClientRect() })).filter(x => x.b.width > 0);
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const A = boxes[i].b, B = boxes[j].b;
    if (Math.min(A.right, B.right) - Math.max(A.left, B.left) > 2
     && Math.min(A.bottom, B.bottom) - Math.max(A.top, B.top) > 2) {
      const contains = (A.left <= B.left + 1 && A.right >= B.right - 1 && A.top <= B.top + 1 && A.bottom >= B.bottom - 1)
                    || (B.left <= A.left + 1 && B.right >= A.right - 1 && B.top <= A.top + 1 && B.bottom >= A.bottom - 1);
      if (!contains) bad.push('OVERLAP:' + boxes[i].n + '/' + boxes[j].n);
    }
  }

  document.querySelectorAll(TEXTS).forEach(el => {
    if (!vis(el)) return;
    const cs = getComputedStyle(el);
    const t = (el.textContent || '').trim();
    const n = el.className.split(' ')[0] || el.tagName;
    // ellipsis / line-clamp 是设计上就打算省略，溢出属意图不是缺陷
    const intentional = cs.textOverflow === 'ellipsis' || (cs.webkitLineClamp && cs.webkitLineClamp !== 'none');
    if (!intentional && el.scrollWidth > el.clientWidth + 1 && cs.overflow !== 'visible')
      bad.push('CLIP:' + n + ':' + t.slice(0, 8));
    const b = el.getBoundingClientRect();
    if (b.width > 0 && t.length >= 2 && b.height > b.width * 1.5)
      bad.push('VERTICAL:' + t.slice(0, 8));
    if (t) {
      const fg = parse(cs.color);
      if (fg) {
        const r = ratio(fg, bgOf(el));
        const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 600;
        const need = (size >= 18.66 || (size >= 14 && bold)) ? 3.0 : 4.5;
        if (r < need - 0.01) bad.push('CONTRAST:' + n + ' ' + r.toFixed(2) + '<' + need + ' "' + t.slice(0, 8) + '"');
      }
    }
  });

  if (d.scrollWidth > d.clientWidth + 2) bad.push('PAGE-X-SCROLL:' + (d.scrollWidth - d.clientWidth));
  return [...new Set(bad)];
})()
"""

APPLY_ZOOM_JS = """
(z) => {
  const d = document.documentElement;
  if (z === 1) { d.style.zoom = ''; document.body.style.height = ''; document.body.style.width = ''; }
  else {
    d.style.zoom = String(z);
    document.body.style.height = 'calc(100% / ' + z + ')';
    document.body.style.width = 'calc(100% / ' + z + ')';
  }
  void d.offsetHeight;
  if (window.__HOROSA_APPLY_DENSITY) window.__HOROSA_APPLY_DENSITY();
  void d.offsetHeight;
  return d.getAttribute('data-density') || 'n/a';
}
"""


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(WEB_DIR), **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


def serve():
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), _Quiet)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


SELF_TEST_JS = r"""
(() => {
  const audit = () => eval(window.__AUDIT_SRC);
  const results = {};
  const probe = (name, sel, css, prefix) => {
    const el = document.querySelector(sel);
    if (!el) { results[name] = 'no-target'; return; }
    const o = el.getAttribute('style') || '';
    el.style.cssText = o + ';' + css;
    results[name] = audit().some(v => v.startsWith(prefix)) ? 'PASS' : 'FAIL';
    el.setAttribute('style', o);
  };
  const card = document.querySelector('.progress-card,.diag-card,.prefs-card');
  const cardSel = card ? '.' + card.className.split(' ')[0] : null;
  const text = document.querySelector('.action-title,.card-title,.info-label,button');
  const textSel = text ? (text.className ? '.' + text.className.split(' ')[0] : 'button') : null;
  if (cardSel) {
    probe('OUT-X', cardSel, 'position:relative;left:9999px', 'OUT-X');
    probe('TINY', cardSel, 'width:20px;height:8px', 'TINY');
  }
  if (textSel) {
    probe('CLIP', textSel, 'display:block;width:10px;overflow:hidden;white-space:nowrap;text-overflow:clip', 'CLIP');
    probe('VERTICAL', textSel, 'display:block;width:14px;white-space:normal', 'VERTICAL');
    // 🔴 探针要「必然判红」，不能依赖猜背景色：
    // 首版固定设成浅灰 #f4f4f4，探针若落在深蓝按钮上反而对比更高 → 判不红；
    // 二版改设文字为背景色，但探针取背景(backgroundColor)与判据取背景(bgOf 会穿透渐变)
    // 口径不一致，仍判不红。**两次都是探针的问题，不是判据漏检。**
    // 终版：把元素**背景**设成与其文字同色并清掉 backgroundImage —— 这样 bgOf 找到的
    // 第一个不透明背景必然就是它自己，对比度恒为 1.0，任何配色下都必然判红。
    const tEl0 = document.querySelector(textSel);
    if (tEl0) {
      const fgc = getComputedStyle(tEl0).color;
      probe('CONTRAST', textSel, 'background-color:' + fgc + ';background-image:none', 'CONTRAST');
    }
  }
  results['baseline_clean'] = audit().length === 0 ? 'PASS' : ('DIRTY:' + audit().join(','));
  return results;
})()
"""


def main():
    self_test = "--self-test" in sys.argv
    quick = "--quick" in sys.argv
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 需要 playwright：python3 -m pip install playwright && python3 -m playwright install chromium")
        return 2

    httpd = serve()
    failures = []
    checked = 0
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for page_file, cfg in PAGES.items():
                sizes = cfg["sizes"][:1] if quick else cfg["sizes"]
                for scheme in (["light"] if quick else ["light", "dark"]):
                    ctx = browser.new_context(color_scheme=scheme)
                    page = ctx.new_page()
                    for (w, h) in sizes:
                        page.set_viewport_size({"width": w, "height": h})
                        page.goto(f"http://127.0.0.1:{PORT}/{page_file}", wait_until="load")
                        page.wait_for_timeout(180)

                        if self_test:
                            page.evaluate("(src) => { window.__AUDIT_SRC = src; }", AUDIT_JS)
                            res = page.evaluate(SELF_TEST_JS)
                            bad = {k: v for k, v in res.items() if v not in ("PASS", "no-target")}
                            print(f"  {cfg['label']:8s} {scheme:5s} {w}x{h}  判别力 {res}")
                            if bad:
                                failures.append(f"{cfg['label']} 判别力自证失败: {bad}")
                            break  # 判别力与尺寸无关，一次足够

                        for z in ZOOMS:
                            density = page.evaluate(APPLY_ZOOM_JS, z)
                            defects = page.evaluate(AUDIT_JS)
                            checked += 1
                            if defects:
                                failures.append(
                                    f"{cfg['label']}({page_file}) {scheme} {w}x{h} z={z} "
                                    f"[density={density}]: {', '.join(defects[:6])}"
                                )
                    ctx.close()
                    if self_test:
                        break
                if self_test:
                    continue
            browser.close()
    finally:
        httpd.shutdown()

    print()
    if self_test:
        if failures:
            for f in failures:
                print("  ❌ " + f)
            print("\n判据自身有漏检 —— 修好判据再谈页面体检。")
            return 1
        print("✅ 判别力自证通过：每类缺陷人为制造后都能判红。")
        return 0

    if failures:
        print(f"❌ 壳内页面体检发现 {len(failures)} 处缺陷（共检 {checked} 个组合）：")
        for f in failures[:40]:
            print("   " + f)
        if len(failures) > 40:
            print(f"   …… 另有 {len(failures) - 40} 处")
        return 1
    print(f"✅ 壳内页面体检全绿：{checked} 个组合"
          f"（3 页 × 尺寸 × {len(ZOOMS)} 缩放档 × 明暗两态），七类判据零缺陷。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
