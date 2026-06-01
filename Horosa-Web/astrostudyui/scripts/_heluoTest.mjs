/* eslint-disable no-console */
// Fixture tests for heluoLocal 起命. Run via: esbuild bundle → node.
import calc, { NAME_INDEX, daYun, liuNian, liuYue, liuRi, judge, transformHoutian, guaLines, solarTermHuagong, classifyErShu, zhongZong, shunFanShu, isXiongPair, mingGe } from '../src/utils/heluoLocal.js';

let pass = 0;
let fail = 0;
function eq(label, got, want) {
	const ok = got === want;
	console.log(`${ok ? '✓' : '✗'} ${label}: got=${got} want=${want}`);
	if (ok) pass += 1; else fail += 1;
}

// Fixture 1: 甲子·丁卯·庚申·庚辰, 男, 辰时 → 先天 天风姤, 元堂 上九(6)
const f1 = calc({
	fourPillars: { year: '甲子', month: '丁卯', day: '庚申', hour: '庚辰' },
	gender: '男', hourZhi: '辰', birthYear: 1924, monthZhi: '卯',
});
eq('F1 天数', f1.tian, 31);
eq('F1 地数', f1.di, 34);
eq('F1 天数卦', f1.tianGua, '乾');
eq('F1 地数卦', f1.diGua, '巽');
eq('F1 先天卦', f1.xian.name, '天風姤');
eq('F1 元堂', f1.xian.yuan, 6);

// Fixture 2: 丁巳·丙午·壬寅·辛丑, 阴男 → 先天 水风井 (上坎下巽)
const f2 = calc({
	fourPillars: { year: '丁巳', month: '丙午', day: '壬寅', hour: '辛丑' },
	gender: '男', hourZhi: '丑', birthYear: 1977, monthZhi: '午',
});
eq('F2 天数', f2.tian, 29);
eq('F2 地数', f2.di, 40);
eq('F2 天数卦', f2.tianGua, '巽');
eq('F2 地数卦', f2.diGua, '坎');
eq('F2 先天卦', f2.xian.name, '水風井');

// 64 卦索引完整性
eq('64卦覆盖', Object.keys(NAME_INDEX).length, 64);
eq('天风姤序', NAME_INDEX['天風姤'], 44);
eq('水风井序', NAME_INDEX['水風井'], 48);

// ── 后天卦推导 (翻元堂爻 + 移外卦入内) 参考实例：丙戌·丁酉·丙寅·癸巳 阳男 巳时 → 否上九 → 临六三 ──
const f3 = calc({
	fourPillars: { year: '丙戌', month: '丁酉', day: '丙寅', hour: '癸巳' },
	gender: '男', hourZhi: '巳', birthYear: 2006, monthZhi: '酉',
});
eq('F3 天数', f3.tian, 31);
eq('F3 地数', f3.di, 42);
eq('F3 先天卦', f3.xian.name, '天地否');
eq('F3 先天元堂', f3.xian.yuan, 6);
eq('F3 后天卦(翻爻+互换)', f3.hou.name, '地澤臨');
eq('F3 后天元堂', f3.hou.yuan, 3);
// F1 天风姤·元堂6 经翻爻+互换应得 风泽中孚·元堂3（与 男命例 一致）
eq('F1 后天卦', f1.hou.name, '風澤中孚');
eq('F1 后天元堂', f1.hou.yuan, 3);

// ── 大限 (天风姤·元堂6 → 先天主51年；后天 风泽中孚·元堂3 主52-99) ──
const xian = { name: '天風姤', up: '乾', low: '巽', lines: f1.xian.lines, yuan: 6 };
const hou = { name: '風澤中孚', up: '巽', low: '兌', lines: [1, 1, 0, 0, 1, 1], yuan: 3 };
const dy = daYun(xian, hou);
eq('大限·先天首段卦', dy.xian[0].gua, '天風姤');
eq('大限·先天首段爻', dy.xian[0].pos, 6);
eq('大限·先天首段年龄', `${dy.xian[0].ageStart}-${dy.xian[0].ageEnd}`, '1-9');
eq('大限·先天次段(初六)', `${dy.xian[1].pos}:${dy.xian[1].ageStart}-${dy.xian[1].ageEnd}`, '1:10-15');
eq('大限·先天三段(九二)', `${dy.xian[2].pos}:${dy.xian[2].ageStart}-${dy.xian[2].ageEnd}`, '2:16-24');
eq('大限·先天末段(九五)', `${dy.xian[5].pos}:${dy.xian[5].ageStart}-${dy.xian[5].ageEnd}`, '5:43-51');
eq('大限·先天止于51', dy.xianEndAge, 51);
eq('大限·后天起于52(六三)', `${dy.hou[0].pos}:${dy.hou[0].ageStart}`, '3:52');
eq('大限·后天止于99', dy.endAge, 99);

