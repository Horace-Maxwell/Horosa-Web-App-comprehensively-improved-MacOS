// 风水 理气核心 · 字节级 golden 基准。
import {
	flyChart, sanheChangshengTable, qkgbPositions, zibaiYearStar, mingGua, mingGroup, val, idx,
} from '../liqiCore';
import { SHAN_ORDER, GONG_NAME } from '../fengshuiData';

describe('风水 理气核心 golden', ()=>{
	it('飞星原语 idx/val（飞泊步序 5→0…4→8）', ()=>{
		expect([1, 2, 3, 4, 5, 6, 7, 8, 9].map(idx)).toEqual([5, 6, 7, 8, 0, 1, 2, 3, 4]);
		expect(val(9, 5, true)).toBe(9);   // 9 入中顺飞，中宫=9（对照 grid「中 5 4／9」运盘 9）
	});

	it('玄空飞星 下卦：坐子向午(9运) == golden 基准（双星到坐·山反吟）', ()=>{
		const c = flyChart(9, '午');
		expect(c.zuoShan).toBe('子');
		expect(c.ge).toBe('双星到坐');
		// 九宫「山 向」逐宫对齐 golden（巽6 3 / 离1 8 / 坤8 1 / 震7 2 / 中5 4 / 兑3 6 / 艮2 7 / 坎9 9 / 乾4 5）。
		const exp = { 4: [6, 3], 9: [1, 8], 2: [8, 1], 3: [7, 2], 5: [5, 4], 7: [3, 6], 8: [2, 7], 1: [9, 9], 6: [4, 5] };
		for (let g = 1; g <= 9; g++) {
			expect([c.shanPan[g], c.xiangPan[g]]).toEqual(exp[g]);
		}
		// 运盘（9入中顺飞）。
		expect(c.yunPan[4]).toBe(8); expect(c.yunPan[9]).toBe(4); expect(c.yunPan[5]).toBe(9);
	});

	it('玄空飞星：坐壬向丙(9运)=双星到向·山伏吟（golden 基准）', ()=>{
		const c = flyChart(9, '丙');
		expect(c.zuoShan).toBe('壬');   // 向丙→坐壬
		expect(c.ge).toBe('双星到向');
		const exp = { 4: [4, 5], 9: [9, 9], 2: [2, 7], 3: [3, 6], 5: [5, 4], 7: [7, 2], 8: [8, 1], 1: [1, 8], 6: [6, 3] };
		for (let g = 1; g <= 9; g++) { expect([c.shanPan[g], c.xiangPan[g]]).toEqual(exp[g]); }
	});

	it('玄空飞星：24 山全运 flyChart 不抛、格局 ∈ 四格/侧局', ()=>{
		const GE = new Set(['旺山旺向', '上山下水', '双星到向', '双星到坐', '其他/侧局']);
		for (let yun = 1; yun <= 9; yun++) {
			for (const x of SHAN_ORDER) {
				const c = flyChart(yun, x);
				expect(c).toBeTruthy();
				expect(GE.has(c.ge)).toBe(true);
				// 九宫山/向盘均为 1-9 排列。
				const sv = Object.values(c.shanPan).sort((a, b)=>a - b);
				expect(sv).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
			}
		}
	});

	it('三合 十二长生四局全周 == golden 基准（12×4 字节级）', ()=>{
		const t = sanheChangshengTable();
		const got = t.map((r)=>`${r.shuangshan} ${r.火局} ${r.金局} ${r.水局} ${r.木局}`);
		expect(got).toEqual([
			'壬子 胎 死 帝旺 沐浴', '癸丑 养 墓 衰 冠带', '艮寅 长生 绝 病 临官', '甲卯 沐浴 胎 死 帝旺',
			'乙辰 冠带 养 墓 衰', '巽巳 临官 长生 绝 病', '丙午 帝旺 沐浴 胎 死', '丁未 衰 冠带 养 墓',
			'坤申 病 临官 长生 绝', '庚酉 死 帝旺 沐浴 胎', '辛戌 墓 衰 冠带 养', '乾亥 绝 病 临官 长生',
		]);
	});

	it('乾坤国宝 先后天位(八坐) == golden 基准（字节级）', ()=>{
		const exprows = {
			坎: ['坎(北)', '兑(西)', '坤(西南)'], 坤: ['坤(西南)', '坎(北)', '巽(东南)'],
			震: ['震(东)', '艮(东北)', '离(南)'], 巽: ['巽(东南)', '坤(西南)', '兑(西)'],
			乾: ['乾(西北)', '离(南)', '艮(东北)'], 兑: ['兑(西)', '巽(东南)', '坎(北)'],
			艮: ['艮(东北)', '乾(西北)', '震(东)'], 离: ['离(南)', '震(东)', '乾(西北)'],
		};
		Object.keys(exprows).forEach((z)=>{
			const p = qkgbPositions(z);
			expect([p.houtianFang, p.xianTianWei, p.houTianWei]).toEqual(exprows[z]);
		});
	});

	it('紫白 年入中 2014–2043 == golden 基准（字节级）', ()=>{
		const exp = { 2014: '四绿', 2015: '三碧', 2016: '二黑', 2017: '一白', 2018: '九紫', 2019: '八白',
			2020: '七赤', 2021: '六白', 2022: '五黄', 2023: '四绿', 2024: '三碧', 2025: '二黑',
			2026: '一白', 2027: '九紫', 2028: '八白', 2029: '七赤', 2030: '六白', 2031: '五黄',
			2032: '四绿', 2033: '三碧', 2034: '二黑', 2035: '一白', 2036: '九紫', 2037: '八白',
			2038: '七赤', 2039: '六白', 2040: '五黄', 2041: '四绿', 2042: '三碧', 2043: '二黑' };
		Object.keys(exp).forEach((y)=>{ expect(zibaiYearStar(+y).star).toBe(exp[y]); });
	});

	it('八宅 命卦（正统古法 算例）+ 东西四命组', ()=>{
		// 1984(甲子) 男=七赤兑(西四) / 女=八白艮(西四)；2000 男=九紫离(东四)/女=六白乾(西四)。
		expect(mingGua(1984, true)).toBe(7);
		expect(mingGua(1984, false)).toBe(8);
		expect(mingGroup(mingGua(1984, true))).toBe('西四命');
		// 命卦无 5：男 5→坤2、女 5→艮8（中宫寄）。
		for (let y = 1900; y <= 2043; y++) {
			expect(mingGua(y, true)).not.toBe(5);
			expect(mingGua(y, false)).not.toBe(5);
		}
		expect(Object.keys(GONG_NAME).length).toBe(9);
	});
});
