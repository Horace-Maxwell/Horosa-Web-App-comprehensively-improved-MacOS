import { Component } from 'react';
import { wrapperPropsEqual } from '../../utils/chartUpdateGuard';
import { XQTabs as Tabs } from '../xq-ui';
import QuickDockBar from '../common/QuickDockBar';
import { randomStr } from '../../utils/helper';
import AstroGermany from '../germany/AstroGermany';
import HellenAstroMain from '../hellenastro/HellenAstroMain';
import Dwadasamsa12Main from '../hellenastro/Dwadasamsa12Main';
import LocAstroMain from '../loc/LocAstroMain';
import OtherBuMain from '../otherbu/OtherBuMain';
import AstroHarmonicLab from './AstroHarmonicLab';
import AstroDraconicLab from './AstroDraconicLab';
import AstroRelocationLab from './AstroRelocationLab';
import HoraryMain from '../horary/HoraryMain';
import ElectionMain from '../election/ElectionMain';
import MundaneMain from '../mundane/MundaneMain';
// 🔴 共享真值源 import 绝不许进 private marker 块:消费点(AUX_TABS)在块外,strip 后
// public 侧成悬空自由变量→模块顶层 ReferenceError→辅盘页干净安装必炸(v3.6.0 实案)。
import { AUX_SUBTABS } from '../../constants/SubTabRegistry';
import BabylonMain from '../babylon/BabylonMain';

const TabPane = Tabs.TabPane;
// 合法子页签集合的单一真值源在 constants/SubTabRegistry(导航层同源,防「切回来被打回首档」)。
const AUX_TABS = AUX_SUBTABS;

