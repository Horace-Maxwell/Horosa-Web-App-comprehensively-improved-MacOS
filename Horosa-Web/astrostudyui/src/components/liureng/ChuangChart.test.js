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

// 八专结构(甲寅日,干支同位:甲寄寅=日支寅)+ 天盘=地盘+4。
// 四课无近克,但日干甲遥克 2/4 课上神戌(木克土)。
// 按《九法》遥克(第4法)优先于八专(第9法),正确应判"弹射课"(日干遥克),而非"八专课"。
function buildChartBaZhuanYaoKe(){
	const downZi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
	const upZi   = ['辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑', '寅', '卯'];
	const ke = [
		['贵人', '午', '甲'],
		['贵人', '戌', '午'],
		['贵人', '午', '寅'],
		['贵人', '戌', '午'],
	];
	return new ChuangChart({
		owner: null,
		chartObj: { nongli: { dayGanZi: '甲寅' } },
		nongli: { dayGanZi: '甲寅' },
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

	it('八专结构且日干遥克他课上神时,按九法优先遥克(弹射课)而非八专课', ()=>{
		const chart = buildChartBaZhuanYaoKe();
		const sangCuang = chart.getSangCuang();
		expect(sangCuang.name).toBe('弹射课');
		expect(sangCuang.cuang[0]).toBe('戌');
	});
});
