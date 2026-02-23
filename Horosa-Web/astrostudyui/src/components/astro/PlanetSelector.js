import { Component } from 'react';
import { Checkbox, Row, Col, Tabs, Divider } from 'antd';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';

const TabPane = Tabs.TabPane;


class PlanetSelector extends Component{

	constructor(props) {
		super(props);

		this.onChange = this.onChange.bind(this);
		this.onLotsChange = this.onLotsChange.bind(this);
	}

	renderLabel(item){
		return (
			<span>
				<span style={{fontFamily: AstroConst.AstroFont}}>{AstroText.AstroMsg[item]}</span>
				<span>&nbsp;({AstroText.AstroTxtMsg[item]})</span>
			</span>
		);
	}

	onChange(checkedValues){
		if(this.props.dispatch){
			this.props.dispatch({
				type: 'app/save',
				payload:{ 
					planetDisplay: checkedValues,
				},
			});		

		}
	}

	onLotsChange(checkedValues){
		if(this.props.dispatch){
			this.props.dispatch({
				type: 'app/save',
				payload:{ 
					lotsDisplay: checkedValues
				},
			});		

		}
	}

	render(){
		let allobjs = AstroConst.LIST_POINTS.map((item)=>{
			return (
				<Col span={24} key={item}>
					<Checkbox value={item}>
						{this.renderLabel(item)}
					</Checkbox>
				</Col>
			);
		});

		let lots = AstroConst.LOTS.map((item, idx)=>{
			let col = (
				<Col span={24} key={item}>
					<Checkbox value={item}>
						{this.renderLabel(item)}
					</Checkbox>
				</Col>
			);
			if(idx === 0){
				col = (
					<Col span={24} key={item}>
						<Divider>希腊点</Divider>
						<Checkbox value={item}>
							{this.renderLabel(item)}
						</Checkbox>
					</Col>
				);
			}else if(idx === 5){
				col = (
					<Col span={24} key={item}>
						<Checkbox value={item}>
							{this.renderLabel(item)}
						</Checkbox>
						<Divider>阿拉伯点</Divider>
					</Col>
				);
			}

			return col;
		});

		return (
			<div>
				<Tabs defaultActiveKey="1" tabPosition='top'>
					<TabPane tab="行星" key="1">
						<Checkbox.Group 
							style={{ width: '100%' }} 
							onChange={this.onChange}
							value={this.props.value}
						>
							<Row gutter={12}>
								{allobjs}
							</Row>
						</Checkbox.Group>
					</TabPane>
					<TabPane tab="希腊点" key="2">
						<Checkbox.Group 
							style={{ width: '100%' }} 
							onChange={this.onLotsChange}
							value={this.props.lots}
						>
							<Row gutter={12}>
								{lots}
							</Row>
						</Checkbox.Group>

					</TabPane>
				</Tabs>
			</div>
		);
	}
}

export default PlanetSelector;
