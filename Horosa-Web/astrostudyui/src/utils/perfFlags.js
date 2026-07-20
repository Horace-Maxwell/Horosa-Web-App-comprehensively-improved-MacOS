import { safeLocalStorageSet } from './safeStorage';
// perfFlags.js —— 流畅度优化项的独立开关(默认全开,调用时读取)。
//
// 每项优化只动「时机/调度」不动「内容/语义」,但仍各配 kill-switch:现场发现异常时
// 单项关闭立即回到旧行为,无需回滚代码。关闭方法(控制台执行后刷新):
//   safeLocalStorageSet('horosa.perf.lazySnapshot', '0')   // 快照惰性构建
//   safeLocalStorageSet('horosa.perf.ziweiRulesCache', '0')// 紫微 rules 会话缓存
//   safeLocalStorageSet('horosa.perf.chartDrawGuard', '0') // 图面重绘签名守卫
//   safeLocalStorageSet('horosa.perf.chartSCU', '0')       // 盘面重组件 shouldComponentUpdate
//   safeLocalStorageSet('horosa.perf.hookRaf', '0')        // 排盘 hook rAF 化
//   safeLocalStorageSet('horosa.perf.freezeInactiveTabs','0')// 冻结非激活 TabPane 重渲
//   safeLocalStorageSet('horosa.perf.requestDedupe', '0')  // 计算请求 去重+短TTL缓存
//   safeLocalStorageSet('horosa.perf.techniqueCache', '0') // L2 技法结果缓存(10min,来回拨参数≈0)
//   safeLocalStorageSet('horosa.perf.idleWarmQueue', '0')  // 就绪后空闲预热队列(chunk/引擎/数据)
//   —— 以下九项为「点时间→出盘极速化」大修(2026-07) ——
//   safeLocalStorageSet('horosa.perf.fieldsFastCommit', '0')      // chartFree 页 fields 先行提交(快车道)
//   safeLocalStorageSet('horosa.perf.prewarmRequests', '0')       // 非快车道页并行预热请求集
//   safeLocalStorageSet('horosa.perf.silentTechniquePanels', '0') // 技法面板请求 silent+keep-stale(关=旧全屏 Spin)
//   safeLocalStorageSet('horosa.perf.ziweiLocalFirst', '0')       // 紫微默认本地引擎(关=旧 Java 默认)
//   safeLocalStorageSet('horosa.perf.leadingDebounce', '0')       // 主盘时间防抖 leading 立发(关=纯 trailing 180ms)
//   safeLocalStorageSet('horosa.perf.sharedNativeModel', '0')     // native 技法 center/aux 共享模型 memo
//   safeLocalStorageSet('horosa.perf.singleTriggerPredictive','0')// PD/ZR hook+didUpdate 同签名去重
//   safeLocalStorageSet('horosa.perf.stepPrefetch', '0')          // 时间步进方向预取
//   safeLocalStorageSet('horosa.perf.chartCloneLite', '0')        // 出盘缓存冻结共享引用(关=每次深拷贝)
//   safeLocalStorageSet('horosa.perf.hoverPrefetch', '0')         // 导航悬停预取 chunk(关=点击才载)
//   safeLocalStorageSet('horosa.perf.netResultCache', '0')        // 请求结果 L3 持久缓存(IndexedDB,跨重启 0 往返)
//   safeLocalStorageSet('horosa.perf.bootGate', '0')              // [B1] early 导航后端探活门(关=请求直发,未起时报错重试)
//   safeLocalStorageSet('horosa.perf.rsaSessionKey', '0')         // [A2] RSA 会话密钥复用(关=每请求重算 2048 位模幂)
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

// [A1] L3 持久结果缓存(IndexedDB):同参跨会话零网络零 RSA。默认开;置 '0' 一键回退到纯内存 L1/L2。
export function netResultCacheEnabled(){
	return flagEnabled('horosa.perf.netResultCache');
}

export function idleWarmQueueEnabled(){
	return flagEnabled('horosa.perf.idleWarmQueue');
}

// —— 「点时间→出盘极速化」大修(2026-07) 九开关 ——
// 与既有开关同则:默认开、只动时机/调度不动内容语义、单项关闭即回旧行为。

