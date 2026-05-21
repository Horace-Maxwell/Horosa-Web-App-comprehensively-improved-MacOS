import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import { moiraMergeStellarRelationRows as mergeStellarRelationRows, } from './GuoLaoMoiraWheel';
import './GuoLaoMoiraPanel.less';

const PLANET_ORDER = [
	{ id: AstroConst.SUN, name: '日' },
	{ id: AstroConst.MOON, name: '月' },
	{ id: AstroConst.VENUS, name: '金' },
	{ id: AstroConst.JUPITER, name: '木' },
	{ id: AstroConst.MERCURY, name: '水' },
	{ id: AstroConst.MARS, name: '火' },
	{ id: AstroConst.SATURN, name: '土' },
	{ id: AstroConst.SOUTH_NODE, name: '计' },
	{ id: AstroConst.NORTH_NODE, name: '罗' },
	{ id: AstroConst.PURPLE_CLOUDS, name: '炁' },
	{ id: AstroConst.DARKMOON, name: '孛' },
];

const STEM_BRANCHES = ['甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午', '辛未', '壬申', '癸酉', '甲戌', '乙亥', '丙子', '丁丑', '戊寅', '己卯', '庚辰', '辛巳', '壬午', '癸未', '甲申', '乙酉', '丙戌', '丁亥', '戊子', '己丑', '庚寅', '辛卯', '壬辰', '癸巳', '甲午', '乙未', '丙申', '丁酉', '戊戌', '己亥', '庚子', '辛丑', '壬寅', '癸卯', '甲辰', '乙巳', '丙午', '丁未', '戊申', '己酉', '庚戌', '辛亥', '壬子', '癸丑', '甲寅', '乙卯', '丙辰', '丁巳', '戊午', '己未', '庚申', '辛酉', '壬戌', '癸亥'];
const YEAR_STAR_BY_STEM = {
	甲: '火',
	乙: '孛',
	丙: '木',
	丁: '金',
	戊: '土',
	己: '月',
	庚: '水',
	辛: '炁',
	壬: '计',
	癸: '罗',
};
const YEAR_INFO_GROUPS = [
	['天禄', '科名', '天马', '生官'],
	['天暗', '科甲', '地驿'],
	['天福', '文星', '禄元'],
	['天耗', '魁星', '马元', '值难'],
	['天荫', '官星', '天元', '职元'],
	['天贵', '印星', '地元', '局主'],
	['天嗣', '寿元', '人元', '天经'],
	['天刑', '催官', '仁元', '地纬'],
	['天印', '禄神', '血支'],
	['天囚', '喜神', '血忌'],
	['天权', '爵星', '产星', '伤官'],
];
const TEN_GOD_ORG = ['天禄', '天暗', '天福', '天耗', '天荫', '天贵', '天嗣', '天刑', '天印', '天囚', '天权'];
const TEN_GOD_ALT = ['比肩', '劫财', '食神', '伤官', '偏财', '正财', '七杀', '正官', '偏印', '正印'];
const SPEED_LIMITS = {
	Venus: { slow: 0.71, fast: 1.245 },
	Jupiter: { slow: 0.05, fast: 0.23 },
	Mercury: { slow: 0.88, fast: 1.50 },
	Mars: { slow: 0.4, fast: 0.70 },
	Saturn: { slow: 0.02, fast: 0.13 },
};

function safeList(val){
	return val && val.length ? val : [];
}

function safeMap(val){
	return val && typeof val === 'object' ? val : {};
}

function joinYearItems(items){
	return safeList(items).map((item)=>{
		if(item && typeof item === 'object'){
			return [item.name, item.star ? `化${item.star}` : ''].filter(Boolean).join(' ');
		}
		return `${item || ''}`;
	}).filter(Boolean).join('、');
}

function hasUnverifiedMoiraPatternSource(value){
	return value && (
		value.styleSource === 'moira-dsl-not-evaluated'
		|| value.engine === 'moira-rules-on-horosa-ephemeris'
		|| value.version === 'qizheng-moira-rules-v1'
	);
}

