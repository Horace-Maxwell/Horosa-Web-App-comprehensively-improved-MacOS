#!/usr/bin/env node
// jest_heavy_reuse.js —— 全量 jest 里的「重套件」按依赖闭包内容复用上次的通过结果(发版基线 jest_full 用;日常全量 jest 也可用)。
//
// 为什么:全量 jest 一千五百多套里,择日三式 / 太乙压测与全谱齿轮差分闸这几族占了绝大部分机时,而一次改动多半碰不到它们读的代码。
//   改动没碰到某套的依赖闭包 → 它这次的结果与上次逐字相同,重跑只是烧机时。
//
// 判据(全部按内容,不看 git 历史:工作区有未提交改动、提交被合并成一条都照样成立):
//   每个重套件(登记表 Horosa-Web/astrostudyui/scripts/jest-heavy-suites.json 的 families[].tests)算一把「输入指纹」=
//     ① 依赖闭包:用 jest 自己的 haste map + 解析器(与真跑同一套 moduleNameMapper / 别名 / jest.mock 路径)从测试文件出发
//        沿 import / require / jest.mock / requireActual 递归,node_modules 之外每个文件的内容哈希;
//     ② 全局输入:登记表 globalInputs(依赖锁、jest 配置、测试垫片、本工具与登记表自身…)+ node_modules/.package-lock.json
//        + jest 生效配置(--showConfig,去掉机器相关的缓存目录)+ node 版本;
//     ③ 族外部输入:families[].externalInputs(差分闸在线时打本地后端 → 后端源码树),按 git 跟踪 + 未忽略的新文件逐个哈希;
//     ④ 环境:登记表 envKeys 列出的环境变量取值。
//   指纹与上次「通过」时记下的相同、且上次通过不早于 maxAgeDays 天 → 复用(本次不跑);否则跑。另外:
//     · 每族每次固定轮换跑 sample 片(复用面再大,每次也有真跑的样本;N 次跑遍全族);
//     · 闭包里的测试助手(__tests__ / test / src/test 下)出现读文件系统的调用 → 该族永不复用(读到的文件不在闭包里,指纹看不见);
//     · HOROSA_BASELINE_JEST_FULL=1 或 --full → 全跑;状态文件缺 / 坏 / 版本不对 → 全跑。
//   复用状态存在本机(缺省 Horosa_Desktop_Installer/build/release-baseline/jest-heavy-reuse.json,不入库);只有「这次真跑且通过」才记。
//
// 用法:
//   node jest_heavy_reuse.js run [--ui <astrostudyui>] [--state <文件>] [--full] [--summary-out <文件>] -- <交给 umi-test 的参数…>
//   node jest_heavy_reuse.js plan [--ui …] [--state …] [--full] [--json]      只看判定不跑
//   node jest_heavy_reuse.js check [--ui …]                                  登记表合同(预检用)
//   node jest_heavy_reuse.js --self-test                                     判据自证(合成输入;每条判据各一组反例)
'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync, spawnSync } = require('child_process');

