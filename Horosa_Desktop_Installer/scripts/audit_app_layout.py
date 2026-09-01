#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主应用版面体检 —— 制度化闸门(壳内三页之外的另一半)。

由来(2026-08-27):用户旧 MacBook 在缩放 0.8 下全站底部一大条死带,新机同版正常。
既有护栏全绿却毫无察觉,原因有二,本脚本各补一条:

  ① preflight [177] 是**结构锁**(查 URL query 在不在、有没有 100vh),不看渲染结果;
     audit_shell_pages.py 会看渲染,但**只覆盖壳内三页,主应用一页都没进闸门**。
  ② 所有护栏都只跑一种引擎语义(Chromium)。而真机实测两台机器语义不同:
        E3  画面缩放、rect 跟着缩放   —— Chromium / 新机 Tahoe
        E2  画面缩放、rect **不**反映 —— 旧 MacBook(Safari 26.2)实测
     出事那段代码「clientHeight ÷ rect探针」在 E3 上恰好正确、在 E2 上算短 z 倍。
     只跑一种语义 ⇒ 这类缺陷在 CI 里天然不可见。

🔴 判据 FILL 是本次缺陷的直接对应:内容是否真的铺满了容器。既有七类判据里没有它,
   所以壳内三页 384 组合全绿也照样漏掉死带。

🔴 裁判不能被 shim 骗:E2 模型改写的是**页面看到的** getBoundingClientRect,
   判据自身走 window.__REAL_GBCR(shim 前保存的原始函数)取真实渲染坐标。

已知局限:E2 模型只能复现「rect 读数域」的差异,无法复现 `vh` 解析差异
(真机 WebKit 上 100vh = 布局视口即正确;Chromium 上 = 物理视口即偏小)。
主应用骨架不依赖 vh(preflight [177]① 已禁),故该局限不影响本闸门结论。

用法:
  python3 scripts/audit_app_layout.py              # 全量,有缺陷 exit 1
  python3 scripts/audit_app_layout.py --self-test  # 只验判据自身的判别力
  python3 scripts/audit_app_layout.py --quick      # 少量组合,本地快验
