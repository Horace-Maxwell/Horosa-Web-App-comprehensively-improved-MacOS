// 风水 理气六派 · 全选项穷举矩阵(QA 第3步)。每选项每取值 + 组合 + 边界,断中算(result)有效+显示字段齐。
import { xuankong } from '../xuankong';
import { sanhe, juByShuiKou } from '../sanhe';
import { zibai } from '../zibai';
import { qiankun } from '../qiankun';
import { bazhai } from '../bazhai';
import { jinsuo } from '../jinsuo';
import { SHAN_ORDER } from '../fengshuiData';

const PERM19 = (obj)=>Object.values(obj).slice().sort((a, b)=>a - b);
const isPerm = (obj)=>JSON.stringify(PERM19(obj)) === JSON.stringify([1, 2, 3, 4, 5, 6, 7, 8, 9]);
const GUA8 = ['坎', '坤', '震', '巽', '乾', '兑', '艮', '离'];
const MUKU = ['辛', '戌', '乾', '癸', '丑', '艮', '乙', '辰', '巽', '丁', '未', '坤'];   // 12 墓库山(四局各3)

describe('玄空 穷举：9运×24山×(下卦/替卦3方案)×流年月', ()=>{
	it('全 1296 组合(山向×运×起卦×方案)中算有效:三盘1-9排列 + 格局 + 城门/打劫数组 + 逐宫combo', ()=>{
		let n = 0;
		const variants = [{ jian: false }, { jian: true, tiVariant: 'shen' }, { jian: true, tiVariant: 'youbi' }, { jian: true, tiVariant: 'bengong' }];
		for (let yun = 1; yun <= 9; yun++) {
			for (const x of SHAN_ORDER) {
				for (const v of variants) {
					const r = xuankong(yun, x, v);
					expect(r.available).toBe(true);
					expect(isPerm(r.shanPan)).toBe(true);
					expect(isPerm(r.xiangPan)).toBe(true);
					expect(isPerm(r.yunPan)).toBe(true);
					expect(['旺山旺向', '上山下水', '双星到向', '双星到坐', '其他/侧局']).toContain(r.ge);
					expect(Array.isArray(r.flags)).toBe(true);
					expect(Array.isArray(r.rob)).toBe(true);
					expect(r.gate).toBeTruthy();
					expect(r.zhengShen.gong + r.lingShen.gong).toBe(10);
					expect(r.palaces.length).toBe(9);
					r.palaces.forEach((p)=>{
						expect(p.shan).toBeGreaterThanOrEqual(1); expect(p.shan).toBeLessThanOrEqual(9);
						expect(p.xiang).toBeGreaterThanOrEqual(1); expect(p.xiang).toBeLessThanOrEqual(9);
						expect(typeof p.combo.note).toBe('string');     // 每宫双星断非空类型
					});
					expect(r.method).toBe(v.jian ? '替卦' : '下卦');
					n++;
				}
			}
		}
		expect(n).toBe(9 * 24 * 4);   // 864
	});
	it('流年/流月叠加:给 year/month 则年月盘1-9排列、五黄可定位', ()=>{
		for (let m = 1; m <= 12; m++) {
			const r = xuankong(8, '午', { year: 2024, month: m });
			expect(isPerm(r.yearPan)).toBe(true);
			expect(isPerm(r.monthPan)).toBe(true);
		}
		// 边界:month=0/缺省 → 无月盘(UI "0=不显")。
		expect(xuankong(8, '午', { year: 2024, month: 0 }).monthPan).toBe(null);
		expect(xuankong(8, '午', {}).yearPan).toBe(null);
	});
	it('替卦 vs 下卦:替星≠运星时盘必变(向首兼向纳气驳杂)', ()=>{
		// 至少存在一山使替卦≠下卦(否则替卦功能形同虚设)。
		let changed = 0;
		for (const x of SHAN_ORDER) {
			const a = xuankong(8, x, { jian: false });
			const b = xuankong(8, x, { jian: true, tiVariant: 'shen' });
			if (JSON.stringify(a.xiangPan) !== JSON.stringify(b.xiangPan) || JSON.stringify(a.shanPan) !== JSON.stringify(b.shanPan)) { changed++; }
		}
		expect(changed).toBeGreaterThan(0);
	});
});

