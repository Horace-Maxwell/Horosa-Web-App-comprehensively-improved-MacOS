#!/usr/bin/env node
/**
 * CSS-Modules 覆盖 antd 的「权重打平」机械网。
 *
 * 为什么要有它:本仓的 CSS 分散在十几个「运行时追加」的分包里(页面模块一个 async chunk;
 * antd Collapse 的样式被复制进九个 async chunk;antd Radio 在 umi 主表;全站覆盖在 layouts 与
 * xq-ui 两个分包)。样式表落地顺序取决于用户此前逛过哪些技法页与运行时落地序 —— 源码序在这里
 * 【没有定义】。于是「模块覆盖与 antd 权重打平」不是小瑕疵,而是随浏览历史抛硬币:
 *   · 本机实测赢家是 antd → 作者写的样式一行都没生效(FL-20260907-1 记了整族,一次抓到五处)。
 *   · 换台机器 / 换个进页面的路径,赢家可能就换了 —— 这类 bug 复现不了、也测不出。
 * 所以纪律是「每条覆盖必须比被它覆盖的那条严格高至少一个 class」,不是「统一提到某个档」。
 *
 * 判据:对目标 LESS 里每条「同时含模块类与 antd 类」的选择器算权重 b 列(class + 伪类 + 属性
 * 选择器;`:not(X)` 记 X 的权重;`::伪元素` 不计 b),再按台账断言下限。台账里的竞争者权重是
 * 读 antd 4.24 / app.less / xq-ui 源码算出来的,只许加严不许放宽(棘轮)。
 *
 * 用法: node check_css_specificity.js <less 文件…>
 *       node check_css_specificity.js --self-test     # 判别向量自证(计数器 + 台账各一红一绿)
 *   退出码 0 = 全达标;1 = 有打平/欠权重;2 = 环境或用法不对。
 */
const fs = require('fs');

// ── 权重 b 列计数(与浏览器口径一致)──
function bCount(sel) {
  let s = sel;
  let extra = 0;
  // :not() / :is() / :matches() 记参数的权重;:where() 记 0
  s = s.replace(/:(not|is|matches)\(([^()]*)\)/g, (m, fn, inner) => { extra += bCount(inner); return ' '; });
  s = s.replace(/:where\([^()]*\)/g, ' ');
  s = s.replace(/::[a-zA-Z-]+/g, ' ');           // 伪元素进 c 列,不进 b
  const classes = (s.match(/\.[A-Za-z_-][\w-]*/g) || []).length;
  const attrs = (s.match(/\[[^\]]*\]/g) || []).length;
  const pseudos = (s.match(/:[a-zA-Z-]+(\([^()]*\))?/g) || []).length;
  return classes + attrs + pseudos + extra;
}

// ── 台账:命中在前者优先。need = 竞争者权重 + 1。──
// 竞争者出处:antd 4.24 collapse/radio 样式源、src/layouts/app.less、src/components/xq-ui/styles.less。
const LEDGER = [
  { re: /\.ant-radio-button-wrapper-checked(?!\w)/, need: 6, label: '分段选中态', rival: 'xq-ui 暗档 :root:not([…]) .shell .…-checked:not(…) = 5' },
  { re: /\.ant-collapse-arrow/, need: 5, label: '折叠箭头', rival: 'antd …-icon-position-end > …-item > …-header .ant-collapse-arrow = 4' },
  { re: /\.ant-collapse-content-box/, need: 5, label: 'ghost 正文内距', rival: 'antd .ant-collapse-ghost > …-item > …-content > …-content-box = 4' },
  { re: /\.ant-collapse-header/, need: 4, label: '折叠头', rival: 'antd .ant-collapse > …-item > …-header = 3' },
  { re: /\.ant-collapse-content/, need: 4, label: '折叠正文', rival: 'antd .ant-collapse-ghost > …-item > …-content = 3' },
  { re: /\.ant-collapse-item/, need: 4, label: '折叠项', rival: 'antd .ant-collapse > .ant-collapse-item:last-child = 3(:last-child 计入 b 列)' },
  { re: /\.ant-radio-button-wrapper/, need: 3, label: '分段按钮', rival: 'antd .ant-radio-group-small .ant-radio-button-wrapper = 2' },
];

// 只脱掉 `:global(` 与其配对的 `)`,其余括号(如 `:not(…)`)原样保留 —— 一把梭地删所有括号会把
// `:not(.x)` 压成 `:not.x`,权重多算 1,是这个网自己的假红来源。模块类哈希后仍是 1 个 class,
// 所以脱掉包装后的 class 计数与浏览器里的真选择器逐位相同。
function unwrapGlobal(sel) {
  let out = '';
  for (let i = 0; i < sel.length; i += 1) {
    if (sel.startsWith(':global(', i)) {
      let depth = 1;
      let j = i + 8;
      for (; j < sel.length && depth > 0; j += 1) {
        if (sel[j] === '(') depth += 1;
        else if (sel[j] === ')') { depth -= 1; if (depth === 0) break; }
        out += sel[j];
      }
      i = j;
      continue;
    }
    out += sel[i];
  }
  return out;
}
function hasModuleClass(sel) {
  let raw = '';
  for (let i = 0; i < sel.length; i += 1) {
    if (sel.startsWith(':global(', i)) {
      let depth = 1;
      let j = i + 8;
      for (; j < sel.length && depth > 0; j += 1) {
        if (sel[j] === '(') depth += 1;
        else if (sel[j] === ')') { depth -= 1; if (depth === 0) break; }
      }
      i = j;
      raw += ' ';
      continue;
    }
    raw += sel[i];
  }
  return /\.[A-Za-z_-][\w-]*/.test(raw);
}

