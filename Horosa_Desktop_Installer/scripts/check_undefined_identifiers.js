#!/usr/bin/env node
/**
 * 静态扫「引用了却在任何作用域都没声明」的标识符(浏览器 / ES / Node / jest 全局白名单之外),
 * 以及「const / let 在自己的初值里读自己」(`const x = x || {}`):
 * 原生 JS 下这是暂时性死区 ReferenceError,经 Babel 降成 var 后又静默变成 undefined,两种结果都错。
 *
 * 为什么要有它:手工维护的大文件里删掉一行 `const xxxRef = React.useRef(null)` 而别处还传着 `xxxRef`,
 * 语法完全合法、构建照过、单测不渲染该组件也照绿,只有真打开页面才 ReferenceError 整页白。
 * 本脚本用 Babel 作用域分析做机械网:任何未声明引用 = 红。
 *
 * 用法: node check_undefined_identifiers.js <astrostudyui 目录> <相对 src 的目录或文件…>
 *       node check_undefined_identifiers.js <astrostudyui 目录> --self-test   # 判别向量自证(一红一绿)
 *   退出码 0 = 零新增未声明引用;1 = 有;2 = 环境不满足(缺 @babel/parser 或路径不存在)。
 *   存量棘轮表 LEGACY 在脚本内:只许减不许增,清掉一条就从表里删一条。
 */
const fs = require('fs');
const path = require('path');

const uiRoot = process.argv[2];
const targets = process.argv.slice(3);
if (!uiRoot || !targets.length) {
  console.error('用法: node check_undefined_identifiers.js <astrostudyui 目录> <相对 src 的目录或文件…>');
  process.exit(2);
}
let parser;
let traverse;
try {
  parser = require(path.join(uiRoot, 'node_modules', '@babel', 'parser'));
  traverse = require(path.join(uiRoot, 'node_modules', '@babel', 'traverse')).default;
} catch (e) {
  console.error('缺 @babel/parser 或 @babel/traverse:' + e.message);
  process.exit(2);
}

const GLOBALS = new Set((
  'window document navigator location history localStorage sessionStorage indexedDB console ' +
  'setTimeout clearTimeout setInterval clearInterval requestAnimationFrame cancelAnimationFrame requestIdleCallback cancelIdleCallback ' +
  'fetch Request Response Headers AbortController AbortSignal URL URLSearchParams Blob File FileList FileReader FormData TextEncoder TextDecoder ' +
  'Image Audio Event CustomEvent MouseEvent KeyboardEvent FocusEvent InputEvent ClipboardEvent PointerEvent WheelEvent TouchEvent DragEvent ' +
  'MessageEvent ErrorEvent ProgressEvent UIEvent EventTarget Node Element HTMLElement HTMLInputElement HTMLTextAreaElement HTMLSelectElement ' +
  'HTMLCanvasElement HTMLImageElement HTMLAnchorElement HTMLButtonElement HTMLDivElement SVGElement SVGSVGElement Document DocumentFragment ' +
  'Range Selection MutationObserver ResizeObserver IntersectionObserver PerformanceObserver performance screen devicePixelRatio innerWidth innerHeight ' +
  'outerWidth outerHeight scrollX scrollY pageXOffset pageYOffset getComputedStyle matchMedia scrollTo scrollBy alert confirm prompt atob btoa crypto ' +
  'structuredClone queueMicrotask WebSocket EventSource XMLHttpRequest Worker SharedWorker Notification ImageData OffscreenCanvas createImageBitmap ' +
  'DOMParser XMLSerializer XPathResult CSS CanvasRenderingContext2D Path2D DOMRect DOMRectReadOnly DOMMatrix DOMPoint MediaQueryList ' +
  'IDBKeyRange IDBRequest IDBDatabase IDBTransaction IDBObjectStore IDBCursor IDBIndex visualViewport self globalThis top parent frames open close print ' +
  'getSelection speechSynthesis SpeechSynthesisUtterance DataTransfer ClipboardItem Intl WebAssembly SharedArrayBuffer Atomics BigInt BigInt64Array ' +
  'BigUint64Array FinalizationRegistry WeakRef AggregateError AudioContext webkitAudioContext MediaRecorder MediaStream HTMLMediaElement ' +
  'HTMLVideoElement HTMLAudioElement ImageBitmap Path2D TextMetrics FontFace CompressionStream DecompressionStream ReadableStream WritableStream ' +
  'TransformStream ResizeObserverEntry IntersectionObserverEntry PerformanceEntry PerformanceNavigationTiming NodeFilter NodeList HTMLCollection ' +
  'process require module exports __dirname __filename Buffer global setImmediate clearImmediate ' +
  'jest describe it test expect beforeEach afterEach beforeAll afterAll xit xdescribe fit fdescribe Storage DOMException ' +
  'arguments undefined NaN Infinity'
).split(/\s+/).filter(Boolean));

