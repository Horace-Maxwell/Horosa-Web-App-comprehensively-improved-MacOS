import { Component } from 'react';
import { Row, Col, Divider, Popover, } from 'antd';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import * as AstroHelper from '../astro/AstroHelper';
import { randomStr} from '../../utils/helper'
import { buildMeaningTipByCategory, } from '../astro/AstroMeaningData';
import { isMeaningEnabled, wrapWithMeaning, } from '../astro/AstroMeaningPopover';
import styles from '../../css/styles.less';

class Midpoint extends Component{

	constructor(props) {
		super(props);
		this.state = {
			 
		}

			this.genOneMidDom = this.genOneMidDom.bind(this);
			this.genMidsDom = this.genMidsDom.bind(this);
			this.showMeaning = this.showMeaning.bind(this);
		}

	showMeaning(){
		return isMeaningEnabled(this.props.showAstroMeaning);
	}

	genOneMidDom(obj){
		let degs = AstroHelper.splitDegree(obj.signlon);
		let term = AstroHelper.whichTerm(obj.sign, obj.signlon);
			let dom = (
				<div key={randomStr(8)} style={{marginTop:3}}>
					{wrapWithMeaning(
						<span style={{fontFamily: AstroConst.AstroFont}}>{AstroText.AstroMsg[obj.idA]}</span>,
						this.showMeaning(),
						buildMeaningTipByCategory('planet', obj.idA)
					)}
					<span style={{fontFamily: AstroConst.NormalFont}}>&nbsp;|&nbsp;</span>
					{wrapWithMeaning(
						<span style={{fontFamily: AstroConst.AstroFont}}>{AstroText.AstroMsg[obj.idB]}</span>,
						this.showMeaning(),
						buildMeaningTipByCategory('planet', obj.idB)
					)}
					<span style={{fontFamily: AstroConst.NormalFont}}>&nbsp;=&nbsp;</span>
					<span style={{fontFamily: AstroConst.NormalFont}}>{degs[0] + 'º'}&nbsp;</span>
					{wrapWithMeaning(
						<span style={{fontFamily: AstroConst.AstroFont}}>{AstroText.AstroMsg[obj.sign]}&nbsp;</span>,
						this.showMeaning(),
						buildMeaningTipByCategory('sign', obj.sign)
					)}
					<span style={{fontFamily: AstroConst.NormalFont}}>{degs[1] + "'；"}</span>
					<span style={{fontFamily: AstroConst.NormalFont}}>位于&nbsp;</span>
					{wrapWithMeaning(
						<span style={{fontFamily: AstroConst.AstroFont}}>{term}</span>,
						this.showMeaning(),
						buildMeaningTipByCategory('sign', obj.sign)
					)}
					<span style={{fontFamily: AstroConst.NormalFont}}>&nbsp;界</span>
				</div>
			);

		return dom;
	}

	genMidsDom(midpoints){
		if(midpoints === undefined || midpoints === null){
			return null;
		}
		let divs = [];
		let lastsig = midpoints[0].sign;
		for(let i=0; i<midpoints.length; i++){
			let obj = midpoints[i];
			let middom = this.genOneMidDom(obj);
			if(obj.sign !== lastsig){
				let spacedom = (
					<Col key={randomStr(8)} span={24}>
					<div key={randomStr(8)}>
						<span>&nbsp;</span>
					</div>
					</Col>
				);
				lastsig = obj.sign
				divs.push(spacedom);
			}
			let dom = (
				<Col key={randomStr(8)} span={24}>{middom}</Col>
			);
			divs.push(dom);
		}

		return divs;
	}


	render(){
		let height = this.props.height ? this.props.height : '100%';
		let style = {
			height: (height-180) + 'px',
			overflowY:'auto', 
			overflowX:'hidden',
		};

		let mids = this.genMidsDom(this.props.value);

		return (
			<div className={styles.scrollbar} style={style}>
				<Row>
				{mids}
				</Row>
			</div>
		);
	}

}

export default Midpoint;
