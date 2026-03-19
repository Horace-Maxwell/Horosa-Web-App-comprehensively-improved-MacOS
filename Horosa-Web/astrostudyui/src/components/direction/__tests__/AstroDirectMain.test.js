jest.mock('../../astro/AstroPrimaryDirection', ()=>null);
jest.mock('../../astro/AstroPrimaryDirectionChart', ()=>null);
jest.mock('../../astro/AstroZR', ()=>null);
jest.mock('../../astro/AstroFirdaria', ()=>null);
jest.mock('../../astro/AstroSolarReturn', ()=>null);
jest.mock('../../astro/AstroLunarReturn', ()=>null);
jest.mock('../../astro/AstroGivenYear', ()=>null);
jest.mock('../../astro/AstroSolarArc', ()=>null);
jest.mock('../../astro/AstroProfection', ()=>null);
jest.mock('../../astro/AstroDecennials', ()=>null);
jest.mock('../../../utils/request', ()=>jest.fn());
jest.mock('../../../utils/moduleAiSnapshot', ()=>({
	saveModuleAISnapshot: jest.fn(),
}));
jest.mock('../../../utils/planetHouseInfo', ()=>({
	appendPlanetHouseInfoById: (text)=>text,
}));

import { AstroDirectMain, } from '../AstroDirectMain';

function buildFields(){
	return {
		date: { name: ['date'], value: { ad: 1, zone: '+00:00' }, },
		time: { name: ['time'], value: { zone: '+00:00' }, },
		ad: { name: ['ad'], value: 1, },
		zone: { name: ['zone'], value: '+00:00', },
		lat: { name: ['lat'], value: '30N0', },
		lon: { name: ['lon'], value: '120E0', },
		gpsLat: { name: ['gpsLat'], value: '30N0', },
		gpsLon: { name: ['gpsLon'], value: '120E0', },
		hsys: { name: ['hsys'], value: 0, },
		zodiacal: { name: ['zodiacal'], value: 0, },
		tradition: { name: ['tradition'], value: 0, },
		strongRecption: { name: ['strongRecption'], value: 0, },
		simpleAsp: { name: ['simpleAsp'], value: 0, },
		virtualPointReceiveAsp: { name: ['virtualPointReceiveAsp'], value: 0, },
		doubingSu28: { name: ['doubingSu28'], value: 0, },
		predictive: { name: ['predictive'], value: 1, },
		showPdBounds: { name: ['showPdBounds'], value: 1, },
		pdtype: { name: ['pdtype'], value: 0, },
		pdMethod: { name: ['pdMethod'], value: 'core_alchabitius', },
		pdTimeKey: { name: ['pdTimeKey'], value: 'Ptolemy', },
		pdaspects: { name: ['pdaspects'], value: [0, 60, 90, 120, 180], },
		name: { name: ['name'], value: 'unit chart', },
		pos: { name: ['pos'], value: 'unit place', },
		southchart: { name: ['southchart'], value: 0, },
		cid: { name: ['cid'], value: null, },
	};
}

function buildChartObj(){
	return {
		params: {
			birth: '1984-01-23 00:00:00',
			zone: '+00:00',
			lat: '30N0',
			lon: '120E0',
			gpsLat: '30N0',
			gpsLon: '120E0',
			hsys: 0,
			zodiacal: 0,
			tradition: 0,
			strongRecption: 0,
			simpleAsp: 0,
			virtualPointReceiveAsp: 0,
			doubingSu28: 0,
			showPdBounds: 1,
			southchart: 0,
			pdaspects: [0, 60, 90, 120, 180],
			name: 'unit chart',
			pos: 'unit place',
		},
		predictives: {},
	};
}

describe('AstroDirectMain primary direction sync', ()=>{
	test('defaults invalid sub tab keys to primarydirect on entry', ()=>{
		const instance = new AstroDirectMain({
			currentSubTab: 'not-a-direction-tab',
		});

		expect(instance.state.currentTab).toBe('primarydirect');
	});

	test('primary direction calculate updates fields and uses direct pd fetch', ()=>{
		const dispatch = jest.fn();
		const chartObj = buildChartObj();
		const fields = buildFields();
		const instance = new AstroDirectMain({
			dispatch,
			chartObj,
			fields,
		});
		instance.requestPrimaryDirectionRows = jest.fn();

		instance.applyPrimaryDirectionConfig('horosa_legacy', 'Ptolemy');

		expect(dispatch).toHaveBeenCalledWith({
			type: 'app/save',
			payload: {
				pdMethod: 'horosa_legacy',
				pdTimeKey: 'Ptolemy',
			},
		});
		expect(dispatch).toHaveBeenCalledWith(expect.objectContaining({
			type: 'astro/save',
			payload: expect.objectContaining({
				fields: expect.any(Object),
			}),
		}));
		expect(dispatch.mock.calls.find(([action])=>action.type === 'astro/fetchByFields')).toBeUndefined();
		expect(instance.requestPrimaryDirectionRows).toHaveBeenCalledWith(expect.objectContaining({
			chartObj,
			pdMethod: 'horosa_legacy',
			pdTimeKey: 'Ptolemy',
			fields: expect.any(Object),
			runHook: true,
		}));
	});
});
