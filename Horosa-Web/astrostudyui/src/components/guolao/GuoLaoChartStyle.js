export const GUOLAO_CHART_STYLE_CLASSIC = 'classic';
export const GUOLAO_CHART_STYLE_MOIRA = 'moira';
export const GUOLAO_CHART_STYLE_PICK = 'pick';
export const GUOLAO_CHART_STYLE_QIZHENG = 'qizhengKin';
export const GUOLAO_CHART_STYLE_KEY = 'horosaGuolaoChartStyle';
export const GUOLAO_SU28_MODE_KEY = 'horosaGuolaoSu28Mode';
export const GUOLAO_MOIRA_TRANSIT_GODS_KEY = 'horosaGuolaoMoiraTransitGods';
export const GUOLAO_LIFE_MODE_KEY = 'horosaGuolaoLifeMode';
export const GUOLAO_NODE_MODE_KEY = 'horosaGuolaoNodeMode';
export const GUOLAO_DEFAULT_SU28_MODE = 2;
export const GUOLAO_LIFE_MODE_ASC = 'asc';
export const GUOLAO_LIFE_MODE_YUMAO = 'yumao';
export const GUOLAO_LIFE_MODE_COTRANS = 'cotrans';
export const GUOLAO_NODE_MODE_NORTH_KETU = 'northKetuSouthRahu';
export const GUOLAO_NODE_MODE_NORTH_RAHU = 'northRahuSouthKetu';

function getStorage(){
	return typeof localStorage === 'undefined' ? null : localStorage;
}

function readItem(key){
	const storage = getStorage();
	return storage ? storage.getItem(key) : null;
}

function writeItem(key, val){
	const storage = getStorage();
	if(storage){
		storage.setItem(key, val);
	}
}

export function getStoredGuolaoChartStyle(){
	const val = readItem(GUOLAO_CHART_STYLE_KEY);
	if(val === GUOLAO_CHART_STYLE_CLASSIC){
		return GUOLAO_CHART_STYLE_CLASSIC;
	}
	if(val === GUOLAO_CHART_STYLE_PICK){
		return GUOLAO_CHART_STYLE_PICK;
	}
	if(val === GUOLAO_CHART_STYLE_QIZHENG){
		return GUOLAO_CHART_STYLE_QIZHENG;
	}
	return GUOLAO_CHART_STYLE_MOIRA;
}

export function setStoredGuolaoChartStyle(val){
	const next = val === GUOLAO_CHART_STYLE_PICK
		? GUOLAO_CHART_STYLE_PICK
		: (val === GUOLAO_CHART_STYLE_QIZHENG
			? GUOLAO_CHART_STYLE_QIZHENG
			: (val === GUOLAO_CHART_STYLE_MOIRA ? GUOLAO_CHART_STYLE_MOIRA : GUOLAO_CHART_STYLE_CLASSIC));
	writeItem(GUOLAO_CHART_STYLE_KEY, next);
	return next;
}

export function getStoredGuolaoSu28Mode(){
	const raw = readItem(GUOLAO_SU28_MODE_KEY);
	if(raw === null || raw === ''){
		return GUOLAO_DEFAULT_SU28_MODE;
	}
	const val = Number(raw);
	return [0, 1, 2, 3, 4].indexOf(val) >= 0 ? val : GUOLAO_DEFAULT_SU28_MODE;
}

export function setStoredGuolaoSu28Mode(val){
	const next = Number(val);
	const mode = [0, 1, 2, 3, 4].indexOf(next) >= 0 ? next : GUOLAO_DEFAULT_SU28_MODE;
	writeItem(GUOLAO_SU28_MODE_KEY, `${mode}`);
	return mode;
}

export function normalizeGuolaoLifeMode(val){
	if(val === GUOLAO_LIFE_MODE_YUMAO){
		return GUOLAO_LIFE_MODE_YUMAO;
	}
	if(val === GUOLAO_LIFE_MODE_COTRANS){
		return GUOLAO_LIFE_MODE_COTRANS;
	}
	return GUOLAO_LIFE_MODE_ASC;
}

export function getStoredGuolaoLifeMode(){
	return normalizeGuolaoLifeMode(readItem(GUOLAO_LIFE_MODE_KEY));
}

export function setStoredGuolaoLifeMode(val){
	const mode = normalizeGuolaoLifeMode(val);
	writeItem(GUOLAO_LIFE_MODE_KEY, mode);
	return mode;
}

export function normalizeGuolaoNodeMode(val){
	if(val === GUOLAO_NODE_MODE_NORTH_RAHU){
		return GUOLAO_NODE_MODE_NORTH_RAHU;
	}
	return GUOLAO_NODE_MODE_NORTH_KETU;
}

export function getStoredGuolaoNodeMode(){
	return normalizeGuolaoNodeMode(readItem(GUOLAO_NODE_MODE_KEY));
}

export function setStoredGuolaoNodeMode(val){
	const mode = normalizeGuolaoNodeMode(val);
	writeItem(GUOLAO_NODE_MODE_KEY, mode);
	return mode;
}

export function getStoredMoiraTransitGodsVisible(){
	return readItem(GUOLAO_MOIRA_TRANSIT_GODS_KEY) !== '0';
}

export function setStoredMoiraTransitGodsVisible(visible){
	const next = visible !== false;
	writeItem(GUOLAO_MOIRA_TRANSIT_GODS_KEY, next ? '1' : '0');
	return next;
}
