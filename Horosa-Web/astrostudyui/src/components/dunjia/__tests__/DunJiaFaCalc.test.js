import {
	computeDangers,
	computeWuHe,
	computePanType,
	buildJieHua,
	computeProtect,
	computeYongShen,
	computeWealth,
	computeGuGua,
	computeCareer,
	computeRomance,
	buildFaQimenAnalysis,
	OPPOSITE_PALACE,
	POS_GUA,
	POS_DIRECTION,
} from '../DunJiaFaCalc';

// 🔴 对宫金标(非自洽·按后天八卦方位断)：巽东南↔乾西北、离南↔坎北、坤西南↔艮东北、震东↔兑西。
// 用户报障:旧 {1:6} 把巽(东南)误对兑(正西);此测用「方位 180° 对冲」独立验证,防再错。
describe('OPPOSITE_PALACE 后天八卦方位对宫(金标·方位判)', ()=>{
	const DIR_OPPOSITE = {
		东南: '西北', 西北: '东南', 正南: '正北', 正北: '正南',
		西南: '东北', 东北: '西南', 正东: '正西', 正西: '正东',
	};
	test('每宫对宫方位 = 本宫方位的 180° 反向(逐宫)', ()=>{
		[1, 2, 3, 4, 6, 7, 8, 9].forEach((p)=>{
			const opp = OPPOSITE_PALACE[p];
			expect(POS_DIRECTION[opp]).toBe(DIR_OPPOSITE[POS_DIRECTION[p]]);
		});
	});
	test('关键对:巽1↔乾9(东南↔西北)、震4↔兑6(正东↔正西)、坤3↔艮7(西南↔东北)、离2↔坎8', ()=>{
		expect(OPPOSITE_PALACE[1]).toBe(9);
		expect(POS_GUA[OPPOSITE_PALACE[1]]).toBe('乾');
		expect(POS_DIRECTION[OPPOSITE_PALACE[1]]).toBe('西北');
		expect(OPPOSITE_PALACE[4]).toBe(6);
		expect(OPPOSITE_PALACE[3]).toBe(7);
		expect(OPPOSITE_PALACE[2]).toBe(8);
	});
	test('对宫为对合(involution)且 = 10 − 宫号,中5无对宫', ()=>{
		[1, 2, 3, 4, 6, 7, 8, 9].forEach((p)=>{
			expect(OPPOSITE_PALACE[p]).toBe(10 - p);
			expect(OPPOSITE_PALACE[OPPOSITE_PALACE[p]]).toBe(p);
		});
		expect(OPPOSITE_PALACE[5]).toBeUndefined();
	});
});

// 极简 cell 工厂：只填本引擎消费的字段。
function cell(palaceNum, tianGan, diGan, god, door, tianXing){
	return { palaceNum, palaceName: '', tianGan: tianGan || '', diGan: diGan || '', god: god || '', door: door || '', tianXing: tianXing || '' };
}
function mkPan(over){
	return Object.assign(
		{
			cells: [],
			tianPan: {},
			diPan: {},
			jiXingPalaces: [],
			ruMuPalaces: [],
			menPo: { list: [], palaces: [] },
			kongWangPalaces: [],
			zhiFuPalace: 0,
		},
		over,
	);
}

