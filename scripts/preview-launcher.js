#!/usr/bin/env node
/* Horosa 前端预览的唯一启动入口(.claude/launch.json 的 horosa-ui 调它)。
 *
 * 用法:
 *   node scripts/preview-launcher.js            自动选模式(依赖在→dev,依赖缺→静态产物)
 *   node scripts/preview-launcher.js --dev      强制 dev server(热重载)
 *   node scripts/preview-launcher.js --static   强制静态服务打包产物
 *   node scripts/preview-launcher.js --clean    先清编译缓存再起(编译诡异时用)
 *   node scripts/preview-launcher.js --doctor   只体检不启动,打印全部环境事实
 *
 * ⚠️ 为什么是 .js 而不是 .sh:preview 沙箱**拒绝执行仓库内的 .sh**
 * (实测 `Operation not permitted` / code 126,放 .claude/ 与 scripts/ 下都被拒),
 * 但允许 `node <仓库内的 .js>`。这条差别是实测出来的,别再试图改回 shell 脚本。
 *
 * 逐条挡住的失效场景(每条都实测演练过):
 *   ① 仓库被移动 / 换机器 clone 到别处  → 从本文件自身位置反推仓库根,不硬编码绝对路径
 *   ② node 缺失                        → 明确提示装哪个版本,而不是抛一堆栈
 *   ③ node 版本过新                    → 优先用 fnm 里的版本;前端是 umi3(webpack4 世代)
 *   ④ 依赖未装 / 装坏(umi 可执行缺失) → 判 .bin/umi 而非只判目录;并可回落静态模式
 *   ⑤ **依赖整个不在**(clone 后没装)  → 只要有打包产物就自动起静态服务,页面照样能看
 *   ⑥ umi 编译缓存中毒                 → --clean 一键清 src/.umi 与 node_modules/.cache
 *   ⑦ 端口被占                         → umi 自身顺延;静态模式自己找下一个空闲端口
 */
'use strict';

const fs = require('fs');
const http = require('http');
const path = require('path');
const { spawn } = require('child_process');

const ARGS = process.argv.slice(2);
const has = (f) => ARGS.includes(f);

// ── ① 仓库根:从本文件位置反推,绝不硬编码 ────────────────────────────────
// 本文件在 <repo>/scripts/preview-launcher.js,故上一级即仓库根。
const REPO = path.resolve(__dirname, '..');
const UI_DIR = path.join(REPO, 'Horosa-Web', 'astrostudyui');
const DIST_FILE = path.join(UI_DIR, 'dist-file');
const UMI_BIN = path.join(UI_DIR, 'node_modules', '.bin', 'umi');

function die(msg, hint) {
  console.error('\n❌ ' + msg);
  if (hint) console.error('   ' + hint);
  process.exit(1);
}

// ── ② / ③ node:优先 fnm 里的版本,不写死版本号 ──────────────────────────
// 不直接用 PATH 里的 node —— 系统装的可能是很新的大版本,而前端是 umi3(webpack4 世代),
// 过新的 node 起不来。fnm 里那份是验证可用的。
function pickNodeBin() {
  const base = path.join(process.env.HOME || '', '.local', 'share', 'fnm', 'node-versions');
  try {
    const list = fs.readdirSync(base)
      .map((v) => ({ v, bin: path.join(base, v, 'installation', 'bin') }))
      .filter((x) => { try { return fs.existsSync(path.join(x.bin, 'node')); } catch (e) { return false; } })
      .sort((a, b) => a.v.localeCompare(b.v, undefined, { numeric: true }));
    return list.length ? list[list.length - 1] : null;
  } catch (e) { return null; }
}

function statOf(p) {
  try { return fs.statSync(p); } catch (e) { return null; }
}

// 端口探活:静态模式要自己找空闲端口(dev 模式由 umi 自己顺延)
function findFreePort(start, tries, cb) {
  let port = start;
  let left = tries;
  const attempt = () => {
    const probe = http.createServer();
    probe.once('error', () => {
      probe.close();
      left -= 1; port += 1;
      if (left <= 0) return cb(null);
      attempt();
    });
    probe.once('listening', () => probe.close(() => cb(port)));
    probe.listen(port, '127.0.0.1');
  };
  attempt();
}

