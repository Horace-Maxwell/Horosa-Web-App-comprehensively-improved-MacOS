jest.mock('../../../utils/helper', ()=>({
	randomStr: ()=> 'astro-info-test',
}));

import { resolveAstroDisplayMode, } from '../AstroInfo';

describe('AstroInfo display mode', ()=>{
	test('uses current chart labels when available and falls back to field labels otherwise', ()=>{
		expect(resolveAstroDisplayMode({
			zodiacal: 'Sidereal',
			hsys: 'Alcabitus',
		}, {
			zodiacal: '回归黄道',
			hsys: '整宫制',
		})).toEqual({
			zodiacal: '恒星黄道',
			hsys: 'Alcabitus',
		});

		expect(resolveAstroDisplayMode({}, {
			zodiacal: '回归黄道',
			hsys: '整宫制',
		})).toEqual({
			zodiacal: '回归黄道',
			hsys: '整宫制',
		});
	});
});