function mergeDefined(){
	const res = {};
	for(let i=0; i<arguments.length; i++){
		const obj = safeMap(arguments[i]);
		Object.keys(obj).forEach((key)=>{
			if(obj[key] !== undefined && obj[key] !== null && obj[key] !== ''){
				res[key] = obj[key];
			}
		});
	}
	return res;
}

function levelText(level){
	if(level === 'good'){
		return '吉';
	}
	if(level === 'bad'){
		return '忌';
	}
	if(level === 'notice'){
		return '察';
	}
	return '平';
}

function joinNames(list){
	const arr = safeList(list).map(formatGodName).filter(Boolean);
	return arr.length ? arr.join('、') : '无';
}

function formatGodName(name){
	let val = `${name || ''}`.replace(/\s+/g, '');
	if(!val){
		return '';
	}
	val = val.split(/[\/／]/)[0];
	const aliases = {
		天乙贵人: '天贵',
		玉堂贵人: '玉贵',
	};
	return aliases[val] || val;
}

function msg(id){
	if(id === undefined || id === null){
		return '';
	}
	return AstroText.AstroMsgCN[id] || AstroText.AstroTxtMsg[id] || AstroText.AstroMsg[id] || `${id}`;
}

function norm(deg){
	let val = Number(deg);
	if(!Number.isFinite(val)){
		return 0;
	}
	val %= 360;
	if(val < 0){
		val += 360;
	}
	return val;
}

function objectLon(obj){
	const num = Number(obj && (obj.ra !== undefined ? obj.ra : obj.lon));
	if(Number.isFinite(num)){
		return norm(num);
	}
	const sign = obj && obj.sign ? AstroConst.LIST_SIGNS.indexOf(obj.sign) : -1;
	const signlon = Number(obj && obj.signlon);
	if(sign >= 0 && Number.isFinite(signlon)){
		return norm(sign * 30 + signlon);
	}
	return null;
}

function degreeText(lon){
	const val = norm(lon);
	const deg = Math.floor(val % 30);
	const min = Math.floor(((val % 30) - deg) * 60);
	return `${deg}度${min}分`;
}

function suDegreeText(lon){
	const val = norm(lon);
	const deg = Math.floor(val);
	const min = Math.floor((val - deg) * 60);
	return `${deg}度${min}分`;
}

function signNameFromLon(lon){
	const idx = Math.floor(norm(lon) / 30) % 12;
	return msg(AstroConst.LIST_SIGNS[idx]);
}

function ziFromLon(lon){
	const list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
	return list[Math.floor(norm(lon) / 30) % 12] || '';
}

function anchorFromObject(chart, id, fallbackId, label){
	const obj = findObject(chart, id) || findObject(chart, fallbackId);
	const lon = objectLon(obj);
	if(!obj || lon === null){
		return {};
	}
	return {
		longitude: lon,
		signName: signNameFromLon(lon),
		degreeText: degreeText(lon),
		zi: ziFromLon(lon),
		area: msg(obj.id) || label,
		moiraHouse: msg(obj.house) || '',
	};
}

function suHostForLon(chart, lon){
	const val = Number(lon);
	const stars = safeList(chart && chart.fixedStarSu28).map((item)=>({
		name: item.name || item.label || '',
		ra: Number(item.ra),
	})).filter((item)=>item.name && Number.isFinite(item.ra)).sort((a, b)=>a.ra - b.ra);
	if(!stars.length || !Number.isFinite(val)){
		return null;
	}
	const degree = norm(val);
	let star = stars[stars.length - 1];
	for(let i = 0; i < stars.length; i++){
		if(stars[i].ra <= degree){
			star = stars[i];
		}else {
			break;
		}
	}
	const offset = norm(degree - star.ra);
	return {
		name: star.name,
		degreeText: suDegreeText(offset),
		value: `${star.name} ${suDegreeText(offset)}`,
	};
}

function compactDegreeText(lon){
	const val = norm(lon);
	const deg = `${Math.floor(val % 30)}`.padStart(2, '0');
	const min = `${Math.floor(((val % 30) - Math.floor(val % 30)) * 60)}`.padStart(2, '0');
	return `${deg}.${min}`;
}

