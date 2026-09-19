import { Component } from 'react';
import { XQTabs as Tabs } from '../xq-ui';
import AstroMidpoint from './AstroMidpoint';
import UranianDialMain from './UranianDialMain';
import UranianGraphicEphemeris from './UranianGraphicEphemeris';
import UranianHouseFrames from './UranianHouseFrames';
import { getStoredUranianDisplay, URANIAN_DISPLAY_EVENT } from './UranianDialStyle';   // [Q-355] 六宫框开关要即时反映到页签栏
// [视觉底线·2026-09-17] 最小尺寸是屏幕可读意图(物理 px),壳缩放 z 下按 1/z 折算成布局 px;z=1 恒等。
import { visualFloorPx } from '../../utils/zoomDomain';

const TabPane = Tabs.TabPane;

class AstroGermany extends Component{

	constructor(props) {
		super(props);
		this.state = {
			currentTab: 'Midpoint',
			hook: {
				Midpoint: { fun: null },
				Dial: { fun: null },
				GraphicEphem: { fun: null },
				HouseFrames: { fun: null },
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
		// [Q-355/T-336] 「六宫框」开关住在子组件(90°中点盘的显示偏好),而决定页签出不出现的是**本组件** render 里
		// 读的那次 getStoredUranianDisplay() —— 子组件 setState 不会让父重渲。订阅写入事件即时重渲,页签当场跟上。
		this._onUranianDisplay = ()=>{ if(this._mounted !== false){ this.forceUpdate(); } };
		if(typeof window !== 'undefined'){ window.addEventListener(URANIAN_DISPLAY_EVENT, this._onUranianDisplay); }
	}

	componentWillUnmount(){
		this._mounted = false;
		if(typeof window !== 'undefined' && this._onUranianDisplay){ window.removeEventListener(URANIAN_DISPLAY_EVENT, this._onUranianDisplay); }
	}

	render(){
		let height = this.props.height ? this.props.height : 760;
		// 子 tab nav 占约 44px，扣掉以免子页底部被挤掉。
		let childHeight = Math.max(visualFloorPx(360), height - 44);
		let hook = this.state.hook;
		// 六宫框 Tab 受 WP-1「showHouseFrames」开关控制(汉堡/美国对称默认开;纯净派/宇宙生物学关)。
		// 关时直接隐藏该 Tab,避免与流派语义冲突;开关存于 90°中点盘的持久化偏好,实时读取。
		let showFrames = true;
		try { showFrames = getStoredUranianDisplay().showHouseFrames !== false; } catch (e) { showFrames = true; }
		// 当前 Tab 落在被隐藏的「六宫框」上时回退到「行星中点」,防止白屏。
		let activeKey = (!showFrames && this.state.currentTab === 'HouseFrames') ? 'Midpoint' : this.state.currentTab;

		return (
			<div className="horosa-aux-module-page xq-chart-renderer xq-chart-renderer-germany">
				<Tabs activeKey={activeKey} onChange={this.changeTab} className="horosa-content-tabs horosa-germany-subtabs">
					<TabPane tab="行星中点" key="Midpoint">
						<AstroMidpoint
							onChange={this.onFieldsChange}
							height={childHeight}
							fields={this.props.fields}
							chart={this.props.chart}
							wheelArt={this.props.wheelArt}
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
							fieldsAry={this.props.fieldsAry}
							chart={this.props.chart}
							planetDisplay={this.props.planetDisplay}
							hook={hook.Dial}
						/>
					</TabPane>
					<TabPane tab="图形星历" key="GraphicEphem">
						<UranianGraphicEphemeris
							height={childHeight}
							fields={this.props.fields}
							chart={this.props.chart}
							hook={hook.GraphicEphem}
						/>
					</TabPane>
					{showFrames ? (
						<TabPane tab="六宫框" key="HouseFrames">
							<UranianHouseFrames
								height={childHeight}
								fields={this.props.fields}
								chart={this.props.chart}
								wheelArt={this.props.wheelArt}
								chartDisplay={this.props.chartDisplay}
								planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								showAstroMeaning={this.props.showAstroMeaning}
								hook={hook.HouseFrames}
							/>
						</TabPane>
					) : null}
				</Tabs>
			</div>
		);
	}
}

export default AstroGermany;
