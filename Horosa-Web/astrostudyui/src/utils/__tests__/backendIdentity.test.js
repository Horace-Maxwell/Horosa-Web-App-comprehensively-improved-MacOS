// 身份握手 + 服务地址自愈再协商 回归矩阵(2026-07-04 事故复盘)。
// 事故复现锚:端口被陌生进程占用(对任意路径回 200 "ok" text/plain)时,
// 旧实现把毒 200 误判成「服务未就绪」且重试死循环;新实现必须:
//   ① verifyBackendIdentity 判非本应用后端(fail-closed);
//   ② renegotiateLocalServerRoot 换到首个通过身份握手的候选;
//   ③ 全候选不过 = 原地不换(verify-to-switch, never verify-to-block)。

import {
	verifyBackendIdentity,
	renegotiateLocalServerRoot,
	identityCheckDisabled,
	__resetBackendIdentityForTests,
} from '../backendIdentity';
import * as Constants from '../constants';
import { getKentangRootOverride } from '../../integrations/kentang/serviceRoot';

function mockFetchByRoot(routes){
	// routes: { 'http://127.0.0.1:9999': {status, body} | (url)=>({status, body}) }
	global.fetch = jest.fn((url)=>{
		const hit = Object.keys(routes).find((root)=>`${url}`.indexOf(root) === 0);
		if(!hit){
			return Promise.reject(new TypeError('Failed to fetch'));
		}
		const spec = typeof routes[hit] === 'function' ? routes[hit](`${url}`) : routes[hit];
		return Promise.resolve({
			status: spec.status,
			text: () => Promise.resolve(spec.body),
		});
	});
}

const JAVA_ID = JSON.stringify({ app: 'horosa-backend', proto: 1, nonce: '' });

describe('verifyBackendIdentity', ()=>{
	beforeEach(()=>{
		__resetBackendIdentityForTests();
		window.localStorage.clear();
		window.sessionStorage.clear();
	});

	it('陌生进程的毒 200(text/plain "ok")必须拒绝 —— 事故根因锚', async ()=>{
		mockFetchByRoot({ 'http://127.0.0.1:10009': { status: 200, body: 'ok' } });
		const v = await verifyBackendIdentity('http://127.0.0.1:10009', { expectApp: 'horosa-backend' });
		expect(v.ok).toBe(false);
		expect(v.reason).toBe('not-json');
	});

	it('真后端 app 标记通过', async ()=>{
		mockFetchByRoot({ 'http://127.0.0.1:9999': { status: 200, body: JAVA_ID } });
		const v = await verifyBackendIdentity('http://127.0.0.1:9999', { expectApp: 'horosa-backend' });
		expect(v.ok).toBe(true);
	});

	it('app 标记不符拒绝(别的软件恰好回 JSON 也不行)', async ()=>{
		mockFetchByRoot({ 'http://127.0.0.1:9999': { status: 200, body: JSON.stringify({ app: 'other-app' }) } });
		const v = await verifyBackendIdentity('http://127.0.0.1:9999', { expectApp: 'horosa-backend' });
		expect(v.ok).toBe(false);
		expect(v.reason).toBe('app-mark-mismatch');
	});

	it('期望 nonce 在时:不一致拒绝、一致通过、缺失拒绝(同机多实例互斥)', async ()=>{
		mockFetchByRoot({ 'http://127.0.0.1:9999': { status: 200, body: JSON.stringify({ app: 'horosa-backend', nonce: 'aaaa1111' }) } });
		expect((await verifyBackendIdentity('http://127.0.0.1:9999', { expectApp: 'horosa-backend', expectSid: 'bbbb2222' })).ok).toBe(false);
		expect((await verifyBackendIdentity('http://127.0.0.1:9999', { expectApp: 'horosa-backend', expectSid: 'aaaa1111' })).ok).toBe(true);
		mockFetchByRoot({ 'http://127.0.0.1:9999': { status: 200, body: JAVA_ID } });
		const missing = await verifyBackendIdentity('http://127.0.0.1:9999', { expectApp: 'horosa-backend', expectSid: 'aaaa1111' });
		expect(missing.ok).toBe(false);
		expect(missing.reason).toBe('nonce-missing');
	});

	it('http 404(旧版运行时)与网络不可达都 fail-closed', async ()=>{
		mockFetchByRoot({ 'http://127.0.0.1:9999': { status: 404, body: '' } });
		expect((await verifyBackendIdentity('http://127.0.0.1:9999', {})).reason).toBe('http-404');
		mockFetchByRoot({});
		expect((await verifyBackendIdentity('http://127.0.0.1:9999', {})).reason).toBe('unreachable');
	});
});