describe('DunJiaFaCalc · computeDangers（六害完整 + 危害排序）', ()=>{
	// 击刑(震4·戊) / 入墓(巽1·辛) / 庚(乾9) / 白虎(兑6·神虎) / 门迫(离2·休) / 空亡(坎8)
	const pan = mkPan({
		cells: [
			cell(4, '戊', '', '合', '伤', '冲'),
			cell(1, '辛', '', '蛇', '杜', '辅'),
			cell(9, '庚', '', '天', '开', '心'),
			cell(6, '丁', '', '虎', '惊', '柱'),
			cell(2, '丙', '', '阴', '休', '英'),
			cell(8, '壬', '', '玄', '生', '蓬'),
		],
		jiXingPalaces: [4],
		ruMuPalaces: [1],
		menPo: { palaces: [2], list: [] },
		kongWangPalaces: [8],
	});

	it('六类危害按 击刑>入墓>庚>白虎>门迫>空亡 排序', ()=>{
		const d = computeDangers(pan);
		expect(d.map((x)=>x.type)).toEqual(['击刑', '入墓', '庚', '白虎', '门迫', '空亡']);
	});

	it('庚（天盘干）与白虎（八神）被正确检测并定位', ()=>{
		const d = computeDangers(pan);
		const geng = d.find((x)=>x.type === '庚');
		const hu = d.find((x)=>x.type === '白虎');
		expect(geng.palaceNum).toBe(9);
		expect(geng.symbol).toBe('庚');
		expect(hu.palaceNum).toBe(6);
		expect(hu.symbol).toBe('白虎');
	});

	it('击刑取该宫天盘干与正确方位', ()=>{
		const d = computeDangers(pan);
		expect(d[0].symbol).toBe('戊');
		expect(d[0].palaceName).toBe('震');
		expect(d[0].direction).toBe('正东');
		const menpo = d.find((x)=>x.type === '门迫');
		expect(menpo.symbol).toBe('休');
	});

	it('阳遁神「勾」归一为白虎', ()=>{
		const p = mkPan({ cells: [cell(6, '丁', '', '勾', '惊', '柱')] });
		const d = computeDangers(p);
		expect(d.some((x)=>x.type === '白虎' && x.palaceNum === 6)).toBe(true);
	});

	it('空盘无六害', ()=>{
		expect(computeDangers(mkPan({}))).toEqual([]);
	});
});

describe('DunJiaFaCalc · computeWuHe（天干五合）', ()=>{
	it('甲取值符宫定位；天地盘五合宫被识别', ()=>{
		const pan = mkPan({
			zhiFuPalace: 3,
			cells: [
				cell(7, '己', '', '', '', ''), // 己在艮7
				cell(1, '丁', '壬', '', '', ''), // 丁壬同宫 → 天地合
			],
		});
		const { pairs, tianDiHe } = computeWuHe(pan);
		const jiaJi = pairs.find((x)=>x.ganA === '甲' && x.ganB === '己');
		expect(jiaJi.palaceA).toBe(3); // 甲＝值符宫
		expect(jiaJi.palaceB).toBe(7); // 己＝艮7
		expect(jiaJi.hiddenJia).toBe(true);
		expect(tianDiHe).toHaveLength(1);
		expect(tianDiHe[0].palaceNum).toBe(1);
		expect(tianDiHe[0].tianGan).toBe('丁');
		expect(tianDiHe[0].diGan).toBe('壬');
	});
});

describe('DunJiaFaCalc · computePanType（伏吟/反吟）', ()=>{
	const base = { 1: '戊', 2: '己', 3: '庚', 4: '辛', 6: '壬', 7: '癸', 8: '丁', 9: '丙' };

	it('天地盘干逐宫相同 → 伏吟', ()=>{
		const pan = mkPan({ tianPan: { ...base }, diPan: { ...base } });
		expect(computePanType(pan).type).toBe('伏吟');
	});

	it('天盘干 ≡ 对宫地盘干 → 反吟', ()=>{
		const di = {};
		Object.keys(base).forEach((p)=>{
			di[OPPOSITE_PALACE[p]] = base[p];
		});
		const pan = mkPan({ tianPan: { ...base }, diPan: di });
		expect(computePanType(pan).type).toBe('反吟');
	});

	it('普通局既非伏吟也非反吟', ()=>{
		const di = { 1: '甲', 2: '乙', 3: '丙', 4: '丁', 6: '戊', 7: '己', 8: '庚', 9: '辛' };
		expect(computePanType(mkPan({ tianPan: { ...base }, diPan: di })).type).toBeNull();
	});
});

