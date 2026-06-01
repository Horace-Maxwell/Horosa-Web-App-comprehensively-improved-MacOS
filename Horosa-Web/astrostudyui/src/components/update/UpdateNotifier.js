import React from 'react';
import {
	isDesktopBridgeAvailable,
	updateCheckSilent,
	updateStartBackground,
	updateInstallAndRestart,
} from '../../utils/aiAnalysisDesktop';
import styles from './UpdateNotifier.less';

// v2.2.1 软件内升级·非阻塞 UX。
// 复用 Rust 自研 updater 核心(下载/校验/双件/重启),这里只做主窗口内的非模态交互:
//   启动自动检测 → 右下角卡片(更新/稍后/查看更新内容)→ 后台下载(可最小化为进度药丸,不挡使用)
//   → 下载完成「重启更新」由用户主动触发。非桌面环境整体静默不渲染。
// 事件来自 Rust emit_update_event → window.__horosaUpdateEvent;手动检查入口 window.__horosaTriggerUpdateCheck。

const PHASE_IDLE = 'idle';
const PHASE_AVAILABLE = 'available';
const PHASE_DOWNLOADING = 'downloading';
const PHASE_READY = 'ready';
const PHASE_ERROR = 'error';

class UpdateNotifier extends React.Component {
	constructor(props){
		super(props);
		this.state = {
			phase: PHASE_IDLE,
			minimized: false,
			pct: 0,
			message: '',
			latestVersion: '',
			currentVersion: '',
			notes: '',
			releaseUrl: '',
			toast: '',
		};
		this.mounted = false;
		this.toastTimer = null;
		this.onEvent = this.onEvent.bind(this);
		this.onUpdate = this.onUpdate.bind(this);
		this.onLater = this.onLater.bind(this);
		this.onViewNotes = this.onViewNotes.bind(this);
		this.onRestart = this.onRestart.bind(this);
		this.onRetry = this.onRetry.bind(this);
		this.triggerManualCheck = this.triggerManualCheck.bind(this);
	}

	componentDidMount(){
		this.mounted = true;
		if(!isDesktopBridgeAvailable()){
			return;
		}
		window.__horosaUpdateEvent = this.onEvent;
		window.__horosaTriggerUpdateCheck = this.triggerManualCheck;
		// 补读启动期间可能已发出的 pending 事件(镜像 launcher __horosaPending* 模式)。
		if(window.__horosaPendingUpdateEvent){
			try{ this.onEvent(window.__horosaPendingUpdateEvent); }catch(e){ /* noop */ }
		}
	}

	componentWillUnmount(){
		this.mounted = false;
		if(this.toastTimer){ clearTimeout(this.toastTimer); }
		if(window.__horosaUpdateEvent === this.onEvent){ window.__horosaUpdateEvent = null; }
		if(window.__horosaTriggerUpdateCheck === this.triggerManualCheck){ window.__horosaTriggerUpdateCheck = null; }
	}

	showToast(text){
		if(!this.mounted){ return; }
		this.setState({ toast: text });
		if(this.toastTimer){ clearTimeout(this.toastTimer); }
		this.toastTimer = setTimeout(()=>{
			if(this.mounted){ this.setState({ toast: '' }); }
		}, 3200);
	}

	onEvent(payload){
		if(!this.mounted || !payload){ return; }
		const phase = payload.phase;
		if(phase === 'available'){
			this.setState({
				phase: PHASE_AVAILABLE,
				minimized: false,
				latestVersion: payload.latestVersion || '',
				currentVersion: payload.currentVersion || '',
				notes: payload.notes || '',
				releaseUrl: payload.releaseUrl || '',
			});
		}else if(phase === 'checking' || phase === 'downloading'){
			this.setState({
				phase: PHASE_DOWNLOADING,
				pct: typeof payload.pct === 'number' ? payload.pct : this.state.pct,
				message: payload.message || this.state.message,
			});
		}else if(phase === 'ready'){
			this.setState({
				phase: PHASE_READY,
				minimized: false,
				pct: 100,
				latestVersion: payload.version || this.state.latestVersion,
			});
		}else if(phase === 'uptodate'){
			this.setState({ phase: PHASE_IDLE });
			this.showToast('已是最新版本');
		}else if(phase === 'error'){
			this.setState({ phase: PHASE_ERROR, message: payload.message || '更新失败' });
		}
	}

	async triggerManualCheck(){
		if(!isDesktopBridgeAvailable()){ return; }
		this.showToast('正在检查更新…');
		try{
			const res = await updateCheckSilent();
			if(res && res.available){
				this.onEvent({
					phase: 'available',
					latestVersion: res.latestVersion,
					currentVersion: res.currentVersion,
					notes: res.notes,
					releaseUrl: res.releaseUrl,
				});
			}else{
				this.showToast('已是最新版本');
			}
		}catch(e){
			this.showToast('检查更新失败,请稍后再试');
		}
	}

