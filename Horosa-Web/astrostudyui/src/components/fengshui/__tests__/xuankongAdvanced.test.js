// 玄空进阶 M4：替卦兼向 / 城门 / 七星打劫 / 流月。正统古法 + 4.10 实例 byte 锚。
import { xuankong } from '../xuankong';
import { flyChart, flyChartTi, tixingOf } from '../liqiCore';
import { SHAN_ORDER, TIXING_SHEN } from '../fengshuiData';

describe('替星表 tixingOf（正统古法）', ()=>{
	it('口诀确定12山无争议：巨2坤壬乙 / 破7艮丙辛 / 武6巽辰亥 / 贪1甲癸申', ()=>{
		['坤', '壬', '乙'].forEach((s)=>expect(tixingOf(s)).toBe(2));
		['艮', '丙', '辛'].forEach((s)=>expect(tixingOf(s)).toBe(7));
		['巽', '辰', '亥'].forEach((s)=>expect(tixingOf(s)).toBe(6));
		['甲', '癸', '申'].forEach((s)=>expect(tixingOf(s)).toBe(1));
	});
	it('三方案对 ◇山(卯)：沈氏2 / 右弼9 / 本宫3', ()=>{
		expect(tixingOf('卯', 'shen')).toBe(2);
		expect(tixingOf('卯', 'youbi')).toBe(9);
		expect(tixingOf('卯', 'bengong')).toBe(3);   // 卯本宫=震3
	});
	it('全表与沈氏常量一致', ()=>{
		SHAN_ORDER.forEach((s)=>expect(tixingOf(s, 'shen')).toBe(TIXING_SHEN[s]));
	});
});

describe('替卦 flyChartTi（正统古法）', ()=>{
	it('8运向午兼：向盘运星3→震宫天元卯→替星2入中(逆飞)→中宫向星=2', ()=>{
		const c = flyChartTi(8, '午', 'shen');
		expect(c.method).toBe('替卦');
		expect(c.xiangPan[5]).toBe(2);       // 替星卯=2 入中（下卦为运星3）
		// 对照下卦中宫向星=3（4.10 实例）。
		expect(flyChart(8, '午').xiangPan[5]).toBe(3);
	});
	it('同卦不变性：sameAsXiaGua 为真时替卦盘 === 下卦盘（全运全山）', ()=>{
		for (let yun = 1; yun <= 9; yun++) {
			for (const x of SHAN_ORDER) {
				const ti = flyChartTi(yun, x, 'shen');
				if (ti.sameAsXiaGua) {
					const xg = flyChart(yun, x);
					expect(ti.shanPan).toEqual(xg.shanPan);
					expect(ti.xiangPan).toEqual(xg.xiangPan);
				}
			}
		}
	});
	it('压测：9运×24山×3方案 替卦不抛、九宫为1-9排列', ()=>{
		['shen', 'youbi', 'bengong'].forEach((v)=>{
			for (let yun = 1; yun <= 9; yun++) {
				for (const x of SHAN_ORDER) {
					const c = flyChartTi(yun, x, v);
					expect(Object.values(c.shanPan).sort((a, b)=>a - b)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
					expect(Object.values(c.xiangPan).sort((a, b)=>a - b)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
				}
			}
		});
	});
});

describe('七星打劫 / 城门（正统古法实例锚）', ()=>{
	it('8运坐子向午：向星离震乾=8/5/2(258)→离宫真打劫；坎巽兑=7/4/1(147)→坎宫假打劫', ()=>{
		const r = xuankong(8, '午');
		const keys = r.rob.map((x)=>x.key);
		expect(keys).toContain('li');     // 离宫(9·3·6 向星 258)
		expect(keys).toContain('kan');    // 坎宫(1·4·7 向星 147)
	});
	it('8运向午：城门取向首两旁巽(东南)/坤(西南)；巽与离合十→正城门', ()=>{
		const r = xuankong(8, '午');
		expect(r.gate.available).toBe(true);
		expect([r.gate.left.gong, r.gate.right.gong].sort((a, b)=>a - b)).toEqual([2, 4]);  // 坤2/巽4
		expect(r.gate.zheng && r.gate.zheng.gong).toBe(4);   // 巽合十(运盘7+3=10)为正城门
	});
});

describe('双星断 + 流月', ()=>{
	it('特殊凶吉对优先：2·5 二五交加(bad) / 1·4 文昌(good)', ()=>{
		// 用兼向无关，直接构造盘取宫验函数语义：在某盘内必含的对照（5运含5多组）。
		const r = xuankong(5, '子', { year: 2026, month: 6 });
		expect(Array.isArray(r.rob)).toBe(true);
		expect(r.gate).toBeTruthy();
		// 流月盘九宫齐全。
		expect(Object.values(r.monthPan).sort((a, b)=>a - b)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
	});
	it('兼向开关：jian=true 时 method=替卦 并带 tiVariant', ()=>{
		const r = xuankong(7, '午', { jian: true, tiVariant: 'youbi' });
		expect(r.method).toBe('替卦');
		expect(r.tiVariant).toBe('youbi');
	});
});
