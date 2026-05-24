import {
	captureWindowSize,
	installWindowSizePersistence,
	readSavedWindowSize,
	restoreWindowSize,
	saveWindowSize,
} from '../windowSizePersistence';

function makeWindow(overrides = {}){
	const listeners = {};
	const storage = new Map();
	return {
		outerWidth: 1280,
		outerHeight: 820,
		innerWidth: 1264,
		innerHeight: 780,
		screenX: 80,
		screenY: 60,
		localStorage: {
			getItem(key){
				return storage.has(key) ? storage.get(key) : null;
			},
			setItem(key, value){
				storage.set(key, value);
			},
		},
		document: {
			visibilityState: 'visible',
			addEventListener(type, fn){
				listeners[`document:${type}`] = fn;
			},
		},
		addEventListener(type, fn){
			listeners[type] = fn;
		},
		resizeTo: jest.fn(),
		moveTo: jest.fn(),
		__listeners: listeners,
		__storage: storage,
		...overrides,
	};
}

describe('windowSizePersistence', ()=>{
	beforeEach(()=>{
		jest.useRealTimers();
	});

	it('saves and reads the browser window size without dropping position', ()=>{
		const win = makeWindow();
		expect(saveWindowSize(win)).toBe(true);
		const saved = readSavedWindowSize(win);
		expect(saved.width).toBe(1280);
		expect(saved.height).toBe(820);
		expect(saved.x).toBe(80);
		expect(saved.y).toBe(60);
	});

	it('restores web window size when the browser allows resizing', ()=>{
		const win = makeWindow({
			outerWidth: 1000,
			outerHeight: 700,
		});
		win.localStorage.setItem('horosa.window.size.v1', JSON.stringify({
			version: 1,
			width: 1480,
			height: 960,
			x: 120,
			y: 80,
		}));
		expect(restoreWindowSize(win)).toBe(true);
		expect(win.moveTo).toHaveBeenCalledWith(120, 80);
		expect(win.resizeTo).toHaveBeenCalledWith(1480, 960);
	});

	it('does not fight the Tauri desktop shell window restore', ()=>{
		const win = makeWindow({
			__TAURI__: { core: {} },
		});
		win.localStorage.setItem('horosa.window.size.v1', JSON.stringify({
			version: 1,
			width: 1480,
			height: 960,
		}));
		expect(restoreWindowSize(win)).toBe(false);
		expect(win.resizeTo).not.toHaveBeenCalled();
	});

	it('installs resize and close hooks once', ()=>{
		jest.useFakeTimers();
		const win = makeWindow();
		expect(installWindowSizePersistence(win)).toBe(true);
		expect(installWindowSizePersistence(win)).toBe(false);
		win.outerWidth = 1360;
		win.outerHeight = 900;
		win.__listeners.resize();
		jest.advanceTimersByTime(300);
		const saved = JSON.parse(win.localStorage.getItem('horosa.window.size.v1'));
		expect(saved.width).toBe(1360);
		expect(saved.height).toBe(900);
	});

	it('ignores unusably small or malformed saved values', ()=>{
		const malformed = makeWindow();
		malformed.localStorage.setItem('horosa.window.size.v1', '{bad json');
		expect(readSavedWindowSize(malformed)).toBe(null);
		expect(captureWindowSize(makeWindow({ outerWidth: 100, outerHeight: 100 }))).toBe(null);
	});
});