// ── 流年 (姤 上九 大限, 甲子起阳年 → 姤/讼/困/兑为泽/泽雷随/泽火革/水火既济/地火明夷) ──
const ln = liuNian({ gua: '天風姤', pos: 6, yang: true, years: 9, ageStart: 1 });
const expectGua = ['天風姤', '天水訟', '澤水困', '兌為澤', '澤雷隨', '澤火革', '水火既濟', '地火明夷'];
expectGua.forEach((g, i) => eq(`流年Y${i + 1}卦`, ln[i].gua, g));

// ── 命运篇 (壬子年命例: 先天澤地萃·元堂4, 后天地水師·元堂1, 丑月) ──
// 天元 壬=乾(命卦无乾→absent)；地元 子=坎(后天师含坎→present)；化工 丑→坎(present)。
const caseChart = {
	tian: 0, di: 0, yangLing: false,
	xian: { name: '澤地萃', up: '兌', low: '坤', lines: [0, 0, 0, 1, 1, 0], yuan: 4 },
	hou: { name: '地水師', up: '坤', low: '坎', lines: [0, 1, 0, 0, 0, 0], yuan: 1 },
};
const jg = judge(caseChart, { year: '壬子', month: '癸丑', day: '丁卯', hour: '甲辰' }, '丑');
eq('命运篇 天元卦', jg.yuan.tian.gua, '乾');
eq('命运篇 天元(命卦无乾)', jg.yuan.tian.present, false);
eq('命运篇 地元卦', jg.yuan.di.gua, '坎');
eq('命运篇 地元(后天师含坎)', jg.yuan.di.present, true);
eq('命运篇 化工卦', jg.huagong.guas.join(''), '坎');
eq('命运篇 化工present', jg.huagong.present.join(''), '坎');
eq('命运篇 葉(有元气/化工)', jg.xie, true);

// ── 三至尊卦 后天换卦特例 ──
// 坎為水[0,1,0,0,1,0] 元堂九五(5)：阴令→变而不易→地水師(元堂仍5)；阳令→正常翻爻+互换→水地比(元堂2)
const kanLines = guaLines('坎', '坎');
const zzYin = transformHoutian('坎為水', kanLines, 5, false);   // 阴令
const zzYang = transformHoutian('坎為水', kanLines, 5, true);   // 阳令
eq('三至尊 坎為水·九五·阴令(变而不易)', `${zzYin.name}/${zzYin.yuan}`, '地水師/5');
eq('三至尊 坎為水·九五·阳令(正常)', `${zzYang.name}/${zzYang.yuan}`, '水地比/2');
// 普通卦 否上九 阴令也应正常翻爻+互换(非三至尊) → 临六三
const fou = transformHoutian('天地否', guaLines('乾', '坤'), 6, false);
eq('普通 否·上九 后天', `${fou.name}/${fou.yuan}`, '地澤臨/3');

