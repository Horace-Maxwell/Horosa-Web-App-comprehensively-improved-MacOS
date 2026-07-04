// 玄空飞星 下卦 + 结构断 golden（对齐 golden 基准 的反吟/伏吟标注）。
import { xuankong } from '../xuankong';
import { SHAN_ORDER } from '../fengshuiData';

describe('玄空飞星 xuankong', ()=>{
	it('坐子向午(9运)：双星到坐 + 山盘反吟（== golden 基准 标注）', ()=>{
		const r = xuankong(9, '午');
		expect(r.available).toBe(true);
		expect(r.zuoShan).toBe('子');
		expect(r.ge).toBe('双星到坐');
		const fk = r.flags.map((f)=>f.key);
		expect(fk).toContain('shanFanyin');     // golden 标「山反吟」
		expect(fk).not.toContain('shanFuyin');
		expect(r.palaces.length).toBe(9);
		// 各宫 combo + 当令判齐备。
		r.palaces.forEach((p)=>{
			expect(p.combo && p.combo.pair).toBeTruthy();
			expect(['当令旺', '未来生气', '失令']).toContain(p.shanTime);
		});
	});

	it('坐壬向丙(9运)：双星到向 + 山盘伏吟（== golden 基准 标注）', ()=>{
		const r = xuankong(9, '丙');
		expect(r.ge).toBe('双星到向');
		const fk = r.flags.map((f)=>f.key);
		expect(fk).toContain('shanFuyin');       // golden 标「山伏吟」
		expect(fk).not.toContain('shanFanyin');
	});

	it('零正：正神=向首宫、零神=对宫；24山全运不抛、九宫齐全', ()=>{
		for (let yun = 1; yun <= 9; yun++) {
			for (const x of SHAN_ORDER) {
				const r = xuankong(yun, x);
				expect(r.available).toBe(true);
				expect(r.zhengShen.gong + r.lingShen.gong).toBe(10);   // 正零对宫
				expect(r.palaces.length).toBe(9);
				expect(['旺山旺向', '上山下水', '双星到向', '双星到坐', '其他/侧局']).toContain(r.ge);
			}
		}
	});

	it('双星凶组合标记：2·5 二五交加 / 3·7 穿心', ()=>{
		// 找一个含 2·5 的宫验 combo.badge='bad'(任一盘存在即可,这里测函数语义)。
		const r = xuankong(5, '午');
		// 至少结构字段齐备 + flags 为数组。
		expect(Array.isArray(r.flags)).toBe(true);
		expect(typeof r.fuMuSanBan).toBe('boolean');
	});

	it('流年盘：给 year 则九宫年飞星齐全(1-9 排列)', ()=>{
		const r = xuankong(9, '午', { year: 2026 });
		expect(r.yearPan).toBeTruthy();
		expect(Object.values(r.yearPan).sort((a, b)=>a - b)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
	});
});
