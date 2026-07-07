// 七政四余「值难 / 职元 · 局主 · 天经 · 天元 · 地元 · 人元 / 地纬」8 系星值神煞。
// 这些是 Moira birth_year_info 里 50–57 号「星值」年曜标注(与地支落宫的神煞不同,值为某七政/四余星曜)。
// 数据 byte-perfect 抽自 Moira moira_t.prop:month_key_seq=值難、sky_key_seq=職元/局主/天經/天元/地元/人元、year_birth_earth_key=地緯;
// 繁→简仅 羅→罗、計→计。每行 12 字符,按 ZHI 序(子丑寅卯辰巳午未申酉戌亥)。
// 语义(照 prop 原注):
//   值难 = 月支查(某曜为月中之难)。
//   地纬 = 命宫支查(年干起五虎遁顺至命宫,地支所属五行)。
//   职元/局主/天经/天元/地元/人元 = 年干 × 命宫支 查(化禄/卦气/五虎遁诸法归一为查表)。
// 单一真值源:此 8 表 + resolveStarShensha;显示层(GuoLaoMoiraPanel)与 wheel 均取此。
import { GAN, ZHI } from './guolaoMoiraTables';

// 命宫黄道星座序→地支(白羊=戌 镜像,与 guolaoMoiraTables.smallLimitBranch 的 SIGN_BRANCH 同口径)。
const SIGN_BRANCH = ['戌', '酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑', '子', '亥'];

const idxZhi = (zhi) => ZHI.indexOf(`${zhi || ''}`.slice(-1));
const charAt = (rowStr, i) => (i >= 0 && i < 12 ? `${rowStr}`.charAt(i) : '');

// —— 值难(月支查)——
const ZHINAN_BY_MONTH = '金金日日月月火罗水孛木炁';
// —— 地纬(命宫支查)——
const DIWEI_BY_LIFE = '水土木木土火火土金金土水';
// —— 年干 × 命宫支 六系 ——
const BY_GAN = {
	职元: { 甲: '孛木金土月水炁计罗火孛火', 乙: '月水炁计罗火孛木孛木金土', 丙: '木金木金土月水炁计罗火孛', 丁: '水炁计罗火孛木金土金土月', 戊: '土月水炁计罗火孛木金土月', 己: '孛木金土月水月水炁计罗火', 庚: '月水炁水炁计罗火孛木金土', 辛: '土月水炁计炁计罗火孛木金', 壬: '罗火孛木金土月水炁计罗计', 癸: '金土月水炁计罗火罗火孛木' },
	局主: { 甲: '水炁计罗火孛木金土月水月', 乙: '火孛木金土月水炁水炁计罗', 丙: '炁计炁计罗火孛木金土月水', 丁: '孛木金土月水炁计罗计罗火', 戊: '罗火孛木金土月水炁计罗火', 己: '水炁计罗火孛火孛木金土月', 庚: '火孛木孛木金土月水炁计罗', 辛: '罗火孛木金木金土月水炁计', 壬: '土月水炁计罗火孛木金土金', 癸: '计罗火孛木金土月土月水炁' },
	天经: { 甲: '火火火火土土金金水水木木', 乙: '土土土土金金水水木木火火', 丙: '金金金金水水木木火火土土', 丁: '水水水水木木火火土土金金', 戊: '木木木木火火土土金金水水', 己: '火火火火土土金金水水木木', 庚: '土土土土金金水水木木火火', 辛: '金金金金水水木木火火土土', 壬: '水水水水木木火火土土金金', 癸: '木木木木火火土土金金水水' },
	天元: { 甲: '木金木金土月水炁计罗火孛', 乙: '土月土月水炁计罗火孛木金', 丙: '水炁水炁计罗火孛木金土月', 丁: '计罗计罗火孛木金土月水炁', 戊: '火孛火孛木金土月水炁计罗', 己: '木金木金土月水炁计罗火孛', 庚: '土月土月水炁计罗火孛木金', 辛: '水炁水炁计罗火孛木金土月', 壬: '计罗计罗火孛木金土月水炁', 癸: '火孛火孛木金土月水炁计罗' },
	地元: { 甲: '木木水水金金土土火火木木', 乙: '水水金金土土火火木火木木', 丙: '土火火火火木木水水金金土', 丁: '火木木水水金金土土火土火', 戊: '土土土火火木木水水金金土', 己: '木木水水金金土金土土火火', 庚: '水水金金金金土土火火木木', 辛: '火木木水水金水金金土土火', 壬: '水水金金土土火火木木水水', 癸: '金金土土火火木木水木水水' },
	人元: { 甲: '水木木火火土土金金水水水', 乙: '木火火土土金金水水木木木', 丙: '火土土金金水水木木火火火', 丁: '土金金水水木木火火土土土', 戊: '金水水木木火火土土金金金', 己: '水木木火火土土金金水水水', 庚: '木火火土土金金水水木木木', 辛: '火土土金金水水木木火火火', 壬: '土金金水水木木火火土土土', 癸: '金水水木木火火土土金金金' },
};

// 命宫黄经 → 命宫地支。
export function lifeSignBranch(lifeLon){
	const deg = (((Number(lifeLon) || 0) % 360) + 360) % 360;
	return SIGN_BRANCH[Math.floor(deg / 30) % 12];
}

// 出生公历年 → 年干。
export function yearGan(year){
	return GAN[((((Number(year) || 0) - 4) % 10) + 10) % 10];
}

// 解析并返回全部 8 系星值:[{key,name,star}]。缺输入的项 star 为 ''(照 Moira:数据缺则空)。
// 顺序照 Moira 编号 50–57:值难/职元/局主/天经/地纬/天元/地元/人元。
export function resolveStarShensha({ birthYear, lifeLon, monthZhi } = {}){
	const li = idxZhi(lifeSignBranch(lifeLon));
	const mi = idxZhi(monthZhi);
	const gan = yearGan(birthYear);
	const byGan = (name) => charAt(BY_GAN[name][gan] || '', li);
	return [
		{ key: 'zhinan', name: '值难', star: charAt(ZHINAN_BY_MONTH, mi) },
		{ key: 'zhiyuan', name: '职元', star: byGan('职元') },
		{ key: 'juzhu', name: '局主', star: byGan('局主') },
		{ key: 'tianjing', name: '天经', star: byGan('天经') },
		{ key: 'diwei', name: '地纬', star: charAt(DIWEI_BY_LIFE, li) },
		{ key: 'tianyuan', name: '天元', star: byGan('天元') },
		{ key: 'diyuan', name: '地元', star: byGan('地元') },
		{ key: 'renyuan', name: '人元', star: byGan('人元') },
	];
}

export const STAR_SHENSHA_NAMES = ['值难', '职元', '局主', '天经', '地纬', '天元', '地元', '人元'];
