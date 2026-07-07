// 宿名映射回归守卫:chart.fixedStarSu28 按升度排序(起点随宿度制漂,如 壁 起),
// 与 FULL_STELLAR 的固定 28 宿序(娄 起)位序不通用 —— 历史 bug 用 fixedStarSu28 位序直切
// FULL_STELLAR 导致「限度/度主」全盘错宿(age→箕 实为心 等)。此测锁死「按名映射」而非「按位序」。
import { moiraFullStellarByName, moiraStarHostByName, moiraBuildStellarRelations } from '../GuoLaoMoiraWheel';

describe('七政宿名按名映射(反 FULL_STELLAR 位序错宿 bug)', ()=>{
	test('fullStellarByName:宿短名 → 宿+五行 全名(28 宿首字互异,唯一命中)', ()=>{
		expect(moiraFullStellarByName('心')).toBe('心月');
		expect(moiraFullStellarByName('氐')).toBe('氐土');
		expect(moiraFullStellarByName('翼')).toBe('翼火');
		expect(moiraFullStellarByName('参')).toBe('参水');
		expect(moiraFullStellarByName('牛')).toBe('牛金');
		expect(moiraFullStellarByName('壁')).toBe('壁水'); // 壁=fixedStarSu28 常见首宿,历史错切成"娄金"
		expect(moiraFullStellarByName('奎')).toBe('奎木');
		expect(moiraFullStellarByName('角')).toBe('角木');
	});

	test('未知/空名回退原串(不抛)', ()=>{
		expect(moiraFullStellarByName('')).toBe('');
		expect(moiraFullStellarByName('無')).toBe('無');
	});

	test('starHostByName:度主=宿五行字(壁→水,不再被位序错切成 金)', ()=>{
		expect(moiraStarHostByName('壁')).toBe('水');
		expect(moiraStarHostByName('奎')).toBe('木');
		expect(moiraStarHostByName('心')).toBe('月');
		expect(moiraStarHostByName('氐')).toBe('土');
	});

	test('buildStellarRelations 度主按真实宿名取(fixedStarSu28 壁起序不再错切)', ()=>{
		// 合成 chart:fixedStarSu28 按真实后端顺序(升度、壁起),name=宿短名。
		const su = [
			{ name: '壁', ra: 10 }, { name: '奎', ra: 22 }, { name: '娄', ra: 34 },
			{ name: '胃', ra: 47 }, { name: '昴', ra: 59 }, { name: '毕', ra: 68 },
		];
		const chart = { fixedStarSu28: su, objects: [] };
		const rows = moiraBuildStellarRelations(chart);
		const byName = {};
		rows.forEach((r)=>{ byName[r.name] = r; });
		// 壁 的度主必须是"水"(壁水),历史 bug 会取 FULL_STELLAR[0]="娄金" → "金"(错)。
		expect(byName['壁'].host).toBe('水');
		expect(byName['奎'].host).toBe('木'); // 奎木
		expect(byName['娄'].host).toBe('金'); // 娄金
		expect(byName['胃'].host).toBe('土'); // 胃土
		// 反向断言:绝不等于「拿位序 idx 直切 FULL_STELLAR」的错值
		// idx0=壁 若错切 FULL_STELLAR[0]=娄金→金;这里必须是水,证明按名不按位。
		expect(byName['壁'].host).not.toBe('金');
	});
});
