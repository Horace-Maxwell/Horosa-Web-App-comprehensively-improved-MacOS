import { Component } from 'react';
import { Row, Col, Divider, Popover} from 'antd';
import { XQCard as Card, XQTabs as Tabs } from '../xq-ui';
import { randomStr } from '../../utils/helper';
import { BaZiMsg } from '../../msg/bazimsg';
import styles from '../../css/styles.less';

const TabPane = Tabs.TabPane;

function safeArray(value){
	return Array.isArray(value) ? value : [];
}

function describeStemBranch(item){
	if(!item){
		return '';
	}
	return `${BaZiMsg[item.polar] || ''}${item.cell || ''}${BaZiMsg[item.element] || ''}•${BaZiMsg[item.relative] || item.relative || ''}`;
}

class MainDirection extends Component{
	constructor(props) {
		super(props);
		this.state = {
			
		};
		this.genDirectionDom = this.genDirectionDom.bind(this);
		this.genSubDirectDom = this.genSubDirectDom.bind(this);
		this.genGods = this.genGods.bind(this);
		this.genGodsDom = this.genGodsDom.bind(this);
	}

	genGodsDom(rec){
		if(rec === undefined || rec === null){
			return null;
		}
		let cols = this.genGods(rec, '柱');
		let ganCols = this.genGods(rec.stem, '干');
		let ziCols = this.genGods(rec.branch, '支');
		let doms = [];
		if(cols){
			let row = (
				<Row key={randomStr(8)}>
					{cols}
				</Row>
			);
			doms.push(row);
		}
		if(ganCols){
			let row = (
				<Row key={randomStr(8)}>
					{ganCols}
				</Row>
			);
			doms.push(row);
		}
		if(ziCols){
			let row = (
				<Row key={randomStr(8)}>
					{ziCols}
				</Row>
			);
			doms.push(row);
		}

		let taisuiCols = [];
		let spans = [];
			const taisuiGods = safeArray(rec.branch && rec.branch.taisuiGods);
			if(taisuiGods.length > 0){
				spans.push(taisuiGods.join('，'));
			}
		if(spans.length > 0){
			let content = (
				<Col key={randomStr(8)} span={24}>
					<div>岁：&emsp;{spans.join('，')}</div>
				</Col>
			);
			taisuiCols.push(content);
		}
		if(taisuiCols.length > 0){
			let row = (
				<Row key={randomStr(8)}>
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
			if(goodGods.length > 0){
				spans.push(goodGods.join('，'));
			}
			if(neutralGods.length > 0){
				spans.push(neutralGods.join('，'));
			}
			if(badGods.length > 0){
				spans.push(badGods.join('，'));
			}

		if(spans.length > 0){
			let content = (
				<Col key={randomStr(8)} span={24}>
					<div>{titleStr}：&emsp;{spans.join('，')}</div>
				</Col>
			);
			cols.push(content);
		}
		if(cols.length > 0){
			return cols;
		}
		return null;
	}


	genSubDirectDom(dir, startYear, age, mainDirect, directTime, height){
		let dirdoms = [];
			for(let i=0; i<dir.length; i++){
				let sub = dir[i] || {};
				let y = startYear + i;
				let dirtm = y;
				let gods = this.genGodsDom(sub);
				let starCharger = sub.starCharger || {};
				let popcontent = (
					<div style={{width: 350}}>
						<Row key={randomStr(8)} style={{width: 350}}>
							<Col span={24} key={randomStr(8)}>
								{describeStemBranch(sub.stem)}
							</Col>
							<Col span={24} key={randomStr(8)}>
								{describeStemBranch(sub.branch)}
							</Col>
						</Row>
						<Divider />
						{gods}
						<h4>值年星宿：{starCharger.name || '暂无'}</h4>
						<div>{starCharger.event || ''}</div>
					</div>
				)
				let titlerow = (
					<Popover content={popcontent} title={(sub.ganzi || '') + ' ' + dirtm + ' ' + (age + i) + '岁'} key={randomStr(8)}>
						<Row key={randomStr(8)}>
							<Col span={4}>{sub.ganzi || ''}</Col>
							<Col span={6}>{sub.naying || ''}</Col>
							<Col span={9}>{dirtm}</Col>
							<Col span={5}>{age + i}岁</Col>
					</Row>
				</Popover>
			);

			dirdoms.push(titlerow);
		}
		let dirTime = startYear;

			let maingods = this.genGodsDom(mainDirect);
			let title = (
				<div key={randomStr(8)}>
					<Row>
						<Col span={12}>{[mainDirect.ganzi, mainDirect.ganziPhase].filter(Boolean).join('-')}</Col>
						<Col span={12}>{[mainDirect.naying, mainDirect.nayingPhase].filter(Boolean).join('-')}</Col>
						<Col span={12} key={randomStr(8)}>
							{describeStemBranch(mainDirect.stem)}
						</Col>
						<Col span={12} key={randomStr(8)}>
							{describeStemBranch(mainDirect.branch)}
						</Col>
				</Row>
				{maingods}
				<Row>
					<Col span={24}>{'开始时间：' + dirTime}</Col>
				</Row>
			</div>
		);
		let dom = (
			<Card title={title} bordered={false}>
				{dirdoms}
			</Card>
		);
		return dom;
	}

	genDirectionDom(dirs, directTime, height){
		let panes = [];
		if(dirs && dirs.length){
				for(let i = 0; i<dirs.length && i<8; i++){
					let dir = dirs[i];
					let age = dir.age;
					let startYear = dir.startYear;
					let mainDirect = dir.mainDirect || {};
					let subdir = this.genSubDirectDom(safeArray(dir.subDirect), startYear, age, mainDirect, directTime, height);
					let pane = (
						<TabPane tab={startYear + ' ' + (mainDirect.ganzi || '')} key={i}>
							{subdir}
						</TabPane>
				);
				panes.push(pane);
			}	
		}
		return panes;
	}

	render(){
		let rec = this.props.value ? this.props.value : {};
		let height = this.props.height ? this.props.height : '100%';
		let style = {
			height: (height-130) + 'px',
			overflowY:'auto', 
			overflowX:'hidden',
		};

			let doms = this.genDirectionDom(safeArray(rec.direction), rec.directTime, height);
			let directAge = Number.isFinite(rec.directAge) ? rec.directAge.toFixed(0) : '';
			let directYear = typeof rec.directTime === 'string' ? rec.directTime.substr(0, 4) : '';

		return (
			<div className={styles.scrollbar} style={style}>
				<Row style={{marginLeft:20}}>
						<Col span={24} style={{fontSize: 16, fontWeight: 'bold'}}>
							{'上运时间：' + directAge + '周岁 ' + directYear + ' '}
						</Col>
				</Row>
				<Tabs defaultActiveKey="0" tabPosition='right' style={{marginTop: 15}}>
					{doms}
				</Tabs>
			</div>
		);
	}
}

export default MainDirection;
