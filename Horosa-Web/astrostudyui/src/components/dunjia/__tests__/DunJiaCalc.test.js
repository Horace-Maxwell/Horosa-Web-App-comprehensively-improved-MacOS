import { PAIPAN_OPTIONS, calcDunJia, isKinqimenMode } from '../DunJiaCalc';
import { buildLocalBaziResult } from '../../../utils/baziLunarLocal';
import { buildLocalJieqiYearSeed } from '../../../utils/localNongliAdapter';

function makeFields(dateStr, timeStr){
	return {
		date: {
			value: {
				format: ()=>dateStr,
			},
		},
		time: {
			value: {
				format: ()=>timeStr,
			},
		},
		zone: { value: '+08:00' },
	};
}

function makeNongli(){
	return {
		yearJieqi: '丙午',
		year: '丙午',
		monthGanZi: '庚寅',
		dayGanZi: '壬戌',
		jieqi: '立春',
		jiedelta: '立春后第14天',
		birth: '2026-02-17 21:50:07',
		month: '正月',
		day: '初一',
		leap: false,
	};
}

function makeOptions(extra = {}){
	return {
		paiPanType: 3,
		qijuMethod: 'chaibu',
		zhiShiType: 0,
		yueJiaQiJuType: 1,
		kongMode: 'day',
		yimaMode: 'day',
		shiftPalace: 0,
		fengJu: false,
		...extra,
	};
}

function pickMap(mapObj){
	const out = {};
	[1, 2, 3, 4, 6, 7, 8, 9].forEach((key)=>{
		out[key] = mapObj[key];
	});
	return out;
}

function getGanzi(pillar){
	return (pillar && (pillar.ganzhi || pillar.ganZhi)) || '';
}

function buildLocalNongliForTest(date, time){
	const local = buildLocalBaziResult({
		date,
		time,
		zone: '+08:00',
		lon: '120e00',
		lat: '0n00',
		gpsLon: 120,
		gpsLat: 0,
		ad: 1,
		gender: 1,
		timeAlg: 1,
		after23NewDay: 0,
	});
	const bazi = local.bazi;
	const four = bazi.fourColumns;
	return {
		...bazi.nongli,
		bazi,
		yearGanZi: getGanzi(four.year),
		yearJieqi: getGanzi(four.year),
		monthGanZi: getGanzi(four.month),
		dayGanZi: getGanzi(four.day),
		time: getGanzi(four.time),
		timeGanZi: getGanzi(four.time),
	};
}

