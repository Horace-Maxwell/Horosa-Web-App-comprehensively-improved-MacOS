/**
 * 防回归自检（用户拍板，字面直觉版 + v3 时柱开关）:
 *   2026-05-27 23:30:00 - 两个独立开关的全矩阵:
 *   ┌──────────────────────────────┬─────────────┬─────────────┐
 *   │                              │ lateZi=1    │ lateZi=0    │
 *   │                              │ (按次日干起)│ (按当日干起)│
 *   ├──────────────────────────────┼─────────────┼─────────────┤
 *   │ after23=1 (23点算第二天/进位)│ 壬寅 庚子   │ 壬寅 庚子   │
 *   │ after23=0 (24点算第二天/守今)│ 辛丑 庚子   │ 辛丑 戊子   │ ← 核心新 case
 *   └──────────────────────────────┴─────────────┴─────────────┘
 * 时柱开关仅在 hour∈[23,24) 影响; after23=1 时日柱已次日,当日干即次日干,等价。
 */
import { buildLocalBaziResult } from '../baziLunarLocal';

function pillarsAt(dateStr, timeStr, after23NewDay, lateZiHourUseNextDay){
	const params = {
		date: dateStr,
		time: timeStr,
		zone: '+08:00',
		lon: 113.0,
		gpsLon: 113.0,
		lat: 23.0,
		gpsLat: 23.0,
		gender: 1,
		timeAlg: 1, // skip apparent-solar 调整,锁定时分
		after23NewDay,
	};
	if(lateZiHourUseNextDay !== undefined){
		params.lateZiHourUseNextDay = lateZiHourUseNextDay;
	}
	const result = buildLocalBaziResult(params);
	const cols = result && result.bazi && result.bazi.fourColumns;
	return {
		year: cols && cols.year && cols.year.ganzi,
		month: cols && cols.month && cols.month.ganzi,
		day: cols && cols.day && cols.day.ganzi,
		time: cols && cols.time && cols.time.ganzi,
	};
}

describe('baziLunarLocal · 日界点（after23NewDay）语义自检', () => {
	test('2026-05-27 23:30 + after23NewDay=1（23点算第二天）→ 壬寅日庚子时', () => {
		const p = pillarsAt('2026-05-27', '23:30:00', 1);
		expect(p.year).toBe('丙午');
		expect(p.month).toBe('癸巳');
		expect(p.day).toBe('壬寅');
		expect(p.time).toBe('庚子');
	});

	test('2026-05-27 23:30 + after23NewDay=0（24点算第二天）→ 辛丑日庚子时', () => {
		const p = pillarsAt('2026-05-27', '23:30:00', 0);
		expect(p.year).toBe('丙午');
		expect(p.month).toBe('癸巳');
		expect(p.day).toBe('辛丑');
		expect(p.time).toBe('庚子');
	});

	test('2026-05-27 22:30 两种模式日柱都应是 辛丑（边界前不受影响）', () => {
		const p1 = pillarsAt('2026-05-27', '22:30:00', 1);
		const p0 = pillarsAt('2026-05-27', '22:30:00', 0);
		expect(p1.day).toBe('辛丑');
		expect(p0.day).toBe('辛丑');
	});

	test('2026-05-28 00:30 两种模式日柱都应是 壬寅（边界后不受影响）', () => {
		const p1 = pillarsAt('2026-05-28', '00:30:00', 1);
		const p0 = pillarsAt('2026-05-28', '00:30:00', 0);
		expect(p1.day).toBe('壬寅');
		expect(p0.day).toBe('壬寅');
	});
});

describe('baziLunarLocal · v3 第二开关「晚子时·时柱起干」自检', () => {
	test('after23=0 + lateZi=1 (默认按次日干起) → 辛丑日 庚子时', () => {
		const p = pillarsAt('2026-05-27', '23:30:00', 0, 1);
		expect(p.day).toBe('辛丑');
		expect(p.time).toBe('庚子');
	});

	test('after23=0 + lateZi=0 (按当日干起) → 辛丑日 戊子时 ← 核心新 case', () => {
		const p = pillarsAt('2026-05-27', '23:30:00', 0, 0);
		expect(p.day).toBe('辛丑');
		expect(p.time).toBe('戊子'); // 辛日 子时起戊 (五鼠遁: 丙辛从戊起)
	});

	test('after23=1 + lateZi=1 (默认) → 壬寅日 庚子时', () => {
		const p = pillarsAt('2026-05-27', '23:30:00', 1, 1);
		expect(p.day).toBe('壬寅');
		expect(p.time).toBe('庚子');
	});

	test('after23=1 + lateZi=0 (日柱进位但时柱按今日辛干起) → 壬寅日 戊子时', () => {
		// 用户拍板:「按当日柱计算」= 不论 23/24 点是否换日,都按 clock-当天(27日辛丑)的干支起时干。
		// 即时柱开关与日柱开关完全独立。
		const p = pillarsAt('2026-05-27', '23:30:00', 1, 0);
		expect(p.day).toBe('壬寅');
		expect(p.time).toBe('戊子'); // 辛日子时起戊 (今日 27日 = 辛, 不受日柱开关影响)
	});

	test('22:30 非晚子时 + lateZi=0 不受影响（仍按当日干起子时无意义)', () => {
		const p0 = pillarsAt('2026-05-27', '22:30:00', 0, 0);
		const p1 = pillarsAt('2026-05-27', '22:30:00', 0, 1);
		expect(p0.day).toBe('辛丑');
		expect(p1.day).toBe('辛丑');
		// 22:30 是亥时,不是子时,lateZi 开关不影响
		expect(p0.time).toBe(p1.time);
	});

	test('00:30 子正不受 lateZi 影响（hour=0 不是 23）', () => {
		const p0 = pillarsAt('2026-05-28', '00:30:00', 0, 0);
		const p1 = pillarsAt('2026-05-28', '00:30:00', 0, 1);
		expect(p0.day).toBe('壬寅');
		expect(p1.day).toBe('壬寅');
		expect(p0.time).toBe(p1.time);
	});
});
