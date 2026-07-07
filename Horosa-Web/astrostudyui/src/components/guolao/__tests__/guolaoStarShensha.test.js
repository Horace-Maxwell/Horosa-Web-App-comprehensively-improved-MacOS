// 值难/宫位系 8 星值神煞 golden(照 Moira moira_t.prop:值難/職元/局主/天經/地緯/天元/地元/人元)。
import {
	resolveStarShensha,
	lifeSignBranch,
	yearGan,
	STAR_SHENSHA_NAMES,
} from '../guolaoStarShensha';

describe('guolaoStarShensha — 年干/命宫支 派生', () => {
	test('yearGan:公历年→年干(1984=甲子、2006=丙戌)', () => {
		expect(yearGan(1984)).toBe('甲');
		expect(yearGan(2006)).toBe('丙');
		expect(yearGan(2023)).toBe('癸');
	});

	test('lifeSignBranch:命宫黄经→地支(白羊=戌 镜像)', () => {
		expect(lifeSignBranch(0)).toBe('戌');   // 白羊 0°
		expect(lifeSignBranch(30)).toBe('酉');  // 金牛
		expect(lifeSignBranch(240)).toBe('寅'); // 人马起段
		expect(lifeSignBranch(300)).toBe('子'); // 摩羯
		expect(lifeSignBranch(360)).toBe('戌'); // 归一
	});
});

describe('guolaoStarShensha — 8 系星值 golden(甲年·命宫戌·辰月)', () => {
	// 年干甲、命宫支戌(黄经 300°+ 落 戌?这里直接用 lifeLon 使 lifeSignBranch→戌)、月支辰。
	// lifeSignBranch(300)=子;戌 对应星座序 10 → 黄经 [300,330) 是子。要落戌须星座序10=黄经300? 见下用显式 monthZhi/命宫。
	const rows = resolveStarShensha({ birthYear: 1984, lifeLon: 0, monthZhi: '辰' });
	const byName = Object.fromEntries(rows.map((r) => [r.name, r.star]));

	test('返回 8 项、顺序=值难/职元/局主/天经/地纬/天元/地元/人元', () => {
		expect(rows.map((r) => r.name)).toEqual(STAR_SHENSHA_NAMES);
	});

	// lifeLon=0 → 命宫支=戌(SIGN_BRANCH[0]);年干=甲;月支=辰。
	test('值难(辰月)=月', () => expect(byName['值难']).toBe('月'));
	test('职元(甲·戌)=孛', () => expect(byName['职元']).toBe('孛'));
	test('局主(甲·戌)=水', () => expect(byName['局主']).toBe('水'));
	test('天经(甲·戌)=木', () => expect(byName['天经']).toBe('木'));
	test('地纬(戌)=土', () => expect(byName['地纬']).toBe('土'));
	test('天元(甲·戌)=火', () => expect(byName['天元']).toBe('火'));
	test('地元(甲·戌)=木', () => expect(byName['地元']).toBe('木'));
	test('人元(甲·戌)=水', () => expect(byName['人元']).toBe('水'));
});

describe('guolaoStarShensha — 其它交叉点 golden', () => {
	test('值难各月支(子:金 午:火 未:罗 亥:炁)', () => {
		const at = (mz) => resolveStarShensha({ birthYear: 1984, lifeLon: 0, monthZhi: mz }).find((r) => r.name === '值难').star;
		expect(at('子')).toBe('金');
		expect(at('午')).toBe('火');
		expect(at('未')).toBe('罗');
		expect(at('亥')).toBe('炁');
	});

	test('癸年·命宫亥(lifeLon 330)诸元 vs Moira', () => {
		// lifeLon=330 → 星座序 11 → SIGN_BRANCH[11]=亥。年干癸。
		const rows = resolveStarShensha({ birthYear: 2023, lifeLon: 330, monthZhi: '子' });
		const byName = Object.fromEntries(rows.map((r) => [r.name, r.star]));
		expect(lifeSignBranch(330)).toBe('亥');
		expect(yearGan(2023)).toBe('癸');
		// Moira:职元癸 亥:木、局主癸 亥:炁、天经癸 亥:水、天元癸 亥:罗、地元癸 亥:水、人元癸 亥:金、地纬 亥:水
		expect(byName['职元']).toBe('木');
		expect(byName['局主']).toBe('炁');
		expect(byName['天经']).toBe('水');
		expect(byName['天元']).toBe('罗');
		expect(byName['地元']).toBe('水');
		expect(byName['人元']).toBe('金');
		expect(byName['地纬']).toBe('水');
	});

	test('缺输入 → 对应项 star 为空(不抛错)', () => {
		const rows = resolveStarShensha({});
		expect(rows).toHaveLength(8);
		// lifeLon 缺→默认 0→命宫戌 仍可解;月支缺→值难空。
		expect(rows.find((r) => r.name === '值难').star).toBe('');
	});
});
