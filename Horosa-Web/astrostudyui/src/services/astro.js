import request from '../utils/request';
import { ServerRoot } from '../utils/constants';

const CHART_CACHE_MAX = 96;
const chartMem = new Map();
const chartInflight = new Map();

function clonePlain(obj){
	if(obj === undefined || obj === null){
		return obj;
	}
	try{
		return JSON.parse(JSON.stringify(obj));
	}catch(e){
		return obj;
	}
}

function pushCache(map, key, val){
	if(!key || val === undefined || val === null){
		return;
	}
	if(map.has(key)){
		map.delete(key);
	}
	map.set(key, val);
	if(map.size > CHART_CACHE_MAX){
		const first = map.keys().next().value;
		if(first){
			map.delete(first);
		}
	}
}

function buildChartKey(values){
	try{
		return JSON.stringify(values || {});
	}catch(e){
		return '';
	}
}

export function fetchChart(values, requestOptions){
	const opts = requestOptions || {};
	const disableCache = opts.cache === false;
	const key = disableCache ? '' : buildChartKey(values);
	if(key && chartMem.has(key)){
		return Promise.resolve(clonePlain(chartMem.get(key)));
	}
	if(key && chartInflight.has(key)){
		return chartInflight.get(key).then((rsp)=>clonePlain(rsp));
	}
	const req = request(`${ServerRoot}/chart`, {
		body: JSON.stringify(values),
		...opts,
	}).then((rsp)=>{
		if(key && rsp){
			pushCache(chartMem, key, clonePlain(rsp));
		}
		return rsp;
	}).finally(()=>{
		if(key){
			chartInflight.delete(key);
		}
	});
	if(key){
		chartInflight.set(key, req);
	}
	return req.then((rsp)=>clonePlain(rsp));
}

export function fetchAllowedCharts(values){
    return request(`${ServerRoot}/allowedcharts`, {
        body: JSON.stringify(values),
    });
}

export function fetchFateEvents(values){
    return request(`${ServerRoot}/deeplearn/fateevents`, {
        body: JSON.stringify(values),
    });
}

export function dlTrain(values){
    return request(`${ServerRoot}/deeplearn/train`, {
        body: JSON.stringify(values),
    });
}