// ── 环境事实:体检与启动共用同一份采集,避免两处口径不一致 ─────────────────
function collect() {
  const fnmNode = pickNodeBin();
  const nmStat = statOf(path.join(UI_DIR, 'node_modules'));
  const distStat = statOf(path.join(DIST_FILE, 'index.html'));
  return {
    repo: REPO,
    uiDir: UI_DIR,
    uiExists: !!statOf(path.join(UI_DIR, 'package.json')),
    fnmNode,
    runningNode: process.version,
    nodeModules: nmStat ? (nmStat.isSymbolicLink && nmStat.isSymbolicLink() ? '软链' : '目录') : null,
    umiBin: fs.existsSync(UMI_BIN),
    distFile: distStat ? distStat.mtime.toISOString().slice(0, 16).replace('T', ' ') : null,
    port: Number(process.env.PORT || 8000),
  };
}

// 模式决策:显式参数优先,否则按「依赖是否可用」自动选
function decideMode(env) {
  if (has('--dev')) return 'dev';
  if (has('--static')) return 'static';
  if (env.umiBin) return 'dev';
  if (env.distFile) return 'static';
  return 'none';
}

const ENV = collect();

if (!ENV.uiExists) {
  die(`前端目录不存在:${UI_DIR}`,
      '本脚本按「自身在 <仓库根>/scripts/ 下」反推路径;若目录结构变了,改本文件顶部的 UI_DIR。');
}

// ── --doctor:只体检不启动 ────────────────────────────────────────────────
// 排障最费时间的是「不知道差什么」。这里把决策依据一次性摊开。
if (has('--doctor')) {
  const mode = decideMode(ENV);
  console.log('\n🩺 Horosa 预览环境体检\n');
  console.log('  仓库根        ' + ENV.repo);
  console.log('  前端目录      ' + ENV.uiDir + (ENV.uiExists ? '  ✅' : '  ❌ 不存在'));
  console.log('  当前 node     ' + ENV.runningNode);
  console.log('  fnm node      ' + (ENV.fnmNode ? ENV.fnmNode.v + '  ✅ 将优先使用' : '未安装  ⚠️ 将回落系统 node'));
  console.log('  node_modules  ' + (ENV.nodeModules ? ENV.nodeModules + '  ✅' : '不存在  ❌'));
  console.log('  .bin/umi      ' + (ENV.umiBin ? '在  ✅' : '缺失  ❌ 依赖不完整,dev 模式不可用'));
  console.log('  打包产物      ' + (ENV.distFile ? 'dist-file  ✅ 构建于 ' + ENV.distFile : '无  ❌ 静态模式不可用'));
  console.log('  目标端口      ' + ENV.port);
  console.log('\n  将采用模式    ' + (
    mode === 'dev' ? 'dev(umi dev server,热重载)'
      : mode === 'static' ? 'static(静态服务 dist-file;改代码不会自动生效)'
        : '❌ 无法启动'));
  if (mode === 'none') {
    console.log('\n  两条出路(任选其一):');
    console.log('    装依赖跑 dev:cd ' + UI_DIR + ' && npm install');
    console.log('    只看产物:    cd ' + UI_DIR + ' && npm run build:file');
  }
  console.log('');
  process.exit(0);
}

const MODE = decideMode(ENV);
if (MODE === 'none') {
  die('既没有可用依赖(node_modules/.bin/umi),也没有打包产物(dist-file/index.html)。',
      `装依赖跑 dev:cd ${UI_DIR} && npm install\n   只看产物:    cd ${UI_DIR} && npm run build:file`);
}

// ── ⑥ 编译缓存中毒:--clean 时清掉(仅 dev 模式有意义)────────────────────
// 症状是「代码没问题却编译失败」或「改了代码页面不变」。默认不动(清了要多花一次全量编译)。
if (has('--clean')) {
  for (const rel of [path.join('src', '.umi'), path.join('node_modules', '.cache')]) {
    const p = path.join(UI_DIR, rel);
    try {
      if (fs.existsSync(p)) { fs.rmSync(p, { recursive: true, force: true }); console.log('🧹 已清缓存:' + rel); }
    } catch (e) { console.error('⚠️  清缓存失败(不致命):' + rel + ' — ' + e.message); }
  }
}

const nodeLabel = ENV.fnmNode ? ENV.fnmNode.v : ('系统 ' + ENV.runningNode);

