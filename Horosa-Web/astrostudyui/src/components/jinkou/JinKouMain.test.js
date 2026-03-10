import { resolveJinKouDiFen } from './JinKouState';

describe('JinKouMain', ()=>{
	it('seeds auto 地分 from 时支 on first load only', ()=>{
		expect(resolveJinKouDiFen('子', true, '申', false)).toBe('申');
		expect(resolveJinKouDiFen('申', true, '酉', true)).toBe('申');
	});

	it('preserves manual 地分 selection', ()=>{
		expect(resolveJinKouDiFen('午', false, '酉', true)).toBe('午');
		expect(resolveJinKouDiFen('午', false, '子', false)).toBe('午');
	});
});
