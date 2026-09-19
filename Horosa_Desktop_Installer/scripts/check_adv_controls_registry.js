#!/usr/bin/env node
// 「进阶」页控件登记表机械网(preflight 由控件登记段调用;FL-20260907-2 族:「写了键、没人读」的死开关只能靠
// 「每个控件必登记、必有消费方、必有真栈判据」的登记表堵住 —— 组件测试绿证不了消费方读键)。
//
// 用法: node check_adv_controls_registry.js <astrostudyui 目录> [--self-test] [--json]
// 判据:
//   (a) 14 个面板源码(剥注释)里出现的每个 data-* 都在 controls ∪ markers 里;登记的锚反过来必须出现在其声明文件里
//   (b) 每条 controls.l5[] 的 id 必须存在于 Horosa_Desktop_Installer/scripts/l5/scenarios/*.json(无 l5 目录 → 跳过并打印)
//   (c) 每条 consumers[] 形如 file#symbol:文件在 src 下存在,且剥注释后声明了该符号(function / const / let / export / 赋值)
//   (d) id 唯一;card ∈ AdvCard.js 的分区锚集 ∪ {pane};kind ∈ 登记表 kinds;非 collapse/tab/pill/pagination 类必须有 ≥1 消费方
//   (e) 棘轮:controls 数 ≥ REGISTRY_FLOOR(只增);尚无 端到端判据的控件数 ≤ PENDING_MAX(只减)
//   (f) 挂名网(M-177 / M-178,2026-09-14):「用例 id 存在」证不了「用例操作了这个控件」——
//       · 每条 l5[] 用例的 JS / localStorage / cleanupKeys 文本必须命中本条的锚或存储键,否则记「挂名」;挂名对数 ≤ L5_NOMINAL_MAX(只减);
//       · 每条 l5[] 用例的 expect 不得为空(零判据的用例不算判据);
//       · jest[] 里的名字必须能落到 src 下真实的 *.test.js(硬红),且文件正文命中锚 / 消费符号 / 存储键,否则记「挂名」;≤ JEST_NOMINAL_MAX(只减);
//       · 新增 l5Twin[](负孪生 / 效果用例):id 必须存在,且用例文本必须命中本条锚或存储键(硬红 —— 孪生不许挂名)。
// --self-test:六向量必红(删一条登记 / 假消费方符号 / 假用例 id / 棘轮 / 挂名孪生 / 假 jest 名 / 挂名棘轮压 0)+ 一向量必绿(原表),网本身坏了当场判红。
const fs = require('fs');
const path = require('path');

const REGISTRY_FLOOR = 125;   // 共享登记表的控件数下限:加控件同提交抬线,不许减(2026-09-11 +agent.openTaskCenter;2026-09-17 +ext.edit 编辑入口登记)
// 🔴 本检查器会把扩展登记表(advancedControls.private.json,存在才读)并进 controls,故实际下限
//    = 基表下限 + 本次并入的扩展条目数;写成合并后的总数只在扩展表存在时成立,不存在时恒红。
const PENDING_MAX = 0;        // 尚无 端到端判据的控件数上限(含扩展表):只减不增(C3 已落地:每个控件至少一条 端到端判据;新控件不带 用例 id = 红)
const L5_NOMINAL_MAX = 20;    // 挂名 端到端链接(用例文本不含本条锚 / 存储键)对数上限:2026-09-14 实测 20,只减不增
const JEST_NOMINAL_MAX = 32;  // 挂名 jest 链接(文件不含本条锚 / 消费符号 / 存储键)条数上限:2026-09-14 实测 32,只减不增
const PANE_FILES = [
	'chat/AdvancedPane.js', 'chat/AdvCard.js', 'chat/AdvSectionNav.js', 'chat/ChatContextPolicyPanel.js', 'chat/ChatModelRoutesPanel.js',
	'chat/BestOfPanel.js', 'chat/PersonaMemoryPanel.js', 'chat/SkillPackPanel.js', 'AgentAbilityPanel.js', 'ExternalAgentPanel.js',
	'ExternalServersPanel.js', 'WebSearchPanel.js', 'AutomationRulesPanel.js', 'ActionLedgerPanel.js',
];
const NO_CONSUMER_KINDS = ['collapse', 'tab', 'pill', 'pagination'];