/** 扫一段 LESS 源码,回 [{sel, b, need, label, ok}] */
function scanSource(src) {
  const out = [];
  const noComment = src.split('\n').map((l) => l.replace(/\/\/.*$/, '')).join('\n');
  const re = /([^{};]+)\{/g;                        // 选择器头可以含括号(:global / :not),但不含 { } ;
  let m;
  while ((m = re.exec(noComment))) {
    const head = m[1];
    if (head.trim().startsWith('@')) continue;      // @media / @supports 等不归本网
    if (head.indexOf('.ant-') < 0) continue;
    head.split(',').forEach((one) => {
      const sel = one.trim().replace(/\s+/g, ' ');
      if (!sel || sel.indexOf('.ant-') < 0) return;
      if (!hasModuleClass(sel)) return;              // 纯全局规则不归本网管
      const flat = unwrapGlobal(sel);
      // 台账认的是「这条规则打在谁身上」:`:not(…)` 里的类是排除项、不是目标,匹配前必须剥掉。
      // 不剥的话,静息态那条 `…-wrapper:not(…-wrapper-checked)` 会被当成选中态规则去要 6 权重 —— 假红。
      const target = flat.replace(/:(not|is|matches|where)\([^()]*\)/g, ' ');
      const hit = LEDGER.find((x) => x.re.test(target));
      if (!hit) return;                               // 台账外的 antd 目标:本网不判,留给人工
      const b = bCount(flat);
      out.push({ sel, b, need: hit.need, label: hit.label, rival: hit.rival, ok: b >= hit.need });
    });
  }
  return out;
}

if (process.argv[2] === '--self-test') {
  // ① 计数器判别向量:伪类 / :not / 伪元素 / 属性选择器各一
  const vec = [['.a.b>.c', 3], ['.a>.b:last-child', 3], ['.a .b:not(.c)', 3], ['.a .b::before', 2],
    ['.a[data-x] .b', 3], [':root:not([data-y="light"]) .s .t:not(.u)', 5], ['.a .b:where(.c)', 2]];
  const cbad = vec.filter(([sel, exp]) => bCount(sel) !== exp);
  console.log((cbad.length ? '❌' : '✅') + ' 判别向量①:权重计数器 ' + (vec.length - cbad.length) + '/' + vec.length
    + (cbad.length ? ' → ' + JSON.stringify(cbad) : ''));
  // ② 台账判别向量:打平必红、提权必绿(同一目标)
  const red = scanSource('.m :global(.ant-collapse-item > .ant-collapse-header) { padding: 0; }');
  const green = scanSource('.m.m :global(.ant-collapse) > :global(.ant-collapse-item) > :global(.ant-collapse-header) { padding: 0; }');
  const okRed = red.length === 1 && red[0].ok === false && red[0].b === 3;
  const okGreen = green.length === 1 && green[0].ok === true;
  console.log((okRed ? '✅' : '❌') + ' 判别向量②:与 antd 打平的折叠头覆盖必判红 → ' + JSON.stringify(red.map((r) => r.b + 'c/' + r.need)));
  console.log((okGreen ? '✅' : '❌') + ' 判别向量③:提权后的同一目标必判绿 → ' + JSON.stringify(green.map((r) => r.b + 'c/' + r.need)));
  process.exit(!cbad.length && okRed && okGreen ? 0 : 1);
}

const files = process.argv.slice(2);
if (!files.length) {
  console.error('用法: node check_css_specificity.js <less 文件…> | --self-test');
  process.exit(2);
}
let bad = 0;
let checked = 0;
for (const f of files) {
  if (!fs.existsSync(f)) { console.error('路径不存在:' + f); process.exit(2); }
  const rows = scanSource(fs.readFileSync(f, 'utf8'));
  checked += rows.length;
  rows.filter((r) => !r.ok).forEach((r) => {
    bad += 1;
    console.log(`❌ ${f}: ${r.label} 权重 ${r.b} < ${r.need}(竞争者 ${r.rival})\n   ${r.sel}`);
  });
}
if (bad) {
  console.log(`❌ CSS 覆盖权重不达标 ${bad} 处(共查 ${checked} 条;打平=随分包序抛硬币,见 FL-20260907-1)`);
  process.exit(1);
}
console.log(`✅ CSS 覆盖权重全达标(共查 ${checked} 条 antd 覆盖,无一与竞争者打平)`);
process.exit(0);
