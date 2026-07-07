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
import GeomancyMain from '../geomancy/GeomancyMain';
import TarotMain from '../tarot/TarotMain';
import QuickDockBar from '../common/QuickDockBar';


const TabPane = Tabs.TabPane;
const CNYIBU_VALID_TABS = ['suzhan', 'jinkou', 'tongshefa', 'huangji', 'wuzhao', 'taixuan', 'jingjue', 'shenyishu', 'geomancy', 'tarot'];

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
				},
				geomancy:{
					fun: null
				},
				tarot:{
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
			geomancy: createRef(),
			tarot: createRef(),
		};

		this.changeTab = this.changeTab.bind(this);
		this.renderBottomQuickDock = this.renderBottomQuickDock.bind(this);
		this.wrapDockHandler = this.wrapDockHandler.bind(this);

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

	componentDidMount(){
		this.unmounted = false;
		// 首渲时子页 ref 尚未挂上,取不到 getQuickDockConfig;挂载后补一拍让 dock 内容就位
		this.forceUpdate();
	}

	componentWillUnmount(){
		this.unmounted = true;
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

	// dock 不在子页渲染树内,子页 setState 不会连带重渲容器——动作后补拍 forceUpdate,
	// 让 hasResult/禁用态跟上子页内部状态。补三拍(0/600/2500ms):起盘/起课类动作是异步的,
	// 结果落地在网络/计算返回之后,单拍会读到旧态(dock 永远禁用的伪死)。
	wrapDockHandler(fn){
		if(!fn){
			return fn;
		}
		return (...args)=>{
			fn(...args);
			[0, 600, 2500].forEach((delay)=>{
				window.setTimeout(()=>{
					if(!this.unmounted){
						this.forceUpdate();
					}
				}, delay);
			});
		};
	}

	// 快捷栏契约:原十套硬编码分支(右栏 tab 镜像/跨子页目录/跨页导航,经 ref 穿透)全部撤除——
	// 那是目录不是快捷功能。各子页以 getQuickDockConfig() 自述主键/专属动词/保存,容器只透传。
	renderBottomQuickDock(){
		const tab = this.state.currentTab;
		const child = this.getActiveChild();
		const config = child && typeof child.getQuickDockConfig === 'function' ? child.getQuickDockConfig() : {};
		const wrapItem = (item)=>(item ? { ...item, onClick: this.wrapDockHandler(item.onClick) } : item);
		const primary = Array.isArray(config.primary) ? config.primary.map(wrapItem) : wrapItem(config.primary);
		return (
			<QuickDockBar
				page={`cnyibu-${tab}`}
				className="horosa-cnyibu-quick-dock"
				hasResult={config.hasResult !== undefined ? !!config.hasResult : false}
				primary={primary}
				extras={(config.extras || []).map(wrapItem)}
				save={this.wrapDockHandler(config.save)}
				ai={config.ai !== undefined ? config.ai : true}
				dispatch={this.props.dispatch}
			/>
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

					<TabPane tab="地占" key="geomancy">
						<GeomancyMain
							ref={this.childRefs.geomancy}
							value={this.props.chart}
							height={contentHeight}
							fields={this.props.fields}
							hook={this.state.hook.geomancy}
							dispatch={this.props.dispatch}
							hideQuickDock
						/>
					</TabPane>

					<TabPane tab="塔罗" key="tarot">
						<TarotMain
							ref={this.childRefs.tarot}
							value={this.props.chart}
							height={contentHeight}
							fields={this.props.fields}
							hook={this.state.hook.tarot}
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
