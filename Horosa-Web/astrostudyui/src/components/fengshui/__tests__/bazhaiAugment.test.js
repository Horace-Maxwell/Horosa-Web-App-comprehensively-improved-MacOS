// WP-3 八宅深化：阳宅三要门主灶(3.9) + 九星配六事(3.10) 锚大游年表(3.4)。
import { bazhai, guaRelation } from '../bazhai';

describe('WP-3 八宅 · 两卦大游年关系（正统古法）', () => {
	test('坎↔离=延年、坎↔坤=绝命、乾↔坤=延年、乾↔离=绝命', () => {
		expect(guaRelation('坎', '离').name).toBe('延年');
		expect(guaRelation('坎', '坤').name).toBe('绝命');
		expect(guaRelation('乾', '坤').name).toBe('延年');
		expect(guaRelation('乾', '离').name).toBe('绝命');
	});
	test('同卦=伏位、坎↔震=天医、坎↔巽=生气、坎↔乾=六煞', () => {
		expect(guaRelation('坎', '坎').name).toBe('伏位');
		expect(guaRelation('坎', '震').name).toBe('天医');
		expect(guaRelation('坎', '巽').name).toBe('生气');
		expect(guaRelation('坎', '乾').name).toBe('六煞');
	});
});

describe('WP-3 八宅 · 阳宅三要门主灶（正统古法）', () => {
	test('门坎·主震·灶巽（全东四）→ 三吉宅', () => {
		const r = bazhai({ zuoGua: '坎', doorGua: '坎', mainGua: '震', stoveGua: '巽' });
		expect(r.sanYao.menMain.name).toBe('天医');     // 坎→震
		expect(r.sanYao.mainStove.name).toBe('延年');   // 震→巽
		expect(r.sanYao.menStove.name).toBe('生气');    // 坎→巽
		expect(r.sanYao.verdict.jx).toBe('good');
	});
	test('门坎·主乾（跨组，绝命/五鬼）→ 凶宅', () => {
		const r = bazhai({ zuoGua: '坎', doorGua: '坎', mainGua: '坤', stoveGua: '乾' });
		// 坎→坤=绝命 → 犯大凶
		expect(r.sanYao.menMain.name).toBe('绝命');
		expect(r.sanYao.verdict.jx).toBe('bad');
	});
	test('未给门主灶 → sanYao=null（向后兼容）', () => {
		const r = bazhai({ zuoGua: '坎' });
		expect(r.sanYao).toBeNull();
		expect(r.doorMainStove).toBeTruthy();          // 旧提示仍在
	});
});

describe('WP-3 八宅 · 九星配六事（正统古法）+ 静动变化宅（3.8）', () => {
	test('八方各有六事宜忌，吉方宜门床、凶方宜厕库', () => {
		const r = bazhai({ zuoGua: '坎' });
		expect(r.liushi).toHaveLength(8);
		const shengqi = r.liushi.find((x)=>x.star === '生气');
		const jueming = r.liushi.find((x)=>x.star === '绝命');
		expect(shengqi.advice).toMatch(/大门|主卧/);
		expect(jueming.advice).toMatch(/压灶|厕|不住人/);
	});
	test('静/动/变/化宅分类', () => {
		expect(bazhai({ zuoGua: '坎', zhaiType: 'jing' }).zhaiTypeInfo.name).toBe('静宅');
		expect(bazhai({ zuoGua: '坎', zhaiType: 'dong' }).zhaiTypeInfo.name).toBe('动宅');
		expect(bazhai({ zuoGua: '坎', zhaiType: 'hua' }).zhaiTypeInfo.range).toMatch(/十一至十五/);
	});
});
