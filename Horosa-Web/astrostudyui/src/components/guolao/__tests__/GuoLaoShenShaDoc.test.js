import { GUOLAO_SHENSHA_DOC, guolaoShenShaTip, guolaoShenShaJx } from '../GuoLaoShenShaDoc';
import { MOIRA_BIRTH_GOD_ORDER, MOIRA_TRANSIT_GOD_ORDER } from '../GuoLaoMoiraWheel';

describe('GuoLaoShenShaDoc 神煞判语库', () => {
	test('命盘轮所有起例神煞（本命+流年）都有判语', () => {
		const names = Array.from(new Set([...MOIRA_BIRTH_GOD_ORDER, ...MOIRA_TRANSIT_GOD_ORDER]));
		const missing = names.filter((n) => !GUOLAO_SHENSHA_DOC[n]);
		expect(missing).toEqual([]);
	});

	test('每条判语 jx 合法、desc 非空', () => {
		Object.entries(GUOLAO_SHENSHA_DOC).forEach(([name, v]) => {
			expect(['吉', '凶', '中']).toContain(v.jx);
			expect(typeof v.desc).toBe('string');
			expect(v.desc.length).toBeGreaterThan(2);
		});
	});

	test('guolaoShenShaTip：命中返回吉凶标签+含义；缺项兜底不抛', () => {
		const tip = guolaoShenShaTip('天贵');
		expect(tip).toContain('天贵');
		expect(tip).toContain('天乙贵人');
		expect(['【吉】', '【凶】', '【中】'].some((t) => tip.indexOf(t) >= 0)).toBe(true);
		expect(guolaoShenShaTip('不存在神煞XYZ')).toContain('不存在神煞XYZ');
		expect(guolaoShenShaTip('')).toBe('');
	});

	test('guolaoShenShaJx 返回吉凶或空串', () => {
		expect(guolaoShenShaJx('禄勋')).toBe('吉');
		expect(guolaoShenShaJx('劫杀')).toBe('凶');
		expect(guolaoShenShaJx('不存在')).toBe('');
	});
});