function stemBranchForYear(year){
	const idx = ((Number(year) - 1984) % 60 + 60) % 60;
	return STEM_BRANCHES[idx] || '';
}

function yearFromParams(params){
	const raw = params && params.date ? `${params.date}` : '';
	const match = raw.match(/-?\d{3,4}/);
	return match ? Number(match[0]) : new Date().getFullYear();
}

function dateTextFromParams(params){
	return `${params.date || ''} ${params.time || ''}`.trim();
}

function pickDeep(root, keys){
	const stack = [root];
	const visited = new Set();
	while(stack.length){
		const cur = stack.shift();
		if(!cur || typeof cur !== 'object' || visited.has(cur)){
			continue;
		}
		visited.add(cur);
		for(const key of Object.keys(cur)){
			if(keys.includes(key) && cur[key] !== undefined && cur[key] !== null && cur[key] !== ''){
				return cur[key];
			}
			if(cur[key] && typeof cur[key] === 'object'){
				stack.push(cur[key]);
			}
		}
	}
	return '';
}

function getBazi(root){
	const chart = root && root.chart ? root.chart : {};
	return (chart.nongli && chart.nongli.bazi) || (root && root.nongli && root.nongli.bazi) || {};
}

function textFromBaziPole(value){
	if(value === undefined || value === null || value === ''){
		return '';
	}
	if(typeof value === 'string' || typeof value === 'number'){
		return `${value}`;
	}
	if(typeof value !== 'object'){
		return '';
	}
	const direct = value.text || value.name || value.value || value.ganzi || value.ganZi || value.pillar || value.column;
	if(direct){
		return `${direct}`;
	}
	const stem = safeMap(value.stem);
	const branch = safeMap(value.branch);
	const stemText = stem.cell || stem.text || stem.name || stem.value || value.gan || value.stemText || value.tianGan || '';
	const branchText = branch.cell || branch.text || branch.name || branch.value || value.zhi || value.branchText || value.diZhi || '';
	return `${stemText || ''}${branchText || ''}`;
}

function readBaziPole(bazi, key){
	const data = safeMap(bazi);
	const fourColumns = safeMap(data.fourColumns || data.fourcolumns || data.fourPillars || data.pillars);
	const fourZhuMap = safeMap(fourColumns.fourZhuMap || data.fourZhuMap);
	const zhKeys = {
		year: '年',
		month: '月',
		day: '日',
		time: '时',
	};
	const candidates = [
		data[key],
		fourColumns[key],
		data[`${key}Pole`],
		fourColumns[`${key}Pole`],
		data[`${key}Pillar`],
		fourColumns[`${key}Pillar`],
		data[`${key}Column`],
		fourColumns[`${key}Column`],
		data[`${key}Ganzi`],
		fourColumns[`${key}Ganzi`],
		zhKeys[key] ? fourZhuMap[zhKeys[key]] : '',
	];
	for(const item of candidates){
		const text = textFromBaziPole(item).trim();
		if(text){
			return text;
		}
	}
	return '';
}

function lunarText(root){
	const chart = root && root.chart ? root.chart : {};
	const nongli = chart.nongli || root.nongli || {};
	return nongli.text || nongli.nongli || nongli.lunar || nongli.lunarText || '';
}

function baziStemBranch(root, key, fallbackYear){
	const bazi = getBazi(root);
	const pole = readBaziPole(bazi, key);
	if(pole){
		return pole;
	}
	if(key === 'year'){
		return stemBranchForYear(fallbackYear);
	}
	return '';
}

function baziText(root){
	const bazi = getBazi(root);
	const direct = bazi.text || bazi.name || bazi.fourColumnsText || bazi.fourPillarsText;
	if(direct){
		return direct;
	}
	return ['year', 'month', 'day', 'time'].map((key)=>readBaziPole(bazi, key)).filter(Boolean).join(' ');
}

function findObject(chart, id){
	const objects = chart && chart.objects ? chart.objects : [];
	return objects.find((obj)=>obj.id === id);
}