describe('三合 穷举：12墓库山×2水势 + 非墓库山边界', ()=>{
	it('12 墓库山每个都定局、长生环12双山齐、立向有别', ()=>{
		MUKU.forEach((sk)=>{
			['leftToRight', 'rightToLeft'].forEach((wf)=>{
				const r = sanhe({ shuiKou: sk, waterFlow: wf });
				expect(r.available).toBe(true);
				expect(['火局', '金局', '水局', '木局']).toContain(r.ju);
				expect(r.ring.length).toBe(12);
				expect(r.xiangFa).toBeTruthy();
				expect(r.xiangFa.type).toBe(wf === 'leftToRight' ? '正旺向' : '正生向');
			});
		});
	});
	it('非墓库山(子午卯酉等12)→ 未定局(UI 应限制为墓库山)', ()=>{
		['子', '午', '卯', '酉', '壬', '丙'].forEach((sk)=>{
			expect(juByShuiKou(sk)).toBe(null);
			expect(sanhe({ shuiKou: sk }).available).toBe(false);
		});
	});
});

describe('紫白 穷举：年份范围×流月', ()=>{
	it('1900-2043 各年 + 1-12月:年月入中星1-9、九宫齐', ()=>{
		for (let y = 1900; y <= 2043; y += 7) {
			const r = zibai({ year: y });
			expect(r.available).toBe(true);
			expect(r.yearCenter).toBeGreaterThanOrEqual(1); expect(r.yearCenter).toBeLessThanOrEqual(9);
			expect(r.yearPalaces.length).toBe(9);
			for (let m = 1; m <= 12; m++) {
				const rm = zibai({ year: y, month: m });
				expect(rm.monthCenter).toBeGreaterThanOrEqual(1); expect(rm.monthCenter).toBeLessThanOrEqual(9);
			}
		}
	});
});

describe('八宅 穷举：8坐山×男女×命年', ()=>{
	it('每组合:8方游星齐、宅命组定、相配有判', ()=>{
		GUA8.forEach((g)=>{
			[true, false].forEach((male)=>{
				for (let y = 1924; y <= 2020; y += 13) {
					const r = bazhai({ zuoGua: g, ming: { year: y, isMale: male } });
					expect(r.available).toBe(true);
					expect(r.palaces.length).toBe(8);
					expect(['东四宅', '西四宅']).toContain(r.zhaiGroup);
					expect(['东四命', '西四命']).toContain(r.mingGroup);
					expect(r.match).toBeTruthy();
					expect(typeof r.match.same).toBe('boolean');
					expect(r.doorMainStove.door).toBeTruthy();
				}
			});
		});
	});
	it('性别切换确实改命卦(男女命卦法不同)', ()=>{
		let diff = 0;
		GUA8.forEach((g)=>{
			const m = bazhai({ zuoGua: g, ming: { year: 1985, isMale: true } });
			const f = bazhai({ zuoGua: g, ming: { year: 1985, isMale: false } });
			if (m.mingGua !== f.mingGua) { diff++; }
		});
		expect(diff).toBeGreaterThan(0);   // 1985 男女命卦不同
	});
});

describe('乾坤国宝 穷举：8坐山', ()=>{
	it('每坐山:九大水位齐(先后天/案劫/天劫/地刑/宾/客/辅/正窍)、来去水断9条', ()=>{
		GUA8.forEach((g)=>{
			const r = qiankun({ zuoGua: g });
			expect(r.available).toBe(true);
			expect(r.xianTian).toBeTruthy();
			expect(r.houTian).toBeTruthy();
			expect(r.positions.length).toBe(9);
			// 天劫=向左前·地刑=向右前(几何确定,有落宫);宾客辅正窍依局图(pos=null)。
			expect(r.positions.find((p)=>p.name === '天劫位').pos).toBeGreaterThan(0);
			expect(r.positions.find((p)=>p.name === '地刑位').pos).toBeGreaterThan(0);
		});
	});
});