describe('DunJiaFaCalc · buildJieHua（逐宫合并化解）', ()=>{
	it('庚击刑同宫 → 灭庚象 + 高乙 + 低巳（乙去重一次）', ()=>{
		const pan = mkPan({
			cells: [cell(7, '庚', '', '天', '开', '心')],
			jiXingPalaces: [7], // 庚在艮7击刑
		});
		const gen = buildJieHua(pan).find((c)=>c.palaceNum === 7);
		expect(gen.dangers.map((d)=>d.type).sort()).toEqual(['击刑', '庚'].sort());
		expect(gen.mie.join()).toContain('庚');
		const high = gen.placements.filter((p)=>p.where.indexOf('高处') >= 0).map((p)=>p.text).join();
		const low = gen.placements.filter((p)=>p.where.indexOf('低处') >= 0).map((p)=>p.text).join();
		expect(high).toContain('乙');
		expect(low).toContain('巳');
		expect(gen.placements.filter((p)=>p.text.indexOf('「乙」') >= 0).length).toBe(1);
	});

	it('庚单独（非击刑）→ 只用乙、无巳', ()=>{
		const pan = mkPan({ cells: [cell(9, '庚', '', '天', '开', '心')] });
		const gen = buildJieHua(pan).find((c)=>c.palaceNum === 9);
		expect(gen.dangers.map((d)=>d.type)).toEqual(['庚']);
		const txt = gen.placements.map((p)=>p.text).join();
		expect(txt).toContain('乙');
		expect(txt).not.toContain('巳');
	});

	it('入墓 → 对宫冲墓、只可移', ()=>{
		const pan = mkPan({ cells: [cell(1, '辛', '', '蛇', '杜', '辅')], ruMuPalaces: [1] });
		const c = buildJieHua(pan).find((x)=>x.palaceNum === 1);
		expect(c.mie.join()).toContain('只可移');
		const dui = c.placements.find((p)=>p.where.indexOf('对宫') >= 0);
		expect(dui.text).toContain('戌'); // 辛入辰墓、辰冲戌
	});

	it('按宫严重度排序 + 一字标记', ()=>{
		const pan = mkPan({
			cells: [cell(4, '戊', '', '合', '伤', '冲'), cell(8, '壬', '', '玄', '生', '蓬')],
			jiXingPalaces: [4],
			kongWangPalaces: [8],
		});
		const cards = buildJieHua(pan);
		expect(cards[0].palaceNum).toBe(4); // 击刑(6) 排在 空亡(1) 前
		expect(cards[0].dangers[0].oneChar).toBe('刑');
	});
});

describe('DunJiaFaCalc · computeProtect（八门化气大阵保护清单）', ()=>{
	it('日干/时干/意象/符使均定位；生年干随相关人员逐人显示（未选则不出该行）', ()=>{
		const pan = mkPan({
			ganzhi: { year: '甲子', month: '丙寅', day: '戊午', time: '辛丑' },
			zhiFuPalace: 9,
			zhiShiPalace: 2,
			jiXingPalaces: [4],
			cells: [
				cell(4, '戊', '', '合', '伤', '冲'),
				cell(1, '辛', '', '蛇', '杜', '辅'),
				cell(9, '庚', '', '天', '开', '心'),
				cell(2, '丙', '', '阴', '休', '英'),
			],
		});
		const rows = computeProtect(pan, { topic: 'wealth' });
		const day = rows.find((r)=>r.label.indexOf('日干') >= 0);
		expect(day.gan).toBe('戊');
		expect(day.palaceNum).toBe(4);
		expect(day.hazards).toContain('击刑');
		expect(day.ok).toBe(false);
		// 未选相关人员 → 不出「生年干」行（占位「示本盘年干」已移除）。
		expect(rows.some((r)=>r.label.indexOf('生年') >= 0)).toBe(false);
		expect(rows.some((r)=>r.label.indexOf('值符') >= 0)).toBe(true);
		expect(rows.some((r)=>r.label.indexOf('意象') >= 0)).toBe(true);
		// 选入相关人员（生年干甲）→ 逐人一行（标姓名），定位到甲所在的值符宫(9)。
		pan.faRelatedPeople = [{ cid: 'c1', name: '张三', yearGan: '甲' }];
		const rows2 = computeProtect(pan, { topic: 'wealth' });
		const year = rows2.find((r)=>r.label.indexOf('生年') >= 0);
		expect(year).toBeTruthy();
		expect(year.gan).toBe('甲');
		expect(year.palaceNum).toBe(9); // 甲＝值符宫
		expect(year.label.indexOf('张三') >= 0).toBe(true);
	});
});

