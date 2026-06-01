import request from '../request';
import { fetchPreciseJieqiSeed } from '../preciseCalcBridge';
import { buildLocalJieqiYearSeed } from '../localNongliAdapter';

jest.mock('../request', ()=>jest.fn());

describe('preciseCalcBridge jieqi seed fallback', ()=>{
	beforeEach(()=>{
		request.mockReset();
	});

	test('fills missing jieqi day ganzhi from local calendar while preserving backend term time', async()=>{
		request.mockResolvedValue({
			Result: {
				year: 2047,
				jieqi24: [
					{
						jieqi: '大雪',
						time: '2047-12-07 13:11:06',
					},
				],
			},
		});
		const seed = await fetchPreciseJieqiSeed({
			year: '2047',
			ad: 1,
			zone: '+08:00',
			timeAlg: 1,
			jieqis: ['大雪'],
		});
		const localSeed = buildLocalJieqiYearSeed(2047, '+08:00');
		expect(seed.大雪.time).toEqual('2047-12-07 13:11:06');
		expect(seed.大雪.dayGanzhi).toEqual(localSeed.大雪.dayGanzhi);
		expect(seed.大雪.dayGanzhi).toBeTruthy();
	});
});
