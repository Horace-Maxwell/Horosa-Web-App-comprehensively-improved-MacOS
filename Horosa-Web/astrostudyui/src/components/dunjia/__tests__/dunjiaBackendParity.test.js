// 前端↔后端 时家定局平价锚(2026-07-04 定局修复同步保证,2026-07-04):
// 奇门时家生产走后端 vendor(kinqimen);前端本地 calcDunJia 是 dunjia 页与三式合一的
// 回退层(getCachedDunJia/后端不可达)。后端修复拆补「14 天日差交节日两档回退」与
// 置闰「晚子时不进位」后,本测试把两层钉在同一真值上(锚值取自修后 42,731 点全矩阵
// 扫描,与用户参考引擎 0 差)——任何一层将来漂移即红。
import { calcDunJia } from '../DunJiaCalc';
import { buildLocalBaziResult } from '../../../utils/baziLunarLocal';
import { buildLocalJieqiYearSeed } from '../../../utils/localNongliAdapter';

function nongliOf(date, time){
	const local = buildLocalBaziResult({ date, time, zone: '+08:00', lon: '120e00', lat: '0n00', gpsLon: 120, gpsLat: 0, ad: 1, gender: 1, timeAlg: 1, after23NewDay: 1 });
	return { ...local.bazi.nongli, bazi: local.bazi };
}
function juOf(date, time, method){
	const fields = { date: { value: { format: () => date } }, time: { value: { format: () => time } }, zone: { value: '+08:00' } };
	const y = parseInt(date.slice(0, 4), 10);
	const ctx = { jieqiYearSeeds: {
		[y - 1]: buildLocalJieqiYearSeed(y - 1, '+08:00'),
		[y]: buildLocalJieqiYearSeed(y, '+08:00'),
		[y + 1]: buildLocalJieqiYearSeed(y + 1, '+08:00'),
	} };
	const p = calcDunJia(fields, nongliOf(date, time), { paiPanType: 3, qijuMethod: method, school: '转盘', timeAlg: 1, after23NewDay: 1 }, ctx);
	return p.juText;
}

it('Bug1锚:2026-02-18 10:30 拆补=阳遁二局下元(立春,绝非大寒阳六)', () => {
	expect(juOf('2026-02-18', '10:30:00', 'chaibu')).toEqual('阳遁二局下元');
});
it('至界时刻感知:2015-12-22 拆补 10:30(冬至12:48前)=阴遁七局中元 / 14:30(后)=阳遁七局中元', () => {
	expect(juOf('2015-12-22', '10:30:00', 'chaibu')).toEqual('阴遁七局中元');
	expect(juOf('2015-12-22', '14:30:00', 'chaibu')).toEqual('阳遁七局中元');
});
it('Bug2锚:2015-01-02 23:30 置闰(晚子时)=阳遁二局上元,与次日 00:30 连续', () => {
	expect(juOf('2015-01-02', '23:30:00', 'zhirun')).toEqual('阳遁二局上元');
	expect(juOf('2015-01-03', '00:30:00', 'zhirun')).toEqual('阳遁二局上元');
});
it('置闰常规锚:2015-12-22 12:30=阳遁七局中元(超神已入冬至)', () => {
	expect(juOf('2015-12-22', '12:30:00', 'zhirun')).toEqual('阳遁七局中元');
});
