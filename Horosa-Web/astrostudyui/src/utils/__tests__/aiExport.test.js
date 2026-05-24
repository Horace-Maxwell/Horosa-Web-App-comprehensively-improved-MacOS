import {
	AI_EXPORT_SETTINGS_VERSION,
	getAIExportAuditMatrix,
	getAIExportEffectiveSectionsForTechnique,
	listAIExportTechniqueSettings,
	loadAIExportSettings,
	resolveAIExportContextForTest,
} from '../aiExport';
import { saveModuleAISnapshot } from '../moduleAiSnapshot';

const SETTINGS_KEY = 'horosa.ai.export.settings.v1';

function optionsByTechnique(){
	return listAIExportTechniqueSettings().reduce((acc, item)=>{
		acc[item.key] = item.options;
		return acc;
	}, {});
}

beforeEach(()=>{
	window.localStorage.clear();
});

describe('aiExport settings', ()=>{
	it('keeps every listed technique selectable with at least one export section', ()=>{
		const techniques = listAIExportTechniqueSettings();
		expect(techniques.length).toBeGreaterThan(20);
		techniques.forEach((item)=>{
			expect(item.key).toBeTruthy();
			expect(item.label).toBeTruthy();
			expect(item.options.length).toBeGreaterThan(0);
		});
	});

	it('exposes structured section groups for newly added techniques', ()=>{
		const options = optionsByTechnique();
		expect(options.suzhan).toEqual(expect.arrayContaining(['起盘信息', '宿盘宫位与二十八宿星曜']));
		expect(options.qimen).toEqual(expect.arrayContaining(['八宫详解', '九宫方盘', '九宫与宫内星体']));
		expect(options.jinkou).toEqual(expect.arrayContaining([
			'金口诀速览',
			'金口诀四位',
			'金口诀三盘',
			'四位神煞',
			'十二长生',
		]));
		expect(options.taiyi).toEqual(expect.arrayContaining([
			'太乙盘',
			'太乙诸神',
			'风游',
			'主客定算',
			'十二神',
			'八门与宿曜',
			'断法',
			'十六宫标记',
		]));
		expect(options.wuzhao).toEqual(expect.arrayContaining(['起盘', '揲筮', '兆', '木乡', '水乡', '特殊标记']));
		expect(options.taixuan).toEqual(expect.arrayContaining(['起盘', '玄首', '方州部家', '表']));
		expect(options.jingjue).toEqual(expect.arrayContaining(['起课', '卦辞', '三分', '十六卦']));
		expect(options.shenyishu).toEqual(expect.arrayContaining(['干支与五行', '神卦', '五行法则', '主客判断', '长生', '吉凶']));
		expect(options.germany).toEqual(expect.arrayContaining(['宫位宫头', '行星', '中点', '中点相位']));
		expect(options.otherbu).toEqual(expect.arrayContaining(['骰子结果', '骰子盘宫位与星体', '天象盘宫位与星体']));
		expect(options.bazi).toEqual(expect.arrayContaining(['四柱与三元', '神煞（四柱与三元）', '大运', '流年行运概略']));
		expect(options.ziwei).toEqual(expect.arrayContaining(['起盘信息', '宫位总览']));
		expect(options.qizhengkin).toEqual(expect.arrayContaining(['星曜', '张果断语', '命宫解读']));
		expect(options.tieban).toEqual(expect.arrayContaining(['十二宫', '十二宫条文', '紫微安星', '六亲佐证']));
		expect(options.cetian).toEqual(expect.arrayContaining(['命宮', '父母宮', '星曜属性', '飞化规则', '三合组']));
	});

	it('keeps every AI export technique wired to settings groups and an extractor path', ()=>{
		const matrix = getAIExportAuditMatrix();
		expect(matrix.length).toBeGreaterThan(40);
		matrix.forEach((item)=>{
			expect(item.key).toBeTruthy();
			expect(item.label).toBeTruthy();
			expect(item.presetSections.length).toBeGreaterThan(0);
			expect(item.options.length).toBeGreaterThan(0);
			expect(item.extractionKind).toBeTruthy();
			if(item.key !== 'generic'){
				expect(item.structuredSnapshotKeys.length).toBeGreaterThan(0);
			}
		});
		expect(matrix.filter((item)=>item.isJieQiSplit).map((item)=>item.key)).toEqual([
			'jieqi_meta',
			'jieqi_chunfen',
			'jieqi_xiazhi',
			'jieqi_qiufen',
			'jieqi_dongzhi',
		]);
		matrix.filter((item)=>item.isJieQiSplit).forEach((item)=>{
			expect(item.extractionKind).toBe('jieqi');
			expect(item.presetSections.length).toBeLessThanOrEqual(2);
		});
	});

	it('uses backend snapshot aliases for newly added structured techniques', ()=>{
		const byKey = getAIExportAuditMatrix().reduce((acc, item)=>{
			acc[item.key] = item;
			return acc;
		}, {});
		expect(byKey.sixyao.snapshotModuleKey).toBe('guazhan');
		expect(byKey.sixyao.structuredSnapshotKeys).toEqual(expect.arrayContaining(['guazhan', 'sixyao']));
		expect(byKey.qizhengkin.snapshotModuleKey).toBe('guolao-qizhengkin');
		expect(byKey.qizhengkin.structuredSnapshotKeys).toEqual(expect.arrayContaining(['guolao-qizhengkin', 'qizhengkin']));
		expect(byKey.shaozi.snapshotModuleKey).toBe('kinastro-shaozi');
		expect(byKey.tieban.snapshotModuleKey).toBe('kinastro-tieban');
		expect(byKey.fendjing.snapshotModuleKey).toBe('kinastro-fendjing');
		expect(byKey.beiji.snapshotModuleKey).toBe('kinastro-beiji');
		expect(byKey.nanji.snapshotModuleKey).toBe('kinastro-nanji');
		expect(byKey.chunzi.snapshotModuleKey).toBe('kinastro-chunzi');
		expect(byKey.xianqin.snapshotModuleKey).toBe('kinastro-xianqin');
		expect(byKey.cetian.snapshotModuleKey).toBe('kinastro-cetian');
		[
			'suzhan',
			'tongshefa',
			'huangji',
			'wuzhao',
			'taixuan',
			'jingjue',
			'shenyishu',
			'taiyi',
			'jinkou',
			'qimen',
			'sanshiunited',
			'bazi',
			'ziwei',
		].forEach((key)=>{
			expect(byKey[key].snapshotModuleKey).toBe(key);
		});
	});

	it('keeps split jieqi tab export scoped to the active tab section group', ()=>{
		const settings = {
			version: AI_EXPORT_SETTINGS_VERSION,
			sections: {
				jieqi_chunfen: ['春分星盘'],
				jieqi_xiazhi: ['夏至宿盘'],
				jieqi_qiufen: ['秋分星盘'],
				jieqi_dongzhi: ['冬至宿盘'],
			},
		};
		expect(getAIExportEffectiveSectionsForTechnique('jieqi_chunfen', settings)).toEqual(['春分星盘']);
		expect(getAIExportEffectiveSectionsForTechnique('jieqi_xiazhi', settings)).toEqual(['夏至宿盘']);
		expect(getAIExportEffectiveSectionsForTechnique('jieqi_qiufen', settings)).toEqual(['秋分星盘']);
		expect(getAIExportEffectiveSectionsForTechnique('jieqi_dongzhi', settings)).toEqual(['冬至宿盘']);
		expect(getAIExportEffectiveSectionsForTechnique('jieqi', settings)).toEqual(expect.arrayContaining([
			'春分星盘',
			'夏至宿盘',
			'秋分星盘',
			'冬至宿盘',
		]));
	});

	it('resolves the running jieqi export context to the active split setting key', ()=>{
		saveModuleAISnapshot('jieqi_current', [
			'[夏至星盘]',
			'太阳 巨蟹 0.00',
			'',
			'[夏至宿盘]',
			'夏至宿盘结构化内容',
		].join('\n'));
		const context = resolveAIExportContextForTest({
			key: 'jieqi',
			displayName: '节气盘',
		});
		expect(context.key).toBe('jieqi_xiazhi');
		expect(context.displayName).toBe('节气盘-夏至');
		expect(getAIExportEffectiveSectionsForTechnique(context.key, {
			version: AI_EXPORT_SETTINGS_VERSION,
			sections: {
				jieqi_xiazhi: ['夏至宿盘'],
			},
		})).toEqual(['夏至宿盘']);
	});

	it('migrates old per-technique selections so new backend sections are not silently filtered', ()=>{
		window.localStorage.setItem(SETTINGS_KEY, JSON.stringify({
			version: 7,
			sections: {
				suzhan: ['起盘信息'],
				qimen: ['起盘信息'],
				jinkou: ['起盘信息'],
				taiyi: ['起盘信息'],
				germany: ['起盘信息'],
				otherbu: ['起盘信息'],
				bazi: ['起盘信息'],
				ziwei: ['起盘信息'],
			},
		}));
		const settings = loadAIExportSettings();
		expect(settings.version).toBe(AI_EXPORT_SETTINGS_VERSION);
		expect(settings.sections.suzhan).toEqual(expect.arrayContaining(['宿盘宫位与二十八宿星曜']));
		expect(settings.sections.qimen).toEqual(expect.arrayContaining(['九宫与宫内星体']));
		expect(settings.sections.jinkou).toEqual(expect.arrayContaining(['金口诀三盘', '十二长生']));
		expect(settings.sections.taiyi).toEqual(expect.arrayContaining(['太乙诸神', '断法', '十六宫标记']));
		expect(settings.sections.germany).toEqual(expect.arrayContaining(['中点', '中点相位']));
		expect(settings.sections.otherbu).toEqual(expect.arrayContaining(['骰子结果', '天象盘宫位与星体']));
		expect(settings.sections.bazi).toEqual(expect.arrayContaining(['大运']));
		expect(settings.sections.ziwei).toEqual(expect.arrayContaining(['宫位总览']));
	});

	it('migrates corrected backend section names for kentang-derived techniques', ()=>{
		window.localStorage.setItem(SETTINGS_KEY, JSON.stringify({
			version: 8,
			sections: {
				wuzhao: ['五兆', '标记'],
				taixuan: ['起盘', '条文'],
				jingjue: ['起盘'],
				shenyishu: ['干支', '五行'],
				qizhengkin: ['命宫', '宿度'],
				tieban: ['宫位'],
				cetian: ['命宫', '父母宫', '十八飞星'],
			},
		}));
		const settings = loadAIExportSettings();
		expect(settings.version).toBe(AI_EXPORT_SETTINGS_VERSION);
		expect(settings.sections.wuzhao).toEqual(expect.arrayContaining(['揲筮', '兆', '特殊标记']));
		expect(settings.sections.taixuan).toEqual(expect.arrayContaining(['玄首', '方州部家', '表']));
		expect(settings.sections.jingjue).toEqual(expect.arrayContaining(['起课', '卦辞', '三分', '十六卦']));
		expect(settings.sections.shenyishu).toEqual(expect.arrayContaining(['干支与五行', '神卦', '五行法则', '主客判断', '吉凶']));
		expect(settings.sections.qizhengkin).toEqual(expect.arrayContaining(['星曜', '张果断语', '命宫解读']));
		expect(settings.sections.tieban).toEqual(expect.arrayContaining(['十二宫', '十二宫条文', '紫微安星']));
		expect(settings.sections.cetian).toEqual(expect.arrayContaining(['命宮', '父母宮', '星曜属性', '飞化规则']));
	});
});