describe('DunJiaFaCalc · 用神/分论（P3）', ()=>{
	function richPan(over){
		return mkPan(Object.assign({
			ganzhi: { year: '甲子', month: '丙寅', day: '戊午', time: '辛丑' },
			zhiFuPalace: 9,
			zhiShiPalace: 2,
			cells: [
				cell(4, '戊', '', '合', '生', '冲'),
				cell(1, '辛', '', '蛇', '杜', '辅'),
				cell(9, '庚', '', '虎', '开', '心'),
				cell(2, '丙', '', '阴', '景', '英'),
				cell(6, '壬', '', '玄', '惊', '柱'),
			],
		}, over));
	}
	it('用神＝日干并定位', ()=>{
		const ys = computeYongShen(richPan({}), { faceToFace: true });
		expect(ys.dayGan.symbol).toBe('戊');
		expect(ys.dayGan.palaceNum).toBe(4);
		expect(ys.yongShenText).toContain('用神＝日干');
	});
	it('财富七要定位戊/生门/六合/时干 + 月令关系', ()=>{
		const w = computeWealth(richPan({}));
		const wu = w.items.find((x)=>x.name.indexOf('戊') >= 0);
		const sheng = w.items.find((x)=>x.name.indexOf('生门') >= 0);
		expect(wu.palaceNum).toBe(4);
		expect(sheng.palaceNum).toBe(4);
		expect(w.month.zhi).toBe('寅');
		expect(w.month.relation).toContain('月令');
	});
	it('解孤辰寡宿读神煞并给六合解法', ()=>{
		const pan = richPan({ shenSha: { allItems: [{ name: '孤辰', value: '寅', group: '年支' }] } });
		const g = computeGuGua(pan);
		expect(g[0].name).toBe('孤辰');
		expect(g[0].jie).toContain('亥'); // 寅六合亥
	});
});

describe('DunJiaFaCalc · buildFaQimenAnalysis（总入口）', ()=>{
	it('pan 为空返回 null；正常返回全部分段', ()=>{
		expect(buildFaQimenAnalysis(null)).toBeNull();
		const a = buildFaQimenAnalysis(mkPan({}), { askTopic: 'wealth' });
		['dangers', 'wuHe', 'panType', 'jieHua', 'protect', 'yongShen', 'wealth', 'career', 'romance', 'guGua'].forEach((k)=>{
			expect(a).toHaveProperty(k);
		});
		expect(a.ctx).toEqual({ askTopic: 'wealth' });
	});
});

describe('DunJiaFaCalc · 化解去说明 + 生肖替代 + 用神完整（本轮）', ()=>{
	it('placements 不含 五合/冲开/柔化 等进阶说明', ()=>{
		const pan = mkPan({ cells: [cell(7, '庚', '', '天', '开', '心'), cell(1, '辛', '', '蛇', '杜', '辅')], jiXingPalaces: [7], ruMuPalaces: [1] });
		const txt = JSON.stringify(buildJieHua(pan));
		expect(txt).not.toContain('五合');
		expect(txt).not.toContain('冲开');
		expect(txt).not.toContain('柔化');
	});
	it('placement 用龙/蛇/虎(辰/巳/寅)时给替代脚注', ()=>{
		const pan = mkPan({ cells: [cell(7, '庚', '', '天', '开', '心')], jiXingPalaces: [7] });
		const c = buildJieHua(pan).find((x)=>x.palaceNum === 7);
		expect(c.notes.join()).toContain('把握不住');
		expect(c.notes.join()).toContain('红烛代蛇');
	});
	it('事业七要含行业取象；恋爱含斩桃花', ()=>{
		const pan = mkPan({ ganzhi: { year: '甲子', month: '丙寅', day: '戊午', time: '辛丑' }, zhiFuPalace: 9, zhiShiPalace: 2, cells: [cell(4, '戊', '', '合', '生', '冲')] });
		expect(computeCareer(pan).industryHint).toContain('行业取象');
		expect(computeRomance(pan).zhanTaoHua).toContain('斩桃花');
	});
});