// 既往存量(棘轮:只许减不许增;键 = 相对 src 的路径 + ':' + 标识符,解析失败记 ':parse')。
// 新增任何一条 = 红;这里的都是历史遗留,逐条清掉后从此表删除。
const LEGACY = new Set([
  'components/astro3d/vendor/DRACOLoader.js:DracoDecoderModule',   // 第三方解码器运行时全局
]);

const PLUGINS = ['jsx', 'classProperties', 'classPrivateProperties', 'classPrivateMethods', 'objectRestSpread', 'optionalChaining',
  'nullishCoalescingOperator', 'dynamicImport', 'exportDefaultFrom', 'exportNamespaceFrom', 'numericSeparator', 'optionalCatchBinding',
  'logicalAssignment', 'topLevelAwait', ['decorators', { decoratorsBeforeExport: true }]];

function listFiles(p) {
  const st = fs.statSync(p);
  if (st.isFile()) return /\.jsx?$/.test(p) ? [p] : [];
  const out = [];
  for (const name of fs.readdirSync(p)) {
    if (name === 'node_modules' || name.startsWith('.')) continue;
    out.push(...listFiles(path.join(p, name)));
  }
  return out;
}

const problems = [];
const legacyHits = [];
let files = 0;
let parseErrors = 0;
const keyOf = (f, ident) => path.relative(path.join(uiRoot, 'src'), f).split(path.sep).join('/') + ':' + ident;

/** 扫一段源码,回未声明引用名单(不含白名单/存量判断)。 */
function scanSource(src) {
  const found = [];
  const ast = parser.parse(src, { sourceType: 'module', plugins: PLUGINS, errorRecovery: false });
  traverse(ast, {
    // JSX 正文里写成注释样子的文字(`</span>   /* 说明 */</div>`):JSX 里它不是注释,会原样渲染到页面上
    JSXText(p) {
      const v = p.node.value;
      if (/\/\*|\*\/|(^|\s)\/\/\s/.test(v)) found.push({ name: v.trim().slice(0, 40), line: p.node.loc ? p.node.loc.start.line : 0, jsxComment: true });
    },
    ReferencedIdentifier(p) {
      const name = p.node.name;
      const binding = p.scope.getBinding(name);
      if (binding && (binding.kind === 'const' || binding.kind === 'let') && binding.path.isVariableDeclarator()) {
        // 声明前自引用:读点落在自己声明的初值里,且不在初值里的函数体内(函数体是之后才调用的,不算)
        const initPath = binding.path.get('init');
        if (initPath.node && p.isDescendant(initPath)) {
          const fn = p.getFunctionParent();
          if (!(fn && (fn === initPath || fn.isDescendant(initPath)))) {
            found.push({ name, line: p.node.loc ? p.node.loc.start.line : 0, selfRef: true });
          }
        }
      }
      if (GLOBALS.has(name)) return;
      if (p.scope.hasBinding(name)) return;
      if (p.parentPath && p.parentPath.isUnaryExpression({ operator: 'typeof' })) return;
      found.push({ name, line: p.node.loc ? p.node.loc.start.line : 0 });
    },
  });
  return found;
}

