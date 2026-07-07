// 🔴 Moira 星辰庙旺(殿垣庙旺乐喜怒)+速度态(顺逆留伏迟速)金标:
// 抄自 moira_t.prop:1845-1858(星辰X 表)+ 714-724(speed_state/stationary_gap/slow_speed/fast_speed/invisible_gap)。
// 数据 byte-perfect,失败要核 Moira 源、不是改测试将就。
import { SIGN_STATUS_SEQ, SIGN_STATUS_TABLE, starDignityStatuses, starMotionState, STAR_SPEED_SPEC, starCombust } from '../guolaoData';

describe('Moira 庙旺表 SIGN_STATUS_TABLE(殿垣庙旺乐喜怒)', ()=>{
	test('序 = 殿,垣,庙,旺,乐,喜,怒', ()=>{
		expect(SIGN_STATUS_SEQ).toEqual(['殿', '垣', '庙', '旺', '乐', '喜', '怒']);
	});
	test('日在午 = 垣·庙·乐(同地支多态按序)', ()=>{
		expect(SIGN_STATUS_TABLE.日.午).toEqual(['垣', '庙', '乐']);
	});
	test('金在酉 = 垣·庙·乐;金在寅 = 怒;金在午 = 旺', ()=>{
		expect(SIGN_STATUS_TABLE.金.酉).toEqual(['垣', '庙', '乐']);
		expect(SIGN_STATUS_TABLE.金.寅).toEqual(['怒']);
		expect(SIGN_STATUS_TABLE.金.午).toEqual(['旺']);
	});
	test('土在子/丑 = 垣·庙·乐;水在申/巳 = 垣·旺·乐', ()=>{
		expect(SIGN_STATUS_TABLE.土.子).toEqual(['垣', '庙', '乐']);
		expect(SIGN_STATUS_TABLE.土.丑).toEqual(['垣', '庙', '乐']);
		expect(SIGN_STATUS_TABLE.水.申).toEqual(['垣', '旺', '乐']);
		expect(SIGN_STATUS_TABLE.水.巳).toEqual(['垣', '旺', '乐']);
	});
	test('四余有庙旺:计巳=庙、罗午=庙、炁申=庙、孛未=庙', ()=>{
		expect(SIGN_STATUS_TABLE.计.巳).toEqual(['庙']);
		expect(SIGN_STATUS_TABLE.罗.午).toEqual(['庙']);
		expect(SIGN_STATUS_TABLE.炁.申).toEqual(['庙']);
		expect(SIGN_STATUS_TABLE.孛.未).toEqual(['庙']);
	});
});

describe('starDignityStatuses(升殿=擢升度峰值前置「殿」)', ()=>{
	test('日在午非峰值 → 垣·庙·乐', ()=>{
		expect(starDignityStatuses('日', '午', false)).toEqual(['垣', '庙', '乐']);
	});
	test('日在戌且躔擢升度峰值 → 殿·旺(殿前置)', ()=>{
		expect(starDignityStatuses('日', '戌', true)).toEqual(['殿', '旺']);
	});
	test('天海冥无 Moira 庙旺 → []', ()=>{
		expect(starDignityStatuses('天', '午', false)).toEqual([]);
		expect(starDignityStatuses('海', '子', true)).toEqual(['殿']);   // 天海冥无表项,但若强制峰值仅得殿(实际无擢升不会触发)
	});
});

describe('starMotionState(顺逆留伏迟速,金标阈值 金木水火土)', ()=>{
	test('阈值 = Moira 原值(金木水火土)', ()=>{
		expect(STAR_SPEED_SPEC.金).toEqual({ stat: 0.15, invisible: 3.0, slow: 0.71, fast: 1.245 });
		expect(STAR_SPEED_SPEC.土).toEqual({ stat: 0.05, invisible: 3.0, slow: 0.02, fast: 0.13 });
	});
	test('金 速>fast(1.3) → 顺·速;金 速∈(slow,fast)(1.0) → 顺', ()=>{
		expect(starMotionState('金', 1.3, false)).toBe('顺·速');
		expect(starMotionState('金', 1.0, false)).toBe('顺');
	});
	test('金 逆行小速(-0.5) → 逆·迟;金 |速|<stat(0.1) → 留', ()=>{
		expect(starMotionState('金', -0.5, false)).toBe('逆·迟');
		expect(starMotionState('金', 0.1, false)).toBe('留');
	});
	test('金 合日(伏)优先并入:伏·留', ()=>{
		expect(starMotionState('金', 0.1, true)).toBe('伏·留');
	});
	test('日月无迟速档 → 仅顺;计罗无速度 → 逆(平交点)', ()=>{
		expect(starMotionState('日', 0.98, false)).toBe('顺');
		expect(starMotionState('月', 13.1, false)).toBe('顺');
		expect(starMotionState('计', NaN, false)).toBe('逆');
		expect(starMotionState('罗', NaN, false)).toBe('逆');
	});
	test('天(天王)派生阈值:速>fast(0.06)→顺·速;逆行(-0.01)→逆·迟;近留(0.003)→留', ()=>{
		expect(starMotionState('天', 0.06, false)).toBe('顺·速');
		expect(starMotionState('天', -0.01, false)).toBe('逆·迟');
		expect(starMotionState('天', 0.003, false)).toBe('留');
	});
	test('升顶角点(非计罗、无速度)→ 空串', ()=>{
		expect(starMotionState('升', NaN, false)).toBe('');
		expect(starMotionState('顶', NaN, false)).toBe('');
	});
});

// 🔴 合日「伏」单一真值 starCombust：照 Moira invisible_gap=3.0 且 <= 判(非面板 isCombustObj 的 8° 焦伤)。
// 消「右栏星点动态 8° vs AI 快照 3°」双口径分歧(审计确认 bug)。
describe('starCombust(Moira 合日 3° · 仅五星 · <=)', ()=>{
	test('金距日 3.0° 整 → 伏(<= 边界含)', ()=>{
		expect(starCombust('金', 100, 103)).toBe(true);
		expect(starCombust('金', 103, 100)).toBe(true);
	});
	test('金距日 5° → 不伏(>3,曾被 8° 误判为伏)', ()=>{
		expect(starCombust('金', 100, 105)).toBe(false);
	});
	test('金距日 0° → 伏;跨 0° 环绕(359 vs 1,距 2°)→ 伏', ()=>{
		expect(starCombust('金', 100, 100)).toBe(true);
		expect(starCombust('火', 359, 1)).toBe(true);
	});
	test('非五星(日/月/计/天海冥)一律不伏', ()=>{
		expect(starCombust('日', 100, 101)).toBe(false);
		expect(starCombust('月', 100, 101)).toBe(false);
		expect(starCombust('计', 100, 101)).toBe(false);
		expect(starCombust('天', 100, 101)).toBe(false);
	});
	test('缺数据(NaN)→ 不伏(不抛)', ()=>{
		expect(starCombust('金', NaN, 100)).toBe(false);
		expect(starCombust('金', 100, undefined)).toBe(false);
	});
	test('阈值取自 canonical STAR_SPEED_SPEC.invisible=3.0(非硬编码)', ()=>{
		expect(STAR_SPEED_SPEC.金.invisible).toBe(3.0);
		// 3.0 恰边界含、3.01 排除 → 证明用的是 <= invisible
		expect(starCombust('土', 100, 103.0)).toBe(true);
		expect(starCombust('土', 100, 103.01)).toBe(false);
	});
});
