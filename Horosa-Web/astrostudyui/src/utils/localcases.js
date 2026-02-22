const LocalCasesKey = 'horosa.localCases.v1';
const AstroAiSnapshotKey = 'horosa.ai.snapshot.astro.v1';
const ModuleAiSnapshotPrefix = 'horosa.ai.snapshot.module.v1.';
let fallbackToMemoryStore = false;
let fallbackWarned = false;
let memoryCases = [];

function getLocalStorage(){
	try{
		if(typeof window !== 'undefined' && window.localStorage){
			return window.localStorage;
		}
		if(typeof localStorage !== 'undefined'){
			return localStorage;
		}
	}catch(e){
		return null;
	}
	return null;
}

function warnMemoryFallback(){
	if(fallbackWarned){
		return;
	}
	fallbackWarned = true;
	if(typeof console !== 'undefined' && console && typeof console.warn === 'function'){
		console.warn('[horosa] localStorage unavailable, case data falls back to memory for this session.');
	}
}

function enableMemoryFallback(){
	fallbackToMemoryStore = true;
	warnMemoryFallback();
}

function isQuotaError(err){
	if(!err){
		return false;
	}
	const name = `${err.name || ''}`;
	const code = Number(err.code || 0);
	const message = `${err.message || ''}`.toLowerCase();
	if(code === 22 || code === 1014){
		return true;
	}
	if(name === 'QuotaExceededError' || name === 'NS_ERROR_DOM_QUOTA_REACHED'){
		return true;
	}
	return message.indexOf('quota') >= 0;
}

function purgeHeavyLocalCache(){
	const storage = getLocalStorage();
	if(!storage){
		return;
	}
	try{
		storage.removeItem(AstroAiSnapshotKey);
	}catch(e){
		// ignore
	}
	const keys = [];
	try{
		for(let i=0; i<storage.length; i++){
			const key = storage.key(i);
			if(key && key.indexOf(ModuleAiSnapshotPrefix) === 0){
				keys.push(key);
			}
		}
	}catch(e){
		return;
	}
	keys.forEach((key)=>{
		try{
			storage.removeItem(key);
		}catch(e){
			// ignore
		}
	});
}

export const CASE_TYPE_OPTIONS = [
	{ value: 'liuyao', label: '六爻', subTab: 'guazhan', module: 'guazhan' },
	{ value: 'liureng', label: '六壬', subTab: 'liureng', module: 'liureng' },
	{ value: 'jinkou', label: '金口诀', subTab: 'jinkou', module: 'jinkou' },
	{ value: 'taiyi', label: '太乙', subTab: 'taiyi', module: 'taiyi' },
	{ value: 'qimen', label: '奇门', subTab: 'dunjia', module: 'qimen' },
	{ value: 'sanshiunited', label: '三式合一', subTab: null, tab: 'sanshiunited', module: 'sanshiunited' },
];

function safeParseJson(txt, defVal){
	if(!txt){
		return defVal;
	}
	try{
		return JSON.parse(txt);
	}catch(e){
		return defVal;
	}
}

function nowStr(){
	const dt = new Date();
	const y = dt.getFullYear();
	const m = String(dt.getMonth() + 1).padStart(2, '0');
	const d = String(dt.getDate()).padStart(2, '0');
	const hh = String(dt.getHours()).padStart(2, '0');
	const mm = String(dt.getMinutes()).padStart(2, '0');
	const ss = String(dt.getSeconds()).padStart(2, '0');
	return `${y}-${m}-${d} ${hh}:${mm}:${ss}`;
}

function normalizeGroup(group){
	if(group === undefined || group === null || group === ''){
		return null;
	}
	if(group instanceof Array){
		return JSON.stringify(group);
	}
	if(typeof group === 'string'){
		const parsed = safeParseJson(group, null);
		if(parsed instanceof Array){
			return JSON.stringify(parsed);
		}
		return group;
	}
	return JSON.stringify([group]);
}

function normalizeCaseType(type){
	const val = `${type || ''}`.trim();
	if(val === '六爻'){
		return 'liuyao';
	}
	if(val === '六壬'){
		return 'liureng';
	}
	if(val === '金口诀'){
		return 'jinkou';
	}
	if(val === '太乙'){
		return 'taiyi';
	}
	if(val === '奇门' || val === '遁甲'){
		return 'qimen';
	}
	if(val === '三式合一'){
		return 'sanshiunited';
	}
	if(CASE_TYPE_OPTIONS.find((item)=>item.value === val)){
		return val;
	}
	return 'liuyao';
}

export function getCaseTypeLabel(type){
	const one = CASE_TYPE_OPTIONS.find((item)=>item.value === normalizeCaseType(type));
	return one ? one.label : '六爻';
}

export function getCaseTypeMeta(type){
	const one = CASE_TYPE_OPTIONS.find((item)=>item.value === normalizeCaseType(type));
	return one || CASE_TYPE_OPTIONS[0];
}

function sortByUpdateTimeDesc(list){
	return list.sort((a, b)=>{
		const ta = Date.parse(a.updateTime || '') || 0;
		const tb = Date.parse(b.updateTime || '') || 0;
		return tb - ta;
	});
}

