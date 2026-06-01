import { Component } from 'react';
import { Row, Col, Popover} from 'antd';
import { randomStr } from '../../utils/helper';
import { BaZiMsg } from '../../msg/bazimsg';
import DateTime from '../comp/DateTime';

function gongName(gong12, palace, part){
	return gong12 && gong12[palace] && gong12[palace][part] && gong12[palace][part].name
		? gong12[palace][part].name : '';
}

class MDSYear extends Component{
	constructor(props) {
		super(props);
		this.state = {
			
		};

		this.background = 'var(--horosa-bazi-year-bg, #66FFFF)';

		this.genGong12GodDom = this.genGong12GodDom.bind(this);

	}

	genGong12GodDom(gong12){
		let dom = null;
		if(gong12 === null || gong12 === undefined){
			return dom;
		}

		dom = (
			<div>
			<ul>
				<li>大运：{gongName(gong12, '运', '干')}，{gongName(gong12, '运', '支')}</li>
				<li>年柱：{gongName(gong12, '年', '干')}，{gongName(gong12, '年', '支')}</li>
				<li>月柱：{gongName(gong12, '月', '干')}，{gongName(gong12, '月', '支')}</li>
				<li>日柱：{gongName(gong12, '日', '干')}，{gongName(gong12, '日', '支')}</li>
				<li>时柱：{gongName(gong12, '时', '干')}，{gongName(gong12, '时', '支')}</li>
				<li>胎元：{gongName(gong12, '胎', '干')}，{gongName(gong12, '胎', '支')}</li>
				<li>命宫：{gongName(gong12, '命', '干')}，{gongName(gong12, '命', '支')}</li>
				<li>身宫：{gongName(gong12, '身', '干')}，{gongName(gong12, '身', '支')}</li>
			</ul>
			</div>
		);

		return dom;
	}


	render(){
		let dir = this.props.value ? this.props.value : {};
		let mainDirect = dir.mainDirect ? dir.mainDirect : {};
		let subs = dir.subDirect ? dir.subDirect : [];
		let startYear = dir.startYear;
		let age = dir.age;

		let gong12god = dir.gong12God;
		
		let now = new DateTime();

		let yearStyle={
			textAlign: 'center',
			fontSize: 12,
			padding: 5,
			margin: 2,
			width: '100%',
			color: 'var(--horosa-text)',
		};
		let futureStyle={
			textAlign: 'center',
			fontSize: 12,
			padding: 5,
			margin: 2,
			width: '100%',
			background: this.background,
			color: 'var(--horosa-text)',
		};

		let subdoms = subs.map((sub, idx)=>{
			sub = sub || {};
			let y = startYear + idx;
			let yStyle = y >= now.year ? futureStyle : yearStyle;
			let nowage = age + idx;
			let gong12dom = null;
			if(gong12god){
				gong12dom = this.genGong12GodDom(gong12god[idx]);
			}
			const starCharger = sub && sub.starCharger ? sub.starCharger : {};
			let condom = (
				<div style={{width: 200,}}>
					<h4>值年星宿：{starCharger.name || '暂无'}</h4>
					<div>{starCharger.event || ''}</div>
					<hr />
					{gong12dom}
				</div>
			)
			return (
				<Popover title={(sub.ganzi || '') + '，公元' + y + '年，' + nowage + '周岁'} key={randomStr(8)}
					content={condom}
				>
					<Row key={randomStr(8)} style={{width: '100%'}}>
						<Col span={24} className={y >= now.year ? 'horosa-bazi-year-cell horosa-bazi-year-cell-future' : 'horosa-bazi-year-cell'} style={yStyle}>
							<span>{sub.ganzi || ''}</span>
						</Col>
					</Row>
				</Popover>
			)
		});


		return (
			<div>
				{subdoms}
			</div>
		);
	}
}

export default MDSYear;