	async onUpdate(){
		this.setState({ phase: PHASE_DOWNLOADING, pct: 2, message: '准备下载…', minimized: false });
		try{
			await updateStartBackground();
		}catch(e){
			this.setState({ phase: PHASE_ERROR, message: '无法开始下载,请稍后再试' });
		}
	}

	onLater(){
		this.setState({ phase: PHASE_IDLE });
	}

	onViewNotes(){
		const url = this.state.releaseUrl;
		if(url){
			try{ window.open(url, '_blank'); }catch(e){ /* noop */ }
		}
	}

	async onRestart(){
		try{
			await updateInstallAndRestart();
		}catch(e){
			this.setState({ phase: PHASE_ERROR, message: '重启更新失败,请稍后再试' });
		}
	}

	onRetry(){
		this.onUpdate();
	}

	renderToast(){
		if(!this.state.toast){ return null; }
		return <div className={styles.toast}>{this.state.toast}</div>;
	}

	render(){
		const { phase, minimized, pct, message, latestVersion, currentVersion, notes } = this.state;
		if(!isDesktopBridgeAvailable()){
			return null;
		}
		if(phase === PHASE_IDLE){
			return this.renderToast();
		}

		// 最小化:收成右下角进度药丸(下载中),点开恢复卡片。
		if(minimized && phase === PHASE_DOWNLOADING){
			return (
				<React.Fragment>
					{this.renderToast()}
					<button
						type="button"
						className={styles.pill}
						onClick={()=>this.setState({ minimized: false })}
						title="正在后台下载更新"
					>
						<span className={styles.pillSpinner} />
						<span className={styles.pillText}>更新 {Math.round(pct)}%</span>
					</button>
				</React.Fragment>
			);
		}

		let body = null;
		if(phase === PHASE_AVAILABLE){
			body = (
				<React.Fragment>
					<div className={styles.title}>发现新版本 v{latestVersion}</div>
					<div className={styles.sub}>当前 v{currentVersion} → 新版 v{latestVersion}</div>
					{notes ? <div className={styles.notes}>{notes}</div> : null}
					<div className={styles.actions}>
						<button type="button" className={styles.btnPrimary} onClick={this.onUpdate}>立即更新</button>
						<button type="button" className={styles.btnGhost} onClick={this.onLater}>稍后</button>
						<button type="button" className={styles.btnLink} onClick={this.onViewNotes}>查看更新内容</button>
					</div>
				</React.Fragment>
			);
		}else if(phase === PHASE_DOWNLOADING){
			body = (
				<React.Fragment>
					<div className={styles.titleRow}>
						<div className={styles.title}>正在下载更新 v{latestVersion}</div>
						<button type="button" className={styles.iconBtn} onClick={()=>this.setState({ minimized: true })} title="最小化,继续使用">—</button>
					</div>
					<div className={styles.progressTrack}>
						<div className={styles.progressFill} style={{ width: `${Math.max(2, Math.min(100, pct))}%` }} />
					</div>
					<div className={styles.sub}>{message || '下载中…'} · {Math.round(pct)}%</div>
					<div className={styles.hint}>可最小化继续使用,下载完成后再重启更新。</div>
				</React.Fragment>
			);
		}else if(phase === PHASE_READY){
			body = (
				<React.Fragment>
					<div className={styles.title}>更新已就绪 v{latestVersion}</div>
					<div className={styles.sub}>已下载并校验完成,准备好后即可重启完成更新。</div>
					<div className={styles.actions}>
						<button type="button" className={styles.btnPrimary} onClick={this.onRestart}>重启更新</button>
						<button type="button" className={styles.btnGhost} onClick={this.onLater}>稍后</button>
					</div>
				</React.Fragment>
			);
		}else if(phase === PHASE_ERROR){
			body = (
				<React.Fragment>
					<div className={styles.title}>更新未完成</div>
					<div className={styles.sub}>{message}</div>
					<div className={styles.actions}>
						<button type="button" className={styles.btnPrimary} onClick={this.onRetry}>重试</button>
						<button type="button" className={styles.btnGhost} onClick={this.onLater}>关闭</button>
					</div>
				</React.Fragment>
			);
		}

		return (
			<React.Fragment>
				{this.renderToast()}
				<div className={styles.card} role="dialog" aria-label="软件更新">
					{body}
				</div>
			</React.Fragment>
		);
	}
}

export default UpdateNotifier;
