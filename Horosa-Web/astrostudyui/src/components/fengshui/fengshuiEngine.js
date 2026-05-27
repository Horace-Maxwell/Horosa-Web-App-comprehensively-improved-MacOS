// 风水纳气盘引擎（从 public/fengshui/app.js 移植为框架无关模块）。
// 由 React 组件持有：构造时传入 canvas 与 onChange(viewModel) 回调；
// 所有画布绘制/几何/判定/历史/导出/快照逻辑在此，React 只渲染 Antd 控件并调用本类方法。
// 注意：画布按工作区尺寸铺满、户型图居中绘制，纳气盘可延伸到图外空白区而不被裁切。

export const SECTORS = [
	{ num: 1, name: '北(坎)', start: 337.5, end: 22.5 },
	{ num: 8, name: '东北(艮)', start: 22.5, end: 67.5 },
	{ num: 3, name: '东(震)', start: 67.5, end: 112.5 },
	{ num: 4, name: '东南(巽)', start: 112.5, end: 157.5 },
	{ num: 9, name: '南(离)', start: 157.5, end: 202.5 },
	{ num: 2, name: '西南(坤)', start: 202.5, end: 247.5 },
	{ num: 7, name: '西(兑)', start: 247.5, end: 292.5 },
	{ num: 6, name: '西北(乾)', start: 292.5, end: 337.5 },
];

export const MARKER_TYPES = [
	{ id: 'entryDoor', label: '入户门', short: '门', category: 'wind', color: '#c34f3a' },
	{ id: 'window', label: '窗户', short: '窗', category: 'wind', color: '#b05445' },
	{ id: 'balcony', label: '阳台', short: '阳', category: 'wind', color: '#c76a3c' },
	{ id: 'stove', label: '灶台', short: '灶', category: 'wind', color: '#d26a4e' },
	{ id: 'sofa', label: '沙发', short: '沙', category: 'wind', color: '#b76b58' },
	{ id: 'bed', label: '床', short: '床', category: 'wind', color: '#a8615e' },
	{ id: 'desk', label: '书桌', short: '桌', category: 'wind', color: '#9e5a6a' },
	{ id: 'altar', label: '神龛', short: '龛', category: 'wind', color: '#8c4e44' },
	{ id: 'petBed', label: '宠物床', short: '宠', category: 'wind', color: '#a96a5b' },
	{ id: 'sink', label: '水槽', short: '槽', category: 'water', color: '#2b5ea0' },
	{ id: 'washbasin', label: '洗手池', short: '洗', category: 'water', color: '#2e6ea7' },
	{ id: 'toilet', label: '马桶', short: '厕', category: 'water', color: '#2f5c88' },
	{ id: 'drain', label: '下水管', short: '管', category: 'water', color: '#2a5a93' },
	{ id: 'washingMachine', label: '洗衣机', short: '机', category: 'water', color: '#2f6f9c' },
	{ id: 'bathroom', label: '卫生间', short: '卫', category: 'water', color: '#275783' },
	{ id: 'custom', label: '自定义', short: '标', category: 'neutral', color: '#6b655a' },
];

const WIND_NUMS = new Set([6, 7, 8, 9]);
const WATER_NUMS = new Set([1, 2, 3, 4]);
const WIND_COLOR = 'rgb(180, 30, 30)';
const WATER_COLOR = 'rgb(20, 30, 100)';
const SNAP_TOLERANCE = 8;
const HISTORY_LIMIT = 80;

const TIPS = [
	'楼门朝向以卫星地图为准，门内朝门外，记录真北角度。',
	'家门方向在户型图上画出，令两箭头平行后再判定。',
	'房屋主体以矩形为准，扩大范围导致空缺大于实体时不再扩大。',
	'盘心放在太极点，八方颜色与数字即可判断气位与水位。',
];
const ADVICE = '气位建议放置：门、窗、灶台、沙发、床、书桌、神龛、宠物床等。水位建议放置：水槽、洗手池、马桶、下水管、洗衣机、厕所等。';

function rotatePoint(point, origin, angleDeg) {
	const rad = (angleDeg * Math.PI) / 180;
	const dx = point.x - origin.x;
	const dy = point.y - origin.y;
	return {
		x: origin.x + dx * Math.cos(rad) - dy * Math.sin(rad),
		y: origin.y + dx * Math.sin(rad) + dy * Math.cos(rad),
	};
}

function angleInSector(angle, start, end) {
	if (start < end) return angle >= start && angle < end;
	return angle >= start || angle < end;
}

function formatAngle(value) {
	if (value === null || value === undefined || Number.isNaN(value)) return '--';
	return `${Math.round(value * 10) / 10}°`;
}

export default class FengShuiEngine {
	constructor(canvas, options = {}) {
		this.canvas = canvas;
		this.ctx = canvas.getContext('2d');
		this.onChange = options.onChange || (() => {});

		this.img = new Image();
		this.imgLoaded = false;
		this.scale = 1;
		this.viewScale = 1;
		this.viewOffset = { x: 0, y: 0 };

		this.rect = { x: 0, y: 0, w: 0, h: 0, rotation: 0, active: false };
		this.mode = 'none';
		this.isDragging = false;
		this.startPoint = { x: 0, y: 0 };
		this.activeHandle = null;
		this.initialRectState = null;
		this.dragMarkerId = null;
		this.panStart = null;
		this.panMode = false;
		this.snapEnabled = true;

		this.unitAzimuth = null;
		this.doorImageAngle = null;
		this.globalAlpha = 0.3;
		this.diskScale = 1;
		this.diskCenterMode = 'house';
		this.customCenter = null;
		this.periodMode = 'current';

		this.markers = [];
		this.selectedMarkerId = null;
		this.markerIdSeed = 1;
		this.currentFilter = 'all';
		this.markerType = MARKER_TYPES[0].id;

		this.status = '请上传户型图开始。';

		this.historyStack = [];
		this.redoStack = [];
		this.historyLocked = false;
		this.historyTimer = null;

		this._onMouseDown = this._onMouseDown.bind(this);
		this._onMouseMove = this._onMouseMove.bind(this);
		this._onMouseUp = this._onMouseUp.bind(this);

		canvas.addEventListener('mousedown', this._onMouseDown);
		canvas.addEventListener('mousemove', this._onMouseMove);
		window.addEventListener('mouseup', this._onMouseUp);

		this.initHistory();
		this.emit();
	}

