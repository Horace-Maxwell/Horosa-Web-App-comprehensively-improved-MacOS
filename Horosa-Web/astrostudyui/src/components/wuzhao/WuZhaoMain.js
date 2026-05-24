import { Component } from 'react';
import { InputNumber, Spin } from 'antd';
import DateTime from '../comp/DateTime';
import SpaceTimePanel, { buildDateTimeFromFields, formatSpaceTime } from '../comp/SpaceTimePanel';
import XQIcon from '../xq-icons';
import { XQButton as Button, XQSelect as Select, XQTabs as Tabs } from '../xq-ui';
import { saveModuleAISnapshot } from '../../utils/moduleAiSnapshot';
import { ServerRoot, ResultKey } from '../../utils/constants';
import { buildKentangEndpoint } from '../../integrations/kentang/serviceRoot';
import { openKentangCaseDrawer, getKentangSavedCasePayload } from '../../utils/kentangCaseSave';
import { formatHumanValue } from '../../utils/humanReadableFields';

const { Option } = Select;
const { TabPane } = Tabs;

const MODE_OPTIONS = [
	{ value: 'ganzhi', label: '干支起盘' },
	{ value: 'day', label: '日干起盘' },
	{ value: 'hour', label: '时干起盘' },
	{ value: 'minute', label: '分干起盘' },
	{ value: 'tang', label: '唐代正法揲筮' },
];

const POSITION_ORDER = ['兆', '木鄉', '火鄉', '土鄉', '金鄉', '水鄉'];
const DEFAULT_SPLITS = [18, 8, 5, 2, 1, 1];

function appendUnique(list, value){
	const text = value ? `${value}`.replace(/\/$/, '') : '';
	if(text && /^https?:\/\/.+/i.test(text) && list.indexOf(text) < 0){
		list.push(text);
	}
}

function parseFieldsDateTime(fields){
	if(!fields || !fields.date || !fields.time || !fields.date.value || !fields.time.value){
		return null;
	}
	const dateStr = fields.date.value.format('YYYY-MM-DD');
	const timeStr = fields.time.value.format('HH:mm:ss');
	const d = dateStr.split('-').map((item)=>parseInt(item, 10));
	const t = timeStr.split(':').map((item)=>parseInt(item, 10));
	if(d.length < 3 || t.length < 2){
		return null;
	}
	return {
		year: d[0],
		month: d[1],
		day: d[2],
		hour: t[0],
		minute: t[1],
		second: t[2] || 0,
		date: dateStr,
		time: timeStr,
		zone: fields.zone && fields.zone.value ? fields.zone.value : '',
	};
}

