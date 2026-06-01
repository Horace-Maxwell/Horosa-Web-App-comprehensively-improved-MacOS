import { Component, createRef } from 'react';
import { Row, Col, Slider, InputNumber, Empty } from 'antd';
import { XQButton, XQToggle, XQSegmented, XQSelect, XQTabs } from '../xq-ui';
import FengShuiEngine, { MARKER_TYPES } from './fengshuiEngine';
import { saveModuleAISnapshot } from '../../utils/moduleAiSnapshot';

const { TabPane } = XQTabs;
const { Option } = XQSelect;

const FILTERS = [
	{ key: 'all', label: '全部' },
	{ key: 'ok', label: '位置合适' },
	{ key: 'wind-bad', label: '气位冲突' },
	{ key: 'water-bad', label: '水位冲突' },
	{ key: 'unknown', label: '未定位' },
];

const TIPS = [
	'楼门朝向以卫星地图为准，门内朝门外，记录真北角度。',
	'家门方向在户型图上画出，令两箭头平行后再判定。',
	'房屋主体以矩形为准，扩大范围导致空缺大于实体时不再扩大。',
	'盘心放在太极点，八方颜色与数字即可判断气位与水位。',
];

const CENTER_OPTIONS = [
	{ value: 'house', label: '房屋中心' },
	{ value: 'door', label: '入户门' },
	{ value: 'custom', label: '自定义点' },
	{ value: 'marker', label: '选中标记' },
];

const PERIOD_OPTIONS = [
	{ value: 'current', label: '1964-2044' },
	{ value: 'reversed', label: '2044-2124' },
];

class FengShuiMain extends Component {
	constructor(props) {
		super(props);
		this.state = {
			vm: null,
			controlTab: 'base',
			workspaceTab: 'canvas',
		};
		this.canvasRef = createRef();
		this.fileInputRef = createRef();
		this.engine = null;
		this.resizeObserver = null;
		this.handleSnapshotRefreshRequest = this.handleSnapshotRefreshRequest.bind(this);
		this.handleKeyDown = this.handleKeyDown.bind(this);
		this.onVm = this.onVm.bind(this);
	}

	componentDidMount() {
		const canvas = this.canvasRef.current;
		if (!canvas) return;
		this.engine = new FengShuiEngine(canvas, { onChange: this.onVm });
		const host = canvas.parentElement;
		if (host && 'ResizeObserver' in window) {
			this.resizeObserver = new ResizeObserver(() => this.engine && this.engine.resize());
			this.resizeObserver.observe(host);
		}
		setTimeout(() => this.engine && this.engine.resize(), 0);
		window.addEventListener('keydown', this.handleKeyDown);
		window.addEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
	}

	componentDidUpdate(prevProps, prevState) {
		if (prevState.workspaceTab !== 'canvas' && this.state.workspaceTab === 'canvas') {
			setTimeout(() => this.engine && this.engine.resize(), 0);
		}
	}

	componentWillUnmount() {
		if (this.resizeObserver) this.resizeObserver.disconnect();
		window.removeEventListener('keydown', this.handleKeyDown);
		window.removeEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		if (this.engine) this.engine.destroy();
	}

	onVm(vm) {
		this.setState({ vm });
		if (vm && vm.snapshotText) {
			saveModuleAISnapshot('fengshui', vm.snapshotText, { source: 'react', savedAt: Date.now() });
		}
	}

	handleKeyDown(e) {
		if (this.engine) this.engine.handleKey(e);
	}

	handleSnapshotRefreshRequest(evt) {
		if (!evt || !evt.detail || evt.detail.module !== 'fengshui') return;
		if (!this.engine) return;
		const text = this.engine.buildAiSnapshotText();
		if (text) {
			saveModuleAISnapshot('fengshui', text, { source: 'react', savedAt: Date.now() });
			if (typeof evt.detail === 'object') evt.detail.snapshotText = text;
		}
	}

	onFile(e) {
		const file = e.target.files && e.target.files[0];
		if (file && this.engine) this.engine.loadImageFile(file);
		e.target.value = '';
	}

