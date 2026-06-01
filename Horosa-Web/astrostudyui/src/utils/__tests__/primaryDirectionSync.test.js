jest.mock('../helper', ()=>({
	randomStr: ()=> 'chart-seq-1',
}));

import {
	DEFAULT_PD_TYPE,
	PD_SYNC_REV,
	mergePrimaryDirectionChartObj,
	normalizePrimaryDirectionSubTabKey,
} from '../primaryDirectionSync';

describe('primaryDirectionSync', ()=>{
	test('merges primary direction rows into chart state with synced params', ()=>{
		const chartObj = {
			params: {
				name: 'before',
				pos: 'before pos',
				showPdBounds: 0,
			},
			predictives: {
				firdaria: [{ id: 1 }],
			},
		};
		const next = mergePrimaryDirectionChartObj(chartObj, {
			pdRows: [[1, 'SUN', 'MOON', '', '2000-01-01']],
			showPdBounds: 1,
			pdMethod: 'horosa_legacy',
			pdTimeKey: 'Ptolemy',
			name: 'after',
			pos: 'after pos',
		});

		expect(next.chartId).toBe('chart-seq-1');
		expect(next.params.name).toBe('after');
		expect(next.params.pos).toBe('after pos');
		expect(next.params.showPdBounds).toBe(1);
		expect(next.params.pdtype).toBe(DEFAULT_PD_TYPE);
		expect(next.params.pdMethod).toBe('horosa_legacy');
		expect(next.params.pdTimeKey).toBe('Ptolemy');
		expect(next.params.pdSyncRev).toBe(PD_SYNC_REV);
		expect(next.predictives.primaryDirection).toEqual([[1, 'SUN', 'MOON', '', '2000-01-01']]);
		expect(next.predictives.firdaria).toEqual([{ id: 1 }]);
	});

	test('keeps valid direction sub tabs and falls back only for invalid keys', ()=>{
		expect(normalizePrimaryDirectionSubTabKey('primarydirchart')).toBe('primarydirchart');
		expect(normalizePrimaryDirectionSubTabKey('firdaria')).toBe('firdaria');
		expect(normalizePrimaryDirectionSubTabKey('unexpected')).toBe('primarydirect');
	});
});
