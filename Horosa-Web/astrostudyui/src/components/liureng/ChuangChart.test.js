jest.mock('../../utils/helper', ()=>({
	randomStr: ()=> 'mocked',
}));

import ChuangChart from './ChuangChart';

function buildChart(){
	const upZi = ['未', '申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰', '巳', '午'];
	const downZi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
	const ke = [
		['玄武', '申', '癸'],
		['朱雀', '卯', '申'],
		['玄武', '申', '丑'],
		['朱雀', '卯', '申'],
	];
	return new ChuangChart({
		owner: null,
		chartObj: { nongli: { dayGanZi: '癸丑' } },
		nongli: { dayGanZi: '癸丑' },
		ke,
		liuRengChart: {
			upZi,
			downZi,
			houseTianJiang: new Array(12).fill('贵人'),
		},
		x: 0,
		y: 0,
		width: 0,
		height: 0,
	});
}

function buildChartForXun(){
	const upZi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
	const downZi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
	const chart = new ChuangChart({
		owner: null,
		chartObj: { nongli: { dayGanZi: '癸丑' } },
		nongli: { dayGanZi: '癸丑' },
		ke: [
			['贵人', '子', '癸'],
			['贵人', '丑', '子'],
			['贵人', '子', '丑'],
			['贵人', '丑', '子'],
		],
		liuRengChart: {
			upZi,
			downZi,
			houseTianJiang: new Array(12).fill('贵人'),
		},
		x: 0,
		y: 0,
		width: 0,
		height: 0,
	});
	chart.getSangCuang = ()=>({
		cuang: ['未', '子', '丑'],
		name: 'mock',
	});
	return chart;
}

describe('ChuangChart', ()=>{
	it('counts duplicated 贼课 as one课 and sets 初传 to 卯', ()=>{
		const chart = buildChart();
		const sangCuang = chart.getSangCuang();
		expect(sangCuang.cuang[0]).toBe('卯');

		chart.genCuangs();
		expect(chart.cuangs.cuang[0]).toBe('空卯');
	});

	it('maps 甲辰旬 branch 未 to 丁未 instead of 己未', ()=>{
		const chart = buildChartForXun();
		chart.genCuangs();
		expect(chart.cuangs.cuang[0]).toBe('丁未');
	});
});
