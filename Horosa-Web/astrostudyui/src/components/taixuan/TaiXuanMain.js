import { Component } from 'react';
import { InputNumber, Spin } from 'antd';
import DateTime from '../comp/DateTime';
import SpaceTimePanel, { buildDateTimeFromFields, formatSpaceTime } from '../comp/SpaceTimePanel';
import XQIcon from '../xq-icons';
import { XQButton as Button, XQTabs as Tabs } from '../xq-ui';
import { saveModuleAISnapshot } from '../../utils/moduleAiSnapshot';
import { ServerRoot, ResultKey } from '../../utils/constants';
import { buildKentangEndpoint } from '../../integrations/kentang/serviceRoot';
import { openKentangCaseDrawer, getKentangSavedCasePayload } from '../../utils/kentangCaseSave';
import { formatHumanValue } from '../../utils/humanReadableFields';

const { TabPane } = Tabs;

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

function defaultSeed(){
	return Math.floor((Date.now() + Math.random() * 1000000) % 1000000000);
}

async function postTaiXuan(path, payload){
	let rsp = null;
	try{
		const rawResponse = await fetch(buildKentangEndpoint('taixuan', path), {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json; charset=UTF-8',
			},
			body: JSON.stringify(payload),
		});
		const rawText = await rawResponse.text();
		rsp = rawText ? JSON.parse(rawText) : null;
		if(!rsp || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)){
			throw new Error(rsp && rsp[ResultKey] ? `${rsp[ResultKey]}` : 'taixuan.local.fetch.failed');
		}
	}catch(e){
		const rawResponse = await fetch(`${ServerRoot}/taixuan/${path}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json; charset=UTF-8',
			},
			body: JSON.stringify(payload),
		});
		const rawText = await rawResponse.text();
		rsp = rawText ? JSON.parse(rawText) : null;
	}
	if(!rsp || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)){
		throw new Error(rsp && rsp[ResultKey] ? `${rsp[ResultKey]}` : 'taixuan.fetch.failed');
	}
	return rsp && rsp[ResultKey] ? rsp[ResultKey] : rsp;
}

function fmtValue(value){
	return formatHumanValue(value);
}

function buildSnapshotText(pan){
	if(!pan){
		return '暂无太玄数据';
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

class TaiXuanMain extends Component{
	constructor(props){
		super(props);
		this.state = {
			loading: false,
			pan: null,
			rightPanelTab: 'overview',
			seed: defaultSeed(),
		};
		this.unmounted = false;
		this.timeHook = {};
		this.requestSeq = 0;
		this.onTimeChanged = this.onTimeChanged.bind(this);
		this.getTimeFieldsFromSelector = this.getTimeFieldsFromSelector.bind(this);
		this.clickPlot = this.clickPlot.bind(this);
		this.randomizeSeed = this.randomizeSeed.bind(this);
		this.fetchPan = this.fetchPan.bind(this);
		this.clickSaveCase = this.clickSaveCase.bind(this);
		this.restoreFromCurrentCase = this.restoreFromCurrentCase.bind(this);
		this.setRightPanelTab = this.setRightPanelTab.bind(this);

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
		if(this.skipNextSeedFetch){
			this.skipNextSeedFetch = false;
			return;
		}
		if(prevState.seed !== this.state.seed){
			this.fetchPan(this.props.fields);
		}
	}

	componentWillUnmount(){
		this.unmounted = true;
	}

	restoreFromCurrentCase(force){
		const saved = getKentangSavedCasePayload('taixuan');
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
		this.skipNextSeedFetch = true;
		this.setState({
			loading: false,
			pan: payload.pan || null,
			seed: options.seed !== undefined ? options.seed : this.state.seed,
		}, ()=>{
			saveModuleAISnapshot('taixuan', buildSnapshotText(this.state.pan));
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

	randomizeSeed(){
		this.setState({ seed: defaultSeed() });
	}

	async fetchPan(fields){
		const dt = parseFieldsDateTime(fields);
		if(!dt){
			return;
		}
		const reqSeq = ++this.requestSeq;
		this.setState({ loading: true });
		try{
			const pan = await postTaiXuan('pan', {
				...dt,
				seed: this.state.seed,
			});
			if(this.unmounted || reqSeq !== this.requestSeq){
				return;
			}
			this.setState({ pan, loading: false }, ()=>{
				saveModuleAISnapshot('taixuan', buildSnapshotText(pan));
			});
		}catch(e){
			console.warn('taixuanshifa backend failed', e);
			if(!this.unmounted && reqSeq === this.requestSeq){
				this.setState({ loading: false });
			}
		}
	}

	clickSaveCase(){
		openKentangCaseDrawer({
			dispatch: this.props.dispatch,
			fields: this.props.fields,
			module: 'taixuan',
			label: '太玄',
			payload: {
				options: {
					seed: this.state.seed,
				},
				pan: this.state.pan,
				snapshot: buildSnapshotText(this.state.pan),
			},
		});
	}

	setRightPanelTab(key){
		this.setState({ rightPanelTab: key });
	}

	renderInputPanel(){
		const fields = this.props.fields || {};
		const datetm = buildDateTimeFromFields(fields);
		return (
			<div className="horosa-huangji-input-stack horosa-taixuan-input-stack">
				<div>
					<div className="horosa-side-panel-title">太玄设置</div>
					<div className="horosa-side-panel-subtitle">时间与起筮复现选项</div>
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
					<div className="horosa-huangji-field-title"><XQIcon name="other" />太玄选项</div>
					<div className="horosa-huangji-select-grid">
						<label className="horosa-huangji-select-field is-wide">
							<span>起筮种子</span>
							<InputNumber value={this.state.seed} min={0} max={999999999} onChange={(v)=>this.setState({ seed: v || 0 })} />
						</label>
					</div>
					<div className="horosa-taixuan-note">太玄筮法上游使用随机揲筮。星阙用种子固定本盘，点击“重起”会换一组新筮数。</div>
				</div>
				<div className="horosa-huangji-action-row">
					<Button type="primary" onClick={this.clickPlot}>起盘</Button>
					<Button onClick={this.randomizeSeed}>重起</Button>
				</div>
			</div>
		);
	}

	renderLineDiagram(){
		const tx = this.state.pan && this.state.pan.taixuan ? this.state.pan.taixuan : {};
		const places = tx.fourPlaces || [];
		return (
			<div className="horosa-taixuan-line-stack">
				{places.map((item)=>(
					<div className="horosa-taixuan-line-row" key={item.key}>
						<span>{item.label}</span>
						<strong>{item.symbol || '—'}</strong>
					</div>
				))}
			</div>
		);
	}

	renderCenter(){
		const pan = this.state.pan;
		if(!pan || !pan.taixuan){
			return <div className="horosa-huangji-empty">暂无太玄数据</div>;
		}
		const tx = pan.taixuan || {};
		const gz = pan.ganzhi || {};
		const xh = tx.xuanHead || {};
		const winter = pan.winterSolstice || {};
		const gzItems = [
			{ label: '年柱', value: gz.year },
			{ label: '月柱', value: gz.month },
			{ label: '日柱', value: gz.day },
			{ label: '时柱', value: gz.hour },
		];
		return (
			<div className="horosa-taixuan-board">
				<div className="horosa-huangji-board-header">
					<div>
						<h2 className="horosa-taixuan-title">太玄筮法</h2>
					</div>
					<div className="horosa-huangji-board-time">{`${fmtValue(pan.dateStr)} ${fmtValue(pan.hour)}时`}</div>
				</div>
				<div className="horosa-huangji-meta-grid horosa-taixuan-meta-grid">
					<div><span>首</span><strong>{fmtValue(tx.gua && tx.gua.name)}</strong></div>
					<div><span>起筮时段</span><strong>{fmtValue(tx.period)}</strong></div>
					<div><span>玄首</span><strong>{fmtValue(xh.number)}，{fmtValue(xh.relation)}</strong></div>
					<div><span>星宿</span><strong>{fmtValue(tx.starLodge && tx.starLodge.text)}</strong></div>
					<div><span>方州部家</span><strong>{fmtValue(tx.head)}</strong></div>
					<div><span>休咎</span><strong>{fmtValue(xh.judgment)}</strong></div>
					<div><span>占 / 玄赞</span><strong>{fmtValue(tx.zhanNumber)} / {fmtValue(xh.xuanZan)}</strong></div>
					<div><span>冬至起算</span><strong>{fmtValue(winter.date)}，{fmtValue(winter.days)}日</strong></div>
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
				<div className="horosa-taixuan-main-grid">
					<div className="horosa-taixuan-symbol-card">
						<div className="horosa-taixuan-symbol-head">
							<span>筮得</span>
							<strong>{fmtValue(tx.zhou)}</strong>
						</div>
						{this.renderLineDiagram()}
					</div>
					<div className="horosa-taixuan-text-card">
						<span>首辞</span>
						<strong>{fmtValue(tx.gua && tx.gua.text)}</strong>
						<div className="horosa-taixuan-selected-lines">
							{(tx.selectedLines || []).map((item)=>(
								<div key={item.name}>
									<em>{item.name}</em>
									<p>{fmtValue(item.content)}</p>
								</div>
							))}
						</div>
					</div>
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

	renderAllLines(){
		const lines = this.state.pan && this.state.pan.taixuan ? (this.state.pan.taixuan.allLines || []) : [];
		if(!lines.length){
			return <div className="horosa-huangji-empty">暂无全文</div>;
		}
		return (
			<div className="horosa-taixuan-all-lines">
				{lines.map((item)=>(
					<div className="horosa-huangji-classic-section" key={item.name}>
						<strong>{item.name}</strong>
						<p>{fmtValue(item.content)}</p>
					</div>
				))}
			</div>
		);
	}

	renderClassics(){
		const classics = this.state.pan && this.state.pan.classics ? this.state.pan.classics : null;
		if(!classics || !classics.sections || !classics.sections.length){
			return <div className="horosa-huangji-empty">暂无来源说明</div>;
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
		const activeKey = ['overview', 'head', 'lines', 'fulltext'].indexOf(this.state.rightPanelTab) >= 0 ? this.state.rightPanelTab : 'overview';
		return (
			<Tabs activeKey={activeKey} onChange={this.setRightPanelTab} defaultActiveKey="overview" tabPosition="top" className="horosa-huangji-tabs">
				<TabPane tab="概览" key="overview">
					<div className="horosa-huangji-section-list">
						{this.renderRows(pan ? (pan.sections || []).slice(0, 2) : [])}
					</div>
				</TabPane>
				<TabPane tab="玄首" key="head">
					<div className="horosa-huangji-section-list">
						{this.renderRows(pan ? (pan.sections || []).slice(1, 3) : [])}
					</div>
				</TabPane>
				<TabPane tab="表" key="lines">
					<div className="horosa-huangji-section-list">
						{this.renderRows(pan ? (pan.sections || []).slice(3, 4) : [])}
					</div>
				</TabPane>
				<TabPane tab="全文" key="fulltext">
					<div className="horosa-huangji-section-list">{this.renderAllLines()}</div>
				</TabPane>
			</Tabs>
		);
	}

	renderBottomQuickDock(){
		const actions = [
			{ label: '起筮', icon: 'quickPrimary', onClick: this.randomizeSeed },
			{ label: '概览', icon: 'quickComposite', active: this.state.rightPanelTab === 'overview', onClick: ()=>this.setRightPanelTab('overview') },
			{ label: '玄首', icon: 'quickTransit', active: this.state.rightPanelTab === 'head', onClick: ()=>this.setRightPanelTab('head') },
			{ label: '表', icon: 'quickFirdaria', active: this.state.rightPanelTab === 'lines', onClick: ()=>this.setRightPanelTab('lines') },
			{ label: '全文', icon: 'quickNote', active: this.state.rightPanelTab === 'fulltext', onClick: ()=>this.setRightPanelTab('fulltext') },
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
			<div className={`horosa-huangji-page horosa-astro-redesign horosa-huangji-redesign horosa-taixuan-redesign${embedded ? ' horosa-huangji-embedded' : ''}`} style={pageStyle}>
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
										<div className="horosa-side-panel-title">太玄信息</div>
										<div className="horosa-side-panel-subtitle">玄首、表与全文</div>
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

export default TaiXuanMain;
