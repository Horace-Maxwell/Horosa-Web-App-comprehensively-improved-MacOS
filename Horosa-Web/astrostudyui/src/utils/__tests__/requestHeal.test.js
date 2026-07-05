// 服务地址自愈安全重放(healAndRetryOnce)回归(2026-07-04 事故复盘)。
// 不变量:只有「再协商后根确实换了」才重放(原请求从未到达真后端 → 重放零副作用);
// 根没换 / 已重放过 / 非可疑错误 → 返回 null,外层行为与旧版逐字节一致。

jest.mock('../backendIdentity', () => ({
	renegotiateLocalServerRoot: jest.fn(),
}));

import { healAndRetryOnce } from '../request';
import { renegotiateLocalServerRoot } from '../backendIdentity';

const UNREACHABLE = new TypeError('Failed to fetch');
const POISONED = { status: 200, url: 'http://127.0.0.1:10009/chart', horosaIdentitySuspect: true };
const BUSINESS = new Error('miss.date');

beforeEach(() => {
	renegotiateLocalServerRoot.mockReset();
});

it('毒 200 + 根换了 → 用新根重放一次并回传结果', async () => {
	renegotiateLocalServerRoot.mockResolvedValue({
		changed: true,
		from: 'http://127.0.0.1:10009',
		to: 'http://127.0.0.1:9999',
	});
	const replay = jest.fn().mockResolvedValue({ Result: 'healed' });
	const out = await healAndRetryOnce('http://127.0.0.1:10009/chart', { silent: true }, POISONED, replay);
	expect(out).toEqual({ value: { Result: 'healed' } });
	expect(replay).toHaveBeenCalledWith(
		'http://127.0.0.1:9999/chart',
		expect.objectContaining({ silent: true, __horosaHealed: true }),
	);
});

it('后端不可达同样触发;根没换则不重放(慢启动/真宕机零行为差异)', async () => {
	renegotiateLocalServerRoot.mockResolvedValue({
		changed: false,
		from: 'http://127.0.0.1:9999',
		to: 'http://127.0.0.1:9999',
	});
	const replay = jest.fn();
	const out = await healAndRetryOnce('http://127.0.0.1:9999/chart', {}, UNREACHABLE, replay);
	expect(out).toBe(null);
	expect(replay).not.toHaveBeenCalled();
});

it('业务错误(非可疑)不触发再协商', async () => {
	const replay = jest.fn();
	const out = await healAndRetryOnce('http://127.0.0.1:9999/chart', {}, BUSINESS, replay);
	expect(out).toBe(null);
	expect(renegotiateLocalServerRoot).not.toHaveBeenCalled();
});

it('__horosaHealed 防递归:重放过的请求绝不二次自愈', async () => {
	const replay = jest.fn();
	const out = await healAndRetryOnce('http://127.0.0.1:10009/chart', { __horosaHealed: true }, POISONED, replay);
	expect(out).toBe(null);
	expect(renegotiateLocalServerRoot).not.toHaveBeenCalled();
});

it('URL 不以旧根开头(外站/相对路径)不重放', async () => {
	renegotiateLocalServerRoot.mockResolvedValue({
		changed: true,
		from: 'http://127.0.0.1:10009',
		to: 'http://127.0.0.1:9999',
	});
	const replay = jest.fn();
	const out = await healAndRetryOnce('https://srv.horosa.com/chart', {}, POISONED, replay);
	expect(out).toBe(null);
	expect(replay).not.toHaveBeenCalled();
});

it('再协商自身异常被吞(自愈层绝不放大故障)', async () => {
	renegotiateLocalServerRoot.mockRejectedValue(new Error('boom'));
	const out = await healAndRetryOnce('http://127.0.0.1:10009/chart', {}, POISONED, jest.fn());
	expect(out).toBe(null);
});
