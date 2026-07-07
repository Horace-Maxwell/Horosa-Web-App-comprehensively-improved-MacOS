// 🔴 百六大限锚点金标(照 Moira ChartData.getLimitDegree 第 3921 行):
//   degree_offset = floor(life_sign_pos/30)*30 + 30 —— 1 岁起于「命宫整宫界」而非精确命度。
// 历史 bug:锚在精确命度,整盘偏 (30 − 命度宫内度) 度(用户对照 Moira 原软件实测发现)。
import { moiraLimitAnchor, moiraLimitAgeOffset, moiraLimitDegreeForAge } from '../GuoLaoMoiraWheel';

describe('百六大限锚点 = 命宫整宫界(照 Moira getLimitDegree,非精确命度)', ()=>{
	test('锚点 = floor(命度/30)*30 + 30(整宫界高边,30° 对齐)', ()=>{
		expect(moiraLimitAnchor(250.713)).toBe(270); // 命度在摩羯(240~270)→ 锚 270
		expect(moiraLimitAnchor(0)).toBe(30);         // 白羊 0° → 锚 30
		expect(moiraLimitAnchor(29.9)).toBe(30);      // 仍白羊 → 锚 30
		expect(moiraLimitAnchor(30)).toBe(60);        // 金牛起 → 锚 60
		expect(moiraLimitAnchor(359.9)).toBe(360 % 360 === 0 ? 0 : 360); // 双鱼末 → 锚 360→0
	});

	test('1 岁 = 锚点(命宫整宫界),不是精确命度', ()=>{
		// 命度 250.713(宫内度 10.713):Moira 1 岁在 270(宫界),旧 bug 会给 250.713(命度)。
		expect(moiraLimitDegreeForAge(250.713, 1)).toBeCloseTo(270, 6);
		expect(moiraLimitDegreeForAge(250.713, 1)).not.toBeCloseTo(250.713, 1);
	});

	test('童限岁末 = 命宫整宫起(锚点 − 30);随岁减度(反向排限)', ()=>{
		const life = 250.713;
		const childYear = 9 + (250.713 % 30) / 3; // 12.571(不四舍)
		// 1 + childYear 岁:消耗首宫满 30° → 度 = 270 − 30 = 240(命宫整宫起,摩羯 0°)。
		expect(moiraLimitDegreeForAge(life, 1 + childYear)).toBeCloseTo(240, 4);
		// 度数随岁增而减(反向)。
		expect(moiraLimitDegreeForAge(life, 5)).toBeLessThan(270);
		expect(moiraLimitDegreeForAge(life, 5)).toBeGreaterThan(240);
	});

	test('偏移 s 累计:1 岁=0、childYear+1 岁≈30、满盘→360', ()=>{
		const life = 60; // 双子 0°,宫内度 0 → childYear=9
		expect(moiraLimitAgeOffset(life, 1)).toBeCloseTo(0, 6);
		expect(moiraLimitAgeOffset(life, 1 + 9)).toBeCloseTo(30, 4);      // 首宫 9 年满 → 30°
		expect(moiraLimitAgeOffset(life, 1 + 9 + 10)).toBeCloseTo(60, 4); // + 二宫 10 年 → 60°
		// 总年数 = 9 + limit_seq[1..11] 之和(85.5)= 94.5 → 满 360° 附近。
		expect(moiraLimitAgeOffset(life, 1 + 94.5)).toBeGreaterThan(358);
	});
});
