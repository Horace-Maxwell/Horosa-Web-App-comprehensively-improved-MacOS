// 输入签名记忆化(本地纯函数引擎用):同签名直接复用结果,小容量 LRU 防增长。
// 适用前提:被包函数为纯函数(同输入同输出、结果不被调用方原地改写——若调用方会
// spread/改写,请在调用侧浅拷或提高槽位谨慎评估)。
// kill-switch:localStorage horosa.perf.localEngineMemo = '0' 关闭(默认开,perfFlags 同款约定)。
export function memoEnabled(){
	try{
		if(typeof window !== 'undefined' && window.localStorage){
			return window.localStorage.getItem('horosa.perf.localEngineMemo') !== '0';
		}
	}catch(e){ /* 按默认开 */ }
	return true;
}

// 创建带签名的 LRU 记忆器。slots 默认 8(WS-3b 4→8:覆盖「多设置来回拨」——
// 流派×开关组合常超 4 个;条目是本地引擎结果对象,8 槽内存增量可忽略)。
export function createSignatureMemo(slots){
	const cap = Math.max(1, slots || 8);
	const map = new Map(); // Map 迭代序=插入序,充当 LRU
	return {
		get(key){
			if(!memoEnabled() || !map.has(key)) return undefined;
			const v = map.get(key);
			map.delete(key); map.set(key, v); // 触摸置新
			return v;
		},
		set(key, value){
			if(!memoEnabled()) return value;
			if(map.has(key)) map.delete(key);
			map.set(key, value);
			if(map.size > cap){ map.delete(map.keys().next().value); }
			return value;
		},
		clear(){ map.clear(); },
	};
}

// 稳定签名:对普通对象按键排序序列化(浅层顺序无关);数组/标量原样。
export function stableSignature(...parts){
	const norm = (v) => {
		if(v === null || v === undefined) return String(v);
		if(typeof v !== 'object') return String(v);
		if(Array.isArray(v)) return '[' + v.map(norm).join(',') + ']';
		return '{' + Object.keys(v).sort().map((k) => k + ':' + norm(v[k])).join(',') + '}';
	};
	return parts.map(norm).join('|');
}

export default createSignatureMemo;
