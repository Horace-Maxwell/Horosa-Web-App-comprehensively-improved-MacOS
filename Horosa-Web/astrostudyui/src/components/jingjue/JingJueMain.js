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

async function postJingJue(path, payload){
	let rsp = null;
	try{
		const rawResponse = await fetch(buildKentangEndpoint('jingjue', path), {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json; charset=UTF-8',
			},
			body: JSON.stringify(payload),
		});
		const rawText = await rawResponse.text();
		rsp = rawText ? JSON.parse(rawText) : null;
		if(!rsp || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)){
			throw new Error(rsp && rsp[ResultKey] ? `${rsp[ResultKey]}` : 'jingjue.local.fetch.failed');
		}
	}catch(e){
		const rawResponse = await fetch(`${ServerRoot}/jingjue/${path}`, {
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
		throw new Error(rsp && rsp[ResultKey] ? `${rsp[ResultKey]}` : 'jingjue.fetch.failed');
	}
	return rsp && rsp[ResultKey] ? rsp[ResultKey] : rsp;
}

function fmtValue(value){
	return formatHumanValue(value);
}

function buildSnapshotText(pan){
	if(!pan){
		return '暂无荆诀数据';
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

class JingJueMain extends Component{
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
		const saved = getKentangSavedCasePayload('jingjue');
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
			saveModuleAISnapshot('jingjue', buildSnapshotText(this.state.pan));
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
			const pan = await postJingJue('pan', {
				...dt,
				seed: this.state.seed,
			});
			if(this.unmounted || reqSeq !== this.requestSeq){
				return;
			}
			this.setState({ pan, loading: false }, ()=>{
				saveModuleAISnapshot('jingjue', buildSnapshotText(pan));
			});
		}catch(e){
			console.warn('jingjue backend failed', e);
			if(!this.unmounted && reqSeq === this.requestSeq){
				this.setState({ loading: false });
			}
		}
	}

	clickSaveCase(){
		openKentangCaseDrawer({
			dispatch: this.props.dispatch,
			fields: this.props.fields,
			module: 'jingjue',
			label: '荆诀',
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
			<div className="horosa-huangji-input-stack horosa-jingjue-input-stack">
				<div>
					<div className="horosa-side-panel-title">荆诀设置</div>
					<div className="horosa-side-panel-subtitle">时间与起课复现选项</div>
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
					<div className="horosa-huangji-field-title"><XQIcon name="quickNote" />荆诀选项</div>
					<div className="horosa-huangji-select-grid">
						<label className="horosa-huangji-select-field is-wide">
							<span>起筮种子</span>
							<InputNumber value={this.state.seed} min={0} max={999999999} onChange={(v)=>this.setState({ seed: v || 0 })} />
						</label>
					</div>
					<div className="horosa-taixuan-note">上游荆诀使用随机三十算起课。星阙用种子固定本课，点击“重起”会换一组新三分。</div>
				</div>
				<div className="horosa-huangji-action-row">
					<Button type="primary" onClick={this.clickPlot}>起课</Button>
					<Button onClick={this.randomizeSeed}>重起</Button>
				</div>
			</div>
		);
	}

	renderGroups(){
		const jj = this.state.pan && this.state.pan.jingjue ? this.state.pan.jingjue : {};
		const groups = jj.groups || [];
		return (
			<div className="horosa-jingjue-group-stack">
				{groups.map((item)=>(
					<div className="horosa-jingjue-group-row" key={item.key}>
						<span>{item.key}</span>
						<strong>{fmtValue(item.count)} 算</strong>
						<em>余 {fmtValue(item.remainder)}</em>
					</div>
				))}
			</div>
		);
	}

	renderCenter(){
		const pan = this.state.pan;
		if(!pan || !pan.jingjue){
			return <div className="horosa-huangji-empty">暂无荆诀数据</div>;
		}
		const jj = pan.jingjue || {};
		const gua = jj.gua || {};
		return (
			<div className="horosa-taixuan-board horosa-jingjue-board">
				<div className="horosa-huangji-board-header">
					<div>
						<h2 className="horosa-taixuan-title">荆诀</h2>
					</div>
					<div className="horosa-huangji-board-time">{fmtValue(pan.dateStr)} {fmtValue(pan.timeStr)}</div>
				</div>
				<div className="horosa-huangji-meta-grid horosa-taixuan-meta-grid horosa-jingjue-meta-grid">
					<div><span>干卦</span><strong>{fmtValue(gua.name)}</strong></div>
					<div><span>吉凶</span><strong>{fmtValue(gua.verdict)}</strong></div>
					<div><span>卦键</span><strong>{fmtValue(jj.key)}</strong></div>
					<div><span>三分余数</span><strong>{fmtValue(jj.remainders)}</strong></div>
					<div><span>关键词</span><strong>{fmtValue(gua.keyword)}</strong></div>
					<div><span>祟提示</span><strong>{fmtValue(gua.spirit)}</strong></div>
					<div><span>起筮种子</span><strong>{fmtValue(pan.seed)}</strong></div>
				</div>
				<div className="horosa-taixuan-main-grid horosa-jingjue-main-grid">
					<div className="horosa-taixuan-symbol-card horosa-jingjue-symbol-card">
						<div className="horosa-taixuan-symbol-head">
							<span>三十算</span>
							<strong>{fmtValue(jj.key)}</strong>
						</div>
						{this.renderGroups()}
					</div>
					<div className="horosa-taixuan-text-card horosa-jingjue-text-card">
						<span>卦义</span>
						<strong>{fmtValue(gua.text)}</strong>
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

	renderAllGua(){
		const items = this.state.pan && this.state.pan.jingjue ? (this.state.pan.jingjue.allGua || []) : [];
		if(!items.length){
			return <div className="horosa-huangji-empty">暂无十六卦</div>;
		}
		return (
			<div className="horosa-jingjue-gua-list">
				{items.map((item)=>(
					<div className="horosa-huangji-classic-section horosa-jingjue-gua-card" key={item.key}>
						<strong>{item.name} · {item.key} · {item.verdict}</strong>
						<em>{fmtValue(item.keyword)}</em>
						<p>{fmtValue(item.text)}</p>
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
		const activeKey = ['overview', 'cast', 'gua'].indexOf(this.state.rightPanelTab) >= 0 ? this.state.rightPanelTab : 'overview';
		return (
			<Tabs activeKey={activeKey} onChange={this.setRightPanelTab} defaultActiveKey="overview" tabPosition="top" className="horosa-huangji-tabs">
				<TabPane tab="概览" key="overview">
					<div className="horosa-huangji-section-list">
						{this.renderRows(pan ? (pan.sections || []).slice(0, 2) : [])}
					</div>
				</TabPane>
				<TabPane tab="起课" key="cast">
					<div className="horosa-huangji-section-list">
						{this.renderRows(pan ? (pan.sections || []).slice(0, 3) : [])}
					</div>
				</TabPane>
				<TabPane tab="十六卦" key="gua">
					<div className="horosa-huangji-section-list">{this.renderAllGua()}</div>
				</TabPane>
			</Tabs>
		);
	}

	renderBottomQuickDock(){
		const actions = [
			{ label: '重起', icon: 'quickPrimary', onClick: this.randomizeSeed },
			{ label: '概览', icon: 'quickComposite', active: this.state.rightPanelTab === 'overview', onClick: ()=>this.setRightPanelTab('overview') },
			{ label: '起课', icon: 'quickTransit', active: this.state.rightPanelTab === 'cast', onClick: ()=>this.setRightPanelTab('cast') },
			{ label: '十六卦', icon: 'quickFirdaria', active: this.state.rightPanelTab === 'gua', onClick: ()=>this.setRightPanelTab('gua') },
			{ label: '保存', icon: 'quickReturn', onClick: this.clickSaveCase },
		];
		return (
			<div className="horosa-bottom-quick-dock horosa-huangji-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-huangji-quick-actions">
					{actions.map((item)=>(
						<button
							type="button"
							key={`${item.label}_${item.icon}`}
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
			<div className={`horosa-huangji-page horosa-astro-redesign horosa-huangji-redesign horosa-taixuan-redesign horosa-jingjue-redesign${embedded ? ' horosa-huangji-embedded' : ''}`} style={pageStyle}>
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
										<div className="horosa-side-panel-title">荆诀信息</div>
										<div className="horosa-side-panel-subtitle">起课与十六卦</div>
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

export default JingJueMain;
