import { Component } from 'react';
import { Row, Col, Popover, Divider, } from 'antd';
import { randomStr } from '../../utils/helper';
import { BaZiMsg } from '../../msg/bazimsg';
import styles from '../../css/styles.less';

function safeArray(value){
	return Array.isArray(value) ? value : [];
}

function describeStemBranch(item){
	if(!item){
		return '';
	}
	return `${BaZiMsg[item.polar] || ''}${item.cell || ''}${BaZiMsg[item.element] || ''}•${BaZiMsg[item.relative] || item.relative || ''}`;
}

class SmallDirection extends Component{
	constructor(props) {
		super(props);
		this.state = {
			
		};

		this.genDirectionDom = this.genDirectionDom.bind(this);
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

	genDirectionDom(dirs){
		let dirdoms = [];
			for(let i=0; i<dirs.length; i++){
				let dir = dirs[i] || {};
				let age = dir.age;
				let year = dir.year;
				let subdir = dir.direct || {};
				let yeardir = dir.yearGanzi || {};
				let subgods = this.genGodsDom(subdir);
				let yeargods = this.genGodsDom(yeardir);
				let starCharger = yeardir.starCharger || {};
				let popsubcontent = (
					<div style={{width: 350}}>
						<Row key={randomStr(8)}>
							<Col span={24} key={randomStr(8)}>
								{describeStemBranch(subdir.stem)}
							</Col>
							<Col span={24} key={randomStr(8)}>
								{describeStemBranch(subdir.branch)}
							</Col>
						<Col span={24} key={randomStr(8)}><Divider /></Col>
					</Row>
					{subgods}
				</div>
			)
			let popyearcontent = (
				<div style={{width: 350}}>
					<Row key={randomStr(8)}>
							<Col span={24} key={randomStr(8)}>
								{describeStemBranch(yeardir.stem)}
							</Col>
							<Col span={24} key={randomStr(8)}>
								{describeStemBranch(yeardir.branch)}
							</Col>
						<Col span={24} key={randomStr(8)}><Divider /></Col>
						</Row>
						{yeargods}
						<h4>值年星宿：{starCharger.name || '暂无'}</h4>
						<div>{starCharger.event || ''}</div>
					</div>
				)

			let row = (
				<Row key={randomStr(8)} gutter={12}>
					<Col span={9}>
							<Popover content={popsubcontent} title={'小运：' + (subdir.ganzi || '')}>
								小运：{subdir.ganzi || ''}（{subdir.naying || ''}）
							</Popover>
						</Col>
						<Col span={9}>
							<Popover content={popyearcontent} title={'流年：' + (yeardir.ganzi || '') + ' ' + year + ' ' + age + '岁'}>
								流年：{yeardir.ganzi || ''}（{yeardir.naying || ''}）
							</Popover>
					</Col>
					<Col span={3}>{year}</Col>
					<Col span={3}>{age}周岁</Col>
				</Row>
			);
			dirdoms.push(row);
		}
		return dirdoms;

	}

	render(){
		let rec = this.props.value ? this.props.value : {};
		let height = this.props.height ? this.props.height : '100%';
		let style = {
			height: (height-130) + 'px',
			overflowY:'auto', 
			overflowX:'hidden',
		};

			let doms = this.genDirectionDom(safeArray(rec.smallDirection));

		return (
			<div className={styles.scrollbar} style={style}>
				{doms}
			</div>
		);
	}
}

export default SmallDirection;

