import { Component, createRef } from 'react';
import { XQTabs as Tabs } from '../xq-ui';
import { randomStr } from '../../utils/helper';
import SuZhanMain from '../suzhan/SuZhanMain';
import JinKouMain from '../jinkou/JinKouMain';
import TongSheFaMain from '../tongshefa/TongSheFaMain';
import HuangJiMain from '../huangji/HuangJiMain';
import WuZhaoMain from '../wuzhao/WuZhaoMain';
import TaiXuanMain from '../taixuan/TaiXuanMain';
import JingJueMain from '../jingjue/JingJueMain';
import ShenYiShuMain from '../shenyishu/ShenYiShuMain';
import XQIcon from '../xq-icons';


const TabPane = Tabs.TabPane;
const CNYIBU_VALID_TABS = ['suzhan', 'jinkou', 'tongshefa', 'huangji', 'wuzhao', 'taixuan', 'jingjue', 'shenyishu'];

function getRuntimeCnYiBuTab(){
	if(typeof window === 'undefined'){
		return null;
	}
	const tab = window.__horosaCnyibuCurrentTab;
	return CNYIBU_VALID_TABS.indexOf(tab) >= 0 ? tab : null;
}

function setRuntimeCnYiBuTab(tab){
	if(typeof window !== 'undefined' && CNYIBU_VALID_TABS.indexOf(tab) >= 0){
		window.__horosaCnyibuCurrentTab = tab;
	}
}

class CnYiBuMain extends Component{

