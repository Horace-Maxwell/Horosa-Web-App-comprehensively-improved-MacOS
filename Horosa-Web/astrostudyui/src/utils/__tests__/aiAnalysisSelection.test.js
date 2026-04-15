import {
	filterTechniqueKeysBySource,
	getTechniqueContextMode,
} from '../aiAnalysisSelection';

describe('aiAnalysisSelection', ()=>{
	test('filters stale technique keys when source changes', ()=>{
		const activeSource = {
			id: 'chart-1',
			sourceType: 'chart',
		};
		const techniqueOptions = [
			{ value: 'bazi', label: '八字' },
			{ value: 'ziwei', label: '紫微斗数' },
		];
		const selectedTechniqueKeys = ['liureng', 'bazi', 'ziwei'];

		expect(filterTechniqueKeysBySource(activeSource, techniqueOptions, selectedTechniqueKeys)).toEqual(['bazi', 'ziwei']);
	});

	test('returns empty technique list without an active source', ()=>{
		expect(filterTechniqueKeysBySource(null, [
			{ value: 'bazi', label: '八字' },
		], ['bazi'])).toEqual([]);
	});

	test('uses context meta mode only when valid technique keys remain', ()=>{
		expect(getTechniqueContextMode([])).toBe('full');
		expect(getTechniqueContextMode(['bazi'])).toBe('meta');
	});
});
