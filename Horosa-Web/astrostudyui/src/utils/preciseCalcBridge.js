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
const JIE_QI_YEAR_KEYS = ['year', 'ad', 'zone', 'lon', 'lat', 'gpsLat', 'gpsLon', 'timeAlg', 'hsys', 'zodiacal', 'doubingSu28', 'jieqis', 'seedOnly', 'needBazi', 'needCharts'];
const MAX_CACHE_SIZE = 192;
const DEFAULT_SEED_TERMS = ['大雪', '芒种'];
const PRECISE_REQ_TIMEOUT_MS = 45000;

const nongliMem = new Map();
const nongliInflight = new Map();
const jieqiYearMem = new Map();
const jieqiYearInflight = new Map();
const jieqiSeedMem = new Map();
const jieqiSeedInflight = new Map();

function safe(v, d = ''){
	return v === undefined || v === null ? d : `${v}`;
}

function parseZoneHour(zone){
	const text = safe(zone).trim();
	if(!text){
		return null;
	}
	const mStd = text.match(/^([+-])(\d{1,2})(?::?(\d{2}))?$/);
	if(mStd){
		const sign = mStd[1] === '-' ? -1 : 1;
		const hh = parseInt(mStd[2], 10);
		const mm = parseInt(mStd[3] || '0', 10);
		if(!Number.isNaN(hh) && !Number.isNaN(mm)){
			return sign * (hh + mm / 60);
		}
	}
	const mUtc = text.match(/^(?:UTC|GMT)\s*([+-])(\d{1,2})(?::?(\d{2}))?$/i);
	if(mUtc){
		const sign = mUtc[1] === '-' ? -1 : 1;
		const hh = parseInt(mUtc[2], 10);
		const mm = parseInt(mUtc[3] || '0', 10);
		if(!Number.isNaN(hh) && !Number.isNaN(mm)){
			return sign * (hh + mm / 60);
		}
	}
	const mCn = text.match(/^([东西])\s*(\d{1,2})(?:[:：]?(\d{1,2}))?\s*区?$/);
	if(mCn){
		const sign = mCn[1] === '西' ? -1 : 1;
		const hh = parseInt(mCn[2], 10);
		const mm = parseInt(mCn[3] || '0', 10);
		if(!Number.isNaN(hh) && !Number.isNaN(mm)){
			return sign * (hh + mm / 60);
		}
	}
	const numeric = Number(text);
	if(Number.isFinite(numeric)){
		return numeric;
	}
	return null;
}

function formatZoneHour(hour){
	if(hour === null || hour === undefined || Number.isNaN(hour)){
		return '+08:00';
	}
	const sign = hour < 0 ? '-' : '+';
	const abs = Math.abs(hour);
	let hh = Math.floor(abs);
	let mm = Math.round((abs - hh) * 60);
	if(mm >= 60){
		hh += 1;
		mm -= 60;
	}
	return `${sign}${`${hh}`.padStart(2, '0')}:${`${mm}`.padStart(2, '0')}`;
}

function normalizeZone(zone, fallback = '+08:00'){
	const parsed = parseZoneHour(zone);
	if(parsed !== null && !Number.isNaN(parsed)){
		return formatZoneHour(parsed);
	}
	const fb = parseZoneHour(fallback);
	return formatZoneHour((fb !== null && !Number.isNaN(fb)) ? fb : 8);
}

function normalizeAd(ad, date){
	const text = safe(ad).trim().toUpperCase();
	if(text === 'BC' || text === 'BCE'){
		return -1;
	}
	if(text === 'AD' || text === 'CE'){
		return 1;
	}
	if(text){
		const n = parseInt(text, 10);
		if(!Number.isNaN(n) && n !== 0){
			return n > 0 ? 1 : -1;
		}
	}
	const dateText = safe(date).trim();
	return dateText.startsWith('-') ? -1 : 1;
}

function normalizeBit(value, def = 0){
	if(value === undefined || value === null || value === ''){
		return def === 1 ? 1 : 0;
	}
	if(value === true){
		return 1;
	}
	if(value === false){
		return 0;
	}
	const text = safe(value).trim().toLowerCase();
	if(text === '1' || text === 'true' || text === 'yes'){
		return 1;
	}
	return 0;
}

function normalizeNongliParams(params){
	const src = params || {};
	return {
		...src,
		zone: normalizeZone(src.zone, '+08:00'),
		ad: normalizeAd(src.ad, src.date),
		timeAlg: normalizeBit(src.timeAlg, 0),
		after23NewDay: normalizeBit(src.after23NewDay, 0),
	};
}

function normalizeJieqiParams(params){
	const src = params || {};
	return {
		...src,
		zone: normalizeZone(src.zone, '+08:00'),
		ad: normalizeAd(src.ad),
		timeAlg: normalizeBit(src.timeAlg, 0),
	};
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
	const reqParams = normalizeNongliParams(params);
	const key = buildKey(reqParams, NONG_LI_KEYS);
	if(key && nongliMem.has(key)){
		return nongliMem.get(key);
	}
	const localHit = getNongliLocalCache(reqParams);
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
				body: JSON.stringify(reqParams),
				silent: true,
				timeoutMs: PRECISE_REQ_TIMEOUT_MS,
			});
			const result = rsp && rsp[ResultKey] ? rsp[ResultKey] : null;
			if(result){
				pushCache(nongliMem, key, result);
				setNongliLocalCache(reqParams, result);
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
	const reqParams = normalizeJieqiParams(params);
	const key = buildKey(reqParams, JIE_QI_YEAR_KEYS);
	if(key && jieqiYearMem.has(key)){
		return jieqiYearMem.get(key);
	}
	if(key && jieqiYearInflight.has(key)){
		return jieqiYearInflight.get(key);
	}
	const req = (async()=>{
		try{
			const rsp = await request(`${ServerRoot}/jieqi/year`, {
				body: JSON.stringify(reqParams),
				silent: true,
				timeoutMs: PRECISE_REQ_TIMEOUT_MS,
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
	const reqParams = buildJieqiSeedRequestParams(normalizeJieqiParams(params));
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
