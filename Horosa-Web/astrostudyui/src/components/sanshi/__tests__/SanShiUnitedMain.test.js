jest.mock('../../astro/AstroHelper', ()=>({
	splitDegree: jest.fn(),
	convertLatToStr: (value)=>`${value}`,
	convertLonToStr: (value)=>`${value}`,
}));
jest.mock('../../liureng/ChuangChart', ()=>null);
jest.mock('../../amap/GeoCoordModal', ()=>null);
jest.mock('../../astro/PlusMinusTime', ()=>null);
jest.mock('../../../utils/request', ()=>jest.fn());
jest.mock('../../../utils/moduleAiSnapshot', ()=>({
	saveModuleAISnapshot: jest.fn(),
}));
jest.mock('../../../utils/preciseCalcBridge', ()=>({
	fetchPreciseNongli: jest.fn(),
	fetchPreciseJieqiSeed: jest.fn(),
}));

import SanShiUnitedMain from '../SanShiUnitedMain';
import DateTime from '../../comp/DateTime';

function buildDateTime(text){
	const dt = new DateTime();
	dt.parse(text, 'YYYY-MM-DD HH:mm:ss');
	dt.setZone('+08:00');
	return dt;
}

function buildFields(cid, name, birth, lon, lat, gender = 1){
	const dt = buildDateTime(birth);
	return {
		cid: { value: cid },
		name: { value: name },
		date: { value: dt.clone() },
		time: { value: dt.clone() },
		ad: { value: dt.ad },
		zone: { value: '+08:00' },
		lon: { value: lon },
		lat: { value: lat },
		gpsLon: { value: lon },
		gpsLat: { value: lat },
		zodiacal: { value: 0 },
		hsys: { value: 0 },
		timeAlg: { value: 0 },
		gender: { value: gender },
	};
}

function buildChart(chartId){
	return {
		chartId,
		chart: {
			objects: [],
			nongli: {
				dayGanZi: '甲子',
				time: '甲子',
			},
		},
	};
}

function mountLike(component){
	component.setState = (patch, callback)=>{
		const nextPatch = typeof patch === 'function' ? patch(component.state, component.props) : patch;
		component.state = {
			...component.state,
			...(nextPatch || {}),
		};
		if(callback){
			callback();
		}
	};
	return component;
}

describe('SanShiUnitedMain chart-list synchronization', ()=>{
	beforeEach(()=>{
		jest.useFakeTimers();
	});

	afterEach(()=>{
		jest.runOnlyPendingTimers();
		jest.useRealTimers();
	});

	it('replaces plotted fields and auto recalculates when a second saved chart is selected', ()=>{
		const firstFields = buildFields('chart-a', 'A', '2006-10-04 09:58:00', '119e24', '30n54', 1);
		const secondFields = buildFields('chart-b', 'B', '1988-04-20 12:20:00', '118e27', '31n38', 0);
		const component = mountLike(new SanShiUnitedMain({
			fields: firstFields,
			chartObj: buildChart('chart-a'),
			hook: {},
		}));
		component.state = {
			...component.state,
			hasPlotted: true,
			localFields: firstFields,
			plottedFields: firstFields,
			loading: false,
		};
		component.prefetchNongliForFields = jest.fn();
		component.prefetchJieqiSeedForFields = jest.fn();
		component.refreshAll = jest.fn();

		component.handleExternalFieldsSync(secondFields, buildChart('chart-b'));

		expect(component.state.localFields).toBe(secondFields);
		expect(component.state.plottedFields).toBe(secondFields);
		expect(component.state.options.sex).toBe(0);
		expect(component.state.loading).toBe(true);
		expect(component.prefetchNongliForFields).toHaveBeenCalledWith(secondFields);
		expect(component.prefetchJieqiSeedForFields).toHaveBeenCalledWith(secondFields, component.state.options);

		jest.runOnlyPendingTimers();

		expect(component.refreshAll).toHaveBeenCalledWith(secondFields, true);
	});

	it('syncs right-side input fields without auto recalculating before the first plot', ()=>{
		const firstFields = buildFields('chart-a', 'A', '2006-10-04 09:58:00', '119e24', '30n54');
		const secondFields = buildFields('chart-b', 'B', '1988-04-20 12:20:00', '118e27', '31n38');
		const component = mountLike(new SanShiUnitedMain({
			fields: firstFields,
			chartObj: buildChart('chart-a'),
			hook: {},
		}));
		component.prefetchNongliForFields = jest.fn();
		component.prefetchJieqiSeedForFields = jest.fn();
		component.refreshAll = jest.fn();

		component.handleExternalFieldsSync(secondFields, buildChart('chart-b'));
		jest.runOnlyPendingTimers();

		expect(component.state.localFields).toBe(secondFields);
		expect(component.state.plottedFields).toBe(null);
		expect(component.refreshAll).not.toHaveBeenCalled();
	});

	it('uses the shared DunJia calculation for Sanshi qimen tianpan stems', ()=>{
		const fields = buildFields('qimen-sample', 'Qimen Sample', '1998-02-20 20:48:00', '119e19', '26n04');
		const component = mountLike(new SanShiUnitedMain({
			fields,
			chartObj: buildChart('qimen-sample'),
			hook: {},
		}));
		const nongli = {
			yearJieqi: '戊寅',
			year: '戊寅',
			monthGanZi: '甲寅',
			dayGanZi: '戊戌',
			time: '壬戌',
			jieqi: '雨水',
			jiedelta: '雨水后第1天',
			birth: '1998-02-20 20:48:00',
			month: '正月',
			day: '廿四',
			leap: false,
		};
		const pan = component.getCachedDunJia(fields, nongli, {
			paiPanType: 3,
			qijuMethod: 'chaibu',
			zhiShiType: 0,
			yueJiaQiJuType: 1,
			kongMode: 'time',
			yimaMode: 'time',
			timeAlg: 1,
			shiftPalace: 0,
			fengJu: false,
			after23NewDay: 1,
		}, 1998, true);
		expect(pan.juText).toEqual('阳遁九局上元');
		expect(pan.tianGan).toMatchObject({
			1: '庚',
			2: '丙',
			3: '丁',
			4: '戊',
			6: '己',
			7: '壬',
			8: '辛',
			9: '乙',
		});
	});
});