	constructor(props) {
		super(props);
		const subtab = this.props.currentSubTab || getRuntimeCnYiBuTab() || 'suzhan';
		const tab = CNYIBU_VALID_TABS.indexOf(subtab) >= 0 ? subtab : 'suzhan';
		setRuntimeCnYiBuTab(tab);

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
				},
				huangji:{
					fun: null
				},
				wuzhao:{
					fun: null
				},
				taixuan:{
					fun: null
				},
				jingjue:{
					fun: null
				},
				shenyishu:{
					fun: null
				}
			},
		};

		this.childRefs = {
			suzhan: createRef(),
			jinkou: createRef(),
			tongshefa: createRef(),
			huangji: createRef(),
			wuzhao: createRef(),
			taixuan: createRef(),
			jingjue: createRef(),
			shenyishu: createRef(),
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
		setRuntimeCnYiBuTab(key);
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

	componentDidUpdate(prevProps){
		if(prevProps.currentSubTab !== this.props.currentSubTab){
			const key = this.props.currentSubTab;
			if(CNYIBU_VALID_TABS.indexOf(key) >= 0 && key !== this.state.currentTab){
				setRuntimeCnYiBuTab(key);
				this.setState({ currentTab: key }, ()=>{
					const hook = this.state.hook;
					if(hook[key] && hook[key].fun){
						hook[key].fun(this.props.fields, this.props.chart);
					}
				});
			}
		}
	}

	getActiveChild(){
		const ref = this.childRefs[this.state.currentTab];
		return ref && ref.current ? ref.current : null;
	}

	runChildAction(fn){
		const child = this.getActiveChild();
		if(child && fn){
			fn(child);
			window.setTimeout(()=>this.forceUpdate(), 0);
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
				{ label: '皇极经世', icon: 'quickReturn', onClick: ()=>this.changeTab('huangji') },
				{ label: '五兆', icon: 'quickPrimary', onClick: ()=>this.changeTab('wuzhao') },
				{ label: '太玄', icon: 'quickNote', onClick: ()=>this.changeTab('taixuan') },
				{ label: '荆诀', icon: 'book', onClick: ()=>this.changeTab('jingjue') },
				{ label: '神易数', icon: 'quickTransit', onClick: ()=>this.changeTab('shenyishu') },
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
				{ label: '皇极经世', icon: 'quickTransit', onClick: ()=>this.changeTab('huangji') },
				{ label: '五兆', icon: 'quickPrimary', onClick: ()=>this.changeTab('wuzhao') },
				{ label: '太玄', icon: 'quickNote', onClick: ()=>this.changeTab('taixuan') },
				{ label: '荆诀', icon: 'book', onClick: ()=>this.changeTab('jingjue') },
				{ label: '神易数', icon: 'quickTransit', onClick: ()=>this.changeTab('shenyishu') },
				{ label: 'AI助手', icon: 'quickAi', onClick: ()=>this.navigateFeature('aianalysis') },
			];
		}else if(tab === 'tongshefa'){
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
				{ label: '皇极经世', icon: 'quickTransit', onClick: ()=>this.changeTab('huangji') },
				{ label: '五兆', icon: 'quickPrimary', onClick: ()=>this.changeTab('wuzhao') },
				{ label: '太玄', icon: 'quickNote', onClick: ()=>this.changeTab('taixuan') },
				{ label: '荆诀', icon: 'book', onClick: ()=>this.changeTab('jingjue') },
				{ label: '神易数', icon: 'quickTransit', onClick: ()=>this.changeTab('shenyishu') },
			];
		}else if(tab === 'huangji'){
			const rightPanelTab = activeChild && activeChild.state ? activeChild.state.rightPanelTab : 'overview';
			actions = [
				{ label: '起盘', icon: 'quickPrimary', onClick: ()=>this.runChildAction((child)=>child.clickPlot()) },
				{ label: '概览', icon: 'quickComposite', active: rightPanelTab === 'overview', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('overview')) },
				{ label: '卦象', icon: 'quickTransit', active: rightPanelTab === 'gua', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('gua')) },
				{ label: '心易', icon: 'quickFirdaria', active: rightPanelTab === 'xinyi', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('xinyi')) },
				{ label: '年表', icon: 'quickNote', active: rightPanelTab === 'history', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('history')) },
				{ label: '典籍', icon: 'book', active: rightPanelTab === 'classics', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('classics')) },
				{ label: '保存', icon: 'quickReturn', onClick: ()=>this.runChildAction((child)=>child.clickSaveCase()) },
				{ label: '完整', icon: 'quickProfection', active: rightPanelTab === 'full', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('full')) },
				{ label: '快照', icon: 'quickAi', active: rightPanelTab === 'snapshot', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('snapshot')) },
				{ label: '太玄', icon: 'quickNote', onClick: ()=>this.changeTab('taixuan') },
				{ label: '荆诀', icon: 'book', onClick: ()=>this.changeTab('jingjue') },
				{ label: '神易数', icon: 'quickTransit', onClick: ()=>this.changeTab('shenyishu') },
			];
		}else if(tab === 'wuzhao'){
			const rightPanelTab = activeChild && activeChild.state ? activeChild.state.rightPanelTab : 'overview';
			actions = [
				{ label: '起盘', icon: 'quickPrimary', onClick: ()=>this.runChildAction((child)=>child.clickPlot()) },
				{ label: '概览', icon: 'quickComposite', active: rightPanelTab === 'overview', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('overview')) },
				{ label: '六位', icon: 'quickTransit', active: rightPanelTab === 'positions', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('positions')) },
				{ label: '标记', icon: 'quickFirdaria', active: rightPanelTab === 'flags', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('flags')) },
				{ label: '典籍', icon: 'book', active: rightPanelTab === 'classics', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('classics')) },
				{ label: '保存', icon: 'quickReturn', onClick: ()=>this.runChildAction((child)=>child.clickSaveCase()) },
				{ label: '完整', icon: 'quickProfection', active: rightPanelTab === 'full', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('full')) },
				{ label: '快照', icon: 'quickAi', active: rightPanelTab === 'snapshot', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('snapshot')) },
				{ label: '太玄', icon: 'quickNote', onClick: ()=>this.changeTab('taixuan') },
				{ label: '荆诀', icon: 'book', onClick: ()=>this.changeTab('jingjue') },
				{ label: '神易数', icon: 'quickTransit', onClick: ()=>this.changeTab('shenyishu') },
			];
		}else if(tab === 'taixuan'){
			const rightPanelTab = activeChild && activeChild.state ? activeChild.state.rightPanelTab : 'overview';
			actions = [
				{ label: '起筮', icon: 'quickPrimary', onClick: ()=>this.runChildAction((child)=>child.randomizeSeed()) },
				{ label: '概览', icon: 'quickComposite', active: rightPanelTab === 'overview', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('overview')) },
				{ label: '玄首', icon: 'quickTransit', active: rightPanelTab === 'head', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('head')) },
				{ label: '表', icon: 'quickFirdaria', active: rightPanelTab === 'lines', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('lines')) },
				{ label: '全文', icon: 'quickNote', active: rightPanelTab === 'fulltext', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('fulltext')) },
				{ label: '典籍', icon: 'book', active: rightPanelTab === 'classics', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('classics')) },
				{ label: '保存', icon: 'quickReturn', onClick: ()=>this.runChildAction((child)=>child.clickSaveCase()) },
				{ label: '快照', icon: 'quickAi', active: rightPanelTab === 'snapshot', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('snapshot')) },
				{ label: '荆诀', icon: 'book', onClick: ()=>this.changeTab('jingjue') },
				{ label: '神易数', icon: 'quickTransit', onClick: ()=>this.changeTab('shenyishu') },
			];
		}else if(tab === 'jingjue'){
			const rightPanelTab = activeChild && activeChild.state ? activeChild.state.rightPanelTab : 'overview';
			actions = [
				{ label: '重起', icon: 'quickPrimary', onClick: ()=>this.runChildAction((child)=>child.randomizeSeed()) },
				{ label: '概览', icon: 'quickComposite', active: rightPanelTab === 'overview', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('overview')) },
				{ label: '起课', icon: 'quickTransit', active: rightPanelTab === 'cast', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('cast')) },
				{ label: '十六卦', icon: 'quickFirdaria', active: rightPanelTab === 'gua', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('gua')) },
				{ label: '来源', icon: 'book', active: rightPanelTab === 'classics', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('classics')) },
				{ label: '保存', icon: 'quickReturn', onClick: ()=>this.runChildAction((child)=>child.clickSaveCase()) },
				{ label: '快照', icon: 'quickAi', active: rightPanelTab === 'snapshot', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('snapshot')) },
				{ label: '神易数', icon: 'quickTransit', onClick: ()=>this.changeTab('shenyishu') },
			];
		}else{
			const rightPanelTab = activeChild && activeChild.state ? activeChild.state.rightPanelTab : 'overview';
			actions = [
				{ label: '起盘', icon: 'quickPrimary', onClick: ()=>this.runChildAction((child)=>child.clickPlot()) },
				{ label: '概览', icon: 'quickComposite', active: rightPanelTab === 'overview', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('overview')) },
				{ label: '干支', icon: 'quickTransit', active: rightPanelTab === 'pillars', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('pillars')) },
				{ label: '五行', icon: 'quickReturn', active: rightPanelTab === 'wuxing', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('wuxing')) },
				{ label: '兵占', icon: 'quickFirdaria', active: rightPanelTab === 'military', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('military')) },
				{ label: '神煞', icon: 'quickProfection', active: rightPanelTab === 'shensha', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('shensha')) },
				{ label: '完整', icon: 'quickNote', active: rightPanelTab === 'full', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('full')) },
				{ label: '保存', icon: 'quickReturn', onClick: ()=>this.runChildAction((child)=>child.clickSaveCase()) },
				{ label: '来源', icon: 'book', active: rightPanelTab === 'classics', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('classics')) },
				{ label: '快照', icon: 'quickAi', active: rightPanelTab === 'snapshot', onClick: ()=>this.runChildAction((child)=>child.setRightPanelTab('snapshot')) },
			];
		}

		const hiddenQuickActions = {
			huangji: ['典籍', '完整', '快照'],
			wuzhao: ['典籍', '完整', '快照'],
			taixuan: ['典籍', '快照'],
			jingjue: ['来源', '快照'],
			shenyishu: ['完整', '来源', '快照'],
		}[tab];
		if(hiddenQuickActions){
			actions = actions.filter((item)=>hiddenQuickActions.indexOf(item.label) < 0);
		}

		const actionGridStyle = {
			gridTemplateColumns: `repeat(${actions.length}, minmax(58px, 1fr))`,
		};
		return (
			<div className="horosa-bottom-quick-dock horosa-cnyibu-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-cnyibu-quick-actions" style={actionGridStyle}>
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
					<TabPane tab="皇极经世" key="huangji">
						<HuangJiMain
							ref={this.childRefs.huangji}
							value={this.props.chart}
							height={contentHeight}
							fields={this.props.fields}
							hook={this.state.hook.huangji}
							dispatch={this.props.dispatch}
							hideQuickDock
						/>
					</TabPane>
					<TabPane tab="五兆" key="wuzhao">
						<WuZhaoMain
							ref={this.childRefs.wuzhao}
							value={this.props.chart}
							height={contentHeight}
							fields={this.props.fields}
							hook={this.state.hook.wuzhao}
							dispatch={this.props.dispatch}
							hideQuickDock
						/>
					</TabPane>
					<TabPane tab="太玄" key="taixuan">
						<TaiXuanMain
							ref={this.childRefs.taixuan}
							value={this.props.chart}
							height={contentHeight}
							fields={this.props.fields}
							hook={this.state.hook.taixuan}
							dispatch={this.props.dispatch}
							hideQuickDock
						/>
					</TabPane>
					<TabPane tab="荆诀" key="jingjue">
						<JingJueMain
							ref={this.childRefs.jingjue}
							value={this.props.chart}
							height={contentHeight}
							fields={this.props.fields}
							hook={this.state.hook.jingjue}
							dispatch={this.props.dispatch}
							hideQuickDock
						/>
					</TabPane>
					<TabPane tab="神易数" key="shenyishu">
						<ShenYiShuMain
							ref={this.childRefs.shenyishu}
							value={this.props.chart}
							height={contentHeight}
							fields={this.props.fields}
							hook={this.state.hook.shenyishu}
							dispatch={this.props.dispatch}
							hideQuickDock
						/>
					</TabPane>

				</Tabs>
				{this.renderBottomQuickDock()}
			</div>
		);
	}
}

export default CnYiBuMain;