	renderQuickbar(vm) {
		const e = this.engine;
		const dis = !vm.imgLoaded;
		return (
			<div className="horosa-fengshui-quickbar">
				<XQButton type="primary" size="small" onClick={() => this.fileInputRef.current && this.fileInputRef.current.click()}>上传户型图</XQButton>
				<XQButton size="small" disabled={dis} onClick={() => e.startDrawRect()}>框选房屋</XQButton>
				<XQButton size="small" disabled={dis} onClick={() => e.startDrawDoor()}>画入户门</XQButton>
				<XQButton size="small" disabled={dis} onClick={() => e.startPlaceMarker()}>放置标记</XQButton>
				<XQButton size="small" variant="ghost" disabled={!vm.canUndo} onClick={() => e.undo()}>撤销</XQButton>
				<XQButton size="small" variant="ghost" disabled={!vm.canRedo} onClick={() => e.redo()}>重做</XQButton>
				<XQButton size="small" variant="ghost" disabled={dis} onClick={() => e.exportPng()}>导出 PNG</XQButton>
				<span className="horosa-fengshui-status">{vm.status}</span>
			</div>
		);
	}

	renderBasePanel(vm) {
		const e = this.engine;
		const dis = !vm.imgLoaded;
		return (
			<div className="horosa-fengshui-card">
				<div className="horosa-fengshui-card-title">图片与房屋</div>
				<div className="horosa-fengshui-btn-row">
					<XQButton onClick={() => this.fileInputRef.current && this.fileInputRef.current.click()}>上传户型图</XQButton>
					<XQButton variant="ghost" disabled={dis} onClick={() => e.startDrawRect()}>手动框选房屋</XQButton>
					<XQButton variant="ghost" disabled={dis} onClick={() => e.resetRect()}>重置房屋框</XQButton>
				</div>
				<div className="horosa-fengshui-field">
					<label>矩形旋转角度</label>
					<div className="horosa-fengshui-dual">
						<Slider min={-45} max={45} step={0.5} value={vm.rectRotation} onChange={(v) => e.setRectRotation(v)} disabled={dis} style={{ flex: 1 }} />
						<InputNumber size="small" step={0.5} value={vm.rectRotation} onChange={(v) => e.setRectRotation(v)} disabled={dis} />
					</div>
				</div>
				<div className="horosa-fengshui-card-title" style={{ marginTop: 12 }}>角度与门向</div>
				<div className="horosa-fengshui-field">
					<label>单元门真北角度 (0-360°)</label>
					<InputNumber size="small" style={{ width: '100%' }} placeholder="例如 58.5" step={0.1} value={vm.unitAzimuth} onChange={(v) => e.setUnitAngle(v)} />
				</div>
				<div className="horosa-fengshui-field">
					<label>入户门方向 (0-360°)</label>
					<InputNumber size="small" style={{ width: '100%' }} step={1} value={vm.doorImageAngle} onChange={(v) => e.setDoorAngle(v)} />
					<XQButton variant="ghost" style={{ marginTop: 6 }} disabled={dis} onClick={() => e.startDrawDoor()}>在图上画入户门方向</XQButton>
				</div>
				<div className="horosa-fengshui-stats">
					<span>单元门 <strong>{vm.unitAngleText}</strong></span>
					<span>入户门 <strong>{vm.doorAngleText}</strong></span>
					<span>盘旋转 <strong>{vm.diskRotationText}</strong></span>
				</div>
			</div>
		);
	}

	renderDiskPanel(vm) {
		const e = this.engine;
		return (
			<div className="horosa-fengshui-card">
				<div className="horosa-fengshui-card-title">纳气盘</div>
				<div className="horosa-fengshui-field">
					<label>透明度 <span className="horosa-fengshui-inline-val">{Math.round(vm.globalAlpha * 100)}%</span></label>
					<Slider min={0.2} max={0.95} step={0.05} value={vm.globalAlpha} onChange={(v) => e.setOpacity(v)} />
				</div>
				<div className="horosa-fengshui-field">
					<label>盘大小 <span className="horosa-fengshui-inline-val">{Math.round(vm.diskScale * 100)}%</span></label>
					<Slider min={1} max={1.6} step={0.05} value={vm.diskScale} onChange={(v) => e.setDiskScale(v)} />
				</div>
				<div className="horosa-fengshui-field">
					<label>盘中心位置</label>
					<XQSegmented value={vm.diskCenterMode} options={CENTER_OPTIONS} onChange={(ev) => e.setDiskCenterMode(ev.target.value)} />
					<div className="horosa-fengshui-helper">自定义点：选「自定义」后按住 Shift 在画布点击设定。</div>
				</div>
				<div className="horosa-fengshui-field">
					<label>运期模式</label>
					<XQSegmented value={vm.periodMode} options={PERIOD_OPTIONS} onChange={(ev) => e.setPeriodMode(ev.target.value)} />
					<div className="horosa-fengshui-helper">2044 后风水位置反转：气位与水位互换。</div>
				</div>
			</div>
		);
	}