	destroy() {
		this.canvas.removeEventListener('mousedown', this._onMouseDown);
		this.canvas.removeEventListener('mousemove', this._onMouseMove);
		window.removeEventListener('mouseup', this._onMouseUp);
		if (this.historyTimer) clearTimeout(this.historyTimer);
	}

	// ── 视图模型 ───────────────────────────────────────────────
	emit() {
		this.onChange(this.getViewModel());
	}

	getViewModel() {
		const markers = this.markers.map((m) => {
			const ev = this.evaluateMarker(m);
			return {
				id: m.id,
				label: m.label,
				short: m.short,
				category: m.category,
				color: m.color,
				sector: ev.sector ? { num: ev.sector.num, name: ev.sector.name } : null,
				actual: ev.actual,
				ok: ev.ok,
			};
		});
		const stats = { windOk: 0, waterOk: 0, windBad: 0, waterBad: 0, unknown: 0 };
		this.markers.forEach((m) => {
			const ev = this.evaluateMarker(m);
			if (!ev.sector) stats.unknown += 1;
			else if (m.category === 'wind') ev.ok ? (stats.windOk += 1) : (stats.windBad += 1);
			else if (m.category === 'water') ev.ok ? (stats.waterOk += 1) : (stats.waterBad += 1);
		});
		const summary = this.markers.length
			? `气位正确 ${stats.windOk} 项，气位冲突 ${stats.windBad} 项；水位正确 ${stats.waterOk} 项，水位冲突 ${stats.waterBad} 项；未定位 ${stats.unknown} 项。`
			: '';
		return {
			status: this.status,
			imgLoaded: this.imgLoaded,
			rectActive: this.rect.active,
			rectRotation: this.rect.rotation || 0,
			unitAzimuth: this.unitAzimuth,
			doorImageAngle: this.doorImageAngle,
			unitAngleText: formatAngle(this.unitAzimuth),
			doorAngleText: formatAngle(this.doorImageAngle),
			diskRotationText: formatAngle(this.getDiskRotation()),
			globalAlpha: this.globalAlpha,
			diskScale: this.diskScale,
			diskCenterMode: this.diskCenterMode,
			periodMode: this.periodMode,
			snapEnabled: this.snapEnabled,
			panMode: this.panMode,
			zoomPct: Math.round(this.viewScale * 100),
			markerType: this.markerType,
			currentFilter: this.currentFilter,
			selectedMarkerId: this.selectedMarkerId,
			markers,
			summary,
			canUndo: this.historyStack.length >= 2,
			canRedo: this.redoStack.length > 0,
			snapshotText: this.buildAiSnapshotText(),
		};
	}

	setStatus(text) {
		this.status = text;
	}

	// ── 历史（撤销/重做）─────────────────────────────────────────
	captureState() {
		return {
			rect: { ...this.rect },
			markers: this.markers.map((m) => ({ ...m })),
			unitAzimuth: this.unitAzimuth,
			doorImageAngle: this.doorImageAngle,
			globalAlpha: this.globalAlpha,
			diskScale: this.diskScale,
			diskCenterMode: this.diskCenterMode,
			customCenter: this.customCenter ? { ...this.customCenter } : null,
			periodMode: this.periodMode,
			selectedMarkerId: this.selectedMarkerId,
			markerIdSeed: this.markerIdSeed,
		};
	}

	applySnapshot(s) {
		if (!s) return;
		this.historyLocked = true;
		this.rect = { ...s.rect };
		this.markers = s.markers.map((m) => ({ ...m }));
		this.unitAzimuth = s.unitAzimuth;
		this.doorImageAngle = s.doorImageAngle;
		this.globalAlpha = s.globalAlpha;
		this.diskScale = s.diskScale;
		this.diskCenterMode = s.diskCenterMode;
		this.customCenter = s.customCenter ? { ...s.customCenter } : null;
		this.periodMode = s.periodMode;
		this.selectedMarkerId = s.selectedMarkerId ?? null;
		this.markerIdSeed = s.markerIdSeed ?? this.markers.reduce((mx, m) => Math.max(mx, m.id), 0) + 1;
		this.drawAll();
		this.historyLocked = false;
	}

	initHistory() {
		this.historyStack = [this.captureState()];
		this.redoStack = [];
	}

	pushHistory() {
		if (this.historyLocked) return;
		this.historyStack.push(this.captureState());
		if (this.historyStack.length > HISTORY_LIMIT) this.historyStack.shift();
		this.redoStack = [];
	}

	scheduleHistoryPush() {
		if (this.historyLocked) return;
		clearTimeout(this.historyTimer);
		this.historyTimer = setTimeout(() => this.pushHistory(), 350);
	}

	undo() {
		if (this.historyStack.length < 2) return;
		const cur = this.historyStack.pop();
		this.redoStack.push(cur);
		this.applySnapshot(this.historyStack[this.historyStack.length - 1]);
		this.setStatus('已撤销上一步。');
		this.emit();
	}

	redo() {
		if (this.redoStack.length === 0) return;
		const next = this.redoStack.pop();
		this.historyStack.push(next);
		this.applySnapshot(next);
		this.setStatus('已重做一步。');
		this.emit();
	}

	// ── 几何 ───────────────────────────────────────────────────
	getCombinedScale() {
		return this.scale * this.viewScale;
	}

	getRectCenter() {
		return { x: this.rect.x + this.rect.w / 2, y: this.rect.y + this.rect.h / 2 };
	}

	getMousePos(evt) {
		const r = this.canvas.getBoundingClientRect();
		return { x: evt.clientX - r.left, y: evt.clientY - r.top };
	}

	screenToImage(pos) {
		const c = this.getCombinedScale();
		return { x: (pos.x - this.viewOffset.x) / c, y: (pos.y - this.viewOffset.y) / c };
	}

	getDiskRotation() {
		if (this.unitAzimuth === null || this.doorImageAngle === null) return 0;
		if (Number.isNaN(this.unitAzimuth) || Number.isNaN(this.doorImageAngle)) return 0;
		return this.doorImageAngle - this.unitAzimuth;
	}

	isWindSector(num) {
		if (this.periodMode === 'current') return WIND_NUMS.has(num);
		return WATER_NUMS.has(num);
	}

	getDiskCenter() {
		if (!this.rect.active) return null;
		if (this.diskCenterMode === 'house') return this.getRectCenter();
		if (this.diskCenterMode === 'custom') return this.customCenter || this.getRectCenter();
		if (this.diskCenterMode === 'marker') {
			const m = this.markers.find((x) => x.id === this.selectedMarkerId);
			return m ? { x: m.x, y: m.y } : this.getRectCenter();
		}
		if (this.diskCenterMode === 'door') {
			const m = this.markers.find((x) => x.type === 'entryDoor');
			return m ? { x: m.x, y: m.y } : this.getRectCenter();
		}
		return this.getRectCenter();
	}

