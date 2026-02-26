import { Component, createRef } from 'react';
import { Card } from 'antd';
import { saveModuleAISnapshot, } from '../../utils/moduleAiSnapshot';

class FengShuiMain extends Component {
	constructor(props){
		super(props);
		this.state = {
			reloadKey: 1,
		};
		this.iframeRef = createRef();
		this.snapshotTimer = null;
		this.handleSnapshotRefreshRequest = this.handleSnapshotRefreshRequest.bind(this);
		this.handleIframeLoad = this.handleIframeLoad.bind(this);
	}

	componentDidMount(){
		if(typeof window !== 'undefined'){
			window.addEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
		this.restartSnapshotPolling();
	}

	componentWillUnmount(){
		if(typeof window !== 'undefined'){
			window.removeEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
		this.stopSnapshotPolling();
	}

	handleIframeLoad(){
		this.saveFengShuiSnapshot();
		this.restartSnapshotPolling();
	}

	handleSnapshotRefreshRequest(evt){
		const moduleName = evt && evt.detail ? evt.detail.module : '';
		if(moduleName !== 'fengshui'){
			return;
		}
		const snapshotText = this.saveFengShuiSnapshot();
		if(snapshotText && evt && evt.detail && typeof evt.detail === 'object'){
			evt.detail.snapshotText = snapshotText;
		}
	}

	stopSnapshotPolling(){
		if(this.snapshotTimer){
			clearInterval(this.snapshotTimer);
			this.snapshotTimer = null;
		}
	}

	restartSnapshotPolling(){
		this.stopSnapshotPolling();
		this.snapshotTimer = setInterval(()=>{
			this.saveFengShuiSnapshot();
		}, 1200);
	}

	readFengShuiSnapshotText(){
		const iframe = this.iframeRef && this.iframeRef.current ? this.iframeRef.current : null;
		if(!iframe || !iframe.contentWindow){
			return '';
		}
		try{
			const win = iframe.contentWindow;
			if(typeof win.__horosa_fengshui_snapshot_text === 'string'){
				return `${win.__horosa_fengshui_snapshot_text}`.trim();
			}
		}catch(e){
		}
		return '';
	}

	saveFengShuiSnapshot(){
		const snapshotText = this.readFengShuiSnapshotText();
		if(!snapshotText){
			return '';
		}
		saveModuleAISnapshot('fengshui', snapshotText, {
			source: 'iframe',
			savedAt: Date.now(),
		});
		return snapshotText;
	}

	render(){
		let height = this.props.height ? this.props.height : 760;
		if(height === '100%'){
			height = 'calc(100% - 48px)';
		}else{
			height = height + 28;
		}

		return (
			<div style={{ minHeight: height, marginTop: -12 }}>
				<Card bordered={false} bodyStyle={{ padding: 0 }}>
					<iframe
						ref={this.iframeRef}
						key={`fengshui_iframe_${this.state.reloadKey}`}
						title="风水纳气"
						src="/fengshui/index.html?embedded=horosa"
						onLoad={this.handleIframeLoad}
						style={{
							width: '100%',
							height: typeof height === 'number' ? `${height}px` : 'calc(100vh - 132px)',
							border: '1px solid #f0f0f0',
							borderRadius: 8,
							background: '#fff',
						}}
					/>
				</Card>
			</div>
		);
	}
}

export default FengShuiMain;
