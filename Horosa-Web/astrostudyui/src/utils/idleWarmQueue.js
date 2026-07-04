// 就绪后空闲预热队列(WS-3c)。
//
// 目标:暖后「任意技法首点亚秒」——把用户第一次点某技法才付的成本
// (引擎模块初始化/常量表构建/JIT、乃至高频数据请求)挪进就绪后的空闲时段。
// 三层任务:
//   chunk 层 —— UI 组件 chunk 预载已由 pages/index.js startIdlePreload 承担(概率序+悬停预取);
//   引擎层 —— 本注册表:动态 import 本地纯计算引擎模块(模块级常量表/查表结构构建是首点大头;
//             动态 import 不进主包,已预载过的 chunk 秒回);
//   数据层 —— registerIdleWarmTask 留给各技法按真实取数口径登记(绝不在此臆造技法参数)。
//
// 调度纪律:
//   · requestIdleCallback 逐个执行(降级 setTimeout),每次只跑一个任务;
//   · 用户任何交互(pointerdown/keydown/wheel)即让路 —— 暂停队列,静默 4s 后再续;
//   · 任务失败静默跳过(预热是优化不是功能,绝不影响业务);
//   · kill-switch:localStorage horosa.perf.idleWarmQueue = '0'(perfFlags 同款约定)。
import { idleWarmQueueEnabled } from './perfFlags';

// 引擎层注册表:动态 import 高频技法的本地纯计算模块(与导航概率序同基准)。
// 只列「用户首点该技法必然要初始化」的模块;新技法引擎按同格式追加。
const ENGINE_WARM_IMPORTS = [
	() => import('./baziLunarLocal'),          // 八字本地历法引擎(主盘走本地)
	() => import('./baziShenShaLocal'),        // 八字神煞
	() => import('../components/ziwei/ZiweiCalc'),      // 紫微本地引擎(流派/四化表)
	() => import('../components/guazhan/GuaZhanMain'),  // 六爻装卦引擎(卦表)
	() => import('../components/lrzhan/LiuRengMain'),   // 大六壬(课经/神煞表)
	() => import('../components/dunjia/DunJiaCalc'),    // 奇门排盘引擎
	() => import('../components/taiyi/TaiYiCalc'),      // 太乙本地推演
	() => import('./heluoLocal'),              // 河洛理数
	() => import('../divination/horary/horaryEngine'),  // 卜卦盘引擎
	() => import('../divination/election/electionEngine'), // 择日引擎
];

// 数据层任务注册(各技法自行登记「按当前命盘的真实取数」,如填 L1/L2/后端 paramhash 的
// 幂等请求)。task: () => Promise<any>;name 仅用于诊断。
const DATA_WARM_TASKS = [];
export function registerIdleWarmTask(name, task){
	if(typeof task === 'function'){
		DATA_WARM_TASKS.push({ name: `${name || 'anon'}`, task });
	}
}

let started = false;
let paused = false;
let pauseTimer = null;

function scheduleIdle(fn){
	if(typeof window !== 'undefined' && typeof window.requestIdleCallback === 'function'){
		window.requestIdleCallback(fn, { timeout: 4000 });
	}else{
		setTimeout(fn, 500);
	}
}

function attachYieldListeners(){
	if(typeof window === 'undefined'){
		return;
	}
	const yieldNow = ()=>{
		paused = true;
		if(pauseTimer){
			clearTimeout(pauseTimer);
		}
		// 交互后静默 4s 再续跑:预热永远给用户操作让路。
		pauseTimer = setTimeout(()=>{ paused = false; }, 4000);
	};
	try{
		window.addEventListener('pointerdown', yieldNow, { passive: true });
		window.addEventListener('keydown', yieldNow, { passive: true });
		window.addEventListener('wheel', yieldNow, { passive: true });
	}catch(e){ /* 监听失败不影响队列(只是不让路) */ }
}

// 启动队列:index.js 首屏就绪后调用(幂等)。initialDelayMs 默认 4s——
// 排在 chunk 预载(1s 起步)之后,错峰不抢同一段空闲。
export function startIdleWarmQueue(options = {}){
	if(started || !idleWarmQueueEnabled()){
		return;
	}
	if(typeof window === 'undefined'){
		return;
	}
	started = true;
	attachYieldListeners();
	// __tasksOverride:仅测试注入(调度语义可测,不真拉引擎模块)。
	const tasks = Array.isArray(options.__tasksOverride)
		? options.__tasksOverride.slice()
		: [
			...ENGINE_WARM_IMPORTS.map((imp, i) => ({ name: `engine:${i}`, task: imp })),
			...DATA_WARM_TASKS,
		];
	const next = ()=>{
		if(paused){
			scheduleIdle(next);
			return;
		}
		const entry = tasks.shift();
		if(!entry){
			return;
		}
		Promise.resolve()
			.then(entry.task)
			.catch(()=>{ /* 预热失败静默:首点回到冷即付的现状 */ })
			.finally(()=>{ scheduleIdle(next); });
	};
	setTimeout(()=>{ scheduleIdle(next); }, options.initialDelayMs || 4000);
}

// 测试用
export function __resetIdleWarmQueue(){
	started = false;
	paused = false;
	DATA_WARM_TASKS.length = 0;
}
export function __idleWarmStats(){
	return { started, paused, dataTasks: DATA_WARM_TASKS.length, engines: ENGINE_WARM_IMPORTS.length };
}
