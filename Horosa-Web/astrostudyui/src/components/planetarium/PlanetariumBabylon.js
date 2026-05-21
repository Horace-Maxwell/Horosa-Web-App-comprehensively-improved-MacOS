import { Component, createRef } from 'react';
import DateTime from '../comp/DateTime';
import { fetchPlanetariumState } from '../../services/planetarium';
import GeoCoordModal from '../amap/GeoCoordModal';
import { convertLatToStr, convertLonToStr } from '../astro/AstroHelper';

const BABYLON = typeof window !== 'undefined' ? window.BABYLON : null;

const SKY_RADIUS = 2600;
const BODY_RADIUS = 820;
const STAR_RADIUS = 780;
const LINE_RADIUS = 760;
const OBSERVER_EYE_HEIGHT = 5;
const PLANETARIUM_PERF_KEY = '__horosaPlanetariumPerf';

const BODY_LABELS = {
	Sun: '太阳',
	Moon: '月亮',
	Earth: '地球',
	Mercury: '水星',
	Venus: '金星',
	Mars: '火星',
	Jupiter: '木星',
	Saturn: '土星',
	Uranus: '天王星',
	Neptune: '海王星',
	Pluto: '冥王星',
	'North Node': '北交点',
	'South Node': '南交点',
};

const BODY_COLORS = {
	Sun: new BABYLON.Color3(1.0, 0.76, 0.25),
	Moon: new BABYLON.Color3(0.82, 0.9, 1.0),
	Earth: new BABYLON.Color3(0.24, 0.55, 0.95),
	Mercury: new BABYLON.Color3(0.72, 0.72, 0.68),
	Venus: new BABYLON.Color3(0.98, 0.72, 0.48),
	Mars: new BABYLON.Color3(1.0, 0.34, 0.22),
	Jupiter: new BABYLON.Color3(0.95, 0.72, 0.48),
	Saturn: new BABYLON.Color3(0.92, 0.82, 0.56),
	Uranus: new BABYLON.Color3(0.44, 0.9, 0.96),
	Neptune: new BABYLON.Color3(0.38, 0.52, 1.0),
	Pluto: new BABYLON.Color3(0.78, 0.66, 0.58),
	'North Node': new BABYLON.Color3(0.75, 0.88, 1.0),
	'South Node': new BABYLON.Color3(0.7, 0.58, 0.96),
};

const TEXTURED_BODY_IDS = new Set([
	'Sun', 'Moon', 'Earth', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto',
]);

const DEFAULT_LAYERS = {
	stars: true,
	bodies: true,
	horizon: true,
	equator: true,
	ecliptic: true,
	houses: true,
	su28: true,
	beidou: true,
	qizheng: true,
};

function degToRad(deg){
	return (Number(deg) || 0) * Math.PI / 180;
}

function nowMs(){
	if(typeof performance !== 'undefined' && performance && performance.now){
		return performance.now();
	}
	return Date.now();
}

function normalizeAzimuth(azimuth){
	return ((Number(azimuth) || 0) + 180) % 360;
}

function clamp(value, min, max){
	return Math.max(min, Math.min(max, value));
}

function starTemperatureColor(star, brightness){
	const kelvin = Number(star && star.colorTemperature);
	if(!Number.isFinite(kelvin) || kelvin <= 0){
		return {
			r: 0.58 + brightness * 0.34,
			g: 0.66 + brightness * 0.22,
			b: 0.86 + brightness * 0.1,
		};
	}
	const t = clamp(kelvin, 2800, 14000);
	const warm = clamp((6500 - t) / 3700, 0, 1);
	const cool = clamp((t - 6500) / 7500, 0, 1);
	return {
		r: clamp(0.82 + warm * 0.18 - cool * 0.08, 0.52, 1),
		g: clamp(0.82 + warm * 0.06 + cool * 0.05, 0.52, 1),
		b: clamp(0.86 - warm * 0.34 + cool * 0.14, 0.48, 1),
	};
}

function toSkyVector(item, radius){
	const alt = Number(item.altitudeAppa !== undefined && item.altitudeAppa !== null ? item.altitudeAppa : item.altitudeTrue) || 0;
	const az = normalizeAzimuth(item.azimuth);
	const altRad = degToRad(alt);
	const azRad = degToRad(az);
	const r = radius * Math.cos(altRad);
	return new BABYLON.Vector3(
		r * Math.sin(azRad),
		radius * Math.sin(altRad),
		r * Math.cos(azRad),
	);
}

function normalizeDegrees(deg){
	return ((Number(deg) % 360) + 360) % 360;
}

function parseGeoDegree(value){
	if(value === undefined || value === null || value === ''){
		return null;
	}
	if(typeof value === 'number' && Number.isFinite(value)){
		return value;
	}
	const text = `${value}`.trim().toLowerCase();
	const direct = Number(text);
	if(Number.isFinite(direct)){
		return direct;
	}
	const sign = /[ws]/.test(text) ? -1 : 1;
	const parts = text.replace(/[nsew]/g, ' ').trim().split(/[^0-9.]+/).filter(Boolean).map(Number);
	if(!parts.length || !Number.isFinite(parts[0])){
		return null;
	}
	return sign * (Math.abs(parts[0]) + (Number(parts[1]) || 0) / 60 + (Number(parts[2]) || 0) / 3600);
}

function observerFromFields(fields, data){
	const observer = data && data.observer ? data.observer : {};
	const firstGeo = (...values)=>{
		for(let i = 0; i < values.length; i += 1){
			const parsed = parseGeoDegree(values[i]);
			if(parsed !== null && parsed !== undefined && Number.isFinite(parsed)){
				return parsed;
			}
		}
		return 0;
	};
	const lat = firstGeo(
		fields && fields.gpsLat ? fields.gpsLat.value : null,
		observer.gpsLat,
		fields && fields.lat ? fields.lat.value : null,
		observer.lat,
	);
	const lon = firstGeo(
		fields && fields.gpsLon ? fields.gpsLon.value : null,
		observer.gpsLon,
		fields && fields.lon ? fields.lon.value : null,
		observer.lon,
	);
	return { lat, lon };
}

function gmstDegrees(jd){
	const t = (Number(jd) - 2451545.0) / 36525;
	return normalizeDegrees(280.46061837 + 360.98564736629 * (Number(jd) - 2451545.0) + 0.000387933 * t * t - (t * t * t) / 38710000);
}

function equatorialToHorizontal(ra, decl, jd, observer){
	if(!Number.isFinite(Number(ra)) || !Number.isFinite(Number(decl)) || !Number.isFinite(Number(jd))){
		return null;
	}
	const lat = degToRad(observer.lat || 0);
	const dec = degToRad(decl);
	const lst = normalizeDegrees(gmstDegrees(jd) + Number(observer.lon || 0));
	const ha = degToRad(normalizeDegrees(lst - Number(ra)));
	const sinAlt = Math.sin(dec) * Math.sin(lat) + Math.cos(dec) * Math.cos(lat) * Math.cos(ha);
	const alt = Math.asin(clamp(sinAlt, -1, 1));
	const az = Math.atan2(
		-Math.sin(ha),
		Math.tan(dec) * Math.cos(lat) - Math.sin(lat) * Math.cos(ha),
	);
	const standardAz = normalizeDegrees(az * 180 / Math.PI);
	return {
		altitudeAppa: alt * 180 / Math.PI,
		azimuth: normalizeDegrees(standardAz + 180),
	};
}

function eclipticToEquatorial(lon, lat = 0){
	if(!Number.isFinite(Number(lon)) || !Number.isFinite(Number(lat))){
		return null;
	}
	const obliquity = degToRad(23.4392911);
	const lonRad = degToRad(lon);
	const latRad = degToRad(lat);
	const sinDec = Math.sin(latRad) * Math.cos(obliquity) + Math.cos(latRad) * Math.sin(obliquity) * Math.sin(lonRad);
	const dec = Math.asin(clamp(sinDec, -1, 1));
	const y = Math.sin(lonRad) * Math.cos(obliquity) - Math.tan(latRad) * Math.sin(obliquity);
	const x = Math.cos(lonRad);
	const ra = Math.atan2(y, x);
	return {
		ra: normalizeDegrees(ra * 180 / Math.PI),
		decl: dec * 180 / Math.PI,
	};
}

function projectedEquatorialItem(item, jd, observer){
	let ra = item && item.ra;
	let decl = item && item.decl;
	if((!Number.isFinite(Number(ra)) || !Number.isFinite(Number(decl))) && item && item.lon !== undefined){
		const eq = eclipticToEquatorial(item.lon, item.lat || 0);
		if(eq){
			ra = eq.ra;
			decl = eq.decl;
		}
	}
	const pos = equatorialToHorizontal(ra, decl, jd, observer);
	if(!pos){
		return item;
	}
	return {
		...item,
		ra,
		decl,
		...pos,
		visible: pos.altitudeAppa > 0,
		horizonState: pos.altitudeAppa > 0 ? '可见' : '地平线下',
	};
}

function cameraRotationForDirection(direction){
	const dir = direction.clone().normalize();
	return {
		x: -Math.asin(clamp(dir.y, -1, 1)),
		y: Math.atan2(dir.x, dir.z),
	};
}

function formatDeg(val){
	if(val === undefined || val === null || Number.isNaN(Number(val))){
		return '--';
	}
	return `${Math.round(Number(val) * 1000) / 1000}°`;
}

function bodyName(item){
	return BODY_LABELS[item.id] || item.name || item.id || '天体';
}

function objectType(item){
	if(!item){
		return '--';
	}
	if(item.kind === 'catalogStar'){
		return '恒星';
	}
	if(item.layer === 'su28'){
		return '二十八宿';
	}
	if(item.layer === 'beidou'){
		return '北斗';
	}
	if(item.layer === 'body'){
		if(item.id === 'Earth'){
			return '地球/观测点';
		}
		return item.id === 'Sun' || item.id === 'Moon' ? '日月' : '行星/交点';
	}
	return item.type || item.kind || item.layer || '--';
}

function visibilityText(item){
	if(!item){
		return '--';
	}
	const state = item.horizonState || (Number(item.altitudeAppa || 0) > 0 ? '可见' : '不可见');
	return item.visible === false ? `${state} · 条件不佳` : state;
}

