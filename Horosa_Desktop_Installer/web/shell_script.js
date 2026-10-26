// 壳自带页面(启动器 / 设置 / 诊断)的界面简繁显示层。
// 这三页不在主应用里,没有主应用的显示层转换器;页面里照写简体,繁体档时在这里就地换成繁体:
//   · 字表 = shell_hant_table.js(生成物):三页源码与壳层源码字符串里出现的每一段中文 → 主应用转换器的转换结果
//     (前端 jest shellPageScript.test.js 逐段比对,文案一改不重新生成即红);表外的段按表里最长的段拼、再逐字兜底。
//   · 档位:壳建窗时注入 window.__HOROSA_SHELL_SCRIPT(hans / hant),页面载入后再向壳确认一次;
//     切换简繁时壳对已开着的这几页调 HorosaShellScript.setMode(…)。
//   · 文字节点与显示属性(title / placeholder / aria-label / alt / 按钮 value)就地转,原文逐节点记住,切回简体放回原文;
//     之后页面脚本写进来的字由观察者跟着转。输入框的值、textarea、script / style、horosa-script-keep 区域不转。
(function (root) {
  'use strict';

  // 一段中文:以汉字起头,后接汉字或中文标点(与生成字表的 jest 同一份正则,导出给它用)
  const RUN_SOURCE = '[\\u3400-\\u9fff\\uf900-\\ufaff][\\u3400-\\u9fff\\uf900-\\ufaff\\u3000-\\u303f\\uff01-\\uff0f\\uff1a-\\uff20\\uff3b-\\uff40\\uff5b-\\uff65…—·]*';
  const MAX_PIECE = 24;
  const ATTRS = ['title', 'placeholder', 'aria-label', 'alt'];
  const SKIP_TAGS = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, NOSCRIPT: 1 };
  const KEEP_CLASS = 'horosa-script-keep';

  function table() {
    const t = root && root.HorosaShellHantTable;
    return t && t.runs && t.chars ? t : { runs: {}, chars: {} };
  }

  function lookupRun(run, t) {
    if (Object.prototype.hasOwnProperty.call(t.runs, run)) return t.runs[run];
    let out = '';
    let i = 0;
    while (i < run.length) {
      let hit = '';
      for (let j = Math.min(run.length, i + MAX_PIECE); j > i + 1; j -= 1) {
        const piece = run.slice(i, j);
        if (Object.prototype.hasOwnProperty.call(t.runs, piece)) { hit = t.runs[piece]; i = j; break; }
      }
      if (hit) { out += hit; continue; }
      const ch = run[i];
      out += Object.prototype.hasOwnProperty.call(t.chars, ch) ? t.chars[ch] : ch;
      i += 1;
    }
    return out;
  }

  // 简体 → 繁体(只给显示用;不认识的字原样)
  function toHant(text) {
    const s = text === undefined || text === null ? '' : String(text);
    if (!s) return s;
    const t = table();
    return s.replace(new RegExp(RUN_SOURCE, 'g'), (run) => lookupRun(run, t));
  }

  let mode = root && root.__HOROSA_SHELL_SCRIPT === 'hant' ? 'hant' : 'hans';
  const nodeOrig = new WeakMap();
  const nodeShown = new WeakMap();
  const attrOrig = new WeakMap();
  let observer = null;
  let langBefore = null;

  function skipped(node) {
    for (let el = node.nodeType === 1 ? node : node.parentNode; el && el.nodeType === 1; el = el.parentNode) {
      if (SKIP_TAGS[el.tagName]) return true;
      if (el.classList && el.classList.contains(KEEP_CLASS)) return true;
      if (el.isContentEditable) return true;
    }
    return false;
  }

  function applyText(node) {
    if (skipped(node)) return;
    // 自己转出去的字回来时认得出:节点当前的字 = 上次转出的结果 → 原文不变;否则是页面新写的原文
    const orig = nodeShown.has(node) && nodeShown.get(node) === node.data ? nodeOrig.get(node) : node.data;
    nodeOrig.set(node, orig);
    const out = mode === 'hant' ? toHant(orig) : orig;
    nodeShown.set(node, out);
    if (node.data !== out) node.data = out;
  }

  function attrList(el) {
    const list = ATTRS.slice();
    if (el.tagName === 'INPUT' && /^(button|submit|reset)$/i.test(el.type || '')) list.push('value');
    return list;
  }

  function applyAttrs(el) {
    if (skipped(el)) return;
    let rec = attrOrig.get(el);
    attrList(el).forEach((name) => {
      if (!el.hasAttribute(name)) return;
      const cur = el.getAttribute(name);
      const prev = rec && rec[name];
      const orig = prev && prev.shown === cur ? prev.orig : cur;
      const out = mode === 'hant' ? toHant(orig) : orig;
      if (!rec) { rec = {}; attrOrig.set(el, rec); }
      rec[name] = { orig, shown: out };
      if (cur !== out) el.setAttribute(name, out);
    });
  }

  function walk(start) {
    if (!start) return;
    if (start.nodeType === 3) { applyText(start); return; }
    if (start.nodeType !== 1 && start.nodeType !== 9) return;
    const doc = start.ownerDocument || start;
    const it = doc.createTreeWalker(start, 5 /* SHOW_ELEMENT | SHOW_TEXT */);
    let n = start.nodeType === 1 ? start : it.nextNode();
    while (n) {
      if (n.nodeType === 3) applyText(n); else applyAttrs(n);
      n = it.nextNode();
    }
  }

  function setLang(doc) {
    const html = doc.documentElement;
    if (!html) return;
    if (langBefore === null) langBefore = html.getAttribute('lang') || '';
    if (mode === 'hant') html.setAttribute('lang', 'zh-Hant');
    else if (langBefore) html.setAttribute('lang', langBefore);
    else html.removeAttribute('lang');
  }

  function observe(doc) {
    if (observer || typeof root.MutationObserver !== 'function') return;
    observer = new root.MutationObserver((records) => {
      records.forEach((r) => {
        if (r.type === 'characterData') applyText(r.target);
        else if (r.type === 'attributes') applyAttrs(r.target);
        else r.addedNodes.forEach((n) => walk(n));
      });
    });
    observer.observe(doc.documentElement, {
      subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ATTRS.concat(['value']),
    });
  }

  function applyAll(doc) {
    setLang(doc);
    walk(doc.documentElement);
  }

  function setMode(next) {
    const m = next === 'hant' ? 'hant' : 'hans';
    if (root) root.__HOROSA_SHELL_SCRIPT = m;
    if (m === mode) return mode;
    mode = m;
    if (root && root.document && root.document.documentElement) applyAll(root.document);
    return mode;
  }

  function getMode() {
    return mode;
  }

  function start(doc) {
    applyAll(doc);
    observe(doc);
    doc.documentElement.style.removeProperty('visibility');
    // 建窗注入的档位可能已过时(页面在切换简繁之后才重新载入):再向壳确认一次
    const bridge = root.HorosaShellBridge;
    if (bridge && bridge.available && bridge.available()) {
      bridge.invoke('get_shell_script_command').then((m) => setMode(m)).catch(() => {});
    }
  }

  const api = { toHant, setMode, getMode, RUN_SOURCE };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.HorosaShellScript = api;

  if (root && root.document && root.document.documentElement && !(typeof module !== 'undefined' && module.exports)) {
    const doc = root.document;
    // 繁体档:正文转好之前先不显示(最多 1.5 秒),免得先闪一下简体
    if (mode === 'hant') {
      doc.documentElement.style.setProperty('visibility', 'hidden');
      root.setTimeout(() => doc.documentElement.style.removeProperty('visibility'), 1500);
    }
    if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', () => start(doc), { once: true });
    else start(doc);
  }
})(typeof window !== 'undefined' ? window : null);