// ── 董鴻煦 参考盘全链核对：丙戌·丁酉·丙寅·癸巳 阳男 巳时 (2006-10-04) ──
const D = calc({ fourPillars: { year: '丙戌', month: '丁酉', day: '丙寅', hour: '癸巳' }, gender: '男', hourZhi: '巳', birthYear: 2006, monthZhi: '酉' });
eq('董 先天卦/元堂', `${D.xian.name}/${D.xian.yuan}`, '天地否/6');
eq('董 后天卦/元堂', `${D.hou.name}/${D.hou.yuan}`, '地澤臨/3');
// 大限：先天否 1-45(6段)，后天临 46起
const dyD = daYun(D.xian, D.hou, 2006);
eq('董 大限·先天止于', dyD.xianEndAge, 45);
eq('董 大限·先天段年龄', dyD.xian.map((s) => `${s.ageStart}-${s.ageEnd}`).join(','), '1-9,10-15,16-21,22-27,28-36,37-45');
eq('董 大限·后天起于', dyD.hou[0].ageStart, 46);
// 流年：否上九大限 → 否/遯/咸/革/夬/兑/节/临/损
const lnD = liuNian(dyD.xian[0], 2006);
eq('董 流年9卦序', lnD.map((y) => y.gua).join(' '), '天地否 天山遯 澤山咸 澤火革 澤天夬 兌為澤 水澤節 地澤臨 山澤損');
// 流年链式变爻（动爻自上一年往上一爻累变）—— 对照董盘截图：否初六/否六二/临六三/临六四
const lnSeq = (seg) => liuNian(seg, 2006).map((y) => y.gua).join(' ');
const lnPos = (seg) => liuNian(seg, 2006).map((y) => y.pos).join('');
eq('董 流年·否初六(大限2)卦', lnSeq(dyD.xian[1]), '天雷無妄 天澤履 乾為天 風天小畜 山天大畜 地天泰');
eq('董 流年·否初六(大限2)动爻', lnPos(dyD.xian[1]), '123456');
eq('董 流年·否六二(大限3)卦', lnSeq(dyD.xian[2]), '天水訟 天風姤 巽為風 山風蠱 地風升 地天泰');
eq('董 流年·否六二(大限3)动爻', lnPos(dyD.xian[2]), '234561');
eq('董 流年·临六三(后天1)卦', lnSeq(dyD.hou[0]), '地天泰 雷天大壯 澤天夬 乾為天 天風姤 天山遯');
eq('董 流年·临六三(后天1)动爻', lnPos(dyD.hou[0]), '345612');
eq('董 流年·临六四(后天2)卦', lnSeq(dyD.hou[1]), '雷澤歸妹 兌為澤 天澤履 天水訟 天地否 天山遯');
eq('董 流年·临六四(后天2)动爻', lnPos(dyD.hou[1]), '456123');
// 后天阳爻大限：临初九(9年，起于阴年乙未2075) —— 验应爻+链式+阴年首年
eq('董 流年·临初九(后天5)卦', lnSeq(dyD.hou[4]), '地水師 雷水解 雷澤歸妹 震為雷 雷火豐 地火明夷 水火既濟 風火家人 風山漸');
eq('董 流年·临初九(后天5)动爻', lnPos(dyD.hou[4]), '141234561');
// 流月（阳爻大限年）：2075师(动爻初六1) / 2076解(动爻九四4)，含阳月累变+阴月应爻
const ln5 = liuNian(dyD.hou[4], 2006);
eq('董 流月·2075师 正~九', liuYue(ln5[0].lines, ln5[0].pos).slice(0, 9).map((mo) => mo.gua).join(' '), '坤為地 水地比 地山謙 艮為山 雷山小過 雷火豐 澤山咸 澤風大過 天山遯');
eq('董 流月·2076解 正~九', liuYue(ln5[1].lines, ln5[1].pos).slice(0, 9).map((mo) => mo.gua).join(' '), '澤水困 澤地萃 天水訟 天風姤 天澤履 風澤中孚 天雷無妄 火雷噬嗑 天火同人');
// 流月（阴爻大限年）：2052大壯(动爻九四4)
const ln_dz = liuNian(dyD.hou[0], 2006)[1];
eq('董 流月·2052大壯 正~九', liuYue(ln_dz.lines, ln_dz.pos).slice(0, 9).map((mo) => mo.gua).join(' '), '澤天夬 澤火革 乾為天 天澤履 天風姤 巽為風 天山遯 火山旅 天地否');
// 流日·2052正月壬寅(月卦 夬·元堂九五) → 5块 乾/大過/革/兌/需，各6日、块内动爻初→上（对照董盘正月壬寅流日 02/03起）
const m2052_1 = liuYue(ln_dz.lines, ln_dz.pos)[0];
const lr2052 = liuRi(m2052_1.lines, m2052_1.pos);
eq('董 流日·2052正月 5块卦', [0, 6, 12, 18, 24].map((i) => lr2052[i].gua).join(' '), '乾為天 澤風大過 澤火革 兌為澤 水天需');
eq('董 流日·2052正月 30日+动爻', `${lr2052.length}|${lr2052[0].pos}${lr2052[5].pos}${lr2052[6].pos}${lr2052[29].pos}`, '30|1616');
// 流月：2007 流年=遯(动爻3) → 渐/家人/艮/蛊/谦/坤/明夷/丰/泰…
const lyD = liuYue(guaLines('乾', '艮'), 3);   // 天山遯, 元堂九三
eq('董 流月正~九月', lyD.slice(0, 9).map((mo) => mo.gua).join(' '), '風山漸 風火家人 艮為山 山風蠱 地山謙 坤為地 地火明夷 雷火豐 地天泰');
// 流日：二月流月=家人(元堂初九) → 5卦×6日, 块1小畜/块5既济, 每块动爻初→上
const lrD = liuRi(guaLines('巽', '離'), 1);    // 风火家人, 元堂初九
eq('董 流日30日', lrD.length, 30);
eq('董 流日块1卦/块5卦', `${lrD[0].gua}/${lrD[24].gua}`, '風天小畜/水火既濟');
eq('董 流日动爻初→上', `${lrD[0].pos}${lrD[5].pos}${lrD[6].pos}`, '161');   // 第1日初,第6日上,第7日(块2)初

