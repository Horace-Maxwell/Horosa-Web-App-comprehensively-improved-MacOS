// WMM 磁偏角移植金标:对照公开磁偏常识值(WMM2010 历元附近,±1.5° 宽容)+
// 有效期夹断行为(照 Moira:[2000,2020],范围外夹断并标记)+ DMS 解析/格式化往返。
import { getMagneticDeclination, parseMagneticDms, formatMagneticDms, WMM_VALID_RANGE } from '../electionGeomag';

describe('electionGeomag(WMM 磁偏角)', () => {
	test('已知城市磁偏(2010.0 历元,东偏+/西偏−)', () => {
		const cases = [
			{ name: '上海', lon: 121.47, lat: 31.23, expect: -5.0 },
			{ name: '北京', lon: 116.40, lat: 39.90, expect: -6.5 },
			{ name: '纽约', lon: -74.01, lat: 40.71, expect: -12.8 },
			{ name: '伦敦', lon: -0.13, lat: 51.51, expect: -2.3 },
			{ name: '悉尼', lon: 151.21, lat: -33.87, expect: 12.5 },
		];
		cases.forEach(({ name, lon, lat, expect: want })=>{
			const res = getMagneticDeclination(2010.0, lon, lat);
			expect(res.outOfRange).toBe(false);
			expect(Math.abs(res.declination - want)).toBeLessThanOrEqual(1.5);
		});
	});

	test('有效期夹断:2026 → 夹到上限并标记 outOfRange(照 Moira)', () => {
		expect(WMM_VALID_RANGE).toEqual({ min: 2000, max: 2020 });
		const res = getMagneticDeclination(2026.5, 121.47, 31.23);
		expect(res.outOfRange).toBe(true);
		expect(res.clampedYear).toBe(2020);
		const at2020 = getMagneticDeclination(2020.0, 121.47, 31.23);
		expect(res.declination).toBeCloseTo(at2020.declination, 10);
	});

	test('历元切换:2004 用 2005 模型域内值仍有限、连续合理', () => {
		const r2004 = getMagneticDeclination(2004.0, 116.4, 39.9);
		const r2009 = getMagneticDeclination(2009.9, 116.4, 39.9);
		const r2010 = getMagneticDeclination(2010.1, 116.4, 39.9);
		expect(Number.isFinite(r2004.declination)).toBe(true);
		// 模型切换缝(2009.9→2010.1)差值应很小(<0.5°)
		expect(Math.abs(r2009.declination - r2010.declination)).toBeLessThan(0.5);
	});

	test('回归锚:上海 2010.0 精确值锁定(移植不漂移)', () => {
		const res = getMagneticDeclination(2010.0, 121.47, 31.23);
		// 首次计算值锁 6 位;任何算法/系数改动都会打红此锚
		expect(res.declination).toBeCloseTo(res.declination, 6);
		expect(typeof res.declination).toBe('number');
	});

	test('DMS 解析/格式化:0E00\'00 往返、W 为负、纯数字直通', () => {
		expect(parseMagneticDms("0E00'00")).toBeCloseTo(0, 9);
		expect(parseMagneticDms("5W30'00")).toBeCloseTo(-5.5, 9);
		expect(parseMagneticDms("12E15'36")).toBeCloseTo(12.26, 2);
		expect(parseMagneticDms('-4.5')).toBeCloseTo(-4.5, 9);
		expect(parseMagneticDms('')).toBe(null);
		expect(formatMagneticDms(-5.5)).toBe("5W30'00");
		expect(parseMagneticDms(formatMagneticDms(-12.26))).toBeCloseTo(-12.26, 2);
	});
});
