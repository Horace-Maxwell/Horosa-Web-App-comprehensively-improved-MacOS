// WP-5 紫白深化：日紫白(8.1.3)/时紫白(8.1.4)/紫白诀(8.9)。锚 2025-12-21=冬至且甲子日→阳遁上元一白。
import { zibai, dayCenter, hourCenter, ZIBAI_JUE } from '../zibai';

describe('WP-5 紫白 · 日紫白（正统古法）', () => {
	test('2025-12-21（冬至·甲子日）阳遁上元一白入中', () => {
		const dc = dayCenter(2025, 12, 21);
		expect(dc.yang).toBe(true);
		expect(dc.center).toBe(1);
		expect(dc.dayGanZhi).toBe('甲子');
	});
	test('阳遁逐日顺行+1（1/15→1/16 center +1）', () => {
		const a = dayCenter(2026, 1, 15).center;
		const b = dayCenter(2026, 1, 16).center;
		expect(((b - a) % 9 + 9) % 9).toBe(1);
	});
	test('夏至后阴遁·逐日逆行', () => {
		const dc = dayCenter(2026, 7, 15);
		expect(dc.yang).toBe(false);
		const a = dayCenter(2026, 7, 15).center;
		const b = dayCenter(2026, 7, 16).center;
		expect(((a - b) % 9 + 9) % 9).toBe(1);   // 逆行
	});
});

describe('WP-5 紫白 · 时紫白（正统古法）', () => {
	test('甲子日(子日,阳遁)子时一白·丑时二黑（顺）', () => {
		expect(hourCenter(2025, 12, 21, 0).center).toBe(1);   // 子时
		expect(hourCenter(2025, 12, 21, 2).center).toBe(2);   // 丑时
		expect(hourCenter(2025, 12, 21, 0).shiZhi).toBe('子');
	});
});

describe('WP-5 紫白 · 紫白诀 + 整合', () => {
	test('紫白诀名句含二五交加/七九回禄', () => {
		expect(ZIBAI_JUE.some((j)=>j.text.indexOf('二五交加') >= 0)).toBe(true);
		expect(ZIBAI_JUE.some((j)=>j.text.indexOf('七九合辙') >= 0)).toBe(true);
	});
	test('zibai 给 date → 日/时盘齐；不给则 null（向后兼容）', () => {
		const r = zibai({ year: 2026, month: 6, date: { y: 2025, m: 12, d: 21, hour: 0 } });
		expect(r.yearPalaces).toHaveLength(9);
		expect(r.dayPalaces).toHaveLength(9);
		expect(r.hourPalaces).toHaveLength(9);
		expect(zibai({ year: 2026 }).dayPalaces).toBeNull();
	});
});
