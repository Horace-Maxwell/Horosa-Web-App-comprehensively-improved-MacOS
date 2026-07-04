// 风水 QA 轮2:核心算法 vs正统堪舆诸家原文 byte 锚(直对古法原文)。
import { dayouNian } from '../bazhai';
import { sanheStageAt, flyChart, mingGua } from '../liqiCore';
import { monthCenter } from '../zibai';
import { qiankun } from '../qiankun';
import { jinsuo } from '../jinsuo';
import { SHAN_ORDER } from '../fengshuiData';

// 正统古法 八宅游年全表(伏位本卦 × 八方所得之星)—— 逐格抄录。
const YOUNIAN_MANUAL = {
	乾: { 坎: '六煞', 艮: '天医', 震: '五鬼', 巽: '祸害', 离: '绝命', 坤: '延年', 兑: '生气', 乾: '伏位' },
	坎: { 坎: '伏位', 艮: '五鬼', 震: '天医', 巽: '生气', 离: '延年', 坤: '绝命', 兑: '祸害', 乾: '六煞' },
	艮: { 坎: '五鬼', 艮: '伏位', 震: '六煞', 巽: '绝命', 离: '祸害', 坤: '生气', 兑: '延年', 乾: '天医' },
	震: { 坎: '天医', 艮: '六煞', 震: '伏位', 巽: '延年', 离: '生气', 坤: '祸害', 兑: '绝命', 乾: '五鬼' },
	巽: { 坎: '生气', 艮: '绝命', 震: '延年', 巽: '伏位', 离: '天医', 坤: '五鬼', 兑: '六煞', 乾: '祸害' },
	离: { 坎: '延年', 艮: '祸害', 震: '生气', 巽: '天医', 离: '伏位', 坤: '六煞', 兑: '五鬼', 乾: '绝命' },
	坤: { 坎: '绝命', 艮: '生气', 震: '祸害', 巽: '五鬼', 离: '六煞', 坤: '伏位', 兑: '天医', 乾: '延年' },
	兑: { 坎: '祸害', 艮: '延年', 震: '绝命', 巽: '六煞', 离: '五鬼', 坤: '天医', 兑: '伏位', 乾: '生气' },
};

describe('八宅大游年 翻卦变爻法 == 游年全表(8×8 全 64 格)', ()=>{
	Object.keys(YOUNIAN_MANUAL).forEach((fu)=>{
		it(`伏位 ${fu}：八方八星逐格对古法`, ()=>{
			const stars = dayouNian(fu);                       // {gong: {gua, name, ...}}
			const byGua = {};
			Object.values(stars).forEach((s)=>{ byGua[s.gua] = s.name; });
			Object.keys(YOUNIAN_MANUAL[fu]).forEach((fw)=>{
				expect(byGua[fw]).toBe(YOUNIAN_MANUAL[fu][fw]);
			});
		});
	});
});

describe('三合 十二长生四大局 == 古法(火长生寅/金巳/水申/木亥)', ()=>{
	it('四局长生位逐一对古法', ()=>{
		expect(sanheStageAt('寅', '火局')).toBe('长生');
		expect(sanheStageAt('巳', '金局')).toBe('长生');
		expect(sanheStageAt('申', '水局')).toBe('长生');
		expect(sanheStageAt('亥', '木局')).toBe('长生');
		// 帝旺位(长生后第4位):火午/金酉/水子/木卯。
		expect(sanheStageAt('午', '火局')).toBe('帝旺');
		expect(sanheStageAt('酉', '金局')).toBe('帝旺');
		expect(sanheStageAt('子', '水局')).toBe('帝旺');
		expect(sanheStageAt('卯', '木局')).toBe('帝旺');
		// 墓库位:火戌/金丑/水辰/木未。
		expect(sanheStageAt('戌', '火局')).toBe('墓');
		expect(sanheStageAt('丑', '金局')).toBe('墓');
		expect(sanheStageAt('辰', '水局')).toBe('墓');
		expect(sanheStageAt('未', '木局')).toBe('墓');
	});
});