function moonPhaseGlyph(phase){
	if(!phase){
		return '○';
	}
	const angle = Number(phase.phaseAngle || 0);
	if(angle < 22.5 || angle >= 337.5){ return '●'; }
	if(angle < 67.5){ return '☽'; }
	if(angle < 112.5){ return '◐'; }
	if(angle < 157.5){ return '◑'; }
	if(angle < 202.5){ return '○'; }
	if(angle < 247.5){ return '◐'; }
	if(angle < 292.5){ return '◑'; }
	return '☾';
}

function noise2(x, y, seed){
	const v = Math.sin(x * 12.9898 + y * 78.233 + seed * 37.719) * 43758.5453;
	return v - Math.floor(v);
}

function drawEllipse(ctx, x, y, rx, ry, color, alpha = 1){
	ctx.save();
	ctx.globalAlpha = alpha;
	ctx.fillStyle = color;
	ctx.beginPath();
	ctx.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2);
	ctx.fill();
	ctx.restore();
}

function planetTextureSize(id){
	return id === 'Moon' ? { width: 512, height: 512 } : { width: 512, height: 256 };
}

function paintPlanetSurface(ctx, id, width, height){
	ctx.clearRect(0, 0, width, height);
	const grad = ctx.createLinearGradient(0, 0, 0, height);
	const base = {
		Sun: ['#ffdf73', '#ff9127', '#b94a16'],
		Mercury: ['#bfc0b9', '#777873', '#494b49'],
		Venus: ['#ffe1aa', '#d9965d', '#8b5c37'],
		Earth: ['#1e61a6', '#133d73', '#071d3d'],
		Moon: ['#d6d9d5', '#888e8e', '#3e4448'],
		Mars: ['#df7444', '#9b3b28', '#4d221c'],
		Jupiter: ['#f4d2a5', '#c48759', '#7f5135'],
		Saturn: ['#f2dda4', '#c8a86a', '#806946'],
		Uranus: ['#b5fbff', '#55c5d1', '#226f83'],
		Neptune: ['#6ca6ff', '#2556bd', '#102868'],
		Pluto: ['#d7c2a8', '#8d755f', '#4a403a'],
	}[id] || ['#e5e9ff', '#8b93b0', '#30364c'];
	grad.addColorStop(0, base[0]);
	grad.addColorStop(0.52, base[1]);
	grad.addColorStop(1, base[2]);
	ctx.fillStyle = grad;
	ctx.fillRect(0, 0, width, height);

	if(id === 'Sun'){
		for(let i = 0; i < 28; i += 1){
			const y = (i / 28) * height;
			ctx.strokeStyle = i % 2 ? 'rgba(255,244,148,0.34)' : 'rgba(207,67,18,0.22)';
			ctx.lineWidth = 3 + noise2(i, 2, 5) * 8;
			ctx.beginPath();
			for(let x = 0; x <= width; x += 18){
				const wave = Math.sin(x * 0.018 + i * 0.8) * (4 + noise2(i, x, 2) * 6);
				if(x === 0){ ctx.moveTo(x, y + wave); }else{ ctx.lineTo(x, y + wave); }
			}
			ctx.stroke();
		}
		for(let i = 0; i < 42; i += 1){
			drawEllipse(ctx, noise2(i, 1, 7) * width, noise2(i, 2, 8) * height, 8 + noise2(i, 3, 9) * 28, 3 + noise2(i, 4, 10) * 11, '#fff1a6', 0.18);
		}
		return;
	}

	if(id === 'Earth'){
		const land = '#4e9a5f';
		const desert = '#c49d6a';
		[
			[0.18, 0.38, 0.12, 0.2, land],
			[0.34, 0.62, 0.18, 0.14, desert],
			[0.58, 0.42, 0.22, 0.18, land],
			[0.78, 0.66, 0.17, 0.12, desert],
			[0.88, 0.34, 0.16, 0.18, land],
		].forEach((item)=>{
			drawEllipse(ctx, item[0] * width, item[1] * height, item[2] * width, item[3] * height, item[4], 0.82);
		});
		for(let i = 0; i < 18; i += 1){
			ctx.strokeStyle = 'rgba(245,250,255,0.45)';
			ctx.lineWidth = 4 + noise2(i, 1, 4) * 7;
			ctx.beginPath();
			const y = noise2(i, 2, 5) * height;
			for(let x = 0; x <= width; x += 30){
				const wave = Math.sin(x * 0.022 + i) * 12;
				if(x === 0){ ctx.moveTo(x, y + wave); }else{ ctx.lineTo(x, y + wave); }
			}
			ctx.stroke();
		}
		return;
	}

	if(id === 'Jupiter' || id === 'Saturn'){
		const stripeColors = id === 'Jupiter'
			? ['rgba(92,47,29,0.32)', 'rgba(255,239,202,0.38)', 'rgba(177,89,44,0.36)']
			: ['rgba(132,99,54,0.24)', 'rgba(255,241,190,0.3)', 'rgba(88,68,50,0.18)'];
		for(let i = 0; i < 15; i += 1){
			const y = (i / 15) * height;
			ctx.fillStyle = stripeColors[i % stripeColors.length];
			ctx.fillRect(0, y, width, 8 + noise2(i, 0, 7) * 15);
		}
		if(id === 'Jupiter'){
			drawEllipse(ctx, width * 0.68, height * 0.58, width * 0.07, height * 0.095, '#b75a38', 0.82);
			drawEllipse(ctx, width * 0.68, height * 0.58, width * 0.043, height * 0.058, '#edb17b', 0.58);
		}
		return;
	}

	if(id === 'Uranus' || id === 'Neptune' || id === 'Venus'){
		for(let i = 0; i < 18; i += 1){
			ctx.strokeStyle = id === 'Venus' ? 'rgba(255,244,216,0.2)' : 'rgba(232,255,255,0.18)';
			ctx.lineWidth = 2 + noise2(i, 1, 12) * 5;
			ctx.beginPath();
			const y = (i / 18) * height;
			for(let x = 0; x <= width; x += 28){
				const wave = Math.sin(x * 0.014 + i * 0.9) * 8;
				if(x === 0){ ctx.moveTo(x, y + wave); }else{ ctx.lineTo(x, y + wave); }
			}
			ctx.stroke();
		}
		return;
	}

	for(let i = 0; i < 80; i += 1){
		const x = noise2(i, 3, 1) * width;
		const y = noise2(i, 5, 2) * height;
		const r = 1.5 + noise2(i, 9, 3) * (id === 'Moon' || id === 'Mercury' ? 12 : 7);
		const color = id === 'Mars' ? '#5b241d' : 'rgba(34,38,42,0.28)';
		drawEllipse(ctx, x, y, r, r * (0.55 + noise2(i, 8, 4) * 0.55), color, 0.32);
	}
}

function paintMoonPhase(ctx, phase, size){
	const radius = size * 0.45;
	const cx = size / 2;
	const cy = size / 2;
	const angle = degToRad(Number(phase && phase.phaseAngle) || 0);
	const cosA = Math.cos(angle);
	const image = ctx.createImageData(size, size);
	for(let y = 0; y < size; y += 1){
		for(let x = 0; x < size; x += 1){
			const nx = (x - cx) / radius;
			const ny = (y - cy) / radius;
			const idx = (y * size + x) * 4;
			const d = nx * nx + ny * ny;
			if(d > 1){
				image.data[idx + 3] = 0;
				continue;
			}
			const limb = Math.sqrt(Math.max(0, 1 - ny * ny));
			const lit = angle <= Math.PI ? nx > cosA * limb : nx < -cosA * limb;
			const shade = clamp(1 - d * 0.22 + noise2(x, y, 13) * 0.05, 0, 1);
			const v = lit ? Math.round(170 + shade * 76) : Math.round(20 + shade * 26);
			image.data[idx] = v;
			image.data[idx + 1] = v + (lit ? 2 : 0);
			image.data[idx + 2] = v + (lit ? 8 : 4);
			image.data[idx + 3] = 255;
		}
	}
	ctx.putImageData(image, 0, 0);
	ctx.save();
	ctx.beginPath();
	ctx.arc(cx, cy, radius, 0, Math.PI * 2);
	ctx.clip();
	for(let i = 0; i < 42; i += 1){
		const x = cx + (noise2(i, 1, 21) * 2 - 1) * radius * 0.86;
		const y = cy + (noise2(i, 2, 22) * 2 - 1) * radius * 0.86;
		const dx = (x - cx) / radius;
		const dy = (y - cy) / radius;
		if(dx * dx + dy * dy > 0.92){ continue; }
		const r = 3 + noise2(i, 3, 23) * 16;
		ctx.strokeStyle = 'rgba(18,24,32,0.22)';
		ctx.lineWidth = 1 + noise2(i, 4, 24) * 2;
		ctx.beginPath();
		ctx.ellipse(x, y, r, r * (0.74 + noise2(i, 5, 25) * 0.38), 0, 0, Math.PI * 2);
		ctx.stroke();
	}
	ctx.restore();
}

function buildObservationTime(fields){
	const dt = fields && fields.time && fields.time.value && fields.time.value.clone
		? fields.time.value.clone()
		: new DateTime();
	if(fields && fields.date && fields.date.value){
		const d = fields.date.value;
		dt.year = d.year;
		dt.month = d.month;
		dt.date = d.date;
		dt.ad = d.ad;
	}
	if(fields && fields.zone){
		dt.zone = fields.zone.value;
	}
	dt.calcJdn();
	return dt;
}

function buildRequestParams(fields, time){
	return {
		date: time.format('YYYY/MM/DD'),
		time: time.format('HH:mm:ss'),
		ad: time.ad,
		zone: time.zone,
		lat: fields.lat.value,
		lon: fields.lon.value,
		gpsLat: fields.gpsLat.value,
		gpsLon: fields.gpsLon.value,
		name: fields.name ? fields.name.value : null,
		pos: fields.pos ? fields.pos.value : null,
		hsys: fields.hsys ? fields.hsys.value : 1,
		zodiacal: fields.zodiacal ? fields.zodiacal.value : 0,
		doubingSu28: fields.doubingSu28 ? fields.doubingSu28.value : 0,
		southchart: fields.southchart ? fields.southchart.value : 0,
		starLimit: 9000,
	};
}

function buildPlaybackSyncParams(fields, time){
	return {
		...buildRequestParams(fields, time),
		starLimit: 0,
		includeOverlays: false,
		includeTraditions: false,
	};
}

function buildSceneSyncParams(fields, time){
	return {
		...buildRequestParams(fields, time),
		starLimit: 0,
		includeOverlays: true,
		includeTraditions: true,
	};
}

