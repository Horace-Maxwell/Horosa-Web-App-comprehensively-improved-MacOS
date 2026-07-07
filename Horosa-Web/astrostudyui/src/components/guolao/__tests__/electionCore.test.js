// 择日双轮纯数学金标(对照 Moira 语义):度空间换算/山分度「07子山30」/快盘投影/磁偏套用。
import { normDeg, swissAzToCompass, azTheta, mountainPosition, shanNameAt, quickWheelAz, applyDeclination, shanColor } from '../electionCore';

describe('electionCore(择日双轮数学核)', () => {
	test('swiss 南零方位 → 罗盘:0(南)→180,180(北)→0', () => {
		expect(swissAzToCompass(0)).toBe(180);
		expect(swissAzToCompass(180)).toBe(0);
		expect(swissAzToCompass(270)).toBe(90);
	});

	test('azTheta 子下卯左:az0 正下(90),az90(东) 在左(180)', () => {
		expect(normDeg(azTheta(0))).toBe(90);
		expect(normDeg(azTheta(90))).toBe(180);
		expect(normDeg(azTheta(180))).toBe(270);
	});

	test('座山分度(Moira 默认):az=0 → 07子山30;山界与中心', () => {
		expect(mountainPosition(0).text).toBe('07子山30');
		expect(mountainPosition(0).shan).toBe('子');
		// 子山中心 0,山界 ±7.5:352.5=子山头 00子山00;7.49≈14子山59
		expect(mountainPosition(352.5).text).toBe('00子山00');
		expect(mountainPosition(7.4).deg).toBe(14);
		// 卯=东 90:az=90 → 07卯山30
		expect(mountainPosition(90).text).toBe('07卯山30');
		expect(shanNameAt(90)).toBe('卯');
		// 天盘 +7.5:山界顺移,az=0 恰为子山头 → 00子山00
		expect(mountainPosition(0, 'tian').text).toBe('00子山00');
		// 人盘 −7.5:山界逆移,az=0 恰为癸山头;子山尾在 359.9
		expect(mountainPosition(0, 'ren').text).toBe('00癸山00');
		expect(mountainPosition(359.9, 'ren').shan).toBe('子');
		expect(mountainPosition(359.9, 'ren').deg).toBe(14);
	});

	test('快盘投影(Moira quick 公式):宫头/宫中/跨宫;等宫制往返', () => {
		const equal = Array.from({length: 12}, (_, i)=>i * 30); // 等宫,1宫头=0°
		// lon=宫头 → ratio 0 → chartDeg=180+idx*30 → az=315-chartDeg
		expect(quickWheelAz(0, equal)).toBe(normDeg(315 - 180));
		expect(quickWheelAz(15, equal)).toBe(normDeg(315 - 195));
		expect(quickWheelAz(30, equal)).toBe(normDeg(315 - 210));
		// 不等宫:宫1 跨 350→40(span 50),lon=15 → ratio 0.5
		const cusps = [350, 40, 70, 100, 130, 160, 190, 220, 250, 280, 310, 340];
		expect(quickWheelAz(15, cusps)).toBe(normDeg(315 - (30 * 0.5 + 180)));
	});

	test('磁偏套用:正北模式不动;磁北模式减东偏', () => {
		expect(applyDeclination(100, 'true', -5)).toBe(100);
		expect(applyDeclination(100, 'magnetic', -5)).toBe(105);
		expect(applyDeclination(2, 'magnetic', 5)).toBe(357);
	});

	test('山五行配色两套表齐全 24 山', () => {
		['壬','子','癸','丑','艮','寅','甲','卯','乙','辰','巽','巳','丙','午','丁','未','坤','申','庚','酉','辛','戌','乾','亥'].forEach((s)=>{
			expect(shanColor(s, 'main')).toMatch(/var\(/);
			expect(shanColor(s, 'combo')).toMatch(/var\(/);
		});
	});
});

describe('resolveRingShifts(环向推挤,照 Moira computeSignShift 语义)', () => {
	const { resolveRingShifts } = require('../electionCore');
	test('稀疏行星不动(gap>minGap 时 shifted=az)', () => {
		const out = resolveRingShifts([0, 90, 180, 270], 8);
		expect(out.map(Math.round)).toEqual([0, 90, 180, 270]);
	});
	test('密集行星推开:任意相邻(含环绕)间距≥minGap−0.1', () => {
		const az = [10, 11, 12, 13, 200, 200.5];
		const out = resolveRingShifts(az, 7);
		const sorted = out.slice().sort((a, b)=>a - b);
		for(let i = 0; i < sorted.length; i++){
			const gap = i + 1 < sorted.length ? sorted[i + 1] - sorted[i] : sorted[0] + 360 - sorted[i];
			expect(gap).toBeGreaterThanOrEqual(7 - 0.1);
		}
	});
	test('保持原索引对应(输出[i] 对应输入[i])', () => {
		const az = [350, 5, 120];
		const out = resolveRingShifts(az, 4);
		expect(Math.abs(out[2] - 120)).toBeLessThan(0.01);
	});
});

describe('PICK_LAYOUTS(择日三套布局,数值=moira prop 逐值)', () => {
	const { PICK_LAYOUTS, pickLayoutMode, COMPASS_STELLAR } = require('../electionCore');
	test('三表半径逐值', () => {
		expect(PICK_LAYOUTS.pick.ringPos).toEqual([0.19, 0.31, 0.37, 0.43, 0.51, 0.54, 0.60, 0.68, 0.71, 0.77, 0.92, 0.95, 1.0]);
		expect(PICK_LAYOUTS.compass.ringPos).toEqual([0.19, 0.31, 0.37, 0.43, 0.51, 0.54, 0.60, 0.66, 0.72, 0.75, 0.83, 0.86, 0.92, 0.95, 1.0]);
		expect(PICK_LAYOUTS.fixstar.ringPos).toEqual([0.16, 0.28, 0.34, 0.40, 0.48, 0.50, 0.56, 0.58, 0.72, 0.78, 0.80, 0.93, 0.95, 1.0]);
	});
	test('键位槽:动盘/山/罗盘宿/度环', () => {
		expect(PICK_LAYOUTS.pick.slots.nowPlanets).toEqual([6, 7]);
		expect(PICK_LAYOUTS.pick.slots.gods).toEqual([9, 10]);
		expect(PICK_LAYOUTS.compass.slots.nowPlanets).toEqual([9, 10]);
		expect(PICK_LAYOUTS.compass.slots.mountain).toEqual([7, 8]);
		expect(PICK_LAYOUTS.compass.slots.compassRing).toEqual([11, 12]);
		expect(PICK_LAYOUTS.compass.slots.gods).toBeUndefined();
		expect(PICK_LAYOUTS.fixstar.slots.nowPlanets).toEqual([10, 11]);
		expect(PICK_LAYOUTS.fixstar.slots.starRing).toEqual([7, 8]);
	});
	test('模式优先级:恒星最优先,其余恒 pick(带神煞环)', () => {
		expect(pickLayoutMode({showFixstar: true, showCompass: true})).toBe('fixstar');
		// 「显示罗盘」开关已撤:择日盘恒用 pick 布局(含神煞带),不再落 compass(会丢神煞)。
		expect(pickLayoutMode({showCompass: true})).toBe('pick');
		expect(pickLayoutMode({})).toBe('pick');
		expect(pickLayoutMode({showCompass: false})).toBe('pick');
	});
	test('罗盘宿 28 项且方位升序', () => {
		expect(COMPASS_STELLAR).toHaveLength(28);
		for(let i = 1; i < 28; i++){
			expect(COMPASS_STELLAR[i][1]).toBeGreaterThan(COMPASS_STELLAR[i - 1][1]);
		}
	});
});