function planetStatus(obj){
	const speed = Number(obj && obj.lonspeed);
	if(!Number.isFinite(speed)){
		return '顺';
	}
	if(speed < -0.000001){
		return '逆';
	}
	if(Math.abs(speed) < 0.002){
		return '留';
	}
	const limit = SPEED_LIMITS[obj.id];
	if(limit){
		const abs = Math.abs(speed);
		if(abs < limit.slow){
			return '迟';
		}
		if(abs > limit.fast){
			return '速';
		}
	}
	return '顺';
}

function speedText(speed){
	if(!Number.isFinite(speed)){
		return '';
	}
	const sign = speed > 0 ? '+' : '';
	return `${sign}${speed.toFixed(4)}`;
}

function buildPlanetRows(chart, rulePlanets){
	const byRule = new Map(safeList(rulePlanets).map((item)=>[item.id, item]));
	return PLANET_ORDER.map((def)=>{
		const obj = findObject(chart, def.id);
		const lon = objectLon(obj);
		if(!obj || lon === null){
			return null;
		}
		const rule = byRule.get(def.id) || {};
		return {
			id: def.id,
			name: def.name,
			signName: rule.signName || msg(obj.sign),
			degreeText: rule.degreeText || degreeText(lon),
			compactDegree: compactDegreeText(lon),
			su28: obj.su28 || rule.su28 || '',
			house: rule.moiraHouse || msg(obj.house) || '',
			dignity: rule.dignity || '',
			status: planetStatus(obj),
			speed: Number(obj.lonspeed),
		};
	}).filter(Boolean);
}

function yearInfoRows(title, stemBranch){
	const stem = stemBranch ? stemBranch.slice(0, 1) : '';
	return YEAR_INFO_GROUPS.map((items, idx)=>({
		title: idx === 0 ? title : '',
		main: items[0],
		items,
		yearStar: idx === 0 ? (YEAR_STAR_BY_STEM[stem] || '') : '',
	}));
}

function Section({title, children}){
	return (
		<div className="horosa-guolao-moira-section">
			<div className="horosa-guolao-moira-section-title">{title}</div>
			{children}
		</div>
	);
}

function KeyValueGrid({items}){
	return (
		<div className="horosa-guolao-moira-kv-grid">
			{items.filter((item)=>item && item.value !== undefined && item.value !== '').map((item)=>(
				<div className="horosa-guolao-moira-kv" key={item.label}>
					<span>{item.label}</span>
					<strong>{item.value}</strong>
				</div>
			))}
		</div>
	);
}

function PlanetTable({rows}){
	return (
		<div className="horosa-guolao-moira-table">
			<div className="horosa-guolao-moira-table-row horosa-guolao-moira-table-head">
				<span>星</span><span>宫/座</span><span>宿度</span><span>势/速</span>
			</div>
			{rows.map((item)=>(
				<div className="horosa-guolao-moira-table-row" key={item.id}>
					<strong>{item.name}</strong>
					<span>{item.house || item.signName} · {item.signName}</span>
					<span>{item.su28 || '-'} {item.compactDegree}</span>
					<span>{[item.dignity, item.status, speedText(item.speed)].filter(Boolean).join(' · ')}</span>
				</div>
			))}
		</div>
	);
}

function YearSignTable({rows}){
	return (
		<div className="horosa-guolao-moira-table">
			<div className="horosa-guolao-moira-table-row horosa-guolao-moira-table-head">
				<span>宫</span><span>化曜</span><span>曜名</span><span>宫性</span>
			</div>
			{safeList(rows).map((item)=>(
				<div className="horosa-guolao-moira-table-row" key={`${item.mode || 'year'}-${item.name}`}>
					<strong>{item.name}</strong>
					<span>{item.star || '-'}</span>
					<span>{item.shortName || '-'}</span>
					<span>{[item.quality, item.zi, item.signName].filter(Boolean).join(' · ')}</span>
				</div>
			))}
		</div>
	);
}

