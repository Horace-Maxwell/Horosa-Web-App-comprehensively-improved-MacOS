import request from '../utils/request';
import { ServerRoot } from '../utils/constants';

export function fetchMoiraQizhengRules(values, requestOptions){
	return request(`${ServerRoot}/qizheng/moira`, {
		body: JSON.stringify(values || {}),
		...(requestOptions || {}),
	});
}
