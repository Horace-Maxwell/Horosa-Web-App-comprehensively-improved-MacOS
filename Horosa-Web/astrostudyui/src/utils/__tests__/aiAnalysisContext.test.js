jest.mock('../localcharts', ()=>({
	listLocalCharts: jest.fn(()=>[
		{
			cid: 'chart-1',
			name: '测试命盘',
			birth: '2026-04-04 10:00:00',
			zone: '+08:00',
			lon: '118e27',
			lat: '31n38',
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
				moduleSnapshots: {
					liureng: {
						content: '大六壬结构化快照',
						meta: {
							date: '2026/04/04',
							time: '11:00',
						},
					},
					qimen: {
						content: '奇门遁甲结构化快照',
						meta: {
							date: '2026/04/04',
							time: '11:00',
						},
					},
				},
				snapshot: {
					content: '这是缓存的 AI 导出文本',
				},
			}),
			group: '["感情"]',
			divTime: '2026-04-04 11:00:00',
			updateTime: '2026-04-04 11:00:00',
		},
		{
			cid: 'case-2',
			event: '无快照六壬',
			caseType: 'liureng',
			sourceModule: 'liureng',
			payload: JSON.stringify({
				module: 'liureng',
				liureng: {
					nongli: {
						birth: '2026-04-04 12:00:00',
					},
				},
				runyear: { year: '丙午', age: 32 },
				wuxing: '木',
				guireng: 2,
			}),
			group: '["工作"]',
			divTime: '2026-04-04 12:00:00',
			zone: '+08:00',
			lon: '118e27',
			lat: '31n38',
			updateTime: '2026-04-04 12:00:00',
		},
		{
			cid: 'case-3',
			event: '空载六壬',
			caseType: 'liureng',
			sourceModule: 'liureng',
			payload: JSON.stringify({}),
			group: '["工作"]',
			divTime: '2026-04-04 13:00:00',
			zone: '+08:00',
			lon: '118e27',
			lat: '31n38',
			updateTime: '2026-04-04 13:00:00',
		},
	]),
	getCaseTypeLabel: jest.fn((type)=>type),
	getCaseTypeMeta: jest.fn(()=>({ module: 'sanshiunited', value: 'sanshiunited' })),
}));

const mockLoadAstroAISnapshot = jest.fn(()=>null);

jest.mock('../astroAiSnapshot', ()=>({
	buildAstroSnapshotContent: jest.fn(()=> 'snapshot'),
	loadAstroAISnapshot: (...args)=>mockLoadAstroAISnapshot(...args),
}));

const mockSaveModuleAISnapshot = jest.fn();
const mockModuleSnapshots = {
	primarydirect: '主限法结构化快照',
	bazi: '八字结构化快照',
	ziwei: '紫微斗数结构化快照',
	guolao: '七政四余结构化快照',
	germany: '量化盘结构化快照',
	jieqi: '节气盘结构化快照',
	jieqi_meta: '节气盘参数结构化快照',
	jieqi_chunfen: '节气盘春分快照',
	jieqi_xiazhi: '节气盘夏至快照',
	jieqi_qiufen: '节气盘秋分快照',
	jieqi_dongzhi: '节气盘冬至快照',
	indiachart: '印度律盘结构化快照',
	relative: '关系盘结构化快照',
	guazhan: '六爻结构化快照',
	tongshefa: '统摄法结构化快照',
	suzhan: '宿占结构化快照',
	fengshui: '风水结构化快照',
	otherbu: '西洋游戏结构化快照',
	qimen: '奇门遁甲结构化快照',
	jinkou: '金口诀结构化快照',
	taiyi: '太乙结构化快照',
	sanshiunited: '三式合一结构化快照',
};

jest.mock('../moduleAiSnapshot', ()=>({
	loadModuleAISnapshot: jest.fn((moduleName)=>{
		if(mockModuleSnapshots[moduleName]){
			return {
				content: mockModuleSnapshots[moduleName],
				meta: {
					date: '2026/04/04',
					time: '10:00',
					zone: '+08:00',
				},
			};
		}
		return null;
	}),
	saveModuleAISnapshot: (...args)=>mockSaveModuleAISnapshot(...args),
}));

jest.mock('../../services/astro', ()=>({
	fetchChart: jest.fn(async ()=>({
		Result: {
			chart: {
				objects: [],
				stars: [],
			},
			lots: [],
		},
	})),
}));

jest.mock('../request', ()=>({
	__esModule: true,
	default: jest.fn(async ()=>({
		Result: {
			liureng: {
				nongli: {
					time: '午时',
					dayGanZi: '甲子',
				},
			},
		},
	})),
}));

