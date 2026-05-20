import { Component, createRef } from 'react';
import { XQTabs as Tabs } from '../xq-ui';
import { randomStr } from '../../utils/helper';
import SuZhanMain from '../suzhan/SuZhanMain';
import JinKouMain from '../jinkou/JinKouMain';
import TongSheFaMain from '../tongshefa/TongSheFaMain';
import XQIcon from '../xq-icons';


const TabPane = Tabs.TabPane;

class CnYiBuMain extends Component{

	constructor(props) {
		super(props);
		const subtab = this.props.currentSubTab ? this.props.currentSubTab : 'suzhan';
		const validTabs = ['suzhan', 'jinkou', 'tongshefa'];
		const tab = validTabs.indexOf(subtab) >= 0 ? subtab : 'suzhan';

		this.state = {
			divId: 'div_' + randomStr(8),
			currentTab: tab,
			hook:{
				suzhan:{
					fun: null
				},
				jinkou:{
					fun: null
				},
				tongshefa:{
					fun: null
				}
			},
		};

		this.childRefs = {
			suzhan: createRef(),
			jinkou: createRef(),
			tongshefa: createRef(),
		};

		this.changeTab = this.changeTab.bind(this);
		this.navigateFeature = this.navigateFeature.bind(this);
		this.renderBottomQuickDock = this.renderBottomQuickDock.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields, chartObj)=>{
				let hook = this.state.hook;
				if(hook[this.state.currentTab].fun){
					hook[this.state.currentTab].fun(fields, chartObj);
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
				hook[key].fun(this.props.fields, this.props.chart);
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

	getActiveChild(){
		const ref = this.childRefs[this.state.currentTab];
		return ref && ref.current ? ref.current : null;
	}

	runChildAction(fn){
		const child = this.getActiveChild();
		if(child && fn){
			fn(child);
			this.forceUpdate();
		}
	}

	navigateFeature(tabKey, subTab){
		if(this.props.dispatch){
			const payload = {
				currentTab: tabKey,
			};
			if(subTab){
				payload.currentSubTab = subTab;
			}
			this.props.dispatch({
				type: 'astro/save',
				payload,
			});
		}
	}

	renderBottomQuickDock(){
		const tab = this.state.currentTab;
		const activeChild = this.getActiveChild();
		let actions = [];

		if(tab === 'suzhan'){
			const rightPanelTab = activeChild && activeChild.state ? activeChild.state.rightPanelTab : 'overview';
			actions = [
				{ label: '概览', icon: 'quickPrimary', active: rightPanelTab === 'overview', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('overview')) },
				{ label: '宫宿', icon: 'quickComposite', active: rightPanelTab === 'houses', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('houses')) },
				{ label: '快照', icon: 'quickNote', active: rightPanelTab === 'snapshot', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('snapshot')) },
				{ label: '金口诀', icon: 'quickFirdaria', onClick: ()=>this.changeTab('jinkou') },
				{ label: '统摄法', icon: 'quickProfection', onClick: ()=>this.changeTab('tongshefa') },
				{ label: '太乙', icon: 'quickReturn', onClick: ()=>this.navigateFeature('taiyi') },
				{ label: '遁甲', icon: 'quickTransit', onClick: ()=>this.navigateFeature('dunjia') },
				{ label: 'AI助手', icon: 'quickAi', onClick: ()=>this.navigateFeature('aianalysis') },
			];
		}else if(tab === 'jinkou'){
			const rightPanelTab = activeChild && activeChild.state ? activeChild.state.rightPanelTab : 'overview';
			actions = [
				{ label: '起课', icon: 'quickPrimary', onClick: ()=>this.runChildAction((child)=>child.requestGods(child.props.fields, child.props.value)) },
				{ label: '概览', icon: 'quickComposite', active: rightPanelTab === 'overview', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('overview')) },
				{ label: '四位', icon: 'quickTransit', active: rightPanelTab === 'rows', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('rows')) },
				{ label: '神煞', icon: 'quickFirdaria', active: rightPanelTab === 'gods', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('gods')) },
				{ label: '保存', icon: 'quickNote', onClick: ()=>this.runChildAction((child)=>child.clickSaveCase()) },
				{ label: '宿盘', icon: 'quickReturn', onClick: ()=>this.changeTab('suzhan') },
				{ label: '统摄法', icon: 'quickProfection', onClick: ()=>this.changeTab('tongshefa') },
				{ label: 'AI助手', icon: 'quickAi', onClick: ()=>this.navigateFeature('aianalysis') },
			];
		}else{
			const detailTab = activeChild && activeChild.state ? activeChild.state.detailTab : 'observe32';
			const showMatrixBorder = activeChild && activeChild.state ? activeChild.state.showMatrixBorder : true;
			actions = [
				{ label: '三十二观', icon: 'quickPrimary', active: detailTab === 'observe32', onClick: ()=>this.runChildAction((child)=>child.changeDetailTab('observe32')) },
				{ label: '三界', icon: 'quickComposite', active: detailTab === 'sanjie', onClick: ()=>this.runChildAction((child)=>child.changeDetailTab('sanjie')) },
				{ label: '爻位', icon: 'quickTransit', active: detailTab === 'yaowei', onClick: ()=>this.runChildAction((child)=>child.changeDetailTab('yaowei')) },
				{ label: '纳甲', icon: 'quickFirdaria', active: detailTab === 'najia', onClick: ()=>this.runChildAction((child)=>child.changeDetailTab('najia')) },
				{ label: showMatrixBorder ? '隐藏边框' : '显示边框', icon: 'quickNote', onClick: ()=>this.runChildAction((child)=>child.onBorderToggle(showMatrixBorder ? 0 : 1)) },
				{ label: '保存', icon: 'quickReturn', onClick: ()=>this.runChildAction((child)=>child.clickSaveCase()) },
				{ label: '宿盘', icon: 'quickProfection', onClick: ()=>this.changeTab('suzhan') },
				{ label: '金口诀', icon: 'quickAi', onClick: ()=>this.changeTab('jinkou') },
			];
		}

		return (
			<div className="horosa-bottom-quick-dock horosa-cnyibu-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-cnyibu-quick-actions">
					{actions.map((item)=>(
						<button
							type="button"
							key={item.label}
							className={`horosa-bottom-quick-button horosa-cnyibu-quick-button${item.active ? ' is-active' : ''}`}
							onClick={item.onClick}
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
		const contentHeight = typeof height === 'number' ? Math.max(height - 44, 260) : 'calc(100% - 44px)';
		const tab = this.state.currentTab;

		return (
			<div id={this.state.divId} className="horosa-cnyibu-page">
				<Tabs 
					defaultActiveKey={tab} tabPosition='right'
					activeKey={tab}
					onChange={this.changeTab}
					style={{ height: '100%', minHeight: 0 }}
				>
					<TabPane tab="宿盘" key="suzhan">
						<SuZhanMain 
							ref={this.childRefs.suzhan}
							value={this.props.chart}
							height={contentHeight}
							fields={this.props.fields}
							chartDisplay={this.props.chartDisplay}
							planetDisplay={this.props.planetDisplay}
							hook={this.state.hook.suzhan}
							dispatch={this.props.dispatch}
							hideQuickDock
						/>
					</TabPane>

					<TabPane tab="金口诀" key="jinkou">
						<JinKouMain
							ref={this.childRefs.jinkou}
							value={this.props.chart}
							height={contentHeight}
							fields={this.props.fields}
							hook={this.state.hook.jinkou}
							dispatch={this.props.dispatch}
							hideQuickDock
						/>
					</TabPane>
					<TabPane tab="统摄法" key="tongshefa">
						<TongSheFaMain
							ref={this.childRefs.tongshefa}
							value={this.props.chart}
							height={contentHeight}
							fields={this.props.fields}
							hook={this.state.hook.tongshefa}
							dispatch={this.props.dispatch}
						/>
					</TabPane>

				</Tabs>
				{this.renderBottomQuickDock()}
			</div>
		);
	}
}

export default CnYiBuMain;