class PlanetariumRenderer {
	constructor(canvas, onPick, onMetrics){
		this.canvas = canvas;
		this.onPick = onPick;
		this.onMetrics = onMetrics;
		this.engine = new BABYLON.Engine(canvas, true, {
			preserveDrawingBuffer: false,
			stencil: false,
			antialias: true,
			powerPreference: 'high-performance',
		});
		this.scene = new BABYLON.Scene(this.engine);
		this.scene.clearColor = new BABYLON.Color4(0.008, 0.012, 0.026, 1);
		this.scene.ambientColor = new BABYLON.Color3(0.12, 0.16, 0.3);
		this.groups = [];
		this.pickMeshes = [];
		this.bodyMeshes = {};
		this.projectableMeshes = [];
		this.projectableLines = [];
		this.followMeshes = [];
		this.starPcs = null;
		this.starMesh = null;
		this.starCount = 0;
		this.starCatalog = [];
		this.starBuildPending = false;
		this.lastData = null;
		this.disposed = false;
		this.viewMode = 'ground';
		this.layers = {...DEFAULT_LAYERS};
		this.initScene();
	}

	initScene(){
		const CameraCtor = BABYLON.UniversalCamera || BABYLON.FreeCamera;
		this.groundCamera = new CameraCtor(
			'planetarium-ground-camera',
			new BABYLON.Vector3(0, OBSERVER_EYE_HEIGHT, 0),
			this.scene,
		);
		this.groundCamera.minZ = 0.5;
		this.groundCamera.maxZ = SKY_RADIUS * 3;
		this.groundCamera.fov = 1.08;
		this.groundCamera.inertia = 0.45;
		this.groundCamera.angularSensibility = 1600;
		this.groundCamera.speed = 0;
		this.groundCamera.setTarget(new BABYLON.Vector3(0, 110, 760));
		if(this.groundCamera.inputs && this.groundCamera.inputs.removeByType){
			this.groundCamera.inputs.removeByType('FreeCameraKeyboardMoveInput');
			this.groundCamera.inputs.removeByType('FreeCameraGamepadInput');
		}

		this.orbitCamera = new BABYLON.ArcRotateCamera(
			'planetarium-orbit-camera',
			Math.PI * 1.25,
			Math.PI * 0.42,
			1120,
			BABYLON.Vector3.Zero(),
			this.scene,
		);
		this.orbitCamera.lowerRadiusLimit = 180;
		this.orbitCamera.upperRadiusLimit = 1400;
		this.orbitCamera.wheelPrecision = 45;
		this.orbitCamera.panningSensibility = 0;

		this.wheelHandler = (evt)=>{
			if(!this.camera){
				return;
			}
			evt.preventDefault();
			if(this.viewMode === 'orbit'){
				this.camera.radius = clamp(this.camera.radius + (evt.deltaY > 0 ? 42 : -42), 180, 1400);
				return;
			}
			this.camera.fov = clamp(this.camera.fov + (evt.deltaY > 0 ? 0.06 : -0.06), 0.34, 1.24);
		};
		this.canvas.addEventListener('wheel', this.wheelHandler, { passive: false });

		const light = new BABYLON.HemisphericLight('planetarium-light', new BABYLON.Vector3(0, 1, 0), this.scene);
		light.intensity = 0.38;

		const sky = BABYLON.MeshBuilder.CreateSphere('sky-shell', { diameter: SKY_RADIUS * 2, segments: 96, sideOrientation: BABYLON.Mesh.BACKSIDE }, this.scene);
		sky.isPickable = false;
		sky.alwaysSelectAsActiveMesh = true;
		sky.infiniteDistance = true;
		const skyMat = new BABYLON.StandardMaterial('sky-material', this.scene);
		skyMat.disableLighting = true;
		skyMat.disableDepthWrite = true;
		skyMat.backFaceCulling = false;
		skyMat.emissiveColor = new BABYLON.Color3(0.006, 0.011, 0.032);
		skyMat.alpha = 1;
		sky.material = skyMat;
		this.skyMat = skyMat;

		const horizonGlow = BABYLON.MeshBuilder.CreateTorus('horizon-glow', { diameter: LINE_RADIUS * 2, thickness: 10, tessellation: 192 }, this.scene);
		horizonGlow.rotation.x = Math.PI / 2;
		horizonGlow.isPickable = false;
		horizonGlow.material = this.material('horizon-glow-material', new BABYLON.Color3(0.08, 0.22, 0.38), 0.18);
		this.horizonGlow = horizonGlow;

		const groundOccluder = BABYLON.MeshBuilder.CreateGround('ground-horizon-occluder', {
			width: SKY_RADIUS * 4.8,
			height: SKY_RADIUS * 4.8,
			subdivisions: 1,
		}, this.scene);
		groundOccluder.position.y = -0.8;
		groundOccluder.isPickable = false;
		groundOccluder.alwaysSelectAsActiveMesh = true;
		const groundMat = new BABYLON.StandardMaterial('ground-horizon-occluder-material', this.scene);
		groundMat.disableLighting = true;
		groundMat.diffuseColor = new BABYLON.Color3(0.004, 0.007, 0.014);
		groundMat.emissiveColor = new BABYLON.Color3(0.004, 0.007, 0.014);
		groundMat.specularColor = BABYLON.Color3.Black();
		groundOccluder.material = groundMat;
		this.groundOccluder = groundOccluder;

		this.setViewMode('ground');

		this.glow = null;
		this.sky = sky;

		this.scene.onPointerObservable.add((pointerInfo)=>{
			if(pointerInfo.type !== BABYLON.PointerEventTypes.POINTERPICK){
				return;
			}
			const hit = pointerInfo.pickInfo && pointerInfo.pickInfo.pickedMesh;
			if(hit && hit.metadata && hit.metadata.body && this.onPick){
				this.onPick(hit.metadata.body);
			}
		});

		this.engine.runRenderLoop(()=>{
			if(this.scene){
				this.applyLabelVisibility();
				this.scene.render();
				if(this.onMetrics){
					const fps = Math.round(this.engine.getFps());
					this.onMetrics({
						fps: Number.isFinite(fps) ? Math.min(240, Math.max(0, fps)) : 0,
						meshes: this.scene.meshes.length,
					});
				}
			}
		});
		this.resizeHandler = ()=>{
			if(this.engine){
				this.engine.resize();
			}
		};
		window.addEventListener('resize', this.resizeHandler);
	}

	setLayers(layers){
		this.layers = {...this.layers, ...(layers || {})};
		this.applyLayerVisibility();
	}

	setViewMode(mode){
		const nextMode = mode === 'orbit' ? 'orbit' : 'ground';
		const nextCamera = nextMode === 'orbit' ? this.orbitCamera : this.groundCamera;
		if(!nextCamera){
			return;
		}
		if(this.camera && this.camera.detachControl){
			this.camera.detachControl(this.canvas);
		}
		this.viewMode = nextMode;
		this.camera = nextCamera;
		this.scene.activeCamera = nextCamera;
		nextCamera.attachControl(this.canvas, true);
		if(nextMode === 'ground'){
			this.groundCamera.position = new BABYLON.Vector3(0, OBSERVER_EYE_HEIGHT, 0);
		}
		if(this.groundOccluder){
			this.groundOccluder.setEnabled(nextMode === 'ground');
		}
		this.applyLabelVisibility();
	}

	clearData(){
		this.pickMeshes = [];
		this.bodyMeshes = {};
		this.projectableMeshes = [];
		this.projectableLines = [];
		this.followMeshes = [];
		this.groups.forEach((group)=>{
			group.dispose(false, true);
		});
		this.groups = [];
		this.starPcs = null;
		this.starMesh = null;
		this.starCount = 0;
		this.starCatalog = [];
	}

	makeGroup(name){
		const group = new BABYLON.TransformNode(name, this.scene);
		this.groups.push(group);
		return group;
	}

	material(name, color, alpha = 1){
		const mat = new BABYLON.StandardMaterial(name, this.scene);
		mat.disableLighting = true;
		mat.emissiveColor = color;
		mat.diffuseColor = color;
		mat.alpha = alpha;
		return mat;
	}

	createSurfaceTexture(id, phase){
		const size = planetTextureSize(id);
		const texture = new BABYLON.DynamicTexture(`surface-${id}-${Math.random()}`, size, this.scene, true);
		texture.hasAlpha = id === 'Moon';
		const ctx = texture.getContext();
		if(id === 'Moon'){
			paintMoonPhase(ctx, phase || this.currentMoonPhase, size.width);
		}else{
			paintPlanetSurface(ctx, id, size.width, size.height);
		}
		texture.update(true);
		return texture;
	}

	createBodyMaterial(body){
		const id = body.id;
		const color = BODY_COLORS[id] || new BABYLON.Color3(0.9, 0.9, 1);
		if(!TEXTURED_BODY_IDS.has(id)){
			return this.material(`body-mat-${id}`, color, 1);
		}
		const mat = new BABYLON.StandardMaterial(`body-surface-mat-${id}-${Math.random()}`, this.scene);
		const texture = this.createSurfaceTexture(id, id === 'Moon' ? this.currentMoonPhase : null);
		mat.diffuseTexture = texture;
		mat.emissiveTexture = id === 'Sun' ? texture : null;
		mat.diffuseColor = color;
		mat.specularColor = id === 'Sun' ? new BABYLON.Color3(0.9, 0.45, 0.16) : new BABYLON.Color3(0.05, 0.06, 0.08);
		mat.emissiveColor = id === 'Sun'
			? new BABYLON.Color3(1, 0.48, 0.12)
			: color.scale(id === 'Moon' ? 0.72 : 0.18);
		mat.disableLighting = id === 'Sun';
		mat.useAlphaFromDiffuseTexture = id === 'Moon';
		return mat;
	}

	createBodyHalo(mesh, body, group){
		const id = body.id;
		if(id !== 'Sun' && id !== 'Venus' && id !== 'Jupiter'){
			return;
		}
		const color = BODY_COLORS[id] || new BABYLON.Color3(1, 1, 1);
		const scale = id === 'Sun' ? 2.2 : 1.55;
		const halo = BABYLON.MeshBuilder.CreateSphere(`body-halo-${id}`, { diameter: mesh.getBoundingInfo().boundingSphere.radius * 2 * scale, segments: 24 }, this.scene);
		halo.position.copyFrom(mesh.position);
		halo.material = this.material(`body-halo-mat-${id}`, color, id === 'Sun' ? 0.18 : 0.08);
		halo.parent = group;
		halo.isPickable = false;
		this.registerFollowerMesh(halo, id, ()=>BABYLON.Vector3.Zero());
	}