function StellarRelationTable({rows}){
	const list = safeList(rows).filter((item)=>safeList(item.main).length || safeList(item.same).length || safeList(item.transitMain).length || safeList(item.transitSame).length);
	if(!list.length){
		return <div className="horosa-guolao-moira-empty">当前星宿未形成可摘录的落宿/同经信息。</div>;
	}
	return (
		<div className="horosa-guolao-moira-table horosa-guolao-moira-stellar-table">
			<div className="horosa-guolao-moira-table-row horosa-guolao-moira-table-head">
				<span>宿</span><span>本命落入</span><span>本命同经</span><span>流年落入</span>
			</div>
			{list.map((item)=>(
				<div className="horosa-guolao-moira-table-row" key={`stellar-${item.index}-${item.name}`}>
					<strong>{item.label || item.name}</strong>
					<span>{joinNames(item.main)}</span>
					<span>{joinNames(item.same)}</span>
					<span>{[joinNames(item.transitMain), safeList(item.transitSame).length ? `同经：${joinNames(item.transitSame)}` : ''].filter((val)=>val && val !== '无').join('；') || '无'}</span>
				</div>
			))}
		</div>
	);
}

function hasRenderableChart(rootValue){
	return safeList(rootValue && rootValue.chart && rootValue.chart.objects).length > 0;
}

function buildPanelFallbackValue(rootValue){
	return {
		engine: 'horosa-local-moira-panel-fallback',
		engineLabel: 'Moira政余格局',
		summary: '',
		styleWarning: '',
		params: mergeDefined(rootValue && rootValue.params),
		anchors: {},
		houses: [],
		planets: [],
		patterns: [],
		godHits: [],
	};
}

