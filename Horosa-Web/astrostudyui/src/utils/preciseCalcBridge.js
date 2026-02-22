import request from './request';
import { ServerRoot, ResultKey } from './constants';
import {
	getNongliLocalCache,
	setNongliLocalCache,
	getJieqiSeedLocalCache,
	setJieqiSeedLocalCache,
} from './localCalcCache';

const NONG_LI_KEYS = ['date', 'time', 'zone', 'lon', 'lat', 'gpsLat', 'gpsLon', 'ad', 'gender', 'after23NewDay', 'timeAlg'];
const JIE_QI_SEED_KEYS = ['year', 'ad', 'zone', 'lon', 'lat', 'gpsLat', 'gpsLon', 'timeAlg', 'jieqis', 'seedOnly'];
const JIE_QI_YEAR_KEYS = ['year', 'ad', 'zone', 'lon', 'lat', 'gpsLat', 'gpsLon', 'timeAlg', 'hsys', 'zodiacal', 'doubingSu28', 'jieqis', 'seedOnly'];
const MAX_CACHE_SIZE = 192;
const DEFAULT_SEED_TERMS = ['大雪', '芒种'];

const nongliMem = new Map();
const nongliInflight = new Map();
const jieqiYearMem = new Map();
const jieqiYearInflight = new Map();
const jieqiSeedMem = new Map();
const jieqiSeedInflight = new Map();

function safe(v, d = ''){
	return v === undefined || v === null ? d : `${v}`;
}

function pushCache(cacheMap, key, val){
	if(!key || val === undefined || val === null){
		return;
	}
	if(cacheMap.has(key)){
		cacheMap.delete(key);
	}
	cacheMap.set(key, val);
	if(cacheMap.size > MAX_CACHE_SIZE){
		const first = cacheMap.keys().next().value;
		if(first){
			cacheMap.delete(first);
		}
	}
}

function buildKey(params, keys){
	return keys.map((k)=>{
		if(k === 'jieqis'){
			const list = params && Array.isArray(params.jieqis) ? params.jieqis : [];
			return list.join(',');
		}
		return safe(params && params[k]);
	}).join('|');
}

function toDateKey(time){
	const txt = safe(time);
	if(!txt){
		return '';
	}
	const date = txt.split(' ')[0] || '';
	return date.replace(/-/g, '');
}

function normalizeDayGanzhi(entry){
	const bazi = entry && entry.bazi ? entry.bazi : null;
	const four = bazi && bazi.fourColumns ? bazi.fourColumns : null;
	const day = four && four.day ? four.day : null;
	return safe(day && day.ganzi);
}

function normalizeSeedTerms(params){
	const terms = params && Array.isArray(params.jieqis) ? params.jieqis : DEFAULT_SEED_TERMS;
	const uniq = [];
	terms.forEach((term)=>{
		const t = safe(term);
		if(t && uniq.indexOf(t) < 0){
			uniq.push(t);
		}
	});
	if(!uniq.length){
		return [...DEFAULT_SEED_TERMS];
	}
	return uniq;
}

function buildJieqiSeedRequestParams(params){
	const terms = normalizeSeedTerms(params);
	return {
		...(params || {}),
		jieqis: terms,
		seedOnly: true,
	};
}

function hasSeedTerms(seed, terms){
	if(!seed || !Array.isArray(terms) || !terms.length){
		return false;
	}
	for(let i=0; i<terms.length; i++){
		if(!seed[terms[i]]){
			return false;
		}
	}
	return true;
}

export async function fetchPreciseNongli(params){
	const key = buildKey(params, NONG_LI_KEYS);
	if(key && nongliMem.has(key)){
		return nongliMem.get(key);
	}
	const localHit = getNongliLocalCache(params);
	if(localHit){
		if(key){
			pushCache(nongliMem, key, localHit);
		}
		return localHit;
	}
	if(key && nongliInflight.has(key)){
		return nongliInflight.get(key);
	}
	const req = (async()=>{
		try{
			const rsp = await request(`${ServerRoot}/nongli/time`, {
				body: JSON.stringify(params),
				silent: true,
			});
			const result = rsp && rsp[ResultKey] ? rsp[ResultKey] : null;
			if(result){
				pushCache(nongliMem, key, result);
				setNongliLocalCache(params, result);
			}
			return result;
		}catch(e){
			return null;
		}
	})().finally(()=>{
		if(key){
			nongliInflight.delete(key);
		}
	});
	if(key){
		nongliInflight.set(key, req);
	}
	return req;
}

export async function fetchPreciseJieqiYear(params){
	const key = buildKey(params, JIE_QI_YEAR_KEYS);
	if(key && jieqiYearMem.has(key)){
		return jieqiYearMem.get(key);
	}
	if(key && jieqiYearInflight.has(key)){
		return jieqiYearInflight.get(key);
	}
	const req = (async()=>{
		try{
			const rsp = await request(`${ServerRoot}/jieqi/year`, {
				body: JSON.stringify(params),
				silent: true,
			});
			const result = rsp && rsp[ResultKey] ? rsp[ResultKey] : null;
			if(result){
				pushCache(jieqiYearMem, key, result);
			}
			return result;
		}catch(e){
			return null;
		}
	})().finally(()=>{
		if(key){
			jieqiYearInflight.delete(key);
		}
	});
	if(key){
		jieqiYearInflight.set(key, req);
	}
	return req;
}

export async function fetchPreciseJieqiSeed(params){
	const reqParams = buildJieqiSeedRequestParams(params);
	const requiredTerms = reqParams.jieqis;
	const key = buildKey(reqParams, JIE_QI_SEED_KEYS);
	if(key && jieqiSeedMem.has(key)){
		const memHit = jieqiSeedMem.get(key);
		if(hasSeedTerms(memHit, requiredTerms)){
			return memHit;
		}
	}
	const localHit = getJieqiSeedLocalCache(reqParams);
	if(hasSeedTerms(localHit, requiredTerms)){
		if(key){
			pushCache(jieqiSeedMem, key, localHit);
		}
		return localHit;
	}
	if(key && jieqiSeedInflight.has(key)){
		return jieqiSeedInflight.get(key);
	}
	const req = (async()=>{
		const yearRes = await fetchPreciseJieqiYear(reqParams);
		if(!yearRes || !Array.isArray(yearRes.jieqi24)){
			return null;
		}
		const seed = {};
		yearRes.jieqi24.forEach((entry)=>{
			const term = safe(entry && entry.jieqi);
			if(!term){
				return;
			}
			const time = safe(entry && entry.time);
			seed[term] = {
				term,
				time,
				dateKey: toDateKey(time),
				dayGanzhi: normalizeDayGanzhi(entry),
			};
		});
		const result = Object.keys(seed).length ? seed : null;
		if(result && hasSeedTerms(result, requiredTerms)){
			pushCache(jieqiSeedMem, key, result);
			setJieqiSeedLocalCache(reqParams, result);
			return result;
		}
		return null;
	})().finally(()=>{
		if(key){
			jieqiSeedInflight.delete(key);
		}
	});
	if(key){
		jieqiSeedInflight.set(key, req);
	}
	return req;
}