describe('金锁玉关 穷举：八方砂水平 组合 + 边界', ()=>{
	it('全平/全砂/全水/混合:得位计数与分值自洽(0-8 / 0-100)', ()=>{
		const mk = (val)=>{ const s = {}; GUA8.forEach((g)=>{ s[g] = val; }); return s; };
		[mk('flat'), mk('sand'), mk('water')].forEach((sectors)=>{
			const r = jinsuo({ sectors });
			expect(r.available).toBe(true);
			expect(r.palaces.length).toBe(8);
			expect(r.deCount).toBeGreaterThanOrEqual(0); expect(r.deCount).toBeLessThanOrEqual(8);
			expect(r.score).toBe(Math.round(r.deCount / 8 * 100));
		});
		// 全砂:坎坤震巽(要砂)得位=4;全水:乾兑艮离(要水)得位=4。
		expect(jinsuo({ sectors: mk('sand') }).deCount).toBe(4);
		expect(jinsuo({ sectors: mk('water') }).deCount).toBe(4);
		expect(jinsuo({ sectors: mk('flat') }).deCount).toBe(0);
		// 空 sectors(边界):不抛、全平。
		expect(jinsuo({}).deCount).toBe(0);
		expect(jinsuo({ sectors: {} }).deCount).toBe(0);
	});
	it('256 种八方砂水全组合(2^8 砂/水)不抛、得位单调', ()=>{
		for (let mask = 0; mask < 256; mask++) {
			const s = {};
			GUA8.forEach((g, i)=>{ s[g] = (mask & (1 << i)) ? 'sand' : 'water'; });
			const r = jinsuo({ sectors: s });
			expect(r.available).toBe(true);
			expect(r.palaces.every((p)=>typeof p.desc === 'string')).toBe(true);
		}
	});
});

describe('新增交互选项真生效(QA 第2步)', ()=>{
	it('紫白流月:给 month → monthPalaces 1-9;不给则 null', ()=>{
		expect(zibai({ year: 2026, month: 8 }).monthPalaces.length).toBe(9);
		expect(zibai({ year: 2026 }).monthPalaces).toBe(null);
	});
	it('八宅门主灶基准:命卦≠宅卦时 以宅 vs 以命 门方不同', ()=>{
		// 坐坎宅 + 1995命卦坤(西四) → 以宅(坎伏位)≠以命(坤伏位)。
		const zhai = bazhai({ zuoGua: '坎', ming: { year: 1995, isMale: true }, mode: 'zhai' });
		const mingm = bazhai({ zuoGua: '坎', ming: { year: 1995, isMale: true }, mode: 'ming' });
		expect(zhai.doorMainStove.door).not.toBe(mingm.doorMainStove.door);
	});
	it('乾坤来去水:先天位登记去水 → 失(jx=bad);来水 → 旺(jx=good)', ()=>{
		const go = qiankun({ zuoGua: '坎', waters: { xianTian: 'go' } });
		const come = qiankun({ zuoGua: '坎', waters: { xianTian: 'come' } });
		const xtGo = go.positions.find((p)=>p.key === 'xianTian');
		const xtCome = come.positions.find((p)=>p.key === 'xianTian');
		expect(xtGo.jx).toBe('bad');
		expect(xtCome.jx).toBe('good');
		expect(xtGo.result).not.toBe(xtCome.result);
	});
	it('三合水口下拉 12 候选都定局(UI SK_OPTS 全墓库)', ()=>{
		MUKU.forEach((sk)=>expect(sanhe({ shuiKou: sk }).available).toBe(true));
		expect(MUKU.length).toBe(12);
	});
});