	createSaturnRing(mesh, group){
		const ring = BABYLON.MeshBuilder.CreateTorus('saturn-ring', { diameter: 28, thickness: 2.2, tessellation: 96 }, this.scene);
		ring.position.copyFrom(mesh.position);
		ring.rotation.x = Math.PI * 0.58;
		ring.rotation.z = Math.PI * 0.12;
		ring.scaling.y = 0.38;
		ring.material = this.material('saturn-ring-mat', new BABYLON.Color3(0.95, 0.82, 0.55), 0.72);
		ring.parent = group;
		ring.isPickable = false;
		this.registerFollowerMesh(ring, 'Saturn', ()=>BABYLON.Vector3.Zero());
	}

	createMoonPhaseDisc(body, mesh, group){
		const texture = this.createSurfaceTexture('Moon', this.currentMoonPhase);
		const mat = new BABYLON.StandardMaterial(`moon-phase-disc-mat-${Math.random()}`, this.scene);
		mat.diffuseTexture = texture;
		mat.emissiveTexture = texture;
		mat.opacityTexture = texture;
		mat.disableLighting = true;
		mat.useAlphaFromDiffuseTexture = true;
		const disc = BABYLON.MeshBuilder.CreatePlane('moon-phase-disc', { width: 22, height: 22 }, this.scene);
		disc.position = mesh.position.add(mesh.position.clone().normalize().scale(2.5));
		disc.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;
		disc.material = mat;
		disc.parent = group;
		disc.metadata = { body: { ...body, displayName: bodyName(body), layer: 'body' } };
		this.pickMeshes.push(disc);
		this.registerFollowerMesh(disc, 'Moon', (target)=>target.position.clone().normalize().scale(2.5));
	}

	createEarthAnchor(group){
		const body = {
			id: 'Earth',
			name: 'Earth',
			displayName: '地球',
			layer: 'body',
			type: '地球/观测点',
			altitudeAppa: -90,
			azimuth: 0,
			visible: false,
			horizonState: '脚下地球',
		};
		const mesh = BABYLON.MeshBuilder.CreateSphere('body-Earth', { diameter: 34, segments: 32 }, this.scene);
		mesh.position = new BABYLON.Vector3(0, -BODY_RADIUS + 74, 0);
		mesh.material = this.createBodyMaterial(body);
		mesh.parent = group;
		mesh.metadata = { body };
		this.pickMeshes.push(mesh);
		this.bodyMeshes.Earth = mesh;
		this.bodyMeshes['地球'] = mesh;
		const label = this.createTextPlane('地球', 40, '#d8ecff', 'rgba(0,0,0,0)');
		label.position = mesh.position.add(new BABYLON.Vector3(0, 26, 0));
		label.parent = group;
		label.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;
		label.metadata = { labelKind: 'body' };
	}

	updateData(data, layers){
		this.layers = {...DEFAULT_LAYERS, ...(layers || {})};
		if(!data){
			return;
		}
		this.lastData = data;
		this.currentMoonPhase = data.sky && data.sky.moonPhase ? data.sky.moonPhase : null;
		const started = nowMs();
		const hasStarCatalog = !!(data.stars && data.stars.catalog && data.stars.catalog.length);
		this.updateSky(data);
		this.clearDynamicData(!hasStarCatalog && !!this.starPcs);
		this.createCardinals();
		this.updateStars(data.stars && data.stars.catalog ? data.stars.catalog : []);
		this.createOverlayLines(data.overlays || {});
		this.createBodies(data.bodies || []);
		this.createTraditionalLayer('su28', data.traditions && data.traditions.su28 ? data.traditions.su28 : [], new BABYLON.Color3(0.9, 0.68, 0.36), 4.8);
		this.createTraditionalLayer('beidou', data.traditions && data.traditions.beidou ? data.traditions.beidou : [], new BABYLON.Color3(0.52, 0.82, 1), 6.2);
		this.applyLayerVisibility();
		return Math.round(nowMs() - started);
	}

	applyPlaybackCalibration(data, time, fields){
		if(!data){
			return 0;
		}
		const started = nowMs();
		this.lastData = {
			...(this.lastData || {}),
			...data,
			stars: this.lastData && this.lastData.stars ? this.lastData.stars : data.stars,
			overlays: this.lastData && this.lastData.overlays ? this.lastData.overlays : data.overlays,
			traditions: this.lastData && this.lastData.traditions ? this.lastData.traditions : data.traditions,
		};
		this.currentMoonPhase = data.sky && data.sky.moonPhase ? data.sky.moonPhase : this.currentMoonPhase;
		this.updateSky(data);
		const bodiesById = {};
		(data.bodies || []).forEach((body)=>{
			if(body && body.id){
				bodiesById[body.id] = body;
			}
		});
		this.projectableMeshes.forEach((item)=>{
			const body = item.source && item.source.id ? bodiesById[item.source.id] : null;
			if(body){
				item.source = body;
				item.mesh.position = toSkyVector(body, item.radius);
				if(item.mesh.metadata && item.mesh.metadata.body){
					item.mesh.metadata.body = { ...item.mesh.metadata.body, ...body, displayName: bodyName(body), layer: 'body' };
				}
			}
		});
		this.updateFollowers();
		this.updateProjectedTime(time, fields);
		return Math.round(nowMs() - started);
	}

	updateProjectedTime(time, fields){
		if(!time || !this.lastData){
			return 0;
		}
		const started = nowMs();
		const jd = time.jdn || time.calcJdn();
		const observer = observerFromFields(fields, this.lastData);
		if(this.starPcs && this.starPcs.particles && this.starCatalog && this.starCatalog.length === this.starPcs.particles.length){
			this.starCatalog.forEach((star, idx)=>{
				const particle = this.starPcs.particles[idx];
				if(!particle){
					return;
				}
				const projected = projectedEquatorialItem(star, jd, observer);
				particle.position = toSkyVector(projected, STAR_RADIUS);
			});
			this.starPcs.setParticles();
		}
		this.projectableMeshes.forEach((item)=>{
			const projected = projectedEquatorialItem(item.source, jd, observer);
			if(!projected || !item.mesh){
				return;
			}
			item.mesh.position = toSkyVector(projected, item.radius);
			if(item.mesh.metadata && item.mesh.metadata.body){
				item.mesh.metadata.body = {
					...item.mesh.metadata.body,
					altitudeAppa: projected.altitudeAppa,
					azimuth: projected.azimuth,
					visible: projected.visible,
					horizonState: projected.horizonState,
				};
			}
		});
		this.projectableLines.forEach((item)=>{
			if(!item || !item.mesh || !item.sources || !item.sources.length){
				return;
			}
			let vectors = null;
			if(item.innerRadius !== undefined && item.sources.length === 1){
				const projected = projectedEquatorialItem(item.sources[0], jd, observer);
				vectors = [
					toSkyVector(projected, item.radius),
					toSkyVector(projected, item.innerRadius),
				];
			}else{
				vectors = item.sources.map((source)=>toSkyVector(projectedEquatorialItem(source, jd, observer), item.radius));
			}
			BABYLON.MeshBuilder.CreateLines(item.mesh.name, {
				points: vectors,
				instance: item.mesh,
			});
		});
		this.updateFollowers();
		return Math.round(nowMs() - started);
	}

	clearDynamicData(preserveStars = false){
		if(preserveStars){
			const isBrightStarMesh = (mesh)=>mesh && mesh.name && mesh.name.indexOf('bright-star-') === 0;
			const retainedBodyMeshes = {};
			Object.keys(this.bodyMeshes || {}).forEach((key)=>{
				const mesh = this.bodyMeshes[key];
				if(isBrightStarMesh(mesh)){
					retainedBodyMeshes[key] = mesh;
				}
			});
			this.pickMeshes = (this.pickMeshes || []).filter(isBrightStarMesh);
			this.bodyMeshes = retainedBodyMeshes;
			this.projectableMeshes = (this.projectableMeshes || []).filter((item)=>isBrightStarMesh(item && item.mesh));
			this.projectableLines = [];
			this.followMeshes = [];
			const keep = [];
			this.groups.forEach((group)=>{
				if(group.name.indexOf('stars-layer') === 0 || group.name.indexOf('bright-stars-layer') === 0){
					keep.push(group);
				}else{
					group.dispose(false, true);
				}
			});
			this.groups = keep;
			return;
		}
		this.pickMeshes = [];
		this.bodyMeshes = {};
		this.projectableMeshes = [];
		this.projectableLines = [];
		this.followMeshes = [];
		const keep = [];
		this.groups.forEach((group)=>{
			if(group.name.indexOf('stars-layer') === 0){
				keep.push(group);
			}else{
				group.dispose(false, true);
			}
		});
		this.groups = keep;
	}

	registerProjectableMesh(mesh, source, radius){
		if(!mesh || !source){
			return;
		}
		this.projectableMeshes.push({ mesh, source, radius });
	}

	registerProjectableLine(mesh, sources, radius, innerRadius){
		if(!mesh || !sources || !sources.length){
			return;
		}
		this.projectableLines.push({ mesh, sources, radius, innerRadius });
	}

	registerFollowerMesh(mesh, targetId, offsetFactory){
		if(!mesh || !targetId){
			return;
		}
		this.followMeshes.push({ mesh, targetId, offsetFactory });
	}

	updateFollowers(){
		this.followMeshes.forEach((item)=>{
			const target = this.bodyMeshes[item.targetId];
			if(!target || !target.position || !item.mesh){
				return;
			}
			const offset = typeof item.offsetFactory === 'function' ? item.offsetFactory(target) : BABYLON.Vector3.Zero();
			item.mesh.position = target.position.add(offset || BABYLON.Vector3.Zero());
		});
	}

