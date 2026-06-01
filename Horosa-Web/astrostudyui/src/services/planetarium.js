import request from '../utils/request';
import { ServerRoot } from '../utils/constants';

export function fetchPlanetariumState(values, requestOptions){
	return request(`${ServerRoot}/planetarium/state`, {
		body: JSON.stringify(values || {}),
		silent: true,
		timeoutMs: 15000,
		...(requestOptions || {}),
	});
}
