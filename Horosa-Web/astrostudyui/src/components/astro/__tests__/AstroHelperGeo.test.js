import { convertLatToStr, convertLonToStr, splitDegree } from '../AstroHelper';

// 回归哨兵:gps 十进制 → 命盘录入串(NNeMM / NNwMM)。
// 历史 bug:对西经/南纬把「分」也取负 → 产「121w0-44」畸形串 → 后端 param error、技法挂载缺失;
// 以及分=10 时 `>10` 补零产「010」三位串。本测试覆盖全四半球 + 边界,确保「不能有丝毫差错」。
describe('AstroHelper 经纬度串 — 全半球无畸形(param error 哨兵)', ()=>{
	const VALID_LON = /^\d{1,3}[ew]\d{2}$/;   // 度 + e/w + 两位分,无负号/无多余位
	const VALID_LAT = /^\d{1,2}[ns]\d{2}$/;

	const cases = [
		{ name: '北京 E/N', lon: 116.4074, lat: 39.9042 },
		{ name: '旧金山 W/N', lon: -122.4194, lat: 37.7749 },
		{ name: '洛杉矶 W/N', lon: -118.2437, lat: 34.0522 },
		{ name: '悉尼 E/S', lon: 151.2093, lat: -33.8688 },
		{ name: '圣保罗 W/S', lon: -46.6333, lat: -23.5505 },
		{ name: '伦敦 W/N(小负经)', lon: -0.1276, lat: 51.5074 },
		{ name: '东京 E/N', lon: 139.6917, lat: 35.6895 },
		{ name: '开普敦 E/S', lon: 18.4241, lat: -33.9249 },
		{ name: '赤道·本初子午线', lon: 0, lat: 0 },
		{ name: '负小数', lon: -0.5, lat: -0.5 },
	];

	cases.forEach((c)=>{
		test(`${c.name} 不产畸形串(无负号、方向正确、两位分)`, ()=>{
			const lon = convertLonToStr(c.lon);
			const lat = convertLatToStr(c.lat);
			expect(lon).toMatch(VALID_LON);
			expect(lat).toMatch(VALID_LAT);
			expect(lon).not.toContain('-');
			expect(lat).not.toContain('-');
			expect(lon).toContain(c.lon < 0 ? 'w' : 'e');
			expect(lat).toContain(c.lat < 0 ? 's' : 'n');
		});
	});

	test('分=10 应输出两位「10」而非三位「010」', ()=>{
		expect(convertLatToStr(39 + 10 / 60)).toBe('39n10');
		expect(convertLonToStr(116 + 10 / 60)).toBe('116e10');
		expect(convertLonToStr(-(122 + 10 / 60))).toBe('122w10');
	});

	test('splitDegree 对负值只把度取负、分秒为正绝对值(转换器赖以判向的不变量)', ()=>{
		const d = splitDegree(-122.4194);
		expect(d[0]).toBeLessThan(0);     // 度带负号
		expect(d[1]).toBeGreaterThanOrEqual(0);  // 分为正(若被当负数取负即重现畸形 bug)
	});
});
