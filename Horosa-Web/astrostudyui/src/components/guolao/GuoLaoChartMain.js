import { Component } from 'react';
import '../../utils/timeBasisLine';
import '../../utils/recordFieldsRestore';   // 首开只补空的判默认基准
import { wrapperPropsEqual } from '../../utils/chartUpdateGuard';
// R4-B3(horosa_prefetch_registry_v1):七政三段链式预取登记(R10 情报③)。
import { stepPrefetchEnabled } from '../../utils/perfFlags';
import { registerStepPrefetcher, unregisterStepPrefetcher } from '../../utils/stepPrefetch';
import '../../utils/safeStorage';
import '../../utils/dayBoundary';
import XQIcon from '../xq-icons';
import '../../utils/request';
import {randomStr,} from '../../utils/helper';
import '../comp/DateTime';
import GuoLaoInput from './GuoLaoInput';
import './guolaoData';
import './guolaoTransit';
import GuoLaoChart from './GuoLaoChart';
import GuoLaoMoiraPanel from './GuoLaoMoiraPanel';
import '../../utils/baziLunarLocal';   // 无头/快照路径的流年月支(月限用)
import GuoLaoMoiraWheel from './GuoLaoMoiraWheel';
import GuoLaoMoiraPickWheel from './GuoLaoMoiraPickWheel';
import { GUOLAO_CHART_STYLE_MOIRA, GUOLAO_CHART_STYLE_PICK, GUOLAO_CHART_STYLE_QIZHENG, getStoredGuolaoChartStyle, getStoredGuolaoDisplay, getStoredMoiraTransitGodsVisible, getStoredGuolaoElection, getStoredGuolaoEleLifeMode } from './GuoLaoChartStyle';
import { fetchMoiraQizhengRules } from '../../services/qizheng';
import '../../constants/AstroText';
import '../suzhan/SZConst';
import '../su28/Su28Helper';
import '../astro/AstroHelper';
// 组件外的模块级助手(纯函数 / 常量 / 表 / 小组件)与组件方法(inputs · requests · election · quickPanels · kinPanels;类后 mixinMethods 挂回原型)按职责拆在 ./main/ 下;
// 构造、生命周期、render 与对外导出面仍在本文件。
import { getStoredGuolaoEngineMode, getStoredKinastroQizhengOptions } from './main/prefs';
import { applyGuolaoNodeMode } from './main/aspectsNodeMode';
import { fetchGuolaoChartCached } from './main/chartCache';
import { fieldsToParams, makeDefaultMoiraTransitTime, paramsWithMoiraTransit } from './main/params';
import { loadGuolaoAscRaMode, guolaoAscRaModeOf, withAscRaMode, withAscRaModeRoot } from '../../utils/ascRaMode';
import { mixinMethods } from '../../utils/mixinMethods';
import { inputMethods } from './main/inputs';
import { requestMethods } from './main/requests';
import { electionMethods } from './main/election';
import { quickPanelMethods } from './main/quickPanels';
import { kinPanelMethods } from './main/kinPanels';
// 对外导出面不变:搬进子模块的导出原样重导出
export { applyGuolaoNodeMode } from './main/aspectsNodeMode';
export { guolaoSu28ModeFromFields } from './main/fieldModes';
export { computeGuolaoSeedPatch, warmGuolaoNatal } from './main/params';
export {
	buildHouseSuAndGodsSection, buildGuolaoSnapshotForFields, buildStarDignityMotionSection,
	buildGuolaoWeakSolidSection, buildGuolaoBirthStarsSection, buildGuolaoMastersSection,
	buildGuolaoLimitCalcSection, buildGuolaoAspectSection, buildGuolaoLimitSection,
} from './main/snapshot';


