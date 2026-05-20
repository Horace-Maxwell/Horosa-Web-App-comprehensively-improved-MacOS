import { Component } from 'react';
import { Row, Col } from 'antd';
import { XQCard as Card } from '../xq-ui';
import { randomStr } from '../../utils/helper';
import styles from '../../css/styles.less';

function safeArray(value){
	return Array.isArray(value) ? value : [];
}

class Gods extends Component{
	constructor(props) {
		super(props);
		this.state = {
			
		};

		this.genGods = this.genGods.bind(this);
		this.genGodsDom = this.genGodsDom.bind(this);
	}

	genGodsDom(rec){
		if(rec === undefined || rec === null){
			return null;
		}
		let cols = this.genGods(rec, '整柱');
		let ganCols = this.genGods(rec.stem, '天干');
		let ziCols = this.genGods(rec.branch, '地支');
		let doms = [];
		if(cols){
			let row = (
				<Row gutter={12} key={randomStr(8)}>
					{cols}
				</Row>
			);
			doms.push(row);
		}
		if(ganCols){
			let row = (
				<Row gutter={12} key={randomStr(8)}>
					{ganCols}
				</Row>
			);
			doms.push(row);
		}
		if(ziCols){
			let row = (
				<Row gutter={12} key={randomStr(8)}>
					{ziCols}
				</Row>
			);
			doms.push(row);
		}

		let taisuiCols = [];
		let spans = [];
		const taisuiGods = safeArray(rec.branch && rec.branch.taisuiGods);
		for(let i=0; i<taisuiGods.length; i++){
			let str = taisuiGods[i];
			let span = (
				<span key={randomStr(8)}>{str}&emsp;</span>
			);
			spans.push(span);
		}
		if(spans.length > 0){
			let title = (<Col key={randomStr(8)} span={4}>太岁：</Col>);
			taisuiCols.push(title);
			let content = (
				<Col key={randomStr(8)} span={20}>{spans}</Col>
			);
			taisuiCols.push(content);
		}
		if(taisuiCols.length > 0){
			let row = (
				<Row gutter={12} key={randomStr(8)}>
					{taisuiCols}
				</Row>
			);
			doms.push(row);
		}
		if(doms.length > 0){
			return doms;
		}else{
			return null;
		}
	}

	genGods(rec, titleStr){
		if(rec === undefined || rec === null){
			return null;
		}
		let cols = [];
		let spans = [];
		const goodGods = safeArray(rec.goodGods);
		const neutralGods = safeArray(rec.neutralGods);
		const badGods = safeArray(rec.badGods);
		for(let i=0; i<goodGods.length; i++){
			let str = goodGods[i];
			let span = (
				<span key={randomStr(8)}>{str}&emsp;</span>
			);
			spans.push(span);
		}
		for(let i=0; i<neutralGods.length; i++){
			let str = neutralGods[i];
			let span = (
				<span key={randomStr(8)}>{str}&emsp;</span>
			);
			spans.push(span);
		}
		for(let i=0; i<badGods.length; i++){
			let str = badGods[i];
			let span = (
				<span key={randomStr(8)}>{str}&emsp;</span>
			);
			spans.push(span);
		}
		if(spans.length > 0){
			let title = (<Col key={randomStr(8)} span={4}>{titleStr}：</Col>);
			cols.push(title);
			let content = (
				<Col key={randomStr(8)} span={20}>{spans}</Col>
			);
			cols.push(content);
		}
		if(cols.length > 0){
			return cols;
		}
		return null;
	}

	render(){
		let rec = this.props.value ? this.props.value : {};
		let height = this.props.height ? this.props.height : '100%';
		let style = {
			height: (height-130) + 'px',
			overflowY:'auto', 
			overflowX:'hidden',
		};

		let yeardom = this.genGodsDom(rec.year);
		let monthdom = this.genGodsDom(rec.month);
		let daydom = this.genGodsDom(rec.day);
		let timedom = this.genGodsDom(rec.time);
		let taidom = this.genGodsDom(rec.tai);
		let mingdom = this.genGodsDom(rec.ming);
		let shendom = this.genGodsDom(rec.shen);

		return (
			<div className={styles.scrollbar} style={style}>
				<Card title='年柱' bordered={true} >
					{yeardom}
				</Card>	
				<Card title='月柱' bordered={true} >
					{monthdom}
				</Card>
				<Card title='日柱' bordered={true} >
					{daydom}
				</Card>
				<Card title='时柱' bordered={true} >
					{timedom}
				</Card>
				{
					taidom && (
						<Card title='胎元' bordered={true} >
							{taidom}
						</Card>		
					)
				}
				{
					mingdom && (
						<Card title='命宫' bordered={true} >
							{mingdom}
						</Card>		
					)
				}
				{
					shendom && (
						<Card title='身宫' bordered={true} >
							{shendom}
						</Card>		
					)
				}
			</div>
		);
	}
}

export default Gods;
