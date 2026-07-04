// 七政四余 行运 golden(guolaoTransit,据古籍 §10):洞微大限/小限/月限/童限。
import { computeDongwei, computeXiaoxian, computeYuexian, computeTongxian } from '../guolaoTransit';

describe('洞微大限(§10.1 · WP-E 捷法重生成)', () => {
	// WP-E:据《古今星制之别考》ch.3-4 捷法订正——出限虚岁 = 10 + 太阳宫内度/3 + 月份/12,不 floor;逐宫飞星吊度。
	test('命宫顺行各宫年数表(命宫15相貌10…疾厄7,共12宫)', () => {
		const d = computeDongwei(9);   // 太阳本宫 9°,无月份 → 10 + 9/3 = 13
		expect(d.startAge).toBe(13);
		expect(d.rows[0].palace).toBe('命宫');
		expect(d.rows[0].years).toBe(15);
		expect(d.rows[0].fromAge).toBe(13);
		expect(d.rows[0].toAge).toBe(28);
		expect(d.rows[1].palace).toBe('相貌');
		expect(d.rows[1].years).toBe(10);
		expect(d.rows[1].fromAge).toBe(28);
		expect(d.rows.length).toBe(12);
		expect(d.rows[11].palace).toBe('疾厄');
	});
	test('不 floor + 月份项:0°→10岁;29°→19.67岁;太阳19.5°+8月→17.17岁(PDF worked-example 17岁2月)', () => {
		expect(computeDongwei(0).startAge).toBe(10);
		expect(computeDongwei(29).startAge).toBe(19.67);    // 10+29/3,不 floor(旧 floor 给 19)
		expect(computeDongwei(2.9).startAge).toBe(10.97);   // 10+2.9/3,不 floor
		// PDF p12 worked-example:太阳巳宫 19.50°、8 月(酉月)生 → 17 岁 2 月出限 = 17.167 岁。
		expect(computeDongwei(19.5, 8).startAge).toBe(17.17);
	});
	test('飞星吊度:命宫(15年)每年 30/15=2°,逐岁链式;入度=太阳宫内度', () => {
		const d = computeDongwei(9);
		expect(d.rows[0].perYearDeg).toBe(2);            // 30/15
		expect(d.rows[0].entryDeg).toBe(9);              // 命宫入度=太阳宫内度
		expect(d.rows[0].diaodu[0]).toEqual({ age: 13, deg: 9 });   // 第一岁:9°
		expect(d.rows[0].diaodu[1]).toEqual({ age: 14, deg: 11 });  // 次岁:9+2
		expect(d.rows[1].perYearDeg).toBe(3);            // 相貌 30/10=3
	});
});

describe('小限(§10.2:生年支加命宫逆数)', () => {
	test('age1=命宫宫支;age2财帛;age3兄弟;逆行一宫', () => {
		// 命宫午(idx6):age1=午(命宫)、age2=巳(财帛,逆)、age3=辰(兄弟)
		expect(computeXiaoxian('午', 1)).toEqual({ age: 1, palaceZi: '午', palaceName: '命宫' });
		expect(computeXiaoxian('午', 2)).toEqual({ age: 2, palaceZi: '巳', palaceName: '财帛' });
		expect(computeXiaoxian('午', 3)).toEqual({ age: 3, palaceZi: '辰', palaceName: '兄弟' });
		// 13 岁回命宫(12 年一轮)
		expect(computeXiaoxian('午', 13).palaceZi).toBe('午');
		expect(computeXiaoxian('午', 13).palaceName).toBe('命宫');
	});
	test('命宫子(idx0):age2=亥逆', () => {
		expect(computeXiaoxian('子', 1).palaceZi).toBe('子');
		expect(computeXiaoxian('子', 2).palaceZi).toBe('亥');
	});
	test('zi 含宫后缀容错;缺数据→null', () => {
		expect(computeXiaoxian('午宫', 1).palaceZi).toBe('午');
		expect(computeXiaoxian('', 1)).toBe(null);
	});
});

describe('月限 + 童限(§10.2)', () => {
	test('月限:小限宫起生月逆寻 + 宫名(防 undefined 回归)', () => {
		// 命午、age1→小限午;正月(1)→午、二月→巳(逆)
		expect(computeYuexian('午', 1, 1).palaceZi).toBe('午');
		expect(computeYuexian('午', 1, 2).palaceZi).toBe('巳');
		// palaceName 必须有(此前漏返致面板「undefined（酉）」)
		expect(computeYuexian('午', 1, 1).palaceName).toBe('命宫');   // 午=命宫
		expect(computeYuexian('午', 1, 2).palaceName).toBe('财帛');   // 巳=财帛(逆布)
		expect(computeYuexian('午', 1, 8).palaceName).toBeTruthy();   // 任意月不 undefined
	});
	test('童限:命财疾妻福顺排;出限≈逆至中气三日一年+10', () => {
		const t = computeTongxian(45);   // 太阳45°:距上一中气(45=15×3)0° → 出限10岁
		expect(t.palaces).toEqual(['命宫', '财帛', '疾厄', '妻妾', '福德']);
		expect(t.exitAge).toBe(10);
		expect(t.baseVariant).toBe('tong10');   // 默认通行十年
		const t2 = computeTongxian(50);   // 50 mod 15 = 5° → 5/3+10 ≈ 11.7
		expect(t2.exitAge).toBeCloseTo(11.7, 1);
	});
	test('童限基数分歧做成选项(古9/通行10默认/虚11·早不过11晚不过20)', () => {
		// 默认零回归:缺/无效 variant 均回退 tong10(=现状)。
		expect(computeTongxian(45, 'bad').exitAge).toBe(10);
		expect(computeTongxian(45, undefined).exitAge).toBe(10);
		// gu9 古九岁:base 9。
		expect(computeTongxian(45, 'gu9').exitAge).toBe(9);
		expect(computeTongxian(50, 'gu9').exitAge).toBeCloseTo(10.7, 1);
		// xu11 虚十一:base 11 + 早不过11晚不过20 界钳。
		expect(computeTongxian(45, 'xu11').exitAge).toBe(11);   // 0/3+11=11,界钳下限
		expect(computeTongxian(50, 'xu11').exitAge).toBeCloseTo(12.7, 1);   // 5/3+11
		expect(computeTongxian(45, 'xu11').baseVariant).toBe('xu11');
	});
});