	updateSky(data){
		const sky = data && data.sky ? data.sky : {};
		const mode = sky.mode || 'night';
		const palettes = {
			day: { clear: [0.26, 0.43, 0.68], sky: [0.22, 0.42, 0.74], glow: [0.56, 0.72, 0.9], glowAlpha: 0.28 },
			civilTwilight: { clear: [0.11, 0.16, 0.32], sky: [0.12, 0.15, 0.36], glow: [0.86, 0.46, 0.22], glowAlpha: 0.24 },
			nauticalTwilight: { clear: [0.035, 0.055, 0.13], sky: [0.035, 0.055, 0.16], glow: [0.35, 0.43, 0.72], glowAlpha: 0.18 },
			astronomicalTwilight: { clear: [0.012, 0.02, 0.055], sky: [0.01, 0.018, 0.052], glow: [0.14, 0.24, 0.48], glowAlpha: 0.13 },
			night: { clear: [0.004, 0.006, 0.014], sky: [0.004, 0.007, 0.022], glow: [0.04, 0.11, 0.22], glowAlpha: 0.08 },
		};
		const p = palettes[mode] || palettes.night;
		this.scene.clearColor = new BABYLON.Color4(p.clear[0], p.clear[1], p.clear[2], 1);
		if(this.skyMat){
			this.skyMat.emissiveColor = new BABYLON.Color3(p.sky[0], p.sky[1], p.sky[2]);
		}
		if(this.horizonGlow && this.horizonGlow.material){
			this.horizonGlow.material.emissiveColor = new BABYLON.Color3(p.glow[0], p.glow[1], p.glow[2]);
			this.horizonGlow.material.alpha = p.glowAlpha;
		}
	}

	createCardinals(){
		const group = this.makeGroup('cardinals');
		[
			{ label: '南', azimuth: 0 },
			{ label: '西', azimuth: 90 },
			{ label: '北', azimuth: 180 },
			{ label: '东', azimuth: 270 },
		].forEach((item)=>{
			const plane = this.createTextPlane(item.label, 84, '#d7e9ff', 'rgba(8,16,34,0.1)');
			plane.position = toSkyVector({...item, altitudeAppa: 2}, LINE_RADIUS);
			plane.parent = group;
			plane.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;
			plane.metadata = { labelKind: 'cardinal' };
		});
	}

	createTextPlane(text, size, color, bg){
		const texture = new BABYLON.DynamicTexture(`label-${text}-${Math.random()}`, { width: 256, height: 128 }, this.scene, true);
		texture.hasAlpha = true;
		const ctx = texture.getContext();
		ctx.clearRect(0, 0, 256, 128);
		ctx.fillStyle = bg || 'rgba(0,0,0,0)';
		ctx.fillRect(0, 0, 256, 128);
		texture.drawText(text, null, 78, `600 ${size || 48}px sans-serif`, color || '#fff', null, true, true);
		const mat = new BABYLON.StandardMaterial(`label-mat-${text}-${Math.random()}`, this.scene);
		mat.diffuseTexture = texture;
		mat.emissiveTexture = texture;
		mat.opacityTexture = texture;
		mat.disableLighting = true;
		mat.useAlphaFromDiffuseTexture = true;
		const plane = BABYLON.MeshBuilder.CreatePlane(`label-${text}`, { width: 58, height: 29 }, this.scene);
		plane.material = mat;
		plane.isPickable = false;
		return plane;
	}

	updateStars(stars){
		if(!stars || !stars.length){
			return;
		}
		this.starCatalog = stars;
		if(this.starPcs && this.starPcs.particles && this.starPcs.particles.length === stars.length && this.starPcs.setParticles){
			stars.forEach((star, idx)=>{
				const particle = this.starPcs.particles[idx];
				if(!particle){
					return;
				}
				const mag = Number(star.mag || 5);
				particle.position = toSkyVector(star, STAR_RADIUS);
				const b = Math.max(0.18, Math.min(1.0, 1.18 - mag / 6.5));
				const c = starTemperatureColor(star, b);
				particle.color = new BABYLON.Color4(c.r, c.g, c.b, Math.max(0.14, b * 0.86));
			});
			this.starPcs.setParticles();
			this.updateBrightStars(stars);
			return;
		}
		if(this.starBuildPending){
			return;
		}
		const oldGroup = this.groups.find((group)=>group.name.indexOf('stars-layer') === 0);
		if(oldGroup){
			oldGroup.dispose(false, true);
			this.groups = this.groups.filter((group)=>group !== oldGroup);
		}
		const group = this.makeGroup('stars-layer');
		const pcs = new BABYLON.PointsCloudSystem('star-point-cloud', 1.22, this.scene);
		this.starBuildPending = true;
		pcs.addPoints(stars.length, (particle, idx)=>{
			const star = stars[idx];
			const mag = Number(star.mag || 5);
			particle.position = toSkyVector(star, STAR_RADIUS);
			const b = Math.max(0.18, Math.min(1.0, 1.18 - mag / 6.5));
			const c = starTemperatureColor(star, b);
			particle.color = new BABYLON.Color4(c.r, c.g, c.b, Math.max(0.14, b * 0.86));
		});
		pcs.buildMeshAsync().then((mesh)=>{
			if(this.disposed || !this.scene){
				return;
			}
			mesh.parent = group;
			mesh.isPickable = false;
			this.starPcs = pcs;
			this.starMesh = mesh;
			this.starCount = stars.length;
			this.starBuildPending = false;
			this.applyLayerVisibility();
			this.updateBrightStars(stars);
		}).catch(()=>{
			this.starBuildPending = false;
		});
	}

	updateBrightStars(stars){
		const oldGroup = this.groups.find((group)=>group.name.indexOf('bright-stars-layer') === 0);
		if(oldGroup){
			oldGroup.dispose(false, true);
			this.groups = this.groups.filter((group)=>group !== oldGroup);
		}
		const group = this.makeGroup('bright-stars-layer');
		(stars || []).filter((star)=>Number(star.mag) <= 1.5).slice(0, 80).forEach((star)=>{
			const b = Math.max(0.35, Math.min(1.0, 1.18 - Number(star.mag || 0) / 6.5));
			const c = starTemperatureColor(star, b);
			const mesh = BABYLON.MeshBuilder.CreateSphere(`bright-star-${star.id}`, { diameter: 2.4 + b * 4.4, segments: 8 }, this.scene);
			mesh.position = toSkyVector(star, STAR_RADIUS + 2);
			mesh.material = this.material(`bright-star-mat-${star.id}`, new BABYLON.Color3(c.r, c.g, c.b), 0.88);
			mesh.parent = group;
			mesh.metadata = { body: { ...star, displayName: star.name || star.id, layer: 'stars' } };
			this.pickMeshes.push(mesh);
			this.registerProjectableMesh(mesh, star, STAR_RADIUS + 2);
			if(star.name){ this.bodyMeshes[star.name] = mesh; }
			if(star.id){ this.bodyMeshes[star.id] = mesh; }
		});
	}

	createLine(name, points, color, alpha, parent, radius, projectable = false){
		if(!points || points.length < 2){
			return null;
		}
		const vectors = points.map((p)=>toSkyVector(p, radius || LINE_RADIUS));
		const line = BABYLON.MeshBuilder.CreateLines(name, { points: vectors, updatable: true }, this.scene);
		line.color = color;
		line.alpha = alpha === undefined ? 1 : alpha;
		line.parent = parent;
		line.isPickable = false;
		if(projectable){
			this.registerProjectableLine(line, points, radius || LINE_RADIUS);
		}
		return line;
	}

	createShortRadialLine(name, item, color, alpha, parent, outerRadius, innerRadius, projectable = false){
		if(!item){
			return null;
		}
		const p1 = toSkyVector(item, outerRadius);
		const p2 = toSkyVector(item, innerRadius);
		const line = BABYLON.MeshBuilder.CreateLines(name, { points: [p1, p2], updatable: true }, this.scene);
		line.color = color;
		line.alpha = alpha;
		line.parent = parent;
		line.isPickable = false;
		if(projectable){
			this.registerProjectableLine(line, [item], outerRadius, innerRadius);
		}
		return line;
	}

	createOverlayLines(overlays){
		const group = this.makeGroup('overlay-layer');
		this.createLine('horizon', overlays.horizon && overlays.horizon.points, new BABYLON.Color3(0.48, 0.82, 0.96), 0.5, group, LINE_RADIUS);
		this.createLine('meridian', overlays.meridian && overlays.meridian.points, new BABYLON.Color3(0.48, 0.68, 0.88), 0.18, group, LINE_RADIUS - 2);
		this.createLine('equator', overlays.equator && overlays.equator.points, new BABYLON.Color3(0.42, 0.54, 0.92), 0.2, group, LINE_RADIUS - 4, true);
		this.createLine('ecliptic', overlays.ecliptic && overlays.ecliptic.points, new BABYLON.Color3(1.0, 0.7, 0.22), 0.82, group, LINE_RADIUS + 14, true);
		(overlays.houses || []).forEach((item)=>{
			this.createShortRadialLine(`house-${item.id}`, item, new BABYLON.Color3(0.48, 0.82, 0.68), 0.22, group, LINE_RADIUS + 20, LINE_RADIUS - 46, true);
		});
	}

	createBodies(bodies){
		const group = this.makeGroup('body-layer');
		bodies.forEach((body)=>{
			const diameter = body.id === 'Sun' ? 24 : (body.id === 'Moon' ? 17 : (body.id === 'Jupiter' || body.id === 'Saturn' ? 15 : 12));
			const mesh = BABYLON.MeshBuilder.CreateSphere(`body-${body.id}`, { diameter, segments: TEXTURED_BODY_IDS.has(body.id) ? 32 : 18 }, this.scene);
			mesh.position = toSkyVector(body, BODY_RADIUS);
			mesh.material = this.createBodyMaterial(body);
			mesh.parent = group;
			mesh.metadata = { body: { ...body, displayName: bodyName(body), layer: 'body' } };
			this.pickMeshes.push(mesh);
			this.bodyMeshes[body.id] = mesh;
			this.bodyMeshes[bodyName(body)] = mesh;
			this.registerProjectableMesh(mesh, body, BODY_RADIUS);
			this.createBodyHalo(mesh, body, group);
			if(body.id === 'Moon'){
				this.createMoonPhaseDisc(body, mesh, group);
			}
			if(body.id === 'Saturn'){
				this.createSaturnRing(mesh, group);
			}

			if(body.id === 'Sun' || body.id === 'Moon' || body.id === 'Jupiter' || body.id === 'Saturn'){
				const label = this.createTextPlane(bodyName(body), 42, '#f4f7ff', 'rgba(0,0,0,0)');
				label.position = mesh.position.add(new BABYLON.Vector3(0, 24, 0));
				label.parent = group;
				label.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;
				label.metadata = { labelKind: 'body' };
				this.registerFollowerMesh(label, body.id, ()=>new BABYLON.Vector3(0, 24, 0));
			}
		});
		this.createEarthAnchor(group);
	}

