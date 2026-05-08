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
});