	renderMarkerPanel(vm) {
		const e = this.engine;
		const dis = !vm.imgLoaded;
		return (
			<div className="horosa-fengshui-card">
				<div className="horosa-fengshui-card-title">家具与设施标注</div>
				<div className="horosa-fengshui-field">
					<label>选择标记类型</label>
					<XQSelect size="small" style={{ width: '100%' }} value={vm.markerType} onChange={(v) => e.setMarkerType(v)}>
						{MARKER_TYPES.map((t) => {
							const tag = t.category === 'wind' ? '气' : t.category === 'water' ? '水' : '观';
							return <Option key={t.id} value={t.id}>{`${t.label}（${tag}）`}</Option>;
						})}
					</XQSelect>
				</div>
				<div className="horosa-fengshui-btn-row">
					<XQButton disabled={dis} onClick={() => e.startPlaceMarker()}>放置标记</XQButton>
					<XQButton variant="ghost" disabled={dis} onClick={() => e.clearMarkers()}>清空标记</XQButton>
				</div>
				<div className="horosa-fengshui-helper">点击画布放置，拖动可调整位置。</div>
			</div>
		);
	}

	renderExportPanel(vm) {
		const e = this.engine;
		const dis = !vm.imgLoaded;
		return (
			<div className="horosa-fengshui-card">
				<div className="horosa-fengshui-card-title">导出</div>
				<XQButton disabled={dis} onClick={() => e.exportPng()}>导出当前视图 PNG</XQButton>
				<div className="horosa-fengshui-btn-row" style={{ marginTop: 10 }}>
					<XQButton variant="ghost" disabled={dis} onClick={() => e.exportReportPng()}>导出判定报告 PNG</XQButton>
					<XQButton variant="ghost" disabled={dis} onClick={() => e.exportReportPdf()}>导出判定报告 PDF</XQButton>
				</div>
				<div className="horosa-fengshui-helper">导出会包含底图、房屋框、纳气盘与标记。</div>
			</div>
		);
	}

	renderJudgePanel(vm) {
		const e = this.engine;
		const filtered = (vm.markers || []).filter((m) => {
			if (vm.currentFilter === 'all') return true;
			if (vm.currentFilter === 'unknown') return !m.sector;
			if (vm.currentFilter === 'ok') return m.ok;
			if (vm.currentFilter === 'wind-bad') return m.category === 'wind' && m.sector && !m.ok;
			if (vm.currentFilter === 'water-bad') return m.category === 'water' && m.sector && !m.ok;
			return true;
		});
		return (
			<div className="horosa-fengshui-judge">
				<div className="horosa-fengshui-card-title">标记判定</div>
				<div className="horosa-fengshui-filterbar">
					{FILTERS.map((f) => (
						<XQToggle key={f.key} size="small" active={vm.currentFilter === f.key} onClick={() => e.setFilter(f.key)}>{f.label}</XQToggle>
					))}
				</div>
				<div className="horosa-fengshui-marker-list">
					{(vm.markers || []).length === 0 ? (
						<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无标记，请先放置。" />
					) : filtered.length === 0 ? (
						<div className="horosa-fengshui-helper">当前筛选无结果</div>
					) : filtered.map((m) => (
						<div
							key={m.id}
							className={`horosa-fengshui-marker-row${m.id === vm.selectedMarkerId ? ' active' : ''}`}
							onClick={() => e.selectMarker(m.id)}
						>
							<div className="horosa-fengshui-marker-chip">
								<span className="horosa-fengshui-chip-dot" style={{ background: m.color }} />
								<span>{m.label}</span>
							</div>
							<div className="horosa-fengshui-marker-meta">
								{m.sector ? `${m.sector.num} · ${m.sector.name} · ${m.actual === 'wind' ? '气位' : '水位'}` : '未定位'}
							</div>
							<div className={`horosa-fengshui-marker-status ${m.ok ? 'ok' : 'warn'}`}>
								{m.category === 'neutral' ? '观察' : m.ok ? '位置合适' : '位置冲突'}
							</div>
							<XQButton size="small" variant="ghost" danger onClick={(ev) => { ev.stopPropagation(); e.deleteMarker(m.id); }}>删除</XQButton>
						</div>
					))}
				</div>
				{vm.summary ? <div className="horosa-fengshui-summary">{vm.summary}</div> : null}
				<div className="horosa-fengshui-helper">气位建议放置：门、窗、灶台、沙发、床、书桌、神龛、宠物床等。水位建议放置：水槽、洗手池、马桶、下水管、洗衣机、厕所等。</div>
			</div>
		);
	}

