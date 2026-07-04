import golden from './liuyao64.golden.json';
import { Gua64 } from '../../gua/GuaConst';
import { parseYaoName, palaceTypeOf } from '../../gua/LiuYaoEngine';

// WP-0 真值 golden:前端 Gua64 + 引擎派生 逐爻对照文档 内核基准 build_all_64() 字节一致。
// 文档卦序类型「本宫(八纯)」↔ 前端「本宫」。
function normType(t){ return t.replace('(八纯)', ''); }

describe('六爻 WP-0 · 64卦纳甲 golden(对文档 内核基准)', () => {
	test('golden 含 64 卦', () => {
		expect(Object.keys(golden).length).toBe(64);
	});

	test('每卦逐爻 地支/五行/六亲/世应/阴阳 + 卦序类型/世位/应位 全字节一致', () => {
		let checked = 0;
		const fails = [];
		Object.keys(golden).forEach((name) => {
			const g = Gua64.find((x) => x.name === name);
			if(!g){ fails.push(`缺卦:${name}`); return; }
			const exp = golden[name];
			// 卦序类型/世应(引擎派生)
			const pt = palaceTypeOf(g);
			if(!pt){ fails.push(`${name}:palaceTypeOf null`); return; }
			if(normType(exp.type) !== pt.type){ fails.push(`${name}:类型 ${pt.type}≠${exp.type}`); }
			if(exp.shi !== pt.shi){ fails.push(`${name}:世位 ${pt.shi}≠${exp.shi}`); }
			if(exp.ying !== pt.ying){ fails.push(`${name}:应位 ${pt.ying}≠${exp.ying}`); }
			// 逐爻
			for(let i = 0; i < 6; i++){
				const p = parseYaoName(g.yaoname[i] || '');
				const ey = exp.yaos[i];
				if(p.zhi !== ey.zhi){ fails.push(`${name}#${i + 1}:支 ${p.zhi}≠${ey.zhi}`); }
				if(p.wuxing !== ey.wx){ fails.push(`${name}#${i + 1}:五行 ${p.wuxing}≠${ey.wx}`); }
				if(p.liuqin !== ey.lq){ fails.push(`${name}#${i + 1}:六亲 ${p.liuqin}≠${ey.lq}`); }
				if((p.shiYing || '') !== (ey.sy || '')){ fails.push(`${name}#${i + 1}:世应 ${p.shiYing}≠${ey.sy}`); }
				const yy = g.value[i] === 1 ? '阳' : '阴';
				if(yy !== ey.yy){ fails.push(`${name}#${i + 1}:阴阳 ${yy}≠${ey.yy}`); }
			}
			checked++;
		});
		if(fails.length){ throw new Error(`64卦 golden 不一致(${fails.length}):\n` + fails.slice(0, 30).join('\n')); }
		expect(checked).toBe(64);
	});
});
