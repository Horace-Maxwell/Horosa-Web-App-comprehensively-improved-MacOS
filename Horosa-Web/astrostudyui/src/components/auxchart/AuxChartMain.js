import { Component } from 'react';
import { Tabs, } from 'antd';
import { randomStr } from '../../utils/helper';
import AstroGermany from '../germany/AstroGermany';
import HellenAstroMain from '../hellenastro/HellenAstroMain';
import LocAstroMain from '../loc/LocAstroMain';
import OtherBuMain from '../otherbu/OtherBuMain';

const TabPane = Tabs.TabPane;
const AUX_TABS = ['germanytech', 'hellenastro', 'locastro', 'otherbu'];

class AuxChartMain extends Component{

	constructor(props) {
		super(props);

		const subtab = this.props.currentSubTab ? this.props.currentSubTab : 'germanytech';
		const tab = AUX_TABS.indexOf(subtab) >= 0 ? subtab : 'germanytech';
		this.state = {
			divId: 'div_' + randomStr(8),
			currentTab: tab,
			hook:{
				germanytech:{
					fun: null
				},
				hellenastro:{
					fun: null
				},
				locastro:{
					fun: null
				},
				otherbu:{
					fun: null
				},
			},
		};

		this.changeTab = this.changeTab.bind(this);
		this.findTab = this.findTab.bind(this);
		this.callCurrentHook = this.callCurrentHook.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields, chartObj)=>{
				this.callCurrentHook(fields, chartObj);
			};
		}
	}

	findTab(){
		const tab = this.state.currentTab ? this.state.currentTab : 'germanytech';
		return AUX_TABS.indexOf(tab) >= 0 ? tab : 'germanytech';
	}

	callCurrentHook(fields, chartObj){
		const tab = this.findTab();
		const hook = this.state.hook[tab];
		if(hook && hook.fun){
			hook.fun(fields || this.props.fields, chartObj || this.props.chart);
		}
	}

	changeTab(key){
		this.setState({
			currentTab: key,
		}, ()=>{
			this.callCurrentHook(this.props.fields, this.props.chart);
			if(this.props.dispatch){
				this.props.dispatch({
					type: 'astro/save',
					payload: {
						currentSubTab: key,
					}
				});
			}
		});
	}

	render(){
		let height = this.props.height ? this.props.height : 760;
		height = height - 20;
		const tab = this.findTab();

		return (
			<div id={this.state.divId} className="horosa-auxchart-page">
				<Tabs
					defaultActiveKey={tab} tabPosition='right'
					activeKey={tab}
					onChange={this.changeTab}
					style={{ height: height }}
				>
					<TabPane tab="量化盘" key="germanytech">
						<AstroGermany
							onChange={this.props.onChange}
							fields={this.props.fields}
							fieldsAry={this.props.fieldsAry}
							height={height}
							chart={this.props.chart}
							chartDisplay={this.props.chartDisplay}
							planetDisplay={this.props.planetDisplay}
							lotsDisplay={this.props.lotsDisplay}
							showAstroMeaning={this.props.showAstroMeaning}
							hook={this.state.hook.germanytech}
							dispatch={this.props.dispatch}
						/>
					</TabPane>

					<TabPane tab="十三分盘" key="hellenastro">
						<HellenAstroMain
							value={this.props.chart}
							onChange={this.props.onChange}
							fields={this.props.fields}
							fieldsAry={this.props.fieldsAry}
							height={height}
							chartDisplay={this.props.chartDisplay}
							planetDisplay={this.props.planetDisplay}
							lotsDisplay={this.props.lotsDisplay}
							showPlanetHouseInfo={this.props.showPlanetHouseInfo}
							showAstroMeaning={this.props.showAstroMeaning}
							hook={this.state.hook.hellenastro}
							dispatch={this.props.dispatch}
						/>
					</TabPane>

					<TabPane tab="占星地图" key="locastro">
						<LocAstroMain
							value={this.props.chart}
							onChange={this.props.onChange}
							fields={this.props.fields}
							fieldsAry={this.props.fieldsAry}
							height={height}
							chartDisplay={this.props.chartDisplay}
							planetDisplay={this.props.planetDisplay}
							lotsDisplay={this.props.lotsDisplay}
							hook={this.state.hook.locastro}
							dispatch={this.props.dispatch}
						/>
					</TabPane>

					<TabPane tab="骰子" key="otherbu">
						<OtherBuMain
							height={height}
							fields={this.props.fields}
							fieldsAry={this.props.fieldsAry}
							chartDisplay={this.props.chartDisplay}
							planetDisplay={this.props.planetDisplay}
							lotsDisplay={this.props.lotsDisplay}
							showAstroMeaning={this.props.showAstroMeaning}
							hook={this.state.hook.otherbu}
							dispatch={this.props.dispatch}
						/>
					</TabPane>
				</Tabs>
			</div>
		);
	}
}

export default AuxChartMain;
