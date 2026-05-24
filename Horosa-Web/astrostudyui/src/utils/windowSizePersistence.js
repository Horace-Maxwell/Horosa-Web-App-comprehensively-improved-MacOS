const WindowSizeKey = 'horosa.window.size.v1';
const WindowSizeVersion = 1;
const MinWidth = 640;
const MinHeight = 480;
const ResizeTolerance = 24;

function getStorage(win){
	try{
		return win && win.localStorage ? win.localStorage : null;
	}catch(e){
		return null;
	}
}

function isFiniteNumber(value){
	return typeof value === 'number' && Number.isFinite(value);
}

function optionalNumber(value){
	if(value === undefined || value === null || value === ''){
		return null;
	}
	const num = Number(value);
	return isFiniteNumber(num) ? num : null;
}

function normalizeWindowSizePayload(payload){
	if(!payload || typeof payload !== 'object'){
		return null;
	}
	const width = Number(payload.width || payload.outerWidth || payload.innerWidth || 0);
	const height = Number(payload.height || payload.outerHeight || payload.innerHeight || 0);
	if(!Number.isFinite(width) || !Number.isFinite(height) || width < MinWidth || height < MinHeight){
		return null;
	}
	return {
		version: Number(payload.version || WindowSizeVersion),
		width,
		height,
		x: optionalNumber(payload.x),
		y: optionalNumber(payload.y),
		updatedAt: payload.updatedAt || null,
	};
}

function parseJson(text){
	if(!text){
		return null;
	}
	try{
		return JSON.parse(text);
	}catch(e){
		return null;
	}
}

export function readSavedWindowSize(win = typeof window !== 'undefined' ? window : null){
	const storage = getStorage(win);
	if(!storage){
		return null;
	}
	return normalizeWindowSizePayload(parseJson(storage.getItem(WindowSizeKey)));
}

export function captureWindowSize(win = typeof window !== 'undefined' ? window : null){
	if(!win){
		return null;
	}
	const width = Number(win.outerWidth || win.innerWidth || 0);
	const height = Number(win.outerHeight || win.innerHeight || 0);
	return normalizeWindowSizePayload({
		version: WindowSizeVersion,
		width,
		height,
		x: isFiniteNumber(Number(win.screenX)) ? Number(win.screenX) : null,
		y: isFiniteNumber(Number(win.screenY)) ? Number(win.screenY) : null,
		updatedAt: new Date().toISOString(),
	});
}

export function saveWindowSize(win = typeof window !== 'undefined' ? window : null){
	const storage = getStorage(win);
	const payload = captureWindowSize(win);
	if(!storage || !payload){
		return false;
	}
	try{
		storage.setItem(WindowSizeKey, JSON.stringify(payload));
		return true;
	}catch(e){
		return false;
	}
}

function isTauriWindow(win){
	return Boolean(win && (win.__TAURI__ || win.__TAURI_INTERNALS__));
}

export function restoreWindowSize(win = typeof window !== 'undefined' ? window : null){
	if(!win || isTauriWindow(win)){
		return false;
	}
	const saved = readSavedWindowSize(win);
	if(!saved || typeof win.resizeTo !== 'function'){
		return false;
	}
	const currentWidth = Number(win.outerWidth || win.innerWidth || 0);
	const currentHeight = Number(win.outerHeight || win.innerHeight || 0);
	const needsResize = Math.abs(currentWidth - saved.width) > ResizeTolerance
		|| Math.abs(currentHeight - saved.height) > ResizeTolerance;
	try{
		if(saved.x !== null && saved.y !== null && typeof win.moveTo === 'function'){
			win.moveTo(saved.x, saved.y);
		}
		if(needsResize){
			win.resizeTo(saved.width, saved.height);
		}
		return needsResize;
	}catch(e){
		return false;
	}
}

export function installWindowSizePersistence(win = typeof window !== 'undefined' ? window : null){
	if(!win || win.__horosaWindowSizePersistenceInstalled){
		return false;
	}
	win.__horosaWindowSizePersistenceInstalled = true;
	restoreWindowSize(win);
	let resizeTimer = null;
	const flush = ()=>{
		if(resizeTimer){
			clearTimeout(resizeTimer);
			resizeTimer = null;
		}
		saveWindowSize(win);
	};
	const scheduleSave = ()=>{
		if(resizeTimer){
			clearTimeout(resizeTimer);
		}
		resizeTimer = setTimeout(flush, 250);
	};
	if(typeof win.addEventListener === 'function'){
		win.addEventListener('resize', scheduleSave);
		win.addEventListener('beforeunload', flush);
		win.addEventListener('pagehide', flush);
		if(win.document && typeof win.document.addEventListener === 'function'){
			win.document.addEventListener('visibilitychange', ()=>{
				if(win.document.visibilityState === 'hidden'){
					flush();
				}
			});
		}
	}
	return true;
}
