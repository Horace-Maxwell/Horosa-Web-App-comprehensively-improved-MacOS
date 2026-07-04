// 纳气盘法增强规则（荀爽法）：破局危害 / 卦位家人 / 龙虎法灶台 / 吉凶评分 / 缓解方案。
// 纯数据 + 纯函数，无 DOM、可单测。判读始终由引擎用 SECTORS 数学产出后传入。
// 源：荀爽纳气盘法。

// 后天八卦家人 —— 破局落在哪个卦位扇区 → 危害该家人。键为 SECTORS[*].num。
export const PALACE_FAMILY = {
	6: '父辈/男主人', // 西北乾
	1: '次子',        // 北坎
	8: '三子',        // 东北艮
	3: '长子',        // 东震
	4: '长女',        // 东南巽
	9: '次女',        // 南离
	2: '母辈/女主人', // 西南坤
	7: '三女',        // 西兑
};

// 破局通用层。score 用于评分累减（锚点：一处破水 + 充足在位物 ≈ 95 分）。
export const HARM_MAP = {
	'break-wind': { label: '破气', affect: '主人气运受压、事业推进受阻、决断力下降', score: -15, remedyKey: 'break-wind' },
	'break-water': { label: '破水', affect: '感情易波动、易因酒色耗财、人际是非', score: -15, remedyKey: 'break-water' },
	'double-bath': { label: '双卫压气', affect: '家中气场受压明显、健康与运势同步走低', score: -12, remedyKey: 'double-bath' },
};

export const REMEDY_LIB = {
	'break-water': ['将水类设施移出该气位扇区', '若不便移动，常关该处门、保持通风'],
	'break-wind': ['将该气位物移至气位扇区', '加强采光与空气流通'],
	'double-bath': ['两处卫生间择一停用', '常关卫生间门、常开小窗排气'],
	'dragon-tiger-bad': ['调整水槽方位至灶台右侧', '或将灶台移位，避开水火直冲'],
};

// 单个「位置冲突」标记 → 危害对象（通用层 + 卦位家人层）。category===actual 时无破局。
export function harmForMarker(category, actual, sectorNum) {
	if (!category || !actual || category === 'neutral' || category === actual) return null;
	const key = category === 'wind' ? 'break-wind' : 'break-water'; // 气物落水位=破气；水物落气位=破水
	const base = HARM_MAP[key];
	const family = PALACE_FAMILY[sectorNum] || '';
	return {
		key,
		label: base.label,
		score: base.score,
		remedyKey: base.remedyKey,
		affect: family ? `${base.affect}（尤不利${family}）` : base.affect,
	};
}

// 龙虎法灶台四格局表。level：1 最差 … 5 最佳。
export const DT = {
	LEFT_PARALLEL: { pattern: '左平行', level: 2, text: '格局不稳，财气进出反复。', remedyKey: 'dragon-tiger-bad' },
	LEFT_VERTICAL: { pattern: '左垂直', level: 1, text: '水火相刑，最为不利，主财损与口舌，宜调整水槽或灶位。', remedyKey: 'dragon-tiger-bad' },
	RIGHT_VERTICAL: { pattern: '右垂直', level: 4, text: '白虎低头，利投资与进取财。', remedyKey: null },
	RIGHT_PARALLEL: { pattern: '右平行', level: 5, text: '格局最佳，大利偏财。', remedyKey: null },
};

// 龙虎法：左右以「灶口朝向」（下厨者面对方向）为基准。stove/sink 为图像坐标 {x,y}；facingAngle 为指北角(0-360)。
// 屏幕/图像坐标 y 向下：compass 0(北)=上=(0,-1)，compass 90(东)=右=(1,0)。
export function evalDragonTiger(stove, sink, facingAngle) {
	if (!stove || !sink || facingAngle === null || facingAngle === undefined || Number.isNaN(facingAngle)) return null;
	const th = (facingAngle * Math.PI) / 180;
	const facingVec = { x: Math.sin(th), y: -Math.cos(th) };          // 灶口前方
	const rightVec = { x: -facingVec.y, y: facingVec.x };            // 顺转 90° = 下厨者右手 = 白虎侧
	const v = { x: sink.x - stove.x, y: sink.y - stove.y };
	const forward = v.x * facingVec.x + v.y * facingVec.y;          // 水火前后对冲轴
	const right = v.x * rightVec.x + v.y * rightVec.y;              // >0 白虎(右) / <0 青龙(左)
	const isParallel = Math.abs(right) >= Math.abs(forward);        // 横向占优=并排(平行)
	const isRight = right > 0;
	if (!isRight && isParallel) return DT.LEFT_PARALLEL;
	if (!isRight && !isParallel) return DT.LEFT_VERTICAL;
	if (isRight && !isParallel) return DT.RIGHT_VERTICAL;
	return DT.RIGHT_PARALLEL;
}

// 吉凶评分 0-100。锚点：一处破水(-15) + 充足在位物(+10 封顶) = 95。
export function scoreNaqi({ windOk = 0, waterOk = 0, harms = [], dragonTiger = null } = {}) {
	let s = 100;
	(harms || []).forEach((h) => { s += (h && h.score) || 0; });
	s += Math.min((windOk || 0) + (waterOk || 0), 10);
	if (dragonTiger && dragonTiger.level) s += (dragonTiger.level - 3) * 2;
	return Math.max(0, Math.min(100, Math.round(s)));
}

export function gradeOf(score) {
	if (score >= 85) return '吉';
	if (score >= 60) return '平';
	return '慎';
}
