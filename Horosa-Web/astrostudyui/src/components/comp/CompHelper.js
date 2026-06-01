import { XQSelect } from '../xq-ui';
import { HOUSE_SYSTEM_OPTIONS } from '../../constants/AstroConst';

const Option = XQSelect.Option;

export function getHousesOption(expanded=false){
	let houses = expanded ? HOUSE_SYSTEM_OPTIONS : HOUSE_SYSTEM_OPTIONS.slice(0, 9);

	let dom = houses.map((item, idx)=>{
		return (
			<Option key={idx} value={item.value}>{item.label}</Option>
		);
	});

	return dom;
}
