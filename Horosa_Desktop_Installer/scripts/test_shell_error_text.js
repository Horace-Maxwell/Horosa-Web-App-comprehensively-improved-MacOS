#!/usr/bin/env node
/**
 * 壳自带页面(启动器 / 设置 / 诊断)自检:
 *   ① 报错文字:壳层命令失败时回来的系统原文(英文、带 os error 码)必须先换成一句看得懂的中文再上屏
 *      (web/shell_errors.js);诊断页另列原始信息,资产状态显示中文叫法。
 *   ② 调壳命令的唯一入口 web/shell_bridge.js:三页都先载入它,只认 __TAURI_INTERNALS__,没有桥时以中文失败。
 *   ③ 页面脚本用到的元素 id 都在各自 html 里,用的地方不判空。
 * 用法: node test_shell_error_text.js [仓库根]    退出码 0 = 全过;1 = 有不符。
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const repoRoot = path.resolve(process.argv[2] || path.join(__dirname, '..', '..'));
const webDir = path.join(repoRoot, 'Horosa_Desktop_Installer', 'web');
const errors = require(path.join(webDir, 'shell_errors.js'));

const V = [];
const eq = (note, got, want) => V.push([note, got === want, `got ${JSON.stringify(got)} want ${JSON.stringify(want)}`]);
const ok = (note, cond, detail) => V.push([note, !!cond, detail || '']);

// ── 映射 ──
eq('中文前缀 + 磁盘满', errors.plain('影子副本落盘失败: No space left on device (os error 28)'), '影子副本落盘失败：磁盘空间不足');
eq('中文前缀 + 找不到文件', errors.plain('备份读取失败: No such file or directory (os error 2)'), '备份读取失败：找不到需要的文件或文件夹');
ok('英文上下文 + 权限', /^没有访问权限/.test(errors.plain('read_dir /Users/x: Permission denied (os error 13)')), errors.plain('read_dir /Users/x: Permission denied (os error 13)'));
ok('Error 对象 + Operation not permitted', /^没有访问权限/.test(errors.plain(new Error('Operation not permitted (os error 1)'))));
eq('只读磁盘', errors.plain('Read-only file system (os error 30)'), '磁盘或文件夹是只读的，写不进去');
eq('壳层中文说明原样', errors.plain('当前没有待确认的安装审查'), '当前没有待确认的安装审查');
eq('不认识的英文 → 通用中文', errors.plain('missing app_data_dir'), '操作没有完成（详细信息可在诊断页查看，或导出诊断包）。');
eq('空错误', errors.plain(''), '操作没有完成。');
const withDetail = errors.withDetail('影子副本写入失败: No space left on device (os error 28)');
ok('诊断页:中文一句 + 原始信息', withDetail.indexOf('影子副本写入失败：磁盘空间不足') === 0 && withDetail.indexOf('原始信息：影子副本写入失败: No space left') > 0, withDetail);
eq('诊断页:已是中文就不重复', errors.withDetail('当前没有待确认的安装审查'), '当前没有待确认的安装审查');
for (const s of ['missing app_data_dir', 'read_dir /x: Permission denied (os error 13)', 'Broken pipe (os error 32)', 'operation timed out']) {
  ok(`上屏文字不带英文原文:${s}`, !/[A-Za-z]{4,}/.test(errors.plain(s)), errors.plain(s));
}

// ── 三个页面都接上了 ──
const PAGES = [['diagnostics.html', 'diagnostics.js'], ['settings.html', 'settings.js'], ['index.html', 'app.js']];
for (const [html, js] of PAGES) {
  const h = fs.readFileSync(path.join(webDir, html), 'utf8');
  const a = h.indexOf('<script src="./shell_errors.js"></script>');
  const m = h.indexOf('<script src="./shell_bridge.js"></script>');
  const b = h.indexOf(`<script src="./${js}"></script>`);
  ok(`${html} 先载 shell_errors.js 再载 ${js}`, a >= 0 && b > a);
  ok(`${html} 先载 shell_bridge.js 再载 ${js}`, m >= 0 && b > m);
}
const diag = fs.readFileSync(path.join(webDir, 'diagnostics.js'), 'utf8');
const settings = fs.readFileSync(path.join(webDir, 'settings.js'), 'utf8');
const app = fs.readFileSync(path.join(webDir, 'app.js'), 'utf8');
ok('诊断页不再把壳层原文直接上屏', !/textContent = error\.message \|\| String\(error\)/.test(diag));
ok('诊断页报错走 withDetail', /HorosaShellErrors\.withDetail\(error\)/.test(diag));
ok('诊断页资产状态显示中文', /ASSET_STATE_LABELS\[item\.state\]/.test(diag) && /cache_only: '待清理缓存'/.test(diag));
ok('设置页提示不再直出原文', !/showToast\(error\.message \|\| String\(error\)\)/.test(settings) && /HorosaShellErrors\.plain\(error\)/.test(settings));
ok('启动器「操作失败」走中文', /操作失败：\$\{window\.HorosaShellErrors \? window\.HorosaShellErrors\.plain\(error\)/.test(app));
// shell_errors.js 总在页面脚本之前载入(上面逐页锁住),设置页 / 诊断页的报错文字不需要「没载入」的退路
for (const [name, src] of [['设置页', settings], ['诊断页', diag]]) {
  ok(`${name} errorText 直接走 shell_errors.js`, !/\(error && error\.message\) \|\| String\(error\)/.test(src));
}

// ── 调壳命令的唯一入口 shell_bridge.js ──
// 打包版只有 __TAURI_INTERNALS__(没开 withGlobalTauri,全局 Tauri 对象不存在):三页共用一个入口,不再各写一份探测。
const bridgeSrc = fs.readFileSync(path.join(webDir, 'shell_bridge.js'), 'utf8');
function loadBridge(win) {
  const sandbox = { window: win };
  vm.runInNewContext(bridgeSrc, sandbox);
  return win.HorosaShellBridge;
}
const BRIDGE_DOWN = '无法连接桌面程序，请重新打开星阙后重试';
const asyncChecks = [];
{
  const calls = [];
  const win = { __TAURI_INTERNALS__: { invoke: (cmd, args) => { calls.push([cmd, args]); return Promise.resolve({ echoed: cmd }); } } };
  const bridge = loadBridge(win);
  ok('有桥:available() 为真', bridge.available() === true);
  asyncChecks.push(bridge.invoke('read_diagnostics_snapshot', { a: 1 }).then(
    (r) => ok('有桥:命令原样转给 __TAURI_INTERNALS__.invoke', r && r.echoed === 'read_diagnostics_snapshot' && calls.length === 1 && calls[0][1].a === 1, JSON.stringify(calls)),
    (e) => ok('有桥:命令原样转给 __TAURI_INTERNALS__.invoke', false, String(e))
  ));
}
{
  const bridge = loadBridge({});
  ok('无桥:available() 为假', bridge.available() === false);
  let syncThrow = false;
  let p = null;
  try { p = bridge.invoke('load_preferences_payload'); } catch (e) { syncThrow = true; }
  ok('无桥:invoke 返回被拒的 Promise 而不是同步抛错(页面用 .catch 接)', !syncThrow && p && typeof p.then === 'function');
  if (p) {
    asyncChecks.push(p.then(
      () => ok('无桥:调用以中文失败', false, 'resolved'),
      (e) => ok('无桥:调用以中文失败', e && e.message === BRIDGE_DOWN, String(e && e.message))
    ));
  }
}
{
  // 只有全局 Tauri 对象、没有 __TAURI_INTERNALS__ 的环境在打包版里不存在,不再当作可用的桥
  const globalKey = ['__TAURI', '__'].join('');
  const bridge = loadBridge({ [globalKey]: { core: { invoke: () => Promise.resolve('wrong-path') } } });
  ok('只有全局 Tauri 对象:不算有桥', bridge.available() === false);
  asyncChecks.push(bridge.invoke('x').then(
    () => ok('只有全局 Tauri 对象:不走它', false, 'resolved'),
    (e) => ok('只有全局 Tauri 对象:不走它', e && e.message === BRIDGE_DOWN, String(e && e.message))
  ));
}

// 去掉注释后的代码文本(整行 // 注释与 /* */ 块)
function codeOnly(src) {
  return src.replace(/\/\*[\s\S]*?\*\//g, '').split('\n').filter((l) => !/^\s*\/\//.test(l)).join('\n');
}
const webJs = fs.readdirSync(webDir).filter((f) => f.endsWith('.js'));
for (const f of webJs) {
  const code = codeOnly(fs.readFileSync(path.join(webDir, f), 'utf8'));
  ok(`${f} 不探全局 Tauri 对象(打包版不存在,只认 __TAURI_INTERNALS__)`, code.indexOf(['__TAURI', '__'].join('')) < 0);
}
for (const [, js] of PAGES) {
  const src = fs.readFileSync(path.join(webDir, js), 'utf8');
  ok(`${js} 调壳命令走 shell_bridge.js`, /const invoke = window\.HorosaShellBridge\.invoke;/.test(src) && !/function invoke\(/.test(src));
}

// ── 页面用到的元素都在自己的 html 里 ──
// 三页的元素全是 html 里写死的,脚本放在 </body> 前,运行期只改叶子容器的内容:取到的元素不会是空的,用的地方不判空。
for (const [html, js] of PAGES) {
  const h = fs.readFileSync(path.join(webDir, html), 'utf8');
  const src = fs.readFileSync(path.join(webDir, js), 'utf8');
  const code = codeOnly(src);
  const ids = new Set();
  for (const re of [/getElementById\('([A-Za-z0-9_-]+)'\)/g, /\bbind\('([A-Za-z0-9_-]+)'/g, /\bset\('([A-Za-z0-9_-]+)'/g]) {
    let m;
    while ((m = re.exec(code))) ids.add(m[1]);
  }
  const missing = [...ids].filter((id) => h.indexOf(`id="${id}"`) < 0);
  ok(`${js} 用到的 ${ids.size} 个元素 id 都在 ${html} 里`, ids.size > 0 && missing.length === 0, missing.join(', '));
  const bound = new Set();
  const bre = /\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*document\.getElementById\(/g;
  let bm;
  while ((bm = bre.exec(code))) bound.add(bm[1]);
  const guarded = [...bound].filter((n) => new RegExp(`if \\(!?${n}\\)|if \\(!${n} \\|\\||\\|\\| !${n}\\)|\\b${n}\\?\\.`).test(code));
  ok(`${js} 不对 html 里写死的元素判空`, guarded.length === 0, guarded.join(', '));
}
ok('启动器 bindAction 不判空按钮', /function bindAction\(button, handler\) \{\n\s*button\.addEventListener/.test(app));
ok('设置页 bind 不判空按钮', /function bind\(id, fn\) \{\n\s*document\.getElementById\(id\)\.addEventListener/.test(settings));
ok('诊断页读数 set 不判空', /var set = function \(id, txt\) \{\n\s*document\.getElementById\(id\)\.textContent = txt;/.test(diag));
ok('诊断页读缩放不包 try(读 style.zoom 与 parseFloat 不会抛)', !/try \{ var z = parseFloat/.test(diag) && /var z = parseFloat\(d\.style\.zoom\);/.test(diag));
ok('启动器进度条外框直接取 #progressFill 的父元素', /const progressTrack = progressFill\.parentElement;/.test(app));

Promise.all(asyncChecks).then(() => {
  let bad = 0;
  for (const [note, pass, detail] of V) {
    if (!pass) bad += 1;
    console.log(`${pass ? '✅' : '❌'} ${note}${pass ? '' : ' → ' + detail}`);
  }
  console.log(`== 壳自带页面:${V.length - bad}/${V.length} 通过 ==`);
  process.exit(bad ? 1 : 0);
});