// 🔴 WP-A 金标:用神/保护 值符·值使落宫以「盘面 cells」为单一真值(与盘面八神/八门同源),
// 不用派生字段 pan.zhiFuPalace(GUA_POS_MAP+移星旋转 另算,移星档下会与盘面漂移)。防再对不上盘面。
describe('WP-A 值符/值使落宫 = 盘面 cells(非漂移 pan.zhiFuPalace)', ()=>{
	test('用神值符宫 = 八神「符」所在宫(即使 pan.zhiFuPalace 指向别宫)', ()=>{
		const pan = mkPan({
			ganzhi: { day: '丙寅', time: '庚子' },
			zhiFuPalace: 9,   // 漂移的派生值
			cells: [cell(1, '丙', '戊', '符', '开', '蓬'), cell(9, '庚', '乙', '虎', '惊', '心')],
		});
		expect(computeYongShen(pan).zhiFu.palaceNum).toBe(1);   // 以盘面「符」宫(1)为准,非 9
	});
	test('用神值使宫 = 值使门(pan.zhiShi「死门」)所在宫', ()=>{
		const pan = mkPan({
			ganzhi: { day: '丙寅', time: '庚子' },
			zhiShi: '死门', zhiShiPalace: 3,   // 漂移
			cells: [cell(1, '丙', '戊', '符', '开', '蓬'), cell(6, '庚', '乙', '虎', '死', '柱')],
		});
		expect(computeYongShen(pan).zhiShi.palaceNum).toBe(6);   // 死门在 6 宫,非 3
	});
	test('保护清单值符/值使宫同随盘面(computeProtect)', ()=>{
		const pan = mkPan({
			ganzhi: { day: '丙寅', time: '庚子' },
			zhiFuPalace: 9, zhiShi: '死门', zhiShiPalace: 3,
			cells: [cell(1, '丙', '戊', '符', '开', '蓬'), cell(6, '庚', '乙', '虎', '死', '柱')],
		});
		const prot = computeProtect(pan);
		expect((prot.find((r)=>`${r.label}`.indexOf('值符') >= 0) || {}).palaceNum).toBe(1);
		expect((prot.find((r)=>`${r.label}`.indexOf('值使') >= 0) || {}).palaceNum).toBe(6);
	});
	test('无「符」cell 时兜底 pan.zhiFuPalace(向后兼容零回归)', ()=>{
		const pan = mkPan({ ganzhi: { day: '丙寅', time: '庚子' }, zhiFuPalace: 7, cells: [cell(4, '戊', '', '合', '生', '冲')] });
		expect(computeYongShen(pan).zhiFu.palaceNum).toBe(7);
	});
});

// 🔴 WP-C 命局/事局 日时干语义:命盘 日=内心·时=外在;事盘 日=实质·时=表象。ctx.chartCategory 驱动。
describe('WP-C 命局/事局 日时干语义标注', ()=>{
	const base = { ganzhi: { day: '丙寅', time: '庚子' }, cells: [cell(1, '丙', '戊', '符', '开', '蓬')] };
	test('事盘:日干=实质、时干=表象', ()=>{
		const ys = computeYongShen(mkPan(base), { chartCategory: 'shi' });
		expect(ys.dayRole).toBe('实质');
		expect(ys.timeRole).toBe('表象');
		expect(ys.isMing).toBe(false);
	});
	test('命盘:日干=内心、时干=外在', ()=>{
		const ys = computeYongShen(mkPan(base), { chartCategory: 'ming' });
		expect(ys.dayRole).toBe('内心');
		expect(ys.timeRole).toBe('外在');
		expect(ys.isMing).toBe(true);
	});
	test('computeProtect 日/时干标签随盘类切换', ()=>{
		const ming = computeProtect(mkPan(base), { chartCategory: 'ming' });
		expect(ming.some((r)=>r.label === '日干·内心')).toBe(true);
		expect(ming.some((r)=>r.label === '时干·外在')).toBe(true);
		const shi = computeProtect(mkPan(base), { chartCategory: 'shi' });
		expect(shi.some((r)=>r.label === '日干·实质')).toBe(true);
		expect(shi.some((r)=>r.label === '时干·表象')).toBe(true);
	});
	test('缺 ctx/盘类 → 默认事盘(实质/表象)', ()=>{
		expect(computeYongShen(mkPan(base)).dayRole).toBe('实质');
	});
});
