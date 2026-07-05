import React from 'react';
import ReactDOM from 'react-dom';

// 通用左栏全宽展开器(2026-07-05 L1):所有技法页左栏(.horosa-astro-input-panel)右上角
// 注入一枚「全宽/还原」切换钮——展开时 body 挂 horosa-left-panel-expanded,由 app.less 的
// :has 规则把该左栏所在网格改为单列、兄弟列隐藏 → 左栏占满工作区,密集设置完整可读;
// 再点或按 Esc 还原。单点挂载(pages/index.js),零逐页侵入;无可见左栏时按钮自隐。
const BODY_CLASS = 'horosa-left-panel-expanded';
const PANEL_SELECTOR = '.horosa-astro-input-panel';

function findVisiblePanel(){
	const panels = document.querySelectorAll(PANEL_SELECTOR);
	for(let i = 0; i < panels.length; i++){
		const rect = panels[i].getBoundingClientRect();
		if(rect.width > 0 && rect.height > 0){
			return panels[i];
		}
	}
	return null;
}

export default class LeftPanelExpand extends React.Component {
	constructor(props){
		super(props);
		this.state = { host: null, expanded: false };
		this.sync = this.sync.bind(this);
		this.toggle = this.toggle.bind(this);
		this.onKeyDown = this.onKeyDown.bind(this);
	}

	componentDidMount(){
		// 轻量轮询定位可见左栏(页面切换/FreezeInactive 换活页时跟随);400ms 一次,零感知开销。
		this.timer = setInterval(this.sync, 400);
		this.sync();
		window.addEventListener('keydown', this.onKeyDown);
	}

	componentWillUnmount(){
		clearInterval(this.timer);
		window.removeEventListener('keydown', this.onKeyDown);
		document.body.classList.remove(BODY_CLASS);
	}

	onKeyDown(ev){
		if(ev.key === 'Escape' && this.state.expanded){
			this.toggle();
		}
	}

	sync(){
		const panel = findVisiblePanel();
		if(panel !== this.state.host){
			this.setState({ host: panel });
		}
	}

	toggle(){
		const expanded = !this.state.expanded;
		document.body.classList.toggle(BODY_CLASS, expanded);
		this.setState({ expanded });
	}

	render(){
		const { host, expanded } = this.state;
		if(!host){
			return null;
		}
		const btn = (
			<button
				type="button"
				className={`horosa-left-expand-toggle${expanded ? ' is-expanded' : ''}`}
				title={expanded ? '还原左栏宽度（Esc）' : '左栏展开为全宽'}
				aria-label={expanded ? '还原左栏宽度' : '左栏展开为全宽'}
				onClick={this.toggle}
			>
				{expanded ? '⤡ 还原' : '⤢ 全宽'}
			</button>
		);
		return ReactDOM.createPortal(btn, host);
	}
}