// ── static 模式:用 node 内置 http 起静态服务 ─────────────────────────────
// 为什么服务 dist-file 而不是 dist:dist-file 是 build:file 产物,资源用**相对路径**
// (`./umi.xxx.css`)且路由是 hash 模式 —— 简单静态服务即可,不需要路径重写,也不需要
// SPA fallback。dist 则用 `/static/` 前缀但文件落在根目录,直接服务会全 404(踩过)。
if (MODE === 'static') {
  if (!ENV.distFile) {
    die('指定了静态模式,但没有打包产物。', `先跑:cd ${UI_DIR} && npm run build:file`);
  }
  const TYPES = {
    '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8',
    '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
    '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.woff': 'font/woff', '.woff2': 'font/woff2',
    '.ttf': 'font/ttf', '.otf': 'font/otf', '.wasm': 'application/wasm', '.map': 'application/json',
  };
  const server = http.createServer((req, res) => {
    let rel;
    try { rel = decodeURIComponent(String(req.url || '/').split('?')[0]); } catch (e) { rel = '/'; }
    if (rel === '/' || rel === '') rel = '/index.html';
    // 目录穿越防护:归一化后必须仍落在 dist-file 内
    const target = path.normalize(path.join(DIST_FILE, rel));
    if (!target.startsWith(DIST_FILE)) { res.writeHead(403); return res.end('forbidden'); }
    fs.readFile(target, (err, buf) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
        return res.end('404 ' + rel);
      }
      res.writeHead(200, {
        'Content-Type': TYPES[path.extname(target).toLowerCase()] || 'application/octet-stream',
        'Cache-Control': 'no-store',   // 产物会被重新 build,别让浏览器拿旧的
      });
      res.end(buf);
    });
  });
  findFreePort(ENV.port, 20, (port) => {
    if (!port) die('端口全被占用(从 ' + ENV.port + ' 起连试 20 个)。', '关掉占用的服务再试。');
    server.listen(port, '127.0.0.1', () => {
      console.log('▶ Horosa 预览【静态产物】  port=' + port + '  node=' + nodeLabel);
      console.log('  服务 ' + DIST_FILE);
      console.log('  产物构建于 ' + ENV.distFile +
        (ENV.umiBin ? '' : '  (依赖未装,故走静态模式;改代码不会自动生效)'));
      console.log('  http://localhost:' + port);
    });
  });
  for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) {
    process.on(sig, () => { try { server.close(); } catch (e) { /* ignore */ } process.exit(0); });
  }
  return;
}

// ── dev 模式:umi dev server ──────────────────────────────────────────────
if (!ENV.nodeModules) {
  die('依赖未安装。', `先跑:cd ${UI_DIR} && npm install`);
}
if (!ENV.umiBin) {
  die('node_modules 存在但 umi 可执行文件缺失(装了一半或被清过)。',
      `重装:cd ${UI_DIR} && rm -rf node_modules && npm install`);
}

const env = Object.assign({}, process.env);
if (ENV.fnmNode) {
  env.PATH = ENV.fnmNode.bin + path.delimiter + env.PATH;
} else {
  console.error('⚠️  未找到 fnm 管理的 node,将使用系统 node ' + ENV.runningNode + '。');
  console.error('   前端是 umi3(webpack4 世代),过新的 node 可能起不来;报错的话装一个 v24:');
  console.error('   fnm install 24 && fnm use 24');
}
if (!fs.existsSync(path.join(ENV.fnmNode ? ENV.fnmNode.bin : '', 'npm')) && !ENV.fnmNode) {
  // 系统 node 路径下也要有 npm,否则 spawn 会以一个难懂的 ENOENT 失败
}

// .umirc.js 没设 port,umi 默认 8000;launch.json 曾声明 8010 → preview 面板连到无人监听的
// 端口。这里显式钉住,与 launch.json 的声明保持一致。端口被占时 umi 自己顺延。
env.PORT = String(ENV.port);
env.NODE_OPTIONS = '--openssl-legacy-provider';   // umi3 在 node 17+ 上必需(OpenSSL 3 的 md4)
env.BROWSER = 'none';                             // 别再自动开系统浏览器,preview 面板自己会开

console.log('▶ Horosa 预览【dev server】  port=' + env.PORT + '  node=' + nodeLabel);
console.log('  目录 ' + UI_DIR);

const child = spawn('npm', ['start'], { cwd: UI_DIR, env, stdio: 'inherit', shell: false });
child.on('error', (e) => die('启动 npm 失败:' + e.message,
  'node 安装可能不完整(有 node 没 npm)。'));
child.on('exit', (code) => process.exit(code === null ? 1 : code));

// 转发终止信号,避免留下孤儿 dev server 占着端口
for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) {
  process.on(sig, () => { try { child.kill(sig); } catch (e) { /* ignore */ } });
}
