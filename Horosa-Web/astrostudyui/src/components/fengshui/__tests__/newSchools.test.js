// WP-6..10 新增流派：辅星水法/净阴净阳/玄空大卦/形势清单/择日。
import { fuxing } from '../fuxing';
import { jingyin } from '../jingyin';
import { dagua } from '../dagua';
import { xingshi } from '../xingshi';
import { yearGods, dayCourse, zaoMing } from '../zeri';

describe('WP-6 辅星水法（8.2/8.8，翻卦同八宅）', () => {
	test('坎起辅弼：巽方生气贪狼(吉)、来水巽=合', () => {
		const r = fuxing({ benGua: '坎', waters: { 巽: 'come', 乾: 'come' } });
		const xun = r.palaces.find((p)=>p.gua === '巽');
		expect(xun.star).toBe('贪狼'); expect(xun.jx).toBe('good');
		expect(xun.verdictJx).toBe('good');                 // 来水吉星方=合
		const qian = r.palaces.find((p)=>p.gua === '乾');   // 乾=六煞(凶星)
		expect(qian.verdictJx).toBe('bad');                 // 来水凶星方=逆
	});
});

describe('WP-7 净阴净阳纳甲水法（8.7）', () => {
	test('乾甲坤俱净阳→吉；混阴阳→凶', () => {
		const ok = jingyin({ long: '乾', xiang: '甲', water: '坤' });
		expect(ok.jing).toBe(true); expect(ok.pureType).toBe('阳'); expect(ok.verdict.jx).toBe('good');
		const bad = jingyin({ long: '乾', xiang: '艮', water: '坤' });   // 艮=阴
		expect(bad.jing).toBe(false); expect(bad.verdict.jx).toBe('bad');
	});
	test('六秀催官：丙(六秀)在向→标催官', () => {
		const r = jingyin({ long: '艮', xiang: '丙', water: '辛' });   // 皆净阴 + 六秀
		expect(r.jing).toBe(true);
		expect(r.liuxiu).toBeTruthy();
	});
});

describe('WP-8 玄空大卦框架（第六部）', () => {
	test('64卦识别：向乾乾=乾为天、坐(错)=坤为地', () => {
		const r = dagua({ xiangLower: '乾', xiangUpper: '乾', yun: 9 });
		expect(r.xiang.name).toBe('乾为天');
		expect(r.zuo.name).toBe('坤为地');
	});
	test('零正按元运：9运正神9/零神1(合十)', () => {
		const r = dagua({ xiangLower: '坎', xiangUpper: '离', yun: 9 });
		expect(r.zheng.yun).toBe(9); expect(r.ling.yun).toBe(1);
	});
	test('卦运方案：input 覆盖 → 真夫妇合十判定随之', () => {
		const r = dagua({ xiangLower: '乾', xiangUpper: '乾', yun: 9, yunScheme: 'input', yunOverride: { 乾为天: 1, 坤为地: 9 } });
		expect(r.xiang.yun).toBe(1); expect(r.zuo.yun).toBe(9);
		expect(r.zhenFuFu).toBe(true);   // 1+9=10 合十真夫妇
	});
});

describe('WP-9 形势派判定清单（第二部）', () => {
	test('龙真穴的砂吉水吉→上吉；龙死砂凶→凶', () => {
		const good = xingshi({ longSheng: true, longStar: '贪狼', boHuan: true, guoXiaGood: true, xueType: '窝穴', zhengXue: ['朝山证', '案山证'], guiSha: ['文笔'], shuiCheng: '金城', laiShuiKai: true, quShuiGuan: true, xiangChaoJi: true });
		expect(good.grade.jx).toBe('good'); expect(good.total).toBeGreaterThan(6);
		const bad = xingshi({ longSheng: false, longStar: '破军', xiongSha: ['探头', '刀枪'], shuiCheng: '火城', xiangChongSha: true });
		expect(bad.grade.jx).toBe('bad');
	});
});

describe('WP-10 择日（第九部）', () => {
	test('年神：2026丙午年三煞在北(亥子丑)、岁破子、太岁午（正统古法）', () => {
		const g = yearGods(2026);
		expect(g.yearGanZhi).toBe('丙午');
		expect(g.sansha.list.map((s)=>s.zhi).sort()).toEqual(['丑', '亥', '子'].sort());
		expect(g.suipo.zhi).toBe('子');
		expect(g.taisui.zhi).toBe('午');
		expect(g.jiDongDirs.length).toBeGreaterThan(0);
	});
	test('日课：建除/黄黑道/28宿齐（lunar 值宿）', () => {
		const c = dayCourse(2026, 3, 20);
		expect(['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']).toContain(c.jianChu.name);
		expect(['黄道', '黑道']).toContain(c.huangHei.dao);
		expect(c.xiu.name).toBeTruthy();
	});
	test('杨公造命：扶山/避煞评分', () => {
		const z = zaoMing({ zuoShan: '子', y: 2026, m: 3, d: 20 });
		expect(z.available).toBe(true);
		expect(Array.isArray(z.items)).toBe(true);
		expect(z.grade).toBeTruthy();
	});
});
