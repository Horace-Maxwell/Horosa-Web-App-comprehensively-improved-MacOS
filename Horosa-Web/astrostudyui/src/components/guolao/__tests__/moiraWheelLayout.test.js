// 动态环布局契约:隐藏环折叠为零宽、可见环按权重铺满(无空带)、全开=历史 RING_POS 逐值一致。
import { MOIRA_HUB_POS, MOIRA_RING_BANDS, computeRingPositions, ringCollapsed } from '../moiraWheelLayout';

const LEGACY = [0.10, 0.22, 0.28, 0.34, 0.43, 0.45, 0.51, 0.53, 0.62, 0.77, 0.92, 0.95, 1.0];

function widths(pos){
	return pos.slice(1).map((p, i)=>p - pos[i]);
}

describe('moiraWheelLayout(动态环布局)', () => {
	test('全开 = 历史静态布局逐值一致(零回归锚)', () => {
		const pos = computeRingPositions({ birthGods: true, transitGods: true, ageRing: true });
		pos.forEach((p, i)=>expect(p).toBeCloseTo(LEGACY[i], 10));
	});

	test('任意开关组合:边界单调不减、首=0.10、可见末边界=1(无外空带)', () => {
		const flags = [true, false];
		flags.forEach((bg)=>flags.forEach((tg)=>flags.forEach((ar)=>{
			const pos = computeRingPositions({ birthGods: bg, transitGods: tg, ageRing: ar });
			expect(pos[0]).toBeCloseTo(MOIRA_HUB_POS, 12);
			for(let i = 1; i < pos.length; i++){
				expect(pos[i]).toBeGreaterThanOrEqual(pos[i - 1] - 1e-12);
			}
			expect(pos[pos.length - 1]).toBeCloseTo(1, 10);
			// 无中间空带:每个隐藏带宽=0,每个可见带宽>0
			widths(pos).forEach((w, i)=>{
				const band = MOIRA_RING_BANDS[i];
				const on = !band.toggle || { birthGods: bg, transitGods: tg, ageRing: ar }[band.toggle] !== false;
				if(on){
					expect(w).toBeGreaterThan(0.005);
				}else{
					expect(w).toBeLessThan(0.0005);
				}
			});
		})));
	});

	test('神煞带不随圈开关折叠(Moira 语义:关圈=字消失带留白,几何恒定)', () => {
		const on = computeRingPositions({});
		const off = computeRingPositions({ birthGods: false, transitGods: false });
		on.forEach((v, i)=>expect(off[i]).toBeCloseTo(v, 6));
	});

	test('ringCollapsed 判零宽带(half 表内圈 nowPlanets/tickUp 折叠)', () => {
		const pos = computeRingPositions({}, 'half');
		expect(ringCollapsed(pos, 4)).toBe(true);
		expect(ringCollapsed(pos, 5)).toBe(true);
		expect(ringCollapsed(pos, 1)).toBe(false);
	});
});


describe('half(单盘)模式基准', () => {
	test('全开边界=Moira half_ring_pos 逐值(零宽带折叠)', () => {
		const { computeRingPositions } = require('../moiraWheelLayout');
		const pos = computeRingPositions({}, 'half');
		const expect13 = [0.12, 0.30, 0.36, 0.44, 0.44, 0.44, 0.50, 0.53, 0.62, 0.77, 0.92, 0.95, 1.0];
		pos.forEach((v, i)=>expect(v).toBeCloseTo(expect13[i], 6));
	});

	test('full 缺省不变(零回归锚)', () => {
		const { computeRingPositions } = require('../moiraWheelLayout');
		const pos = computeRingPositions({});
		const legacy = [0.10, 0.22, 0.28, 0.34, 0.43, 0.45, 0.51, 0.53, 0.62, 0.77, 0.92, 0.95, 1.0];
		pos.forEach((v, i)=>expect(v).toBeCloseTo(legacy[i], 6));
	});
});
