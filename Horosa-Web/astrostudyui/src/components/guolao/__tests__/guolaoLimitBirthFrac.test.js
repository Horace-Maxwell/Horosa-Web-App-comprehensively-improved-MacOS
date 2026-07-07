// 🔴 birthFrac(公历元旦偏移)金标:照 Moira getLimitDegree `val = age − 1 − birthFrac`(减法)。
// 用户实测 DHX(2006-10-04,birthFrac≈0.758,今宿命度 242.46°):Moira「11岁」=星阙旧「10岁」;
// 命度应落 10.78 岁(Moira「10岁尾端」),旧无 birthFrac 落 10.02 岁(前半段)。此测锁死方向与数值。
import { moiraLimitAnchor, moiraLimitAgeOffset, moiraLimitDegreeForAge, moiraBirthYearFraction } from '../GuoLaoMoiraWheel';

// 逆算:给定度偏移(自锚点)与 birthFrac,反解虚岁 —— 复刻 wheel 内 limitAgeAtOffset 逻辑做断言基准。
function ageAtOffset(life, offset, birthFrac, childBase){
	// 单宫近似:此盘命度在命宫内,首宫年数 = base + 命度宫内度/3。
	const inSign = ((life % 30) + 30) % 30;
	const childYear = (childBase === 10 ? 10 : 9) + inSign / 3;
	const years = offset / 30 * childYear; // 命宫内线性
	return 1 + years + birthFrac;
}

describe('birthFrac 减法金标(照 Moira,DHX 2006-10-04)', ()=>{
	const life = 242.46;       // 今宿命度
	const bf = 0.758;          // 出生 10/4 → 公历元旦偏移
	const anchor = 270;        // floor(242.46/30)*30+30

	test('birthFrac=0 零回归:1 岁=锚点', ()=>{
		expect(moiraLimitAnchor(life)).toBe(anchor);
		expect(moiraLimitDegreeForAge(life, 1)).toBeCloseTo(anchor, 6);   // 缺省 birthFrac=0
		expect(moiraLimitDegreeForAge(life, 1, 0, 9)).toBeCloseTo(anchor, 6);
	});

	test('birthFrac 为减法:offset(1,bf) = 30·(−bf)/childYear(负,度贴近锚点上方)', ()=>{
		const childYear = 9 + (life % 30) / 3; // 9.82
		expect(moiraLimitAgeOffset(life, 1, bf, 9)).toBeCloseTo(30 * (-bf) / childYear, 4); // ≈ -2.316
		expect(moiraLimitAgeOffset(life, 1, bf, 9)).toBeLessThan(0);
	});

	test('命度(242.46°)落 10.78 岁(Moira 10岁尾端),非旧 10.02', ()=>{
		const off = anchor - life; // 27.54°,命度自锚点的偏移
		const ageNew = ageAtOffset(life, off, bf, 9);
		const ageOld = ageAtOffset(life, off, 0, 9);
		expect(ageNew).toBeCloseTo(10.77, 1);   // 含 birthFrac → 10 岁尾端
		expect(ageOld).toBeCloseTo(10.02, 1);   // 旧无 birthFrac → 前半段
		expect(ageNew - ageOld).toBeCloseTo(bf, 6); // 差值恰 = birthFrac
	});

	test('同一环位置:含 birthFrac 的岁数 = 不含的岁数 + birthFrac(用户 11 vs 10)', ()=>{
		// 星阙旧「10 岁」的度位置,新算法应标为「10.76 岁」≈ Moira 11 岁
		const degAt10Old = moiraLimitDegreeForAge(life, 10, 0, 9);
		// 反解:该度在新算法(含 bf)对应虚岁
		const offAt = anchor - degAt10Old;
		const ageNew = ageAtOffset(life, offAt, bf, 9);
		expect(ageNew).toBeCloseTo(10 + bf, 1); // ≈10.76,进入虚岁 11
	});
});

// 🔴 回归:birthFrac 渲染时静默算成 0 的真实病根 —— birthYearFraction 只读 chart.params.date,
// 但 wheel 收到的 chart 常无 params(root.params 缺→graft 落空)、fields.date.value 也非 moment。
// 修:加读 chart.date(后端排盘产出 {jd, utcoffset})。此测锁死「有 chart.date 即算出正确 birthFrac」。
describe('birthYearFraction 从 chart.date.jd 取出生日(修复渲染时 birthFrac=0)', ()=>{
	// DHX 2006-10-04 09:58,tz+8 → jd(UT)。365.25 天基准的元旦偏移 ≈ 0.757。
	const chartDate = { jd: 2454012.581944444, utcoffset: { value: 8 }, time: { value: 9.9667 } };

	test('chart 无 params、fields 非 moment,但有 chart.date → birthFrac≈0.757(非 0)', ()=>{
		const frac = moiraBirthYearFraction({ params: null, date: chartDate }, { date: { value: {} } }, 'gregorian');
		expect(frac).toBeGreaterThan(0.74);
		expect(frac).toBeLessThan(0.77);
	});

	test('chart.params.date 主路仍优先(存在时不被 chart.date 覆盖)', ()=>{
		const frac = moiraBirthYearFraction({ params: { date: '2006/1/1', time: '00:00' }, date: chartDate }, undefined, 'gregorian');
		expect(frac).toBeCloseTo(0, 3);   // 元旦 00:00 出生 → 偏移≈0(证明走了 params 主路,非 chart.date 的 0.757)
	});

	test('三路皆缺 → 返回 0(不抛)', ()=>{
		expect(moiraBirthYearFraction({}, undefined, 'gregorian')).toBe(0);
		expect(moiraBirthYearFraction({ date: {} }, undefined, 'gregorian')).toBe(0);
	});

	test('修复效果:base10 + 该 birthFrac → 寅卯宫界(offset=30)落 12 岁 cell(对齐 Moira),缺 birthFrac 落 11', ()=>{
		const life = 240.9;                 // 命宫寅内 0.9°(childYear base10 = 10.3)
		const bf = moiraBirthYearFraction({ date: chartDate }, undefined, 'gregorian');
		const childYear = 10 + (life % 30) / 3; // 10.3
		// 宫界 offset=30 处的累计 val = childYear;所在岁 cell:val∈[N-1-bf, N-bf]
		const cellWith = Math.ceil(childYear + bf);   // 含 birthFrac
		const cellWithout = Math.ceil(childYear);      // 缺 birthFrac(旧 bug)
		expect(cellWith).toBe(12);      // 对齐 Moira
		expect(cellWithout).toBe(11);   // 旧现象
	});
});