"""
import http.server
import socketserver
import sys
import threading
from pathlib import Path

DIST = Path(__file__).resolve().parent.parent.parent / "Horosa-Web" / "astrostudyui" / "dist-file"
PORT = 8793

# 与 src-tauri/src/main.rs 对齐:MIN_ZOOM 0.7 / MAX_ZOOM 1.8 / ZOOM_STEP 0.1
ZOOMS = [round(0.7 + 0.1 * i, 1) for i in range(12)]
# 主窗最小 1180×760(main.rs);再加常见与极端宽高比
SIZES = [(1180, 760), (1440, 900), (1728, 1117), (2560, 1440), (1180, 1400)]

# 壳注入的缩放实现:运行时从 main.rs 的 [zoom-apply-fn:begin/end] 锚间抽取——体检永远测
# 「壳跑的那套」,零内嵌拷贝(历史教训:内嵌拷贝随壳演进悄悄漂移,「逐字对齐」注释成假话
# 而闸门毫无察觉)。锚缺失=硬失败 exit 2,不允许静默退回任何本地拷贝。
MAIN_RS = Path(__file__).resolve().parent.parent / "src-tauri" / "src" / "main.rs"
APPLY_BEGIN = "[zoom-apply-fn:begin]"
APPLY_END = "[zoom-apply-fn:end]"


def extract_apply_zoom_js():
    if not MAIN_RS.exists():
        print(f"❌ 找不到 {MAIN_RS} —— 无法抽取壳缩放实现")
        return None
    text = MAIN_RS.read_text(encoding="utf-8")
    if APPLY_BEGIN not in text or APPLY_END not in text:
        print(f"❌ main.rs 缺 {APPLY_BEGIN}/{APPLY_END} 抽取锚 —— 壳缩放段被改动却没保留锚")
        return None
    seg = text.split(APPLY_BEGIN, 1)[1].split(APPLY_END, 1)[0]
    # 去掉锚行残留的注释收尾(begin 行的 " */" 与 end 行的 "/* "),剩纯 JS(含 JS 注释,合法)
    seg = seg.split("*/", 1)[1].rsplit("/*", 1)[0]
    if "__HOROSA_APPLY_SHELL_ZOOM" not in seg:
        print("❌ 抽取段不含 __HOROSA_APPLY_SHELL_ZOOM —— 锚位错误")
        return None
    return seg


# 调用形态:先把抽取段包函数体 evaluate(挂上 window.__HOROSA_APPLY_SHELL_ZOOM),再逐档调用。
APPLY_CALL_JS = "(z) => { window.__HOROSA_APPLY_SHELL_ZOOM(z); return true; }"

# E2 引擎模型:画面照常缩放,但页面读到的 rect 回到布局域(= Chromium 值 ÷ z)。
# 数值依据真机实测:物理 720、z=0.8 时,1000px 元素在旧机量得 1000(Chromium 给 800,
# 800/0.8=1000 ✓);fixed 铺满在旧机量得 900(Chromium 给 720,720/0.8=900 ✓)。
E2_SHIM_JS = r"""
(() => {
  const real = Element.prototype.getBoundingClientRect;
  window.__REAL_GBCR = real;                 // 判据专用:未被改写的真实渲染坐标
  const zoomOf = () => {
    const z = parseFloat(document.documentElement.style.zoom);
    return (z && z > 0) ? z : 1;
  };
  Element.prototype.getBoundingClientRect = function () {
    const r = real.call(this);
    const z = zoomOf();
    if (z === 1) { return r; }
    return {
      left: r.left / z, top: r.top / z, right: r.right / z, bottom: r.bottom / z,
      width: r.width / z, height: r.height / z, x: r.x / z, y: r.y / z,
      toJSON() { return this; },
    };
  };
})();
"""

E3_SHIM_JS = r"""
(() => { window.__REAL_GBCR = Element.prototype.getBoundingClientRect; })();
"""

AUDIT_JS = r"""
(() => {
  const GB = (el) => window.__REAL_GBCR.call(el);   // 恒取真实渲染坐标,不受引擎模型影响
  const bad = [];
  const host = document.getElementById('mainContent');
  if (!host) { return ['NO-HOST:#mainContent 未渲染']; }

  const vw = window.innerWidth, vh = window.innerHeight;
  const hostBox = GB(host);

  // ① FILL —— 本次缺陷的直接判据:容器里**真的画了内容**的区域,是否铺到了底。
  //
  // 🔴 判据经过一次返工,教训值得留着:首版取「容器内渲染底边最大的元素」,结果恒判 100%
  // —— 因为 .workspaceOuter 是 height:100% 的包裹层,它永远贴底,而死带是**包裹层里面**
  // 的内容短了。拿旧产物一跑就全绿,等于没有判别力。
  // 现版改用 elementsFromPoint 逐点问「这个位置到底画了东西没有」:只命中包裹层 = 空白。
  // 实测(旧产物 · E2 语义):z=1.0 死带 2px/填充 100%;z=0.8 死带 182px/填充 78%;
  // z=0.7 死带 272px/填充 68% —— 填充比恰等于缩放值,与用户照片量出的比例一致。
  const WRAP = /workspaceOuter|workspaceInner/;
  const isWrap = (el) => !el || el === host || el === document.body
                      || el === document.documentElement || WRAP.test(String(el.className || ''));
  let contentBottom = hostBox.top;
  const xs = [0.2, 0.35, 0.5, 0.65, 0.8].map((f) => hostBox.left + hostBox.width * f);
  for (let y = Math.floor(hostBox.bottom) - 2; y > hostBox.top; y -= 3) {
    let hit = false;
    for (const x of xs) {
      const els = document.elementsFromPoint(x, y);
      if (els.length && !isWrap(els[0])) { hit = true; break; }
    }
    if (hit) { contentBottom = y; break; }
  }
  if (hostBox.height > 100) {
    const filled = (contentBottom - hostBox.top) / hostBox.height;
    // 容差 6%:正常版面底部本有内边距;死带是 20%~30% 量级,区分度充足。
    if (filled < 0.94) {
      bad.push('FILL:内容仅铺满容器 ' + Math.round(filled * 100) + '%(底部死带 '
               + Math.round(hostBox.bottom - contentBottom) + 'px)');
    }
  }

  // ② 容器自身要贴住窗口底部(壳层/高度链断裂会在这里现形)
  if (hostBox.bottom < vh - 4) {
    bad.push('HOST-SHORT:容器底边距窗口底 ' + Math.round(vh - hostBox.bottom) + 'px');
  }

  // ③ WIDTH-FILL —— 对应用户说的「不会根据分辨率调整」:窗口变宽了,内容跟不跟。
  //
  // 这里**不判**文档级横向溢出:本应用 html/body 是 overflow:hidden,scrollWidth 永远
  // 不会超过 clientWidth,那条判据恒绿、毫无判别力(自检时判不红才发现);而且应用内部
  // 本就有合法的横向滚动区。留一条触发不了的判据只会制造虚假信心,故换成横向填充。
  let contentRight = hostBox.left;
  const ys = [0.25, 0.45, 0.65, 0.85].map((f) => hostBox.top + hostBox.height * f);
  for (let x = Math.floor(hostBox.right) - 2; x > hostBox.left; x -= 4) {
    let hit = false;
    for (const y of ys) {
      const els = document.elementsFromPoint(x, y);
      if (els.length && !isWrap(els[0])) { hit = true; break; }
    }
    if (hit) { contentRight = x; break; }
  }
  if (hostBox.width > 200) {
    const wf = (contentRight - hostBox.left) / hostBox.width;
    if (wf < 0.94) {
      bad.push('WIDTH-FILL:内容仅铺满容器宽度 ' + Math.round(wf * 100) + '%(右侧留白 '
               + Math.round(hostBox.right - contentRight) + 'px)');
    }
  }

  return bad;
})()
"""

# 判别向量:人为制造每类缺陷,确认判据都能判红。判据改动后必须先跑这个。
SELF_TEST_JS = r"""
(() => {
  const audit = () => eval(window.__AUDIT_SRC);
  const out = {};
  const host = document.getElementById('mainContent');
  if (!host) { return { fatal: 'no #mainContent' }; }

  out['baseline_clean'] = audit().length === 0 ? 'PASS' : ('DIRTY:' + audit().join(','));

  // FILL:把真实内容压到只剩三成高 —— 正是死带的形状。
  // 注意要压**包裹层里的内容**而不是包裹层本身(压包裹层测不出东西,首版就栽在这)。
  const inner = host.querySelector('[class*=workspaceInner]') || host.firstElementChild;
  const victim = inner && inner.firstElementChild ? inner.firstElementChild : inner;
  if (victim) {
    const o = victim.getAttribute('style') || '';
    victim.style.cssText = o + ';height:30%;max-height:30%;overflow:hidden';
    out['FILL'] = audit().some(v => v.startsWith('FILL')) ? 'PASS' : 'FAIL';
    victim.setAttribute('style', o);
  }

  // HOST-SHORT:让容器自己短一截。
  // 探针注意:#mainContent 是 flex 项,单给 height 会被 flex 拉回原高 —— 必须同时
  // flex:none 才真的变短(首版就漏了这个,判不红,是探针的问题不是判据漏检)。
  const o2 = host.getAttribute('style') || '';
  host.style.cssText = o2 + ';flex:none;height:40%;max-height:40%';
  out['HOST-SHORT'] = audit().some(v => v.startsWith('HOST-SHORT')) ? 'PASS' : 'FAIL';
  host.setAttribute('style', o2);

  // WIDTH-FILL:把内容压窄到六成 —— 「窗口变宽内容不跟随」的形状
  if (victim) {
    const o3 = victim.getAttribute('style') || '';
    victim.style.cssText = o3 + ';width:60%;max-width:60%;overflow:hidden';
    out['WIDTH-FILL'] = audit().some(v => v.startsWith('WIDTH-FILL')) ? 'PASS' : 'FAIL';
    victim.setAttribute('style', o3);
  }

  return out;
})()
"""


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(DIST), **kw)

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


ENGINES = [("E3", E3_SHIM_JS), ("E2", E2_SHIM_JS)]


def main():
    self_test = "--self-test" in sys.argv
    quick = "--quick" in sys.argv
    if not (DIST / "index.html").exists():
        print(f"❌ 找不到前端产物 {DIST}/index.html —— 先 npm run build:file")
        return 2
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 需要 playwright：python3 -m pip install playwright && python3 -m playwright install chromium")
        return 2

    apply_src = extract_apply_zoom_js()
    if apply_src is None:
        return 2
    apply_define_js = "() => { " + apply_src + " }"

    httpd = serve()
    failures, checked = [], 0
    sizes = SIZES[:1] if quick else SIZES
    zooms = [0.8, 1.0, 1.5] if quick else ZOOMS
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for code, shim in ENGINES:
                ctx = browser.new_context()
                ctx.add_init_script(shim)
                page = ctx.new_page()
                for (w, h) in sizes:
                    page.set_viewport_size({"width": w, "height": h})
                    page.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="load")
                    try:
                        page.wait_for_selector("#mainContent", timeout=15000)
                    except Exception:
                        failures.append(f"{code} {w}x{h}: #mainContent 始终未渲染")
                        continue
                    page.wait_for_timeout(900)   # 等版面稳定(dva 首次 syncWorkspaceHeight)
                    page.evaluate(apply_define_js)   # 挂上壳抽取版 __HOROSA_APPLY_SHELL_ZOOM

                    if self_test:
                        page.evaluate("(src) => { window.__AUDIT_SRC = src; }", AUDIT_JS)
                        res = page.evaluate(SELF_TEST_JS)
                        bad = {k: v for k, v in res.items() if v != "PASS"}
                        print(f"  {code}  {w}x{h}  判别力 {res}")
                        if bad:
                            failures.append(f"{code} 判别力自证失败: {bad}")
                        # [FOLLOW-STUCK 自证] 钉死 #mainContent 宽后拖视口,增幅判据必须能判红
                        # (SELF_TEST_JS 已污染页面 → 先 reload 回干净态再演练)。
                        page.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="load")
                        page.wait_for_selector("#mainContent", timeout=15000)
                        page.wait_for_timeout(900)
                        page.evaluate(
                            "() => { const m = document.getElementById('mainContent');"
                            " m.style.width = '800px'; m.style.maxWidth = '800px';"
                            " m.style.flex = 'none'; }")
                        fs_before = page.evaluate(
                            "() => window.__REAL_GBCR.call("
                            "document.getElementById('mainContent')).width")
                        page.set_viewport_size({"width": w + 240, "height": h + 160})
                        page.wait_for_timeout(500)
                        fs_after = page.evaluate(
                            "() => window.__REAL_GBCR.call("
                            "document.getElementById('mainContent')).width")
                        follow_verdict = "PASS" if (fs_after - fs_before < 200) else "FAIL"
                        print(f"  {code}  FOLLOW-STUCK 自证(钉宽拖窗须被判红): {follow_verdict}")
                        if follow_verdict != "PASS":
                            failures.append(
                                f"{code} FOLLOW-STUCK 自证失败: 钉宽后拖窗仍量出跟随"
                                f"({fs_before:.0f}→{fs_after:.0f}),判据无判别力")
                        break

                    for z in zooms:
                        page.evaluate(APPLY_CALL_JS, z)
                        page.wait_for_timeout(260)   # 等 resize/RO/rAF 重测拍重算
                        defects = page.evaluate(AUDIT_JS)
                        checked += 1
                        if defects:
                            failures.append(f"{code} {w}x{h} z={z}: {', '.join(defects[:4])}")

                    # [FOLLOW-STUCK] 拖窗跟随判据(直击「不随窗口变化」):缩放档下拖大视口,
                    # #mainContent 的真实(裁判域 __REAL_GBCR)宽度必须即时跟随且版面复审仍绿。
                    # 判别边界(诚实标注):Playwright/Chromium 视口变化必发 resize 事件,复现
                    # 不了 WKWebView 事件源冻结本身——那由壳侧 resize 桥+真机浮层读数覆盖;
                    # 本判据锁的是「事件到了但版面不跟」的回归(钉宽/订阅断/域混挂死)。
                    page.evaluate(APPLY_CALL_JS, 0.9)
                    page.wait_for_timeout(300)
                    fw_before = page.evaluate(
                        "() => { const m = document.getElementById('mainContent');"
                        " return m ? window.__REAL_GBCR.call(m).width : 0; }")
                    page.set_viewport_size({"width": w + 240, "height": h + 160})
                    page.wait_for_timeout(500)
                    fw_after = page.evaluate(
                        "() => { const m = document.getElementById('mainContent');"
                        " return m ? window.__REAL_GBCR.call(m).width : 0; }")
                    checked += 1
                    if fw_after - fw_before < 200:
                        failures.append(
                            f"{code} {w}x{h} FOLLOW-STUCK: 拖窗 +240 后 #mainContent 裁判宽 "
                            f"{fw_before:.0f}→{fw_after:.0f}(增幅<200,版面没跟随)")
                    else:
                        follow_defects = page.evaluate(AUDIT_JS)
                        if follow_defects:
                            failures.append(
                                f"{code} {w + 240}x{h + 160} z=0.9(拖窗后复审): "
                                f"{', '.join(follow_defects[:4])}")
                    page.evaluate(APPLY_CALL_JS, 1)
                ctx.close()
                if self_test:
                    break
            browser.close()
    finally:
        httpd.shutdown()

    print()
    if self_test:
        if failures:
            for f in failures:
                print("  ❌ " + f)
            print("\n判据自身有漏检 —— 修好判据再谈版面体检。")
            return 1
        print("✅ 判别力自证通过：每类缺陷人为制造后都能判红。")
        return 0

    if failures:
        print(f"❌ 主应用版面体检发现 {len(failures)} 处缺陷（共检 {checked} 个组合）：")
        for f in failures[:40]:
            print("   " + f)
        if len(failures) > 40:
            print(f"   …… 另有 {len(failures) - 40} 处")
        return 1
    print(f"✅ 主应用版面体检全绿：{checked} 个组合"
          f"（尺寸 × {len(ZOOMS)} 缩放档 × E2/E3 双引擎语义 + 逐组合拖窗跟随复审;"
          f" 缩放实现=运行时抽取 main.rs 锚段,测的=跑的）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
