import { Component } from 'react';
import { Row, Col, Tabs, } from 'antd';
import { randomStr } from '../../utils/helper';
import SuZhanMain from '../suzhan/SuZhanMain';
import GuaZhanMain from '../guazhan/GuaZhanMain';
import LiuRengMain from '../lrzhan/LiuRengMain';
import JinKouMain from '../jinkou/JinKouMain';
import DunJiaMain from '../dunjia/DunJiaMain';
import TaiYiMain from '../taiyi/TaiYiMain';


const TabPane = Tabs.TabPane;

class CnYiBuMain extends Component{

	constructor(props) {
		super(props);
		const subtab = this.props.currentSubTab ? this.props.currentSubTab : 'suzhan';
		const validTabs = ['suzhan', 'guazhan', 'liureng', 'jinkou', 'dunjia', 'taiyi'];
		const tab = validTabs.indexOf(subtab) >= 0 ? subtab : 'suzhan';

		this.state = {
			divId: 'div_' + randomStr(8),
			currentTab: tab,
			hook:{
				suzhan:{
					fun: null
				},
				guazhan:{
					fun: null
				},
				liureng:{
					fun: null
				},
				jinkou:{
					fun: null
				},
				dunjia:{
					fun: null
				},
				taiyi:{
					fun: null
				}
			},
		};

		this.changeTab = this.changeTab.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields)=>{
				let hook = this.state.hook;
				if(hook[this.state.currentTab].fun){
					hook[this.state.currentTab].fun(fields);
				}
			};
		}

	}

	changeTab(key){
		let hook = this.state.hook;
		this.setState({
			currentTab: key,
		}, ()=>{
			if(hook[key].fun){
				hook[key].fun(this.props.fields);
			}
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
		const tab = this.state.currentTab;

		return (
			<div id={this.state.divId}>
				<Tabs 
					defaultActiveKey={tab} tabPosition='right'
					activeKey={tab}
					onChange={this.changeTab}
					style={{ height: height }}
				>
					<TabPane tab="宿盘" key="suzhan">
						<SuZhanMain 
							value={this.props.chart}
							height={height}
							fields={this.props.fields}
							chartDisplay={this.props.chartDisplay}
							planetDisplay={this.props.planetDisplay}
							hook={this.state.hook.suzhan}
							dispatch={this.props.dispatch}
						/>
					</TabPane>

					<TabPane tab="易卦" key="guazhan">
						<GuaZhanMain 
							value={this.props.chart}
							height={height}
							fields={this.props.fields}
							hook={this.state.hook.guazhan}
							dispatch={this.props.dispatch}
						/>
					</TabPane>

					<TabPane tab="六壬" key="liureng">
						<LiuRengMain 
							value={this.props.chart}
							height={height}
							fields={this.props.fields}
							hook={this.state.hook.liureng}
							dispatch={this.props.dispatch}
						/>
					</TabPane>
					<TabPane tab="金口诀" key="jinkou">
						<JinKouMain
							value={this.props.chart}
							height={height}
							fields={this.props.fields}
							hook={this.state.hook.jinkou}
							dispatch={this.props.dispatch}
						/>
					</TabPane>
					<TabPane tab="遁甲" key="dunjia">
						<DunJiaMain
							value={this.props.chart}
							height={height}
							fields={this.props.fields}
							hook={this.state.hook.dunjia}
							dispatch={this.props.dispatch}
						/>
					</TabPane>
					<TabPane tab="太乙" key="taiyi">
						<TaiYiMain
							value={this.props.chart}
							height={height}
							fields={this.props.fields}
							hook={this.state.hook.taiyi}
							dispatch={this.props.dispatch}
						/>
					</TabPane>

				</Tabs>
			</div>
		);
	}
}

export default CnYiBuMain;