// ── 模块A 流派开关（默认=现状·零回归；新流派为典籍候选，待算例标定）──
// A3 取化工法：立春→四方伯坎；土用期 土王寄坤艮(默认)补坤艮 / 直取四方伯仅坎
eq('A3 默认(土王)立春土用 化工', solarTermHuagong('立春', true).hg.join(''), '坎坤艮');
eq('A3 默认显式==缺省', solarTermHuagong('立春', true, { quHuaGong: 'tuWangKunGen' }).hg.join(''), solarTermHuagong('立春', true).hg.join(''));
eq('A3 直取四方伯 仅坎', solarTermHuagong('立春', true, { quHuaGong: 'siFangBoOnly' }).hg.join(''), '坎');
eq('A3 直取四方伯 tuyong置false', solarTermHuagong('立春', true, { quHuaGong: 'siFangBoOnly' }).tuyong, false);
eq('A3 非土用时两法一致', solarTermHuagong('夏至', false).hg.join(''), solarTermHuagong('夏至', false, { quHuaGong: 'siFangBoOnly' }).hg.join(''));

// ── Phase2 命运篇补充判断（G1 数名/G2 命格/G3 顺反数/G4 眾宗/G5 正反对凶）──
// G1 阴阳二数命名分类（九宫：天-25 × 地-30 符号）
eq('G1 31/34→陰陽相戰', classifyErShu(31, 34).primary, '陰陽相戰');
eq('G1 25/30→安和自寧', classifyErShu(25, 30).primary, '安和自寧');
eq('G1 25/36→孤陰背陽', classifyErShu(25, 36).primary, '孤陰背陽');
eq('G1 31/30→孤陽背陰', classifyErShu(31, 30).primary, '孤陽背陰');
eq('G1 18/36→以弱敵強', classifyErShu(18, 36).primary, '以弱敵強');
eq('G1 18/36 severity 天数不足', classifyErShu(18, 36).severity.join(','), '天數不足');
// G4 眾宗/眾疾（天风姤 5阳1阴=[0,1,1,1,1,1]）
eq('G4 元堂坐独阴=眾宗', zhongZong([0, 1, 1, 1, 1, 1], 1), '眾宗');
eq('G4 元堂非独阴=眾疾', zhongZong([0, 1, 1, 1, 1, 1], 6), '眾疾');
eq('G4 非5:1不适用', zhongZong([1, 1, 0, 0, 1, 1], 3), '');
// G3 顺/反数领命
eq('G3 阳令天数领=顺', shunFanShu(40, 20, true).shun, true);
eq('G3 阳令地数领=反', shunFanShu(20, 40, true).shun, false);
eq('G3 阴令地数领=顺', shunFanShu(20, 40, false).shun, true);
// G5 正/反对体凶
eq('G5 乾↔坤=正對體', isXiongPair([1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0]), '正對體');
eq('G5 同卦不算', isXiongPair([1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]), '');
// G2 看命大法命格（复用壬子命运篇 caseChart + jg；smoke 结构 + 计数范围）
const mg = mingGe(caseChart, jg);
eq('G2 jiCount∈[0,12]', mg.jiCount >= 0 && mg.jiCount <= 12, true);
eq('G2 xiongCount∈[0,12]', mg.xiongCount >= 0 && mg.xiongCount <= 12, true);
eq('G2 命格档为字符串', typeof mg.jiGe === 'string' && typeof mg.xiongGe === 'string', true);

console.log(`\n${pass} passed, ${fail} failed`);
if (fail) process.exit(1);