	applyLabelVisibility(){
		if(!this.camera || !this.scene){
			return;
		}
		const showBody = this.viewMode === 'orbit'
			? this.camera.radius < 1040
			: this.camera.fov < 1.12;
		this.scene.meshes.forEach((mesh)=>{
			const kind = mesh.metadata && mesh.metadata.labelKind;
			if(kind === 'body'){
				mesh.setEnabled(showBody);
			}
		});
	}

	createTraditionalLayer(kind, items, color, diameter){
		const group = this.makeGroup(`${kind}-layer`);
		items.forEach((item)=>{
			const mesh = BABYLON.MeshBuilder.CreateSphere(`${kind}-${item.id || item.name}`, { diameter: diameter || 5, segments: 8 }, this.scene);
			mesh.position = toSkyVector(item, BODY_RADIUS - 28);
			mesh.material = this.material(`${kind}-mat-${item.id || item.name}`, color, 0.9);
			mesh.parent = group;
			mesh.metadata = { body: { ...item, displayName: item.name || item.id, layer: kind } };
			this.pickMeshes.push(mesh);
			this.registerProjectableMesh(mesh, item, BODY_RADIUS - 28);
			if(item.id){ this.bodyMeshes[item.id] = mesh; }
			if(item.name){ this.bodyMeshes[item.name] = mesh; }
		});
		if(kind === 'beidou' && items.length > 1){
			this.createLine('beidou-line', items, color, 0.72, group, BODY_RADIUS - 28, true);
		}
	}

	flyTo(itemOrKey){
		if(!itemOrKey || !this.camera){
			return false;
		}
		let mesh = null;
		if(typeof itemOrKey === 'string'){
			const key = itemOrKey.trim();
			mesh = this.bodyMeshes[key];
			if(!mesh){
				const found = Object.keys(this.bodyMeshes).find((name)=>name.toLowerCase().indexOf(key.toLowerCase()) >= 0);
				mesh = found ? this.bodyMeshes[found] : null;
			}
		}else{
			mesh = this.bodyMeshes[itemOrKey.id] || this.bodyMeshes[itemOrKey.name] || this.bodyMeshes[itemOrKey.displayName];
		}
		if(!mesh){
			return false;
		}
		const pos = mesh.position;
		if(this.viewMode === 'orbit'){
			const radius = Math.max(360, this.camera.radius * 0.82);
			BABYLON.Animation.CreateAndStartAnimation('planetarium-target-x', this.camera, 'target.x', 60, 36, this.camera.target.x, pos.x * 0.18, BABYLON.Animation.ANIMATIONLOOPMODE_CONSTANT);
			BABYLON.Animation.CreateAndStartAnimation('planetarium-target-y', this.camera, 'target.y', 60, 36, this.camera.target.y, pos.y * 0.18, BABYLON.Animation.ANIMATIONLOOPMODE_CONSTANT);
			BABYLON.Animation.CreateAndStartAnimation('planetarium-target-z', this.camera, 'target.z', 60, 36, this.camera.target.z, pos.z * 0.18, BABYLON.Animation.ANIMATIONLOOPMODE_CONSTANT);
			BABYLON.Animation.CreateAndStartAnimation('planetarium-radius', this.camera, 'radius', 60, 36, this.camera.radius, radius, BABYLON.Animation.ANIMATIONLOOPMODE_CONSTANT);
		}else{
			const rot = cameraRotationForDirection(pos.subtract(this.camera.position));
			BABYLON.Animation.CreateAndStartAnimation('planetarium-look-x', this.camera, 'rotation.x', 60, 32, this.camera.rotation.x, rot.x, BABYLON.Animation.ANIMATIONLOOPMODE_CONSTANT);
			BABYLON.Animation.CreateAndStartAnimation('planetarium-look-y', this.camera, 'rotation.y', 60, 32, this.camera.rotation.y, rot.y, BABYLON.Animation.ANIMATIONLOOPMODE_CONSTANT);
			BABYLON.Animation.CreateAndStartAnimation('planetarium-fov', this.camera, 'fov', 60, 28, this.camera.fov, 0.58, BABYLON.Animation.ANIMATIONLOOPMODE_CONSTANT);
		}
		return mesh.metadata && mesh.metadata.body ? mesh.metadata.body : true;
	}

	applyLayerVisibility(){
		this.groups.forEach((group)=>{
			if(group.name.indexOf('stars-layer') === 0){
				group.setEnabled(!!this.layers.stars);
			}else if(group.name.indexOf('bright-stars-layer') === 0){
				group.setEnabled(!!this.layers.stars);
			}else if(group.name.indexOf('body-layer') === 0){
				group.setEnabled(!!this.layers.bodies);
			}else if(group.name.indexOf('overlay-layer') === 0){
				group.setEnabled(true);
				group.getChildMeshes().forEach((mesh)=>{
					if(mesh.name.indexOf('horizon') >= 0){ mesh.setEnabled(!!this.layers.horizon); }
					else if(mesh.name.indexOf('meridian') >= 0){ mesh.setEnabled(!!this.layers.horizon); }
					else if(mesh.name.indexOf('equator') >= 0){ mesh.setEnabled(!!this.layers.equator); }
					else if(mesh.name.indexOf('ecliptic') >= 0){ mesh.setEnabled(!!this.layers.ecliptic); }
					else if(mesh.name.indexOf('house') >= 0){ mesh.setEnabled(!!this.layers.houses); }
				});
			}else if(group.name.indexOf('su28-layer') === 0){
				group.setEnabled(!!this.layers.su28);
			}else if(group.name.indexOf('beidou-layer') === 0){
				group.setEnabled(!!this.layers.beidou);
			}
		});
	}

	dispose(){
		this.disposed = true;
		window.removeEventListener('resize', this.resizeHandler);
		if(this.wheelHandler){
			this.canvas.removeEventListener('wheel', this.wheelHandler);
		}
		this.clearData();
		if(this.sky){
			this.sky.dispose(false, true);
		}
		if(this.horizonGlow){
			this.horizonGlow.dispose(false, true);
		}
		if(this.groundOccluder){
			this.groundOccluder.dispose(false, true);
		}
		if(this.glow){
			this.glow.dispose();
		}
		if(this.scene){
			this.scene.dispose();
			this.scene = null;
		}
		if(this.engine){
			this.engine.stopRenderLoop();
			this.engine.dispose();
			this.engine = null;
		}
	}
}

class PlanetariumBabylon extends Component{
	constructor(props){
		super(props);
		const time = buildObservationTime(props.fields);
		this.state = {
			time,
			data: null,
			selected: null,
			searchQuery: '',
			searchMessage: '',
			leftCollapsed: false,
			observerOverride: null,
			loading: true,
			syncing: false,
			error: null,
			speed: 0,
			viewMode: 'ground',
			layers: {...DEFAULT_LAYERS},
			metrics: {
				fps: 0,
				meshes: 0,
				loadMs: 0,
				apiMs: 0,
				renderMs: 0,
				runtimeLoadMs: props.runtimeLoadMs || 0,
				firstReadyMs: 0,
				releaseOk: '--',
				catalogCount: 0,
			},
			perfLog: [],
		};
		this.canvasRef = createRef();
		this.renderer = null;
		this.reqSeq = 0;
		this.requestInFlight = false;
		this.playbackSyncInFlight = false;
		this.sceneSyncInFlight = false;
		this.pendingRequestOptions = null;
		this.playTimer = null;
		this.lastPlaybackSyncAt = 0;
		this.metricTimer = null;
		this.mountedAt = nowMs();
		this.firstReadyLogged = false;
		this.requestState = this.requestState.bind(this);
		this.toggleLayer = this.toggleLayer.bind(this);
		this.changeSpeed = this.changeSpeed.bind(this);
		this.jumpNow = this.jumpNow.bind(this);
		this.toggleFullscreen = this.toggleFullscreen.bind(this);
		this.searchTarget = this.searchTarget.bind(this);
		this.setSearchQuery = this.setSearchQuery.bind(this);
		this.stepTime = this.stepTime.bind(this);
		this.toggleLeftPanel = this.toggleLeftPanel.bind(this);
		this.changeViewMode = this.changeViewMode.bind(this);
		this.changeObserverGeo = this.changeObserverGeo.bind(this);
		this.clearObserverOverride = this.clearObserverOverride.bind(this);
	}

	componentDidMount(){
		this._isUnmounted = false;
		this.renderer = new PlanetariumRenderer(
			this.canvasRef.current,
			(selected)=>this.setState({ selected }),
			(metrics)=>{
				if(!this.metricTimer){
					this.metricTimer = setTimeout(()=>{
						this.metricTimer = null;
						this.setState((prev)=>({
							metrics: {
								...prev.metrics,
								...metrics,
							},
						}));
					}, 500);
				}
			},
		);
		this.requestState({ showLoading: true, reason: 'initial' });
	}

	componentDidUpdate(prevProps, prevState){
		if(prevState.layers !== this.state.layers && this.renderer){
			this.renderer.setLayers(this.state.layers);
		}
		if(prevState.speed !== this.state.speed){
			this.setupPlayback();
		}
		if(prevState.viewMode !== this.state.viewMode && this.renderer){
			this.renderer.setViewMode(this.state.viewMode);
		}
		if(prevProps.fields !== this.props.fields){
			const time = buildObservationTime(this.props.fields);
			this.setState({ time }, this.requestState);
		}
	}

	componentWillUnmount(){
		this._isUnmounted = true;
		this.pushPerfLog('release', { canvasReleased: true });
		if(this.playTimer){
			clearInterval(this.playTimer);
			this.playTimer = null;
		}
		if(this.metricTimer){
			clearTimeout(this.metricTimer);
			this.metricTimer = null;
		}
		if(this.renderer){
			this.renderer.dispose();
			this.renderer = null;
		}
	}

	pushPerfLog(event, extra = {}){
		const row = {
			event,
			at: new Date().toISOString(),
			...extra,
		};
		if(typeof window !== 'undefined'){
			window[PLANETARIUM_PERF_KEY] = window[PLANETARIUM_PERF_KEY] || [];
			window[PLANETARIUM_PERF_KEY].push(row);
		}
		if(this._isUnmounted){
			return;
		}
		this.setState((prev)=>({
			perfLog: [row].concat(prev.perfLog || []).slice(0, 8),
		}));
	}

