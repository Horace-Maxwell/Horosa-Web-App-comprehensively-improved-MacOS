import { resolveGeoZone } from '../timezone';

// 占卜/星盘各页 changeGeo 选地点时,统一经 resolveGeoZone 求时区偏移(单一真源)。
// 它只决定时区「标签」(配合 DateTime.setZone 保留输入的钟面时刻),不做真太阳时经度校正。
describe('resolveGeoZone · 选地点 → 时区自动校正(占卜/星盘各页 changeGeo 共用)', () => {
	test('手动改过时区(rec.zone)优先沿用,不被坐标推断覆盖', () => {
		expect(resolveGeoZone({ zone: '+05:30', gpsLat: 39.9, gpsLng: 116.4 }, '2026-06-01')).toBe('+05:30');
	});

	test('北京坐标 → +08:00', () => {
		expect(resolveGeoZone({ gpsLat: 39.9, gpsLng: 116.4 }, '2026-06-01')).toBe('+08:00');
	});

	test('洛杉矶坐标(6 月夏令时 PDT)→ -07:00', () => {
		expect(resolveGeoZone({ gpsLat: 34.05, gpsLng: -118.24 }, '2026-06-01')).toBe('-07:00');
	});

	test('洛杉矶坐标(1 月标准时 PST)→ -08:00(DST 随日期变)', () => {
		expect(resolveGeoZone({ gpsLat: 34.05, gpsLng: -118.24 }, '2026-01-15')).toBe('-08:00');
	});

	test('悉尼坐标(南半球 1 月夏令时 AEDT)→ +11:00', () => {
		expect(resolveGeoZone({ gpsLat: -33.87, gpsLng: 151.21 }, '2026-01-15')).toBe('+11:00');
	});

	test('伦敦坐标(1 月冬令时)→ +00:00', () => {
		expect(resolveGeoZone({ gpsLat: 51.5, gpsLng: -0.12 }, '2026-01-15')).toBe('+00:00');
	});

	test('无效/未选坐标 → null,绝不误改时区', () => {
		expect(resolveGeoZone({ gpsLat: 0, gpsLng: 0 }, '2026-06-01')).toBeNull();
		expect(resolveGeoZone({ gpsLat: 999, gpsLng: 999 }, '2026-06-01')).toBeNull();
		expect(resolveGeoZone(null, '2026-06-01')).toBeNull();
		expect(resolveGeoZone(undefined)).toBeNull();
	});

	test('缺盘期日期时兜底「今天」仍能判定(北京全年 +08:00,不返 null)', () => {
		expect(resolveGeoZone({ gpsLat: 39.9, gpsLng: 116.4 })).toBe('+08:00');
	});
});
