// 净阴净阳纳甲水法（正统古法，催官篇廖赖一脉）· 龙/向/水按纳甲归净阴净阳，须同净方清纯。
import { najiaYinYang } from './liqiCore';
import { LIU_XIU } from './fengshuiData';

// 净阴净阳排盘：龙/向/水三山 → 各归阴阳 + 同净判定 + 六秀催官。
//   { long, xiang, water }（皆二十四山名）。
export function jingyin({ long = '乾', xiang = '甲', water = '坤' } = {}) {
	const items = [
		{ key: '龙', shan: long, yy: najiaYinYang(long) },
		{ key: '向', shan: xiang, yy: najiaYinYang(xiang) },
		{ key: '水', shan: water, yy: najiaYinYang(water) },
	];
	const valid = items.every((it)=>it.yy);
	const jing = valid && items.every((it)=>it.yy === items[0].yy);
	const liuxiu = items.filter((it)=>LIU_XIU.has(it.shan)).map((it)=>`${it.key}${it.shan}`);
	return {
		available: true, items, jing, pureType: valid ? items[0].yy : null,
		verdict: !valid
			? { text: '含无纳甲之位，请择二十四山', jx: 'neutral' }
			: (jing
				? { text: `龙向水俱净${items[0].yy}·清纯为吉（阳见阳/阴见阴）`, jx: 'good' }
				: { text: '阴阳驳杂·凶（宜龙向水同净）', jx: 'bad' }),
		liuxiu: liuxiu.length ? { list: liuxiu, text: '六秀（艮丙巽辛兑丁）峰水到位，催官催贵' } : null,
		note: '净阳:乾甲坤乙坎(子)癸申辰离(午)壬寅戌;净阴:艮丙巽辛震(卯)庚亥未兑(酉)丁巳丑;龙向水须同净',
	};
}
