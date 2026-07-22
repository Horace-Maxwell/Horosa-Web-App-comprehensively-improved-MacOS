// 玄史(中国玄学史)模块取数 —— 走 kentang :8899 直连(buildKentangEndpoint),失败回退 ServerRoot。
// 后端 webxuanshisrv 返回 jsonpickle 原始 dict(无 ResultCode 包裹,错误回 {err:...})。
import { ServerRoot } from '../utils/constants';
import { buildKentangEndpoint } from '../integrations/kentang/serviceRoot';
import { cachedKentangFetch } from '../utils/kentangCache';

const _requestCache = {};

async function _post(action, payload) {
	const body = JSON.stringify(payload || {});
	const headers = { 'Content-Type': 'application/json; charset=UTF-8' };
	let rsp = null;
	try {
		const r = await cachedKentangFetch(buildKentangEndpoint('xuanshi', action), { method: 'POST', headers, body }, { retries: 0 });
		const t = await r.text();
		rsp = t ? JSON.parse(t) : null;
		if (!rsp || rsp.err || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)) {
			throw new Error(rsp && rsp.err ? `${rsp.err}` : 'xuanshi.local.fetch.failed');
		}
	} catch (e) {
		const r = await cachedKentangFetch(`${ServerRoot}/xuanshi/${action}`, { method: 'POST', headers, body }, { retries: 0 });
		const t = await r.text();
		rsp = t ? JSON.parse(t) : null;
	}
	if (!rsp || rsp.err || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)) {
		throw new Error(rsp && rsp.err ? `${rsp.err}` : 'xuanshi.fetch.failed');
	}
	return rsp;
}

// 通用 POST(不缓存)
export function postXuanShi(action, payload) {
	return _post(action, payload);
}

// 幂等只读端点缓存(同 action+payload 复用)
export async function postXuanShiCached(action, payload) {
	const key = `${action}:${JSON.stringify(payload || {})}`;
	if (_requestCache[key]) { return _requestCache[key]; }
	const res = await _post(action, payload);
	_requestCache[key] = res;
	return res;
}

export function clearXuanShiCache() {
	Object.keys(_requestCache).forEach((k) => { delete _requestCache[k]; });
}

// —— 便捷端点（与 webxuanshisrv 端点一一对应）——
export const fetchSummary = () => postXuanShiCached('summary', {});
export const fetchEvents = (p) => postXuanShi('events', p);
export const fetchEvent = (event_id) => postXuanShiCached('event', { event_id });
export const fetchCelestial = (p) => postXuanShi('celestial', p);
export const fetchCelestialEvent = (event_id) => postXuanShiCached('celestial_event', { event_id });
export const fetchDecadeOmens = (p) => postXuanShiCached('decade_omens', p || {});
export const fetchMicrochronology = (p) => postXuanShi('microchronology', p);
export const fetchFigures = (p) => postXuanShi('figures', p);
export const fetchFigure = (slug) => postXuanShiCached('figure', { slug });
export const fetchTechniques = (p) => postXuanShiCached('techniques', p || {});
export const fetchTechnique = (slug) => postXuanShiCached('technique', { slug });
export const fetchCelestialTerms = () => postXuanShiCached('celestial-terms', {});
export const fetchCelestialTerm = (slug) => postXuanShiCached('celestial-term', { slug });
export const fetchDynasties = () => postXuanShiCached('dynasties', {});
export const fetchDynasty = (slug) => postXuanShiCached('dynasty', { slug });
export const fetchStories = (p) => postXuanShi('stories', p || {});
export const fetchStory = (slug) => postXuanShiCached('story', { slug });
export const fetchChannels = () => postXuanShiCached('channels', {});
export const fetchMap = (period) => postXuanShi('map', { period });
export const fetchPersonsGraph = (p) => postXuanShi('persons-graph', p || {});
export const fetchTimeline = (p) => postXuanShi('timeline', p || {});
export const fetchSearch = (p) => postXuanShi('search', p);
export const fetchFacets = (p) => postXuanShi('facets', p || {});
export const fetchEventsMeta = (tradition) => postXuanShiCached('events_meta', { tradition: tradition || '' });
export const fetchDaily = (date) => postXuanShi('daily', { date });
