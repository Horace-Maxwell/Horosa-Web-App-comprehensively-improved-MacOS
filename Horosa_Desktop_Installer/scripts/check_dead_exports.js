#!/usr/bin/env node
/**
 * 「写了函数、没人调」机械网(2026-09-08 进阶复查 D19):扫 src/utils/aiAgent · aiTools · aiChat 三目录的具名导出,
 * 在整个 src(排除测试)里找消费方;零消费 = 死导出 = 红(棘轮表 LEGACY 只许减不许增)。
 *
 * 为什么要有它:cancelPendingApprovals / cancelPendingElicitations / clearSteer 三个导出注释写着「会话切换时用」,
 * 全仓零非测试调用者 —— 与「写了键、没人读」同族,只是对象从存储键换成了函数。登记表只管 data-* 控件,管不到函数。
 *
 * 只管**函数**导出(function 声明 / 箭头或函数表达式常量):常量导出给测试用是合法形态,不算。
 * 消费方判定(宁可超集,不可漏):① 定义模块内部除声明本身之外的任何引用;② 文件 F 只要经 import / import * as / export … from /
 * require() / 动态 import() 引到模块 M,F 里任何与 M 的导出同名的 具名 import 说明符 / 成员访问属性 / 对象解构键 / 重导出名 都算消费。
 * 测试文件(__tests__/*.test.js)不算消费。
 *
 * 用法: node check_dead_exports.js <astrostudyui 目录> [--json]
 *       node check_dead_exports.js <astrostudyui 目录> --self-test     # 判别向量自证(内存文件图;四向量 + 棘轮增长必红)
 *   退出码 0 = 零新增死导出;1 = 有新增(或自证失败);2 = 环境不满足。
 */
const fs = require('fs');
const path = require('path');

