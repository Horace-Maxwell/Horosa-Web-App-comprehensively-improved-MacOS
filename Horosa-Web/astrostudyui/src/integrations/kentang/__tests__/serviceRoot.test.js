describe('kentang service root isolation', ()=>{
	const originWindow = window;

	function loadServiceRoot(href){
		jest.resetModules();
		delete global.window;
		global.window = {
			location: new URL(href),
			localStorage: {
				store: {},
				getItem(key){
					return Object.prototype.hasOwnProperty.call(this.store, key) ? this.store[key] : null;
				},
				setItem(key, value){
					this.store[key] = `${value}`;
				},
			},
		};
		return require('../serviceRoot');
	}

	afterEach(()=>{
		jest.resetModules();
		global.window = originWindow;
	});

	test('uses module-specific service params before shared kentang params', ()=>{
		const serviceRoot = loadServiceRoot(
			'http://127.0.0.1:3001/?srv=http%3A%2F%2F127.0.0.1%3A9999&taiyiSrv=http%3A%2F%2F127.0.0.1%3A8898&kentangSrv=http%3A%2F%2F127.0.0.1%3A7777'
		);
		expect(serviceRoot.buildKentangEndpoint('taiyi', 'pan')).toBe('http://127.0.0.1:8898/taiyi/pan');
		expect(serviceRoot.buildKentangEndpoint('qimen', 'pan')).toBe('http://127.0.0.1:7777/qimen/pan');
	});

	test('keeps every module on its own route when one shared service is used', ()=>{
		const serviceRoot = loadServiceRoot(
			'http://127.0.0.1:3001/?srv=http%3A%2F%2F127.0.0.1%3A9999&kentangSrv=http%3A%2F%2F127.0.0.1%3A8898'
		);
		expect(serviceRoot.buildKentangEndpoint('taiyi', 'pan')).toBe('http://127.0.0.1:8898/taiyi/pan');
		expect(serviceRoot.buildKentangEndpoint('jinkou', 'pan')).toBe('http://127.0.0.1:8898/jinkou/pan');
		expect(serviceRoot.buildKentangEndpoint('qimen', 'pan')).toBe('http://127.0.0.1:8898/qimen/pan');
		expect(serviceRoot.buildKentangEndpoint('wangji', 'xinyi')).toBe('http://127.0.0.1:8898/wangji/xinyi');
		expect(serviceRoot.buildKentangEndpoint('wuzhao', 'pan')).toBe('http://127.0.0.1:8898/wuzhao/pan');
		expect(serviceRoot.buildKentangEndpoint('taixuan', 'pan')).toBe('http://127.0.0.1:8898/taixuan/pan');
		expect(serviceRoot.buildKentangEndpoint('jingjue', 'pan')).toBe('http://127.0.0.1:8898/jingjue/pan');
		expect(serviceRoot.buildKentangEndpoint('shenyishu', 'pan')).toBe('http://127.0.0.1:8898/shenyishu/pan');
		expect(serviceRoot.buildKentangEndpoint('shaozi', 'pan')).toBe('http://127.0.0.1:8898/shaozi/pan');
		expect(serviceRoot.buildKentangEndpoint('xianqin', 'pan')).toBe('http://127.0.0.1:8898/xianqin/pan');
		expect(serviceRoot.buildKentangEndpoint('cetian', 'pan')).toBe('http://127.0.0.1:8898/cetian/pan');
	});

	test('uses packaged desktop chart service for all kentang routes', ()=>{
		const serviceRoot = loadServiceRoot(
			'http://127.0.0.1:38991/index.html?srv=http%3A%2F%2F127.0.0.1%3A63968&chartSrv=http%3A%2F%2F127.0.0.1%3A63967'
		);
		expect(serviceRoot.buildKentangEndpoint('taiyi', 'pan')).toBe('http://127.0.0.1:63967/taiyi/pan');
		expect(serviceRoot.buildKentangEndpoint('jinkou', 'pan')).toBe('http://127.0.0.1:63967/jinkou/pan');
		expect(serviceRoot.buildKentangEndpoint('qizhengkin', 'pan')).toBe('http://127.0.0.1:63967/qizhengkin/pan');
	});

	test('derives the local kentang port from the primary local server root', ()=>{
		const serviceRoot = loadServiceRoot(
			'http://127.0.0.1:3001/?srv=http%3A%2F%2F127.0.0.1%3A9999'
		);
		expect(serviceRoot.buildKentangEndpoint('jinkou', 'pan')).toBe('http://127.0.0.1:8898/jinkou/pan');
		expect(serviceRoot.buildKentangEndpoint('taixuan', 'pan')).toBe('http://127.0.0.1:8895/taixuan/pan');
		expect(serviceRoot.buildKentangEndpoint('jingjue', 'pan')).toBe('http://127.0.0.1:8894/jingjue/pan');
		expect(serviceRoot.buildKentangEndpoint('shenyishu', 'pan')).toBe('http://127.0.0.1:8893/shenyishu/pan');
		expect(serviceRoot.buildKentangEndpoint('shaozi', 'pan')).toBe('http://127.0.0.1:8892/shaozi/pan');
		expect(serviceRoot.buildKentangEndpoint('xianqin', 'pan')).toBe('http://127.0.0.1:8892/xianqin/pan');
		expect(serviceRoot.buildKentangEndpoint('cetian', 'pan')).toBe('http://127.0.0.1:8892/cetian/pan');
	});

	test('supports explicit engine aliases for future kentang modules', ()=>{
		const serviceRoot = loadServiceRoot(
			'http://127.0.0.1:3001/?srv=http%3A%2F%2F127.0.0.1%3A9999&kinwangjiSrv=http%3A%2F%2F127.0.0.1%3A8897&kinwuzhaoSrv=http%3A%2F%2F127.0.0.1%3A8896&taixuanshifaSrv=http%3A%2F%2F127.0.0.1%3A8895&jingjueSrv=http%3A%2F%2F127.0.0.1%3A8894&shenyishuSrv=http%3A%2F%2F127.0.0.1%3A8893&kinastroSrv=http%3A%2F%2F127.0.0.1%3A8892'
		);
		expect(serviceRoot.buildKentangEndpoint('wangji', 'pan')).toBe('http://127.0.0.1:8897/wangji/pan');
		expect(serviceRoot.buildKentangEndpoint('wuzhao', 'pan')).toBe('http://127.0.0.1:8896/wuzhao/pan');
		expect(serviceRoot.buildKentangEndpoint('taixuan', 'pan')).toBe('http://127.0.0.1:8895/taixuan/pan');
		expect(serviceRoot.buildKentangEndpoint('jingjue', 'pan')).toBe('http://127.0.0.1:8894/jingjue/pan');
		expect(serviceRoot.buildKentangEndpoint('shenyishu', 'pan')).toBe('http://127.0.0.1:8893/shenyishu/pan');
		expect(serviceRoot.buildKentangEndpoint('shaozi', 'pan')).toBe('http://127.0.0.1:8892/shaozi/pan');
		expect(serviceRoot.buildKentangEndpoint('xianqin', 'pan')).toBe('http://127.0.0.1:8892/xianqin/pan');
		expect(serviceRoot.buildKentangEndpoint('cetian', 'pan')).toBe('http://127.0.0.1:8892/cetian/pan');
	});
});
