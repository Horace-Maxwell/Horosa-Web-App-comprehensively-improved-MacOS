import { Component } from 'react';
import { List, } from 'antd';
import { ColorTheme, ReaderThemeKey, } from '../constants/ReaderConst';

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


function getColorTheme(){
	let theme = localStorage.getItem(ReaderThemeKey);
	if(theme === undefined || theme === null){
		theme = ColorTheme[0];
	}else{
		theme = JSON.parse(theme);
	}

	return theme;
}

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
		let theme = getColorTheme();
		const pages = this.props.pages && this.props.pages.length ? this.props.pages : Pages;
		const currentKey = this.props.currentKey || (this.state.page ? this.state.page.key : '');
		
		let dom = (
			<List
				size='default'
				dataSource={pages}
				renderItem={(rec)=>{
					let style = {
						whiteSpace: 'nowrap', 
						textOverflow: 'ellipsis',
						overflowX: 'hidden',
						marginLeft: 10
					};
					let colorstyle = {};
					if(currentKey === rec.key){
						style.backgroundColor = theme.bgColor;
						style.color = theme.color;				
						colorstyle.backgroundColor = theme.bgColor;
						colorstyle.color = theme.color;				
					}
					return (
						<List.Item key={rec.key} onClick={()=>{ this.clickPage(rec); }}
							style={colorstyle}
						>
							<div style={style}>{rec.label}</div>
						</List.Item>
					)
				}}
			/>
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
