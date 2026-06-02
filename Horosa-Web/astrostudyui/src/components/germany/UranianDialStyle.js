// 汉堡 90°中点盘显示偏好 = 组件 state + 专用 localStorage（镜像 GuoLaoChartStyle）。
// 显示偏好不进 app.js globalSetup（那是跨技法全局开关专用）；切换即时重绘、不触发后端重取。

const KEY = 'horosa.uranian.dial.v1';
// 谐波盘基 H1..H512（窗口 W = 360/H）。折叠/模数皆按 W 计算，刻度自适应。
const VALID_BASES = [360, 180, 120, 90, 60, 45, 30, 22.5, 15, 7.5, 5.625, 3.75, 2.8125, 1.875, 1.40625, 0.9375, 0.703125];
// 盘基 → 谐波号(Hn)标签。
export const DIAL_BASE_HARMONIC = {
	360: 'H1', 180: 'H2', 120: 'H3', 90: 'H4', 60: 'H6', 45: 'H8', 30: 'H12', 22.5: 'H16',
	15: 'H24', 7.5: 'H48', 5.625: 'H64', 3.75: 'H96', 2.8125: 'H128', 1.875: 'H192',
	1.40625: 'H256', 0.9375: 'H384', 0.703125: 'H512',
};
// 盘基 → 显示文案(度分秒)。
export function dialBaseLabel(b){
	const h = DIAL_BASE_HARMONIC[b] || '';
	const deg = Math.floor(b);
	const minF = (b - deg) * 60;
	const min = Math.floor(minF);
	const sec = Math.round((minF - min) * 60);
	let dms = `${deg}°`;
	if (min || sec) dms += `${min}′`;
	if (sec) dms += `${sec}″`;
	return `${h} ${dms}`;
}

const DEFAULTS = {
	dialStyle: 'folded',  // folded=90°折叠盘 / modulus=真360°多环模数盘
	dialBase: 90,
	showTnp: true,
	orb: 1,        // 指针读数容许度（黄道度）
	showPicture: true,
	showTransit: false,
	showSolarArc: false,
	onlyPersonal: true,
	saKey: 'naibod', // 太阳弧换算：naibod / oneDeg
};

export function getStoredUranianDisplay(){
	try {
		const raw = typeof localStorage !== 'undefined' ? localStorage.getItem(KEY) : null;
		if (!raw) return { ...DEFAULTS };
		const obj = JSON.parse(raw) || {};
		return {
			dialStyle: obj.dialStyle === 'modulus' ? 'modulus' : DEFAULTS.dialStyle,
			dialBase: VALID_BASES.indexOf(Number(obj.dialBase)) >= 0 ? Number(obj.dialBase) : DEFAULTS.dialBase,
			showTnp: obj.showTnp === undefined ? DEFAULTS.showTnp : !!obj.showTnp,
			orb: Number.isFinite(Number(obj.orb)) && Number(obj.orb) > 0 ? Number(obj.orb) : DEFAULTS.orb,
			showPicture: obj.showPicture === undefined ? DEFAULTS.showPicture : !!obj.showPicture,
			showTransit: obj.showTransit === undefined ? DEFAULTS.showTransit : !!obj.showTransit,
			showSolarArc: obj.showSolarArc === undefined ? DEFAULTS.showSolarArc : !!obj.showSolarArc,
			onlyPersonal: obj.onlyPersonal === undefined ? DEFAULTS.onlyPersonal : !!obj.onlyPersonal,
			saKey: obj.saKey === 'oneDeg' ? 'oneDeg' : DEFAULTS.saKey,
		};
	} catch (e) {
		return { ...DEFAULTS };
	}
}

export function saveUranianDisplay(next){
	try {
		const merged = { ...getStoredUranianDisplay(), ...(next || {}) };
		if (typeof localStorage !== 'undefined') localStorage.setItem(KEY, JSON.stringify(merged));
		return merged;
	} catch (e) {
		return { ...getStoredUranianDisplay(), ...(next || {}) };
	}
}

export const URANIAN_DIAL_BASES = VALID_BASES;