	getMaxDiskRadius(center) {
		if (!this.rect.active) return 0;
		const rc = this.getRectCenter();
		const hw = this.rect.w / 2;
		const hh = this.rect.h / 2;
		const corners = [
			{ x: rc.x - hw, y: rc.y - hh },
			{ x: rc.x + hw, y: rc.y - hh },
			{ x: rc.x + hw, y: rc.y + hh },
			{ x: rc.x - hw, y: rc.y + hh },
		];
		let max = 0;
		corners.forEach((c) => {
			const r = rotatePoint(c, rc, this.rect.rotation);
			const d = Math.hypot(r.x - center.x, r.y - center.y);
			if (d > max) max = d;
		});
		return max;
	}

	snapPointToRect(pos) {
		if (!this.snapEnabled || !this.rect.active) return pos;
		const tol = SNAP_TOLERANCE / this.getCombinedScale();
		const center = this.getRectCenter();
		const local = rotatePoint(pos, center, -this.rect.rotation);
		let lx = local.x;
		let ly = local.y;
		const hw = this.rect.w / 2;
		const hh = this.rect.h / 2;
		[center.x - hw, center.x, center.x + hw].forEach((line) => {
			if (Math.abs(lx - line) <= tol) lx = line;
		});
		[center.y - hh, center.y, center.y + hh].forEach((line) => {
			if (Math.abs(ly - line) <= tol) ly = line;
		});
		return rotatePoint({ x: lx, y: ly }, center, this.rect.rotation);
	}

	snapRectToImage() {
		if (!this.snapEnabled || !this.imgLoaded) return;
		if (Math.abs(this.rect.rotation) > 0.5) return;
		if (this.rect.w <= 0 || this.rect.h <= 0) return;
		const tol = SNAP_TOLERANCE / this.getCombinedScale();
		const cx = [
			{ edge: this.rect.x, target: 0, offset: 0 },
			{ edge: this.rect.x + this.rect.w, target: this.img.width, offset: this.rect.w },
			{ edge: this.rect.x + this.rect.w / 2, target: this.img.width / 2, offset: this.rect.w / 2 },
		];
		const cy = [
			{ edge: this.rect.y, target: 0, offset: 0 },
			{ edge: this.rect.y + this.rect.h, target: this.img.height, offset: this.rect.h },
			{ edge: this.rect.y + this.rect.h / 2, target: this.img.height / 2, offset: this.rect.h / 2 },
		];
		cx.forEach((c) => { if (Math.abs(c.edge - c.target) <= tol) this.rect.x = c.target - c.offset; });
		cy.forEach((c) => { if (Math.abs(c.edge - c.target) <= tol) this.rect.y = c.target - c.offset; });
	}

	// ── 画布尺寸：铺满工作区 + 户型图居中（纳气盘可越出图边不被裁）──
	resize() {
		const host = this.canvas.parentElement;
		if (!host) return;
		const w = Math.max(320, host.clientWidth);
		const h = Math.max(320, host.clientHeight);
		this.canvas.width = w;
		this.canvas.height = h;
		if (this.imgLoaded) {
			this.scale = Math.min((w * 0.92) / this.img.width, (h * 0.92) / this.img.height);
			this.recenter();
		}
		this.drawAll();
	}

	recenter() {
		const c = this.getCombinedScale();
		this.viewOffset = {
			x: (this.canvas.width - this.img.width * c) / 2,
			y: (this.canvas.height - this.img.height * c) / 2,
		};
	}

	setViewScale(newScale, anchor) {
		const clamped = Math.max(0.4, Math.min(3.0, newScale));
		const combined = this.getCombinedScale();
		const nextCombined = this.scale * clamped;
		const point = anchor || { x: this.canvas.width / 2, y: this.canvas.height / 2 };
		const imgX = (point.x - this.viewOffset.x) / combined;
		const imgY = (point.y - this.viewOffset.y) / combined;
		this.viewScale = clamped;
		this.viewOffset = { x: point.x - imgX * nextCombined, y: point.y - imgY * nextCombined };
		this.drawAll();
		this.emit();
	}

	zoomIn() { this.setViewScale(this.viewScale * 1.1); }
	zoomOut() { this.setViewScale(this.viewScale / 1.1); }
	resetView() { this.viewScale = 1; this.recenter(); this.drawAll(); this.emit(); }

	// ── 绘制 ───────────────────────────────────────────────────
	drawAll() {
		const { ctx, canvas } = this;
		ctx.clearRect(0, 0, canvas.width, canvas.height);
		if (!this.imgLoaded) return;
		const c = this.getCombinedScale();
		ctx.drawImage(this.img, this.viewOffset.x, this.viewOffset.y, this.img.width * c, this.img.height * c);
		if (this.rect.w !== 0 && this.rect.h !== 0) this.drawRotatedRect(ctx, c, this.viewOffset);
		if (this.rect.active) this.drawNaQiDisk(ctx, c, this.viewOffset);
		this.drawMarkers(ctx, c, this.viewOffset);
	}

	drawRotatedRect(ctx, sf, off) {
		const center = this.getRectCenter();
		ctx.save();
		ctx.translate(center.x * sf + off.x, center.y * sf + off.y);
		ctx.rotate((this.rect.rotation * Math.PI) / 180);
		const sw = this.rect.w * sf;
		const sh = this.rect.h * sf;
		ctx.strokeStyle = '#1f7a67';
		ctx.lineWidth = 2;
		ctx.strokeRect(-sw / 2, -sh / 2, sw, sh);
		ctx.beginPath();
		ctx.strokeStyle = 'rgba(31, 122, 103, 0.4)';
		ctx.lineWidth = 1;
		ctx.moveTo(-sw / 2, -sh / 2);
		ctx.lineTo(sw / 2, sh / 2);
		ctx.moveTo(sw / 2, -sh / 2);
		ctx.lineTo(-sw / 2, sh / 2);
		ctx.stroke();
		if (this.rect.active && this.mode !== 'drawRect') {
			const hs = 6;
			ctx.fillStyle = '#fff';
			ctx.strokeStyle = '#333';
			ctx.lineWidth = 1;
			[
				{ x: -sw / 2, y: -sh / 2 }, { x: sw / 2, y: -sh / 2 },
				{ x: sw / 2, y: sh / 2 }, { x: -sw / 2, y: sh / 2 },
			].forEach((p) => {
				ctx.beginPath();
				ctx.arc(p.x, p.y, hs, 0, Math.PI * 2);
				ctx.fill();
				ctx.stroke();
			});
		}
		ctx.restore();
		ctx.beginPath();
		ctx.arc(center.x * sf + off.x, center.y * sf + off.y, 4, 0, Math.PI * 2);
		ctx.fillStyle = '#c34f3a';
		ctx.fill();
	}