	render() {
		const vm = this.state.vm || {
			status: '请上传户型图开始。', imgLoaded: false, rectRotation: 0,
			unitAzimuth: null, doorImageAngle: null, unitAngleText: '--', doorAngleText: '--', diskRotationText: '--',
			globalAlpha: 0.3, diskScale: 1, diskCenterMode: 'house', periodMode: 'current',
			snapEnabled: true, panMode: false, zoomPct: 100, markerType: MARKER_TYPES[0].id,
			currentFilter: 'all', selectedMarkerId: null, markers: [], summary: '', canUndo: false, canRedo: false,
		};
		const e = this.engine;
		let height = this.props.height ? this.props.height : '100%';
		if (typeof height === 'number') height = `${height}px`;
		return (
			<div className="horosa-fengshui-app" style={{ height }}>
				<input ref={this.fileInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={(ev) => this.onFile(ev)} />
				{this.renderQuickbar(vm)}
				<Row gutter={8} className="horosa-fengshui-layout">
					<Col span={6} className="horosa-fengshui-side">
						<XQTabs size="small" activeKey={this.state.controlTab} onChange={(k) => this.setState({ controlTab: k })}>
							<TabPane tab="基础" key="base">{this.renderBasePanel(vm)}</TabPane>
							<TabPane tab="纳气盘" key="disk">{this.renderDiskPanel(vm)}</TabPane>
							<TabPane tab="标注" key="markers">{this.renderMarkerPanel(vm)}</TabPane>
							<TabPane tab="导出" key="export">{this.renderExportPanel(vm)}</TabPane>
						</XQTabs>
					</Col>
					<Col span={18} className="horosa-fengshui-workspace">
						<XQTabs size="small" className="horosa-fengshui-workspace-tabs" activeKey={this.state.workspaceTab} onChange={(k) => this.setState({ workspaceTab: k })}>
							<TabPane tab="画布" key="canvas">
								<div className="horosa-fengshui-canvas-wrap">
									<div className="horosa-fengshui-canvas-toolbar">
										<div className="horosa-fengshui-legend">
											<span><i className="dot wind" />气位（红）</span>
											<span><i className="dot water" />水位（蓝）</span>
										</div>
										<div className="horosa-fengshui-canvas-actions">
											<XQToggle size="small" active={vm.panMode} disabled={!vm.imgLoaded} onClick={() => e.togglePan()}>拖拽</XQToggle>
											<XQToggle size="small" active={vm.snapEnabled} disabled={!vm.imgLoaded} onClick={() => e.toggleSnap()}>吸附</XQToggle>
											<XQButton size="small" variant="ghost" disabled={!vm.imgLoaded} onClick={() => e.zoomOut()}>−</XQButton>
											<span className="horosa-fengshui-zoom">{vm.zoomPct}%</span>
											<XQButton size="small" variant="ghost" disabled={!vm.imgLoaded} onClick={() => e.zoomIn()}>＋</XQButton>
											<XQButton size="small" variant="ghost" disabled={!vm.imgLoaded} onClick={() => e.resetView()}>重置</XQButton>
										</div>
									</div>
									<div className="horosa-fengshui-canvas-host">
										<canvas ref={this.canvasRef} className="horosa-fengshui-canvas" />
										{!vm.imgLoaded ? <div className="horosa-fengshui-canvas-hint">上传户型图后开始操作</div> : null}
									</div>
								</div>
							</TabPane>
							<TabPane tab="判定" key="analysis">{this.renderJudgePanel(vm)}</TabPane>
							<TabPane tab="要点" key="tips">
								<div className="horosa-fengshui-card">
									<div className="horosa-fengshui-card-title">使用要点</div>
									<ul className="horosa-fengshui-tips">{TIPS.map((t, i) => <li key={i}>{t}</li>)}</ul>
								</div>
							</TabPane>
						</XQTabs>
					</Col>
				</Row>
			</div>
		);
	}
}

export default FengShuiMain;
