// 页面状态小件:签名比较、深拷贝、起课缓存与排盘设置跨会话保留
// 从 JinKouMain.js 按职责拆出(门面保留原导入路径与对外导出;读源码的检查读「子模块 + 门面」全集,见 scripts/source-sets.json)。
import { definePageSettings } from '../../../utils/pageSettingsStore';

// 签名数组逐元素严格相等(引用/值);用于装配缓存命中判定(只多算、绝不少算)。
export function sameSigArr(a, b){
	if(!a || !b || a.length !== b.length){
		return false;
	}
	for(let i = 0; i < a.length; i++){
		if(a[i] !== b[i]){
			return false;
		}
	}
	return true;
}

export function clonePlain(obj){
	if(obj === undefined || obj === null){
		return obj;
	}
	try{
		return JSON.parse(JSON.stringify(obj));
	}catch(e){
		return obj;
	}
}

export function buildCacheKey(obj){
	try{
		return JSON.stringify(obj || {});
	}catch(e){
		return '';
	}
}

export function pushCache(map, key, val, max = 96){
	if(!map || !key || val === undefined || val === null){
		return;
	}
	if(map.has(key)){
		map.delete(key);
	}
	map.set(key, val);
	if(map.size > max){
		const first = map.keys().next().value;
		if(first){
			map.delete(first);
		}
	}
}

// 排盘设置跨会话保留(用户实报:排盘设置改了之后每次重开软件都要重设)。只收排盘流派五键 + 时间基准;
// 地分 / 月将 / 占时 / 专题 / 扣题 / 时段是每一课的输入,十二长生五行缺省随日干,都不进。事盘回灌不经这两个 handler,不落盘。
export const JINKOU_PAGE_SETTINGS = definePageSettings('horosa.jinkou.settings.v1', {
	schoolYueJiang: { def: 'zhongqi', oneOf: ['zhongqi', 'jiaojie'] },
	schoolGuiTable: { def: 'shiwu', oneOf: ['shiwu', 'liuren'] },
	schoolGuiPan: { def: 'di', oneOf: ['di', 'tian'] },
	panShi: { def: 'yang', oneOf: ['yang', 'yin'] },
	soilChangSheng: { def: 'shen', oneOf: ['shen', 'yin'] },
	timeBasis: { def: 'direct', oneOf: ['direct', 'trueSolar'] },
});