jest.mock('../preciseCalcBridge', ()=>({
	fetchPreciseNongli: jest.fn(async ()=>({
		jieqi: '惊蛰',
		runyear: '丙午',
		ganzhi: {
			year: '甲子',
			month: '乙丑',
			day: '丙寅',
			time: '丁卯',
		},
	})),
}));

jest.mock('../aiAnalysisStore', ()=>({
	AI_ANALYSIS_STORES: {
		contextCache: 'contextCache',
	},
	getStoreRecord: jest.fn(async ()=>null),
	putStoreRecord: jest.fn(async (storeName, record)=>record),
}));

jest.mock('../../components/lrzhan/LiuRengMain', ()=>({
	buildLiuRengSnapshotText: jest.fn(()=> '自动生成的大六壬快照'),
}));

jest.mock('../../components/jinkou/JinKouMain', ()=>({
	buildJinKouSnapshotText: jest.fn(()=> '自动生成的金口诀快照'),
}));

jest.mock('../../components/jinkou/JinKouCalc', ()=>({
	buildJinKouData: jest.fn(()=>({ ready: true, topInfo: { diFen: '子' }, rows: [] })),
}));

jest.mock('../../components/jinkou/JinKouState', ()=>({
	resolveJinKouDiFen: jest.fn(()=> '子'),
}));

jest.mock('../../components/dunjia/DunJiaCalc', ()=>({
	calcDunJia: jest.fn(()=>({ kind: 'qimen-pan' })),
	buildDunJiaSnapshotText: jest.fn(()=> '自动生成的奇门快照'),
}));

jest.mock('../../components/taiyi/TaiYiCalc', ()=>({
	calcTaiyi: jest.fn(()=>({ kind: 'taiyi-pan' })),
	buildTaiyiSnapshotText: jest.fn(()=> '自动生成的太乙快照'),
}));

jest.mock('../../components/tongshefa/TongSheFaMain', ()=>({
	buildTongSheFaModel: jest.fn((selection)=>selection),
	buildTongSheFaSnapshot: jest.fn(()=> '自动生成的统摄法快照'),
}));

