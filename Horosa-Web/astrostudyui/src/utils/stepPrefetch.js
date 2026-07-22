// stepPrefetch —— 时间步进方向预取调度器(极速化大修 WP-P1)。
//
// 原理:点步进(±步长)时「下一步」的时间完全可预测。主请求 settle 后,空闲时把相邻
// 1-2 步的 /chart(及当前技法登记的端点)预先算好塞进既有缓存(chartMem/requestDedupe)——
// 用户点下一步时命中,请求耗时 229ms → ~8ms(实测)。
//
// 五重风暴防护:
//   ① 触发点在 fetchByFields settle 之后(用户已停手 + 主盘已回,天然错峰);
//   ② latest-wins 代际令牌:新一轮 submit 整队替换,旧代排队任务全弃
//      (已在途的网络请求不 abort —— 结果仍可入缓存,无害);
//   ③ requestIdleCallback 调度(降级 setTimeout 250ms) + 串行并发 1;
//   ④ 每 settle 预算 ≤3 个任务 + 任务间最小间隔 150ms;
//   ⑤ 预取请求由任务方自带 silent + retry:{retries:0} —— 后端重启窗口绝不退避重试风暴。
//
// 纪律(有 jest 快照哨兵 + preflight 机械核双镜像):
//   · 预取参数必须「与用户真点会发出的请求」逐字节同键(复用同一参数构建路径),绝不臆造;
//   · PREFETCH_ALLOWED_PATHS 白名单之外的端点绝不预取 —— 尤其【随机起卦/抽牌类】
//     (dice/摇卦/塔罗/地占),预取即把随机结果钉死;AI/心跳类同禁。
import { stepPrefetchEnabled, stepSelectPrefetchEnabled } from './perfFlags';

/** 允许预取的端点前缀(显式白名单;哨兵对照此数组,增删须同步测试) */
export const PREFETCH_ALLOWED_PATHS = [
	'/chart',        // 共享出盘(chartMem+requestDedupe 双层承接)
	'/predict/',     // 推运(dice 由 FORBIDDEN 拦)
	'/ziwei/',       // 紫微
	'/liureng/',     // 六壬/金口诀共用神将
	'/pan',          // kentang 各技法 /{key}/pan(确定性纯计算)
];
/** 绝不预取(与 _requestCache 头注纪律镜像;哨兵断言两表交集为空) */
export const PREFETCH_FORBIDDEN_MARKERS = [
	'dice', 'gua', 'tarot', 'geomancy', 'aianalysis', 'heartbeat', 'planetarium',
];

const BUDGET_PER_SETTLE = 3;
const MIN_GAP_MS = 150;

let generation = 0;
let running = false;
let queue = [];

function scheduleIdle(fn){
	if(typeof window !== 'undefined' && typeof window.requestIdleCallback === 'function'){
		window.requestIdleCallback(fn, { timeout: 2000 });
		return;
	}
	setTimeout(fn, 250);
}

function pump(){
	if(running){
		return;
	}
	const entry = queue.shift();
	if(!entry){
		return;
	}
	running = true;
	scheduleIdle(()=>{
		if(entry.gen !== generation){
			// 旧代任务:用户已有更新的操作,这步预取的目标时间已不是「下一步」—— 弃
			running = false;
			pump();
			return;
		}
		Promise.resolve().then(entry.run)
			.catch(()=>{ /* 预取失败静默:回到冷即付现状,正式请求自会兜底 */ })
			.finally(()=>{
				setTimeout(()=>{
					running = false;
					pump();
				}, MIN_GAP_MS);
			});
	});
}

/**
 * 提交一轮预取(fetchByFields settle 后调)。整队替换(latest-wins)。
 * @param {Array<{name:string, run:function}>} tasks 预取任务(run 返回 Promise;
 *        任务内的请求自带 silent+零重试;结果自然落进各自缓存层)
 */
export function submitStepPrefetch(tasks, opts){
	if(!stepPrefetchEnabled() || !Array.isArray(tasks) || !tasks.length){
		return;
	}
	generation += 1;
	const gen = generation;
	const budget = opts && Number.isInteger(opts.budget) && opts.budget > 0
		? Math.min(opts.budget, 5)   // 硬顶 5:选步长双向 ±2=4 任务;绝不放开成风暴
		: BUDGET_PER_SETTLE;
	queue = tasks.slice(0, budget).map((t)=>({ ...t, gen }));
	pump();
}

// —— [R3-A1] 选步长即预取:DateTimeSelector.changeTimeType(opt-in 宿主)→ 此处 ——
// 与 settle 后预取共用同一队列/代际/预算体系;处理器由 models/astro 注册
// (读 store 现 fields 走 buildStepPrefetchTasks 双向 ±2,键构造同源)。
// 同 unit 5s 去重:反复点同档不重复排队(切档立即生效,latest-wins 覆盖旧代)。
let stepSelectHandler = null;
let lastStepSelect = { unit: null, at: 0 };

export function registerStepSelectHandler(fn){
	if(typeof fn === 'function'){
		stepSelectHandler = fn;
	}
}

export function fireStepSelectPrefetch(unit){
	try{
		if(!stepPrefetchEnabled() || !stepSelectPrefetchEnabled() || !unit){
			return;
		}
		const now = Date.now();
		if(lastStepSelect.unit === unit && (now - lastStepSelect.at) < 5000){
			return;
		}
		lastStepSelect = { unit, at: now };
		if(stepSelectHandler){
			stepSelectHandler(unit);
		}
	}catch(e){ /* 预取失败无害 */ }
}

/** 测试用:清选步长去重态 */
export function __resetStepSelectForTest(){
	lastStepSelect = { unit: null, at: 0 };
}

// —— Phase B:技法端点注册表(kentang pan 等 raw fetch 不经 requestDedupe,
//    预取必须落到技法自己的缓存层 —— 由各技法用【自己真实的请求函数】登记) ——
const REGISTRY = new Map();

/**
 * @param {string} tabKey 主 tab 键(state.astro.currentTab 口径)
 * @param {function} fn (fieldValues, stepHint) => Array<{name, run}> —— 返回该技法的预取任务
 */
export function registerStepPrefetcher(tabKey, fn){
	if(tabKey && typeof fn === 'function'){
		REGISTRY.set(tabKey, fn);
	}
}

export function getStepPrefetcher(tabKey){
	return REGISTRY.get(tabKey);
}

/** 测试用:清内部态 */
export function __resetStepPrefetch(){
	generation += 1;
	queue = [];
	running = false;
	REGISTRY.clear();
}