	drawNaQiDisk(ctx, sf, off) {
		const center = this.getDiskCenter();
		if (!center) return;
		const cx = center.x * sf + off.x;
		const cy = center.y * sf + off.y;
		const radius = this.getMaxDiskRadius(center) * this.diskScale * sf;
		if (radius <= 0) return;
		const diskRotation = this.getDiskRotation();
		ctx.save();
		ctx.translate(cx, cy);
		ctx.rotate((diskRotation * Math.PI) / 180);
		ctx.globalAlpha = this.globalAlpha;
		SECTORS.forEach((sector) => {
			const sr = ((sector.start - 90) * Math.PI) / 180;
			const er = ((sector.end - 90) * Math.PI) / 180;
			ctx.beginPath();
			ctx.moveTo(0, 0);
			ctx.arc(0, 0, radius, sr, er);
			ctx.fillStyle = this.isWindSector(sector.num) ? WIND_COLOR : WATER_COLOR;
			ctx.fill();
			ctx.beginPath();
			ctx.moveTo(0, 0);
			ctx.lineTo(Math.cos(sr) * radius, Math.sin(sr) * radius);
			ctx.strokeStyle = '#111';
			ctx.lineWidth = 1.4;
			ctx.stroke();
			ctx.beginPath();
			ctx.moveTo(0, 0);
			ctx.lineTo(Math.cos(er) * radius, Math.sin(er) * radius);
			ctx.stroke();
		});
		ctx.globalAlpha = 1;
		SECTORS.forEach((sector) => {
			let mid = (sector.start + sector.end) / 2;
			if (sector.start > sector.end) mid = (sector.start + sector.end + 360) / 2;
			if (mid >= 360) mid -= 360;
			const mr = ((mid - 90) * Math.PI) / 180;
			const tr = radius * 0.7;
			ctx.save();
			ctx.translate(Math.cos(mr) * tr, Math.sin(mr) * tr);
			ctx.rotate((-diskRotation * Math.PI) / 180);
			ctx.textAlign = 'center';
			ctx.textBaseline = 'middle';
			ctx.fillStyle = '#fff';
			ctx.font = `bold ${radius * 0.18}px "Avenir Next"`;
			ctx.shadowColor = 'rgba(0,0,0,0.45)';
			ctx.shadowBlur = 4;
			ctx.fillText(sector.num, 0, -radius * 0.08);
			ctx.font = `bold ${radius * 0.11}px "PingFang SC"`;
			ctx.fillText(sector.name, 0, radius * 0.12);
			ctx.restore();
		});
		if (this.unitAzimuth !== null && !Number.isNaN(this.unitAzimuth)) {
			const ur = ((this.unitAzimuth - 90) * Math.PI) / 180;
			const al = radius * 1.15;
			ctx.beginPath();
			ctx.moveTo(0, 0);
			ctx.lineTo(Math.cos(ur) * al, Math.sin(ur) * al);
			ctx.strokeStyle = '#1f7a67';
			ctx.lineWidth = 3;
			ctx.shadowColor = 'rgba(0,0,0,0.4)';
			ctx.shadowBlur = 2;
			ctx.stroke();
			ctx.shadowBlur = 0;
			ctx.save();
			ctx.translate(Math.cos(ur) * al, Math.sin(ur) * al);
			ctx.rotate(ur);
			ctx.beginPath();
			ctx.moveTo(0, 0);
			ctx.lineTo(-10, -6);
			ctx.lineTo(-10, 6);
			ctx.closePath();
			ctx.fillStyle = '#1f7a67';
			ctx.fill();
			ctx.restore();
			ctx.save();
			ctx.translate(Math.cos(ur) * al, Math.sin(ur) * al);
			ctx.rotate((-diskRotation * Math.PI) / 180);
			ctx.fillStyle = '#1f7a67';
			ctx.font = 'bold 13px sans-serif';
			ctx.fillText(`单元门 ${Math.round(this.unitAzimuth)}°`, 0, -14);
			ctx.restore();
		}
		ctx.restore();
		if (this.doorImageAngle !== null && !Number.isNaN(this.doorImageAngle)) {
			const dr = ((this.doorImageAngle - 90) * Math.PI) / 180;
			ctx.save();
			ctx.translate(cx, cy);
			ctx.beginPath();
			ctx.moveTo(0, 0);
			ctx.lineTo(Math.cos(dr) * radius, Math.sin(dr) * radius);
			ctx.strokeStyle = 'rgba(216, 79, 79, 0.7)';
			ctx.setLineDash([4, 4]);
			ctx.lineWidth = 2;
			ctx.stroke();
			ctx.restore();
		}
	}

	drawMarkers(ctx, sf, off) {
		this.markers.forEach((marker) => {
			const ev = this.evaluateMarker(marker);
			const x = marker.x * sf + off.x;
			const y = marker.y * sf + off.y;
			const radius = marker.id === this.selectedMarkerId ? 9 : 7;
			ctx.beginPath();
			ctx.arc(x, y, radius, 0, Math.PI * 2);
			ctx.fillStyle = marker.color;
			ctx.fill();
			ctx.strokeStyle = !ev.ok && ev.expected !== 'neutral' ? '#b14032' : '#fff';
			ctx.lineWidth = 2;
			ctx.stroke();
			ctx.fillStyle = '#fff';
			ctx.font = 'bold 11px sans-serif';
			ctx.textAlign = 'center';
			ctx.textBaseline = 'middle';
			ctx.fillText(marker.short, x, y + 0.5);
		});
	}

	// ── 判定 ───────────────────────────────────────────────────
	getSectorForPoint(marker) {
		const center = this.getDiskCenter();
		if (!center) return null;
		const dx = marker.x - center.x;
		const dy = marker.y - center.y;
		const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
		let compass = angle + 90;
		if (compass < 0) compass += 360;
		let rotated = compass - this.getDiskRotation();
		if (rotated < 0) rotated += 360;
		rotated %= 360;
		for (const sector of SECTORS) {
			if (angleInSector(rotated, sector.start, sector.end)) return sector;
		}
		return null;
	}

