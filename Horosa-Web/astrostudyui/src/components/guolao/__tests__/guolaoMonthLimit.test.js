// 月限金标(照 Moira getMonthLimit,ChartData.java:7526):index=今农历月−生农历月,
// <0 则 +12 且 +(虚岁−2),否则 +(虚岁−1);地支=zodiac(命宫黄经 + index×30)。
import { monthLimitBranch, lunarMonthNumFromBranch } from '../guolaoMoiraTables';

describe('月限(照 Moira getMonthLimit)', ()=>{
	test('月支 → 农历月序(月建:寅=1、卯=2、子=11、丑=12)', ()=>{
		expect(lunarMonthNumFromBranch('寅')).toBe(1);
		expect(lunarMonthNumFromBranch('卯')).toBe(2);
		expect(lunarMonthNumFromBranch('午')).toBe(5);
		expect(lunarMonthNumFromBranch('子')).toBe(11);
		expect(lunarMonthNumFromBranch('丑')).toBe(12);
		expect(Number.isNaN(lunarMonthNumFromBranch(''))).toBe(true);
	});

	test('今月≥生月:index = 差 + (虚岁−1);命宫白羊(戌)、生6今8、5岁 → 辰', ()=>{
		// index = (8−6) + (5−1) = 6 → zodiac(0 + 180) = SIGN_BRANCH[6] = 辰
		expect(monthLimitBranch(0, 5, 6, 8)).toBe('辰');
	});

	test('今月<生月:index = 差+12 + (虚岁−2);生8今6、5岁 → 酉', ()=>{
		// index = (6−8+12) + (5−2) = 10 + 3 = 13 → zodiac(0 + 390=30) = SIGN_BRANCH[1] = 酉
		expect(monthLimitBranch(0, 5, 8, 6)).toBe('酉');
	});

	test('数据缺(月号 NaN)→ 空串(不抛)', ()=>{
		expect(monthLimitBranch(0, 5, NaN, 8)).toBe('');
		expect(monthLimitBranch(0, 5, 6, undefined)).toBe('');
	});
});
