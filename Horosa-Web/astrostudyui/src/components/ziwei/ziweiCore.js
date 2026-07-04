// 紫微斗数 · 排盘核心算法（纯函数、确定性、与农历层解耦）
// =====================================================================
// 本文件只放「给定 干支/月日时/局数 → 宫位/星曜落宫」的纯算法，便于脱离农历做 golden 单测
// （对齐标准自检锚点；与现 Java ZiWeiChart 同算法）。
// 农历(birth→干支/月日时)、杂曜大表、流派开关 由上层 ZiweiCalc.js 组装，不在此文件。
//
// index 约定: 子=0 丑=1 寅=2 卯=3 辰=4 巳=5 午=6 未=7 申=8 酉=9 戌=10 亥=11；顺=+1 逆=-1。
import { NaYin } from '../../constants/ZWConst';

export const ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
export const GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];

export function z(i){ return ZHI[((i % 12) + 12) % 12]; }
export function zi(s){ return ZHI.indexOf(s); }
export function gi(g){ return GAN.indexOf(g); }
export function isYangGan(g){ return gi(g) % 2 === 0; }   // 甲丙戊庚壬=阳
export function isYangZhi(zhiIndex){ return (((zhiIndex % 12) + 12) % 12) % 2 === 0; }  // 子寅辰午申戌=阳

// 五虎遁：年干 → 寅宫天干（与 ZWConst.WuHuDun 同）。
export const WUHU_YIN = {
	甲: '丙', 己: '丙', 乙: '戊', 庚: '戊', 丙: '庚', 辛: '庚', 丁: '壬', 壬: '壬', 戊: '甲', 癸: '甲',
};
// 五行局
export const WUXING_JU = { 水: 2, 木: 3, 金: 4, 土: 5, 火: 6 };
export const JU_NAME = { 2: '水二局', 3: '木三局', 4: '金四局', 5: '土五局', 6: '火六局' };
// 长生十二神 + 各局起宫（古籍：水二申/木三亥/金四巳/土五申/火六寅）。
export const CHANGSHENG_12 = ['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养'];
export const CHANGSHENG_START = { 2: '申', 3: '亥', 4: '巳', 5: '申', 6: '寅' };
// 十二宫名（自命宫起逆时针）
export const HOUSES = ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄', '迁移', '奴仆', '官禄', '田宅', '福德', '父母'];
// 紫微系（自紫微逆行）+ 天府系（自天府顺行），步长与 ziweistarsmain.json 一致。
export const NORTH_MAIN_STEP = { 紫微: 0, 天机: -1, 太阳: -3, 武曲: -4, 天同: -5, 廉贞: -8 };
export const SOUTH_MAIN_STEP = { 天府: 0, 太阴: 1, 贪狼: 2, 巨门: 3, 天相: 4, 天梁: 5, 七杀: 6, 破军: 10 };

// 纳音五行（取纳音名末字＝五行）→ 五行局数。
export function nayinElement(gan, zhiIndex){
	const ganzi = gan + z(zhiIndex);
	const ny = NaYin[ganzi];
	if(!ny){ return null; }
	return ny.charAt(ny.length - 1);   // 海中金→金 / 炉中火→火 …
}
export function wuxingJu(gan, zhiIndex){
	const elem = nayinElement(gan, zhiIndex);
	const ju = WUXING_JU[elem];
	return ju ? { ju, juText: JU_NAME[ju], element: elem } : null;
}

// 十二宫天干（五虎遁，自寅起顺布；因 10 干配 12 支 → 子寅同干、丑卯同干）。返回 idx→宫干。
// 与 Java setupHouseGanZi 一致：寅(2)=寅干起点，卯(3)=+1…亥(11)=+9，子(0)=+10≡寅干，丑(1)=+11≡寅干+1。
export function palaceGans(yearGan){
	const start = gi(WUHU_YIN[yearGan]);
	const out = {};
	out[0] = GAN[(start + 10) % 10];   // 子
	out[1] = GAN[(start + 11) % 10];   // 丑
	for(let i = 2; i < 12; i++){ out[i] = GAN[(start + i - 2) % 10]; }   // 寅起顺布
	return out;
}

// 命宫 / 身宫：寅起正月顺数至生月→生月宫；再起子时，命逆数至生时、身顺数至生时。
export function mingGong(month, hourIndex){ return ((2 + (month - 1) - hourIndex) % 12 + 12) % 12; }
export function shenGong(month, hourIndex){ return ((2 + (month - 1) + hourIndex) % 12) % 12; }

// 紫微定位（局数除生日，进退补数法；与 Java setupZiWeiPos / 标准紫微定位法 一致）。
export function ziweiPos(day, ju){
	const q = Math.floor(day / ju);
	const r = day % ju;
	let bu;
	let shang;
	if(r === 0){ bu = 0; shang = q; }
	else { bu = ju - r; shang = q + 1; }
	const base = (2 + (shang - 1)) % 12;     // 寅(=2) 起，商=1 在寅
	return bu % 2 === 0 ? ((base + bu) % 12) : (((base - bu) % 12) + 12) % 12;
}
// 天府（与紫微对称于寅申一线）
export function tianfuPos(ziweiIdx){ return ((4 - ziweiIdx) % 12 + 12) % 12; }
// 十四正曜落宫：{星名: idx}
export function fourteenStars(ziweiIdx){
	const tf = tianfuPos(ziweiIdx);
	const out = {};
	Object.keys(NORTH_MAIN_STEP).forEach((s)=>{ out[s] = (((ziweiIdx + NORTH_MAIN_STEP[s]) % 12) + 12) % 12; });
	Object.keys(SOUTH_MAIN_STEP).forEach((s)=>{ out[s] = (((tf + SOUTH_MAIN_STEP[s]) % 12) + 12) % 12; });
	return out;
}

// 阳男阴女 / 阴男阳女：顺(clockwise)/逆。性别 male=true、yearGan 阳干 → 顺。
export function isClockwise(yearGan, male){
	const yang = isYangGan(yearGan);
	return (yang && male) || (!yang && !male);
}

// 长生十二神：按五行局起宫，阳男阴女顺、阴男阳女逆。返回 idx→神名。
export function changsheng12(ju, yearGan, male){
	const start = zi(CHANGSHENG_START[ju]);
	const fwd = isClockwise(yearGan, male);
	const out = {};
	for(let i = 0; i < 12; i++){
		const idx = fwd ? (((start + i) % 12)) : ((((start - i) % 12) + 12) % 12);
		out[idx] = CHANGSHENG_12[i];
	}
	return out;
}

// 大限：第1限落命宫(虚岁=局数起)，阳男阴女顺/阴男阳女逆，每宫 span 年（默认10）。
// 返回 idx→[起虚岁, 讫虚岁]。与现 Java direction[] 同：clockwise 命宫=ju..ju+9，逆同。
export function daxianRanges(lifeIdx, ju, yearGan, male, span = 10){
	const fwd = isClockwise(yearGan, male);
	const out = {};
	for(let k = 0; k < 12; k++){
		const idx = fwd ? (((lifeIdx + k) % 12)) : ((((lifeIdx - k) % 12) + 12) % 12);
		const start = ju + span * k;
		out[idx] = [start, start + span - 1];
	}
	return out;
}
