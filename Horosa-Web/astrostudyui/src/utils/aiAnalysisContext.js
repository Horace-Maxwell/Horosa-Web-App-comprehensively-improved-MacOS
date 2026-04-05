import DateTime from '../components/comp/DateTime';
import { buildAstroSnapshotContent } from './astroAiSnapshot';
import { getCaseTypeLabel, getCaseTypeMeta, listLocalCases } from './localcases';
import { listLocalCharts } from './localcharts';
import { fetchChart } from '../services/astro';
import { AI_ANALYSIS_STORES, getStoreRecord, putStoreRecord } from './aiAnalysisStore';
import { buildRetrievedContextText } from './aiAnalysisRag';

const DEFAULT_PD_ASPECTS = [0, 60, 90, 120, 180];
const DEFAULT_CONTEXT_CHAR_LIMIT = 18000;

function safeParseJson(txt, defVal = null){
	if(!txt){
		return defVal;
	}
	try{
		return JSON.parse(txt);
	}catch(e){
		return defVal;
	}
}

function parseBirthString(text, zone = '+08:00'){
	const raw = `${text || ''}`.trim();
	const matched = raw.match(/^(-?\d+)-(\d{2})-(\d{2})(?:\s+(\d{2}):(\d{2})(?::(\d{2}))?)?$/);
	if(!matched){
		return new DateTime({ zone });
	}
	const yearVal = parseInt(matched[1], 10);
	return new DateTime({
		ad: yearVal < 0 ? -1 : 1,
		year: Math.abs(yearVal),
		month: parseInt(matched[2], 10),
		date: parseInt(matched[3], 10),
		hour: parseInt(matched[4] || '0', 10),
		minute: parseInt(matched[5] || '0', 10),
		second: parseInt(matched[6] || '0', 10),
		zone: zone || '+08:00',
	});
}

function normalizeTags(group){
	const parsed = safeParseJson(group, null);
	if(Array.isArray(parsed)){
		return parsed;
	}
	if(Array.isArray(group)){
		return group;
	}
	if(typeof group === 'string' && group.trim() !== ''){
		return group.split(/[,，\n]/g).map((item)=>`${item || ''}`.trim()).filter(Boolean);
	}
	return [];
}

function buildFieldObject(record){
	const birth = parseBirthString(record.birth, record.zone);
	return {
		cid: { value: record.cid || null },
		ad: { value: birth.ad },
		date: { value: birth.clone().startOf('date') },
		time: { value: birth.clone() },
		zone: { value: record.zone || birth.zone || '+08:00' },
		lat: { value: record.lat || '' },
		lon: { value: record.lon || '' },
		gpsLat: { value: record.gpsLat || 0 },
		gpsLon: { value: record.gpsLon || 0 },
		name: { value: record.name || '' },
		pos: { value: record.pos || '' },
		hsys: { value: record.hsys !== undefined ? record.hsys : 0 },
		zodiacal: { value: record.zodiacal !== undefined ? record.zodiacal : 0 },
		tradition: { value: 0 },
		strongRecption: { value: 0 },
		simpleAsp: { value: 0 },
		virtualPointReceiveAsp: { value: 0 },
		doubingSu28: { value: record.doubingSu28 ? 1 : 0 },
		houseStartMode: { value: 0 },
		predictive: { value: 1 },
		showPdBounds: { value: 1 },
		pdtype: { value: 0 },
		pdMethod: { value: 'astroapp_alchabitius' },
		pdTimeKey: { value: 'Ptolemy' },
		pdaspects: { value: DEFAULT_PD_ASPECTS.slice(0) },
		timeAlg: { value: 0 },
		phaseType: { value: 0 },
		godKeyPos: { value: '年' },
		after23NewDay: { value: 0 },
		adjustJieqi: { value: 0 },
		gender: { value: record.gender !== undefined && record.gender !== null ? record.gender : 1 },
		southchart: { value: 0 },
		group: { value: normalizeTags(record.group) },
	};
}

function fieldParams(fields){
	return {
		cid: null,
		ad: fields.date.value.ad,
		date: fields.date.value.format('YYYY/MM/DD'),
		time: fields.time.value.format('HH:MM:SS'),
		zone: fields.date.value.zone,
		lat: fields.lat.value,
		lon: fields.lon.value,
		gpsLat: fields.gpsLat.value,
		gpsLon: fields.gpsLon.value,
		hsys: fields.hsys.value,
		southchart: fields.southchart.value,
		zodiacal: fields.zodiacal.value,
		tradition: fields.tradition.value,
		doubingSu28: fields.doubingSu28.value,
		strongRecption: fields.strongRecption.value,
		simpleAsp: fields.simpleAsp.value,
		virtualPointReceiveAsp: fields.virtualPointReceiveAsp.value,
		predictive: fields.predictive.value,
		showPdBounds: fields.showPdBounds.value,
		pdtype: fields.pdtype.value,
		pdMethod: fields.pdMethod.value,
		pdTimeKey: fields.pdTimeKey.value,
		pdaspects: fields.pdaspects.value,
		name: fields.name.value,
		pos: fields.pos.value,
		group: fields.group.value,
	};
}