	evaluateMarker(marker) {
		const sector = this.getSectorForPoint(marker);
		if (!sector) return { sector: null, expected: marker.category, actual: null, ok: marker.category === 'neutral' };
		const actual = this.isWindSector(sector.num) ? 'wind' : 'water';
		const ok = marker.category === 'neutral' || marker.category === actual;
		return { sector, expected: marker.category, actual, ok };
	}

	// ── 快照（AI 分析挂载文本）──────────────────────────────────
	buildAiSnapshotText() {
		const periodLabel = this.periodMode === 'current' ? '1964-2044' : '2044-2124';
		const headerLines = [
			`生成时间：${new Date().toLocaleString()}`,
			`单元门角度：${formatAngle(this.unitAzimuth)}   入户门角度：${formatAngle(this.doorImageAngle)}   盘旋转：${formatAngle(this.getDiskRotation())}   运期：${periodLabel}`,
		];
		const details = this.markers.map((m) => {
			const ev = this.evaluateMarker(m);
			const position = ev.sector ? `${ev.sector.num}·${ev.sector.name}·${ev.actual === 'wind' ? '气位' : '水位'}` : '未定位';
			return { marker: m, ev, position };
		});
		const markerLines = this.markers.length
			? details.map((d, i) => {
				const st = d.marker.category === 'neutral' ? '观察' : d.ev.ok ? '位置合适' : '位置冲突';
				return `${i + 1}. ${d.marker.label}：${d.position}（${st}）`;
			})
			: ['暂无标记'];
		const conflictLines = details.filter((d) => d.marker.category !== 'neutral' && d.ev.sector && !d.ev.ok)
			.map((d) => `${d.marker.label}：${d.position}（期望 ${d.ev.expected === 'wind' ? '气位' : '水位'}）`);
		const unknownLines = details.filter((d) => !d.ev.sector).map((d) => `${d.marker.label}：未定位`);
		const stats = { windOk: 0, waterOk: 0, windBad: 0, waterBad: 0, unknown: 0 };
		details.forEach((d) => {
			if (!d.ev.sector) stats.unknown += 1;
			else if (d.marker.category === 'wind') d.ev.ok ? (stats.windOk += 1) : (stats.windBad += 1);
			else if (d.marker.category === 'water') d.ev.ok ? (stats.waterOk += 1) : (stats.waterBad += 1);
		});
		const statsLine = `气位正确 ${stats.windOk} 项，气位冲突 ${stats.windBad} 项；水位正确 ${stats.waterOk} 项，水位冲突 ${stats.waterBad} 项；未定位 ${stats.unknown} 项。`;
		const suggestionLines = [];
		if (!this.markers.length) suggestionLines.push('当前没有标注，可先放置门、窗、床、灶、沙发等关键点。');
		else {
			if (stats.windBad > 0) suggestionLines.push('存在气位冲突，建议将气位类标注调整到气位扇区。');
			if (stats.waterBad > 0) suggestionLines.push('存在水位冲突，建议将水位类标注调整到水位扇区。');
			if (stats.unknown > 0) suggestionLines.push('有未定位标注，请确认盘心、房屋框或角度输入。');
			if (stats.windBad === 0 && stats.waterBad === 0 && stats.unknown === 0) suggestionLines.push('当前标注均在合适位置，可继续完善细节。');
		}
		const out = [];
		const push = (title, rows) => { out.push(`[${title}]`); (rows || []).forEach((l) => out.push(`${l}`)); out.push(''); };
		push('起盘信息', headerLines);
		push('标记判定', [statsLine, ...markerLines]);
		push('冲突清单', conflictLines.length ? conflictLines : ['暂无冲突标记']);
		if (unknownLines.length) push('未定位标注', unknownLines);
		push('使用要点', TIPS);
		push('建议汇总', suggestionLines);
		push('纳气建议', [ADVICE]);
		while (out.length && !out[out.length - 1]) out.pop();
		return out.join('\n');
	}

	// ── 导出 ───────────────────────────────────────────────────
	renderCompositeCanvas() {
		if (!this.imgLoaded) return null;
		const ex = document.createElement('canvas');
		ex.width = this.img.width;
		ex.height = this.img.height;
		const ectx = ex.getContext('2d');
		ectx.drawImage(this.img, 0, 0);
		if (this.rect.w !== 0 && this.rect.h !== 0) this.drawRotatedRect(ectx, 1, { x: 0, y: 0 });
		if (this.rect.active) this.drawNaQiDisk(ectx, 1, { x: 0, y: 0 });
		this.drawMarkers(ectx, 1, { x: 0, y: 0 });
		return ex;
	}

	exportPng() {
		const ex = this.renderCompositeCanvas();
		if (!ex) return;
		const link = document.createElement('a');
		link.download = 'naqi-output.png';
		link.href = ex.toDataURL('image/png');
		link.click();
	}