describe('renegotiateLocalServerRoot', ()=>{
	beforeEach(()=>{
		__resetBackendIdentityForTests();
		window.localStorage.clear();
		window.sessionStorage.clear();
		delete window.__TAURI__;
		delete window.__TAURI_INTERNALS__;
	});

	it('毒化根(存储 10009 撞桩)→ 梯2 换到通过握手的 dev 9999,并持久化', async ()=>{
		Constants.applyLocalServerRoot('http://127.0.0.1:10009', 'page');
		mockFetchByRoot({
			'http://127.0.0.1:10009': { status: 200, body: 'ok' },       // 桩:毒 200
			'http://127.0.0.1:9999': { status: 200, body: JAVA_ID },      // 真后端
		});
		const outcome = await renegotiateLocalServerRoot('test');
		expect(outcome.changed).toBe(true);
		expect(outcome.to).toBe('http://127.0.0.1:9999');
		expect(Constants.ServerRoot).toBe('http://127.0.0.1:9999');       // 活绑定原地更新
		expect(window.localStorage.getItem('horosaLocalServerRoot')).toBe('http://127.0.0.1:9999');
		expect(window.localStorage.getItem('horosaLocalServerRootMode')).toBe('verified');
	});

	it('梯1 壳真值优先:get_backend_endpoints + 身份通过 → 采用并联动 kentang 覆盖根', async ()=>{
		Constants.applyLocalServerRoot('http://127.0.0.1:10009', 'page');
		window.__TAURI__ = {
			core: {
				invoke: jest.fn(() => Promise.resolve({
					srv: 'http://127.0.0.1:54321',
					chartSrv: 'http://127.0.0.1:54322',
					kentangSrv: 'http://127.0.0.1:54322',
					sid: 'cafe0123',
				})),
			},
		};
		mockFetchByRoot({
			'http://127.0.0.1:54321': { status: 200, body: JSON.stringify({ app: 'horosa-backend', nonce: 'cafe0123' }) },
		});
		const outcome = await renegotiateLocalServerRoot('test');
		expect(outcome.via).toBe('shell');
		expect(outcome.changed).toBe(true);
		expect(Constants.ServerRoot).toBe('http://127.0.0.1:54321');
		expect(getKentangRootOverride()).toBe('http://127.0.0.1:54322');
	});

	it('全候选不过 → 原地不换(绝不写入未验证地址)', async ()=>{
		Constants.applyLocalServerRoot('http://127.0.0.1:10009', 'page');
		mockFetchByRoot({ 'http://127.0.0.1:10009': { status: 200, body: 'ok' } }); // 其余全 refused
		const outcome = await renegotiateLocalServerRoot('test');
		expect(outcome.changed).toBe(false);
		expect(Constants.ServerRoot).toBe('http://127.0.0.1:10009');
	});

	it('单飞:并发两次共用一次协商(fetch 调用数不翻倍)', async ()=>{
		Constants.applyLocalServerRoot('http://127.0.0.1:10009', 'page');
		mockFetchByRoot({
			'http://127.0.0.1:10009': { status: 200, body: 'ok' },
			'http://127.0.0.1:9999': { status: 200, body: JAVA_ID },
		});
		const [a, b] = await Promise.all([
			renegotiateLocalServerRoot('t1'),
			renegotiateLocalServerRoot('t2'),
		]);
		expect(a).toBe(b);
	});

	it('kill-switch horosaBackendIdentityOff=1 → 全旁路', async ()=>{
		window.localStorage.setItem('horosaBackendIdentityOff', '1');
		expect(identityCheckDisabled()).toBe(true);
		expect(await renegotiateLocalServerRoot('test')).toBe(null);
	});
});