function summarizeCasePayload(record, payload){
	const lines = [];
	const meta = getCaseTypeMeta(record.caseType);
	lines.push(`案例名称：${record.event || '未命名案例'}`);
	lines.push(`案例类型：${getCaseTypeLabel(record.caseType)}`);
	lines.push(`所属模块：${record.sourceModule || meta.module || meta.value || ''}`);
	if(record.divTime){
		lines.push(`占断时间：${record.divTime}`);
	}
	if(record.zone){
		lines.push(`时区：${record.zone}`);
	}
	if(record.pos){
		lines.push(`地点：${record.pos}`);
	}
	const tags = normalizeTags(record.group);
	if(tags.length){
		lines.push(`标签：${tags.join('、')}`);
	}
	lines.push('');
	lines.push('结构化案例数据：');
	lines.push(JSON.stringify(payload || {}, null, 2));
	return lines.join('\n').trim();
}

function extractCaseSnapshotText(record){
	const payload = safeParseJson(record.payload, null);
	if(!payload){
		return {
			content: summarizeCasePayload(record, null),
			payload: null,
			moduleName: record.sourceModule || getCaseTypeMeta(record.caseType).module,
			snapshotStatus: 'generated',
		};
	}
	const snapshot =
		(payload.snapshot && payload.snapshot.content) ||
		(payload.snapshot && payload.snapshot.text) ||
		payload.aiExport ||
		payload.aiSnapshot ||
		(payload.result && payload.result.aiSnapshot) ||
		(payload.result && payload.result.snapshotText) ||
		'';
	if(`${snapshot || ''}`.trim()){
		return {
			content: `${snapshot}`.trim(),
			payload,
			moduleName: payload.module || record.sourceModule || getCaseTypeMeta(record.caseType).module,
			snapshotStatus: 'ready',
		};
	}
	return {
		content: summarizeCasePayload(record, payload),
		payload,
		moduleName: payload.module || record.sourceModule || getCaseTypeMeta(record.caseType).module,
		snapshotStatus: 'generated',
	};
}

export function listAnalysisSources(){
	const charts = listLocalCharts({}).map((item)=>({
		id: item.cid,
		sourceType: 'chart',
		title: item.name || '未命名命盘',
		module: 'astrochart',
		time: item.birth || item.updateTime || '',
		zone: item.zone || '+08:00',
		tags: normalizeTags(item.group),
		snapshotStatus: 'lazy',
		updatedAt: item.updateTime || '',
		record: item,
	}));
	const cases = listLocalCases({}).map((item)=>{
		const meta = getCaseTypeMeta(item.caseType);
		const extracted = extractCaseSnapshotText(item);
		return {
			id: item.cid,
			sourceType: 'case',
			title: item.event || '未命名事盘',
			module: item.sourceModule || extracted.moduleName || meta.module,
			time: item.divTime || item.updateTime || '',
			zone: item.zone || '+08:00',
			tags: normalizeTags(item.group),
			snapshotStatus: extracted.snapshotStatus,
			updatedAt: item.updateTime || '',
			record: item,
		};
	});
	return charts.concat(cases).sort((a, b)=>{
		const ta = Date.parse(a.updatedAt || a.time || '') || 0;
		const tb = Date.parse(b.updatedAt || b.time || '') || 0;
		return tb - ta;
	});
}

async function buildChartContext(source){
	const record = source && source.record ? source.record : null;
	if(!record){
		throw new Error('chart.source.required');
	}
	const fields = buildFieldObject(record);
	const rsp = await fetchChart({
		...fieldParams(fields),
		includePrimaryDirection: false,
	}, {
		silent: true,
		timeoutMs: 20000,
	});
	if(!rsp || !rsp.Result){
		throw new Error('chart.context.failed');
	}
	const content = buildAstroSnapshotContent(rsp.Result, fields) || '';
	return {
		content: `${content}`.trim(),
		title: source.title,
		module: 'astrochart',
		meta: {
			sourceType: 'chart',
			sourceId: source.id,
			birth: record.birth || '',
			zone: record.zone || '',
		},
	};
}

async function buildCaseContext(source){
	const record = source && source.record ? source.record : null;
	if(!record){
		throw new Error('case.source.required');
	}
	const extracted = extractCaseSnapshotText(record);
	return {
		content: extracted.content,
		title: source.title,
		module: extracted.moduleName,
		meta: {
			sourceType: 'case',
			sourceId: source.id,
			caseType: record.caseType,
			divTime: record.divTime,
		},
	};
}