class AuxChartMain extends Component{
	// [R3-A6] 渲染守卫:宿主无关 dispatch 不再全树重渲(nextState 引用变照常放行;
	// 开关 horosa.perf.chartSCU,语义详 chartUpdateGuard.wrapperPropsEqual)。
	shouldComponentUpdate(nextProps, nextState){
		if(nextState !== this.state){
			return true;
		}
		return !wrapperPropsEqual(this.props, nextProps);
	}


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
				dwadasamsa:{
					fun: null
				},
				locastro:{
					fun: null
				},
				relocation:{
					fun: null
				},
				harmonic:{
					fun: null
				},
				draconic:{
					fun: null
				},
				otherbu:{
					fun: null
				},
				horary:{
					fun: null
				},
				election:{
					fun: null
				},
				mundane:{
					fun: null
				},
				babylon:{
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

	// 外部（如从事件盘列表 applyCase 还原卜卦/择日案例）改动 currentSubTab 时，切到对应子盘。
	componentDidUpdate(prevProps){
		if(prevProps.currentSubTab !== this.props.currentSubTab){
			const key = this.props.currentSubTab;
			if(AUX_TABS.indexOf(key) >= 0 && key !== this.state.currentTab){
				this.setState({ currentTab: key }, ()=>{
					this.callCurrentHook(this.props.fields, this.props.chart);
				});
			}
		}
	}

	// 快捷栏契约:原 11 键=右侧 Tabs 的静态镜像(目录化),全部撤除;辅盘无独立起盘/保存,只留 AI。
	renderQuickDock(){
		return (
			<QuickDockBar
				page="auxchart"
				className="horosa-aux-quick-dock"
				hasResult={!!this.props.chart}
				dispatch={this.props.dispatch}
			/>
		);
	}

	render(){
		let height = this.props.height ? this.props.height : 760;
		height = height - 20;
		const childHeight = Math.max(height - 36, 560);
		const tab = this.findTab();

		return (
			<div id={this.state.divId} className="horosa-auxchart-page">
				<div className="horosa-auxchart-layout">
					<Tabs
						defaultActiveKey={tab} tabPosition='right'
						activeKey={tab}
						onChange={this.changeTab}
						className="xq-tabs-rail horosa-auxchart-tabs"
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
								tripSystem={this.props.tripSystem}
								fields={this.props.fields}
								fieldsAry={this.props.fieldsAry}
								height={childHeight}
								chartStyle={this.props.chartStyle}
								chartDisplay={this.props.chartDisplay}
								planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								showPlanetHouseInfo={this.props.showPlanetHouseInfo}
								showAstroMeaning={this.props.showAstroMeaning}
								hook={this.state.hook.hellenastro}
								dispatch={this.props.dispatch}
							/>
						</TabPane>

						<TabPane tab="十二分盘" key="dwadasamsa">
							<Dwadasamsa12Main
								onChange={this.props.onChange}
								tripSystem={this.props.tripSystem}
								fields={this.props.fields}
								fieldsAry={this.props.fieldsAry}
								height={childHeight}
								chartStyle={this.props.chartStyle}
								chartDisplay={this.props.chartDisplay}
								planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								showPlanetHouseInfo={this.props.showPlanetHouseInfo}
								showAstroMeaning={this.props.showAstroMeaning}
								hook={this.state.hook.dwadasamsa}
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

						<TabPane tab="重置盘" key="relocation">
							<AstroRelocationLab
								value={this.props.chart}
								fields={this.props.fields}
								height={childHeight}
								chartStyle={this.props.chartStyle}
								chartDisplay={this.props.chartDisplay}
								planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								showPlanetHouseInfo={this.props.showPlanetHouseInfo}
								showAstroMeaning={this.props.showAstroMeaning}
								dispatch={this.props.dispatch}
							/>
						</TabPane>

						<TabPane tab="调波盘" key="harmonic">
							<AstroHarmonicLab
								value={this.props.chart}
								height={childHeight}
								chartStyle={this.props.chartStyle}
								chartDisplay={this.props.chartDisplay}
								planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								showAstroMeaning={this.props.showAstroMeaning}
							/>
						</TabPane>

						<TabPane tab="龙盘" key="draconic">
							<AstroDraconicLab
								value={this.props.chart}
								height={childHeight}
								chartStyle={this.props.chartStyle}
								chartDisplay={this.props.chartDisplay}
								planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								showAstroMeaning={this.props.showAstroMeaning}
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

						<TabPane tab="卜卦盘" key="horary">
							<HoraryMain
								fields={this.props.fields}
								fieldsAry={this.props.fieldsAry}
								height={childHeight}
								chartDisplay={this.props.chartDisplay}
								planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								showAstroMeaning={this.props.showAstroMeaning}
								hook={this.state.hook.horary}
								dispatch={this.props.dispatch}
							/>
						</TabPane>

						<TabPane tab="择日盘" key="election">
							<ElectionMain
								fields={this.props.fields}
								fieldsAry={this.props.fieldsAry}
								height={childHeight}
								chartDisplay={this.props.chartDisplay}
								planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								showAstroMeaning={this.props.showAstroMeaning}
								hook={this.state.hook.election}
								dispatch={this.props.dispatch}
							/>
						</TabPane>

						<TabPane tab="世俗盘" key="mundane">
							<MundaneMain
								fields={this.props.fields}
								fieldsAry={this.props.fieldsAry}
								height={childHeight}
								chartDisplay={this.props.chartDisplay}
								planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								showAstroMeaning={this.props.showAstroMeaning}
								hook={this.state.hook.mundane}
								dispatch={this.props.dispatch}
							/>
						</TabPane>

						<TabPane tab="巴比伦" key="babylon">
							<BabylonMain
								fields={this.props.fields}
								fieldsAry={this.props.fieldsAry}
								height={childHeight}
								chart={this.props.chart}
								chartDisplay={this.props.chartDisplay}
								planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								showAstroMeaning={this.props.showAstroMeaning}
								hook={this.state.hook.babylon}
								dispatch={this.props.dispatch}
							/>
						</TabPane>
					</Tabs>
					{this.renderQuickDock()}
				</div>
			</div>
		);
	}
}

export default AuxChartMain;