function readRawCases(){
	if(fallbackToMemoryStore){
		return memoryCases.slice();
	}
	const storage = getLocalStorage();
	if(!storage){
		enableMemoryFallback();
		return memoryCases.slice();
	}
	let raw = null;
	try{
		raw = storage.getItem(LocalCasesKey);
	}catch(e){
		enableMemoryFallback();
		return memoryCases.slice();
	}
	const ary = safeParseJson(raw, []);
	if(!(ary instanceof Array)){
		return [];
	}
	memoryCases = ary.slice();
	return ary;
}

function writeRawCases(list){
	const next = list instanceof Array ? list.slice() : [];
	memoryCases = next;
	if(fallbackToMemoryStore){
		return true;
	}
	const storage = getLocalStorage();
	if(!storage){
		enableMemoryFallback();
		return true;
	}
	const text = JSON.stringify(next);
	try{
		storage.setItem(LocalCasesKey, text);
		return true;
	}catch(e){
		if(isQuotaError(e)){
			purgeHeavyLocalCache();
			try{
				storage.setItem(LocalCasesKey, text);
				return true;
			}catch(e2){
				// ignore and fallback below
			}
		}
		enableMemoryFallback();
		return true;
	}
}

export function listLocalCases(filter){
	let list = readRawCases();
	if(filter && filter.name){
		const name = (filter.name + '').trim().toLowerCase();
		if(name !== ''){
			list = list.filter((item)=>{
				const txt = item && item.event ? (item.event + '').toLowerCase() : '';
				return txt.indexOf(name) >= 0;
			});
		}
	}
	if(filter && filter.tag){
		const tag = filter.tag + '';
		if(tag !== ''){
			list = list.filter((item)=>{
				const grp = safeParseJson(item.group, []);
				return grp instanceof Array && grp.indexOf(tag) >= 0;
			});
		}
	}
	return sortByUpdateTimeDesc(list);
}

export function getPagedLocalCases(params){
	const pidx = params && params.PageIndex ? parseInt(params.PageIndex + '', 10) : 1;
	const psz = params && params.PageSize ? parseInt(params.PageSize + '', 10) : 30;
	const list = listLocalCases(params || {});
	const start = (pidx - 1) * psz;
	const end = start + psz;
	return {
		List: list.slice(start, end),
		Total: list.length,
		PageIndex: pidx,
		PageSize: psz,
	};
}

function normalizePayload(payload){
	if(payload === undefined || payload === null){
		return null;
	}
	if(typeof payload === 'string'){
		return payload;
	}
	try{
		return JSON.stringify(payload);
	}catch(e){
		return `${payload}`;
	}
}

export function buildLocalCaseRecord(values){
	const cid = values && values.cid ? values.cid : `local-case-${Date.now()}-${Math.floor(Math.random() * 1000000)}`;
	let divTime = values.divTime;
	if(divTime && typeof divTime.format === 'function'){
		divTime = divTime.format('YYYY-MM-DD HH:mm:ss');
	}
	const record = {
		cid: cid,
		event: values.event ? values.event : '',
		caseType: normalizeCaseType(values.caseType),
		divTime: divTime ? divTime : nowStr(),
		zone: values.zone !== undefined && values.zone !== null ? values.zone : '+08:00',
		lat: values.lat,
		lon: values.lon,
		gpsLat: values.gpsLat,
		gpsLon: values.gpsLon,
		pos: values.pos ? values.pos : '',
		isPub: values.isPub !== undefined && values.isPub !== null ? parseInt(values.isPub + '', 10) : 0,
		group: normalizeGroup(values.group),
		creator: values.creator ? values.creator : 'local',
		updateTime: nowStr(),
		payload: normalizePayload(values.payload),
		sourceModule: values.sourceModule ? values.sourceModule : null,
	};
	return record;
}

export function upsertLocalCase(values){
	const next = buildLocalCaseRecord(values);
	const list = readRawCases();
	const idx = list.findIndex((item)=> item.cid === next.cid);
	if(idx >= 0){
		list[idx] = {
			...list[idx],
			...next,
		};
	}else{
		list.push(next);
	}
	const saved = writeRawCases(sortByUpdateTimeDesc(list));
	if(!saved){
		throw new Error('local.case.save.failed');
	}
	return next;
}

export function removeLocalCase(cid){
	const list = readRawCases();
	const next = list.filter((item)=> item.cid !== cid);
	const saved = writeRawCases(next);
	if(!saved){
		throw new Error('local.case.delete.failed');
	}
}

export function exportLocalCasesBackup(){
	const cases = sortByUpdateTimeDesc(readRawCases().slice());
	return {
		format: 'horosa-local-cases',
		version: 1,
		exportedAt: nowStr(),
		total: cases.length,
		cases: cases,
	};
}

export function importLocalCasesBackup(payload){
	if(!payload || typeof payload !== 'object'){
		return { imported: 0, total: readRawCases().length };
	}
	const incoming = payload.cases;
	if(!(incoming instanceof Array)){
		return { imported: 0, total: readRawCases().length };
	}
	let imported = 0;
	incoming.forEach((item)=>{
		if(!item || typeof item !== 'object'){
			return;
		}
		upsertLocalCase(item);
		imported += 1;
	});
	const total = readRawCases().length;
	return { imported, total };
}
