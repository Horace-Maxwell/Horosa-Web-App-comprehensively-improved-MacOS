// 合盘「关系量化」→ AI 快照：Score 盘型应产出契合分数 + 顺畅/张力 top 相位段；
// 非 Score 盘型不得误注入该段（守 buildRelativeSnapshotText 分支隔离）。
import { buildRelativeSnapshotText } from '../../components/astro/AstroRelative';

describe('合盘关系量化 → AI 快照(Score 段)', () => {
	const scoreComp = {
		currentTab: 'Score',
		chartA: { record: { name: '甲', birth: '1990-01-01 12:00', lon: 116, lat: 40 } },
		chartB: { record: { name: '乙', birth: '1992-02-02 08:30', lon: 121, lat: 31 } },
		params: { hsys: 0, zodiacal: 0 },
		result: {
			score: 72,
			highlights: [{ a: 'Sun', b: 'Venus', aspect: 120, orb: 0.3, impact: 4 }],
			challenges: [{ a: 'Mars', b: 'Saturn', aspect: 90, orb: 0.5, impact: -4 }],
			aspects: [],
		},
	};

	it('Score 盘型输出契合分数 + 顺畅/张力相位', () => {
		const t = buildRelativeSnapshotText(scoreComp);
		expect(t).toMatch(/\[关系量化\]/);
		expect(t).toMatch(/契合分数：72/);
		expect(t).toMatch(/\[顺畅连接\]/);
		expect(t).toMatch(/\[张力连接\]/);
		expect(t).toMatch(/120˚/); // 三分相位度数
		expect(t).toMatch(/权重/); // impact 权重列
		// 起盘信息头仍在（盘型=关系量化 由 relationNameByKey 回落原键）
		expect(t).toMatch(/关系起盘信息/);
	});

	it('无分数(score 缺省)不崩、以占位符呈现', () => {
		const t = buildRelativeSnapshotText({ ...scoreComp, result: { highlights: [], challenges: [] } });
		expect(t).toMatch(/契合分数：-/);
	});

	it('非 Score 盘型不产出关系量化段(回归：不误注入)', () => {
		const t = buildRelativeSnapshotText({ currentTab: 'Comp', result: {}, params: {} });
		expect(t).not.toMatch(/关系量化/);
	});
});