if (targets[0] === '--self-test') {
  // 判别向量:① 传了未声明的 xxxRef 必抓到;② 同形但声明了的必零命中;③ JSX 组件名/typeof 守卫/白名单全局不误报
  const red = scanSource("import React from 'react';\nexport function A(){ const x = useHook({ a: 1, fooRef }); return <div onClick={()=>window.alert(x)}/>; }");
  const green = scanSource("import React from 'react';\nimport Foo from './Foo';\nexport function A(){ const fooRef = React.useRef(null); const x = useHook2({ fooRef }); if (typeof gtag !== 'undefined') { window.gtag('x'); } return <Foo onClick={()=>document.title = String(x)}/>; }\nfunction useHook2(o){ return o; }");
  const okRed = red.length === 2 && red.some((r) => r.name === 'fooRef') && red.some((r) => r.name === 'useHook');
  const okGreen = green.length === 0;
  console.log((okRed ? '✅' : '❌') + ' 判别向量①:未声明 fooRef/useHook 必抓 → ' + JSON.stringify(red.map((r) => r.name)));
  console.log((okGreen ? '✅' : '❌') + ' 判别向量②:声明后零命中 + typeof 守卫/JSX 组件/白名单不误报 → ' + JSON.stringify(green.map((r) => r.name)));
  // ③ 声明前自引用:外层同名的参数被内层 const 遮蔽并在初值里读自己 → 必抓;递归函数 / 方法体里引用自己 / 普通遮蔽 → 不误报
  const selfRed = scanSource("export function A({ layout }){ function inner(){ const layout = layout || {}; return layout.up; } return inner(); }");
  const selfGreen = scanSource("const walk = (n)=>(n > 0 ? walk(n - 1) : 0);\nconst token = { get(){ return token; } };\nexport function B({ layout }){ function inner(){ const cur = layout || {}; const layout2 = cur; return layout2; } return [walk(2), token.get(), inner()]; }");
  const okSelfRed = selfRed.length === 1 && selfRed[0].name === 'layout' && selfRed[0].selfRef === true;
  const okSelfGreen = selfGreen.length === 0;
  console.log((okSelfRed ? '✅' : '❌') + ' 判别向量③:const x = x || {} 必抓 → ' + JSON.stringify(selfRed.map((r) => r.name)));
  console.log((okSelfGreen ? '✅' : '❌') + ' 判别向量④:递归 / 方法体自引用 / 普通改名不误报 → ' + JSON.stringify(selfGreen.map((r) => r.name)));
  // ⑤ JSX 正文里的注释写法必抓;真 JSX 注释 {/* */}、正文里的普通斜杠不误报
  const jsxRed = scanSource("export function A({ y }){ return <div>{y}   /* 同一函数 */</div>; }");
  const jsxGreen = scanSource("export function A({ y }){ return <div>{y}{/* 同一函数 */} 1/2 a/b</div>; }");
  const okJsxRed = jsxRed.length === 1 && jsxRed[0].jsxComment === true;
  const okJsxGreen = jsxGreen.length === 0;
  console.log((okJsxRed ? '✅' : '❌') + ' 判别向量⑤:JSX 正文里的 /* … */ 必抓 → ' + JSON.stringify(jsxRed.map((r) => r.name)));
  console.log((okJsxGreen ? '✅' : '❌') + ' 判别向量⑥:真 JSX 注释与正文斜杠不误报 → ' + JSON.stringify(jsxGreen.map((r) => r.name)));
  process.exit(okRed && okGreen && okSelfRed && okSelfGreen && okJsxRed && okJsxGreen ? 0 : 1);
}

for (const t of targets) {
  const abs = path.isAbsolute(t) ? t : path.join(uiRoot, 'src', t);
  if (!fs.existsSync(abs)) {
    console.error('路径不存在:' + abs);
    process.exit(2);
  }
  for (const f of listFiles(abs)) {
    files += 1;
    const src = fs.readFileSync(f, 'utf8');
    let refs;
    try {
      refs = scanSource(src);
    } catch (e) {
      parseErrors += 1;
      (LEGACY.has(keyOf(f, 'parse')) ? legacyHits : problems).push(`${path.relative(uiRoot, f)}:${(e.loc && e.loc.line) || 0} 解析失败 ${e.message.split('\n')[0]}`);
      continue;
    }
    for (const r of refs) {
      (LEGACY.has(keyOf(f, r.name)) ? legacyHits : problems).push(`${path.relative(uiRoot, f)}:${r.line} ${r.jsxComment ? 'JSX 正文里的注释写法(会渲染到页面)' : (r.selfRef ? '声明前自引用' : '未声明引用')} ${r.name}`);
    }
  }
}

if (legacyHits.length) {
  console.log(legacyHits.map((l) => '  ⚠️ 存量 ' + l).join('\n'));
}
if (problems.length) {
  console.log(problems.join('\n'));
  console.log(`❌ 未声明引用 ${problems.length} 处(扫 ${files} 文件,解析失败 ${parseErrors};存量 ${legacyHits.length} 处另计)`);
  process.exit(1);
}
console.log(`✅ 零新增未声明引用(扫 ${files} 文件;存量 ${legacyHits.length} 处在棘轮表内)`);
process.exit(0);
