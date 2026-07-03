// astrodataIntegration.test.js —— 名人星盘数据库「工具·数据库」页集成哨兵。
// 覆盖两条集成关键路径:
//   ① 「加入命盘」数据路径:iframe 送来的 chart(birth 为字符串)经 buildLocalChartRecord/upsertLocalChart
//      必须落库不抛(修 addChart 假定 birth 为 moment 的隐藏 bug);
//   ② AstrodataPage.onMsg 接线:仅对本页 iframe 的 astrodata:importChart 消息 dispatch(user/addLocalChartQuiet),
//      忽略无关类型与伪造来源。
import AstrodataPage from '../AstrodataPage';
import { buildLocalChartRecord, upsertLocalChart } from '../../../utils/localcharts';

describe('数据库导入命盘 · 字符串 birth 数据路径', () => {
	// 名人库详情 postMessage 的 chart:birth 是 "YYYY-MM-DD HH:mm:ss" 字符串、group 为数组。
	const adbChart = {
		cid: 'adb-12345', name: 'Albert Einstein', birth: '1879-03-14 11:30:00',
		zone: '+00:39', lat: '48n24', lon: '9e59', gpsLat: 48.4, gpsLon: 9.983,
		pos: 'Ulm, Germany', gender: 1, isPub: 0, doubingSu28: 0,
		group: ['Astrodatabank', 'AA'], creator: 'local',
	};

	test('buildLocalChartRecord 容忍字符串 birth,原样保留、不抛', () => {
		const rec = buildLocalChartRecord(adbChart);
		expect(rec.birth).toBe('1879-03-14 11:30:00');   // 字符串未被当作 moment 调用 .format
		expect(rec.name).toBe('Albert Einstein');
		expect(rec.cid).toBe('adb-12345');
		expect(rec.gender).toBe(1);
		// group 落库为 JSON 字符串(normalizeGroup 约定),读回时解析。
		expect(typeof rec.group).toBe('string');
		expect(rec.group).toContain('Astrodatabank');
		expect(rec.group).toContain('AA');
	});

	test('gender 字符串归一为整数', () => {
		expect(buildLocalChartRecord({ ...adbChart, gender: '0' }).gender).toBe(0);
		expect(buildLocalChartRecord({ ...adbChart, gender: '-1' }).gender).toBe(-1);
	});

	test('upsertLocalChart 端到端落库 + 读回(字符串 birth 全程不抛)', () => {
		try { localStorage.clear(); } catch (e) { /* jsdom localStorage */ }
		const rec = upsertLocalChart(adbChart);
		expect(rec.birth).toBe('1879-03-14 11:30:00');
		expect(rec.cid).toBe('adb-12345');
		// 同 cid 重复导入 = upsert(不重复入库)
		const rec2 = upsertLocalChart({ ...adbChart, name: 'Einstein (dup)' });
		expect(rec2.cid).toBe('adb-12345');
	});
});

describe('AstrodataPage.onMsg 接线', () => {
	function makeInst() {
		const calls = [];
		const inst = new AstrodataPage({ dispatch: (a) => calls.push(a) });
		return { inst, calls };
	}
	const chart = { cid: 'adb-1', name: 'X', birth: '1990-01-01 12:00:00', group: ['Astrodatabank', 'A'] };

	test('合法 astrodata:importChart 消息 → dispatch(user/addLocalChartQuiet)', () => {
		const { inst, calls } = makeInst();
		inst.onMsg({ data: { type: 'astrodata:importChart', chart }, source: null });
		expect(calls.length).toBe(1);
		expect(calls[0].type).toBe('user/addLocalChartQuiet');
		expect(calls[0].payload).toBe(chart);
	});

	test('无关类型 / 空数据 → 不 dispatch', () => {
		const { inst, calls } = makeInst();
		inst.onMsg({ data: { type: 'something-else', chart }, source: null });
		inst.onMsg({ data: null, source: null });
		inst.onMsg({ data: { type: 'astrodata:importChart' }, source: null });   // 缺 chart
		expect(calls.length).toBe(0);
	});

	test('伪造来源窗口 → 拒收;本页 iframe 来源 → 接收', () => {
		const { inst, calls } = makeInst();
		const frameWin = {};
		inst.iframeRef = { current: { contentWindow: frameWin } };
		inst.onMsg({ data: { type: 'astrodata:importChart', chart }, source: {} });   // 别的窗口
		expect(calls.length).toBe(0);
		inst.onMsg({ data: { type: 'astrodata:importChart', chart }, source: frameWin }); // 本页 iframe
		expect(calls.length).toBe(1);
	});
});