class GuoLaoChartMain extends Component{
	constructor(props) {
		super(props);
		// 择日内嵌:引擎锁定星阙七政引擎(zeriPageCalibre.QIZHENG_ZERI_LOCKED)—— 本机记忆是「坚七政」也从 Moira 圆盘起
		const engineLocked = this.engineLockedByZeri();
		const rawChartStyle = getStoredGuolaoChartStyle();
		const storedChartStyle = engineLocked && rawChartStyle === GUOLAO_CHART_STYLE_QIZHENG ? GUOLAO_CHART_STYLE_MOIRA : rawChartStyle;
		const storedEngineMode = engineLocked ? 'horosa' : (storedChartStyle === GUOLAO_CHART_STYLE_QIZHENG ? 'kinastro' : getStoredGuolaoEngineMode());
		this.state = {
			chartObj: null,
			ascRaMode: loadGuolaoAscRaMode(),   // 赤仪上升取法:只用来在左栏改了之后重画 / 重存快照(取值一律经 guolaoAscRaModeOf)
			moiraTransitTime: makeDefaultMoiraTransitTime(props.fields),
			moiraTransitChartObj: null,
			moiraTransitLoading: false,
			tips: null,
			moiraRules: null,
			moiraPanelChartObj: null,
			moiraPanelTransitChartObj: null,
			moiraPanelTransitParams: null,
			moiraLoading: false,
			bundleLoading: false,
			guolaoDisplay: getStoredGuolaoDisplay(),
			chartStyle: storedEngineMode === 'kinastro' ? GUOLAO_CHART_STYLE_QIZHENG : storedChartStyle,
			// 天星择日双轮(pick 盘式):类B 选项 blob + 类A 立命时刻 + 端点数据
			electionOptions: getStoredGuolaoElection(),
			eleLifeMode: getStoredGuolaoEleLifeMode(),
			electionData: null,
			electionLoading: false,
			electionDeclOutOfRange: false,
			showMoiraTransitGods: getStoredMoiraTransitGodsVisible(),
			moiraQuickDialog: null,
			moiraStyleLevel: 3,
			engineMode: storedEngineMode,
			kinastroOptions: getStoredKinastroQizhengOptions(),
			qizhengKinPan: null,
			qizhengKinLoading: false,
			qizhengKinError: '',
			qizhengKinActiveTab: 'overview',
		};

		this.unmounted = false;
		this.bundleSeq = 0;
		this.chartReqSeq = 0;
		this.moiraReqSeq = 0;
		this.prefetchTimer = null;
		this.moiraTransitReqSeq = 0;
		this.qizhengKinReqSeq = 0;
		this.electionReqSeq = 0;

		this.onFieldsChange = this.onFieldsChange.bind(this);
		this.requestChart = this.requestChart.bind(this);
		this.requestChartObj = this.requestChartObj.bind(this);
		this.requestGuolaoBundle = this.requestGuolaoBundle.bind(this);
		this.onGuolaoDisplayChange = this.onGuolaoDisplayChange.bind(this);
		this.onLimitAgeClick = this.onLimitAgeClick.bind(this);
		this.requestMoiraTransitChart = this.requestMoiraTransitChart.bind(this);
		this.genParams = this.genParams.bind(this);
		this.onTipClick = this.onTipClick.bind(this);
		this.saveGuolaoAISnapshot = this.saveGuolaoAISnapshot.bind(this);
		this.applyChartObj = this.applyChartObj.bind(this);
		this.prefetchChart = this.prefetchChart.bind(this);
		this.requestMoiraRules = this.requestMoiraRules.bind(this);
		this.commitMoiraPanel = this.commitMoiraPanel.bind(this);
		this.ensureGuolaoDefaults = this.ensureGuolaoDefaults.bind(this);
		this.onChartStyleChange = this.onChartStyleChange.bind(this);
		this.onMoiraTransitTimeChange = this.onMoiraTransitTimeChange.bind(this);
		this.onMoiraTransitGodsVisibleChange = this.onMoiraTransitGodsVisibleChange.bind(this);
		this.openMoiraQuickDialog = this.openMoiraQuickDialog.bind(this);
		this.closeMoiraQuickDialog = this.closeMoiraQuickDialog.bind(this);
		this.onMoiraStyleLevelChange = this.onMoiraStyleLevelChange.bind(this);
		this.onEngineModeChange = this.onEngineModeChange.bind(this);
		this.onKinastroOptionChange = this.onKinastroOptionChange.bind(this);
		this.requestKinastroQizheng = this.requestKinastroQizheng.bind(this);
		this.onQizhengKinTabChange = this.onQizhengKinTabChange.bind(this);
		this.handleSnapshotRefreshRequest = this.handleSnapshotRefreshRequest.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields, chartObj)=>{
				if(this.unmounted){
					return;
				}
				this.requestChartObj(fields, chartObj);
			};
			// 所见那张盘实际所用的 fields(请求过了代次校验、确定上屏的那一次):择日宿主存案取它 —— 内嵌页自己重排、宿主改了工作台没重排、覆盖层里没确定的草稿,都不会让存案的时间地点与所见不一致(两路都按发请求那一拍的 props.fields 起盘)
			this.props.hook.getPlottedFields = ()=>this._plottedFields || null;
			// 时间变化即预热流年盘(与主 /chart 并行;正式流程到流年段时在途/缓存秒中)。
			// 主 /chart 由模型层照发不重复;失败静默,正式请求自兜底。latency: 主盘+流年串行 → max(主盘,流年)。
			this.props.hook.prewarmRequests = (flds)=>{
				if(this.unmounted || this.state.engineMode === 'kinastro'){ return; }
				if(this.state.chartStyle === GUOLAO_CHART_STYLE_QIZHENG){ return; }
				try{
					const tp = paramsWithMoiraTransit(flds || this.props.fields, this.state.moiraTransitTime);
					if(tp){ fetchGuolaoChartCached(tp, { silent: true }).catch(()=>{ /* 预热静默 */ }); }
				}catch(e){ /* 预热失败无害 */ }
			};
			// R4-B3(horosa_prefetch_registry_v1,R10 情报③「七政三段」):七政步进链=本命→流年→
			// 判读规则三段串行,前两段有缓存、第三段(fetchMoiraQizhengRules,几百 ms 重计算)每步必付。
			// 登记的预取任务把三段【链式】全预热(与 requestGuolaoBundle 同构:同 params/同
			// applyGuolaoNodeMode/同 rules 入参形态 → 键逐字节同,真点步进时第三段归零)。
			// 🔴 取现时红线:moiraTransitTime 为 null(默认过运=「现在」)时流年/规则两段的键含
			//    构造时刻的「现在」——真点时刻已变,键不同=预热白打且徒增负载 → 该态只暖本命段。
			//    键不同也意味着绝不会错误命中旧「现在」(无「今天被冻住」降级)。
			if(stepPrefetchEnabled()){
				this._guolaoStepPrefetcher = (steppedFields)=>{
					if(this.unmounted || this.state.engineMode === 'kinastro'){
						return [];
					}
					if(this.state.chartStyle === GUOLAO_CHART_STYLE_QIZHENG){
						return [];
					}
					let params = null;
					try{
						params = fieldsToParams(steppedFields);
					}catch(e){
						return [];
					}
					if(!params){
						return [];
					}
					const transitTime = this.state.moiraTransitTime;
					const warmAllStages = transitTime !== null && transitTime !== undefined;
					return [{
						name: 'guolao:natal',
						path: '/chart',
						run: async ()=>{
							const natalRaw = await fetchGuolaoChartCached(params, { silent: true });
							if(!natalRaw || !warmAllStages || this.unmounted){
								return natalRaw || null;
							}
							try{
								const chartObj = applyGuolaoNodeMode(natalRaw, steppedFields);
								const tp = paramsWithMoiraTransit(steppedFields, transitTime);
								let transitObj = null;
								if(tp){
									const tRaw = await fetchGuolaoChartCached(tp, { silent: true }).catch(()=>null);
									transitObj = tRaw ? applyGuolaoNodeMode(tRaw, steppedFields) : null;
								}
								// 第三段:判读规则 —— 结果落 services/qizheng 的 cachedPost 缓存,
								// 真点步进到该时刻时 requestGuolaoBundle 的规则段直接命中。
								await fetchMoiraQizhengRules({
									params,
									chartObj,
									transitParams: tp,
									transitChartObj: transitObj,
								}, { silent: true, timeoutMs: 12000 });
							}catch(e){ /* 后两段预热失败静默:首点回到冷即付 */ }
							return natalRaw;
						},
					}];
				};
				registerStepPrefetcher('guolao', this._guolaoStepPrefetcher);
			}
		}
	}


	// WP-H-2 极速化:重 wrapper sCU —— 全 props 机械浅比(函数型跳过,详 wrapperPropsEqual);
	// state 任一引用变照常重渲(setState 恒换引用,此比既完整又廉价)。
	// 收益:宿主因无关状态重渲时,本重组件整树不再白跑。关 chartSCU 开关 = 恒重渲旧行为。
	shouldComponentUpdate(nextProps, nextState){
		if(nextState !== this.state){
			return true;
		}
		return !wrapperPropsEqual(this.props, nextProps);
	}

	componentDidMount(){
		this.unmounted = false;
		// v2.2.1: 监听全局日界 / 晚子时·时柱起干切换 → 重新 fetch 七政四余/Moira 盘。
		// 关键:用 setTimeout 0 延迟到下一 macrotask,让 dva 的 syncFromGlobalLateZiHour subscription
		// 先把 fields.lateZiHourUseNextDay.value 更新到 store + React 把新 props 透给本组件,再 fetch。
		// 否则 this.props.fields 在 listener 同步触发时仍是旧 snapshot,fetch 用的还是旧值,Moira 必须刷新页面才生效。
		if(typeof window !== 'undefined'){
			const refetch = () => {
				if(this.unmounted) return;
				setTimeout(() => {
					if(this.unmounted) return;
					if(this.state.engineMode === 'kinastro'){
						this.requestKinastroQizheng();
					} else if(this.props.fields){
						this.requestChartObj();
					}
				}, 0);
			};
			this._dayBoundaryListener = refetch;
			this._lateZiHourListener = refetch;
			window.addEventListener('horosa:day-boundary-changed', this._dayBoundaryListener);
			window.addEventListener('horosa:late-zi-hour-mode-changed', this._lateZiHourListener);
			window.addEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
		if(this.state.engineMode === 'kinastro'){
			this.requestKinastroQizheng();
			return;
		}
		if(this.ensureGuolaoDefaults()){
			return;
		}
		if(this.props.fields){
			this.requestChartObj();
		}
	}

	componentDidUpdate(prevProps, prevState){
		if(this.state.engineMode === 'kinastro'){
			if(prevProps.fields !== this.props.fields || (prevState && prevState.engineMode !== this.state.engineMode)){
				this.requestKinastroQizheng();
			}
			return;
		}
		// 坚七政样式(kinastro 引擎)不起本页的盘、也不补空;切到别的样式那一刻补一次(fields 没变也要补)
		const leftKinastro = !!(prevState && prevState.engineMode === 'kinastro');
		if((prevProps.fields !== this.props.fields || leftKinastro) && this.ensureGuolaoDefaults()){
			return;
		}
		if(prevProps.planetDisplay !== this.props.planetDisplay){
			this.saveGuolaoAISnapshot(null, this.state.chartObj);
		}
		// 命主取法 / 行运法 / 定童限 / 年界 等显示偏好改动后重存页面快照:此前只在盘数据到达时存,
		// 切「行运法」后 [起盘信息] 标签行、[大限] 与 [限法实算] 段仍是旧值(右栏已变)。
		if(prevState && prevState.guolaoDisplay !== this.state.guolaoDisplay && this.state.chartObj){
			this.saveGuolaoAISnapshot(null, this.state.chartObj);
		}
		if(prevProps.value !== this.props.value && this.props.value){
			this.requestGuolaoBundle(this.props.value);
		}
		// 天星择日:pick 盘式且(切入盘式/择时变化/立命时刻变化/流年盘刷新)→ 重取双轮数据;
		// MOIRA 圆盘同触发(西占宫位格吃 staticHousesBySystem,本盘时刻变化时 staticDate 须跟上)。
		if(this.state.chartStyle === GUOLAO_CHART_STYLE_PICK || this.state.chartStyle === GUOLAO_CHART_STYLE_MOIRA){
			const styleSwitched = prevState && prevState.chartStyle !== this.state.chartStyle;
			const timeChanged = prevState && prevState.moiraTransitTime !== this.state.moiraTransitTime;
			const lifeChanged = prevState && prevState.eleLifeMode !== this.state.eleLifeMode;
			const transitArrived = prevState && prevState.moiraTransitChartObj !== this.state.moiraTransitChartObj;
			const valueChanged = prevProps.value !== this.props.value && !!this.props.value;
			if(styleSwitched || timeChanged || lifeChanged || valueChanged || (transitArrived && !this.state.electionData)){
				this.requestElectionData();
			}
		}
	}

	componentWillUnmount(){
		this.unmounted = true;
		// R4-B3:反注册步进预取器(防卸载后闭包吃到死组件态)。
		if(this._guolaoStepPrefetcher){
			unregisterStepPrefetcher('guolao', this._guolaoStepPrefetcher);
			this._guolaoStepPrefetcher = null;
		}
		this.moiraReqSeq++;
		this.moiraTransitReqSeq++;
		this.qizhengKinReqSeq++;
		if(typeof window !== 'undefined'){
			if(this._dayBoundaryListener){
				window.removeEventListener('horosa:day-boundary-changed', this._dayBoundaryListener);
			}
			if(this._lateZiHourListener){
				window.removeEventListener('horosa:late-zi-hour-mode-changed', this._lateZiHourListener);
			}
			window.removeEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
		if(this.prefetchTimer){
			clearTimeout(this.prefetchTimer);
			this.prefetchTimer = null;
		}
	}

	render(){
		let height = this.props.height ? this.props.height : 760;
		if(height === '100%'){
			height = 'calc(100% - 70px)'
		}else{
			height = height - 20
		}

		let chartObj = this.state.chartObj;
		let chart = chartObj ? chartObj.chart : {};
		chart.aspects = chartObj ? chartObj.aspects : {};
		chart.lots = chartObj ? chartObj.lots : [];
		// 赤仪上升取法(经典档只把上升点的 ra 换成东点黄经;黄仪恒原样):三种盘式、右栏同一份盘数据
		const ascRaMode = guolaoAscRaModeOf(chart, this.props.fields);
		chart = withAscRaMode(chart, ascRaMode);
		chartObj = withAscRaModeRoot(chartObj, ascRaMode);
		const useMoiraWheel = this.state.chartStyle === GUOLAO_CHART_STYLE_MOIRA;
		const usePickWheel = this.state.chartStyle === GUOLAO_CHART_STYLE_PICK;
		const useMoiraLikeWheel = useMoiraWheel || usePickWheel;
		const moiraPanelChartObj = withAscRaModeRoot(this.state.moiraPanelChartObj, ascRaMode) || chartObj;
		const moiraPanelTransitChartObj = this.state.moiraPanelTransitChartObj || this.shownMoiraTransitChartObj();
		const moiraPanelTransitParams = this.state.moiraPanelTransitParams || paramsWithMoiraTransit(this.props.fields, this.state.moiraTransitTime);
		const useKinastroQizheng = this.state.engineMode === 'kinastro';

		return (
			<div className={`horosa-guolao-page horosa-astro-redesign horosa-guolao-redesign${useKinastroQizheng ? ' horosa-qizheng-kin-page' : ''}`}>
				<div className="horosa-astro-layout horosa-astro-redesign-layout horosa-guolao-redesign-layout">
					<div className="horosa-astro-redesign-grid horosa-guolao-redesign-grid">
						<div className="horosa-astro-context-panel horosa-astro-input-panel horosa-guolao-input-panel">
							{/* [择日宿主] 左栏插槽(主七政页不传=零渲染) */}
							{typeof this.props.renderLeftExtra === 'function' ? this.props.renderLeftExtra() : null}
							<GuoLaoInput
								fields={this.props.fields}
								onFieldsChange={this.onFieldsChange}
								persistPrefs={(this.props.techniqueScope || 'guolao') === 'guolao'}
								engineMode={this.state.engineMode}
								onEngineModeChange={this.onEngineModeChange}
								kinastroOptions={this.state.kinastroOptions}
								onKinastroOptionChange={this.onKinastroOptionChange}
								chartStyle={this.state.chartStyle}
								onChartStyleChange={this.onChartStyleChange}
								zeriLocked={this.props.zeriLocked}
								moiraTransitTime={this.state.moiraTransitTime}
								onMoiraTransitTimeChange={this.onMoiraTransitTimeChange}
								showMoiraTransitGods={this.state.showMoiraTransitGods}
								onMoiraTransitGodsVisibleChange={this.onMoiraTransitGodsVisibleChange}
								guolaoDisplay={this.state.guolaoDisplay}
								onGuolaoDisplayChange={this.onGuolaoDisplayChange}
								godNamePools={this.collectGodNamePools()}
								electionOptions={this.state.electionOptions}
								onGuolaoElectionChange={(patch)=>this.onGuolaoElectionChange(patch)}
								eleLifeMode={this.state.eleLifeMode}
								onEleLifeModeChange={(val)=>this.onEleLifeModeChange(val)}
								electionDeclination={this.resolveElectionDeclination()}
								electionDeclOutOfRange={this.state.electionDeclOutOfRange}
								onOpenPatternDialog={()=>this.openMoiraQuickDialog('patterns')}
								onAscRaModeChange={(m)=>this.setState({ ascRaMode: m }, ()=>this.saveGuolaoAISnapshot())}
							/>
						</div>
						<div className={`horosa-chart-stage horosa-chart-stage-redesign horosa-guolao-chart-panel xq-chart-renderer xq-chart-renderer-guolao${useMoiraLikeWheel ? ' horosa-guolao-chart-panel-moira' : ''}`}>
							{useKinastroQizheng ? this.renderQizhengKinBoard() : (this.state.bundleLoading && !chartObj) ? this.renderGuolaoChartSkeleton() : usePickWheel ? (
								<GuoLaoMoiraPickWheel
									rootValue={chartObj}
									value={chart}
									transitValue={this.shownMoiraTransitChartObj()}
									transitParams={paramsWithMoiraTransit(this.props.fields, this.state.moiraTransitTime)}
									transitLoading={this.state.moiraTransitLoading}
									moiraRules={this.state.moiraRules}
									aspectSet={this.state.guolaoDisplay.aspects}
									aspectOrbs={this.state.guolaoDisplay.aspectOrbs}
									hiddenPlanets={this.state.guolaoDisplay.hiddenPlanets}
									hiddenGodsBirth={this.state.guolaoDisplay.hiddenGodsBirth}
									hiddenGodsTransit={this.state.guolaoDisplay.hiddenGodsTransit}
									showDignity={this.state.guolaoDisplay.dignity}
									showMountains={this.state.guolaoDisplay.mountains}
									showBirthGods={this.state.guolaoDisplay.birthGods}
									showAgeRing={this.state.guolaoDisplay.ageRing}
									limitChildBase={this.state.guolaoDisplay.limitChildBase}
									onAgeClick={this.onLimitAgeClick}
									limitYearBoundary={this.state.guolaoDisplay.limitYearBoundary}
									election={this.state.electionOptions}
									electionData={this.state.electionData}
									declination={this.resolveElectionDeclination()}
									declinationOutOfRange={this.state.electionDeclOutOfRange}
									height={height}
									fields={this.props.fields}
									chartDisplay={this.props.chartDisplay}
									planetDisplay={this.props.planetDisplay}
									onTipClick={this.onTipClick}
								/>
							) : useMoiraWheel ? (
								<GuoLaoMoiraWheel
									rootValue={chartObj}
									value={chart}
									election={this.state.electionOptions}
									electionData={this.state.electionData}
									transitValue={this.shownMoiraTransitChartObj()}
									transitParams={paramsWithMoiraTransit(this.props.fields, this.state.moiraTransitTime)}
									transitLoading={this.state.moiraTransitLoading}
									showAspectsMode={this.state.guolaoDisplay.showAspects === true}
									showMoiraTransitGods={this.state.showMoiraTransitGods}
									moiraRules={this.state.moiraRules}
									aspectSet={this.state.guolaoDisplay.aspects}
									aspectOrbs={this.state.guolaoDisplay.aspectOrbs}
									hiddenPlanets={this.state.guolaoDisplay.hiddenPlanets}
									hiddenGodsBirth={this.state.guolaoDisplay.hiddenGodsBirth}
									hiddenGodsTransit={this.state.guolaoDisplay.hiddenGodsTransit}
									showDignity={this.state.guolaoDisplay.dignity}
									showMountains={this.state.guolaoDisplay.mountains}
									showBirthGods={this.state.guolaoDisplay.birthGods}
									showAgeRing={this.state.guolaoDisplay.ageRing}
									limitChildBase={this.state.guolaoDisplay.limitChildBase}
									onAgeClick={this.onLimitAgeClick}
									limitYearBoundary={this.state.guolaoDisplay.limitYearBoundary}
									height={height}
									fields={this.props.fields}
									chartDisplay={this.props.chartDisplay}
									planetDisplay={this.props.planetDisplay}
									onTipClick={this.onTipClick}
								/>
							) : (
								<GuoLaoChart
									value={chart}
									height={height}
									fields={this.props.fields}
									chartDisplay={this.props.chartDisplay}
									planetDisplay={this.props.planetDisplay}
									onTipClick={this.onTipClick}
								/>
							)}
						</div>
						<div className="horosa-inspector-panel horosa-astro-content-panel horosa-guolao-info-panel">
							{useKinastroQizheng ? this.renderQizhengKinInfoPanel() : (
									<GuoLaoMoiraPanel
										value={this.state.moiraRules}
										loading={this.state.bundleLoading || this.state.moiraLoading}
										rootValue={moiraPanelChartObj}
										transitValue={moiraPanelTransitChartObj}
										transitParams={moiraPanelTransitParams}
										fields={this.props.fields}
										display={this.state.guolaoDisplay}
										chartMode={usePickWheel ? 'pick' : 'moira'}
										extraTabs={this.buildMoiraExtraTabs()}
									/>
							)}
						</div>
					</div>
					{this.renderQuickDock(useKinastroQizheng)}
				</div>
				{useKinastroQizheng ? null : this.renderMoiraQuickModal()}
			</div>
		);
	}
}
mixinMethods(GuoLaoChartMain, inputMethods, requestMethods, electionMethods, quickPanelMethods, kinPanelMethods);   // 方法按职责拆在 ./main/ 下(见各文件头),挂回原型

export default GuoLaoChartMain;
// 测试专用别名(选项差分网):模块内构参函数原样导出,零行为变化(与 models/astro.js 的 __fieldsToParamsForTest 同范式)。
export { fieldsToParams as __guolaoFieldsToParamsForTest, paramsWithMoiraTransit as __paramsWithMoiraTransitForTest };