	getEffectiveFields(){
		const fields = this.props.fields || {};
		const observerOverride = this.state.observerOverride;
		if(!observerOverride){
			return fields;
		}
		return {
			...fields,
			lat: {
				...(fields.lat || { name: ['lat'] }),
				value: observerOverride.lat,
			},
			lon: {
				...(fields.lon || { name: ['lon'] }),
				value: observerOverride.lon,
			},
			gpsLat: {
				...(fields.gpsLat || { name: ['gpsLat'] }),
				value: observerOverride.gpsLat,
			},
			gpsLon: {
				...(fields.gpsLon || { name: ['gpsLon'] }),
				value: observerOverride.gpsLon,
			},
			pos: {
				...(fields.pos || { name: ['pos'] }),
				value: observerOverride.label,
			},
		};
	}

	changeObserverGeo(rec){
		if(!rec){
			return;
		}
		const gpsLat = rec.gpsLat !== undefined && rec.gpsLat !== null ? rec.gpsLat : rec.lat;
		const gpsLon = rec.gpsLng !== undefined && rec.gpsLng !== null ? rec.gpsLng : rec.lng;
		this.setState({
			observerOverride: {
				lat: convertLatToStr(rec.lat),
				lon: convertLonToStr(rec.lng),
				gpsLat,
				gpsLon,
				label: '自选观测点',
			},
			selected: null,
			speed: 0,
		}, ()=>this.applyFastSceneChange('observer'));
	}

	clearObserverOverride(){
		if(!this.state.observerOverride){
			return;
		}
		this.setState({
			observerOverride: null,
			selected: null,
			speed: 0,
		}, ()=>this.applyFastSceneChange('observer-reset'));
	}

	setupPlayback(){
		if(this.playTimer){
			clearInterval(this.playTimer);
			this.playTimer = null;
		}
		const speed = Number(this.state.speed || 0);
		if(!speed){
			return;
		}
		const intervalMs = 250;
		this.playTimer = setInterval(()=>{
			this.setState((prev)=>{
				const next = prev.time.clone();
				next.addSecond(speed * intervalMs / 1000);
				return { time: next };
			}, ()=>{
				this.applyLocalPlaybackFrame(speed);
				this.maybeSyncPlayback(speed);
			});
		}, intervalMs);
	}

	applyLocalPlaybackFrame(speed){
		if(!this.renderer || !this.state.data){
			return;
		}
		const renderMs = this.renderer.updateProjectedTime(this.state.time, this.getEffectiveFields());
		this.setState((prev)=>({
			metrics: {
				...prev.metrics,
				renderMs,
				loadMs: 0,
			},
		}));
	}

	maybeSyncPlayback(speed){
		const now = nowMs();
		const syncEvery = speed <= 60 ? 15000 : (speed <= 86400 ? 7000 : 5000);
		if(now - this.lastPlaybackSyncAt < syncEvery){
			return;
		}
		this.lastPlaybackSyncAt = now;
		this.requestPlaybackCalibration();
	}

	async requestPlaybackCalibration(syncTimeArg){
		if(this.playbackSyncInFlight || !this.state.data){
			return;
		}
		this.playbackSyncInFlight = true;
		const syncTime = syncTimeArg && syncTimeArg.clone ? syncTimeArg.clone() : this.state.time.clone();
		const apiStarted = nowMs();
		try{
			const rsp = await fetchPlanetariumState(buildPlaybackSyncParams(this.getEffectiveFields(), syncTime));
			const data = rsp && rsp.Result ? rsp.Result : rsp;
			if(!data || data.err || this._isUnmounted || !this.renderer){
				return;
			}
			const apiMs = Math.round(nowMs() - apiStarted);
			const renderMs = this.renderer.applyPlaybackCalibration(data, syncTime, this.getEffectiveFields());
			this.setState((prev)=>({
				data: {
					...prev.data,
					bodies: data.bodies || prev.data.bodies,
					sky: data.sky || prev.data.sky,
					meta: {
						...(prev.data.meta || {}),
						...(data.meta || {}),
						renderedCatalogCount: prev.data.meta ? prev.data.meta.renderedCatalogCount : 0,
					},
				},
				metrics: {
					...prev.metrics,
					apiMs,
					renderMs,
				},
			}));
		}finally{
			this.playbackSyncInFlight = false;
		}
	}

	applyFastSceneChange(reason){
		if(!this.renderer || !this.state.data){
			this.requestState({ showLoading: false, reason });
			return;
		}
		const renderMs = this.renderer.updateProjectedTime(this.state.time, this.getEffectiveFields());
		this.setState((prev)=>({
			syncing: false,
			metrics: {
				...prev.metrics,
				renderMs,
				loadMs: 0,
			},
		}));
		this.requestSceneCalibration(this.state.time, reason);
	}

	async requestSceneCalibration(syncTimeArg, reason){
		if(this.sceneSyncInFlight || !this.state.data){
			return;
		}
		this.sceneSyncInFlight = true;
		const syncTime = syncTimeArg && syncTimeArg.clone ? syncTimeArg.clone() : this.state.time.clone();
		const fields = this.getEffectiveFields();
		const apiStarted = nowMs();
		try{
			const rsp = await fetchPlanetariumState(buildSceneSyncParams(fields, syncTime));
			const data = rsp && rsp.Result ? rsp.Result : rsp;
			if(!data || data.err || this._isUnmounted || !this.renderer){
				return;
			}
			const apiMs = Math.round(nowMs() - apiStarted);
			let renderMs = this.renderer.updateData(data, this.state.layers) || 0;
			renderMs += this.renderer.updateProjectedTime(syncTime, fields) || 0;
			this.pushPerfLog('scene-sync', {
				reason,
				apiMs,
				renderMs,
				stars: data.meta ? data.meta.renderedCatalogCount : 0,
			});
			this.setState((prev)=>({
				data: {
					...prev.data,
					...data,
					stars: prev.data && prev.data.stars ? prev.data.stars : data.stars,
					meta: {
						...(prev.data && prev.data.meta ? prev.data.meta : {}),
						...(data.meta || {}),
						renderedCatalogCount: prev.data && prev.data.meta ? prev.data.meta.renderedCatalogCount : 0,
					},
				},
				syncing: false,
				loading: false,
				metrics: {
					...prev.metrics,
					apiMs,
					renderMs,
				},
			}));
		}finally{
			this.sceneSyncInFlight = false;
		}
	}

	async requestState(options = {}){
		const opts = options || {};
		if(this.requestInFlight){
			this.pendingRequestOptions = {
				showLoading: false,
				reason: opts.reason || 'pending',
			};
			return;
		}
		this.requestInFlight = true;
		const seq = ++this.reqSeq;
		const started = nowMs();
		const showLoading = opts.showLoading !== false && !this.state.data;
		this.setState({
			loading: showLoading,
			syncing: !showLoading,
			error: null,
		});
		const params = buildRequestParams(this.getEffectiveFields(), this.state.time);
		const apiStarted = nowMs();
		let rsp = null;
		try{
			rsp = await fetchPlanetariumState(params);
		}catch(err){
			rsp = { err: err && err.message ? err.message : '天文馆数据载入失败' };
		}
		const apiMs = Math.round(nowMs() - apiStarted);
		if(seq !== this.reqSeq){
			this.requestInFlight = false;
			this.flushPendingRequest();
			return;
		}
		const data = rsp && rsp.Result ? rsp.Result : rsp;
		if(!data || data.err){
			this.pushPerfLog('request-error', { apiMs, err: data && data.err ? data.err : 'empty' });
			this.setState({
				loading: false,
				syncing: false,
				error: data && data.err ? data.err : '天文馆数据载入失败',
			});
			this.requestInFlight = false;
			this.flushPendingRequest();
			return;
		}
		let renderMs = 0;
		if(this.renderer){
			renderMs = this.renderer.updateData(data, this.state.layers) || 0;
		}
		const firstReadyMs = this.firstReadyLogged ? this.state.metrics.firstReadyMs : Math.round(nowMs() - this.mountedAt);
		this.firstReadyLogged = true;
		this.pushPerfLog('state-ready', {
			apiMs,
			renderMs,
			totalMs: Math.round(nowMs() - started),
			stars: data.meta ? data.meta.renderedCatalogCount : 0,
			skyMode: data.sky ? data.sky.mode : undefined,
		});
		this.setState((prev)=>({
			data,
			loading: false,
			syncing: false,
			error: null,
			metrics: {
				...prev.metrics,
				loadMs: Math.round(nowMs() - started),
				apiMs,
				renderMs,
				firstReadyMs,
				catalogCount: data.meta ? data.meta.renderedCatalogCount : 0,
			},
		}), ()=>{
			this.requestInFlight = false;
			this.flushPendingRequest();
		});
	}

	flushPendingRequest(){
		if(!this.pendingRequestOptions || this._isUnmounted){
			return;
		}
		const opts = this.pendingRequestOptions;
		this.pendingRequestOptions = null;
		setTimeout(()=>this.requestState({
			...opts,
			showLoading: false,
		}), 0);
	}

	toggleLayer(key){
		this.setState((prev)=>({
			layers: {
				...prev.layers,
				[key]: !prev.layers[key],
			},
		}));
	}

	changeSpeed(speed){
		this.lastPlaybackSyncAt = nowMs();
		this.setState({ speed });
	}

	changeViewMode(viewMode){
		this.setState({ viewMode });
	}

	jumpNow(){
		this.setState({
			time: buildObservationTime(this.props.fields),
			speed: 0,
		}, ()=>this.applyFastSceneChange('jump'));
	}

	stepTime(amount, unit){
		this.setState((prev)=>{
			const next = prev.time.clone();
			next.add(amount, unit);
			return {
				time: next,
				speed: 0,
			};
		}, ()=>{
			if(this.renderer && this.state.data){
				this.applyLocalPlaybackFrame(0);
				this.requestPlaybackCalibration(this.state.time);
			}else{
				this.requestState({ showLoading: false, reason: 'step' });
			}
		});
	}

	setSearchQuery(e){
		this.setState({
			searchQuery: e && e.target ? e.target.value : '',
			searchMessage: '',
		});
	}

	searchTarget(){
		const query = `${this.state.searchQuery || ''}`.trim();
		if(!query){
			this.setState({ searchMessage: '输入天体、宿名或北斗星名' });
			return;
		}
		if(!this.renderer){
			return;
		}
		const picked = this.renderer.flyTo(query);
		if(picked && picked !== true){
			this.setState({
				selected: picked,
				searchMessage: `已定位：${picked.displayName || bodyName(picked)}`,
			});
			return;
		}
		this.setState({ searchMessage: '没有找到匹配天体' });
	}

