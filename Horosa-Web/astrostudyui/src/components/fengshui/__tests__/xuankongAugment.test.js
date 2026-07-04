// WP-4 玄空飞星深化：兼向度数判别(4.5/4.12) + 流年会断(4.20) + 阴阳宅(4.19)。
import { xuankong } from '../xuankong';
import { jianXiangByDeg } from '../liqiCore';

describe('WP-4 玄空 · 兼向度数自动判别（正统古法）', () => {
	test('午正中(180°)=下卦、午偏5°=兼向替卦、深兼同卦', () => {
		const c = jianXiangByDeg(180);
		expect(c.xiangShan).toBe('午'); expect(c.jian).toBe(false); expect(c.mode).toMatch(/下卦/);
		const r = jianXiangByDeg(185);
		expect(r.xiangShan).toBe('午'); expect(r.jian).toBe(true); expect(r.adjShan).toBe('丁');
		const l = jianXiangByDeg(175);
		expect(l.adjShan).toBe('丙'); expect(l.jian).toBe(true);
	});
	test('丙午同卦深兼(离宫)vs 丑癸异卦出卦风险', () => {
		const same = jianXiangByDeg(173);   // 午偏丙侧,丙午同离宫
		expect(same.sameGua).toBe(true);
		const cross = jianXiangByDeg(23);    // 丑偏癸侧,艮/坎异卦
		expect(cross.sameGua).toBe(false); expect(cross.kong).toBe(true);
	});
	test('xuankong 给 deg：向首由度数定,jianInfo 返回', () => {
		const r = xuankong(9, '午', { deg: 185 });
		expect(r.xiangShan).toBe('午');
		expect(r.jianInfo.jian).toBe(true);
		// 下卦零回归：不给 deg/jian → 下卦
		expect(xuankong(9, '午').method).toBe('下卦');
	});
});

describe('WP-4 玄空 · 流年会断 + 阴阳宅（正统古法）', () => {
	test('流年五黄入中(2022)→中宫五黄到·忌动土', () => {
		const r = xuankong(9, '午', { year: 2022 });
		expect(Array.isArray(r.yearHui)).toBe(true);
		expect(r.yearHui.some((h)=>h.warn.indexOf('五黄') >= 0 && h.jx === 'bad')).toBe(true);
	});
	test('不给流年→yearHui=null；阴阳宅默认 yang，可切 yin', () => {
		expect(xuankong(9, '午').yearHui).toBeNull();
		expect(xuankong(9, '午').yinYangZhai).toBe('yang');
		expect(xuankong(9, '午', { yinYangZhai: 'yin' }).yinYangZhai).toBe('yin');
	});
});