// 正统古法 全九运24山下卦格局总表 —— 按运的格局分布计数(程序生成·已校验)。
function tallyGe(yun) {
	let wsw = 0; let ssxs = 0; let shuang = 0;
	for (const x of SHAN_ORDER) {
		const ge = flyChart(yun, x).ge;
		if (ge === '旺山旺向') { wsw++; }
		else if (ge === '上山下水') { ssxs++; }
		else { shuang++; }   // 双星到向/到坐
	}
	return { wsw, ssxs, shuang };
}
describe('玄空全九运格局分布 ==', ()=>{
	it('1运/9运:全双星(无旺山旺向/上山下水)', ()=>{
		expect(tallyGe(1)).toEqual({ wsw: 0, ssxs: 0, shuang: 24 });
		expect(tallyGe(9)).toEqual({ wsw: 0, ssxs: 0, shuang: 24 });
	});
	it('5运:旺山旺向12 + 上山下水12(五黄半分)', ()=>{
		expect(tallyGe(5)).toEqual({ wsw: 12, ssxs: 12, shuang: 0 });
	});
	it('2/3/4/6/7/8运:各 旺山旺向6 + 上山下水6 + 双星12', ()=>{
		[2, 3, 4, 6, 7, 8].forEach((yun)=>{
			expect(tallyGe(yun)).toEqual({ wsw: 6, ssxs: 6, shuang: 12 });
		});
	});
	it('4.10锚:8运子山午向=双星到向', ()=>{
		expect(flyChart(8, '午').ge).toBe('双星到向');
	});
});

describe('紫白月入中三 epoch ==(逐月逆退)', ()=>{
	it('子午卯酉年正月起八白 / 辰戌丑未年起五黄 / 寅申巳亥年起二黑', ()=>{
		expect(monthCenter(1900, 1)).toBe(8);   // 1900庚子(子)正月八白
		expect(monthCenter(1900, 2)).toBe(7);   // 逆退
		expect(monthCenter(1904, 1)).toBe(5);   // 1904甲辰(辰)正月五黄
		expect(monthCenter(1902, 1)).toBe(2);   // 1902壬寅(寅)正月二黑
	});
});

// 正统古法 乾坤国宝 先后天定位表(标准龙门八局,八坐山)。
const QKGB_MANUAL = {
	坎: ['兑(西)', '坤(西南)'], 坤: ['坎(北)', '巽(东南)'], 震: ['艮(东北)', '离(南)'], 巽: ['坤(西南)', '兑(西)'],
	乾: ['离(南)', '艮(东北)'], 兑: ['巽(东南)', '坎(北)'], 艮: ['乾(西北)', '震(东)'], 离: ['震(东)', '乾(西北)'],
};
describe('乾坤国宝 先后天位 ==(八坐山逐一)', ()=>{
	Object.keys(QKGB_MANUAL).forEach((zuo)=>{
		it(`坐${zuo}：先天位${QKGB_MANUAL[zuo][0]}/后天位${QKGB_MANUAL[zuo][1]}`, ()=>{
			const r = qiankun({ zuoGua: zuo });
			expect(r.xianTian).toBe(QKGB_MANUAL[zuo][0]);
			expect(r.houTian).toBe(QKGB_MANUAL[zuo][1]);
		});
	});
});

describe('八宅命卦 古法 ==(数字相加古法)', ()=>{
	it('古法实例 2005:男→巽(4)/女→坤(2)', ()=>{
		expect(mingGua(2005, true)).toBe(4);    // 11−7=4 巽
		expect(mingGua(2005, false)).toBe(2);   // 4+7=11→2 坤
	});
	it('数字根5特例:男11−5=寄坤(2);数字根9:男11−9=坤(2)', ()=>{
		expect(mingGua(1995, true)).toBe(2);     // 1995→数字根6→男11−6=5→寄坤2
		expect(mingGua(1980, true)).toBe(2);     // 1980→数字根9→男11−9=2 坤
	});
});

describe('金锁玉关 1234要砂/6789要水 ==', ()=>{
	it('坎(1)要砂:砂得位/水失位;离(9)要水:水得位/砂失位', ()=>{
		expect(jinsuo({ sectors: { 坎: 'sand' } }).palaces.find((p)=>p.gua === '坎').deWei).toBe(true);
		expect(jinsuo({ sectors: { 坎: 'water' } }).palaces.find((p)=>p.gua === '坎').deWei).toBe(false);
		expect(jinsuo({ sectors: { 离: 'water' } }).palaces.find((p)=>p.gua === '离').deWei).toBe(true);
		expect(jinsuo({ sectors: { 离: 'sand' } }).palaces.find((p)=>p.gua === '离').deWei).toBe(false);
	});
	it('1234(坎坤震巽)全要砂 / 6789(乾兑艮离)全要水', ()=>{
		['坎', '坤', '震', '巽'].forEach((g)=>expect(jinsuo({ sectors: { [g]: 'sand' } }).palaces.find((p)=>p.gua === g).deWei).toBe(true));
		['乾', '兑', '艮', '离'].forEach((g)=>expect(jinsuo({ sectors: { [g]: 'water' } }).palaces.find((p)=>p.gua === g).deWei).toBe(true));
	});
});