async function postWuZhao(path, payload){
	const roots = [];
	const endpoints = [];
	if(typeof window !== 'undefined'){
		try{
			const params = new URLSearchParams(window.location.search || '');
			['wuzhaoSrv', 'kinwuzhaoSrv', 'kinastroSrv', 'kentangSrv', 'kinSrv'].forEach((key)=>{
				appendUnique(roots, params.get(key));
			});
		}catch(e){}
	}
	appendUnique(roots, ServerRoot);
	if(/:9999(?:\/)?$/i.test(ServerRoot)){
		appendUnique(roots, ServerRoot.replace(/:9999(?:\/)?$/i, ':8892'));
	}
	appendUnique(roots, 'http://127.0.0.1:8892');
	appendUnique(endpoints, buildKentangEndpoint('wuzhao', path));
	roots.forEach((root)=>appendUnique(endpoints, `${root}/wuzhao/${path}`));
	appendUnique(endpoints, `${ServerRoot}/wuzhao/${path}`);

	let lastError = null;
	for(let i=0; i<endpoints.length; i++){
		try{
			const rawResponse = await fetch(endpoints[i], {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json; charset=UTF-8',
				},
				body: JSON.stringify(payload),
			});
			const rawText = await rawResponse.text();
			const rsp = rawText ? JSON.parse(rawText) : null;
			if(!rsp || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)){
				throw new Error(rsp && rsp[ResultKey] ? `${rsp[ResultKey]}` : 'wuzhao.local.fetch.failed');
			}
			return rsp && rsp[ResultKey] ? rsp[ResultKey] : rsp;
		}catch(e){
			lastError = e;
		}
	}
	try{
		const rawResponse = await fetch(`${ServerRoot}/wuzhao/${path}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json; charset=UTF-8',
			},
			body: JSON.stringify(payload),
		});
		const rawText = await rawResponse.text();
		const rsp = rawText ? JSON.parse(rawText) : null;
		if(!rsp || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)){
			throw new Error(rsp && rsp[ResultKey] ? `${rsp[ResultKey]}` : 'wuzhao.fetch.failed');
		}
		return rsp && rsp[ResultKey] ? rsp[ResultKey] : rsp;
	}catch(e){
		lastError = e || lastError;
	}
	throw lastError || new Error('wuzhao.fetch.failed');
}

function fmtValue(value){
	return formatHumanValue(value);
}

function buildSnapshotText(pan){
	if(!pan){
		return '暂无五兆数据';
	}
	if(pan.snapshot){
		return pan.snapshot;
	}
	const lines = [];
	(pan.sections || []).forEach((section)=>{
		lines.push(`[${section.title}]`);
		(section.rows || []).forEach((row)=>{
			lines.push(`${row.label}：${fmtValue(row.value)}`);
		});
		lines.push('');
	});
	return lines.join('\n').trim();
}

function modeUsesManualSplits(mode){
	return ['day', 'hour', 'minute', 'tang'].indexOf(mode) >= 0;
}

class WuZhaoMain extends Component{
	constructor(props){
		super(props);
		this.state = {
			loading: false,
			pan: null,
			rightPanelTab: 'overview',
			mode: 'ganzhi',
			number: 0,
			manual: false,
			manualSplits: DEFAULT_SPLITS,
		};
		this.unmounted = false;
		this.timeHook = {};
		this.requestSeq = 0;
		this.onTimeChanged = this.onTimeChanged.bind(this);
		this.getTimeFieldsFromSelector = this.getTimeFieldsFromSelector.bind(this);
		this.clickPlot = this.clickPlot.bind(this);
		this.fetchPan = this.fetchPan.bind(this);
		this.clickSaveCase = this.clickSaveCase.bind(this);
		this.restoreFromCurrentCase = this.restoreFromCurrentCase.bind(this);
		this.setRightPanelTab = this.setRightPanelTab.bind(this);
		this.changeMode = this.changeMode.bind(this);
		this.changeManual = this.changeManual.bind(this);
		this.changeSplit = this.changeSplit.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields)=>{
				if(this.unmounted){
					return;
				}
				if(!this.restoreFromCurrentCase()){
					this.fetchPan(fields || this.props.fields);
				}
			};
		}
	}

	componentDidMount(){
		this.unmounted = false;
		if(!this.restoreFromCurrentCase(true)){
			this.fetchPan(this.props.fields);
		}
	}

	componentDidUpdate(prevProps, prevState){
		if(prevProps.fields !== this.props.fields && this.props.fields){
			if(!this.restoreFromCurrentCase()){
				this.fetchPan(this.props.fields);
			}
		}
		if(this.skipNextOptionFetch){
			this.skipNextOptionFetch = false;
			return;
		}
		if(prevState.mode !== this.state.mode
			|| prevState.number !== this.state.number
			|| prevState.manual !== this.state.manual
			|| prevState.manualSplits !== this.state.manualSplits){
			this.fetchPan(this.props.fields);
		}
	}

	componentWillUnmount(){
		this.unmounted = true;
	}

	restoreFromCurrentCase(force){
		const saved = getKentangSavedCasePayload('wuzhao');
		if(!saved || !saved.payload){
			return false;
		}
		if(!force && this.lastRestoredCaseId === saved.caseVersion){
			return false;
		}
		const payload = saved.payload;
		const options = payload.options && typeof payload.options === 'object' ? payload.options : {};
		this.lastRestoredCaseId = saved.caseVersion;
		this.requestSeq += 1;
		this.skipNextOptionFetch = true;
		this.setState({
			loading: false,
			pan: payload.pan || null,
			mode: options.mode || this.state.mode,
			number: options.number !== undefined ? options.number : this.state.number,
			manual: options.manual !== undefined ? !!options.manual : this.state.manual,
			manualSplits: options.manualSplits instanceof Array ? options.manualSplits : this.state.manualSplits,
		}, ()=>{
			saveModuleAISnapshot('wuzhao', buildSnapshotText(this.state.pan));
		});
		return true;
	}

	onFieldsChange(field){
		if(this.props.dispatch){
			const flds = {
				...(this.props.fields || {}),
				...field,
			};
			this.props.dispatch({
				type: 'astro/fetchByFields',
				payload: flds,
			});
		}
	}

	onTimeChanged(value){
		const dt = value.time;
		this.onFieldsChange({
			date: { value: dt.clone() },
			time: { value: dt.clone() },
			ad: { value: dt.ad },
			zone: { value: dt.zone },
		});
	}

	getTimeFieldsFromSelector(baseFields){
		if(!this.timeHook || !this.timeHook.getValue){
			return null;
		}
		const raw = this.timeHook.getValue();
		const dt = raw && raw.value && raw.value instanceof DateTime
			? raw.value
			: (raw && raw.time && raw.time instanceof DateTime ? raw.time : null);
		if(!dt){
			return null;
		}
		const patch = {
			date: { value: dt.clone() },
			time: { value: dt.clone() },
			ad: { value: dt.ad },
			zone: { value: dt.zone },
		};
		return {
			...(baseFields || {}),
			...patch,
		};
	}

	clickPlot(){
		const nextFields = this.getTimeFieldsFromSelector(this.props.fields) || this.props.fields;
		if(!nextFields){
			return;
		}
		if(nextFields.date && nextFields.time && nextFields.zone){
			this.onFieldsChange({
				date: nextFields.date,
				time: nextFields.time,
				ad: nextFields.ad,
				zone: nextFields.zone,
			});
		}
		this.fetchPan(nextFields);
	}

	async fetchPan(fields){
		const dt = parseFieldsDateTime(fields);
		if(!dt){
			return;
		}
		const reqSeq = ++this.requestSeq;
		this.setState({ loading: true });
		try{
			const pan = await postWuZhao('pan', {
				...dt,
				mode: this.state.mode,
				number: this.state.number,
				manual: this.state.manual,
				manualSplits: this.state.manualSplits,
			});
			if(this.unmounted || reqSeq !== this.requestSeq){
				return;
			}
			this.setState({ pan, loading: false }, ()=>{
				saveModuleAISnapshot('wuzhao', buildSnapshotText(pan));
			});
		}catch(e){
			console.warn('kinwuzhao backend failed', e);
			if(!this.unmounted && reqSeq === this.requestSeq){
				this.setState({ loading: false });
			}
		}
	}

	clickSaveCase(){
		openKentangCaseDrawer({
			dispatch: this.props.dispatch,
			fields: this.props.fields,
			module: 'wuzhao',
			label: '五兆',
			payload: {
				options: {
					mode: this.state.mode,
					number: this.state.number,
					manual: this.state.manual,
					manualSplits: this.state.manualSplits,
				},
				pan: this.state.pan,
				snapshot: buildSnapshotText(this.state.pan),
			},
		});
	}

	setRightPanelTab(key){
		this.setState({ rightPanelTab: key });
	}

	changeMode(value){
		const nextMode = value || 'ganzhi';
		this.setState({ mode: nextMode, manual: modeUsesManualSplits(nextMode) ? this.state.manual : false });
	}

	changeManual(value){
		if(!modeUsesManualSplits(this.state.mode)){
			this.setState({ manual: false });
			return;
		}
		this.setState({ manual: value === 'manual' });
	}

	changeSplit(index, value){
		const next = [...this.state.manualSplits];
		next[index] = value || 1;
		this.setState({ manualSplits: next });
	}

	renderInputPanel(){
		const fields = this.props.fields || {};
		const datetm = buildDateTimeFromFields(fields);
		const canUseManualSplits = modeUsesManualSplits(this.state.mode);
		const manualModeValue = canUseManualSplits ? (this.state.manual ? 'manual' : 'auto') : 'computed';
		return (
			<div className="horosa-huangji-input-stack horosa-wuzhao-input-stack">
				<div>
					<div className="horosa-side-panel-title">五兆设置</div>
					<div className="horosa-side-panel-subtitle">时间、起盘法与揲筮选项</div>
				</div>
				<SpaceTimePanel
					fields={fields}
					value={datetm}
					timeText={formatSpaceTime(fields, '---- -- -- --:--:--')}
					onTimeChange={this.onTimeChanged}
					timeHook={this.timeHook}
					showLocation={false}
				/>
				<div className="horosa-huangji-input-section">
					<div className="horosa-huangji-field-title"><XQIcon name="other" />五兆选项</div>
					<div className="horosa-huangji-select-grid">
						<label className="horosa-huangji-select-field is-wide">
							<span>起盘方式</span>
							<Select value={this.state.mode} onChange={this.changeMode}>
								{MODE_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-huangji-select-field">
							<span>报数</span>
							<InputNumber value={this.state.number} min={0} max={90} onChange={(v)=>this.setState({ number: v || 0 })} />
						</label>
						<label className="horosa-huangji-select-field is-wide">
							<span>揲筮模式</span>
							<Select value={manualModeValue} disabled={!canUseManualSplits} onChange={this.changeManual}>
								{!canUseManualSplits ? <Option value="computed">干支计算</Option> : null}
								<Option value="auto">自动随机</Option>
								<Option value="manual">手动复现</Option>
							</Select>
						</label>
					</div>
				</div>
				<div className="horosa-huangji-input-section">
					<div className="horosa-huangji-field-title"><XQIcon name="quickComposite" />手动六数</div>
					<div className="horosa-wuzhao-split-grid">
						{POSITION_ORDER.map((item, idx)=>(
							<label className="horosa-huangji-select-field" key={item}>
								<span>{item.replace('鄉', '乡')}</span>
								<InputNumber
									value={this.state.manualSplits[idx]}
									min={1}
									max={35}
									disabled={!canUseManualSplits || !this.state.manual}
									onChange={(v)=>this.changeSplit(idx, v)}
								/>
							</label>
						))}
					</div>
					<div className="horosa-wuzhao-split-note">
						{canUseManualSplits ? '手动复现只在选择“手动复现”后参与日干、时干、分干与唐代正法计算。' : '干支起盘使用年月日时分干支与报数计算，不调用手动六数。'}
					</div>
				</div>
				<div className="horosa-huangji-action-row">
					<Button type="primary" onClick={this.clickPlot}>起盘</Button>
				</div>
			</div>
		);
	}

	renderPositionCard(item){
		const flags = item.flags || [];
		return (
			<div className="horosa-wuzhao-position-card" key={item.key}>
				<div className="horosa-wuzhao-position-head">
					<strong>{item.label}</strong>
					<span>{item.palace || '—'}宫</span>
				</div>
				<div className="horosa-wuzhao-number">{fmtValue(item.number)}</div>
				<div className="horosa-wuzhao-position-main">
					<span>{fmtValue(item.element)}</span>
					<span>{fmtValue(item.relation)}</span>
					<span>{fmtValue(item.beast)}</span>
				</div>
				<div className="horosa-wuzhao-position-foot">
					<span>{item.prosperity ? `旺相 ${item.prosperity}` : '旺相 —'}</span>
					<em>{flags.length ? flags.join(' · ') : '无特殊标记'}</em>
				</div>
			</div>
		);
	}

	renderCenter(){
		const pan = this.state.pan;
		if(!pan){
			return <div className="horosa-huangji-empty">暂无五兆数据</div>;
		}
		const gz = pan.ganzhi || {};
		const gzItems = [
			{ label: '年柱', value: gz.year },
			{ label: '月柱', value: gz.month },
			{ label: '日柱', value: gz.day },
			{ label: '时柱', value: gz.hour },
			{ label: '分柱', value: gz.minute },
		];
		const positions = pan.positions || [];
		return (
			<div className="horosa-wuzhao-board">
				<div className="horosa-huangji-board-header">
					<div>
						<h2 className="horosa-wuzhao-title">五兆</h2>
					</div>
					<div className="horosa-huangji-board-time">{`${fmtValue(pan.dateStr)} ${fmtValue(pan.timeStr)}`}</div>
				</div>
				<div className="horosa-huangji-meta-grid horosa-wuzhao-meta-grid">
					<div><span>起盘方式</span><strong>{pan.modeLabel || '—'}</strong></div>
					<div><span>节气</span><strong>{pan.solarTerm || '—'}</strong></div>
					<div><span>农历</span><strong>{pan.lunarDate && pan.lunarDate.text ? pan.lunarDate.text : '—'}</strong></div>
					<div><span>上/下柱</span><strong>{fmtValue(pan.upperGanzhi)} / {fmtValue(pan.lowerGanzhi)}</strong></div>
					<div className="horosa-huangji-ganzhi-card">
						<span>干支</span>
						<div className="horosa-huangji-ganzhi-grid">
							{gzItems.map((item)=>(
								<div className="horosa-huangji-ganzhi-item" key={item.label}>
									<em>{item.label}</em>
									<strong>{fmtValue(item.value)}</strong>
								</div>
							))}
						</div>
					</div>
				</div>
				<div className="horosa-wuzhao-board-grid">
					{positions.map((item)=>this.renderPositionCard(item))}
				</div>
			</div>
		);
	}

	renderRows(sections){
		const list = sections || [];
		if(!list.length){
			return <div className="horosa-huangji-empty">暂无数据</div>;
		}
		return list.map((section)=>(
			<div className="horosa-huangji-info-card" key={section.title}>
				<div className="horosa-huangji-info-heading">{section.title}</div>
				{(section.rows || []).map((row, idx)=>(
					<div className="horosa-huangji-info-row" key={`${section.title}_${row.label}_${idx}`}>
						<span>{row.label}</span>
						<strong>{fmtValue(row.value)}</strong>
					</div>
				))}
			</div>
		));
	}

	renderClassics(){
		const classics = this.state.pan && this.state.pan.classics ? this.state.pan.classics : null;
		if(!classics || !classics.sections || !classics.sections.length){
			return <div className="horosa-huangji-empty">暂无五兆古籍目录</div>;
		}
		return (
			<div className="horosa-huangji-classics">
				{(classics.meta || []).map((item)=>(
					<div className="horosa-huangji-info-card" key={item.key}>
						<div className="horosa-huangji-info-heading">{item.title}</div>
						<div className="horosa-huangji-info-row"><span>作者</span><strong>{item.author}</strong></div>
						<div className="horosa-huangji-info-row"><span>说明</span><strong>{item.description}</strong></div>
					</div>
				))}
				<div className="horosa-huangji-classic-list">
					{classics.sections.map((section)=>(
						<div className="horosa-huangji-classic-section" key={section.title}>
							<strong>{section.title}</strong>
							<p>{section.content}</p>
						</div>
					))}
				</div>
			</div>
		);
	}

	renderRightPanel(){
		const pan = this.state.pan;
		const flagRows = [];
		(pan && pan.positions ? pan.positions : []).forEach((item)=>{
			if(item.flags && item.flags.length){
				flagRows.push({ label: item.label, value: item.flags.join('、') });
			}
		});
		const activeKey = ['overview', 'positions', 'flags'].indexOf(this.state.rightPanelTab) >= 0 ? this.state.rightPanelTab : 'overview';
		return (
			<Tabs activeKey={activeKey} onChange={this.setRightPanelTab} defaultActiveKey="overview" tabPosition="top" className="horosa-huangji-tabs">
				<TabPane tab="概览" key="overview">
					<div className="horosa-huangji-section-list">
						{this.renderRows(pan ? (pan.sections || []).slice(0, 2) : [])}
					</div>
				</TabPane>
				<TabPane tab="六位" key="positions">
					<div className="horosa-huangji-section-list">
						{this.renderRows(pan ? (pan.sections || []).slice(2, 8) : [])}
					</div>
				</TabPane>
				<TabPane tab="标记" key="flags">
					<div className="horosa-huangji-section-list">
						{this.renderRows([{ title: '孤虚关籥将军', rows: flagRows.length ? flagRows : [{ label: '标记', value: '无' }] }])}
					</div>
				</TabPane>
			</Tabs>
		);
	}

	renderBottomQuickDock(){
		const actions = [
			{ label: '起盘', icon: 'quickPrimary', onClick: this.clickPlot },
			{ label: '概览', icon: 'quickComposite', active: this.state.rightPanelTab === 'overview', onClick: ()=>this.setRightPanelTab('overview') },
			{ label: '六位', icon: 'quickTransit', active: this.state.rightPanelTab === 'positions', onClick: ()=>this.setRightPanelTab('positions') },
			{ label: '标记', icon: 'quickFirdaria', active: this.state.rightPanelTab === 'flags', onClick: ()=>this.setRightPanelTab('flags') },
			{ label: '保存', icon: 'quickReturn', onClick: this.clickSaveCase },
		];
		return (
			<div className="horosa-bottom-quick-dock horosa-huangji-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-huangji-quick-actions">
					{actions.map((item)=>(
						<button
							type="button"
							key={item.label}
							className={`horosa-bottom-quick-button horosa-huangji-quick-button${item.active ? ' is-active' : ''}`}
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
		const embedded = !!this.props.hideQuickDock;
		let height = this.props.height ? this.props.height : 760;
		let pageStyle = { height, minHeight: height, overflow: 'hidden' };
		if(embedded){
			pageStyle = { height: '100%', minHeight: 0, overflow: 'hidden' };
		}else if(height === '100%'){
			height = 760;
			pageStyle = { height, minHeight: height, overflow: 'hidden' };
		}else{
			height = height - 20;
			pageStyle = { height, minHeight: height, overflow: 'hidden' };
		}
		return (
			<div className={`horosa-huangji-page horosa-astro-redesign horosa-huangji-redesign horosa-wuzhao-redesign${embedded ? ' horosa-huangji-embedded' : ''}`} style={pageStyle}>
				<div className="horosa-astro-layout horosa-astro-redesign-layout horosa-huangji-redesign-layout">
					<Spin spinning={this.state.loading}>
						<div className="horosa-astro-redesign-grid horosa-huangji-redesign-grid">
							<div className="horosa-astro-context-panel horosa-astro-input-panel horosa-huangji-input-panel">
								{this.renderInputPanel()}
							</div>
							<div className="horosa-chart-stage horosa-chart-stage-redesign horosa-huangji-chart-panel xq-chart-renderer">
								<div className="horosa-huangji-board-host">{this.renderCenter()}</div>
							</div>
							<div className="horosa-inspector-panel horosa-astro-content-panel horosa-huangji-info-panel">
								<div className="horosa-side-panel-heading horosa-huangji-info-heading-main">
									<div>
										<div className="horosa-side-panel-title">五兆信息</div>
										<div className="horosa-side-panel-subtitle">六位与标记</div>
									</div>
								</div>
								{this.renderRightPanel()}
							</div>
						</div>
					</Spin>
					{!this.props.hideQuickDock && this.renderBottomQuickDock()}
				</div>
			</div>
		);
	}
}

export default WuZhaoMain;
