// WP-1 三合派全量：十二向(5.9)/黄泉(5.5)/拨砂(5.11·例5.16)/线法(5.12-14)/老三合(5.15) 锚古法。
import { sanhe } from '../sanhe';
import { sanheXiangFaAll, boshaWuGe, chuanshanAt, toudiAt, fenjinAt, huangquanBaYao, huangquanSiDa } from '../liqiCore';
import { sanheChangshengTable } from '../liqiCore';

const ringOf = (ju)=>sanheChangshengTable().map((r)=>({ shuangshan: r.shuangshan, zhi: r.zhi, stage: r[ju] }));

describe('WP-1 三合 · 四局四正向速查（正统古法）', () => {
	// 正统古法 表：火局 正生艮寅·正旺丙午·正墓辛戌·正养癸丑;水局 正生坤申·正旺壬子·正墓乙辰·正养丁未。
	const pick = (ju, type)=>sanheXiangFaAll(ringOf(ju)).find((x)=>x.type === type).shuangshan;
	test('火局四正向', () => {
		expect(pick('火局', '正生向')).toBe('艮寅');
		expect(pick('火局', '正旺向')).toBe('丙午');
		expect(pick('火局', '正墓向')).toBe('辛戌');
		expect(pick('火局', '正养向')).toBe('癸丑');
	});
	test('金/水/木局正旺向', () => {
		expect(pick('金局', '正旺向')).toBe('庚酉');
		expect(pick('水局', '正旺向')).toBe('壬子');
		expect(pick('木局', '正旺向')).toBe('甲卯');
	});
	test('自生向=临官·自旺向=衰（借库向）', () => {
		const all = sanheXiangFaAll(ringOf('水局'));
		expect(all.find((x)=>x.type === '自生向').stage).toBe('临官');
		expect(all.find((x)=>x.type === '自旺向').stage).toBe('衰');
		expect(all).toHaveLength(8);
	});
});

describe('WP-1 三合 · 拨砂五格（正统古法 / 例 5.16）', () => {
	// 例5.16：向丙午属火。木砂=生我(生格上吉)、水砂=克我(煞格凶)、土砂=泄气。
	test('火为我：木砂生格·水砂煞格·土砂泄格·金砂财格·火砂旺格', () => {
		expect(boshaWuGe('火', '木').ge).toBe('生格');
		expect(boshaWuGe('火', '水').ge).toBe('煞格');
		expect(boshaWuGe('火', '土').ge).toBe('泄格');
		expect(boshaWuGe('火', '金').ge).toBe('财格');
		expect(boshaWuGe('火', '火').ge).toBe('旺格');
	});
	test('sanhe 整合：火局正旺向丙午，震(木)砂=生格·坎(水)砂=煞格', () => {
		const r = sanhe({ shuiKou: '戌', xiangFaType: '正旺向', sands: { 震: 'sand', 坎: 'sand' } });
		const zhen = r.bosha.sands.find((s)=>s.gua === '震');
		const kan = r.bosha.sands.find((s)=>s.gua === '坎');
		expect(r.bosha.myWuxing).toBe('火');
		expect(zhen.wuGe.ge).toBe('生格');
		expect(kan.wuGe.ge).toBe('煞格');
	});
});

describe('WP-1 三合 · 黄泉八煞（正统古法）', () => {
	test('八曜煞：坐坎忌辰·坐离忌亥·坐乾忌午', () => {
		expect(huangquanBaYao('坎')).toBe('辰');
		expect(huangquanBaYao('离')).toBe('亥');
		expect(huangquanBaYao('乾')).toBe('午');
	});
	test('四大黄泉：庚丁→坤·乙丙→巽·甲癸→艮·辛壬→乾', () => {
		expect(huangquanSiDa('庚')).toBe('坤');
		expect(huangquanSiDa('丙')).toBe('巽');
		expect(huangquanSiDa('癸')).toBe('艮');
		expect(huangquanSiDa('壬')).toBe('乾');
	});
	test('sanhe 整合：火局正旺向丙午→坐子(丙午冲壬子)坐坎忌辰方', () => {
		const r = sanhe({ shuiKou: '戌', xiangFaType: '正旺向' });
		expect(r.huangquan.zuoGua).toBe('坎');
		expect(r.huangquan.baYao.jiFang).toBe('辰');
	});
});

describe('WP-1 三合 · 线法（正统古法，结构性可靠）', () => {
	test('穿山72龙每山3龙(5°)·中龙正气旺相', () => {
		const c = chuanshanAt(0);   // 子山正中
		expect(c.shan).toBe('子');
		expect(c.longIndex).toBe(1);      // 正中=中龙
		expect(c.positional).toBe('正气旺相');
	});
	test('透地60龙6°/龙·甲己龙空亡', () => {
		const t = toudiAt(0);
		expect(t.shan).toBe('子');
		expect(typeof t.ganzhi).toBe('string');
		// 空亡判据自洽
		const many = Array.from({ length: 60 }, (_, i)=>toudiAt(i * 6));
		expect(many.filter((x)=>x.kong).length).toBe(12);   // 甲/己各6
	});
	test('120分金每山5分金(3°)·中3旺相边2空亡', () => {
		const mid = fenjinAt(0);   // 子山正中
		expect(mid.shan).toBe('子');
		expect(mid.fenIndex).toBe(2);      // 正中=第3分金
		expect(mid.positional).toBe('旺相(取)');
		const edge = fenjinAt(0 - 6);      // 偏出中心
		expect(edge.positional).toBe('空亡(避)');
	});
	test('全周穿山72格·透地60格·分金120格 覆盖不越界', () => {
		for (let d = 0; d < 360; d += 1) {
			expect(chuanshanAt(d).shan).toBeTruthy();
			expect(toudiAt(d).ganzhi).toHaveLength(2);
			expect(['旺相(取)', '空亡(避)']).toContain(fenjinAt(d).positional);
		}
	});
});
