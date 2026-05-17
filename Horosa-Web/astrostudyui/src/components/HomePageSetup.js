import { Component } from 'react';
import { XQNavItem } from './xq-ui';

const Pages = [{
	path: ['astrochart'],
	label: '占星',
	key: 'astrochart',
},{
	path: ['bazi'],
	label: '八字',
	key: 'bazi',
},{
	path: ['ziwei'],
	label: '紫微',
	key: 'ziwei',
},{
	path: ['astroreader'],
	label: '书籍阅读',
	key: 'astroreader',
}];


class HomePageSetup extends Component{

	constructor(props){
		super(props);

		this.state = {
			page: this.getInitialPage(props),
		}

		this.genDom = this.genDom.bind(this);
		this.clickPage = this.clickPage.bind(this);
	}

	getInitialPage(props){
		const pages = props.pages && props.pages.length ? props.pages : Pages;
		const key = props.currentKey;
		const current = pages.find((rec)=>rec.key === key);
		return current || pages[0];
	}

	clickPage(rec){
		this.setState({
			page: rec,
		}, ()=>{
			if(this.props.onNavigate){
				this.props.onNavigate(rec.key);
			}
			if(this.props.onClose){
				this.props.onClose();
			}
		});
	}

	genDom(){
		const pages = this.props.pages && this.props.pages.length ? this.props.pages : Pages;
		const currentKey = this.props.currentKey || (this.state.page ? this.state.page.key : '');
		const groupedPages = pages.reduce((groups, rec)=>{
			const groupName = rec.group || '其他';
			if(!groups[groupName]){
				groups[groupName] = [];
			}
			groups[groupName].push(rec);
			return groups;
		}, {});
		const groupOrder = ['命', '卜', '工具', '内容与管理', '其他'].filter((name)=>groupedPages[name]);
		
		let dom = (
			<div className="xq-nav-list">
				{groupOrder.map((groupName)=>(
					<div className="xq-nav-group" key={groupName}>
						<div className="xq-nav-group-title">{groupName}</div>
						<div className="xq-nav-group-items">
							{groupedPages[groupName].map((rec)=>(
								<XQNavItem
									key={rec.key}
									item={rec}
									active={currentKey === rec.key}
									onClick={()=>{ this.clickPage(rec); }}
								/>
							))}
						</div>
					</div>
				))}
			</div>
		);
		return dom;
	}

	render(){
		let dom = this.genDom();
		return (
			<div>
				{dom}
			</div>
		);
	}

}

export default HomePageSetup;