	buildReportCanvas() {
		const composite = this.renderCompositeCanvas();
		if (!composite) return null;
		const wrapLines = (ctx, text, maxWidth) => {
			const chars = `${text}`.split('');
			const lines = [];
			let line = '';
			chars.forEach((ch) => {
				const test = line + ch;
				if (ctx.measureText(test).width > maxWidth && line) { lines.push(line); line = ch; }
				else line = test;
			});
			if (line) lines.push(line);
			return lines;
		};
		const scaleImg = Math.min(1, 1500 / composite.width);
		const imgW = Math.round(composite.width * scaleImg);
		const imgH = Math.round(composite.height * scaleImg);
		const padding = 36;
		const reportWidth = Math.max(imgW + padding * 2, 1000);
		const imageX = Math.round((reportWidth - imgW) / 2);
		const periodLabel = this.periodMode === 'current' ? '1964-2044' : '2044-2124';
		const headerLines = [
			`生成时间：${new Date().toLocaleString()}`,
			`单元门角度：${formatAngle(this.unitAzimuth)}   入户门角度：${formatAngle(this.doorImageAngle)}   盘旋转：${formatAngle(this.getDiskRotation())}   运期：${periodLabel}`,
		];
		const details = this.markers.map((m) => {
			const ev = this.evaluateMarker(m);
			const position = ev.sector ? `${ev.sector.num}·${ev.sector.name}·${ev.actual === 'wind' ? '气位' : '水位'}` : '未定位';
			return { marker: m, ev, position };
		});
		const markerLines = this.markers.length
			? details.map((d, i) => `${i + 1}. ${d.marker.label}：${d.position}（${d.marker.category === 'neutral' ? '观察' : d.ev.ok ? '位置合适' : '位置冲突'}）`)
			: ['暂无标记'];
		const conflictLines = details.filter((d) => d.marker.category !== 'neutral' && d.ev.sector && !d.ev.ok)
			.map((d) => `${d.marker.label}：${d.position}（期望 ${d.ev.expected === 'wind' ? '气位' : '水位'}）`);
		const unknownLines = details.filter((d) => !d.ev.sector).map((d) => `${d.marker.label}：未定位`);
		const stats = { windOk: 0, waterOk: 0, windBad: 0, waterBad: 0, unknown: 0 };
		details.forEach((d) => {
			if (!d.ev.sector) stats.unknown += 1;
			else if (d.marker.category === 'wind') d.ev.ok ? (stats.windOk += 1) : (stats.windBad += 1);
			else if (d.marker.category === 'water') d.ev.ok ? (stats.waterOk += 1) : (stats.waterBad += 1);
		});
		const statsLine = `气位正确 ${stats.windOk} 项，气位冲突 ${stats.windBad} 项；水位正确 ${stats.waterOk} 项，水位冲突 ${stats.waterBad} 项；未定位 ${stats.unknown} 项。`;
		const suggestionLines = [];
		if (!this.markers.length) suggestionLines.push('当前没有标注，可先放置门、窗、床、灶、沙发等关键点。');
		else {
			if (stats.windBad > 0) suggestionLines.push('存在气位冲突，建议将气位类标注调整到气位扇区。');
			if (stats.waterBad > 0) suggestionLines.push('存在水位冲突，建议将水位类标注调整到水位扇区。');
			if (stats.unknown > 0) suggestionLines.push('有未定位标注，请确认盘心、房屋框或角度输入。');
			if (stats.windBad === 0 && stats.waterBad === 0 && stats.unknown === 0) suggestionLines.push('当前标注均在合适位置，可继续完善细节。');
		}
		const sections = [
			['基础信息', headerLines],
			['标记判定', [statsLine, ...markerLines]],
			['冲突清单', conflictLines.length ? conflictLines : ['暂无冲突标记']],
		];
		if (unknownLines.length) sections.push(['未定位标注', unknownLines]);
		sections.push(['使用要点', TIPS]);
		sections.push(['建议汇总', suggestionLines]);
		sections.push(['纳气建议', [ADVICE]]);
		const measure = document.createElement('canvas').getContext('2d');
		measure.font = '14px "PingFang SC", sans-serif';
		const contentWidth = reportWidth - padding * 2;
		let textHeight = 0;
		sections.forEach(([, lines]) => {
			textHeight += 28;
			lines.forEach((l) => { textHeight += wrapLines(measure, l, contentWidth).length * 22; });
			textHeight += 14;
		});
		const reportCanvas = document.createElement('canvas');
		reportCanvas.width = reportWidth;
		reportCanvas.height = Math.round(padding + 40 + imgH + padding + textHeight + padding);
		const rc = reportCanvas.getContext('2d');
		rc.fillStyle = '#ffffff';
		rc.fillRect(0, 0, reportWidth, reportCanvas.height);
		rc.fillStyle = '#1b1812';
		rc.font = 'bold 24px "PingFang SC", sans-serif';
		rc.fillText('纳气盘判定报告', padding, padding + 6);
		const imageTop = padding + 20;
		rc.drawImage(composite, 0, 0, composite.width, composite.height, imageX, imageTop, imgW, imgH);
		let y = imageTop + imgH + padding;
		sections.forEach(([title, lines]) => {
			rc.fillStyle = '#1b1812';
			rc.font = 'bold 16px "PingFang SC", sans-serif';
			rc.fillText(title, padding, y);
			y += 24;
			rc.fillStyle = '#3a342a';
			rc.font = '14px "PingFang SC", sans-serif';
			lines.forEach((l) => { wrapLines(rc, l, contentWidth).forEach((row) => { rc.fillText(row, padding, y); y += 22; }); });
			y += 10;
		});
		return reportCanvas;
	}

	exportReportPng() {
		const rc = this.buildReportCanvas();
		if (!rc) return;
		const link = document.createElement('a');
		link.download = 'naqi-report.png';
		link.href = rc.toDataURL('image/png');
		link.click();
	}

	exportReportPdf() {
		const rc = this.buildReportCanvas();
		if (!rc) return;
		const dataUrl = rc.toDataURL('image/png');
		const win = window.open('', '_blank');
		if (!win) return;
		win.document.write([
			'<!doctype html><html><head><title>纳气盘判定报告</title>',
			'<style>body{margin:0;padding:24px;font-family:"PingFang SC",sans-serif;background:#fff;}img{width:100%;max-width:100%;}</style>',
			'</head><body>',
			`<img src="${dataUrl}" />`,
			'<scr' + 'ipt>window.onload=function(){window.print();};</scr' + 'ipt>',
			'</body></html>',
		].join(''));
		win.document.close();
	}

	// ── 控件动作（React 调用）──────────────────────────────────
	loadImageFile(file) {
		if (!file) return;
		const reader = new FileReader();
		reader.onload = (event) => {
			this.img = new Image();
			this.img.onload = () => {
				this.imgLoaded = true;
				this.viewScale = 1;
				this.resize();
				this.startDrawRect();
				this.setStatus('图片已加载，已进入手动框选模式。');
				this.initHistory();
				this.emit();
			};
			this.img.src = event.target.result;
		};
		reader.readAsDataURL(file);
	}

	startDrawRect() {
		if (!this.imgLoaded) return;
		this.mode = 'drawRect';
		this.canvas.style.cursor = 'crosshair';
		this.rect.active = false;
		this.rect.rotation = 0;
		this.setStatus('模式：绘制矩形。在图上拖动完成框选。');
		this.emit();
	}

	startDrawDoor() {
		if (!this.imgLoaded) return;
		this.mode = 'drawDoorLine';
		this.canvas.style.cursor = 'crosshair';
		this.setStatus('模式：绘制门向。请从门内向门外画一条线。');
		this.emit();
	}

	startPlaceMarker() {
		if (!this.imgLoaded) return;
		this.mode = 'placeMarker';
		this.canvas.style.cursor = 'crosshair';
		this.setStatus('模式：放置标记。点击画布位置放置。');
		this.emit();
	}

	resetRect() {
		this.rect = { x: 0, y: 0, w: 0, h: 0, rotation: 0, active: false };
		this.setStatus('已重置房屋框。');
		this.drawAll();
		this.pushHistory();
		this.emit();
	}