	toggleLeftPanel(){
		this.setState((prev)=>({
			leftCollapsed: !prev.leftCollapsed,
		}), ()=>{
			if(this.renderer && this.renderer.engine){
				setTimeout(()=>this.renderer.engine.resize(), 120);
			}
		});
	}

	toggleFullscreen(){
		const node = this.canvasRef.current && this.canvasRef.current.parentNode;
		if(!node){
			return;
		}
		if(document.fullscreenElement){
			document.exitFullscreen();
		}else if(node.requestFullscreen){
			node.requestFullscreen();
		}
	}

	renderLayerButton(key, label){
		return (
			<button
				type="button"
				className={`planetarium-chip ${this.state.layers[key] ? 'is-on' : ''}`}
				onClick={()=>this.toggleLayer(key)}
			>
				{label}
			</button>
		);
	}

	renderSelected(){
		const item = this.state.selected;
		if(!item){
			return <div className="planetarium-empty">点击太阳、月亮、行星、二十八宿或北斗星点查看详情</div>;
		}
		return (
			<div className="planetarium-detail">
				<h3>{item.displayName || bodyName(item)}</h3>
				<div><span>类型</span><strong>{objectType(item)}</strong></div>
				<div><span>图层</span><strong>{item.layer || 'body'}</strong></div>
				<div><span>可见性</span><strong>{visibilityText(item)}</strong></div>
				<div><span>高度</span><strong>{formatDeg(item.altitudeAppa)}</strong></div>
				<div><span>方位</span><strong>{formatDeg(item.azimuth)}</strong></div>
				<div><span>赤经</span><strong>{formatDeg(item.ra)}</strong></div>
				<div><span>赤纬</span><strong>{formatDeg(item.decl)}</strong></div>
				<div><span>黄经</span><strong>{formatDeg(item.lon)}</strong></div>
				<div><span>黄纬</span><strong>{formatDeg(item.lat)}</strong></div>
				<div><span>星等</span><strong>{item.mag === undefined || item.mag === null ? '--' : item.mag}</strong></div>
				<div><span>黄道星座</span><strong>{item.zodiacSign ? `${item.zodiacSign} ${formatDeg(item.zodiacDegree)}` : (item.sign || '--')}</strong></div>
				<div><span>星座/宿</span><strong>{item.constellation || item.su28 || '--'}</strong></div>
				<div><span>宫位</span><strong>{item.house || '--'}</strong></div>
				<div><span>光谱/色温</span><strong>{item.spectralClass || (item.colorTemperature ? `${Math.round(item.colorTemperature)}K` : '--')}</strong></div>
			</div>
		);
	}

	render(){
		const { metrics, data } = this.state;
		const sky = data && data.sky ? data.sky : {};
		const moonPhase = sky.moonPhase;
		const effectiveFields = this.getEffectiveFields();
		const observerName = this.state.observerOverride
			? this.state.observerOverride.label
			: (data && data.observer ? data.observer.locationName : '未命名地点');
		const observerLon = effectiveFields && effectiveFields.lon ? effectiveFields.lon.value : '--';
		const observerLat = effectiveFields && effectiveFields.lat ? effectiveFields.lat.value : '--';
		const observerGpsLon = effectiveFields && effectiveFields.gpsLon ? effectiveFields.gpsLon.value : null;
		const observerGpsLat = effectiveFields && effectiveFields.gpsLat ? effectiveFields.gpsLat.value : null;
		return (
			<div className={`horosa-planetarium-page ${this.state.leftCollapsed ? 'is-left-collapsed' : ''}`}>
				<aside className="planetarium-side planetarium-left">
					<div className="planetarium-title">
						<small>地表观测天空</small>
						<h2>天文馆</h2>
						<button type="button" className="planetarium-collapse" onClick={this.toggleLeftPanel}>{this.state.leftCollapsed ? '展开' : '收合'}</button>
					</div>
					<div className="planetarium-time">
						<div>{this.state.time.format('YYYY-MM-DD HH:mm:ss')}</div>
						<small>{this.state.time.zone} · {observerName}</small>
						<div className="planetarium-observer-line">
							<span>{observerLon} · {observerLat}</span>
							{observerGpsLon !== null && observerGpsLat !== null ? <em>GPS {Number(observerGpsLon).toFixed(4)}, {Number(observerGpsLat).toFixed(4)}</em> : null}
						</div>
						<div className="planetarium-observer-actions">
							<GeoCoordModal
								onOk={this.changeObserverGeo}
								lat={observerGpsLat}
								lng={observerGpsLon}
							>
								<button type="button">经纬度选择</button>
							</GeoCoordModal>
							<button type="button" onClick={this.clearObserverOverride} disabled={!this.state.observerOverride}>回命盘地点</button>
						</div>
					</div>
					<div className="planetarium-section">
						<div className="planetarium-section-title">定位</div>
						<div className="planetarium-search">
							<input value={this.state.searchQuery} onChange={this.setSearchQuery} onKeyDown={(e)=>{ if(e.key === 'Enter'){ this.searchTarget(); } }} placeholder="月亮、木星、北斗、角宿..." />
							<button type="button" onClick={this.searchTarget}>定位</button>
						</div>
						{this.state.searchMessage ? <div className="planetarium-hint">{this.state.searchMessage}</div> : null}
					</div>
					<div className="planetarium-section">
						<div className="planetarium-section-title">观察模式</div>
						<div className="planetarium-view-grid">
							<button type="button" className={this.state.viewMode === 'ground' ? 'is-active' : ''} onClick={()=>this.changeViewMode('ground')}>地表观测</button>
							<button type="button" className={this.state.viewMode === 'orbit' ? 'is-active' : ''} onClick={()=>this.changeViewMode('orbit')}>天球外观</button>
						</div>
					</div>
					<div className="planetarium-section">
						<div className="planetarium-section-title">时间播放</div>
						<div className="planetarium-speed-grid">
							<button type="button" className={this.state.speed === 0 ? 'is-active' : ''} onClick={()=>this.changeSpeed(0)}>暂停</button>
							<button type="button" className={this.state.speed === 1 ? 'is-active' : ''} onClick={()=>this.changeSpeed(1)}>1x</button>
							<button type="button" className={this.state.speed === 60 ? 'is-active' : ''} onClick={()=>this.changeSpeed(60)}>60x</button>
							<button type="button" className={this.state.speed === 86400 ? 'is-active' : ''} onClick={()=>this.changeSpeed(86400)}>日进</button>
							<button type="button" className={this.state.speed === 2592000 ? 'is-active' : ''} onClick={()=>this.changeSpeed(2592000)}>月进</button>
							<button type="button" className={this.state.speed === 31536000 ? 'is-active' : ''} onClick={()=>this.changeSpeed(31536000)}>年进</button>
						</div>
						<div className="planetarium-actions">
							<button type="button" onClick={this.jumpNow}>回到命盘时间</button>
							<button type="button" onClick={this.toggleFullscreen}>全屏</button>
						</div>
						<div className="planetarium-step-grid">
							<button type="button" onClick={()=>this.stepTime(-1, 'h')}>-1时</button>
							<button type="button" onClick={()=>this.stepTime(1, 'h')}>+1时</button>
							<button type="button" onClick={()=>this.stepTime(-1, 'd')}>-1日</button>
							<button type="button" onClick={()=>this.stepTime(1, 'd')}>+1日</button>
						</div>
					</div>
					<div className="planetarium-section">
						<div className="planetarium-section-title">图层</div>
						<div className="planetarium-layer-grid">
							{this.renderLayerButton('stars', '恒星')}
							{this.renderLayerButton('bodies', '星体')}
							{this.renderLayerButton('horizon', '地平/子午')}
							{this.renderLayerButton('equator', '天赤道')}
							{this.renderLayerButton('ecliptic', '黄道')}
							{this.renderLayerButton('houses', '宫位')}
							{this.renderLayerButton('su28', '二十八宿')}
							{this.renderLayerButton('beidou', '北斗')}
						</div>
					</div>
				</aside>
				<main className="planetarium-stage">
					<canvas ref={this.canvasRef} className="planetarium-canvas" />
					{this.state.loading ? <div className="planetarium-status">同步天空中...</div> : null}
					{!this.state.loading && this.state.syncing ? <div className="planetarium-status is-syncing">更新天空...</div> : null}
					{this.state.error ? <div className="planetarium-status is-error">{this.state.error}</div> : null}
				</main>
				<aside className="planetarium-side planetarium-right">
					<div className="planetarium-section">
						<div className="planetarium-section-title">观测状态</div>
						<div className="planetarium-metrics">
							<div><span>FPS</span><strong>{metrics.fps}</strong></div>
							<div><span>网格</span><strong>{metrics.meshes}</strong></div>
							<div><span>载入</span><strong>{metrics.loadMs} ms</strong></div>
							<div><span>接口</span><strong>{metrics.apiMs} ms</strong></div>
							<div><span>渲染</span><strong>{metrics.renderMs} ms</strong></div>
							<div><span>首次可用</span><strong>{metrics.firstReadyMs} ms</strong></div>
							<div><span>Babylon</span><strong>{metrics.runtimeLoadMs} ms</strong></div>
							<div><span>恒星</span><strong>{metrics.catalogCount}</strong></div>
							<div><span>天空</span><strong>{sky.mode || '--'}</strong></div>
							<div><span>太阳高度</span><strong>{formatDeg(sky.sunAltitude)}</strong></div>
							<div><span>月相</span><strong>{moonPhase ? `${moonPhaseGlyph(moonPhase)} ${moonPhase.phaseName}` : '--'}</strong></div>
						</div>
					</div>
					<div className="planetarium-section">
						<div className="planetarium-section-title">天体详情</div>
						{this.renderSelected()}
					</div>
					<div className="planetarium-section">
						<div className="planetarium-section-title">性能日志</div>
						<div className="planetarium-perf-log">
							{(this.state.perfLog || []).map((item, idx)=>(
								<div key={`${item.event}-${idx}`}>
									<span>{item.event}</span>
									<strong>{item.totalMs || item.apiMs || item.renderMs || 0} ms</strong>
								</div>
							))}
						</div>
					</div>
				</aside>
			</div>
		);
	}
}

export default PlanetariumBabylon;
