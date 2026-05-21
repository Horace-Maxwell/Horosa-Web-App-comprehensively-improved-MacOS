import { Component } from 'react';
import { XQTabs as Tabs } from '../xq-ui';
import { XQIcon } from '../xq-icons';
import { randomStr } from '../../utils/helper';
import AstroGermany from '../germany/AstroGermany';
import HellenAstroMain from '../hellenastro/HellenAstroMain';
import LocAstroMain from '../loc/LocAstroMain';
import OtherBuMain from '../otherbu/OtherBuMain';
import AstroHarmonicLab from './AstroHarmonicLab';

const TabPane = Tabs.TabPane;
const AUX_TABS = ['germanytech', 'hellenastro', 'locastro', 'harmonic', 'otherbu'];
const AUX_QUICK_ACTIONS = [
	{ key: 'germanytech', label: '量化盘', icon: 'quickPrimary' },
	{ key: 'hellenastro', label: '十三分盘', icon: 'astro' },
	{ key: 'locastro', label: '占星地图', icon: 'locastro' },
	{ key: 'harmonic', label: '调波盘', icon: 'quickTransit' },
	{ key: 'otherbu', label: '骰子', icon: 'quickAi' },
];

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
					harmonic:{
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
		this.renderQuickDock = this.renderQuickDock.bind(this);

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

	renderQuickDock(tab){
		return (
			<div className="horosa-bottom-quick-dock horosa-aux-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-aux-quick-actions">
					{AUX_QUICK_ACTIONS.map((item)=>(
						<button
							type="button"
							key={item.key}
							className={`horosa-bottom-quick-button horosa-aux-quick-button${tab === item.key ? ' is-active' : ''}`}
							onClick={()=>this.changeTab(item.key)}
						>
							<span className="horosa-bottom-quick-icon"><XQIcon name={item.icon} /></span>
							<span>{item.label}</span>
						</button>
					))}
				</div>
			</div>
		);
	}

	render(){
		let height = this.props.height ? this.props.height : 760;
		height = height - 20;
		const childHeight = Math.max(height - 92, 520);
		const tab = this.findTab();

		return (
			<div id={this.state.divId} className="horosa-auxchart-page">
				<div className="horosa-auxchart-layout">
					<Tabs
						defaultActiveKey={tab} tabPosition='right'
						activeKey={tab}
						onChange={this.changeTab}
						className="horosa-auxchart-tabs"
						style={{ height: '100%' }}
					>
						<TabPane tab="量化盘" key="germanytech">
							<AstroGermany
								onChange={this.props.onChange}
								fields={this.props.fields}
								fieldsAry={this.props.fieldsAry}
								height={childHeight}
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
								height={childHeight}
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
								height={childHeight}
								chartDisplay={this.props.chartDisplay}
								planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								hook={this.state.hook.locastro}
								dispatch={this.props.dispatch}
							/>
							</TabPane>

							<TabPane tab="调波盘" key="harmonic">
								<AstroHarmonicLab
									value={this.props.chart}
									height={childHeight}
								/>
							</TabPane>
	
							<TabPane tab="骰子" key="otherbu">
								<OtherBuMain
								height={childHeight}
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
					{this.renderQuickDock(tab)}
				</div>
			</div>
		);
	}
}

export default AuxChartMain;
