//! 注入每个窗口的初始化脚本(页面载入前执行)。

pub(crate) const DESKTOP_WINDOW_INIT_SCRIPT: &str = r#"
(() => {
  const noop = () => undefined;
  const lock = (name) => {
    try {
      Object.defineProperty(window, name, {
        value: noop,
        writable: false,
        configurable: false
      });
    } catch (_) {
      try { window[name] = noop; } catch (_) {}
    }
  };
  try {
    Object.defineProperty(window, "__HOROSA_DESKTOP_SHELL__", {
      value: true,
      writable: false,
      configurable: false
    });
  } catch (_) {
    try { window.__HOROSA_DESKTOP_SHELL__ = true; } catch (_) {}
  }
  lock("resizeTo");
  lock("resizeBy");
  lock("moveTo");
  lock("moveBy");
  // 🔴 壳级缩放应用函数(每个 document 都由本 init 脚本重新挂上,导航后永不丢):
  // CSS zoom 域实现——documentElement.zoom + body 补偿(实测探针决策,详见函数内注释)
  // + 当前 origin localStorage 落键 + resize 通知量高链。z=1 清样式=零残留。
  // 运行时 ⌘±/⌘0 由壳 eval 调用;页面早期由 global.js 以 URL query(shellZoom)同构先行,
  // 此处后到幂等覆盖。探针决策核心与 global.js 逐 token 同构(jest shellZoomProbeGuard 对偶锁)。
  /* [zoom-apply-fn:begin] audit_app_layout.py 运行时抽取本段注入体检页(测的=跑的,零拷贝防 drift) */
  try {
    window.__HOROSA_APPLY_SHELL_ZOOM = function (z) {
      try {
        var v = Number(z);
        if (!v || v <= 0) { v = 1; }
        if (Math.abs(v - 1) < 0.001) { v = 1; }
        var d = document.documentElement;
        // [Tahoe 根修·加固] 补偿=实测探针决策:标准化 zoom 引擎(macOS 26 Tahoe WebKit)布局
        // 空间已自动=物理/z,再写 calc(100%/z)=过度补偿(内容恒缩 1/z^2、右/下缘裁切);旧语义
        // 引擎(Sequoia 及以前:fixed 包含块不随 zoom)才需要。判据=清掉补偿后 body 是否已铺满
        // fixed 探针的布局空间,未铺满才补——不认引擎只认实测,任何语义 by construction 成立。
        // 首拍在布局未 settle 时不可信 → rAF/load 两拍重测;窗口 resize 150ms 去抖重跑
        // (z 现场读 documentElement,换档后重跑不吃旧闭包值);未补偿态重跑=零写入。
        var __applyBodyComp = function (beat) {
            var __b = document.body;
            if (!__b) { return; }
            var __z = Number(document.documentElement.style.zoom || 1) || 1;
            if (Math.abs(__z - 1) < 0.001) { return; }
            var __t = 0;
            var __need = false;
            try {
                if (__b.style.width !== '' || __b.style.height !== '') { __b.style.width = ''; __b.style.height = ''; }
                var __p = document.createElement('div');
                __p.setAttribute('aria-hidden', 'true');
                __p.style.cssText = 'position:fixed;left:0;top:0;right:0;bottom:0;visibility:hidden;pointer-events:none';
                __b.appendChild(__p);
                __t = __p.offsetWidth;
                __b.removeChild(__p);
                __need = __t > 0 && Math.abs(__b.clientWidth - __t) > 2;
            } catch (__e2) { __need = true; }
            if (__need) {
                __b.style.height = 'calc(100% / ' + __z + ')';
                __b.style.width = 'calc(100% / ' + __z + ')';
            }
            try { window.__HOROSA_ZOOM_PROBE_LAST = { z: __z, target: __t, bodyW: __b.clientWidth, need: __need, beat: beat, ts: Date.now() }; } catch (__e3) { /* noop */ }
        };
        var __armZoomReprobe = function () {
            if (window.__HOROSA_ZOOM_REPROBE_ARMED) { return; }
            try { if (localStorage.getItem('horosa.compat.zoomReprobe') === '0') { return; } } catch (__e4) { /* noop */ }
            window.__HOROSA_ZOOM_REPROBE_ARMED = 1;
            if (typeof requestAnimationFrame === 'function') { requestAnimationFrame(function () { __applyBodyComp('raf'); }); }
            window.addEventListener('load', function () { __applyBodyComp('load'); }, { once: true });
            var __rt = null;
            window.addEventListener('resize', function () {
                if (__rt) { clearTimeout(__rt); }
                __rt = setTimeout(function () { __rt = null; __applyBodyComp('resize'); }, 150);
            });
        };
        var apply = function () {
          if (v === 1) {
            d.style.zoom = '';
            if (document.body) { document.body.style.height = ''; document.body.style.width = ''; }
          } else {
            d.style.zoom = String(v);
            __applyBodyComp('first');
            __armZoomReprobe();
          }
        };
        apply();
        if (!document.body) { document.addEventListener('DOMContentLoaded', apply); }
        try { localStorage.setItem('horosa.shell.zoom', String(v)); } catch (_) {}
        try { window.dispatchEvent(new Event('resize')); } catch (_) {}
      } catch (_) {}
    };
  } catch (_) {}
  /* [zoom-apply-fn:end] */
  // [B1] 前后端启动重叠:early 导航后,收尾的第二次 ready(同 srv/chartSrv/kentangSrv 同页)
  // 不许整页重载(否则并行启动省下的 umi 解析全白费)——仅当服务根参数或页面源真变了才导航。
  // 同参时置 __horosaBackendConfirmed=1,前端 boot-gate 以此立即放行排队中的请求。
  // 注:splash(launcher)页脚本晚于本 init 脚本执行,若其自定义 __horosaReady 会照常覆盖本实现。
  try {
    window.__horosaReady = function (url) {
      try {
        var next = new URL(String(url), window.location.href);
        var cur = new URL(window.location.href);
        if (cur.origin === next.origin && cur.pathname === next.pathname) {
          // rv = 运行时版本(前端 L3 缓存版本闸):早导航与收尾 ready 的 rv 不一致(早导航时尚未读到版本、或引导中途换装了运行时)
          // 必须整页重载,否则整个会话沿用错误的缓存版本号。
          var keys = ["srv", "chartSrv", "kentangSrv", "rv"];
          var same = true;
          for (var i = 0; i < keys.length; i += 1) {
            if (cur.searchParams.get(keys[i]) !== next.searchParams.get(keys[i])) { same = false; break; }
          }
          if (same) {
            window.__horosaBackendConfirmed = true;
            try { window.dispatchEvent(new CustomEvent("horosa:backend-confirmed")); } catch (_) {}
            return;
          }
        }
      } catch (_) {}
      window.location.replace(url);
    };
  } catch (_) {}
})();
"#;
