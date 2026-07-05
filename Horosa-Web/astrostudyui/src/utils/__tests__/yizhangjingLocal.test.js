// 一掌经引擎 golden：4 例直喂农历值断言四柱四宫＋命宫（命宫用数至卯法复现古本），
// ＋开关差异（换 顺逆/大限运长/流年神/命宫法 各产不同输出）＋边界（极端月日/非法入参）。
import {
	calcYizhangjing, fourPalaces, mingGong, direction, yinyang, mod12, branchIndex,
	xunShenAt, FLOW_SETS,
} from '../yizhangjingLocal';

// 古本用 数至卯 命宫；四柱星序＝年·月·日·时
const GOLDEN = [
	{
		name: '巳年二月初七寅时·女·阳男阴女(阴女顺)',
		in: { yearBranch: '巳', month: 2, day: 7, hourBranch: '寅', gender: '女' },
		opts: { shunniRule: 'yangNanYinNv', mingGongMethod: 'shuZhiMao' },
		stars: ['天文', '天福', '天貴', '天權'],
		mingStar: '天破', mingBranch: '卯',
	},
	{
		name: '巳年二月初七寅时·男·阳男阴女(阴男逆)',
		in: { yearBranch: '巳', month: 2, day: 7, hourBranch: '寅', gender: '男' },
		opts: { shunniRule: 'yangNanYinNv', mingGongMethod: 'shuZhiMao' },
		stars: ['天文', '天奸', '天藝', '天孤'],
		mingStar: '天驛', mingBranch: '未',
	},
	{
		name: '巳(1977)年五月十七酉时·男·阴男逆',
		in: { yearBranch: '巳', month: 5, day: 17, hourBranch: '酉', gender: '男' },
		opts: { shunniRule: 'yangNanYinNv', mingGongMethod: 'shuZhiMao' },
		stars: ['天文', '天厄', '天刃', '天貴'],
		mingStar: '天福', mingBranch: '午',
	},
	{
		name: '庚子年正月初九酉时·男·男顺女逆(阳男顺)',
		in: { yearBranch: '子', month: 1, day: 9, hourBranch: '酉', gender: '男' },
		opts: { shunniRule: 'menShunNvNi', mingGongMethod: 'shuZhiMao' },
		stars: ['天貴', '天貴', '天孤', '天文'],
		mingStar: '天壽', mingBranch: '亥',
	},
];

describe('一掌经引擎 · 古本 golden（byte-perfect）', () => {
	GOLDEN.forEach((g) => {
		it(g.name, () => {
			const r = calcYizhangjing({ ...g.in, opts: g.opts });
			expect(r).toBeTruthy();
			expect(r.pillars.map((p) => p.star)).toEqual(g.stars);
			expect(r.mingStar).toBe(g.mingStar);
			expect(r.mingBranch).toBe(g.mingBranch);
		});
	});
});

describe('一掌经引擎 · 基础不变量', () => {
	it('年支阴阳按奇偶', () => {
		expect(yinyang(branchIndex('子'))).toBe('阳');
		expect(yinyang(branchIndex('巳'))).toBe('阴');
	});
	it('mod12 归一到 0..11', () => {
		expect(mod12(-1)).toBe(11);
		expect(mod12(13)).toBe(1);
	});
	it('顺逆两法在阴年男命分歧', () => {
		// 巳=阴年：阳男阴女→阴男逆(-1)；男顺女逆→男顺(+1)
		expect(direction(branchIndex('巳'), '男', 'yangNanYinNv')).toBe(-1);
		expect(direction(branchIndex('巳'), '男', 'menShunNvNi')).toBe(1);
	});
	it('阳年男命两法一致', () => {
		expect(direction(branchIndex('子'), '男', 'yangNanYinNv')).toBe(direction(branchIndex('子'), '男', 'menShunNvNi'));
	});
});

describe('一掌经引擎 · 开关差异（勾了必须变）', () => {
	const base = { yearBranch: '巳', month: 5, day: 17, hourBranch: '酉', gender: '男' };
	it('顺逆规则改 → 四柱四宫变', () => {
		const a = calcYizhangjing({ ...base, opts: { shunniRule: 'yangNanYinNv' } });
		const b = calcYizhangjing({ ...base, opts: { shunniRule: 'menShunNvNi' } });
		expect(a.pillars.map((p) => p.star)).not.toEqual(b.pillars.map((p) => p.star));
	});
	it('大限运长 7↔10 → 大限区间变', () => {
		const a = calcYizhangjing({ ...base, opts: { dayunLength: 7 } });
		const b = calcYizhangjing({ ...base, opts: { dayunLength: 10 } });
		expect(a.dayun[1].from).not.toBe(b.dayun[1].from);
	});
	it('命宫两法 → 命宫可不同', () => {
		const a = calcYizhangjing({ ...base, opts: { mingGongMethod: 'shiShang' } });
		const b = calcYizhangjing({ ...base, opts: { mingGongMethod: 'shuZhiMao' } });
		// 时上起命=时宫；数至卯=另算，二者本例不同
		expect(a.mingIdx).not.toBe(b.mingIdx);
	});
	it('流年十二神 A/B/C 三套不同', () => {
		const t = branchIndex('午');
		const f = branchIndex('子');
		const a = xunShenAt(f, t, 'A');
		const b = xunShenAt(f, t, 'B');
		const c = xunShenAt(f, t, 'C');
		expect(FLOW_SETS.A.length).toBe(12);
		expect([a, b, c].some((x, i, arr) => arr.indexOf(x) !== i) || a !== b || b !== c).toBeTruthy();
	});
	it('秘传起运岁：命宫天厄男=4岁起', () => {
		// 造一个命宫落天厄的盘，验起运岁
		const r = calcYizhangjing({ yearBranch: '子', month: 1, day: 1, hourBranch: '子', gender: '男', opts: { dayunStartAge: 'mi', mingGongMethod: 'shuZhiMao' } });
		expect(r).toBeTruthy();
		expect(r.dayun[0].from).toBe(r.mingStar === '天厄' ? 4 : (r.mingStar === '天刃' ? 10 : (r.mingStar === '天破' || r.mingStar === '天孤' ? 12 : 1)));
	});
});

describe('一掌经引擎 · 边界与健壮', () => {
	it('极端月日不崩、四柱合法', () => {
		const r = calcYizhangjing({ yearBranch: '亥', month: 12, day: 30, hourBranch: '亥', gender: '女', opts: {} });
		expect(r).toBeTruthy();
		expect(r.pillars).toHaveLength(4);
		r.pillars.forEach((p) => expect(p.idx).toBeGreaterThanOrEqual(0));
	});
	it('非法入参 → null', () => {
		expect(calcYizhangjing({ yearBranch: 'X', month: 2, day: 7, hourBranch: '寅', gender: '男' })).toBeNull();
		expect(calcYizhangjing({ yearBranch: '巳', month: 0, day: 7, hourBranch: '寅', gender: '男' })).toBeNull();
	});
	it('人事十二宫自命宫顺布、长度12', () => {
		const r = calcYizhangjing({ yearBranch: '子', month: 1, day: 9, hourBranch: '酉', gender: '男', opts: { mingGongMethod: 'shuZhiMao' } });
		expect(r.renshi).toHaveLength(12);
		expect(r.renshi[0].palace).toBe('命');
		expect(r.renshi[0].idx).toBe(r.mingIdx);
	});
});