// 存储键记号:'localStorage:horosa.x.v1' → ['horosa.x.v1'];'idb:workspaceMeta(aimem:)' → ['workspaceMeta','aimem:'];'ui' → []
function storeTokens(store){
	if(!store || store === 'ui'){ return []; }
	const body = `${store}`.indexOf(':') >= 0 ? `${store}`.slice(`${store}`.indexOf(':') + 1) : `${store}`;
	const m = /^([^(]+)(?:\(([^)]+)\))?/.exec(body);
	if(!m){ return [body.trim()].filter(Boolean); }
	return [m[1].trim(), m[2] ? m[2].trim() : ''].filter(Boolean);
}
function stripComments(src){
	return `${src}`.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[^:\\'"])\/\/.*$/gm, '$1');
}
function tokensOf(src){
	const out = new Set();
	const re = /(?:^|[\s{'"(])(data-[a-z][a-z0-9-]*)(?=[=:'"\s})])/g;
	let m;
	while((m = re.exec(src))){ out.add(m[1]); }
	return out;
}
function symbolDeclared(src, sym){
	const s = sym.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
	const re = new RegExp(`(^|[^A-Za-z0-9_$])(?:export\\s+)?(?:async\\s+)?function\\s+${s}\\s*\\(|(^|[^A-Za-z0-9_$])(?:export\\s+)?(?:const|let|var)\\s+${s}\\b|(^|[^A-Za-z0-9_$.])${s}\\s*=[^=]`, 'm');
	return re.test(src);
}
function readJson(p){ return JSON.parse(fs.readFileSync(p, 'utf8')); }

function loadInputs(uiDir){
	const paneDir = path.join(uiDir, 'src', 'components', 'aianalysis');
	const shared = readJson(path.join(paneDir, 'chat', 'advancedControls.registry.json'));
	const privPath = path.join(paneDir, 'chat', 'advancedControls.private.json');
	const priv = fs.existsSync(privPath) ? readJson(privPath) : null;
	const privControls = priv && priv.controls ? priv.controls : [];
	const registry = {
		kinds: shared.kinds || [],
		controls: (shared.controls || []).concat(privControls),
		markers: (shared.markers || []).concat(priv && priv.markers ? priv.markers : []),
		extCount: privControls.length,   // 棘轮下限随扩展条目数加成(见 REGISTRY_FLOOR 注)
	};
	const files = {};
	PANE_FILES.forEach((f)=>{ files[f] = stripComments(fs.readFileSync(path.join(paneDir, f), 'utf8')); });
	const cardSrc = files['chat/AdvCard.js'];
	const cards = new Set(['pane']);
	[...cardSrc.matchAll(/'(adv-[a-z-]+)'/g)].forEach((m)=>cards.add(m[1]));
	// 端到端场景 id(无 l5 目录 → null = 跳过)
	const l5Dir = path.join(uiDir, '..', '..', 'Horosa_Desktop_Installer', 'scripts', 'l5', 'scenarios');
	let scenarioIds = null;
	const scenarioText = new Map();     // id -> 用例正文(去 expect)的 JSON 串
	const scenarioHasExpect = new Map(); // id -> expect 是否非空
	if(fs.existsSync(l5Dir)){
		scenarioIds = new Set();
		fs.readdirSync(l5Dir).filter((f)=>f.endsWith('.json')).forEach((f)=>{
			try{
				const j = readJson(path.join(l5Dir, f));
				const cases = Array.isArray(j) ? j : (Array.isArray(j.cases) ? j.cases : []);
				cases.forEach((c)=>{
					if(!(c && c.id)){ return; }
					scenarioIds.add(`${c.id}`);
					const { expect: ex, ...rest } = c;
					scenarioText.set(`${c.id}`, JSON.stringify(rest));
					scenarioHasExpect.set(`${c.id}`, !!(ex && typeof ex === 'object' && Object.keys(ex).length));
				});
			}catch(e){ /* 坏文件由 端到端自检管 */ }
		});
	}
	const srcDir = path.join(uiDir, 'src');
	const jestFiles = new Map();        // 测试名(去 .test)-> 绝对路径
	(function walk(d){
		fs.readdirSync(d).forEach((n)=>{
			const full = path.join(d, n);
			if(n === 'node_modules' || n.startsWith('.')){ return; }
			if(fs.statSync(full).isDirectory()){ walk(full); return; }
			if(/\.test\.js$/.test(n)){ jestFiles.set(n.replace(/\.test\.js$/, ''), full); }
		});
	})(srcDir);
	return { registry, files, cards, scenarioIds, scenarioText, scenarioHasExpect, jestFiles, srcDir };
}

function check({ registry, files, cards, scenarioIds, scenarioText, scenarioHasExpect, jestFiles, srcDir }, opts){
	const errors = [];
	const floor = opts && Number.isFinite(opts.floor) ? opts.floor : (REGISTRY_FLOOR + (Number(registry.extCount) || 0));
	const pendingMax = opts && Number.isFinite(opts.pendingMax) ? opts.pendingMax : PENDING_MAX;
	const controls = registry.controls || [];
	const markers = registry.markers || [];
	const kinds = new Set(registry.kinds || []);
	const known = new Map();   // anchor -> [files]
	const add = (anchor, file)=>{ if(!known.has(anchor)){ known.set(anchor, new Set()); } known.get(anchor).add(file); };
	controls.forEach((c)=>add(c.anchor, c.file));
	markers.forEach((m)=>add(m.anchor, m.file));
	// (a) 源码锚 ⊆ 登记;登记锚 ⊆ 其文件
	Object.keys(files).forEach((f)=>{
		tokensOf(files[f]).forEach((t)=>{ if(!known.has(t) || !known.get(t).has(f)){ errors.push(`源码锚未登记: ${f} 里的 ${t}`); } });
	});
	known.forEach((fileSet, anchor)=>{
		fileSet.forEach((f)=>{
			if(!files[f]){ errors.push(`登记锚指向未知面板文件: ${anchor} @ ${f}`); return; }
			if(!tokensOf(files[f]).has(anchor)){ errors.push(`登记锚在其文件里找不到: ${anchor} @ ${f}`); }
		});
	});
	// (d) id / card / kind / consumers 形状
	const ids = new Set();
	controls.forEach((c)=>{
		if(!c || !c.id){ errors.push('控件缺 id'); return; }
		if(ids.has(c.id)){ errors.push(`控件 id 重复: ${c.id}`); }
		ids.add(c.id);
		if(!cards.has(c.card)){ errors.push(`控件 ${c.id} 的 card 不在分区锚集: ${c.card}`); }
		if(!kinds.has(c.kind)){ errors.push(`控件 ${c.id} 的 kind 不在枚举: ${c.kind}`); }
		if(NO_CONSUMER_KINDS.indexOf(c.kind) < 0 && !(Array.isArray(c.consumers) && c.consumers.length)){ errors.push(`控件 ${c.id} 没有消费方(kind=${c.kind})`); }
		if(!(Number(c.instances) >= 1)){ errors.push(`控件 ${c.id} instances 须 ≥1`); }
	});
	// (c) consumers file#symbol
	const srcCache = {};
	controls.forEach((c)=>{
		(c.consumers || []).forEach((ref)=>{
			const [file, sym] = `${ref}`.split('#');
			if(!file || !sym){ errors.push(`控件 ${c.id} 消费方引用格式错: ${ref}`); return; }
			const full = path.join(srcDir, file);
			if(!fs.existsSync(full)){ errors.push(`控件 ${c.id} 消费方文件不存在: ${file}`); return; }
			if(!srcCache[full]){ srcCache[full] = stripComments(fs.readFileSync(full, 'utf8')); }
			if(!symbolDeclared(srcCache[full], sym)){ errors.push(`控件 ${c.id} 消费方符号未声明: ${ref}`); }
		});
	});
	// (b) l5 ids + (f) 挂名网
	const l5NominalMax = opts && Number.isFinite(opts.l5NominalMax) ? opts.l5NominalMax : L5_NOMINAL_MAX;
	const jestNominalMax = opts && Number.isFinite(opts.jestNominalMax) ? opts.jestNominalMax : JEST_NOMINAL_MAX;
	let pending = 0;
	const l5Nominal = [];
	const jestNominal = [];
	const hitsControl = (c, text)=>{ const keys = [c.anchor].concat(storeTokens(c.store)); return keys.some((k)=>k && text.indexOf(k) >= 0); };
	controls.forEach((c)=>{
		const ids5 = Array.isArray(c.l5) ? c.l5 : [];
		if(!ids5.length){ pending += 1; }
		if(scenarioIds){
			ids5.forEach((id)=>{
				if(!scenarioIds.has(`${id}`)){ errors.push(`控件 ${c.id} 的 端到端用例不存在: ${id}`); return; }
				if(scenarioHasExpect && scenarioHasExpect.get(`${id}`) === false){ errors.push(`控件 ${c.id} 的 端到端用例 ${id} expect 为空(零判据不算判据)`); }
				if(scenarioText && !hitsControl(c, scenarioText.get(`${id}`) || '')){ l5Nominal.push(`${c.id}←${id}`); }
			});
			(Array.isArray(c.l5Twin) ? c.l5Twin : []).forEach((id)=>{
				if(!scenarioIds.has(`${id}`)){ errors.push(`控件 ${c.id} 的孪生用例不存在: ${id}`); return; }
				if(scenarioText && !hitsControl(c, scenarioText.get(`${id}`) || '')){ errors.push(`控件 ${c.id} 的孪生用例挂名(正文不含本条锚 / 存储键): ${id}`); }
			});
		}
		(Array.isArray(c.jest) ? c.jest : []).forEach((name)=>{
			if(!jestFiles){ return; }
			const full = jestFiles.get(`${name}`);
			if(!full){ errors.push(`控件 ${c.id} 的 jest 文件不存在: ${name}`); return; }
			if(!srcCache[full]){ srcCache[full] = stripComments(fs.readFileSync(full, 'utf8')); }
			const body = srcCache[full];
			const syms = (c.consumers || []).map((r)=>`${r}`.split('#')[1]).filter(Boolean);
			const hit = body.indexOf(c.anchor) >= 0 || syms.some((sy)=>body.indexOf(sy) >= 0) || storeTokens(c.store).some((k)=>body.indexOf(k) >= 0);
			if(!hit){ jestNominal.push(`${c.id}←${name}`); }
		});
	});
	// (e) 棘轮
	if(controls.length < floor){ errors.push(`登记控件数 ${controls.length} < 棘轮下限 ${floor}(登记表只许增)`); }
	if(pending > pendingMax){ errors.push(`尚无 端到端判据的控件 ${pending} 条 > 上限 ${pendingMax}(新控件必须带 用例 id)`); }
	if(l5Nominal.length > l5NominalMax){ errors.push(`挂名 端到端链接 ${l5Nominal.length} 对 > 上限 ${l5NominalMax}(只减不增;用例正文须含本条锚 / 存储键): ${l5Nominal.slice(0, 6).join(' ')}`); }
	if(jestNominal.length > jestNominalMax){ errors.push(`挂名 jest 链接 ${jestNominal.length} 条 > 上限 ${jestNominalMax}(只减不增;文件须含本条锚 / 消费符号 / 存储键): ${jestNominal.slice(0, 6).join(' ')}`); }
	return { errors, stats: { controls: controls.length, markers: markers.length, pending, l5Checked: !!scenarioIds, l5Nominal, jestNominal }, nominal: { l5: l5Nominal, jest: jestNominal } };
}

function selfTest(inputs){
	const base = check(inputs, {});
	if(base.errors.length){ return { ok: false, why: `基线不绿: ${base.errors[0]}` }; }
	const clone = ()=>({ ...inputs, registry: JSON.parse(JSON.stringify(inputs.registry)) });
	// 向量①:删一条源码里真实存在的登记 → 必红「源码锚未登记」
	const v1 = clone(); v1.registry.controls = v1.registry.controls.filter((c)=>c.anchor !== 'data-model-route');
	const r1 = check(v1, { floor: 0 });
	if(!r1.errors.some((e)=>e.indexOf('源码锚未登记') >= 0 && e.indexOf('data-model-route') >= 0)){ return { ok: false, why: '向量①(删登记)未判红' }; }
	// 向量②:假消费方符号 → 必红
	const v2 = clone(); v2.registry.controls[0].consumers = ['utils/aiModelRouting.js#noSuchSymbolXYZ'];
	const r2 = check(v2, {});
	if(!r2.errors.some((e)=>e.indexOf('消费方符号未声明') >= 0)){ return { ok: false, why: '向量②(假消费方)未判红' }; }
	// 向量③:假用例 id → 必红(无 l5 目录时用假场景集代替,网的判别力同样自证)
	const v3 = clone(); v3.registry.controls[0].l5 = ['S_no_such_case_999'];
	if(!v3.scenarioIds){ v3.scenarioIds = new Set(['S0_agent_off']); v3.registry.controls.forEach((c, i)=>{ if(i){ c.l5 = []; } }); }
	const r3 = check(v3, { pendingMax: 10000 });
	if(!r3.errors.some((e)=>e.indexOf('端到端用例不存在') >= 0)){ return { ok: false, why: '向量③(假用例 id)未判红' }; }
	// 向量④:棘轮 → 必红
	const r4 = check(clone(), { floor: inputs.registry.controls.length + 1 });
	if(!r4.errors.some((e)=>e.indexOf('棘轮下限') >= 0)){ return { ok: false, why: '向量④(棘轮)未判红' }; }
	// 向量⑤:挂名孪生 —— 把一条真实存在、但正文不含本条锚 / 存储键的用例挂成 l5Twin → 必红(孪生不许挂名)
	const v5 = clone();
	if(!v5.scenarioIds){ v5.scenarioIds = new Set(['S0_agent_off']); v5.scenarioText = new Map([['S0_agent_off', '{"id":"S0_agent_off"}']]); v5.scenarioHasExpect = new Map([['S0_agent_off', true]]); v5.registry.controls.forEach((c)=>{ c.l5 = []; }); }
	const c5 = v5.registry.controls[0];
	const foreign = Array.from(v5.scenarioIds).find((id)=>{ const t = v5.scenarioText.get(id) || ''; return t.indexOf(c5.anchor) < 0 && !storeTokens(c5.store).some((k)=>t.indexOf(k) >= 0); });
	if(!foreign){ return { ok: false, why: '向量⑤找不到一条不含首控件锚的用例(网无法自证)' }; }
	c5.l5Twin = [foreign];
	const r5 = check(v5, { pendingMax: 10000, l5NominalMax: 10000, jestNominalMax: 10000 });
	if(!r5.errors.some((e)=>e.indexOf('孪生用例挂名') >= 0)){ return { ok: false, why: '向量⑤(挂名孪生)未判红' }; }
	// 向量⑥:假 jest 名 → 必红(src 下没有这个 *.test.js)
	const v6 = clone(); v6.registry.controls[0].jest = ['noSuchJestFile_zz_999'];
	const r6 = check(v6, { pendingMax: 10000, l5NominalMax: 10000, jestNominalMax: 10000 });
	if(!r6.errors.some((e)=>e.indexOf('jest 文件不存在') >= 0)){ return { ok: false, why: '向量⑥(假 jest 名)未判红' }; }
	// 向量⑦:挂名棘轮 —— 上限压到 0 必红(证明挂名计数真的在算),原表上限必绿(基线已证)
	const r7 = check(clone(), { l5NominalMax: 0, jestNominalMax: 0 });
	if(!r7.errors.some((e)=>e.indexOf('挂名') >= 0)){ return { ok: false, why: '向量⑦(挂名棘轮压 0)未判红 —— 挂名计数为 0?那说明网没在算' }; }
	return { ok: true };
}

function main(){
	const args = process.argv.slice(2);
	const uiDir = args.find((a)=>!a.startsWith('--'));
	if(!uiDir){ console.error('用法: node check_adv_controls_registry.js <astrostudyui 目录> [--self-test] [--json]'); process.exit(2); }
	const inputs = loadInputs(path.resolve(uiDir));
	if(args.indexOf('--self-test') >= 0){
		const st = selfTest(inputs);
		if(!st.ok){ console.error(`❌ 登记表检查器判别向量自证失败: ${st.why}`); process.exit(1); }
		console.log('✅ 登记表检查器判别向量自证通过(删登记/假消费方/假用例 id/棘轮/挂名孪生/假 jest 名/挂名棘轮压 0 七向量各判红,原表绿)');
		return;
	}
	const r = check(inputs, {});
	if(args.indexOf('--json') >= 0){ console.log(JSON.stringify(r, null, 2)); }
	if(r.errors.length){
		r.errors.slice(0, 40).forEach((e)=>console.error(`  ❌ ${e}`));
		console.error(`❌ 进阶页控件登记表:${r.errors.length} 处不合(控件 ${r.stats.controls} / 状态锚 ${r.stats.markers} / 待补端到端 ${r.stats.pending})`);
		process.exit(1);
	}
	console.log(`✅ 进阶页控件登记表合规:控件 ${r.stats.controls} / 状态锚 ${r.stats.markers} / 待补 端到端判据 ${r.stats.pending} / 挂名 端到端 ${r.stats.l5Nominal.length}≤${L5_NOMINAL_MAX} / 挂名 jest ${r.stats.jestNominal.length}≤${JEST_NOMINAL_MAX}${r.stats.l5Checked ? '' : '(无 l5 目录,用例 id 校验跳过)'}`);
}

if(require.main === module){ main(); }
module.exports = { check, loadInputs, selfTest, tokensOf, stripComments, symbolDeclared, storeTokens, PANE_FILES, REGISTRY_FLOOR, PENDING_MAX, L5_NOMINAL_MAX, JEST_NOMINAL_MAX };