export default function GuoLaoMoiraPanel(props){
	const rootValue = props.rootValue || {};
	const value = props.value || (hasRenderableChart(rootValue) ? buildPanelFallbackValue(rootValue) : null);
	const birthChart = rootValue.chart || {};
	const transitRoot = props.transitValue || {};
	const transitChart = transitRoot.chart || {};
	const params = mergeDefined(value && value.params, rootValue.params);
	const transitParams = safeMap(props.transitParams);

	if(props.loading && !value){
		return (
			<div className="horosa-guolao-moira">
				<div className="horosa-guolao-moira-empty">正在推演 Moira 规则层...</div>
			</div>
		);
	}
	if(!value){
		return (
			<div className="horosa-guolao-moira">
				<div className="horosa-guolao-moira-empty">Moira 规则层等待当前七政盘完成后载入。</div>
			</div>
		);
	}

	const anchors = value.anchors || {};
	const life = anchors.life && Object.keys(anchors.life).length
		? anchors.life
		: anchorFromObject(birthChart, AstroConst.LIFEMASTERDEG74, AstroConst.ASC, '命度点');
	const self = anchors.self && Object.keys(anchors.self).length
		? anchors.self
		: anchorFromObject(birthChart, AstroConst.MOON, AstroConst.ASC, '身度参考');
	const lifeSuHost = suHostForLon(birthChart, life.longitude);
	const selfSuHost = suHostForLon(birthChart, self.longitude);
	const unverifiedPatternSource = hasUnverifiedMoiraPatternSource(value);
	const styleWarning = value.styleWarning || (unverifiedPatternSource ? '当前接口返回的是旧版 Horosa 近似格局，不是 Moira 本体的政余喜格/忌格；已屏蔽为正式格局输出。' : '');
	const patterns = unverifiedPatternSource ? [] : safeList(value.patterns);
	const planets = safeList(value.planets);
		const natalPlanetRows = buildPlanetRows(birthChart, planets);
		const transitPlanetRows = buildPlanetRows(transitChart, []);
		const godHits = safeList(value.godHits);
		const yearStars = safeMap(value.yearStars);
		const birthYearStars = safeMap(yearStars.birth);
		const currentYearStars = safeMap(yearStars.transit);
		const natalYearStars = safeList(value.natalYearStars);
		const transitYearStars = safeList(value.transitYearStars);
		const transitGodHits = safeList(value.transitGodHits);
		const houses = safeList(value.houses);
	const stellarRelationRows = mergeStellarRelationRows(birthChart, transitChart);
	const birthYear = yearFromParams(params);
	const transitYear = yearFromParams(transitParams);
	const birthYearText = baziStemBranch(rootValue, 'year', birthYear);
	const transitYearText = stemBranchForYear(transitYear);
	const age = transitYear - birthYear + 1;
	const apparentSolar = pickDeep(rootValue, ['apparentSolar', 'apparent_solar', 'apparentSolarTime', 'solarTime', 'trueSolarTime']) || (birthChart.nongli && birthChart.nongli.birth);
	const sunrise = pickDeep(rootValue, ['sunrise', 'sunRise', 'sunriseTime', 'sunRiseTime', 'sun_rise', 'guolaoSunRiseTime']);
	const sunset = pickDeep(rootValue, ['sunset', 'sunSet', 'sunsetTime', 'sunSetTime', 'sun_set']);
	const moonrise = pickDeep(rootValue, ['moonrise', 'moonRise', 'moonriseTime', 'moonRiseTime', 'moon_rise']);
	const moonset = pickDeep(rootValue, ['moonset', 'moonSet', 'moonsetTime', 'moonSetTime', 'moon_set']);
	const hasRiseSet = sunrise || sunset || moonrise || moonset;

	return (
		<div className="horosa-guolao-moira">
			<Section title="起盘与流年">
				<KeyValueGrid items={[
					{label: '计算法', value: '地心计算法'},
					{label: '本命时间', value: dateTextFromParams(params)},
					{label: '流年时间', value: dateTextFromParams(transitParams)},
					{label: '本命四柱', value: baziText(rootValue) || birthYearText},
					{label: '本命农历', value: lunarText(rootValue)},
					{label: '流年', value: `${transitYearText} ${transitYear}，${Number.isFinite(age) ? `${age}岁` : ''}`},
					{label: '地点', value: [params.lon, params.lat].filter(Boolean).join(' ')},
				]} />
			</Section>

			<Section title="真太阳与出没">
				<KeyValueGrid items={[
					{label: '真太阳时间', value: apparentSolar || dateTextFromParams(params)},
					{label: '日出', value: sunrise},
					{label: '日落', value: sunset},
					{label: '月出', value: moonrise},
					{label: '月落', value: moonset},
				]} />
				{hasRiseSet ? null : <div className="horosa-guolao-moira-note">日月出没接口未给出独立字段，当前先以起盘时间和盘面星曜为准。</div>}
			</Section>

			<Section title="命身与限度">
				<div className="horosa-guolao-moira-anchor-grid">
					<div className="horosa-guolao-moira-anchor">
						<span>命主/命度</span>
						<strong>{life.signName || '随盘面'} {life.degreeText || ''}</strong>
						<em>{[life.zi, life.area, life.moiraHouse, anchors.lifeModeName || value.lifeModeName].filter(Boolean).join(' · ')}</em>
					</div>
					<div className="horosa-guolao-moira-anchor">
						<span>身主/身度</span>
						<strong>{self.signName || '随盘面'} {self.degreeText || ''}</strong>
						<em>{[self.zi, self.area, self.moiraHouse].filter(Boolean).join(' · ')}</em>
					</div>
				</div>
				<div className="horosa-guolao-moira-anchor-grid horosa-guolao-moira-su-anchor-grid">
					<div className="horosa-guolao-moira-anchor">
						<span>命度宿主</span>
						<strong>{lifeSuHost ? lifeSuHost.value : '随盘面'}</strong>
					</div>
					<div className="horosa-guolao-moira-anchor">
						<span>身度宿主</span>
						<strong>{selfSuHost ? selfSuHost.value : '随盘面'}</strong>
					</div>
				</div>
			</Section>

				<Section title="本命星曜">
					{natalYearStars.length ? <YearSignTable rows={natalYearStars} /> : <PlanetTable rows={natalPlanetRows} />}
				</Section>

				<Section title="流年星曜">
					{transitYearStars.length ? <YearSignTable rows={transitYearStars} /> : <PlanetTable rows={transitPlanetRows} />}
				</Section>

				<Section title="星宿落入与同经">
					<StellarRelationTable rows={stellarRelationRows} />
				</Section>

			<Section title="十二宫位">
				<div className="horosa-guolao-moira-house-list">
					{houses.map((item)=>(
						<div key={`${item.index}-${item.name}`}>
							<strong>{item.name}</strong>
							<span>{item.zi} · {item.area} · {item.signName}</span>
							<em>{item.moiraStarHouse}</em>
						</div>
					))}
				</div>
			</Section>

				<Section title="年曜与十神">
					<KeyValueGrid items={[
						{label: '本命年柱', value: birthYearStars.yearPole || birthYearText},
						{label: '流年年柱', value: currentYearStars.yearPole || transitYearText},
						{label: '本命首曜', value: birthYearStars.yearStar},
						{label: '流年首曜', value: currentYearStars.yearStar || `${transitYearText.slice(0, 1)} → ${YEAR_STAR_BY_STEM[transitYearText.slice(0, 1)] || '-'}`},
						{label: '原十神序', value: safeList(yearStars.tenGodListOrg).length ? yearStars.tenGodListOrg.join('、') : TEN_GOD_ORG.join('、')},
						{label: '替代十神序', value: safeList(yearStars.tenGodListAlt).length ? yearStars.tenGodListAlt.join('、') : TEN_GOD_ALT.join('、')},
					]} />
					<div className="horosa-guolao-moira-year-groups">
						{safeList(currentYearStars.groups).length ? currentYearStars.groups.map((row, idx)=>(
							<div key={`${row.main}-${idx}`}>
								<strong>{row.main}</strong>
								<span>{joinYearItems(row.items)}</span>
								{row.mainStar ? <em>化曜：{row.mainStar}</em> : null}
							</div>
						)) : yearInfoRows('年曜', transitYearText).map((row, idx)=>(
							<div key={`${row.main}-${idx}`}>
								<strong>{row.main}</strong>
								<span>{row.items.slice(1).join('、') || '主项'}</span>
								{row.yearStar ? <em>化禄：{row.yearStar}</em> : null}
							</div>
					))}
				</div>
			</Section>

			<Section title="神煞全表">
				<div className="horosa-guolao-moira-gods">
					{godHits.map((item)=>(
							<div className="horosa-guolao-moira-god" key={`${item.house}-${item.zi}`}>
								<strong>{item.house}</strong>
								<span>{item.zi} · {item.signName}</span>
								{safeList(item.gods).length ? <div>曜：{joinNames(item.gods)}</div> : (
									<>
										<div>吉：{joinNames(item.goodGods)}</div>
										<div>平：{joinNames(item.neutralGods)}</div>
										<div>忌：{joinNames(item.badGods)}</div>
										<div>太岁：{joinNames(item.taisuiGods)}</div>
									</>
								)}
							</div>
						))}
					{godHits.length === 0 ? <div className="horosa-guolao-moira-empty">当前盘未返回可摘录的七政神煞。</div> : null}
					</div>
				</Section>

				{transitGodHits.length ? (
					<Section title="流年神煞">
						<div className="horosa-guolao-moira-gods">
							{transitGodHits.map((item)=>(
								<div className="horosa-guolao-moira-god" key={`now-${item.house}-${item.zi}`}>
									<strong>{item.house}</strong>
									<span>{item.zi} · {item.signName}</span>
									<div>曜：{joinNames(item.gods || item.taisuiGods)}</div>
								</div>
							))}
						</div>
					</Section>
				) : null}

				<Section title="政余格局">
				{styleWarning ? <div className="horosa-guolao-moira-warning">{styleWarning}</div> : null}
				{patterns.length ? (
					<div className="horosa-guolao-moira-patterns">
						{patterns.map((item, idx)=>(
							<div className={`horosa-guolao-moira-pattern horosa-guolao-moira-pattern-${item.level || 'neutral'}`} key={`${item.name || 'pattern'}-${idx}`}>
								<div className="horosa-guolao-moira-pattern-head">
									<span>{levelText(item.level)}</span>
									<strong>{item.name}</strong>
								</div>
								<div className="horosa-guolao-moira-pattern-detail">{item.detail}</div>
							</div>
						))}
					</div>
				) : <div className="horosa-guolao-moira-empty">当前盘未命中已接入的 Moira 政余喜格/忌格。</div>}
			</Section>
		</div>
	);
}
