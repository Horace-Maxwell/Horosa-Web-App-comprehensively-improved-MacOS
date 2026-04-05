jest.mock('../localcharts', ()=>({
	listLocalCharts: jest.fn(()=>[
		{
			cid: 'chart-1',
			name: '测试命盘',
			birth: '2026-04-04 10:00:00',
			zone: '+08:00',
			group: '["事业"]',
			updateTime: '2026-04-04 10:00:00',
		},
	]),
}));

jest.mock('../localcases', ()=>({
	listLocalCases: jest.fn(()=>[
		{
			cid: 'case-1',
			event: '测试事盘',
			caseType: 'sanshiunited',
			sourceModule: 'sanshiunited',
			payload: JSON.stringify({
				snapshot: {
					content: '这是缓存的 AI 导出文本',
				},
			}),
			group: '["感情"]',
			divTime: '2026-04-04 11:00:00',
			updateTime: '2026-04-04 11:00:00',
		},
	]),
	getCaseTypeLabel: jest.fn((type)=>type),
	getCaseTypeMeta: jest.fn(()=>({ module: 'sanshiunited', value: 'sanshiunited' })),
}));

jest.mock('../astroAiSnapshot', ()=>({
	buildAstroSnapshotContent: jest.fn(()=> 'snapshot'),
}));

jest.mock('../../services/astro', ()=>({
	fetchChart: jest.fn(),
}));

jest.mock('../../components/comp/DateTime', ()=> jest.fn().mockImplementation(()=>({
	ad: 1,
	zone: '+08:00',
	clone(){
		return this;
	},
	startOf(){
		return this;
	},
	format(fmt){
		if(fmt === 'YYYY/MM/DD'){
			return '2026/04/04';
		}
		return '10:00:00';
	},
})));

import { buildPromptContext, listAnalysisSources } from '../aiAnalysisContext';

describe('aiAnalysisContext', ()=>{
	test('listAnalysisSources merges local charts and cases', ()=>{
		const sources = listAnalysisSources();
		expect(sources).toHaveLength(2);
		expect(sources[0]).toMatchObject({
			id: 'case-1',
			sourceType: 'case',
			snapshotStatus: 'ready',
		});
		expect(sources[1]).toMatchObject({
			id: 'chart-1',
			sourceType: 'chart',
		});
	});

	test('buildPromptContext includes source, materials and bundle templates', ()=>{
		const text = buildPromptContext({
			sourceContext: {
				title: '测试案例',
				content: '案例正文',
			},
			materials: [
				{
					name: '资料一',
					extractedText: '资料正文',
				},
			],
			bundles: [
				{
					name: '组合一',
					templateId: 'tpl-1',
				},
			],
			templates: [
				{
					id: 'tpl-1',
					name: '回复模版',
					format: 'text',
					content: '请按以下结构输出',
				},
			],
		});
		expect(text).toContain('案例前提：测试案例');
		expect(text).toContain('资料一');
		expect(text).toContain('模版约束：回复模版');
	});
});
