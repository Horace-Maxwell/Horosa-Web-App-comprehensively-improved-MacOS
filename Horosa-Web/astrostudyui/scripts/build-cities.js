/* eslint-disable no-console */
// 地点选择器全量城市库 builder。
// 两个数据源 → 合并去重 → 输出短键数组到 src/data/citiesFull.json(动态懒加载,不进主 bundle)。
//   1) vendor/kinastro/tools/cities/cities.json   世界城市(英文),筛 pop 阈值;字段 {name,country,admin1,admin2,lat,lon,pop}
//   2) vendor/kinastro/tools/cities/china_cities.json 中国省/市/区中文层级树;字段 {name, center{longitude,latitude}, districts[]}
// 输出条目短键:{ n: 显示名, e: 英文名(中国城市为''), r: 国家/上级名, y: lat, x: lon }
// 运行:cd Horosa-Web/astrostudyui && node scripts/build-cities.js
const fs = require('fs');
const path = require('path');

const CITIES_DIR = path.join(__dirname, '..', '..', 'vendor', 'kinastro', 'tools', 'cities');
const WORLD_SRC = path.join(CITIES_DIR, 'cities.json');
const CHINA_SRC = path.join(CITIES_DIR, 'china_cities.json');
const OUT = path.join(__dirname, '..', 'src', 'data', 'citiesFull.json');

// 体积上限(字节);超过则把世界城市阈值升到 POP_THRESHOLD_HI 重新构建。
const SIZE_LIMIT = 2.5 * 1024 * 1024;
const POP_THRESHOLD_LO = 15000;
const POP_THRESHOLD_HI = 30000;

function num(v){
	const n = Number(v);
	return Number.isFinite(n) ? n : null;
}

// 世界城市 → 短键条目数组(按 pop 阈值过滤)。
function buildWorld(popThreshold){
	const raw = JSON.parse(fs.readFileSync(WORLD_SRC, 'utf8'));
	const out = [];
	for(const c of raw){
		const pop = num(c.pop);
		if(pop === null || pop < popThreshold){
			continue;
		}
		const lat = num(c.lat);
		const lon = num(c.lon);
		const name = `${c.name || ''}`.trim();
		if(lat === null || lon === null || !name){
			continue;
		}
		out.push({ n: name, e: name, r: `${c.country || ''}`.trim(), y: lat, x: lon });
	}
	return out;
}

// 中国层级树 → 扁平短键条目(省/市/区全收,跳过根国家节点)。r = 上级名。
function buildChina(){
	const root = JSON.parse(fs.readFileSync(CHINA_SRC, 'utf8'));
	const out = [];
	const walk = (node, parentName)=>{
		const name = `${node.name || ''}`.trim();
		const center = node.center || {};
		const lat = num(center.latitude);
		const lon = num(center.longitude);
		// 根国家节点不收(parentName 为空 = 根);其余有名+有坐标即收。
		if(parentName && name && lat !== null && lon !== null){
			out.push({ n: name, e: '', r: parentName, y: lat, x: lon });
		}
		const kids = Array.isArray(node.districts) ? node.districts : [];
		for(const k of kids){
			walk(k, name || parentName);
		}
	};
	walk(root, '');
	return out;
}

// 合并去重:key = 显示名 + 四舍五入坐标(2 位)。中国(中文)优先保留。
function merge(china, world){
	const map = new Map();
	const keyOf = (it)=>`${it.n}|${it.y.toFixed(2)}|${it.x.toFixed(2)}`;
	for(const it of china){
		map.set(keyOf(it), it);
	}
	for(const it of world){
		const k = keyOf(it);
		if(!map.has(k)){
			map.set(k, it);
		}
	}
	return Array.from(map.values());
}

function build(popThreshold){
	const china = buildChina();
	const world = buildWorld(popThreshold);
	const merged = merge(china, world);
	// 坐标保留 5 位小数控体积(约 1m 精度,远超城市选点所需)。
	for(const it of merged){
		it.y = Number(it.y.toFixed(5));
		it.x = Number(it.x.toFixed(5));
	}
	return { merged, chinaCount: china.length, worldCount: world.length };
}

function main(){
	let popThreshold = POP_THRESHOLD_LO;
	let res = build(popThreshold);
	let json = JSON.stringify(res.merged);
	if(Buffer.byteLength(json, 'utf8') > SIZE_LIMIT){
		console.log(`[build-cities] 体积超限(${(Buffer.byteLength(json, 'utf8') / 1024 / 1024).toFixed(2)}MB),世界城市阈值升至 pop>=${POP_THRESHOLD_HI} 重建`);
		popThreshold = POP_THRESHOLD_HI;
		res = build(popThreshold);
		json = JSON.stringify(res.merged);
	}
	fs.writeFileSync(OUT, json);
	const sizeMB = (Buffer.byteLength(json, 'utf8') / 1024 / 1024).toFixed(2);
	console.log('[build-cities] 完成');
	console.log(`  世界城市(pop>=${popThreshold}):${res.worldCount} 条`);
	console.log(`  中国省/市/区:${res.chinaCount} 条`);
	console.log(`  合并去重后:${res.merged.length} 条`);
	console.log(`  输出:${OUT}`);
	console.log(`  体积:${sizeMB}MB`);
}

main();
