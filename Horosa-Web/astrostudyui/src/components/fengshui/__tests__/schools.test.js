// 三合 / 紫白 / 乾坤国宝 模块（包 liqiCore golden 核心 + 断事）。
import { sanhe, juByShuiKou } from '../sanhe';
import { zibai, monthCenter } from '../zibai';
import { qiankun } from '../qiankun';

describe('三合 sanhe', ()=>{
	it('水口定局：戌→火局、丑→金局、辰→水局、未→木局', ()=>{
		expect(juByShuiKou('戌')).toBe('火局');
		expect(juByShuiKou('丑')).toBe('金局');
		expect(juByShuiKou('辰')).toBe('水局');
		expect(juByShuiKou('未')).toBe('木局');
		expect(juByShuiKou('子')).toBe(null);   // 非墓库山
	});
	it('火局长生环 == golden(golden 基准 火局列)：双山逐位长生阶 + 吉凶', ()=>{
		const r = sanhe({ shuiKou: '戌', waterFlow: 'leftToRight' });
		expect(r.available).toBe(true);
		expect(r.ju).toBe('火局');
		const byShuang = {};
		r.ring.forEach((c)=>{ byShuang[c.shuangshan] = c.stage; });
		// golden 基准 火局列：壬子胎/丙午帝旺/艮寅长生/坤申病…
		expect(byShuang['丙午']).toBe('帝旺');
		expect(byShuang['艮寅']).toBe('长生');
		expect(byShuang['壬子']).toBe('胎');
		expect(byShuang['坤申']).toBe('病');
		// 左水倒右 → 正旺向(帝旺=丙午)。
		expect(r.xiangFa.type).toBe('正旺向');
		expect(r.xiangFa.shuangshan).toBe('丙午');
	});
});

describe('紫白 zibai', ()=>{
	it('年入中 == golden：2024 三碧、2026 一白', ()=>{
		expect(zibai({ year: 2024 }).yearCenterStar).toBe('三碧');
		expect(zibai({ year: 2026 }).yearCenterStar).toBe('一白');
		const z = zibai({ year: 2024 });
		expect(z.yearPalaces.length).toBe(9);
		// 九宫星 1-9 排列;吉凶标注齐。
		expect(z.yearPalaces.map((p)=>p.star).sort((a, b)=>a - b)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
		z.yearPalaces.forEach((p)=>{ expect(['good', 'bad']).toContain(p.jx); });
	});
	it('月入中：子午卯酉年正月起八白逐月逆退', ()=>{
		// 2024=甲辰年(辰组)→正月起五黄;2023=癸卯(卯组)→正月起八白。
		expect(monthCenter(2023, 1)).toBe(8);
		expect(monthCenter(2023, 2)).toBe(7);   // 逆退
		expect(zibai({ year: 2024, month: 1 }).monthPalaces.length).toBe(9);
	});
});

describe('乾坤国宝 qiankun', ()=>{
	it('坐坎 先后天位 == golden(golden 基准)：先天兑(西)、后天坤(西南)', ()=>{
		const r = qiankun({ zuoGua: '坎', waters: { xianTian: 'come', houTian: 'come', anJie: 'go', tianJie: 'go' } });
		expect(r.available).toBe(true);
		expect(r.xianTian).toBe('兑(西)');
		expect(r.houTian).toBe('坤(西南)');
		// 来去水断 + 合局(7.B.10：先后天来水+案劫天劫去水+地刑无水)。
		expect(r.heJu).toBe(true);
		const xt = r.positions.find((p)=>p.key === 'xianTian');
		expect(xt.result).toMatch(/得水|旺/);
	});
	it('八坐先后天位齐全不抛', ()=>{
		['坎', '坤', '震', '巽', '乾', '兑', '艮', '离'].forEach((z)=>{
			const r = qiankun({ zuoGua: z });
			expect(r.available).toBe(true);
			expect(r.positions.length).toBeGreaterThanOrEqual(3);
		});
	});
});
