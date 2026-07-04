// 空闲预热队列调度语义:顺序执行/失败跳过/交互让路/kill-switch/幂等启动。
import {
	startIdleWarmQueue,
	registerIdleWarmTask,
	__resetIdleWarmQueue,
	__idleWarmStats,
} from '../idleWarmQueue';

// jsdom 无 requestIdleCallback → 走 setTimeout 降级路径,fake timers 可完全驱动。
jest.useFakeTimers();

async function flushAll(){
	// setTimeout 链与 promise 微任务交替推进:每步 advance 后必须让出微任务档,
	// 任务的 .finally(→scheduleIdle) 才有机会登记下一个 timer。
	for(let i = 0; i < 60; i += 1){
		jest.advanceTimersByTime(1000);
		// eslint-disable-next-line no-await-in-loop
		await Promise.resolve();
		// eslint-disable-next-line no-await-in-loop
		await Promise.resolve();
	}
}

beforeEach(()=>{
	__resetIdleWarmQueue();
	window.localStorage.removeItem('horosa.perf.idleWarmQueue');
});

describe('idleWarmQueue', ()=>{
	it('顺序执行全部任务;单个失败静默跳过不断链', async ()=>{
		const ran = [];
		const tasks = [
			{ name: 'a', task: ()=>{ ran.push('a'); return Promise.resolve(); } },
			{ name: 'boom', task: ()=>{ ran.push('boom'); return Promise.reject(new Error('x')); } },
			{ name: 'b', task: ()=>{ ran.push('b'); return Promise.resolve(); } },
		];
		startIdleWarmQueue({ initialDelayMs: 10, __tasksOverride: tasks });
		await flushAll();
		await Promise.resolve();
		await flushAll();
		expect(ran).toEqual(['a', 'boom', 'b']);
	});

	it('kill-switch:horosa.perf.idleWarmQueue=0 时整队列不启动', async ()=>{
		window.localStorage.setItem('horosa.perf.idleWarmQueue', '0');
		const ran = [];
		startIdleWarmQueue({ initialDelayMs: 10, __tasksOverride: [
			{ name: 'a', task: ()=>{ ran.push('a'); return Promise.resolve(); } },
		] });
		await flushAll();
		expect(ran).toEqual([]);
		expect(__idleWarmStats().started).toBe(false);
	});

	it('幂等:重复 start 不叠加队列', async ()=>{
		const ran = [];
		const mk = (n)=>({ name: n, task: ()=>{ ran.push(n); return Promise.resolve(); } });
		startIdleWarmQueue({ initialDelayMs: 10, __tasksOverride: [mk('x')] });
		startIdleWarmQueue({ initialDelayMs: 10, __tasksOverride: [mk('y')] });
		await flushAll();
		await Promise.resolve();
		await flushAll();
		expect(ran).toEqual(['x']);
	});

	it('交互让路:pointerdown 后 4s 静默期内不执行,期满续跑', async ()=>{
		const ran = [];
		startIdleWarmQueue({ initialDelayMs: 10, __tasksOverride: [
			{ name: 'a', task: ()=>{ ran.push('a'); return Promise.resolve(); } },
		] });
		// 队列首个任务尚未到点(initialDelay 10ms 未推进),先触发交互
		window.dispatchEvent(new Event('pointerdown'));
		jest.advanceTimersByTime(2000);   // 静默期内(4s)
		expect(ran).toEqual([]);
		await flushAll();                  // 静默期满 + 空闲档到点
		await Promise.resolve();
		await flushAll();
		expect(ran).toEqual(['a']);
	});

	it('registerIdleWarmTask 注册的数据层任务进入统计', ()=>{
		registerIdleWarmTask('sample', ()=>Promise.resolve());
		expect(__idleWarmStats().dataTasks).toBe(1);
		expect(__idleWarmStats().engines).toBeGreaterThanOrEqual(8);
	});
});