export async function getAnalysisSourceContext(source, options = {}){
	if(!source){
		return null;
	}
	const cacheId = `${source.sourceType}:${source.id}`;
	const preferCache = options.preferCache !== false;
	if(preferCache){
		const cached = await getStoreRecord(AI_ANALYSIS_STORES.contextCache, cacheId);
		if(cached && cached.sourceUpdatedAt === source.updatedAt && cached.content){
			return cached;
		}
	}
	const built = source.sourceType === 'chart'
		? await buildChartContext(source)
		: await buildCaseContext(source);
	const next = {
		id: cacheId,
		sourceId: source.id,
		sourceType: source.sourceType,
		title: source.title,
		module: built.module,
		content: built.content,
		meta: built.meta || {},
		sourceUpdatedAt: source.updatedAt || '',
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	};
	await putStoreRecord(AI_ANALYSIS_STORES.contextCache, next, 'ctx');
	return next;
}

export function estimateTextTokens(text){
	const raw = `${text || ''}`.trim();
	return Math.ceil(raw.length / 4);
}

export function buildContextLayers({
	sourceContext,
	materials,
	bundles,
	templates,
	retrievedChunks,
	conversationMessages,
	systemPrompt,
}) {
	const layers = [];
	layers.push({
		key: 'system',
		title: '系统提示',
		priority: 100,
		content: systemPrompt || '你是星阙的 AI 分析助手。请严格依据当前案例上下文、参考资料与回复模版作答。',
	});
	if(sourceContext && sourceContext.content){
		layers.push({
			key: 'source',
			title: `案例前提：${sourceContext.title || ''}`,
			priority: 95,
			content: sourceContext.content,
		});
	}
	(bundles || []).forEach((bundle)=>{
		if(bundle.defaultSystemPrompt){
			layers.push({
				key: `bundle-system:${bundle.id}`,
				title: `组合系统提示：${bundle.name || ''}`,
				priority: 92,
				content: bundle.defaultSystemPrompt,
			});
		}
	});
	(templates || []).forEach((template)=>{
		const text = template && template.format === 'json'
			? [template.instructionText, template.jsonSchema && `JSON Schema：\n${template.jsonSchema}`].filter(Boolean).join('\n\n')
			: (template && (template.instructionText || template.content));
		if(text){
			layers.push({
				key: `template:${template.id}`,
				title: `模版约束：${template.name || ''}`,
				priority: 90,
				content: text,
			});
		}
	});
	const directMaterials = (materials || []).filter((item)=>!item.retrievedOnly);
	directMaterials.forEach((item, idx)=>{
		if(item.extractedText){
			layers.push({
				key: `material:${item.id}`,
				title: `参考资料 ${idx + 1}：${item.name || '未命名资料'}`,
				priority: 70,
				content: item.extractedText,
			});
		}
	});
	if(Array.isArray(retrievedChunks) && retrievedChunks.length){
		const retrievedText = buildRetrievedContextText(retrievedChunks);
		if(retrievedText){
			layers.push({
				key: 'retrieved-context',
				title: '检索资料片段',
				priority: 80,
				content: retrievedText,
			});
		}
	}
	const visibleHistory = (conversationMessages || []).filter((item)=>item && item.role !== 'system_hidden').slice(-10);
	if(visibleHistory.length){
		layers.push({
			key: 'recent-history',
			title: '最近对话',
			priority: 60,
			content: visibleHistory.map((item)=>`[${item.role}] ${item.content || ''}`).join('\n\n'),
		});
	}
	return layers.map((item)=>({
		...item,
		tokenEstimate: estimateTextTokens(item.content),
	}));
}

export function clipContextLayers(layers, options = {}){
	const maxChars = options.maxChars || DEFAULT_CONTEXT_CHAR_LIMIT;
	const sorted = (layers || []).slice(0).sort((a, b)=>b.priority - a.priority);
	const kept = [];
	let totalChars = 0;
	sorted.forEach((item)=>{
		const content = `${item.content || ''}`.trim();
		if(!content){
			return;
		}
		const nextChars = totalChars + content.length;
		if(nextChars <= maxChars){
			kept.push({
				...item,
				content,
				clipped: false,
			});
			totalChars = nextChars;
			return;
		}
		if(kept.length === 0 || item.priority >= 90){
			const remain = Math.max(0, maxChars - totalChars);
			if(remain > 120){
				kept.push({
					...item,
					content: `${content.slice(0, remain)}\n...[已裁剪]`,
					clipped: true,
				});
				totalChars = maxChars;
			}
		}
	});
	return kept;
}

export function buildPromptContext({
	sourceContext,
	materials,
	bundles,
	templates,
	retrievedChunks,
	conversationMessages,
	systemPrompt,
	maxChars,
}) {
	const layers = buildContextLayers({
		sourceContext,
		materials,
		bundles,
		templates,
		retrievedChunks,
		conversationMessages,
		systemPrompt,
	});
	const clippedLayers = clipContextLayers(layers, { maxChars });
	return clippedLayers.map((item)=>`${item.title}\n${item.content}`).join('\n\n').trim();
}
