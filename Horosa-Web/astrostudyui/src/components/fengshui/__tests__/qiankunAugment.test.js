// WP-2 乾坤国宝 九大水位：天劫/地刑几何(7.B.8) + 来去水断 + 合局(7.B.10) 锚古法。
import { qiankun } from '../qiankun';
import { qkgbFullPositions } from '../liqiCore';

describe('WP-2 乾坤国宝 · 九大水位齐', () => {
	test('坐坎：九位齐，先天兑(西)/后天坤(西南)/案劫离(南)', () => {
		const r = qiankun({ zuoGua: '坎' });
		expect(r.positions).toHaveLength(9);
		const names = r.positions.map((p)=>p.name);
		['先天位', '后天位', '案劫位', '天劫位', '地刑位', '宾位', '客位', '辅卦位', '正窍位'].forEach((n)=>expect(names).toContain(n));
		expect(r.xianTian).toBe('兑(西)');
		expect(r.houTian).toBe('坤(西南)');
		expect(r.anJie).toBe('离(南)');
	});
});

describe('WP-2 乾坤国宝 · 天劫地刑几何（正统古法 坐坎向离）', () => {
	// 坐坎向离(南180°)：天劫=向左前=巽(东南4)、地刑=向右前=坤(西南2)。
	test('坐坎：天劫=巽(4)、地刑=坤(2)、案劫=离(9)', () => {
		const f = qkgbFullPositions('坎');
		const g = (n)=>f.list.find((p)=>p.name === n).gong;
		expect(g('案劫位')).toBe(9);
		expect(g('天劫位')).toBe(4);
		expect(g('地刑位')).toBe(2);
	});
	test('坐离向坎(北0°)：天劫=乾(6)、地刑=艮(8)', () => {
		const f = qkgbFullPositions('离');
		const g = (n)=>f.list.find((p)=>p.name === n).gong;
		expect(g('案劫位')).toBe(1);      // 向坎北
		expect(g('天劫位')).toBe(6);      // 北左前=西北乾
		expect(g('地刑位')).toBe(8);      // 北右前=东北艮
	});
});

describe('WP-2 乾坤国宝 · 来去水断 + 合局（7.B.9/10）', () => {
	test('先天位来水=旺(good)、去水=损(bad)；案劫来水=忌(bad)、去水=合(good)', () => {
		const come = qiankun({ zuoGua: '坎', waters: { xianTian: 'come', anJie: 'come' } });
		expect(come.positions.find((p)=>p.key === 'xianTian').jx).toBe('good');
		expect(come.positions.find((p)=>p.key === 'anJie').jx).toBe('bad');
		const go = qiankun({ zuoGua: '坎', waters: { xianTian: 'go', anJie: 'go' } });
		expect(go.positions.find((p)=>p.key === 'xianTian').jx).toBe('bad');
		expect(go.positions.find((p)=>p.key === 'anJie').jx).toBe('good');
	});
	test('天劫来水=大凶、去水=大利；地刑见水=刑伤', () => {
		const r = qiankun({ zuoGua: '坎', waters: { tianJie: 'come', diXing: 'go' } });
		expect(r.positions.find((p)=>p.key === 'tianJie').jx).toBe('bad');   // 天劫来水凶
		expect(r.positions.find((p)=>p.key === 'diXing').jx).toBe('bad');    // 地刑见水凶
		expect(qiankun({ zuoGua: '坎', waters: { tianJie: 'go' } }).positions.find((p)=>p.key === 'tianJie').jx).toBe('good');
	});
	test('合局：先后天来水+案劫天劫去水+地刑无水', () => {
		expect(qiankun({ zuoGua: '坎', waters: { xianTian: 'come', houTian: 'come', anJie: 'go', tianJie: 'go' } }).heJu).toBe(true);
		expect(qiankun({ zuoGua: '坎', waters: { xianTian: 'come', houTian: 'come', anJie: 'go' } }).heJu).toBe(false);   // 天劫未去
		expect(qiankun({ zuoGua: '坎', waters: { xianTian: 'come', houTian: 'come', anJie: 'go', tianJie: 'go', diXing: 'come' } }).heJu).toBe(false);   // 地刑见水
	});
});
