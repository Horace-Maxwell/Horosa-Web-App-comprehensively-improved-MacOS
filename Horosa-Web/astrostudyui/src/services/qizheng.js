import request from '../utils/request';
import { ServerRoot, ResultKey } from '../utils/constants';
import { buildKentangEndpoint } from '../integrations/kentang/serviceRoot';
import { fetchChartWithRetry } from '../utils/chartFetch';

export function fetchMoiraQizhengRules(values, requestOptions){
	return request(`${ServerRoot}/qizheng/moira`, {
		body: JSON.stringify(values || {}),
		...(requestOptions || {}),
	});
}

export async function fetchKinastroQizheng(values){
	let rsp = null;
	try{
		const response = await fetchChartWithRetry(buildKentangEndpoint('qizhengkin', 'pan'), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json; charset=UTF-8' },
			body: JSON.stringify(values || {}),
		});
		const text = await response.text();
		rsp = text ? JSON.parse(text) : null;
		if(!rsp || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)){
			throw new Error(rsp && rsp[ResultKey] ? `${rsp[ResultKey]}` : 'qizhengkin.local.fetch.failed');
		}
	}catch(e){
		const response = await fetchChartWithRetry(`${ServerRoot}/qizhengkin/pan`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json; charset=UTF-8' },
			body: JSON.stringify(values || {}),
		});
		const text = await response.text();
		rsp = text ? JSON.parse(text) : null;
	}
	if(!rsp || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)){
		throw new Error(rsp && rsp[ResultKey] ? `${rsp[ResultKey]}` : 'qizhengkin.fetch.failed');
	}
	return rsp && rsp[ResultKey] ? rsp[ResultKey] : rsp;
}