	clearMarkers() {
		this.markers = [];
		this.selectedMarkerId = null;
		this.drawAll();
		this.pushHistory();
		this.emit();
	}

	deleteMarker(id) {
		this.markers = this.markers.filter((m) => m.id !== id);
		if (this.selectedMarkerId === id) this.selectedMarkerId = null;
		this.drawAll();
		this.pushHistory();
		this.emit();
	}

	selectMarker(id) {
		this.selectedMarkerId = id;
		this.drawAll();
		this.emit();
	}

	setFilter(f) { this.currentFilter = f; this.emit(); }
	setMarkerType(id) { this.markerType = id; this.emit(); }

	setUnitAngle(v) {
		this.unitAzimuth = v === '' || v === null ? null : parseFloat(v);
		this.drawAll();
		this.scheduleHistoryPush();
		this.emit();
	}

	setDoorAngle(v) {
		this.doorImageAngle = v === '' || v === null ? null : parseFloat(v);
		this.drawAll();
		this.scheduleHistoryPush();
		this.emit();
	}

	setOpacity(v) { this.globalAlpha = parseFloat(v); this.drawAll(); this.scheduleHistoryPush(); this.emit(); }
	setDiskScale(v) { this.diskScale = Math.max(1, parseFloat(v)); this.drawAll(); this.scheduleHistoryPush(); this.emit(); }
	setRectRotation(v) { this.rect.rotation = parseFloat(v) || 0; this.drawAll(); this.scheduleHistoryPush(); this.emit(); }

	setDiskCenterMode(m) {
		this.diskCenterMode = m;
		if (m === 'custom') this.setStatus('自定义盘心：按住 Shift 在画布点击设定。');
		this.drawAll();
		this.pushHistory();
		this.emit();
	}

	setPeriodMode(m) { this.periodMode = m; this.drawAll(); this.pushHistory(); this.emit(); }

	togglePan() {
		this.panMode = !this.panMode;
		this.canvas.style.cursor = this.panMode ? 'grab' : 'default';
		this.setStatus(this.panMode ? '拖拽模式：拖动画布移动' : '拖拽模式已关闭');
		this.emit();
	}

	toggleSnap() { this.snapEnabled = !this.snapEnabled; this.setStatus(this.snapEnabled ? '吸附对齐已开启' : '吸附对齐已关闭'); this.emit(); }

	addMarkerAt(pos) {
		const type = MARKER_TYPES.find((t) => t.id === this.markerType);
		if (!type) return;
		const sp = this.snapPointToRect(pos);
		this.markers.push({ id: this.markerIdSeed++, type: type.id, label: type.label, short: type.short, category: type.category, color: type.color, x: sp.x, y: sp.y });
		this.selectedMarkerId = this.markers[this.markers.length - 1].id;
		this.drawAll();
		this.pushHistory();
		this.emit();
	}

	getMarkerAtPos(pos) {
		const threshold = 10;
		const c = this.getCombinedScale();
		for (let i = this.markers.length - 1; i >= 0; i -= 1) {
			const m = this.markers[i];
			const dx = m.x * c + this.viewOffset.x - pos.x;
			const dy = m.y * c + this.viewOffset.y - pos.y;
			if (Math.hypot(dx, dy) <= threshold) return m;
		}
		return null;
	}

	updateCursorStyle(pos) {
		if (this.panMode) { this.canvas.style.cursor = 'grab'; return; }
		if (!this.rect.active) { this.canvas.style.cursor = 'default'; return; }
		if (this.getMarkerAtPos(pos)) { this.canvas.style.cursor = 'grab'; return; }
		const imgPos = this.screenToImage(pos);
		const center = this.getRectCenter();
		const local = rotatePoint(imgPos, center, -this.rect.rotation);
		const hw = this.rect.w / 2;
		const hh = this.rect.h / 2;
		const dx = local.x - center.x;
		const dy = local.y - center.y;
		const hs = 8 / this.getCombinedScale() + 5;
		if ((Math.abs(dx + hw) < hs && Math.abs(dy + hh) < hs) || (Math.abs(dx - hw) < hs && Math.abs(dy - hh) < hs)) this.canvas.style.cursor = 'nwse-resize';
		else if ((Math.abs(dx - hw) < hs && Math.abs(dy + hh) < hs) || (Math.abs(dx + hw) < hs && Math.abs(dy - hh) < hs)) this.canvas.style.cursor = 'nesw-resize';
		else if (Math.abs(dx) < hw && Math.abs(dy) < hh) this.canvas.style.cursor = 'move';
		else this.canvas.style.cursor = 'default';
	}

	// ── 鼠标事件 ───────────────────────────────────────────────
	_onMouseDown(e) {
		if (!this.imgLoaded) return;
		const pos = this.getMousePos(e);
		const imgPos = this.screenToImage(pos);
		this.startPoint = pos;
		this.isDragging = true;
		if (this.panMode && e.button === 0) {
			this.mode = 'panning';
			this.panStart = { x: pos.x, y: pos.y, offsetX: this.viewOffset.x, offsetY: this.viewOffset.y };
			this.canvas.style.cursor = 'grabbing';
			return;
		}
		if (this.mode === 'placeMarker') {
			this.addMarkerAt(imgPos);
			this.mode = 'none';
			this.canvas.style.cursor = 'default';
			this.setStatus('标记已放置。');
			this.isDragging = false;
			this.emit();
			return;
		}
		if (this.diskCenterMode === 'custom' && e.shiftKey) {
			this.customCenter = imgPos;
			this.setStatus('已更新自定义盘心。');
			this.drawAll();
			this.isDragging = false;
			this.mode = 'none';
			this.pushHistory();
			this.emit();
			return;
		}
		if (this.mode === 'drawRect') {
			this.rect.x = imgPos.x; this.rect.y = imgPos.y; this.rect.w = 0; this.rect.h = 0;
			return;
		}
		if (this.mode === 'drawDoorLine') return;
		const hit = this.getMarkerAtPos(pos);
		if (hit) {
			this.selectedMarkerId = hit.id;
			this.dragMarkerId = hit.id;
			this.mode = 'dragMarker';
			this.canvas.style.cursor = 'grabbing';
			this.drawAll();
			this.emit();
			return;
		}
		if (this.rect.active) {
			const center = this.getRectCenter();
			const local = rotatePoint(imgPos, center, -this.rect.rotation);
			const hw = this.rect.w / 2;
			const hh = this.rect.h / 2;
			const dx = local.x - center.x;
			const dy = local.y - center.y;
			const hs = 8 / this.getCombinedScale() + 5;
			if (Math.abs(dx + hw) < hs && Math.abs(dy + hh) < hs) { this.mode = 'resizingRect'; this.activeHandle = 'tl'; }
			else if (Math.abs(dx - hw) < hs && Math.abs(dy + hh) < hs) { this.mode = 'resizingRect'; this.activeHandle = 'tr'; }
			else if (Math.abs(dx - hw) < hs && Math.abs(dy - hh) < hs) { this.mode = 'resizingRect'; this.activeHandle = 'br'; }
			else if (Math.abs(dx + hw) < hs && Math.abs(dy - hh) < hs) { this.mode = 'resizingRect'; this.activeHandle = 'bl'; }
			else if (Math.abs(dx) < hw && Math.abs(dy) < hh) { this.mode = 'movingRect'; this.canvas.style.cursor = 'move'; }
			else { this.mode = 'none'; this.isDragging = false; return; }
			this.initialRectState = { ...this.rect };
		}
		if (!this.rect.active) { this.isDragging = false; this.mode = 'none'; }
	}