const uiRoot = process.argv[2];
const flags = new Set(process.argv.slice(3));
if (!uiRoot) {
  console.error('用法: node check_dead_exports.js <astrostudyui 目录> [--self-test] [--json]');
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

// 扫描面(相对 src):这些目录/文件族的函数导出必须有非测试消费方(D48:此前只有三个 agent 目录,报告/导出/分析工具链是盲区)
const SCAN_DIRS = ['utils/aiAgent', 'utils/aiTools', 'utils/aiChat'];
const SCAN_FILE_RES = [/^utils\/report[A-Za-z0-9]*\.js$/, /^utils\/aiExport[A-Za-z0-9]*\.js$/, /^utils\/aiAnalysis[A-Za-z0-9]*\.js$/, /^services\/aianalysis\.js$/];
// 拆成子模块的大文件(登记表 astrostudyui/scripts/source-sets.json):子模块随门面进 / 出扫描面;门面里「export { x } from './子模块'」
//   只是转手,不算消费 —— 门面的 x 有人用,子模块的 x 才算有人用;报告里子模块的条目记在门面名下(棘轮表 / 可选消费表的键不变)。
let SOURCE_SETS = new Map();   // 门面路径(相对 src)→ [子模块路径(相对 src)…]
function loadSourceSets(){
  const m = new Map();
  try {
    const sets = JSON.parse(fs.readFileSync(path.join(uiRoot, 'scripts', 'source-sets.json'), 'utf8')).sets || {};
    for (const [facade, v] of Object.entries(sets)) m.set(facade, (v.files || []).map((f) => `${v.dir}/${f}`));
  } catch (e) { /* 登记表不在 = 没有拆过的文件 */ }
  return m;
}
function facadeOf(file){ for (const [facade, subs] of SOURCE_SETS) { if (subs.indexOf(file) >= 0) return facade; } return null; }
function inScanFace(file, scanDirs){
  const facade = facadeOf(file);
  if (facade) return inScanFace(facade, scanDirs);
  return scanDirs.some((d) => file.startsWith(d + '/')) || SCAN_FILE_RES.some((re) => re.test(file));
}
// 豁免:测试专用重置钩(约定名)
const EXEMPT_RE = /ForTests$/;
// 评测装置文件(src/test 下的 jest 驱动 CLI 主体与磁带):视为真消费方(登记表按检出里有的装置补)
const HARNESS_CONSUMERS = new Set();
// astrostudyui/scripts 下的 node CLI(evalCompare/evalAb 等)也是真消费方:按标识符文本命中计入(它们在 src 之外,不走 import 解析)
const SCRIPTS_DIR_CONSUMERS = true;
// 棘轮:既往存量(路径:导出名);只许减不许增 —— 清掉一条就从此表删一条。首次落地时的存量见下(每条都是「导出了但全仓零调用」)。
// 可选消费方:这些共享导出的消费方文件不在时扫不到消费方,但不是死导出(对应文件不在则跳过)。
const OPTIONAL_CONSUMED = new Set([
  'utils/aiExportDocModel.js:parseMarkdownSectionBlocks',
  'utils/aiExportDocModel.js:planCaptureSegments',
  'utils/aiExport.js:getAIExportPresetKeys',
  'utils/aiExport.js:migrateSplitSegments',
  'utils/aiAnalysisRag.js:rankChunksByKeywordWithExtra',
  'utils/aiAnalysisRag.js:filterMaterialsBySchools',
  'utils/aiAnalysisProviders.js:setPersistedThinkingLevel',
  'utils/aiAnalysisProviders.js:getPersistedThinkingLevel',
  // 库内读改写单一入口:合同测试 aiAnalysisStoreRecoverMerge 要求新增的单例文档写点一律经它(测试本身也直测它)
  'utils/aiAnalysisStore.js:mergeStoreRecord',
]);
const LEGACY = new Set([
  // 2026-09-08 存量 11 条已逐条处置(9 删 2 接线),棘轮归零:从此任何一条新死导出 = 红,不再有逃生口。
]);

const PLUGINS = ['jsx', 'classProperties', 'classPrivateProperties', 'classPrivateMethods', 'objectRestSpread', 'optionalChaining',
  'nullishCoalescingOperator', 'dynamicImport', 'exportDefaultFrom', 'exportNamespaceFrom', 'numericSeparator', 'optionalCatchBinding',
  'logicalAssignment', 'topLevelAwait', ['decorators', { decoratorsBeforeExport: true }]];

function parse(code, file) {
  return parser.parse(code, { sourceType: 'module', plugins: PLUGINS, errorRecovery: true, sourceFilename: file });
}

// files: Map<相对 src 路径, 源码>;返回 { exportsOf: Map<file, Set<name>>, consumed: Set<'file:name'> }
function analyze(files) {
  const has = (p) => files.has(p);
  function resolve(fromFile, src) {
    if (!src || typeof src !== 'string') return null;
    let base;
    if (src.startsWith('@/')) base = src.slice(2);
    else if (src.startsWith('.')) base = path.posix.normalize(path.posix.join(path.posix.dirname(fromFile), src));
    else return null;
    for (const cand of [base, base + '.js', base + '.jsx', base + '/index.js']) { if (has(cand)) return cand; }
    return null;
  }
  const exportsOf = new Map();
  const fnExportsOf = new Map();
  const internalUse = new Set();
  const asts = new Map();
  for (const [file, code] of files) {
    let ast;
    try { ast = parse(code, file); } catch (e) { continue; }
    asts.set(file, ast);
    const names = new Set();          // 全部具名导出(供消费判定)
    const fnNames = new Set();        // 其中的函数导出(受检面)
    for (const node of ast.program.body) {
      if (node.type !== 'ExportNamedDeclaration') continue;
      if (node.declaration) {
        const d = node.declaration;
        if (d.type === 'FunctionDeclaration' || d.type === 'ClassDeclaration') { if (d.id) { names.add(d.id.name); if (d.type === 'FunctionDeclaration') fnNames.add(d.id.name); } }
        else if (d.type === 'VariableDeclaration') {
          for (const dec of d.declarations) {
            if (dec.id.type === 'Identifier') { names.add(dec.id.name); if (dec.init && (dec.init.type === 'ArrowFunctionExpression' || dec.init.type === 'FunctionExpression')) fnNames.add(dec.id.name); }
            else if (dec.id.type === 'ObjectPattern') for (const p of dec.id.properties) { if (p.type === 'ObjectProperty' && p.value.type === 'Identifier') names.add(p.value.name); }
          }
        }
      }
      for (const s of node.specifiers || []) { if (s.exported && s.exported.type === 'Identifier') names.add(s.exported.name); }
    }
    exportsOf.set(file, names);
    fnExportsOf.set(file, fnNames);
    // ① 模块内部引用:除声明本身与导出说明符之外,任何同名标识符出现 = 内部消费
    const internal = new Map();
    try{ traverse(ast, {
      Identifier(p) {
        const n = p.node.name; if (!fnNames.has(n)) return;
        const par = p.parent;
        if (par && ((par.type === 'FunctionDeclaration' && par.id === p.node) || (par.type === 'VariableDeclarator' && par.id === p.node) || par.type === 'ExportSpecifier')) return;
        if (par && par.type === 'MemberExpression' && par.property === p.node && !par.computed) return;   // obj.foo 的 foo 不是本模块的绑定
        if (par && par.type === 'ObjectProperty' && par.key === p.node && !par.computed && par.value !== p.node) return;
        internal.set(n, (internal.get(n) || 0) + 1);
      },
    }); }catch(e){ console.error(`[check_dead_exports] traverse 失败 ${file}: ${e && e.message}`); continue; }
    for (const [n, c] of internal) { if (c > 0) internalUse.add(`${file}:${n}`); }
  }
  const consumed = new Set();
  const passThrough = [];             // [门面, 门面导出名, 子模块, 子模块导出名]
  for (const [file, ast] of asts) {
    const isTest = /(^|\/)__tests__\//.test(file) || /\.test\.jsx?$/.test(file) || /(^|\/)test\//.test(file);
    // 评测装置(jest 驱动的 CLI 主体 + 磁带)是真消费方,不是单元测试:有的导出只被它们消费
    if (isTest && !HARNESS_CONSUMERS.has(file)) continue;
    const deps = new Set();            // 本文件引到的模块
    const direct = [];                 // [模块, 导出名] 直接说明符
    const ownSubs = SOURCE_SETS.get(file) || [];   // 门面引自己的子模块:只是转手
    traverse(ast, {
      ImportDeclaration(p) {
        const m = resolve(file, p.node.source.value); if (!m) return; if (ownSubs.indexOf(m) >= 0) return; deps.add(m);
        for (const s of p.node.specifiers) { if (s.type === 'ImportSpecifier') direct.push([m, s.imported.type === 'Identifier' ? s.imported.name : s.imported.value]); }
      },
      ExportNamedDeclaration(p) {
        if (!p.node.source) return;
        const m = resolve(file, p.node.source.value); if (!m) return;
        if (ownSubs.indexOf(m) >= 0) { for (const s of p.node.specifiers) { if (s.type === 'ExportSpecifier') passThrough.push([file, s.exported.name, m, s.local.name]); } return; }
        deps.add(m);
        for (const s of p.node.specifiers) { if (s.type === 'ExportSpecifier') direct.push([m, s.local.name]); }
      },
      ExportAllDeclaration(p) { const m = resolve(file, p.node.source.value); if (m) { deps.add(m); for (const n of exportsOf.get(m) || []) direct.push([m, n]); } },
      CallExpression(p) {
        const c = p.node.callee; const a = p.node.arguments[0];
        if (!a || a.type !== 'StringLiteral') return;
        if ((c.type === 'Identifier' && c.name === 'require') || c.type === 'Import') { const m = resolve(file, a.value); if (m) deps.add(m); }
      },
    });
    for (const [m, n] of direct) consumed.add(`${m}:${n}`);
    if (!deps.size) continue;
    // 宽判:引到的模块的任一导出名,只要在本文件里以 成员属性 / 解构键 / 标识符 形态出现,就算消费
    const seen = new Set();
    traverse(ast, {
      MemberExpression(p) { const pr = p.node.property; if (!p.node.computed && pr.type === 'Identifier') seen.add(pr.name); },
      OptionalMemberExpression(p) { const pr = p.node.property; if (!p.node.computed && pr.type === 'Identifier') seen.add(pr.name); },
      ObjectProperty(p) { const k = p.node.key; if (!p.node.computed && k.type === 'Identifier' && p.parent && p.parent.type === 'ObjectPattern') seen.add(k.name); },
      Identifier(p) { seen.add(p.node.name); },
    });
    for (const m of deps) for (const n of exportsOf.get(m) || []) { if (seen.has(n)) consumed.add(`${m}:${n}`); }
  }
  for (const k of internalUse) consumed.add(k);
  for (const [facade, exported, subFile, local] of passThrough) { if (consumed.has(`${facade}:${exported}`)) consumed.add(`${subFile}:${local}`); }
  return { exportsOf, fnExportsOf, consumed };
}

function scriptsText() {
  try {
    const dir = path.join(uiRoot, 'scripts');
    return fs.readdirSync(dir).filter((n) => /\.js$/.test(n)).map((n) => fs.readFileSync(path.join(dir, n), 'utf8')).join('\n');
  } catch (e) { return ''; }
}
function deadExports(files, scanDirs, opts) {
  const { fnExportsOf, consumed } = analyze(files);
  // scripts 文本消费只在真扫描时启用(self-test 的内存向量名如 lonely/outer 会被脚本文本误命中)
  const scripts = opts && typeof opts.scripts === 'string' ? opts.scripts : '';
  const out = [];
  for (const [file, names] of fnExportsOf) {
    if (!inScanFace(file, scanDirs)) continue;
    for (const n of names) { if (EXEMPT_RE.test(n)) continue; if (consumed.has(`${file}:${n}`)) continue; if (scripts && new RegExp('\\b' + n + '\\b').test(scripts)) continue; out.push(`${facadeOf(file) || file}:${n}`); }
  }
  return out.sort();
}

function loadRepo() {
  const srcRoot = path.join(uiRoot, 'src');
  const files = new Map();
  (function walk(dir) {
    for (const name of fs.readdirSync(dir)) {
      if (name === 'node_modules' || name.startsWith('.')) continue;
      const p = path.join(dir, name);
      const st = fs.statSync(p);
      if (st.isDirectory()) walk(p);
      else if (/\.jsx?$/.test(name)) files.set(path.relative(srcRoot, p).split(path.sep).join('/'), fs.readFileSync(p, 'utf8'));
    }
  })(srcRoot);
  return files;
}

function selfTest() {
  const V = [];
  const base = new Map([
    ['utils/aiAgent/a.js', 'export function foo(){}\nexport function bar(){}\nexport const baz = ()=>1;\nexport const ONLY_CONST = 1;\nexport function __resetForTests(){}\nexport function lonely(){}\nexport function inner(){}\nexport function outer(){ return inner(); }\n'],
    ['utils/aiAgent/b.js', "import { foo } from './a';\nexport function useFoo(){ return foo(); }\n"],
    ['components/x.js', "import * as A from '../utils/aiAgent/a';\nimport { useFoo } from '../utils/aiAgent/b';\nexport default function X(){ return A.bar() + useFoo(); }\n"],
    ['layouts/y.js', "let m = null;\nfunction load(){ if(!m){ m = import('../utils/aiAgent/a').then((mod)=>({ baz: mod.baz })); } return m; }\nexport { load };\n"],
    ['utils/__tests__/a.test.js', "import { lonely } from '../aiAgent/a';\nit('x', ()=>lonely());\n"],
  ]);
  const dead1 = deadExports(base, SCAN_DIRS, { scripts: '' });
  V.push(['具名/命名空间/动态 import/模块内部调用 四种消费都认;常量不受检;测试不算消费;__*ForTests 豁免;outer 零调用', JSON.stringify(dead1) === JSON.stringify(['utils/aiAgent/a.js:lonely', 'utils/aiAgent/a.js:outer']), dead1]);
  const noNs = new Map(base); noNs.set('components/x.js', "import { useFoo } from '../utils/aiAgent/b';\nexport default function X(){ return useFoo(); }\n");
  const dead2 = deadExports(noNs, SCAN_DIRS, { scripts: '' });
  V.push(['拿掉命名空间消费 → bar 变死', dead2.indexOf('utils/aiAgent/a.js:bar') >= 0 && dead2.indexOf('utils/aiAgent/a.js:foo') < 0, dead2]);
  const noDyn = new Map(base); noDyn.delete('layouts/y.js');
  const dead3 = deadExports(noDyn, SCAN_DIRS, { scripts: '' });
  V.push(['拿掉动态 import 消费 → baz 变死', dead3.indexOf('utils/aiAgent/a.js:baz') >= 0, dead3]);
  const reexp = new Map(base); reexp.set('utils/aiAgent/index.js', "export { lonely } from './a';\n"); reexp.set('pages/z.js', "import { lonely } from '../utils/aiAgent';\nexport default lonely;\n");
  const dead4 = deadExports(reexp, SCAN_DIRS, { scripts: '' });
  V.push(['经 index 重导出后被页面引用 → lonely 不再死(outer 仍死)', JSON.stringify(dead4) === JSON.stringify(['utils/aiAgent/a.js:outer']), dead4]);
  // 拆成子模块的门面:门面转手不算消费;门面的名字有人用 → 子模块的才算有人用;子模块的条目记在门面名下
  const savedSets = SOURCE_SETS;
  SOURCE_SETS = new Map([['utils/aiAgent/big.js', ['utils/aiAgent/big/part.js']]]);
  const split = new Map([
    ['utils/aiAgent/big/part.js', 'export function used(){}\nexport function unused(){}\n'],
    ['utils/aiAgent/big.js', "import './a';\nexport { used, unused } from './big/part';\n"],
    ['pages/w.js', "import { used } from '../utils/aiAgent/big';\nexport default used;\n"],
  ]);
  const dead5 = deadExports(split, SCAN_DIRS, { scripts: '' });
  SOURCE_SETS = savedSets;
  V.push(['门面转手不算消费:子模块里只经门面导出、没人用的函数判死,记在门面名下', JSON.stringify(dead5) === JSON.stringify(['utils/aiAgent/big.js:unused']), dead5]);
  // 棘轮增长必红:LEGACY 之外出现一条 = 红
  const grown = ['utils/aiAgent/a.js:lonely'].filter((k) => !LEGACY.has(k));
  V.push(['棘轮表外的死导出必须判红', grown.length === 1, grown]);
  let bad = 0;
  for (const [note, ok, detail] of V) { if (!ok) bad += 1; console.log(`${ok ? '✅' : '❌'} ${note}${ok ? '' : ' → ' + JSON.stringify(detail)}`); }
  console.log(`== 死导出检查器判别向量:${V.length - bad}/${V.length} 按预期 ==`);
  return bad ? 1 : 0;
}

if (flags.has('--self-test')) process.exit(selfTest());
SOURCE_SETS = loadSourceSets();
const files = loadRepo();
const dead = deadExports(files, SCAN_DIRS, { scripts: scriptsText() });
const fresh = dead.filter((k) => !LEGACY.has(k) && !OPTIONAL_CONSUMED.has(k));
const stale = Array.from(LEGACY).filter((k) => dead.indexOf(k) < 0);
if (flags.has('--json')) { console.log(JSON.stringify({ dead, fresh, stale }, null, 1)); }
if (stale.length) console.log(`⚠️ 棘轮表里已不再死的条目(可从 LEGACY 删除):${stale.join(', ')}`);
if (fresh.length) {
  console.log(`❌ 新增死导出 ${fresh.length} 条(导出了、全仓零非测试调用者;要么接线要么删):\n  ${fresh.join('\n  ')}`);
  process.exit(1);
}
console.log(`✅ 零新增死导出(扫 ${SCAN_DIRS.join(' / ')} + report*/aiExport*/aiAnalysis*/services 共 ${files.size} 文件;存量 ${dead.length} 条在棘轮表内)`);
process.exit(0);