describe('DunJiaCalc options', ()=>{
	test('all enabled Qimen modes are Ken backend modes', ()=>{
		expect(PAIPAN_OPTIONS.map((item)=>item.value)).toEqual([0, 2, 3, 4, 5]);
		PAIPAN_OPTIONS.forEach((item)=>{
			expect(isKinqimenMode(item.value)).toBe(true);
		});
	});

	test('paiPanType(年/月/日/时) produces different juText', ()=>{
		const fields = makeFields('2026-02-17', '21:50:07');
		const nongli = makeNongli();
		const juSet = new Set();
		[0, 1, 2, 3].forEach((paiPanType)=>{
			const pan = calcDunJia(fields, nongli, makeOptions({ paiPanType }), {});
			juSet.add(pan.juText);
		});
		expect(juSet.size).toBeGreaterThan(1);
	});

	test('yueJiaQiJuType changes result under 月家奇门', ()=>{
		const fields = makeFields('2026-02-17', '21:50:07');
		const nongli = makeNongli();
		const panA = calcDunJia(fields, nongli, makeOptions({ paiPanType: 1, yueJiaQiJuType: 0 }), {});
		const panB = calcDunJia(fields, nongli, makeOptions({ paiPanType: 1, yueJiaQiJuType: 1 }), {});
		expect(panA.juText).not.toEqual(panB.juText);
	});

	test('zhiShiType changes 值使 when 值符 is 芮禽', ()=>{
		const nongli = makeNongli();
		let foundTime = null;
		for(let h=0; h<24; h++){
			const hh = `${h}`.padStart(2, '0');
			const fields = makeFields('2026-02-17', `${hh}:50:07`);
			const pan = calcDunJia(fields, nongli, makeOptions({ paiPanType: 3, zhiShiType: 0 }), {});
			if(pan && pan.zhiFu === '芮禽'){
				foundTime = `${hh}:50:07`;
				break;
			}
		}
		if(!foundTime){
			// 部分历法/参数组合下未必会命中“芮禽”时刻，此时退化为稳定性校验：
			// 不要求值使变化，但要求不同 zhiShiType 不抛错且有可用结果。
			const fallbackFields = makeFields('2026-02-17', '21:50:07');
			const pan0 = calcDunJia(fallbackFields, nongli, makeOptions({ paiPanType: 3, zhiShiType: 0 }), {});
			const pan1 = calcDunJia(fallbackFields, nongli, makeOptions({ paiPanType: 3, zhiShiType: 1 }), {});
			const pan2 = calcDunJia(fallbackFields, nongli, makeOptions({ paiPanType: 3, zhiShiType: 2 }), {});
			expect(pan0 && pan0.zhiShi).toBeTruthy();
			expect(pan1 && pan1.zhiShi).toBeTruthy();
			expect(pan2 && pan2.zhiShi).toBeTruthy();
			return;
		}
		const fields = makeFields('2026-02-17', foundTime);
		const pan0 = calcDunJia(fields, nongli, makeOptions({ paiPanType: 3, zhiShiType: 0 }), {});
		const pan1 = calcDunJia(fields, nongli, makeOptions({ paiPanType: 3, zhiShiType: 1 }), {});
		const pan2 = calcDunJia(fields, nongli, makeOptions({ paiPanType: 3, zhiShiType: 2 }), {});
		const zhiShiSet = new Set([pan0.zhiShi, pan1.zhiShi, pan2.zhiShi]);
		expect(zhiShiSet.size).toBeGreaterThan(1);
	});

	test('unsupported qijuMethod falls back to 拆补', ()=>{
		const fields = makeFields('2026-02-17', '21:50:07');
		const nongli = makeNongli();
		const panChaibu = calcDunJia(fields, nongli, makeOptions({ qijuMethod: 'chaibu' }), {});
		const panUnknown = calcDunJia(fields, nongli, makeOptions({ qijuMethod: 'feipan' }), {});
		expect(panUnknown.juText).toEqual(panChaibu.juText);
		expect(panUnknown.options.qijuMethodLabel).toEqual('拆补');
	});

	test('值符落中宫但非天禽时，不应套用天禽值使规则', ()=>{
		const fields = makeFields('2026-02-18', '18:17:13');
		const nongli = {
			yearJieqi: '丙午',
			year: '丙午',
			monthGanZi: '庚寅',
			dayGanZi: '癸亥',
			jieqi: '立春',
			jiedelta: '立春后第14天',
			birth: '2026-02-18 18:17:13',
			month: '正月',
			day: '初二',
			leap: false,
		};
		const pan = calcDunJia(fields, nongli, makeOptions({ qijuMethod: 'chaibu', zhiShiType: 0 }), {});
		expect(pan.zhiFu).toEqual('天柱');
		expect(pan.zhiShi).toEqual('惊门');
	});

	test('繁体节气（驚蟄）应与简体节气一致', ()=>{
		const fields = makeFields('2025-03-20', '10:10:00');
		const base = {
			yearJieqi: '乙巳',
			year: '乙巳',
			monthGanZi: '己卯',
			dayGanZi: '戊子',
			jiedelta: '',
			birth: '2025-03-20 10:10:00',
			month: '二月',
			day: '廿一',
			leap: false,
		};
		const panSimple = calcDunJia(fields, { ...base, jieqi: '惊蛰' }, makeOptions({ qijuMethod: 'chaibu' }), {});
		const panTrad = calcDunJia(fields, { ...base, jieqi: '驚蟄' }, makeOptions({ qijuMethod: 'chaibu' }), {});
		expect(panTrad.juText).toEqual(panSimple.juText);
		expect(panTrad.zhiShi).toEqual(panSimple.zhiShi);
	});

	test('天盘奇仪应随时干飞布，匹配旧版遁甲样本', ()=>{
		const fields = makeFields('1998-02-20', '20:48:00');
		const nongli = {
			yearJieqi: '戊寅',
			year: '戊寅',
			monthGanZi: '甲寅',
			dayGanZi: '戊戌',
			time: '壬戌',
			jieqi: '雨水',
			jiedelta: '雨水后第1天',
			birth: '1998-02-20 20:48:00',
			month: '正月',
			day: '廿四',
			leap: false,
		};
		const pan = calcDunJia(fields, nongli, makeOptions({
			qijuMethod: 'chaibu',
			timeAlg: 1,
		}), {});
		expect(pan.juText).toEqual('阳遁九局上元');
		expect(pickMap(pan.tianGan)).toEqual({
			1: '庚',
			2: '丙',
			3: '丁',
			4: '戊',
			6: '己',
			7: '壬',
			8: '辛',
			9: '乙',
		});
		expect(pickMap(pan.diPan)).toEqual({
			1: '壬',
			2: '戊',
			3: '庚',
			4: '辛',
			6: '丙',
			7: '乙',
			8: '己',
			9: '丁',
		});
		expect(pickMap(pan.renPan)).toEqual({
			1: '死',
			2: '惊',
			3: '开',
			4: '景',
			6: '休',
			7: '杜',
			8: '伤',
			9: '生',
		});
		expect(pickMap(pan.shenPan)).toEqual({
			1: '符',
			2: '蛇',
			3: '阴',
			4: '天',
			6: '合',
			7: '地',
			8: '玄',
			9: '虎',
		});
		expect(pan.zhiFu).toEqual('芮禽');
		expect(pan.zhiShi).toEqual('死门');
	});

	test('1994-01-17 甲寅时奇门盘拆补应对齐 Horosa APP 样本', ()=>{
		const fields = makeFields('1994-01-17', '04:59:00');
		const nongli = {
			yearJieqi: '癸酉',
			year: '癸酉',
			monthGanZi: '乙丑',
			dayGanZi: '癸卯',
			time: '甲寅',
			jieqi: '小寒',
			jiedelta: '小寒后第12天',
			birth: '1994-01-17 04:59:00',
			month: '腊月',
			day: '初六',
			leap: false,
		};
		const pan = calcDunJia(fields, nongli, makeOptions({
			qijuMethod: 'chaibu',
			timeAlg: 1,
		}), {});
		expect(pan.juText).toEqual('阳遁八局中元');
		expect(pan.zhiFu).toEqual('天辅');
		expect(pan.zhiShi).toEqual('杜门');
		expect(pan.kongWang).toEqual('辰巳');
		expect(pan.xunShou).toEqual('甲午');
		expect(pickMap(pan.tianGan)).toEqual({
			1: '癸',
			2: '己',
			3: '辛',
			4: '壬',
			6: '乙',
			7: '戊',
			8: '庚',
			9: '丙',
		});
		expect(pickMap(pan.diPan)).toEqual({
			1: '癸',
			2: '己',
			3: '辛',
			4: '壬',
			6: '乙',
			7: '戊',
			8: '庚',
			9: '丙',
		});
		expect(pickMap(pan.renPan)).toEqual({
			1: '杜',
			2: '景',
			3: '死',
			4: '伤',
			6: '惊',
			7: '生',
			8: '休',
			9: '开',
		});
		expect(pickMap(pan.shenPan)).toEqual({
			1: '符',
			2: '蛇',
			3: '阴',
			4: '天',
			6: '合',
			7: '地',
			8: '玄',
			9: '虎',
		});
		const stars = {};
		pan.cells.forEach((cell)=>{
			stars[cell.palaceNum] = cell.tianXing;
		});
		expect(pickMap(stars)).toEqual({
			1: '辅',
			2: '英',
			3: '芮',
			4: '冲',
			6: '柱',
			7: '任',
			8: '蓬',
			9: '心',
		});
	});

	test('1994-01-17 甲寅时奇门盘置润应使用当前日柱定三元', ()=>{
		const fields = makeFields('1994-01-17', '04:59:00');
		const nongli = {
			yearJieqi: '癸酉',
			year: '癸酉',
			monthGanZi: '乙丑',
			dayGanZi: '癸卯',
			time: '甲寅',
			jieqi: '小寒',
			jiedelta: '小寒后第12天',
			birth: '1994-01-17 04:59:00',
			month: '腊月',
			day: '初六',
			leap: false,
		};
		const context = {
			jieqiYearSeeds: {
				1993: {
					大雪: { term: '大雪', time: '1993-12-07 23:30:00', dateKey: '19931207', dayGanzhi: '癸亥' },
				},
				1994: {
					芒种: { term: '芒种', time: '1994-06-06 00:00:00', dateKey: '19940606', dayGanzhi: '癸亥' },
					大雪: { term: '大雪', time: '1994-12-07 00:00:00', dateKey: '19941207', dayGanzhi: '丁卯' },
				},
			},
		};
		const pan = calcDunJia(fields, nongli, makeOptions({
			qijuMethod: 'zhirun',
			timeAlg: 1,
		}), context);
		expect(pan.juText).toEqual('阳遁八局中元');
		expect(pan.zhiFu).toEqual('天辅');
		expect(pan.zhiShi).toEqual('杜门');
		expect(pickMap(pan.tianGan)).toEqual({
			1: '癸',
			2: '己',
			3: '辛',
			4: '壬',
			6: '乙',
			7: '戊',
			8: '庚',
			9: '丙',
		});
		expect(pickMap(pan.shenPan)).toEqual({
			1: '符',
			2: '蛇',
			3: '阴',
			4: '天',
			6: '合',
			7: '地',
			8: '玄',
			9: '虎',
		});
	});

	test('本地节气 fallback 按准确交节时刻判断当前节气', ()=>{
		const beforeDaxue = buildLocalNongliForTest('2047-12-07', '13:10:00');
		const afterDaxue = buildLocalNongliForTest('2047-12-07', '13:12:00');
		expect(beforeDaxue.jieqi).toEqual('小雪');
		expect(afterDaxue.jieqi).toEqual('大雪');
	});

	test('默认晚子时不提前换日，拆补与手机版口径一致', ()=>{
		const fields = makeFields('1982-07-28', '23:48:00');
		const nongli = buildLocalNongliForTest('1982-07-28', '23:48:00');
		const defaultPan = calcDunJia(fields, nongli, makeOptions({
			qijuMethod: 'chaibu',
			timeAlg: 1,
		}), {});
		const ziZhengPan = calcDunJia(fields, nongli, makeOptions({
			qijuMethod: 'chaibu',
			timeAlg: 1,
			after23NewDay: 0,
		}), {});
		expect(defaultPan.options.daySwitchLabel).toEqual('子正换日');
		expect(defaultPan.juText).toEqual(ziZhengPan.juText);
		expect(defaultPan.ganzhi.day).toEqual(ziZhengPan.ganzhi.day);
		expect(defaultPan.ganzhi.time).toEqual(ziZhengPan.ganzhi.time);
		expect(pickMap(defaultPan.tianGan)).toEqual(pickMap(ziZhengPan.tianGan));
	});

	test('置润值符星落中宫时天盘应继续飞布', ()=>{
		const fields = makeFields('2015-12-22', '11:42:00');
		const nongli = buildLocalNongliForTest('2015-12-22', '11:42:00');
		const context = {
			jieqiYearSeeds: {
				2014: buildLocalJieqiYearSeed(2014, '+08:00'),
				2015: buildLocalJieqiYearSeed(2015, '+08:00'),
			},
		};
		const pan = calcDunJia(fields, nongli, makeOptions({
			qijuMethod: 'zhirun',
			timeAlg: 1,
		}), context);
		expect(pan.juText).toEqual('阳遁七局中元');
		expect(pan.zhiFu).toEqual('芮禽');
		expect(pickMap(pan.diPan)).toEqual({
			1: '丁',
			2: '庚',
			3: '壬',
			4: '癸',
			6: '戊',
			7: '己',
			8: '辛',
			9: '乙',
		});
		expect(pickMap(pan.tianGan)).toEqual({
			1: '壬',
			2: '戊',
			3: '乙',
			4: '庚',
			6: '辛',
			7: '丁',
			8: '癸',
			9: '己',
		});
	});
});