const STATE_VERSION = 1;
const REPO_ROOT = path.resolve(__dirname, '..', '..');
const DEFAULT_UI = path.join(REPO_ROOT, 'Horosa-Web', 'astrostudyui');
const DEFAULT_STATE = path.join(REPO_ROOT, 'Horosa_Desktop_Installer', 'build', 'release-baseline', 'jest-heavy-reuse.json');
const REGISTRY_REL = 'scripts/jest-heavy-suites.json';
const FS_READ_RE = /\b(readFileSync|readFile|readdirSync|readdir|statSync|existsSync|createReadStream|openSync)\s*\(/;
const HELPER_DIR_RE = /(^|\/)(__tests__|test)\//;

// ───────────────────────── 纯判据(自证测这一层) ─────────────────────────
// 简单 glob:** 跨目录,* 不跨 /
function globRe(glob){
	const esc = glob.split('**').map((part)=>part.split('*').map((s)=>s.replace(/[.+?^${}()|[\]\\]/g, '\\$&')).join('[^/]*')).join('.*');
	return new RegExp(`^${esc}$`);
}
// 每族该轮换跑的片:按路径排序,第 rotation 轮取 [rot*sample, rot*sample+sample) 取模
function sampleOf(tests, sample, rotation){
	const sorted = tests.slice().sort();
	const n = sorted.length; const out = new Set();
	if(!n || sample <= 0){ return out; }
	for(let j = 0; j < Math.min(sample, n); j += 1){ out.add(sorted[((rotation || 0) * sample + j) % n]); }
	return out;
}
// 闭包里会读文件系统的测试助手(相对仓根):在 __tests__ / test 目录下、源码里有读文件调用、且不是全局输入
//   (全局输入任一字节变就全部重跑;astrostudyui/test 下的 jest 垫片只读 node_modules 里的库源码,由依赖锁覆盖)
function fsReadCulprits(relFiles, readSrc, globalRes){
	return relFiles.filter((rel)=>HELPER_DIR_RE.test(rel) && !globalRes.some((re)=>re.test(rel)) && FS_READ_RE.test(readSrc(rel) || '')).sort();
}
// decide({ families, keys, state, now, maxAgeDays, full, fsReadFamilies }) → { [test]: { run, reason } }
//   families:[{ id, tests:[相对路径], sample }];keys:{ test: 指纹 };fsReadFamilies:Set(族 id)
function decide({ families, keys, state, now, maxAgeDays, full, fsReadFamilies }){
	const out = {};
	const st = state && state.version === STATE_VERSION ? state : null;
	families.forEach((fam)=>{
		const sample = sampleOf(fam.tests, fam.sample || 0, st && st.rotation ? st.rotation[fam.id] : 0);
		fam.tests.forEach((t)=>{
			const rec = st && st.suites ? st.suites[t] : null;
			let reason = null;
			if(full){ reason = '全跑(--full / HOROSA_BASELINE_JEST_FULL=1)'; }
			else if(!st){ reason = '没有复用状态(首跑 / 状态文件缺坏 / 版本变了)'; }
			else if(fsReadFamilies && fsReadFamilies.has(fam.id)){ reason = '闭包里的测试助手读文件系统(指纹看不见读到的文件),本族不复用'; }
			else if(!rec){ reason = '没有通过记录'; }
			else if(rec.key !== keys[t]){ reason = '输入指纹变了(闭包 / 全局输入 / 后端源码 / 环境之一)'; }
			else if(!(now - Date.parse(rec.passedAt) <= maxAgeDays * 86400000)){ reason = `上次通过早于 ${maxAgeDays} 天`; }
			else if(sample.has(t)){ reason = '本轮轮换抽样'; }
			out[t] = reason ? { run: true, reason } : { run: false, reason: `指纹未变,复用 ${rec.passedAt}${rec.head ? ` @ ${rec.head}` : ''} 的通过结果` };
		});
	});
	return out;
}
// record(state, { plan, passed:Set(相对路径), ran:Set, now, head }) → 新状态(只记真跑且通过的;跑了没过的删记录;轮换前进一格)
function record(state, { plan, passed, ran, now, head }){
	const st = state && state.version === STATE_VERSION ? JSON.parse(JSON.stringify(state)) : { version: STATE_VERSION, suites: {}, rotation: {} };
	st.suites = st.suites || {}; st.rotation = st.rotation || {};
	Object.keys(plan.decisions).forEach((t)=>{
		if(!plan.decisions[t].run || !ran.has(t)){ return; }
		if(passed.has(t)){ st.suites[t] = { key: plan.keys[t], passedAt: new Date(now).toISOString(), head: head || '' }; }
		else{ delete st.suites[t]; }
	});
	plan.families.forEach((fam)=>{ if(fam.tests.some((t)=>ran.has(t))){ st.rotation[fam.id] = (st.rotation[fam.id] || 0) + 1; } });
	st.updatedAt = new Date(now).toISOString();
	return st;
}

// ───────────────────────── 取输入(真文件系统 / jest 内部) ─────────────────────────
const sha = (buf)=>crypto.createHash('sha256').update(buf).digest('hex');
const fileCache = new Map();
function fileDigest(abs){
	if(fileCache.has(abs)){ return fileCache.get(abs); }
	let d;
	try{ d = sha(fs.readFileSync(abs)); }catch(_e){ d = 'missing'; }
	fileCache.set(abs, d); return d;
}
function digestOf(absFiles, base){
	const h = crypto.createHash('sha256');
	[...new Set(absFiles)].sort().forEach((f)=>{ h.update(`${path.relative(base, f)}\0${fileDigest(f)}\n`); });
	return h.digest('hex');
}
function gitFiles(globs){
	if(!globs || !globs.length){ return []; }
	const tops = [...new Set(globs.map((g)=>g.split('*')[0].replace(/\/[^/]*$/, '') || '.'))];
	const list = execFileSync('git', ['-C', REPO_ROOT, 'ls-files', '-z', '--cached', '--others', '--exclude-standard', '--', ...tops], { encoding: 'utf8', maxBuffer: 256 * 1024 * 1024 }).split('\0').filter(Boolean);
	const res = globs.map(globRe);
	return list.filter((f)=>res.some((re)=>re.test(f))).map((f)=>path.join(REPO_ROOT, f)).filter((f)=>fs.existsSync(f));
}
function umiTestBin(ui){ return path.join(ui, 'node_modules', '.bin', 'umi-test'); }
function showConfig(ui){
	const out = execFileSync(umiTestBin(ui), ['--showConfig'], { cwd: ui, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, stdio: ['ignore', 'pipe', 'ignore'] });
	return JSON.parse(out.slice(out.indexOf('{')));
}
async function jestClosures(ui, cfg, tests){
	const req = (m)=>require(require.resolve(m, { paths: [ui] }));
	const rt = req('jest-runtime'); const Runtime = rt.default || rt;
	const drm = req('jest-resolve-dependencies'); const DependencyResolver = drm.DependencyResolver || drm.default || drm;
	const { buildSnapshotResolver } = req('jest-snapshot');
	const ctx = await Runtime.createContext(cfg, { maxWorkers: 2, watchman: false });
	const dr = new DependencyResolver(ctx.resolver, ctx.hasteFS, buildSnapshotResolver(cfg));
	const memo = new Map();
	const depsOf = (f)=>{ if(!memo.has(f)){ let d = []; try{ d = dr.resolve(f, {}); }catch(_e){ d = []; } memo.set(f, d.filter((x)=>!x.includes(`${path.sep}node_modules${path.sep}`))); } return memo.get(f); };
	const out = {};
	tests.forEach((rel)=>{
		const seen = new Set(); const stack = [path.join(ui, rel)];
		while(stack.length){ const f = stack.pop(); if(seen.has(f)){ continue; } seen.add(f); depsOf(f).forEach((d)=>{ if(!seen.has(d)){ stack.push(d); } }); }
		out[rel] = [...seen];
	});
	return out;
}

async function plan({ ui, statePath, full }){
	const reg = JSON.parse(fs.readFileSync(path.join(ui, REGISTRY_REL), 'utf8'));
	const cfgAll = showConfig(ui);
	const cfg = cfgAll.configs[0];
	const allTests = execFileSync('git', ['-C', ui, 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }).split('\0').filter(Boolean);
	const families = reg.families.map((f)=>{ const re = globRe(f.tests); return { id: f.id, sample: f.sample || 0, externalInputs: f.externalInputs || [], tests: allTests.filter((t)=>re.test(t)).sort() }; });
	const empty = families.filter((f)=>!f.tests.length).map((f)=>f.id);
	if(empty.length){ throw new Error(`登记表里的族没匹配到任何测试文件:${empty.join(', ')}(改了文件名就同步改 ${REGISTRY_REL})`); }
	const heavy = families.flatMap((f)=>f.tests);
	const closures = await jestClosures(ui, cfg, heavy);
	const cfgForKey = JSON.parse(JSON.stringify(cfg)); delete cfgForKey.cacheDirectory;
	const globalFiles = gitFiles(reg.globalInputs || []);
	const lockFile = path.join(ui, 'node_modules', '.package-lock.json');
	if(fs.existsSync(lockFile)){ globalFiles.push(lockFile); }
	const globalKey = sha(JSON.stringify({ files: digestOf(globalFiles, REPO_ROOT), cfg: cfgForKey, node: process.version, env: (reg.envKeys || []).map((k)=>[k, process.env[k] === undefined ? null : process.env[k]]) }));
	const famExt = {}; families.forEach((f)=>{ famExt[f.id] = digestOf(gitFiles(f.externalInputs), REPO_ROOT); });
	const fsReadFamilies = new Set();
	const fsReadWhy = {};
	const globalRes = (reg.globalInputs || []).map(globRe);
	const readSrc = (abs)=>{ try{ return fs.readFileSync(abs, 'utf8'); }catch(_e){ return ''; } };
	families.forEach((f)=>{
		const culprits = fsReadCulprits([...new Set(f.tests.flatMap((t)=>closures[t]))].map((abs)=>path.relative(REPO_ROOT, abs)), (rel)=>readSrc(path.join(REPO_ROOT, rel)), globalRes);
		if(culprits.length){ fsReadFamilies.add(f.id); fsReadWhy[f.id] = culprits[0]; }
	});
	const keys = {};
	families.forEach((f)=>f.tests.forEach((t)=>{ keys[t] = sha(`${globalKey}\n${famExt[f.id]}\n${digestOf(closures[t], ui)}`); }));
	let state = null;
	try{ state = JSON.parse(fs.readFileSync(statePath, 'utf8')); }catch(_e){ state = null; }
	const decisions = decide({ families, keys, state, now: Date.now(), maxAgeDays: reg.maxAgeDays || 7, full, fsReadFamilies });
	return { ui, statePath, families, keys, decisions, fsReadWhy, ignoreDefaults: cfg.testPathIgnorePatterns || [], closureSizes: Object.fromEntries(heavy.map((t)=>[t, closures[t].length])) };
}

function summarize(p){
	const run = Object.values(p.decisions).filter((d)=>d.run).length;
	const total = Object.keys(p.decisions).length;
	const famLine = p.families.map((f)=>{ const r = f.tests.filter((t)=>p.decisions[t].run).length; return `${f.id} 跑 ${r}/${f.tests.length}`; }).join(' · ');
	return `重套件 ${total}:跑 ${run} · 复用 ${total - run}(${famLine})`;
}
function printPlan(p){
	console.log(`== 重套件复用判定(${summarize(p)})`);
	p.families.forEach((f)=>{
		f.tests.forEach((t)=>{ const d = p.decisions[t]; console.log(`  ${d.run ? '跑  ' : '复用'} ${t}  [闭包 ${p.closureSizes[t]} 件] ${d.reason}`); });
		if(p.fsReadWhy[f.id]){ console.log(`  ⚠️ ${f.id}:闭包里 ${p.fsReadWhy[f.id]} 读文件系统 → 本族不复用`); }
	});
}
const escRe = (s)=>s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
function headShort(){ try{ return execFileSync('git', ['-C', REPO_ROOT, 'rev-parse', '--short=9', 'HEAD'], { encoding: 'utf8' }).trim(); }catch(_e){ return ''; } }

async function cmdRun(opts, jestArgs){
	const p = await plan(opts);
	printPlan(p);
	const skip = Object.keys(p.decisions).filter((t)=>!p.decisions[t].run);
	const jsonOut = path.join(path.dirname(opts.statePath), `jest-heavy-reuse.results.${process.pid}.json`);
	fs.mkdirSync(path.dirname(opts.statePath), { recursive: true });
	const ignore = [...p.ignoreDefaults, ...skip.map((t)=>`^${escRe(path.join(p.ui, t))}$`)];
	// umi-test 用自己的参数解析器(yParser):数组参数只认重复的 --x=值;空格分隔会把第二个值当位置参数、jest 内 .map 报错
	const args = [...jestArgs, '--json', `--outputFile=${jsonOut}`, ...ignore.map((x)=>`--testPathIgnorePatterns=${x}`)];
	const r = spawnSync(umiTestBin(p.ui), args, { cwd: p.ui, stdio: 'inherit' });
	const rc = r.status === null ? 1 : r.status;
	let results = null;
	try{ results = JSON.parse(fs.readFileSync(jsonOut, 'utf8')); }catch(_e){ results = null; }
	try{ fs.unlinkSync(jsonOut); }catch(_e){ /* 没生成 */ }
	if(results && Array.isArray(results.testResults)){
		const ran = new Set(); const passed = new Set();
		results.testResults.forEach((tr)=>{ const rel = path.relative(p.ui, tr.name); ran.add(rel); if(tr.status === 'passed'){ passed.add(rel); } });
		const missing = Object.keys(p.decisions).filter((t)=>p.decisions[t].run && !ran.has(t));
		let state = null; try{ state = JSON.parse(fs.readFileSync(opts.statePath, 'utf8')); }catch(_e){ state = null; }
		fs.writeFileSync(opts.statePath, `${JSON.stringify(record(state, { plan: p, passed, ran, now: Date.now(), head: headShort() }), null, 1)}\n`);
		if(missing.length){ console.log(`⚠️ 判定要跑、jest 却没跑到的重套件 ${missing.length} 套(不记通过):${missing.slice(0, 5).join(', ')}`); }
	}else{
		console.log('⚠️ 没读到 jest 结果文件:本次不记任何通过');
	}
	const line = summarize(p);
	console.log(`== ${line}`);
	if(opts.summaryOut){ fs.writeFileSync(opts.summaryOut, `${line}\n`); }
	return rc;
}

// 登记表合同(预检用):每族都匹配到测试文件;全局输入每条都匹配到文件;仓里每个带片号的测试文件(*.<数字>.test.js = 分片过的
//   大套件)都归某一族 —— 新分片的大套件忘了登记 = 红(它就永远全量跑,复用器省不了它的机时;登记了才会被核复用口径)。
function registryProblems(reg, uiFiles, repoFiles){
	const out = [];
	const famRes = (reg.families || []).map((f)=>({ id: f.id, re: globRe(f.tests) }));
	famRes.forEach((f)=>{ if(!uiFiles.some((t)=>f.re.test(t))){ out.push(`族 ${f.id} 没匹配到任何测试文件(${reg.families.find((x)=>x.id === f.id).tests})`); } });
	(reg.globalInputs || []).forEach((g)=>{ const re = globRe(g); if(!repoFiles.some((f)=>re.test(f))){ out.push(`全局输入没匹配到文件:${g}`); } });
	uiFiles.filter((t)=>/\.\d+\.test\.jsx?$/.test(t) && !/(^|\/)node_modules\//.test(t)).forEach((t)=>{ if(!famRes.some((f)=>f.re.test(t))){ out.push(`分片测试文件不在任何族里:${t}(去 ${REGISTRY_REL} 登记)`); } });
	const ids = (reg.families || []).map((f)=>f.id);
	if(new Set(ids).size !== ids.length){ out.push('族 id 重复'); }
	return out;
}
function cmdCheck(opts){
	const reg = JSON.parse(fs.readFileSync(path.join(opts.ui, REGISTRY_REL), 'utf8'));
	const ls = (cwd)=>execFileSync('git', ['-C', cwd, 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], { encoding: 'utf8', maxBuffer: 256 * 1024 * 1024 }).split('\0').filter(Boolean);
	const probs = registryProblems(reg, ls(opts.ui), ls(REPO_ROOT));
	if(probs.length){ console.error(`❌ 重套件登记表不合:\n  ${probs.join('\n  ')}`); return 1; }
	console.log(`✅ 重套件登记表合规:${reg.families.length} 族,带片号的测试文件全部已登记`);
	return 0;
}

// ───────────────────────── 自证 ─────────────────────────
function selfTest(){
	const fails = [];
	const ok = (cond, what)=>{ if(!cond){ fails.push(what); } };
	const fams = [{ id: 'A', sample: 1, tests: ['a.1.test.js', 'a.2.test.js', 'a.3.test.js'] }, { id: 'B', sample: 0, tests: ['b.test.js'] }];
	const keys = { 'a.1.test.js': 'k1', 'a.2.test.js': 'k2', 'a.3.test.js': 'k3', 'b.test.js': 'kb' };
	const now = Date.parse('2026-10-30T12:00:00Z');
	const fresh = new Date(now - 3600000).toISOString();
	const st = { version: STATE_VERSION, rotation: { A: 0 }, suites: { 'a.1.test.js': { key: 'k1', passedAt: fresh }, 'a.2.test.js': { key: 'k2', passedAt: fresh }, 'a.3.test.js': { key: 'k3', passedAt: fresh }, 'b.test.js': { key: 'kb', passedAt: fresh } } };
	const base = { families: fams, keys, state: st, now, maxAgeDays: 7, full: false, fsReadFamilies: new Set() };
	const d0 = decide(base);
	ok(d0['a.1.test.js'].run && /抽样/.test(d0['a.1.test.js'].reason), '① 轮换抽样:A 族第 0 轮跑第 1 片');
	ok(!d0['a.2.test.js'].run && !d0['a.3.test.js'].run && !d0['b.test.js'].run, '② 指纹未变且新鲜 → 复用');
	ok(decide({ ...base, keys: { ...keys, 'a.3.test.js': 'k3x' } })['a.3.test.js'].run, '③ 指纹变了 → 跑');
	ok(!decide({ ...base, keys: { ...keys, 'a.3.test.js': 'k3x' } })['a.2.test.js'].run, '③b 只变一片 → 别的片仍复用');
	ok(Object.values(decide({ ...base, full: true })).every((d)=>d.run), '④ --full → 全跑');
	ok(Object.values(decide({ ...base, state: null })).every((d)=>d.run), '⑤ 无状态 → 全跑');
	ok(Object.values(decide({ ...base, state: { ...st, version: STATE_VERSION + 1 } })).every((d)=>d.run), '⑤b 状态版本不对 → 全跑');
	const stale = JSON.parse(JSON.stringify(st)); stale.suites['b.test.js'].passedAt = new Date(now - 8 * 86400000).toISOString();
	ok(decide({ ...base, state: stale })['b.test.js'].run, '⑥ 超过 maxAgeDays → 跑');
	ok(decide({ ...base, fsReadFamilies: new Set(['B']) })['b.test.js'].run, '⑦ 闭包里读文件系统 → 本族不复用');
	const noRec = JSON.parse(JSON.stringify(st)); delete noRec.suites['a.2.test.js'];
	ok(decide({ ...base, state: noRec })['a.2.test.js'].run, '⑧ 没有通过记录 → 跑');
	const bad = JSON.parse(JSON.stringify(st)); bad.suites['b.test.js'].passedAt = 'not-a-date';
	ok(decide({ ...base, state: bad })['b.test.js'].run, '⑨ 通过时间坏 → 跑(不当新鲜)');
	// 轮换:N 轮跑遍全族
	const seenSample = new Set(); for(let r = 0; r < 3; r += 1){ sampleOf(fams[0].tests, 1, r).forEach((t)=>seenSample.add(t)); }
	ok(seenSample.size === 3, '⑩ 轮换 3 轮跑遍 A 族 3 片');
	// record:只记真跑且通过;跑了没过删记录;没跑的不动;轮换前进
	const p = { families: fams, keys: { ...keys, 'a.3.test.js': 'k3x' }, decisions: decide({ ...base, keys: { ...keys, 'a.3.test.js': 'k3x' } }) };
	const st2 = record(st, { plan: p, ran: new Set(['a.1.test.js', 'a.3.test.js']), passed: new Set(['a.3.test.js']), now, head: 'abc' });
	ok(st2.suites['a.3.test.js'].key === 'k3x', '⑪ 真跑且通过 → 记新指纹');
	ok(!st2.suites['a.1.test.js'], '⑫ 真跑没过 → 删记录(下次必跑)');
	ok(st2.suites['a.2.test.js'].key === 'k2', '⑬ 没跑的(复用)记录不动');
	ok(st2.rotation.A === 1 && !st2.rotation.B, '⑭ 跑了的族轮换前进一格,没跑的族不动');
	const st3 = record(st, { plan: p, ran: new Set(), passed: new Set(), now });
	ok(st3.suites['a.3.test.js'].key === 'k3', '⑮ 判定要跑却没跑到 → 不记通过');
	// glob
	ok(globRe('src/x/__tests__/s.*.test.js').test('src/x/__tests__/s.3.test.js') && !globRe('src/x/__tests__/s.*.test.js').test('src/x/__tests__/s.3.test.jsx'), '⑯ glob * 匹配片号');
	ok(globRe('Horosa-Web/astropy/**').test('Horosa-Web/astropy/a/b.py') && !globRe('Horosa-Web/astropy/**').test('Horosa-Web/astropyx/a.py'), '⑰ glob ** 跨目录、不越界');
	{
		const srcs = { 'W/ui/src/x/__tests__/h.js': "const s = fs.readFileSync(p, 'utf8')", 'W/ui/test/shim.js': "fs.readFileSync(nm)", 'W/ui/src/a.js': "fs.readFileSync(x)", 'W/ui/src/x/__tests__/k.js': 'export const k = 1' };
		const cul = fsReadCulprits(Object.keys(srcs), (r)=>srcs[r], [globRe('W/ui/test/**')]);
		ok(cul.length === 1 && cul[0] === 'W/ui/src/x/__tests__/h.js', '⑲ 读文件的测试助手算漏洞;全局输入里的垫片、非测试目录、不读文件的助手不算');
	}
	ok(FS_READ_RE.test("fs.readFileSync(p, 'utf8')") && FS_READ_RE.test('fs.existsSync(x)') && !FS_READ_RE.test('fs.writeFileSync(p, s)'), '⑱ 读文件判据:读算、写不算');
	{
		const reg = { families: [{ id: 'S', tests: 'src/a/s.*.test.js' }], globalInputs: ['x/p.json'] };
		ok(registryProblems(reg, ['src/a/s.1.test.js', 'src/a/s.2.test.js'], ['x/p.json']).length === 0, '⑳ 登记表合同:全覆盖时零问题');
		ok(registryProblems(reg, ['src/a/s.1.test.js', 'src/b/t.3.test.js'], ['x/p.json']).some((m)=>/t\.3\.test\.js/.test(m)), '㉑ 带片号的测试文件不在任何族 → 报');
		ok(registryProblems(reg, ['src/a/s.1.test.js'], []).some((m)=>/全局输入/.test(m)), '㉒ 全局输入缺 → 报');
		ok(registryProblems({ ...reg, families: [...reg.families, { id: 'Z', tests: 'src/z/*.test.js' }] }, ['src/a/s.1.test.js'], ['x/p.json']).some((m)=>/族 Z/.test(m)), '㉓ 族匹配不到文件 → 报');
	}
	if(fails.length){ console.error(`❌ jest_heavy_reuse 判据自证失败:\n  ${fails.join('\n  ')}`); return 1; }
	console.log('✅ jest_heavy_reuse 判据自证通过(23 向:抽样 / 复用 / 指纹变 / 单片变 / 全跑 / 无状态 / 版本 / 过期 / 读文件 / 无记录 / 坏时间 / 轮换跑遍 / 记通过 / 删失败 / 复用不动 / 轮换前进 / 没跑到不记 / glob 两条 / 读写区分 / 读文件助手口径 / 登记表合同四条)');
	return 0;
}

function parseOpts(argv){
	const opts = { ui: DEFAULT_UI, statePath: DEFAULT_STATE, full: process.env.HOROSA_BASELINE_JEST_FULL === '1', json: false, summaryOut: null };
	const rest = [];
	for(let i = 0; i < argv.length; i += 1){
		const a = argv[i];
		if(a === '--'){ return { opts, rest, jestArgs: argv.slice(i + 1) }; }
		if(a === '--ui'){ opts.ui = path.resolve(argv[++i]); }
		else if(a === '--state'){ opts.statePath = path.resolve(argv[++i]); }
		else if(a === '--summary-out'){ opts.summaryOut = path.resolve(argv[++i]); }
		else if(a === '--full'){ opts.full = true; }
		else if(a === '--json'){ opts.json = true; }
		else{ rest.push(a); }
	}
	return { opts, rest, jestArgs: [] };
}

if(require.main === module){
	const argv = process.argv.slice(2);
	if(argv[0] === '--self-test'){ process.exit(selfTest()); }
	const cmd = argv[0];
	const { opts, jestArgs } = parseOpts(argv.slice(1));
	(async ()=>{
		if(cmd === 'plan'){ const p = await plan(opts); if(opts.json){ console.log(JSON.stringify({ decisions: p.decisions, keys: p.keys, closureSizes: p.closureSizes, fsReadWhy: p.fsReadWhy }, null, 1)); }else{ printPlan(p); } return 0; }
		if(cmd === 'run'){ return cmdRun(opts, jestArgs); }
		if(cmd === 'check'){ return cmdCheck(opts); }
		console.error('用法:jest_heavy_reuse.js run|plan|check [--ui 目录] [--state 文件] [--full] [--summary-out 文件] [-- umi-test 参数…] | --self-test');
		return 2;
	})().then((rc)=>process.exit(rc), (e)=>{ console.error(`❌ ${e && e.stack ? e.stack : e}`); process.exit(2); });
}

module.exports = { decide, record, sampleOf, globRe, fsReadCulprits, registryProblems, STATE_VERSION };