export function fieldsFastCommitEnabled(){
	return flagEnabled('horosa.perf.fieldsFastCommit');
}

export function prewarmRequestsEnabled(){
	return flagEnabled('horosa.perf.prewarmRequests');
}

export function silentTechniquePanelsEnabled(){
	return flagEnabled('horosa.perf.silentTechniquePanels');
}

export function ziweiLocalFirstEnabled(){
	// ⚠️ 本开关是【opt-in】(缺省=关),与其余默认开的开关相反。
	//    2026-07-19:24 例网格对拍已【全绿】(Java 兼容档三键 yearBoundary:lunar_1_1 /
	//    ziweiLunarBasis:calendar / lifeMasterBy:year_branch,见 ziweiLocalParity.test)=
	//    排盘核心字节证明达成;但「切默认」还差【全响应形状】装配审计(nongli 文本/bazi 块/
	//    顶层兼容字段的本地组装逐字对拍)——审计过前本开关保持 opt-in 且暂无消费者(荷载待接线)。
	try{
		if(typeof window !== 'undefined' && window.localStorage){
			return window.localStorage.getItem('horosa.perf.ziweiLocalFirst') === '1';
		}
	}catch(e){ /* 默认关 */ }
	return false;
}

export function leadingDebounceEnabled(){
	return flagEnabled('horosa.perf.leadingDebounce');
}

export function bootGateEnabled(){
	// [B1] 桌面壳 early 导航(前后端启动重叠)时,请求层按目标根探活排队;
	// 关=请求直发(后端未起时走既有报错/重试/离线横幅,行为回到旧序)。
	return flagEnabled('horosa.perf.bootGate');
}

export function rsaSessionKeyEnabled(){
	// [A2] :9999 请求体加密的 AES 钥+RSA 密文会话内复用(每会话一次 2048 位模幂,
	// 旧式=每请求一次、主线程)。关=逐请求随机钥(字节行为回旧)。Java 侧零改动。
	return flagEnabled('horosa.perf.rsaSessionKey');
}

export function aiBodyEncryptEnabled(){
	// [G2] :9999 AI 分析请求体 RSA 会话束封套(与排盘 API 同机制)。关=回明文请求体
	// (后端有明文直通宽容,恒可回退);响应两态皆不加密。
	return flagEnabled('horosa.sec.aiBodyEncrypt');
}

export function sharedNativeModelEnabled(){
	return flagEnabled('horosa.perf.sharedNativeModel');
}

export function singleTriggerPredictiveEnabled(){
	return flagEnabled('horosa.perf.singleTriggerPredictive');
}

export function stepPrefetchEnabled(){
	return flagEnabled('horosa.perf.stepPrefetch');
}

export function chartCloneLiteEnabled(){
	return flagEnabled('horosa.perf.chartCloneLite');
}

// —— WS-N3(2026-07-16):导航悬停预取 ——
export function hoverPrefetchEnabled(){
	return flagEnabled('horosa.perf.hoverPrefetch');
}

// —— 3D 星盘大修 WS-0(2026-07-16) ——
export function astro3dOnDemandEnabled(){
	// 按需渲染:idle 停 rAF(交互/动画/参数变化时唤醒);关=旧持续 rAF 全速渲染
	return flagEnabled('horosa.perf.astro3dOnDemand');
}

// —— 3D 星盘大修 WS-1(2026-07-16) ——
export function astro3dSpriteLabelsEnabled(){
	// 标签走 canvas sprite(每标签 1 quad,billboard 恒可读);关=旧 TextGeometry 网格观感
	return flagEnabled('horosa.perf.astro3dSpriteLabels');
}

// —— 3D 星盘大修 WS-1b(2026-07-16) ——
export function astro3dMorphEnabled(){
	// 改时间滑移补间:仅 chartObj 变化(坐标语义/显示集合未变)时行星沿最短弧 tween 滑到
	// 新位(~600ms),不走全量重建;关=旧全量 disposeMesh+重建
	return flagEnabled('horosa.perf.astro3dMorph');
}
