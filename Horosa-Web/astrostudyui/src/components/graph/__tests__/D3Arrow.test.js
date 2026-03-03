import * as d3 from 'd3';
jest.mock('../../../utils/helper', () => ({
	randomStr: () => 'unitid',
}));
import D3Arrow from '../D3Arrow';

describe('D3Arrow', () => {
	test('uses a valid marker viewBox', () => {
		const svg = d3.select(document.createElementNS('http://www.w3.org/2000/svg', 'svg'));
		new D3Arrow({
			owner: svg,
			x1: 0,
			y1: 0,
			x2: 10,
			y2: 10,
		});
		const marker = svg.select('marker').node();
		expect(marker).toBeTruthy();
		expect(marker.getAttribute('viewBox')).toBe('0 0 12 12');
	});
});
