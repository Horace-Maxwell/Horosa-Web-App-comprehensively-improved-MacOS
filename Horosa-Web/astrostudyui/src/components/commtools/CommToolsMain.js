import { Component } from 'react';
import { wrapperPropsEqual } from '../../utils/chartUpdateGuard';
import { XQTabs as Tabs } from '../xq-ui';
import { randomStr } from '../../utils/helper';
import Azimuth from './Azimuth';
import CoordTrans from './CoordTrans';
import Calculator from './Calculator';
import DateCalc from './DateCalc';
import NaYing from './NaYing';
import InverseBazi from './InverseBazi';
import BaziPattern from './BaziPattern';
import GuaSymDesc from '../gua/GuaSymDesc';
import CuanGong12 from './CuanGong12';
import BaziPithy from './BaziPithy';
import TechniqueErrorBoundary from '../common/TechniqueErrorBoundary';
import { safeLocalStorageGet, safeLocalStorageSet } from '../../utils/safeStorage';
import { getLayoutViewportHeight } from '../../utils/shellZoom';

const TabPane = Tabs.TabPane;

class CommToolsMain extends Component{
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

		let tab = safeLocalStorageGet('commtoolstab');
		if(tab === undefined || tab === null || tab === ''){
			tab = 'naying';
		}

		this.state = {
			tab: tab,
			layoutH: 0,
		};

		this.changeTab = this.changeTab.bind(this);
		this.handleResize = this.handleResize.bind(this);
	}

	// 抽屉高按**布局域**视口量(壳缩放下 documentElement.clientHeight 恒为物理高,当布局高用 = 缩小档抽屉内容矮一截、
	// 放大档超出抽屉被裁);窗口尺寸 / 壳换档(会派发 resize)后重量。z=1 时两者相等,零变化。
	componentDidMount(){
		if(typeof window !== 'undefined'){ window.addEventListener('resize', this.handleResize); }
		this.handleResize();
	}

	componentWillUnmount(){
		if(typeof window !== 'undefined'){ window.removeEventListener('resize', this.handleResize); }
	}

	handleResize(){
		const h = getLayoutViewportHeight();
		if(h > 0 && Math.abs(h - (this.state.layoutH || 0)) >= 2){ this.setState({ layoutH: h }); }
	}

	changeTab(key){
		safeLocalStorageSet('commtoolstab', key);
		this.setState({
			tab: key
		});
	}

	render(){
		let height = this.state.layoutH > 0 ? this.state.layoutH : getLayoutViewportHeight();
		// 三个带自滚叶子的面板沿用各自的「窗口高 − 常数」算术,但喂给它们的是布局域窗口高(不再各自去读物理域 clientHeight)。
		const leafH = height;
		height = height - 80;

		let fields = this.props.fields;
		// 🔒 防黑屏:fields(或 lat/lon/date 子字段)在未起盘/重置/切页瞬态可能缺失,而坐标类 TabPane 的
		//   <Calculator lat={fields.lat.value}.../> 等 props 在 render 时即被 React.createElement 求值
		//   (即便该 tab 未激活也会求值)→ fields.lat.value 抛 TypeError、整个小工具(无边界)即黑屏。
		//   统一兜底取值,缺失即传 undefined,各坐标面板自身已能处理空值。
		const latV = (fields && fields.lat) ? fields.lat.value : undefined;
		const lonV = (fields && fields.lon) ? fields.lon.value : undefined;
		const timeV = (fields && fields.date) ? fields.date.value : undefined;

		// 🔒 每个面板独立 error boundary:任一技法 render 抛错只显本面板回退卡片,绝不黑全屏(Mac/JSC 更易触发)。
		const wrap = (label, node) => (<TechniqueErrorBoundary label={label}>{node}</TechniqueErrorBoundary>);

		return (
			<div className="horosa-commtools-root">
				<Tabs
					className="horosa-commtools-tabs"
					defaultActiveKey={this.state.tab}
					onChange={this.changeTab}
					tabPosition='left'
					style={{ height: height }}
				>
					<TabPane tab="纳音五行" key="naying">
						{wrap('纳音五行', <NaYing />)}
					</TabPane>

					<TabPane tab="计算器" key="calculator">
						{wrap('计算器', <Calculator lat={latV} lon={lonV} time={timeV} />)}
					</TabPane>

					<TabPane tab="日期计算" key="datecalc">
						{wrap('日期计算', <DateCalc lat={latV} lon={lonV} time={timeV} />)}
					</TabPane>

					<TabPane tab="地平坐标" key="azimuth">
						{wrap('地平坐标', <Azimuth lat={latV} lon={lonV} time={timeV} />)}
					</TabPane>

					<TabPane tab="黄赤坐标" key="cotrans">
						{wrap('黄赤坐标', <CoordTrans lat={latV} lon={lonV} time={timeV} />)}
					</TabPane>

					<TabPane tab="八字反查" key="inversebazi">
						{wrap('八字反查', <InverseBazi />)}
					</TabPane>

					<TabPane tab="八字格局" key="bazipattern">
						{wrap('八字格局', <BaziPattern />)}
					</TabPane>

					<TabPane tab="八卦类象" key="guasym">
						{wrap('八卦类象', <GuaSymDesc height={leafH} />)}
					</TabPane>

					<TabPane tab="十二串宫" key="cuangong12">
						{wrap('十二串宫', <CuanGong12 height={leafH} />)}
					</TabPane>

					<TabPane tab="八字规则" key="pithy">
						{wrap('八字规则', <BaziPithy height={leafH} />)}
					</TabPane>

				</Tabs>
			</div>
		)
	}
}

export default CommToolsMain;
