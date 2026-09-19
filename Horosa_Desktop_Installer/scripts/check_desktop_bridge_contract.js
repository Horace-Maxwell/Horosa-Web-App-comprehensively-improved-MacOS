#!/usr/bin/env node
/**
 * 桌面桥合同三向对拍(2026-09-08 进阶复查;D9 家族「壳返回数组、页面按对象读」的机械网):
 *   Rust `#[tauri::command]` 返回类型形态 ↔ 页面 aiAnalysisDesktop.js 的调用与消费形态 ↔ 桌面 mock(desktop_mock.js,存在才检)的命令表与返回形态。
 * 判据:
 *   ① 页面调用的每个壳命令必须在 main.rs 里有 #[tauri::command](拼错/删掉 = 页面永远 available:false);
 *   ② Rust 返回 Vec<…> 的命令,经 invokeOptional 包成 { value: [...] }:它的页面包装函数(desktop… )的每个消费点必须读 `.value`
 *      (D9 实抓:mcp_client_list_command 返回 Vec,页面 `{...r}` 展开成索引键 → 外部服务器清单在打包版永远空表);
 *   ③ 行动能力相关命令(mcp_ / agent_ / notify_hook_ / scheduler / set_agent / show_desktop_notification / copy_text)必须在桌面 mock 里登记,
 *      且 Vec 命令的 mock 返回必须是数组(mock 与真壳同形,才能复现 D9 这类形态病)。
 * 用法: node check_desktop_bridge_contract.js <仓库根> [--self-test] [--json]
 *   退出码 0 = 合同齐;1 = 有违反(或自证失败);2 = 环境不满足(缺 main.rs / aiAnalysisDesktop.js)。
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const repoRoot = process.argv[2];
const flags = new Set(process.argv.slice(3));
if (!repoRoot) { console.error('用法: node check_desktop_bridge_contract.js <仓库根> [--self-test] [--json]'); process.exit(2); }

// 文件类六命令(save_ai_/pick_ai_/open_ai_/open_external_)纳入 mock 登记与三形态对拍(此前导出/选文件/备份/外链链路零 mock 零合同)
const AGENT_CMD_RE = /^(mcp_|agent_|notify_hook_|set_agent_|set_scheduler_|scheduler_status|show_desktop_notification|copy_text_to_clipboard|auto_export_|save_ai_|pick_ai_|open_ai_|open_external_)/;

// ── Rust:#[tauri::command] fn 名 → 返回形态 ──
function rustCommands(src) {
  const out = new Map();
  const re = /#\[tauri::command\][^\n]*\n(?:\s*#\[[^\n]*\]\s*\n)*\s*(?:pub\s+)?(?:async\s+)?fn\s+([a-z_0-9]+)\s*\(/g;
  let m;
  while ((m = re.exec(src))) {
    const name = m[1];
    // 从 fn 名起找第一个 `{`,取其间的 `-> 类型`
    const rest = src.slice(m.index + m[0].length);
    const brace = rest.indexOf('{');
    const head = brace >= 0 ? rest.slice(0, brace) : rest.slice(0, 400);
    const arrow = head.indexOf('->');
    let ret = arrow >= 0 ? head.slice(arrow + 2).trim() : '()';
    out.set(name, { ret, shape: shapeOfRust(ret) });
  }
  return out;
}
function shapeOfRust(ret) {
  let t = ret.replace(/\s+/g, '');
  // Result<T, E> / std::result::Result<T,E> → T
  const rm = /^(?:std::result::)?Result<(.*)>$/.exec(t);
  if (rm) { let depth = 0; let i = 0; for (; i < rm[1].length; i++) { const c = rm[1][i]; if (c === '<') depth++; else if (c === '>') depth--; else if (c === ',' && depth === 0) break; } t = rm[1].slice(0, i); }
  if (t === '()' || t === '') return 'unit';
  if (/^Vec</.test(t)) return 'array';
  if (/^Option<[A-Z][A-Za-z0-9_]*>$/.test(t)) return 'option';   // Option<结构体>:None=null / Some=对象,两形皆合法
  if (/^(bool|String|&str|usize|u8|u16|u32|u64|i8|i16|i32|i64|f32|f64)$/.test(t)) return 'scalar';
  if (/^Option<(bool|String|usize|u32|u64|i32|i64|f64)>$/.test(t)) return 'scalar';
  return 'object';
}

// ── 页面:invoke*('cmd' …) 调用表 + invokeOptional 包装函数名 ──
function jsCalls(src) {
  const calls = [];
  const re = /(invokeOptional|invokeDesktopCommand|invoke)\(\s*'([a-z_0-9:|]+)'/g;
  let m;
  while ((m = re.exec(src))) calls.push({ via: m[1], cmd: m[2] });
  // 包装函数:export async function NAME(...){ ... return invokeOptional('cmd' ... }
  const wrappers = new Map();
  const wre = /export\s+async\s+function\s+([A-Za-z0-9_]+)\s*\([^)]*\)\s*\{[\s\S]*?invokeOptional\(\s*'([a-z_0-9]+)'/g;
  while ((m = wre.exec(src))) { const body = m[0]; if (!/\n\s*export\s+async\s+function/.test(body.slice(20))) wrappers.set(m[1], m[2]); }
  return { calls, wrappers };
}

// ── 消费点:包装函数被调用处是否读 .value(同一语句或后续 3 行内) ──
function consumersReadValue(files, wrapperName) {
  const bad = [];
  for (const [file, code] of files) {
    if (/aiAnalysisDesktop\.js$/.test(file) || /__tests__\//.test(file) || /\.test\.js$/.test(file)) continue;
    const lines = code.split('\n');
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].indexOf(wrapperName + '(') < 0) continue;
      if (/^\s*(\/\/|\*)/.test(lines[i]) || /^\s*import\b/.test(lines[i])) continue;
      const window = lines.slice(i, i + 4).join('\n');
      if (!/\.value\b(?!s)/.test(window)) bad.push(`${file}:${i + 1}`);   // `.value` 才算读包装(Object.values / .values 不算)
    }
  }
  return bad;
}

// ── mock:在 Node vm 里装上 desktop_mock.js,取命令表并逐条试调 ──
function loadMock(code) {
  const win = { __desktopMockInit: {} };
  win.window = win;
  const ctx = vm.createContext({ window: win, Date, JSON, Object, Array, String, Error, Number, Math, console });
  vm.runInContext(code, ctx);
  const internals = win.__TAURI_INTERNALS__;
  if (!internals || typeof internals.invoke !== 'function') return null;
  return { invoke: internals.invoke, mock: win.__desktopMock };
}

function analyze({ rustSrc, desktopSrc, files, mockSrc }) {
  const problems = [];
  const rust = rustCommands(rustSrc);
  const { calls, wrappers } = jsCalls(desktopSrc);
  const extra = [];
  for (const [file, code] of files) {
    if (/aiAnalysisDesktop\.js$/.test(file) || /__tests__\//.test(file) || /\.test\.js$/.test(file)) continue;
    const re = /invokeDesktopCommand\(\s*'([a-z_0-9:|]+)'/g; let m;
    while ((m = re.exec(code))) extra.push({ via: 'invokeDesktopCommand', cmd: m[1], file });
  }
  const all = calls.concat(extra);
  // ①
  for (const c of all) {
    if (c.cmd.indexOf('plugin:') === 0) continue;
    if (!rust.has(c.cmd)) problems.push(`① 页面调用了壳里没有的命令 ${c.cmd}(${c.via}${c.file ? ' @' + c.file : ''})`);
  }
  // ②
  for (const [wrapper, cmd] of wrappers) {
    const r = rust.get(cmd);
    if (!r || r.shape !== 'array') continue;
    const bad = consumersReadValue(files, wrapper);
    for (const b of bad) problems.push(`② ${cmd} 返回 Vec(${r.ret}),包装 ${wrapper}() 的消费点未读 .value:${b}`);
  }
  // ③
  let mockInfo = null;
  if (mockSrc) {
    let loaded = null;
    try { loaded = loadMock(mockSrc); } catch (e) { problems.push(`③ 桌面 mock 无法装载:${e.message}`); }
    if (loaded) {
      const registered = new Set();
      const arrayOk = [];
      for (const c of calls) {
        if (!AGENT_CMD_RE.test(c.cmd)) continue;
        let res; let unknown = false;
        try { res = loaded.invoke(c.cmd, sampleArgs(c.cmd)); } catch (e) { unknown = /unknown command/.test(`${e && e.message}`); }
        if (res && typeof res.then === 'function') {
          // invoke 返回 promise:同步取不到 → 用 mock 的 unknown 表判断
        }
        const known = loaded.mock && Array.isArray(loaded.mock.unknown) ? !loaded.mock.unknown.some((u) => u === c.cmd || (u && u.cmd === c.cmd)) : !unknown;
        if (!known) { problems.push(`③ 桌面 mock 未登记行动能力命令 ${c.cmd}(桌面用例会拿到 mock: unknown command)`); continue; }
        registered.add(c.cmd);
      }
      mockInfo = { registered: Array.from(registered).sort(), arrayOk };
    }
  }
  return { problems, rust, calls: all, wrappers: Array.from(wrappers), mockInfo };
}
function sampleArgs(cmd) {
  if (/upsert/.test(cmd)) return { spec: { id: 'probe', name: 'p', transport: { kind: 'http', url: 'http://127.0.0.1:1/mcp' } } };
  if (/set_enabled|set_agent|set_scheduler/.test(cmd)) return { enabled: false };
  if (/notify_hook_set/.test(cmd)) return { enabled: false, path: '' };
  if (/notify_hook_run/.test(cmd)) return { payload: {}, test: true };
  if (/agent_notify/.test(cmd)) return { kind: 'tools' };
  if (/set_limits/.test(cmd)) return { callsPerMinute: 60 };
  if (/auto_export_write/.test(cmd)) return { fileName: 'probe.txt', base64Data: 'eA==' };
  if (/save_ai_analysis_file/.test(cmd)) return { payload: { defaultFileName: 'probe.txt', base64Data: 'eA==', mimeType: 'text/plain' } };
  if (/open_external_url/.test(cmd)) return { url: 'https://example.com/' };
  if (/agent_tool_result/.test(cmd)) return { id: 1, ok: true };
  if (/agent_bridge_ready/.test(cmd)) return { version: 1, ready: true };
  if (/show_desktop_notification/.test(cmd)) return { title: 't', body: 'b' };
  if (/copy_text/.test(cmd)) return { text: 'x' };
  if (/mcp_client_(remove|connect|disconnect)/.test(cmd)) return { id: 'probe' };
  if (/mcp_client_call/.test(cmd)) return { id: 'probe', tool: 't', arguments: {} };
  return {};
}

async function checkMockArrays(mockSrc, rust, calls) {
  // [D84] 三形态对拍:真壳 Vec ⇒ mock 必回数组;scalar(bool/数字/字符串)⇒ mock 必回同类原始值;unit(())⇒ mock 必回 null/undefined;
  // object ⇒ mock 必回对象(非数组)。此前只对 Vec 对拍,bool/() 命令的 mock 回对象也放行(与真壳不同形的病复现不了)。
  const problems = [];
  let loaded = null;
  try { loaded = loadMock(mockSrc); } catch (e) { return problems; }
  if (!loaded) return problems;
  for (const c of calls) {
    const r = rust.get(c.cmd);
    if (!r || !AGENT_CMD_RE.test(c.cmd)) continue;
    let v;
    try { v = await loaded.invoke(c.cmd, sampleArgs(c.cmd)); } catch (e) { continue; }
    const kind = Array.isArray(v) ? 'array' : (v === null || v === undefined ? 'unit' : (typeof v === 'object' ? 'object' : 'scalar'));
    if (r.shape === 'array' && kind !== 'array') problems.push(`③ ${c.cmd} 真壳返回 Vec,桌面 mock 却回 ${kind}(与真壳不同形,D9 这类病复现不了)`);
    else if (r.shape === 'scalar' && kind !== 'scalar') problems.push(`③ ${c.cmd} 真壳返回标量(${r.ret}),桌面 mock 却回 ${kind}`);
    else if (r.shape === 'unit' && kind !== 'unit') problems.push(`③ ${c.cmd} 真壳返回 (),桌面 mock 却回 ${kind}`);
    else if (r.shape === 'object' && kind !== 'object') problems.push(`③ ${c.cmd} 真壳返回对象,桌面 mock 却回 ${kind}`);
    else if (r.shape === 'option' && kind !== 'object' && kind !== 'unit') problems.push(`③ ${c.cmd} 真壳返回 Option<结构体>,桌面 mock 却回 ${kind}`);
  }
  return problems;
}

function loadRepo() {
  const rustPath = path.join(repoRoot, 'Horosa_Desktop_Installer', 'src-tauri', 'src', 'main.rs');
  const uiSrc = path.join(repoRoot, 'Horosa-Web', 'astrostudyui', 'src');
  const desktopPath = path.join(uiSrc, 'utils', 'aiAnalysisDesktop.js');
  const mockPath = path.join(repoRoot, 'Horosa_Desktop_Installer', 'scripts', 'l5', 'desktop_mock.js');
  if (!fs.existsSync(rustPath) || !fs.existsSync(desktopPath)) { console.error('缺 main.rs 或 aiAnalysisDesktop.js'); process.exit(2); }
  const files = new Map();
  (function walk(dir) {
    for (const name of fs.readdirSync(dir)) {
      if (name === 'node_modules' || name.startsWith('.')) continue;
      const p = path.join(dir, name); const st = fs.statSync(p);
      if (st.isDirectory()) walk(p); else if (/\.jsx?$/.test(name)) files.set(path.relative(uiSrc, p).split(path.sep).join('/'), fs.readFileSync(p, 'utf8'));
    }
  })(uiSrc);
  return { rustSrc: fs.readFileSync(rustPath, 'utf8'), desktopSrc: fs.readFileSync(desktopPath, 'utf8'), files, mockSrc: fs.existsSync(mockPath) ? fs.readFileSync(mockPath, 'utf8') : null };
}

async function selfTest() {
  const V = [];
  const rustOk = "#[tauri::command]\nfn mcp_client_list_command(app: AppHandle) -> Result<Vec<Value>, String> {\n}\n#[tauri::command]\nfn set_agent_enabled_command(enabled: bool) -> Result<Value, String> {\n}\n#[tauri::command]\nfn copy_text_to_clipboard_command(text: String) {\n}\n";
  const desktopOk = "export async function desktopMcpClientList(){\n\treturn invokeOptional('mcp_client_list_command');\n}\nexport async function desktopSetAgentEnabled(enabled){\n\treturn invokeOptional('set_agent_enabled_command', { enabled: !!enabled });\n}\nexport async function copy(t){ return invoke('copy_text_to_clipboard_command', { text: t }); }\n";
  const filesOk = new Map([['components/x.js', "import { desktopMcpClientList } from '../utils/aiAnalysisDesktop';\nasync function load(){ const r = await desktopMcpClientList(); setRows(Array.isArray(r.value) ? r.value : []); }\n"]]);
  const mockOk = "(function(){ const T = { mcp_client_list_command: ()=>[], set_agent_enabled_command: (a)=>({ ok: true }), copy_text_to_clipboard_command: ()=>null }; const unknown = []; window.__desktopMock = { unknown }; window.__TAURI_INTERNALS__ = { invoke: (cmd, args)=>{ if(!T[cmd]){ unknown.push(cmd); return Promise.reject(new Error('mock: unknown command ' + cmd)); } return Promise.resolve(T[cmd](args)); } }; })();";
  const g = analyze({ rustSrc: rustOk, desktopSrc: desktopOk, files: filesOk, mockSrc: mockOk });
  V.push(['三向一致 → 零问题', g.problems.length === 0, g.problems]);
  const g1 = analyze({ rustSrc: rustOk, desktopSrc: desktopOk, files: new Map([['components/x.js', "import { desktopMcpClientList } from '../utils/aiAnalysisDesktop';\nasync function load(){ const r = await desktopMcpClientList(); setRows(Object.values({ ...r })); }\n"]]), mockSrc: mockOk });
  V.push(['② Vec 命令消费点不读 .value → 红(D9 形态)', g1.problems.some((x) => x.indexOf('② mcp_client_list_command') === 0), g1.problems]);
  const g2 = analyze({ rustSrc: rustOk, desktopSrc: desktopOk + "export async function nope(){ return invokeOptional('mcp_client_nope_command'); }\n", files: filesOk, mockSrc: mockOk });
  V.push(['① 页面调用壳没有的命令 → 红', g2.problems.some((x) => x.indexOf('① 页面调用了壳里没有的命令 mcp_client_nope_command') === 0), g2.problems]);
  const g3 = analyze({ rustSrc: rustOk, desktopSrc: desktopOk, files: filesOk, mockSrc: mockOk.replace('set_agent_enabled_command: (a)=>({ ok: true }), ', '') });
  V.push(['③ mock 缺行动能力命令 → 红', g3.problems.some((x) => x.indexOf('③ 桌面 mock 未登记行动能力命令 set_agent_enabled_command') === 0), g3.problems]);
  // [D84] 三形态对拍:() 命令的 mock 回对象 → 红;对象命令的 mock 回标量 → 红;同形 → 零问题
  const shapeOk = await checkMockArrays(mockOk, g.rust, g.calls);
  V.push(['③ 三形态同形 → 零问题', shapeOk.length === 0, shapeOk]);
  const shapeBad1 = await checkMockArrays(mockOk.replace('copy_text_to_clipboard_command: ()=>null', 'copy_text_to_clipboard_command: ()=>({ ok: true })'), g.rust, g.calls);
  V.push(['③ () 命令 mock 回对象 → 红', shapeBad1.some((x) => x.indexOf('③ copy_text_to_clipboard_command 真壳返回 ()') === 0), shapeBad1]);
  const shapeBad2 = await checkMockArrays(mockOk.replace('set_agent_enabled_command: (a)=>({ ok: true })', 'set_agent_enabled_command: (a)=>true'), g.rust, g.calls);
  V.push(['③ 对象命令 mock 回标量 → 红', shapeBad2.some((x) => x.indexOf('③ set_agent_enabled_command 真壳返回对象') === 0), shapeBad2]);
  let bad = 0;
  for (const [note, ok, detail] of V) { if (!ok) bad += 1; console.log(`${ok ? '✅' : '❌'} ${note}${ok ? '' : ' → ' + JSON.stringify(detail)}`); }
  console.log(`== 桌面桥合同检查器判别向量:${V.length - bad}/${V.length} 按预期 ==`);
  return bad ? 1 : 0;
}

(async () => {
  if (flags.has('--self-test')) { process.exit(await selfTest()); }
  const repo = loadRepo();
  const g = analyze(repo);
  const extra = repo.mockSrc ? await checkMockArrays(repo.mockSrc, g.rust, g.calls) : [];
  const problems = g.problems.concat(extra);
  if (flags.has('--json')) console.log(JSON.stringify({ problems, commands: g.calls.length, wrappers: g.wrappers.length, rust: g.rust.size, mock: g.mockInfo }, null, 1));
  if (problems.length) { console.log(`❌ 桌面桥合同 ${problems.length} 处违反:\n  ${problems.join('\n  ')}`); process.exit(1); }
  console.log(`✅ 桌面桥合同齐:页面调用 ${g.calls.length} 处 / 壳命令 ${g.rust.size} 条 / Vec 包装消费点全读 .value${repo.mockSrc ? ` / 桌面 mock 登记行动能力命令 ${g.mockInfo ? g.mockInfo.registered.length : 0} 条且 Vec 同形` : '(无桌面 mock,跳过 ③)'}`);
  process.exit(0);
})();
