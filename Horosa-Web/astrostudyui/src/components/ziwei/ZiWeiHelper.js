import * as d3 from 'd3';
import * as ZWConst from '../../constants/ZWConst';

let DiZi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
let DiZiMap = new Map();

let HuaLuMap = new Map();
let HuaQuanMap = new Map();
let HuaKeMap = new Map();
let HuaJiMap = new Map();

let HuaMaps = [HuaLuMap, HuaQuanMap, HuaKeMap, HuaJiMap];

function initHuaMap(){
	let ganhua = ZWConst.SiHua.gan;
	for(let gan in ganhua){
		let stars = ganhua[gan];
		for(let i=0; i<4; i++){
			let map = HuaMaps[i];
			let hua = map.get(stars[i]);
			if(hua === undefined || hua === null){
				hua = gan;
			}else{
				hua = hua + gan;
			}
			map.set(stars[i], hua);
		}
	}
}

export function getHouseZiIndex(zi){
	if(ZWConst.HouseZiMap.size === 0){
		for(let i=0; i<ZWConst.HouseZi.length; i++){
			ZWConst.HouseZiMap.set(ZWConst.HouseZi[i], i);
		}
	}
	return ZWConst.HouseZiMap.get(zi);
}

export function getSiHua(star, gan){
	if(HuaLuMap.size === 0){
		initHuaMap();
	}

	let lu = HuaLuMap.get(star);
	let quan = HuaQuanMap.get(star);
	let ke = HuaKeMap.get(star);
	let ji = HuaJiMap.get(star);
	if(lu !== undefined && lu !== null && lu.indexOf(gan) >= 0){
		return ZWConst.SiHua.hua[0];
	}
	if(quan !== undefined && quan !== null && quan.indexOf(gan) >= 0){
		return ZWConst.SiHua.hua[1];
	}
	if(ke !== undefined && ke !== null && ke.indexOf(gan) >= 0){
		return ZWConst.SiHua.hua[2];
	}
	if(ji !== undefined && ji !== null && ji.indexOf(gan) >= 0){
		return ZWConst.SiHua.hua[3];
	}
	return null;
}

export function isDirCloseWise(chartobj){
	let gender = chartobj.gender;
	let polar = chartobj.yearPolar;
	if((gender === 'Male' && polar === 'Positive') 
		|| (gender === 'Female' && polar === 'Negative') ){
		return true;
	}
	return false;
}

export function getDouJun(zidou, yearzi){
	if(DiZiMap.size === 0){
		for(let i=0; i<DiZi.length; i++){
			DiZiMap.set(DiZi[i], i);
		}
	}
	let ziidx = DiZiMap.get(zidou);
	let yearziIdx = DiZiMap.get(yearzi);

	let idx = (ziidx + yearziIdx) % 12;
	return DiZi[idx];
}

// ===== 运限流曜（前端本地计算，与后端 ZiWeiLuck 同源；避免每次点击都打后端） =====
// 年干系：流禄存/流擎羊(禄前一)/流陀罗(禄后一)/流天魁/流天钺  （取自 ziweiyeargan.json）
const FlowLuStorePos = { '甲':'寅','乙':'卯','丙':'巳','丁':'午','戊':'巳','己':'午','庚':'申','辛':'酉','壬':'亥','癸':'子' };
const FlowKuiPos = { '甲':'丑','乙':'子','丙':'亥','丁':'亥','戊':'丑','己':'子','庚':'丑','辛':'午','壬':'卯','癸':'卯' };
const FlowYuePos = { '甲':'未','乙':'申','丙':'酉','丁':'酉','戊':'未','己':'申','庚':'未','辛':'寅','壬':'巳','癸':'巳' };
// 流昌/流曲：干系（与 ziweiliuchangqu.json 一致）
const FlowChangPos = { '甲':'巳','乙':'午','丙':'申','丁':'酉','戊':'申','己':'酉','庚':'亥','辛':'子','壬':'寅','癸':'卯' };
const FlowQuPos = { '甲':'酉','乙':'申','丙':'午','丁':'巳','戊':'午','己':'巳','庚':'寅','辛':'丑','壬':'戌','癸':'亥' };
// 流马：年支三合（申子辰马在寅、寅午戌马在申、巳酉丑马在亥、亥卯未马在巳）
const FlowMaPos = { '子':'寅','丑':'亥','寅':'申','卯':'巳','辰':'寅','巳':'亥','午':'申','未':'巳','申':'寅','酉':'亥','戌':'申','亥':'巳' };

// 返回某天干/地支的全套流曜 [{name, zhi}]
export function getFlowStars(gan, zhi){
	const out = [];
	const lu = FlowLuStorePos[gan];
	if(lu){
		out.push({ name: '流禄', zhi: lu });
		const li = getHouseZiIndex(lu);
		if(li !== undefined && li !== null){
			out.push({ name: '流羊', zhi: DiZi[(li + 1) % 12] });
			out.push({ name: '流陀', zhi: DiZi[(li + 11) % 12] });
		}
	}
	if(FlowKuiPos[gan]) out.push({ name: '流魁', zhi: FlowKuiPos[gan] });
	if(FlowYuePos[gan]) out.push({ name: '流钺', zhi: FlowYuePos[gan] });
	if(FlowChangPos[gan]) out.push({ name: '流昌', zhi: FlowChangPos[gan] });
	if(FlowQuPos[gan]) out.push({ name: '流曲', zhi: FlowQuPos[gan] });
	if(zhi && FlowMaPos[zhi]) out.push({ name: '流马', zhi: FlowMaPos[zhi] });
	return out;
}

// 干支地支 → 本命宫 index（houses[i] 地支 = DiZi[i]）
export function ziToHouseIndex(zhi){
	return getHouseZiIndex(zhi);
}

// 某天干在该命盘上的四化落宫：返回 [{star,hua,houseIndex}]
export function getLayerSihua(chartObj, gan){
	const res = [];
	if(!chartObj || !gan){
		return res;
	}
	const ganhua = ZWConst.SiHua.gan[gan];
	if(!ganhua){
		return res;
	}
	const huaNames = ZWConst.SiHua.hua; // [禄,权,科,忌]
	const houses = chartObj.houses || [];
	for(let h=0; h<4; h++){
		const starName = ganhua[h];
		let houseIndex = -1;
		for(let i=0; i<houses.length; i++){
			const groups = ['starsMain','starsAssist','starsEvil','starsOthersGood','starsOthersBad','starsSmall','stars'];
			let found = false;
			for(const key of groups){
				const arr = houses[i] && houses[i][key] ? houses[i][key] : [];
				if(arr.some((s)=> (typeof s === 'string' ? s : (s && s.name)) === starName)){
					found = true;
					break;
				}
			}
			if(found){ houseIndex = i; break; }
		}
		res.push({ star: starName, hua: huaNames[h], houseIndex });
	}
	return res;
}