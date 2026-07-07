// Moira 信息区四表纯函数金标(对照源码语义与已知命理常识值)。
import { weakBranchOf, weakSolidPillars, lifeHelperRow, smallLimitBranch, flyLimitBranches, limitDegreeSpan, childAgeLimitYears, childLimitBranch, LIFE_HELPER_TABLE } from '../guolaoMoiraTables';

describe('guolaoMoiraTables(Moira 信息区四表)', () => {
	test('虚宫=旬空:甲子旬空戌亥(甲子→戌,乙丑→亥),甲戌旬空申酉', () => {
		expect(weakBranchOf('甲子')).toBe('戌');
		expect(weakBranchOf('乙丑')).toBe('亥');
		expect(weakBranchOf('丙寅')).toBe('戌');
		expect(weakBranchOf('甲戌')).toBe('申');
		expect(weakBranchOf('乙亥')).toBe('酉');
		expect(weakBranchOf('癸酉')).toBe('亥');
	});

	test('虚实四柱两行(用户截图样例:柱 丙午/甲午/庚辰/乙酉 → 实:午午辰酉)', () => {
		const res = weakSolidPillars(['丙午', '甲午', '庚辰', '乙酉']);
		expect(res.solid).toEqual(['午', '午', '辰', '酉']);
		expect(res.weak).toHaveLength(4);
		res.weak.forEach((z)=>expect(z).toMatch(/[子丑寅卯辰巳午未申酉戌亥]/));
	});

	test('难仇恩用查表:七主星全 + 火主星样例(难水孛/仇金/恩木炁/用土计)', () => {
		expect(Object.keys(LIFE_HELPER_TABLE)).toHaveLength(7);
		expect(lifeHelperRow('火')).toEqual(['水孛', '金', '木炁', '土计']);
		expect(lifeHelperRow('日')).toEqual(['木炁', '土计', '金水', '火罗']);
		expect(lifeHelperRow('无')).toBe(null);
	});

	test('小限:命宫+每岁一宫(1 岁=命宫本支)', () => {
		// 命宫 100°(狮子中段)→ 黄道座 3(巨蟹?100/30=3=巨蟹)→ SIGN_BRANCH[3]=未
		expect(smallLimitBranch(100, 1)).toBe('未');
		expect(smallLimitBranch(100, 2)).toBe('午');
		expect(smallLimitBranch(100, 13)).toBe('未');
	});

	test('飞限:童限前 seq1;成年 seq2;半年段返回双支', () => {
		const child = flyLimitBranches(100, 2, 5);
		expect(child.branches).toHaveLength(1);
		const adult = flyLimitBranches(100, 20, 5);
		expect(adult.branches.length).toBeGreaterThanOrEqual(1);
		// 半年段:调整龄 66(=childLimit+66)且相邻序值不同 → 双支各半年
		const half = flyLimitBranches(100, 5 + 66, 5);
		expect(half.halfYear).toBe(true);
		expect(half.branches).toHaveLength(2);
	});

	test('限度/至:1 岁起于命宫下一宫头,首宫按童限年数线性;单调推进', () => {
		const a1 = limitDegreeSpan(100, 1, 11);
		// base = floor(100/30)*30+30 = 120;1 岁 s=0 → from=120
		expect(a1.from).toBeCloseTo(120, 6);
		expect(a1.to).toBeCloseTo(120 - 30 / 11, 6);
		const a12 = limitDegreeSpan(100, 12, 11);
		// 12 岁:消耗首宫 11 年 + 第二宫 0/10 → from=120-30=90
		expect(a12.from).toBeCloseTo(90, 6);
	});

	test('童限岁数上限=round(9+命度宫内度/3)(照 getChildLimit;child_period=0)', () => {
		expect(childAgeLimitYears(0)).toBe(9);      // 宫内度 0 → 9
		expect(childAgeLimitYears(15)).toBe(14);    // 9 + 5
		expect(childAgeLimitYears(30)).toBe(9);     // 30%30=0 → 9(整宫环绕)
		expect(childAgeLimitYears(29.9)).toBe(19);  // 9 + 9.97 ≈ 19
	});

	test('童限地支=命宫 + 30°·child_seq[虚岁-1](child_seq[0..]=0,1,7,6…)', () => {
		// 命宫白羊(0°=戌):[0]=0→戌、[1]=1→酉、[2]=7→(100→pos+210)戌起 210°=SIGN_BRANCH[7]=卯、[3]=6→辰
		expect(childLimitBranch(0, 1)).toBe('戌');
		expect(childLimitBranch(0, 2)).toBe('酉');
		expect(childLimitBranch(0, 3)).toBe('卯');
		expect(childLimitBranch(0, 4)).toBe('辰');
	});

	test('飞限第三分支回归(照 Moira getFlyLimit):调整龄 71 段用 seq[a+1] 非 seq[a]', () => {
		// 命宫 0°(戌·阳)、童限 9;虚岁 81 → cur_age(0基)=80 → a=80−9=71 ∈ [71,75) 第三分支。
		// 正确=fly_seq_yang2[72]=3 → SIGN_BRANCH[3]=未;旧版漏此分支会误取 seq[71]=0→戌。
		const f = flyLimitBranches(0, 80, 9);
		expect(f.halfYear).toBe(false);
		expect(f.branches).toEqual(['未']);
		// 虚岁 83 → cur=82 → a=73 同段:seq[74]=9 → SIGN_BRANCH[9]=丑(旧版误取 seq[73]=3→未)。
		expect(flyLimitBranches(0, 82, 9).branches).toEqual(['丑']);
	});
});
