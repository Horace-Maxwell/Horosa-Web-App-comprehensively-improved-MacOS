import {
	CASE_TYPE_OPTIONS,
	exportLocalCasesBackup,
	getCaseTypeLabel,
	getCaseTypeMeta,
	getPagedLocalCases,
	importLocalCasesBackup,
	listLocalCases,
	removeLocalCase,
	upsertLocalCase,
} from '../localcases';
import {
	exportLocalChartsBackup,
	getPagedLocalCharts,
	importLocalChartsBackup,
	listLocalCharts,
	removeLocalChart,
	upsertLocalChart,
} from '../localcharts';
import { openKentangCaseDrawer } from '../kentangCaseSave';
import { isEditableChartRecord } from '../../components/user/ChartList';

beforeEach(()=>{
	window.localStorage.clear();
});

describe('local chart and case management', ()=>{
	it('keeps every newly added divination case type addressable', ()=>{
		const expected = ['suzhan', 'jinkou', 'tongshefa', 'huangji', 'wuzhao', 'taixuan', 'jingjue', 'shenyishu'];
		const values = CASE_TYPE_OPTIONS.map((item)=>item.value);
		expect(new Set(values).size).toBe(values.length);
		expect(values).toEqual(expect.arrayContaining([
			'liuyao',
			'liureng',
			'taiyi',
			'qimen',
			'sanshiunited',
			...expected,
		]));
		expected.forEach((key)=>{
			const option = CASE_TYPE_OPTIONS.find((item)=>item.value === key);
			expect(option).toBeTruthy();
			expect(getCaseTypeMeta(key).value).toBe(key);
			expect(getCaseTypeMeta(key).tab).toBe('cnyibu');
			expect(getCaseTypeMeta(key).subTab).toBe(key);
			expect(getCaseTypeLabel(key)).toBe(option.label);
		});
		expect(getCaseTypeMeta('皇极经世').value).toBe('huangji');
		expect(getCaseTypeMeta('宿盘').value).toBe('suzhan');
		expect(getCaseTypeMeta('金口诀').tab).toBe('cnyibu');
		expect(getCaseTypeMeta('神易数').value).toBe('shenyishu');
	});

	it('routes every managed case family back to the correct workspace', ()=>{
		const expectedRoutes = {
			liuyao: ['guazhan', null, 'guazhan'],
			liureng: ['liureng', null, 'liureng'],
			taiyi: ['taiyi', null, 'taiyi'],
			qimen: ['dunjia', null, 'qimen'],
			sanshiunited: ['sanshiunited', null, 'sanshiunited'],
			suzhan: ['cnyibu', 'suzhan', 'suzhan'],
			jinkou: ['cnyibu', 'jinkou', 'jinkou'],
			huangji: ['cnyibu', 'huangji', 'huangji'],
			wuzhao: ['cnyibu', 'wuzhao', 'wuzhao'],
			taixuan: ['cnyibu', 'taixuan', 'taixuan'],
			jingjue: ['cnyibu', 'jingjue', 'jingjue'],
			shenyishu: ['cnyibu', 'shenyishu', 'shenyishu'],
		};
		Object.keys(expectedRoutes).forEach((key)=>{
			const meta = getCaseTypeMeta(key);
			expect(meta.tab).toBe(expectedRoutes[key][0]);
			expect(meta.subTab).toBe(expectedRoutes[key][1]);
			expect(meta.module).toBe(expectedRoutes[key][2]);
		});
	});

	it('does not collapse future kentang case types to liuyao', ()=>{
		const rec = upsertLocalCase({
			event: 'future module smoke',
			caseType: 'future-kentang-module',
			divTime: '2026-05-23 09:10:11',
			zone: '+08:00',
			lat: '0n00',
			lon: '0e00',
			payload: { options: { mode: 'x' }, result: { ok: true } },
			sourceModule: 'future-kentang-module',
		});
		expect(rec.caseType).toBe('future-kentang-module');
		expect(getCaseTypeMeta(rec.caseType).module).toBe('future-kentang-module');
		const saved = listLocalCases({})[0];
		expect(saved.caseType).toBe('future-kentang-module');
		expect(JSON.parse(saved.payload).options.mode).toBe('x');
	});

	it('infers managed case type and module metadata from legacy sourceModule-only records', ()=>{
		const rec = upsertLocalCase({
			cid: 'legacy-source-only-case',
			event: '旧备份五兆',
			divTime: '2026-05-23 09:10:11',
			zone: '+08:00',
			lat: '0n00',
			lon: '0e00',
			payload: { pan: { stable: 'legacy-wuzhao' } },
			sourceModule: 'wuzhao',
		});
		expect(rec.caseType).toBe('wuzhao');
		expect(rec.sourceModule).toBe('wuzhao');
		expect(getCaseTypeMeta(rec.caseType).tab).toBe('cnyibu');
		expect(getCaseTypeMeta(rec.caseType).subTab).toBe('wuzhao');
		expect(JSON.parse(rec.payload).pan.stable).toBe('legacy-wuzhao');
	});

	it('preserves case payload, source module, zero coordinates, and backup update time', ()=>{
		importLocalCasesBackup({
			format: 'horosa-local-cases',
			version: 1,
			cases: [{
				cid: 'case-import-1',
				event: '五兆备份',
				caseType: 'wuzhao',
				divTime: '2026-05-23 10:11:12',
				zone: '+08:00',
				lat: '0n00',
				lon: '0e00',
				gpsLat: 0,
				gpsLon: 0,
				payload: JSON.stringify({ module: 'wuzhao', options: { manual: true }, pan: { key: 'kept' } }),
				sourceModule: 'wuzhao',
				updateTime: '2026-05-22 01:02:03',
			}],
		});
		const saved = listLocalCases({})[0];
		expect(saved.caseType).toBe('wuzhao');
		expect(saved.sourceModule).toBe('wuzhao');
		expect(saved.gpsLat).toBe(0);
		expect(saved.gpsLon).toBe(0);
		expect(saved.updateTime).toBe('2026-05-22 01:02:03');
		expect(JSON.parse(saved.payload).pan.key).toBe('kept');
	});

	it('round-trips every managed case type without losing hidden payload data', ()=>{
		CASE_TYPE_OPTIONS.forEach((option, idx)=>{
			upsertLocalCase({
				cid: `case-type-${option.value}`,
				event: `${option.label}测试`,
				caseType: option.value,
				divTime: `2026-05-23 10:${String(idx).padStart(2, '0')}:12`,
				zone: '+08:00',
				lat: '0n00',
				lon: '0e00',
				gpsLat: 0,
				gpsLon: 0,
				payload: {
					module: option.module,
					options: { idx },
					pan: { stable: option.value },
				},
				sourceModule: option.module,
			});
		});
		CASE_TYPE_OPTIONS.forEach((option)=>{
			upsertLocalCase({
				cid: `case-type-${option.value}`,
				event: `${option.label}改名`,
			});
		});

		const saved = listLocalCases({});
		expect(saved.length).toBe(CASE_TYPE_OPTIONS.length);
		CASE_TYPE_OPTIONS.forEach((option)=>{
			const one = saved.find((item)=>item.cid === `case-type-${option.value}`);
			expect(one).toBeTruthy();
			expect(one.event).toBe(`${option.label}改名`);
			expect(one.caseType).toBe(option.value);
			expect(one.sourceModule).toBe(option.module);
			expect(one.gpsLat).toBe(0);
			expect(one.gpsLon).toBe(0);
			expect(JSON.parse(one.payload).pan.stable).toBe(option.value);
		});
	});

	it('supports managed case search, pagination, backup export/import, and deletion', ()=>{
		CASE_TYPE_OPTIONS.forEach((option, idx)=>{
			upsertLocalCase({
				cid: `case-flow-${option.value}`,
				event: idx % 2 === 0 ? `${option.label}根基测试` : `${option.label}普通测试`,
				caseType: option.value,
				divTime: `2026-05-23 13:${String(idx).padStart(2, '0')}:00`,
				zone: '+08:00',
				lat: '0n00',
				lon: '0e00',
				payload: { module: option.module, pan: { key: option.value } },
				sourceModule: option.module,
			});
		});
		const firstPage = getPagedLocalCases({ PageIndex: 1, PageSize: 5 });
		expect(firstPage.List.length).toBe(5);
		expect(firstPage.Total).toBe(CASE_TYPE_OPTIONS.length);

		const searched = getPagedLocalCases({ PageIndex: 1, PageSize: 30, name: '根基' });
		expect(searched.List.length).toBeGreaterThan(0);
		searched.List.forEach((item)=> expect(item.event.indexOf('根基')).toBeGreaterThanOrEqual(0));

		const backup = exportLocalCasesBackup();
		expect(backup.total).toBe(CASE_TYPE_OPTIONS.length);
		expect(backup.cases.find((item)=>item.caseType === 'wuzhao')).toBeTruthy();

		removeLocalCase('case-flow-wuzhao');
		expect(listLocalCases({}).find((item)=>item.cid === 'case-flow-wuzhao')).toBeFalsy();

		window.localStorage.clear();
		const imported = importLocalCasesBackup(backup);
		expect(imported.imported).toBe(CASE_TYPE_OPTIONS.length);
		const restored = listLocalCases({}).find((item)=>item.cid === 'case-flow-wuzhao');
		expect(restored).toBeTruthy();
		expect(JSON.parse(restored.payload).pan.key).toBe('wuzhao');
	});

	it('preserves chart core fields, memos, and backup update time', ()=>{
		importLocalChartsBackup({
			format: 'horosa-local-charts',
			version: 1,
			charts: [{
				cid: 'chart-import-1',
				name: '命法测试',
				birth: '2026-05-23 10:11:12',
				zone: '+08:00',
				lat: '0n00',
				lon: '0e00',
				gpsLat: 0,
				gpsLon: 0,
				pos: '赤道',
				gender: 1,
				doubingSu28: 1,
				memo74: '七政批注',
				memoZiWei: '紫微批注',
				payload: JSON.stringify({ module: 'ziwei', daXian: 35 }),
				sourceModule: 'ziwei',
				chartType: 'ziwei',
				updateTime: '2026-05-22 02:03:04',
			}],
		});
		const saved = listLocalCharts({})[0];
		expect(saved.name).toBe('命法测试');
		expect(saved.gpsLat).toBe(0);
		expect(saved.gpsLon).toBe(0);
		expect(saved.doubingSu28).toBe(1);
		expect(saved.memo74).toBe('七政批注');
		expect(saved.memoZiWei).toBe('紫微批注');
		expect(saved.sourceModule).toBe('ziwei');
		expect(saved.chartType).toBe('ziwei');
		expect(JSON.parse(saved.payload).daXian).toBe(35);
		expect(saved.updateTime).toBe('2026-05-22 02:03:04');
	});

	it('keeps imported local chart records editable even when their cid is not local-prefixed', ()=>{
		expect(isEditableChartRecord({
			cid: 'chart-import-legacy-1',
			creator: 'local',
		}, null)).toBe(true);
		expect(isEditableChartRecord({
			cid: 'remote-chart-1',
			creator: 'user-1',
		}, { uid: 'user-1' })).toBe(true);
		expect(isEditableChartRecord({
			cid: 'remote-chart-2',
			creator: 'user-2',
		}, { uid: 'user-1' })).toBe(false);
	});

	it('round-trips every managed chart family without losing payload or module metadata', ()=>{
		const chartFamilies = [
			'astrochart',
			'indiachart',
			'bazi',
			'ziwei',
			'guolao',
			'qizhengkin',
			'shaozi',
			'tieban',
			'fendjing',
			'beiji',
			'nanji',
			'chunzi',
			'xianqin',
			'cetian',
			'germany',
			'jieqi',
		];
		chartFamilies.forEach((module, idx)=>{
			upsertLocalChart({
				cid: `chart-family-${module}`,
				name: `${module}命盘`,
				birth: `2026-05-23 11:${String(idx).padStart(2, '0')}:12`,
				zone: '+08:00',
				lat: '26n04',
				lon: '119e19',
				gpsLat: 26.0667,
				gpsLon: 119.3167,
				gender: idx % 2,
				payload: {
					module,
					options: { idx },
					pan: { stable: module },
				},
				sourceModule: module,
				chartType: module,
			});
		});
		chartFamilies.forEach((module)=>{
			upsertLocalChart({
				cid: `chart-family-${module}`,
				name: `${module}改名`,
			});
		});

		const saved = listLocalCharts({});
		expect(saved.length).toBe(chartFamilies.length);
		chartFamilies.forEach((module)=>{
			const one = saved.find((item)=>item.cid === `chart-family-${module}`);
			expect(one).toBeTruthy();
			expect(one.name).toBe(`${module}改名`);
			expect(one.sourceModule).toBe(module);
			expect(one.chartType).toBe(module);
			expect(one.gpsLat).toBe(26.0667);
			expect(one.gpsLon).toBe(119.3167);
			expect(JSON.parse(one.payload).pan.stable).toBe(module);
		});
	});

	it('infers chart type from legacy sourceModule-only chart records', ()=>{
		const rec = upsertLocalChart({
			cid: 'legacy-source-only-chart',
			name: '旧备份策天',
			birth: '2026-05-23 14:15:16',
			zone: '+08:00',
			lat: '26n04',
			lon: '119e19',
			payload: { module: 'cetian', pan: { key: 'legacy-cetian' } },
			sourceModule: 'cetian',
		});
		expect(rec.sourceModule).toBe('cetian');
		expect(rec.chartType).toBe('cetian');
		expect(JSON.parse(rec.payload).pan.key).toBe('legacy-cetian');
	});

	it('does not collapse future chart techniques or source-only chart backups', ()=>{
		const rec = upsertLocalChart({
			cid: 'future-source-only-chart',
			name: '未来命法',
			birth: '2026-05-23 16:17:18',
			zone: '+08:00',
			lat: '26n04',
			lon: '119e19',
			payload: {
				module: 'future-chart-module',
				options: { mode: 'future' },
				pan: { stable: 'future-chart-module' },
			},
			sourceModule: 'future-chart-module',
		});
		expect(rec.sourceModule).toBe('future-chart-module');
		expect(rec.chartType).toBe('future-chart-module');
		expect(JSON.parse(rec.payload).options.mode).toBe('future');

		const backup = exportLocalChartsBackup();
		window.localStorage.clear();
		const imported = importLocalChartsBackup(backup);
		expect(imported.imported).toBe(1);
		const restored = listLocalCharts({})[0];
		expect(restored.sourceModule).toBe('future-chart-module');
		expect(restored.chartType).toBe('future-chart-module');
		expect(JSON.parse(restored.payload).pan.stable).toBe('future-chart-module');
	});

	it('supports managed chart search, pagination, backup export/import, and deletion', ()=>{
		const chartFamilies = [
			'astrochart',
			'indiachart',
			'bazi',
			'ziwei',
			'guolao',
			'qizhengkin',
			'shaozi',
			'tieban',
			'fendjing',
			'beiji',
			'nanji',
			'chunzi',
			'xianqin',
			'cetian',
			'germany',
			'jieqi',
		];
		chartFamilies.forEach((module, idx)=>{
			upsertLocalChart({
				cid: `chart-flow-${module}`,
				name: idx % 2 === 0 ? `${module}根基测试` : `${module}普通测试`,
				birth: `2026-05-23 15:${String(idx).padStart(2, '0')}:00`,
				zone: '+08:00',
				lat: '26n04',
				lon: '119e19',
				gpsLat: 26.0667,
				gpsLon: 119.3167,
				payload: { module, pan: { key: module } },
				sourceModule: module,
				chartType: module,
			});
		});
		const firstPage = getPagedLocalCharts({ PageIndex: 1, PageSize: 6 });
		expect(firstPage.List.length).toBe(6);
		expect(firstPage.Total).toBe(chartFamilies.length);

		const searched = getPagedLocalCharts({ PageIndex: 1, PageSize: 30, name: '根基' });
		expect(searched.List.length).toBeGreaterThan(0);
		searched.List.forEach((item)=> expect(item.name.indexOf('根基')).toBeGreaterThanOrEqual(0));

		const backup = exportLocalChartsBackup();
		expect(backup.total).toBe(chartFamilies.length);
		expect(backup.charts.find((item)=>item.chartType === 'cetian')).toBeTruthy();

		removeLocalChart('chart-flow-cetian');
		expect(listLocalCharts({}).find((item)=>item.cid === 'chart-flow-cetian')).toBeFalsy();

		window.localStorage.clear();
		const imported = importLocalChartsBackup(backup);
		expect(imported.imported).toBe(chartFamilies.length);
		const restored = listLocalCharts({}).find((item)=>item.cid === 'chart-flow-cetian');
		expect(restored).toBeTruthy();
		expect(restored.chartType).toBe('cetian');
		expect(JSON.parse(restored.payload).pan.key).toBe('cetian');
	});

	it('updates chart records without dropping existing identifying data when all fields are supplied', ()=>{
		upsertLocalChart({
			cid: 'chart-update-1',
			name: '初始',
			birth: '2026-05-23 10:11:12',
			zone: '+08:00',
			lat: '26n04',
			lon: '119e19',
			gender: 1,
			memoQiMeng: '奇门批注',
		});
		upsertLocalChart({
			cid: 'chart-update-1',
			name: '更新',
			birth: '2026-05-23 10:11:12',
			zone: '+08:00',
			lat: '26n04',
			lon: '119e19',
			gender: 1,
			memoQiMeng: '奇门批注',
			memoSuZhan: '宿占批注',
		});
		const saved = listLocalCharts({})[0];
		expect(saved.name).toBe('更新');
		expect(saved.memoQiMeng).toBe('奇门批注');
		expect(saved.memoSuZhan).toBe('宿占批注');
	});

	it('preserves existing chart and case detail fields during partial updates', ()=>{
		upsertLocalChart({
			cid: 'partial-chart-1',
			name: '完整命盘',
			birth: '2026-05-23 10:11:12',
			zone: '+08:00',
			lat: '26n04',
			lon: '119e19',
			gpsLat: 26.0667,
			gpsLon: 119.3167,
			gender: 1,
			memoZiWei: '紫微原文',
			payload: { module: 'cetian', activeTab: 'overview' },
			sourceModule: 'mingother',
			chartType: 'cetian',
		});
		upsertLocalChart({
			cid: 'partial-chart-1',
			name: '改名命盘',
		});
		const chart = listLocalCharts({})[0];
		expect(chart.name).toBe('改名命盘');
		expect(chart.memoZiWei).toBe('紫微原文');
		expect(chart.lat).toBe('26n04');
		expect(chart.lon).toBe('119e19');
		expect(JSON.parse(chart.payload).activeTab).toBe('overview');
		expect(chart.sourceModule).toBe('mingother');
		expect(chart.chartType).toBe('cetian');

		upsertLocalCase({
			cid: 'partial-case-1',
			event: '完整事盘',
			caseType: 'huangji',
			divTime: '2026-05-23 12:34:56',
			payload: { pan: { key: 'original' } },
			sourceModule: 'huangji',
		});
		upsertLocalCase({
			cid: 'partial-case-1',
			event: '改名事盘',
		});
		const caze = listLocalCases({})[0];
		expect(caze.event).toBe('改名事盘');
		expect(caze.caseType).toBe('huangji');
		expect(caze.sourceModule).toBe('huangji');
		expect(JSON.parse(caze.payload).pan.key).toBe('original');
	});

	it('builds kentang case drawer records with source module, payload, and zero coordinates', ()=>{
		const dispatch = jest.fn();
		const makeTime = (text)=>({ format: jest.fn(()=>text) });
		openKentangCaseDrawer({
			dispatch,
			fields: {
				date: { value: makeTime('2026-05-23') },
				time: { value: makeTime('12:34:56') },
				zone: { value: '+08:00' },
				lat: { value: 0 },
				lon: { value: 0 },
				gpsLat: { value: 0 },
				gpsLon: { value: 0 },
				pos: { value: '赤道' },
			},
			module: 'taixuan',
			label: '太玄',
			payload: {
				options: { seed: 42 },
				pan: { key: 'kept' },
			},
		});
		const action = dispatch.mock.calls[0][0];
		expect(action.type).toBe('astro/openDrawer');
		const record = action.payload.record;
		expect(record.caseType).toBe('taixuan');
		expect(record.sourceModule).toBe('taixuan');
		expect(record.divTime).toBe('2026-05-23 12:34:56');
		expect(record.lat).toBe(0);
		expect(record.lon).toBe(0);
		expect(record.gpsLat).toBe(0);
		expect(record.gpsLon).toBe(0);
		expect(record.payload.options.seed).toBe(42);
		expect(record.payload.pan.key).toBe('kept');
	});
});
