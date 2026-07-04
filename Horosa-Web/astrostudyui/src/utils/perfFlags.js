// perfFlags.js —— 流畅度优化项的独立开关(默认全开,调用时读取)。
//
// 每项优化只动「时机/调度」不动「内容/语义」,但仍各配 kill-switch:现场发现异常时
// 单项关闭立即回到旧行为,无需回滚代码。关闭方法(控制台执行后刷新):
//   localStorage.setItem('horosa.perf.lazySnapshot', '0')   // 快照惰性构建
//   localStorage.setItem('horosa.perf.ziweiRulesCache', '0')// 紫微 rules 会话缓存
//   localStorage.setItem('horosa.perf.chartDrawGuard', '0') // 图面重绘签名守卫
//   localStorage.setItem('horosa.perf.chartSCU', '0')       // 盘面重组件 shouldComponentUpdate
//   localStorage.setItem('horosa.perf.hookRaf', '0')        // 排盘 hook rAF 化
//   localStorage.setItem('horosa.perf.freezeInactiveTabs','0')// 冻结非激活 TabPane 重渲
//   localStorage.setItem('horosa.perf.requestDedupe', '0')  // 计算请求 去重+短TTL缓存
//   localStorage.setItem('horosa.perf.techniqueCache', '0') // L2 技法结果缓存(10min,来回拨参数≈0)
//   localStorage.setItem('horosa.perf.idleWarmQueue', '0')  // 就绪后空闲预热队列(chunk/引擎/数据)
// 恢复:对应 key removeItem 或设 '1'。

function flagEnabled(key){
	try{
		if(typeof window !== 'undefined' && window.localStorage){
			return window.localStorage.getItem(key) !== '0';
		}
	}catch(e){
		// localStorage 不可用时按默认开
	}
	return true;
}

export function lazySnapshotBuildEnabled(){
	return flagEnabled('horosa.perf.lazySnapshot');
}

export function ziweiRulesCacheEnabled(){
	return flagEnabled('horosa.perf.ziweiRulesCache');
}

export function chartDrawGuardEnabled(){
	return flagEnabled('horosa.perf.chartDrawGuard');
}

export function chartSCUEnabled(){
	return flagEnabled('horosa.perf.chartSCU');
}

export function hookRafEnabled(){
	return flagEnabled('horosa.perf.hookRaf');
}

export function freezeInactiveTabsEnabled(){
	return flagEnabled('horosa.perf.freezeInactiveTabs');
}

export function requestDedupeEnabled(){
	return flagEnabled('horosa.perf.requestDedupe');
}

export function techniqueCacheEnabled(){
	return flagEnabled('horosa.perf.techniqueCache');
}

export function idleWarmQueueEnabled(){
	return flagEnabled('horosa.perf.idleWarmQueue');
}
