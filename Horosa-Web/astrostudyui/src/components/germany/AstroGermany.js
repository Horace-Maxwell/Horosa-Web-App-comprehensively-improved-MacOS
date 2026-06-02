import { Component } from 'react';
import { XQTabs as Tabs } from '../xq-ui';
import AstroMidpoint from './AstroMidpoint';
import UranianDialMain from './UranianDialMain';

const TabPane = Tabs.TabPane;

class AstroGermany extends Component{

	constructor(props) {
		super(props);
		this.state = {
			currentTab: 'Midpoint',
			hook: {
				Midpoint: { fun: null },
				Dial: { fun: null },
			},
		}

		this.changeTab = this.changeTab.bind(this);
		this.onFieldsChange = this.onFieldsChange.bind(this);
		this.callCurrentTabHook = this.callCurrentTabHook.bind(this);

		if(this.props.hook){
			this.props.hook.fun = ()=>{
				this.callCurrentTabHook();
			};
		}
	}

	callCurrentTabHook(){
		let hook = this.state.hook;
		if(hook[this.state.currentTab] && hook[this.state.currentTab].fun){
			hook[this.state.currentTab].fun();
		}
	}

	changeTab(key){
		this.setState({ currentTab: key }, ()=>{
			this.callCurrentTabHook();
		});
	}

	onFieldsChange(values){
		if(this.props.onChange){
			this.props.onChange(values);
		}
	}

	componentDidMount(){
		this.callCurrentTabHook();
	}

	render(){
		let height = this.props.height ? this.props.height : 760;
		// 子 tab nav 占约 44px，扣掉以免子页底部被挤掉。
		let childHeight = Math.max(360, height - 44);
		let hook = this.state.hook;

		return (
			<div className="horosa-aux-module-page xq-chart-renderer xq-chart-renderer-germany">
				<Tabs activeKey={this.state.currentTab} onChange={this.changeTab} className="horosa-content-tabs horosa-germany-subtabs">
					<TabPane tab="行星中点" key="Midpoint">
						<AstroMidpoint
							onChange={this.onFieldsChange}
							height={childHeight}
							fields={this.props.fields}
							chart={this.props.chart}
							chartDisplay={this.props.chartDisplay}
							planetDisplay={this.props.planetDisplay}
							lotsDisplay={this.props.lotsDisplay}
							showAstroMeaning={this.props.showAstroMeaning}
							hook={hook.Midpoint}
						/>
					</TabPane>
					<TabPane tab="90°中点盘" key="Dial">
						<UranianDialMain
							height={childHeight}
							fields={this.props.fields}
							chart={this.props.chart}
							planetDisplay={this.props.planetDisplay}
							hook={hook.Dial}
						/>
					</TabPane>
				</Tabs>
			</div>
		);
	}
}

export default AstroGermany;