jest.mock('../../components/guazhan/GuaZhanMain', ()=>({
	buildGuaSnapshotText: jest.fn(()=> '自动生成的六爻快照'),
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

import {
	ANALYSIS_CASE_TECHNIQUES,
	ANALYSIS_CHART_TECHNIQUES,
	buildPromptContext,
	getAnalysisTechniqueContexts,
	getAnalysisSourceContext,
	listAnalysisSources,
	listAnalysisTechniqueOptions,
} from '../aiAnalysisContext';

describe('aiAnalysisContext', ()=>{
	beforeEach(()=>{
		mockSaveModuleAISnapshot.mockClear();
		mockLoadAstroAISnapshot.mockReset();
		mockLoadAstroAISnapshot.mockReturnValue(null);
	});

	test('listAnalysisSources merges local charts and cases', ()=>{
		const sources = listAnalysisSources();
		expect(sources).toHaveLength(4);
		expect(sources[0]).toMatchObject({
			id: 'case-3',
			sourceType: 'case',
			snapshotStatus: 'generated',
		});
		expect(sources[1]).toMatchObject({
			id: 'case-2',
			sourceType: 'case',
			snapshotStatus: 'generated',
		});
		expect(sources[2]).toMatchObject({
			id: 'case-1',
			sourceType: 'case',
			snapshotStatus: 'ready',
		});
		expect(sources[3]).toMatchObject({
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
			techniqueContexts: [
				{
					key: 'liureng',
					title: '大六壬',
					content: '大六壬结构化快照',
				},
			],
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
		expect(text).toContain('使用技法：大六壬');
		expect(text).toContain('资料一');
		expect(text).toContain('模版约束：回复模版');
	});

	test('listAnalysisTechniqueOptions separates chart and case techniques', ()=>{
		const sources = listAnalysisSources();
		const caseSource = sources.find((item)=>item.sourceType === 'case');
		const chartSource = sources.find((item)=>item.sourceType === 'chart');
		const caseOptions = listAnalysisTechniqueOptions(caseSource).map((item)=>item.value);
		const chartOptions = listAnalysisTechniqueOptions(chartSource).map((item)=>item.value);

		expect(caseOptions).toContain('liureng');
		expect(caseOptions).toContain('qimen');
		expect(caseOptions).not.toContain('primarydirect');
		expect(chartOptions).toContain('astrochart');
		expect(chartOptions).toContain('primarydirect');
		expect(chartOptions).toContain('guolao');
		expect(chartOptions).toContain('cntradition');
		expect(chartOptions).not.toContain('liureng');
	});

	test('getAnalysisTechniqueContexts resolves case technique snapshots from payload', async ()=>{
		const sources = listAnalysisSources();
		const caseSource = sources.find((item)=>item.id === 'case-1');
		const contexts = await getAnalysisTechniqueContexts(caseSource, ['liureng', 'qimen']);

		expect(contexts).toEqual(expect.arrayContaining([
			expect.objectContaining({
				key: 'liureng',
				available: true,
				content: '大六壬结构化快照',
			}),
			expect.objectContaining({
				key: 'qimen',
				available: true,
				content: '奇门遁甲结构化快照',
			}),
		]));
	});

	test('getAnalysisTechniqueContexts resolves chart technique snapshots from module cache', async ()=>{
		const sources = listAnalysisSources();
		const chartSource = sources.find((item)=>item.sourceType === 'chart');
		const contexts = await getAnalysisTechniqueContexts(chartSource, ['primarydirect']);

		expect(contexts).toEqual([
			expect.objectContaining({
				key: 'primarydirect',
				available: true,
				content: '主限法结构化快照',
			}),
		]);
	});

	test('getAnalysisSourceContext reuses matching stored astro snapshot before live fetch', async ()=>{
		mockLoadAstroAISnapshot.mockReturnValue({
			content: '已保存的星盘结构化快照',
			signature: 'chart-any|2026-04-04 10:00:00|+08:00|118e27|31n38|Tropical|Placidus|1|0',
		});
		const sources = listAnalysisSources();
		const chartSource = sources.find((item)=>item.sourceType === 'chart');
		const context = await getAnalysisSourceContext(chartSource, { preferCache: false });

		expect(context.content).toBe('已保存的星盘结构化快照');
		expect(context.meta).toMatchObject({
			reusedStoredSnapshot: true,
		});
	});

	test('chart techniques reuse matching stored astro snapshot on technique-only load', async ()=>{
		mockLoadAstroAISnapshot.mockReturnValue({
			content: '已保存的星盘结构化快照',
			signature: 'chart-any|2026-04-04 10:00:00|+08:00|118e27|31n38|Tropical|Placidus|1|0',
		});
		const sources = listAnalysisSources();
		const chartSource = sources.find((item)=>item.sourceType === 'chart');
		const contexts = await getAnalysisTechniqueContexts(chartSource, ['astrochart'], {
			sourceContext: await getAnalysisSourceContext(chartSource, { preferCache: false, mode: 'meta' }),
		});

		expect(contexts).toEqual([
			expect.objectContaining({
				key: 'astrochart',
				available: true,
				content: '已保存的星盘结构化快照',
			}),
		]);
	});

	test('getAnalysisSourceContext auto generates case snapshot from stored payload when missing', async ()=>{
		const sources = listAnalysisSources();
		const source = sources.find((item)=>item.id === 'case-2');
		const context = await getAnalysisSourceContext(source, { preferCache: false });

		expect(context.content).toBe('自动生成的大六壬快照');
		expect(mockSaveModuleAISnapshot).toHaveBeenCalledWith(
			'liureng',
			'自动生成的大六壬快照',
			expect.objectContaining({
				date: '2026/04/04',
				time: '12:00',
			})
		);
	});

	test('getAnalysisTechniqueContexts auto generates missing case technique snapshot and saves it', async ()=>{
		const sources = listAnalysisSources();
		const source = sources.find((item)=>item.id === 'case-2');
		const contexts = await getAnalysisTechniqueContexts(source, ['liureng']);

		expect(contexts).toEqual([
			expect.objectContaining({
				key: 'liureng',
				available: true,
				content: '自动生成的大六壬快照',
			}),
		]);
		expect(mockSaveModuleAISnapshot).toHaveBeenCalledWith(
			'liureng',
			'自动生成的大六壬快照',
			expect.objectContaining({
				generatedFromStoredCase: true,
			})
		);
	});

	test('getAnalysisTechniqueContexts regenerates case technique snapshot from stored case info when payload is empty', async ()=>{
		const sources = listAnalysisSources();
		const source = sources.find((item)=>item.id === 'case-3');
		const contexts = await getAnalysisTechniqueContexts(source, ['liureng', 'qimen', 'taiyi']);

		expect(contexts).toEqual(expect.arrayContaining([
			expect.objectContaining({
				key: 'liureng',
				available: true,
				content: '自动生成的大六壬快照',
			}),
			expect.objectContaining({
				key: 'qimen',
				available: true,
				content: '奇门遁甲结构化快照',
			}),
			expect.objectContaining({
				key: 'taiyi',
				available: true,
				content: '太乙结构化快照',
			}),
		]));
	});

	test('getAnalysisTechniqueContexts uses only the selected chart technique snapshot', async ()=>{
		const sources = listAnalysisSources();
		const chartSource = sources.find((item)=>item.sourceType === 'chart');
		const contexts = await getAnalysisTechniqueContexts(chartSource, ['bazi']);

		expect(contexts).toEqual([
			expect.objectContaining({
				key: 'bazi',
				available: true,
				content: '八字结构化快照',
			}),
		]);
		expect(contexts[0].content).not.toContain('紫微');
		expect(mockSaveModuleAISnapshot).not.toHaveBeenCalledWith(
			'bazi',
			expect.any(String),
			expect.objectContaining({
				generatedFromBaseChart: true,
			})
		);
	});

	test('getAnalysisTechniqueContexts does not fall back to generic chart snapshot for unrelated chart techniques', async ()=>{
		const sources = listAnalysisSources();
		const chartSource = sources.find((item)=>item.sourceType === 'chart');
		const contexts = await getAnalysisTechniqueContexts(chartSource, ['cntradition'], {
			sourceContext: {
				content: '基础命盘结构化快照',
			},
		});

		expect(contexts).toEqual([
			expect.objectContaining({
				key: 'cntradition',
				available: false,
				content: '',
				status: 'missing',
			}),
		]);
	});

	test('each chart technique selection mounts only its own content or stays missing', async ()=>{
		const sources = listAnalysisSources();
		const chartSource = sources.find((item)=>item.sourceType === 'chart');
		const expectedByTechnique = {
			astrochart: 'snapshot',
			astrochart_like: 'snapshot',
			indiachart: '印度律盘结构化快照',
			relative: '关系盘结构化快照',
			guolao: '七政四余结构化快照',
			germany: '量化盘结构化快照',
			jieqi: '节气盘结构化快照',
			jieqi_meta: '节气盘参数结构化快照',
			jieqi_chunfen: '节气盘春分快照',
			jieqi_xiazhi: '节气盘夏至快照',
			jieqi_qiufen: '节气盘秋分快照',
			jieqi_dongzhi: '节气盘冬至快照',
			primarydirect: '主限法结构化快照',
			primarydirchart: '主限法结构化快照',
			bazi: '八字结构化快照',
			ziwei: '紫微斗数结构化快照',
			suzhan: '宿占结构化快照',
			otherbu: '西洋游戏结构化快照',
			fengshui: '风水结构化快照',
		};
		for(const key of ANALYSIS_CHART_TECHNIQUES){
			// eslint-disable-next-line no-await-in-loop
			const contexts = await getAnalysisTechniqueContexts(chartSource, [key], {
				sourceContext: await getAnalysisSourceContext(chartSource, { preferCache: false, mode: 'meta' }),
			});
			expect(contexts).toHaveLength(1);
			expect(contexts[0].key).toBe(key);
			if(expectedByTechnique[key]){
				expect(contexts[0].available).toBe(true);
				expect(contexts[0].content).toContain(expectedByTechnique[key]);
			}else{
				expect(contexts[0].available).toBe(false);
				expect(contexts[0].status).toBe('missing');
			}
		}
	});

	test('each case technique selection mounts only its own content', async ()=>{
		const sources = listAnalysisSources();
		const caseSource = sources.find((item)=>item.id === 'case-1');
		const expectedByTechnique = {
			sixyao: '六爻结构化快照',
			tongshefa: '统摄法结构化快照',
			liureng: '大六壬结构化快照',
			jinkou: '金口诀结构化快照',
			qimen: '奇门遁甲结构化快照',
			sanshiunited: '三式合一结构化快照',
			taiyi: '太乙结构化快照',
			suzhan: '宿占结构化快照',
		};
		for(const key of ANALYSIS_CASE_TECHNIQUES){
			// eslint-disable-next-line no-await-in-loop
			const contexts = await getAnalysisTechniqueContexts(caseSource, [key], {
				sourceContext: await getAnalysisSourceContext(caseSource, { preferCache: false, mode: 'meta' }),
			});
			expect(contexts).toHaveLength(1);
			expect(contexts[0].key).toBe(key);
			expect(contexts[0].available).toBe(true);
			expect(contexts[0].content).toContain(expectedByTechnique[key]);
		}
	});

	test('getAnalysisSourceContext returns metadata-only case context when technique mode is active', async ()=>{
		const sources = listAnalysisSources();
		const source = sources.find((item)=>item.id === 'case-1');
		const context = await getAnalysisSourceContext(source, {
			preferCache: false,
			mode: 'meta',
		});

		expect(context.content).toContain('案例名称：测试事盘');
		expect(context.content).not.toContain('大六壬结构化快照');
		expect(context.content).not.toContain('奇门遁甲结构化快照');
	});

	test('getAnalysisSourceContext returns metadata-only chart context when technique mode is active', async ()=>{
		const sources = listAnalysisSources();
		const source = sources.find((item)=>item.sourceType === 'chart');
		const context = await getAnalysisSourceContext(source, {
			preferCache: false,
			mode: 'meta',
		});

		expect(context.content).toContain('命盘名称：测试命盘');
		expect(context.content).toContain('出生时间：2026-04-04 10:00:00');
		expect(context.content).not.toContain('snapshot');
	});
});
