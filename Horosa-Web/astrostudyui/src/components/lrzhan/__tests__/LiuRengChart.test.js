jest.mock('d3', ()=>({
	select: jest.fn(()=>({
		append: jest.fn().mockReturnThis(),
		attr: jest.fn().mockReturnThis(),
		remove: jest.fn(),
	})),
}));

jest.mock('../../../utils/helper', ()=>({
	randomStr: ()=> 'liureng-chart-test',
	setupFloatingTooltip: jest.fn(),
}));

jest.mock('../../../constants/AstroConst', ()=>({
	AstroColor: {
		ChartBackgroud: '#fff',
	},
}));

jest.mock('../RengChart', ()=> jest.fn().mockImplementation(function(opt){
	Object.assign(this, opt);
	this.draw = jest.fn();
}));

import LiuRengChart from '../LiuRengChart';

describe('LiuRengChart gender sync', ()=>{
	test('drawChart syncs latest gender prop into inner RengChart instance', ()=>{
		const props = {
			value: { nongli: { time: '子' }, objects: [] },
			fields: {},
			liureng: {},
			runyear: { year: '甲子', age: 38 },
			gender: 1,
			zhangshengElem: '土',
			guireng: 2,
			panStyleName: '',
		};
		const comp = new LiuRengChart(props);
		comp.props = {
			...props,
			gender: 0,
		};

		comp.drawChart();

		expect(comp.rengchart.gender).toBe(0);
		expect(comp.rengchart.draw).toHaveBeenCalled();
	});
});
