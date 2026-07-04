// 乾坤国宝（龙门八大局）· 九大水位（先天/后天/案劫/天劫/地刑/宾/客/辅/正窍）+ 来去水断 + 合局。
// 先后天位移植 golden(golden 基准)字节级;天劫=向左前·地刑=向右前(几何确定);宾/客/辅/正窍 注「需按龙门八局图校」。
import { qkgbPositions, qkgbFullPositions } from './liqiCore';
import { POS_NAME, OPP_GONG } from './fengshuiData';

// 位 → 水位登记 key（左栏受控）。
const POS_KEY = {
	先天位: 'xianTian', 后天位: 'houTian', 案劫位: 'anJie', 天劫位: 'tianJie', 地刑位: 'diXing',
	宾位: 'bin', 客位: 'ke', 辅卦位: 'fu', 正窍位: 'zhengQiao',
};

// 来去水断（7.B.9）：want='come' 喜来水;'go' 喜去水;'none'(地刑) 忌一切水。
function verdictOf(want, water) {
	if (want === 'come') {
		if (water === 'come') { return { result: '得来水·旺（合）', jx: 'good' }; }
		if (water === 'go') { return { result: '反去水·失（损）', jx: 'bad' }; }
		return { result: '宜见来水', jx: 'neutral' };
	}
	if (want === 'go') {
		if (water === 'go') { return { result: '去水关锁·合', jx: 'good' }; }
		if (water === 'come') { return { result: '来水冲·忌', jx: 'bad' }; }
		return { result: '宜去水关锁', jx: 'neutral' };
	}
	// 地刑 want='none'（来去水皆刑伤，方向不同但同凶）。
	if (water === 'come') { return { result: '来水刑伤·妻财两空', jx: 'bad' }; }
	if (water === 'go') { return { result: '去水破·妻财两空', jx: 'bad' }; }
	return { result: '宜无水（静）', jx: 'neutral' };
}

// 乾坤国宝排盘：坐山卦 → 九水位 + 来去水断 + 合局。
//   waters: {posKey: 'come'|'go'|''}。
export function qiankun({ zuoGua, waters = {} } = {}) {
	const full = qkgbFullPositions(zuoGua);
	const base = qkgbPositions(zuoGua);
	if (!full || !base) { return { available: false }; }

	const positions = full.list.map((p)=>{
		const key = POS_KEY[p.name];
		const water = waters[key] || '';
		const v = verdictOf(p.want, water);
		return {
			key, name: p.name, role: p.role, pos: p.gong, posName: p.posName,
			tuFig: !!p.tuFig, want: p.want, water, result: v.result, jx: v.jx,
		};
	});

	// 合局（7.B.10）：先天+后天得来水、案劫+天劫得去水、地刑无水。
	const byName = (n)=>positions.find((p)=>p.name === n);
	const heJu = byName('先天位').water === 'come' && byName('后天位').water === 'come'
		&& byName('案劫位').water === 'go' && byName('天劫位').water === 'go'
		&& byName('地刑位').water !== 'come' && byName('地刑位').water !== 'go';

	const anJiePos = OPP_GONG[base.houtianFangPos] || base.houtianFangPos;
	return {
		available: true, zuoGua,
		houtianFang: base.houtianFang,
		xianTian: base.xianTianWei, houTian: base.houTianWei, anJie: POS_NAME[anJiePos],
		xianTianPos: base.xianTianWeiPos, houTianPos: base.houTianWeiPos, anJiePos,
		positions, heJu,
		note: '先后天位字节级确定;天劫=向左前·地刑=向右前(几何);宾/客/辅/正窍 依龙门八局图(门派)',
	};
}
