// 🔴 地点名透传金标:经纬度查找选点 → rec.name → pos 字段(显示于「地点」+ 随盘储存 + 进 AI 快照)。
// 语义单一真值:name===undefined 不动 pos(仅改时区保名);name==='' 据实清空;name='X' 回填。
import { geoNameFieldPatch, geoNameRawPatch, applyGeoNameToFields } from '../geoName';

describe('geoNameFieldPatch(fields 形态 { pos: { value } })', ()=>{
	test('有地名 → { pos: { value } }', ()=>{
		expect(geoNameFieldPatch({ name: '上海市' })).toEqual({ pos: { value: '上海市' } });
	});
	test('空串地名(地图裸点逆地理失败/手输经纬)→ { pos: { value: "" } }(据实清空)', ()=>{
		expect(geoNameFieldPatch({ name: '' })).toEqual({ pos: { value: '' } });
	});
	test('无 name 键(仅改时区)→ {}(不动 pos,保留旧地名)', ()=>{
		expect(geoNameFieldPatch({ lat: 31, lng: 121 })).toEqual({});
		expect(geoNameFieldPatch({})).toEqual({});
		expect(geoNameFieldPatch(null)).toEqual({});
	});
	test('非串地名兜底为空串(不抛)', ()=>{
		expect(geoNameFieldPatch({ name: 123 })).toEqual({ pos: { value: '123' } });
	});
});

describe('geoNameRawPatch(raw 形态 { pos })', ()=>{
	test('有地名 → { pos }', ()=>{
		expect(geoNameRawPatch({ name: '黄浦区' })).toEqual({ pos: '黄浦区' });
	});
	test('空串 → { pos: "" }', ()=>{
		expect(geoNameRawPatch({ name: '' })).toEqual({ pos: '' });
	});
	test('无 name → {}', ()=>{
		expect(geoNameRawPatch({ lat: 1 })).toEqual({});
	});
});

describe('applyGeoNameToFields(直改 flds.pos.value)', ()=>{
	test('flds.pos 存在 + 有地名 → 就地写入', ()=>{
		const flds = { pos: { value: '旧地名' }, lat: { value: 'n31' } };
		applyGeoNameToFields(flds, { name: '成都市' });
		expect(flds.pos.value).toBe('成都市');
	});
	test('无 name 键 → 不动 pos(保名)', ()=>{
		const flds = { pos: { value: '旧地名' } };
		applyGeoNameToFields(flds, { lat: 1 });
		expect(flds.pos.value).toBe('旧地名');
	});
	test('空串 → 清空(据实)', ()=>{
		const flds = { pos: { value: '旧地名' } };
		applyGeoNameToFields(flds, { name: '' });
		expect(flds.pos.value).toBe('');
	});
	test('flds 无 pos 字段 → 跳过不抛(不新建)', ()=>{
		const flds = { lat: { value: 'n31' } };
		expect(()=>applyGeoNameToFields(flds, { name: '西安市' })).not.toThrow();
		expect(flds.pos).toBeUndefined();
	});
});
