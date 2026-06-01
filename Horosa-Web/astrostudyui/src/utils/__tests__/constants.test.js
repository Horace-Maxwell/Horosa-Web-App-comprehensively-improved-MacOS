describe('constants local server root resolution', ()=>{
	const originWindow = window;

	function loadConstantsWithLocation(href, seededStorage = {}){
		jest.resetModules();
		const localStorageMock = {
			store: { ...seededStorage },
			getItem(key){
				return Object.prototype.hasOwnProperty.call(this.store, key) ? this.store[key] : null;
			},
			setItem(key, value){
				this.store[key] = `${value}`;
			},
			removeItem(key){
				delete this.store[key];
			},
		};
		delete global.window;
		global.window = {
			location: new URL(href),
			localStorage: localStorageMock,
		};
		const constants = require('../constants');
		return {
			ServerRoot: constants.ServerRoot,
			storage: localStorageMock.store,
		};
	}

	afterEach(()=>{
		jest.resetModules();
		global.window = originWindow;
	});

	test('prefers pinned local storage over derived page port when query is gone', ()=>{
		const { ServerRoot, storage } = loadConstantsWithLocation('http://127.0.0.1:8000/', {
			horosaLocalServerRoot: 'http://127.0.0.1:50979',
			horosaLocalServerRootMode: 'pinned',
		});
		expect(ServerRoot).toBe('http://127.0.0.1:50979');
		expect(storage.horosaLocalServerRootMode).toBe('pinned');
	});

	test('falls back to derived page port without pinned override', ()=>{
		const { ServerRoot, storage } = loadConstantsWithLocation('http://127.0.0.1:8000/', {
			horosaLocalServerRoot: 'http://127.0.0.1:50979',
		});
		expect(ServerRoot).toBe('http://127.0.0.1:9999');
		expect(storage.horosaLocalServerRoot).toBe('http://127.0.0.1:9999');
		expect(storage.horosaLocalServerRootMode).toBe('page');
	});
});