	_onMouseMove(e) {
		if (!this.imgLoaded) return;
		const pos = this.getMousePos(e);
		if (!this.isDragging) { this.updateCursorStyle(pos); return; }
		const imgPos = this.screenToImage(pos);
		const c = this.getCombinedScale();
		const deltaX = (pos.x - this.startPoint.x) / c;
		const deltaY = (pos.y - this.startPoint.y) / c;
		if (this.mode === 'panning' && this.panStart) {
			this.viewOffset.x = this.panStart.offsetX + (pos.x - this.panStart.x);
			this.viewOffset.y = this.panStart.offsetY + (pos.y - this.panStart.y);
			this.drawAll();
			return;
		}
		if (this.mode === 'drawRect') { this.rect.w = deltaX; this.rect.h = deltaY; this.drawAll(); return; }
		if (this.mode === 'drawDoorLine') {
			this.drawAll();
			this.ctx.beginPath();
			this.ctx.moveTo(this.startPoint.x, this.startPoint.y);
			this.ctx.lineTo(pos.x, pos.y);
			this.ctx.strokeStyle = '#d84f4f';
			this.ctx.lineWidth = 2;
			this.ctx.stroke();
			return;
		}
		if (this.mode === 'movingRect') {
			this.rect.x = this.initialRectState.x + deltaX;
			this.rect.y = this.initialRectState.y + deltaY;
			this.drawAll();
			return;
		}
		if (this.mode === 'resizingRect') {
			const rad = (-this.initialRectState.rotation * Math.PI) / 180;
			const ldx = deltaX * Math.cos(rad) - deltaY * Math.sin(rad);
			const ldy = deltaX * Math.sin(rad) + deltaY * Math.cos(rad);
			let nx = this.initialRectState.x;
			let ny = this.initialRectState.y;
			let nw = this.initialRectState.w;
			let nh = this.initialRectState.h;
			if (this.activeHandle === 'br') { nw += ldx; nh += ldy; }
			else if (this.activeHandle === 'bl') { nx += ldx; nw -= ldx; nh += ldy; }
			else if (this.activeHandle === 'tr') { ny += ldy; nh -= ldy; nw += ldx; }
			else if (this.activeHandle === 'tl') { nx += ldx; ny += ldy; nw -= ldx; nh -= ldy; }
			this.rect.x = nx; this.rect.y = ny; this.rect.w = nw; this.rect.h = nh;
			this.drawAll();
			return;
		}
		if (this.mode === 'dragMarker') {
			const m = this.markers.find((x) => x.id === this.dragMarkerId);
			if (m) { const sp = this.snapPointToRect(imgPos); m.x = sp.x; m.y = sp.y; this.drawAll(); }
		}
	}

	_onMouseUp(e) {
		if (!this.imgLoaded || !this.isDragging) return;
		this.isDragging = false;
		const pos = this.getMousePos(e);
		if (this.mode === 'panning') { this.mode = 'none'; this.canvas.style.cursor = this.panMode ? 'grab' : 'default'; this.drawAll(); return; }
		if (this.mode === 'drawRect') {
			this.rect.active = true;
			if (this.rect.w < 0) { this.rect.x += this.rect.w; this.rect.w = Math.abs(this.rect.w); }
			if (this.rect.h < 0) { this.rect.y += this.rect.h; this.rect.h = Math.abs(this.rect.h); }
			this.snapRectToImage();
			const c = this.getCombinedScale();
			if (this.rect.w < 5 / c || this.rect.h < 5 / c) { this.rect.active = false; this.setStatus('房屋框过小，请重新绘制。'); }
			else this.setStatus('房屋框已完成，可拖动或微调旋转。');
			this.mode = 'none';
			this.pushHistory();
		} else if (this.mode === 'drawDoorLine') {
			const dx = pos.x - this.startPoint.x;
			const dy = pos.y - this.startPoint.y;
			let mapDeg = (Math.atan2(dy, dx) * 180) / Math.PI + 90;
			if (mapDeg < 0) mapDeg += 360;
			this.doorImageAngle = mapDeg;
			this.setStatus(`入户门角度已设定：${Math.round(this.doorImageAngle)}°`);
			this.mode = 'none';
			this.pushHistory();
		} else if (this.mode === 'movingRect' || this.mode === 'resizingRect') {
			if (this.rect.w < 0) { this.rect.x += this.rect.w; this.rect.w = Math.abs(this.rect.w); }
			if (this.rect.h < 0) { this.rect.y += this.rect.h; this.rect.h = Math.abs(this.rect.h); }
			this.snapRectToImage();
			this.mode = 'none';
			this.pushHistory();
		} else if (this.mode === 'dragMarker') {
			this.mode = 'none';
			this.pushHistory();
		}
		this.drawAll();
		this.canvas.style.cursor = 'default';
		this.emit();
	}

	handleKey(e) {
		const key = (e.key || '').toLowerCase();
		const isMod = e.metaKey || e.ctrlKey;
		const editing = e.target && (['input', 'textarea'].includes((e.target.tagName || '').toLowerCase()) || e.target.isContentEditable);
		if (isMod && key === 'z' && !e.shiftKey) { if (!editing) { e.preventDefault(); this.undo(); } return; }
		if (isMod && (key === 'y' || (key === 'z' && e.shiftKey))) { if (!editing) { e.preventDefault(); this.redo(); } return; }
		if (e.key === 'Escape') { this.mode = 'none'; this.canvas.style.cursor = 'default'; this.emit(); }
	}
}
