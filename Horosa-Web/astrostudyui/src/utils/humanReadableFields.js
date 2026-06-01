const HUMAN_FIELD_LABELS = {
	name: '名称',
	title: '标题',
	label: '名称',
	text: '内容',
	content: '内容',
	verse: '条文',
	raw_key: '条目',
	description: '说明',
	desc: '说明',
	poem: '断曰',
	source: '来源',
	author: '作者',
	book: '典籍',
	category: '类别',
	group: '分组',
	condition: '条件',
	stars: '星曜',
	star: '星曜',
	ganzhi: '干支',
	gan: '天干',
	zhi: '地支',
	branch: '地支',
	branch_name: '地支',
	stem: '天干',
	year: '年份',
	birth_year: '出生年',
	start_year: '起年',
	end_year: '止年',
	start_age: '起龄',
	end_age: '止龄',
	age: '年龄',
	duration: '年限',
	lord: '主星',
	palace: '宫位',
	palace_name: '宫名',
	palace_index: '宫序',
	index: '序号',
	code: '代码',
	rawCode: '原码',
	rawSection: '原段',
	section: '部类',
	type: '类别',
	status: '状态',
	result: '结果',
	score: '分值',
	phase: '阶段',
	element: '五行',
	shengxiao: '生肖',
	animal: '禽星',
	tai: '胎星',
	zhu: '命星',
	xing_pin: '形品',
	xi_ji: '喜忌',
};

const INTERNAL_EMPTY_KEYS = new Set([
	'raw',
	'_raw',
	'payload',
	'request',
	'debug',
	'trace',
	'stack',
	'error_code',
	'ResultCode',
]);

function isBlank(value){
	return value === undefined || value === null || value === '';
}

function stripWrappingQuotes(value){
	const text = `${value}`.trim();
	const match = text.match(/^(['"])(.*)\1$/);
	return match ? match[2] : text;
}

function cleanScalar(value){
	const raw = `${value}`.trim();
	const machineText = formatMachineReadableString(raw);
	if(machineText){
		return machineText;
	}
	const text = stripWrappingQuotes(raw)
		.replace(/\bNone\b/g, '无')
		.replace(/\bTrue\b/g, '是')
		.replace(/\bFalse\b/g, '否')
		.replace(/\bnull\b/g, '无')
		.replace(/\bundefined\b/g, '无');
	return text;
}

function labelForKey(key){
	if(HUMAN_FIELD_LABELS[key]){
		return HUMAN_FIELD_LABELS[key];
	}
	const snake = `${key}`.replace(/[A-Z]/g, (match)=>`_${match.toLowerCase()}`).replace(/^_/, '');
	if(HUMAN_FIELD_LABELS[snake]){
		return HUMAN_FIELD_LABELS[snake];
	}
	if(/^[a-zA-Z0-9_]+$/.test(`${key}`)){
		return '项目';
	}
	return key;
}

function formatReadableRecord(value){
	if(!value || typeof value !== 'object' || value instanceof Array){
		return '';
	}
	const name = value.name || value.title || value.label || '';
	const stars = value.stars instanceof Array ? value.stars.join('、') : value.stars;
	const meta = [value.ganzhi, stars].map((item)=>formatHumanValue(item)).filter((item)=>item && item !== '—');
	const condition = value.condition || value.desc || value.description || value.poem || '';
	if(name){
		const suffix = meta.length ? `（${meta.join('，')}）` : '';
		const body = condition ? `：${formatHumanValue(condition)}` : '';
		return `${formatHumanValue(name)}${suffix}${body}`;
	}
	if(value.zhu || value.tai){
		const title = [
			value.zhu ? `命星 ${formatHumanValue(value.zhu)}` : '',
			value.tai ? `胎星 ${formatHumanValue(value.tai)}` : '',
		].filter(Boolean).join(' × ');
		const details = [
			value.xing_pin ? `形品 ${formatHumanValue(value.xing_pin)}` : '',
			value.xi_ji ? `喜忌 ${formatHumanValue(value.xi_ji)}` : '',
			value.desc ? formatHumanValue(value.desc) : '',
			value.description ? formatHumanValue(value.description) : '',
			value.poem ? formatHumanValue(value.poem) : '',
		].filter(Boolean);
		return [title, ...details].filter(Boolean).join('；\n');
	}
	return '';
}

export function formatMachineReadableString(text){
	const machineKeys = 'name|title|label|raw_key|ganzhi|stars|condition|birth_year|start_year|end_year|palace_index|branch_name|branch|lord|code|rawCode|rawSection|type|source|author|book|category|group';
	const dequoted = `${text || ''}`.replace(new RegExp(`['"](${machineKeys})['"]\\s*[：:]`, 'g'), '$1：');
	if(!dequoted || !(new RegExp(`\\b(${machineKeys})\\s*[：:]`)).test(dequoted)){
		return '';
	}
	const normalized = dequoted.replace(new RegExp(`,\\s*(?=(?:${machineKeys})\\s*[：:])`, 'g'), '；');
	const chunks = normalized.split(/、\s*(?=(?:name|title|label)\s*[：:])/).map((item)=>item.trim()).filter(Boolean);
	const rows = chunks.map((chunk)=>{
		const fields = {};
		chunk.split(/[；;]/).forEach((part)=>{
			const pieces = part.split(/[：:]/);
			if(pieces.length >= 2){
				fields[stripWrappingQuotes(pieces.shift().trim())] = stripWrappingQuotes(pieces.join('：').trim());
			}
		});
		return formatReadableRecord(fields) || Object.keys(fields).map((key)=>{
			if(INTERNAL_EMPTY_KEYS.has(key)){
				return '';
			}
			const val = formatHumanValue(fields[key]);
			const label = labelForKey(key);
			return val && val !== '—' ? `${label}：${val}` : '';
		}).filter(Boolean).join('；');
	}).filter(Boolean);
	return rows.join('；\n');
}

export function formatHumanValue(value){
	if(isBlank(value)){
		return '—';
	}
	if(value instanceof Array){
		const joiner = value.some((item)=>item && typeof item === 'object') ? '；\n' : '、';
		const text = value.map((item)=>formatHumanValue(item)).filter((item)=>item && item !== '—').join(joiner);
		return text || '—';
	}
	if(typeof value === 'object'){
		const readable = formatReadableRecord(value);
		if(readable){
			return readable;
		}
		const text = Object.keys(value).map((key)=>{
			if(INTERNAL_EMPTY_KEYS.has(key)){
				return '';
			}
			const val = formatHumanValue(value[key]);
			const label = labelForKey(key);
			return val && val !== '—' ? `${label}：${val}` : '';
		}).filter(Boolean).join('；\n');
		return text || '—';
	}
	return cleanScalar(value);
}
