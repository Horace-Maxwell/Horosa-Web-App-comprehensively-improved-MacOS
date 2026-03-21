jest.mock('../../astro/AstroChartMain', ()=>null);
jest.mock('../../amap/GeoCoordModal', ()=>null);
jest.mock('../../suzhan/SuZhanMain', ()=>null);
jest.mock('../../astro3d/AstroChartMain3D', ()=>null);
jest.mock('../../../utils/request', ()=>jest.fn());
jest.mock('../../../utils/moduleAiSnapshot', ()=>({
	saveModuleAISnapshot: jest.fn(),
}));
jest.mock('../../../utils/preciseCalcBridge', ()=>({
	fetchPreciseJieqiYear: jest.fn(),
}));

import { isJieQiChartCompatible, } from '../JieQiChartsMain';

describe('JieQiChartsMain chart compatibility', ()=>{
	test('reuses cached chart only when zodiacal and house system still match', ()=>{
		const chartObj = {
			params: {
				year: 2026,
				ad: 1,
				zone: '+08:00',
				lat: '26n04',
				lon: '119e19',
				gpsLat: 26.04,
				gpsLon: 119.19,
				hsys: 3,
				zodiacal: 1,
				doubingSu28: 0,
			},
		};

		expect(isJieQiChartCompatible(chartObj, {
			year: 2026,
			ad: 1,
			zone: '+08:00',
			lat: '26n04',
			lon: '119e19',
			gpsLat: 26.04,
			gpsLon: 119.19,
			hsys: 3,
			zodiacal: 1,
			doubingSu28: 0,
		})).toBe(true);

		expect(isJieQiChartCompatible(chartObj, {
			year: 2026,
			ad: 1,
			zone: '+08:00',
			lat: '26n04',
			lon: '119e19',
			gpsLat: 26.04,
			gpsLon: 119.19,
			hsys: 0,
			zodiacal: 0,
			doubingSu28: 0,
		})).toBe(false);
	});
});
