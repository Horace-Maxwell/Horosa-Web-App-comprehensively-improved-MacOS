import { Component } from 'react';
import { Row, Col, Divider, Popover, Card, } from 'antd';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import * as AstroHelper from './AstroHelper';
import { buildMeaningTipByCategory, } from './AstroMeaningData';
import { isMeaningEnabled, wrapWithMeaning, } from './AstroMeaningPopover';
import styles from '../../css/styles.less';

class AstroLots extends Component{

	constructor(props) {
		super(props);
		this.state = {

		}
		this.genLotsDom = this.genLotsDom.bind(this);
		this.renderTitle = this.renderTitle.bind(this);
		this.showMeaning = this.showMeaning.bind(this);
		this.withLotMeaning = this.withLotMeaning.bind(this);
		this.withPlanetMeaning = this.withPlanetMeaning.bind(this);
		this.withSignMeaning = this.withSignMeaning.bind(this);
		this.withHouseMeaning = this.withHouseMeaning.bind(this);
	}

	showMeaning(){
		return isMeaningEnabled(this.props.showAstroMeaning);
	}

	withPlanetMeaning(node, objid){
		return wrapWithMeaning(node, this.showMeaning(), buildMeaningTipByCategory('planet', objid));
	}

	withLotMeaning(node, objid){
		return wrapWithMeaning(node, this.showMeaning(), buildMeaningTipByCategory('lot', objid));
	}

	withSignMeaning(node, signid){
		return wrapWithMeaning(node, this.showMeaning(), buildMeaningTipByCategory('sign', signid));
	}

	withHouseMeaning(node, houseid){
		return wrapWithMeaning(node, this.showMeaning(), buildMeaningTipByCategory('house', houseid));
	}

	renderTitle(objid){
		const symbol = AstroText.AstroMsg[objid];
		const hasSymbol = !!symbol && symbol !== '{';
		const label = AstroText.AstroTxtMsg[objid] || AstroText.AstroMsgCN[objid] || objid;
		const titleNode = (
			<span>
				{hasSymbol ? <span style={{fontFamily: AstroConst.AstroFont}}>{symbol}</span> : null}
				<span style={{fontFamily: AstroConst.NormalFont}}>{`(${label})`}</span>
			</span>
		);
		return this.withLotMeaning(titleNode, objid);
	}


	genLotsDom(chartObj){
		let doms = [];
		for(let i=0; i<AstroConst.LOTS.length; i++){
			let objid = AstroConst.LOTS[i];
			let obj = AstroHelper.getObject(chartObj, objid);
			if(obj === undefined || obj === null){
				continue;
			}

			let titleSpan = 8;
			let ctSpan = 16;

			let stars = AstroHelper.getStars(chartObj, objid);
			let starsDom = null;
			if(stars){
				starsDom = stars.map((item)=>{
					let stardeg = AstroHelper.splitDegree(item[2])
					return (
						<div key={item[0]}>
							{AstroText.AstroMsg[item[0]]}：
							<Popover content={'误差' + Math.round(item[3]*1000) / 1000} >
							<span>{stardeg[0]}</span>
							<span style={{fontFamily: AstroConst.AstroFont}}>{AstroText.AstroMsg[item[1]]}</span>
							<span>{stardeg[1]+"'"}</span>
							</Popover>
						</div>
					);
				});
			}

			let signdeg = AstroHelper.splitDegree(obj.signlon);
			let dom = (
				<Row key={objid}>
					<Col span={24}>
						<Card title={this.renderTitle(objid)} 
							bordered={true} 
							style={{
								background: AstroConst.AstroColor.Backgroud
							}}>
							<Row gutter={12}>
								<Col span={titleSpan}>落座</Col>
								<Col span={ctSpan} style={{fontFamily: AstroConst.NormalFont}}>
										<div>
											<span>{signdeg[0] + 'º'}</span>
											{this.withSignMeaning((
												<span style={{fontFamily: AstroConst.AstroFont}}>{AstroText.AstroMsg[obj.sign]}</span>
											), obj.sign)}
											<span>{signdeg[1]+"'；"}</span>
											{this.withSignMeaning((
												<span style={{fontFamily: AstroConst.AstroFont}}>位于&nbsp;{AstroHelper.whichTerm(obj.sign, signdeg[0])}&nbsp;界</span>
											), obj.sign)}
										</div>
									</Col>
								</Row>
								<Row gutter={12}>
									<Col span={titleSpan}>落宫</Col>
									<Col span={ctSpan} style={{fontFamily: AstroConst.NormalFont}}>
										{this.withHouseMeaning((
											<span>{AstroText.AstroMsg[obj.house]}</span>
										), obj.house)}
									</Col>
								</Row>
							{
								stars && (
									<Row gutter={12}>
										<Col span={titleSpan}>汇合恒星</Col>
										<Col span={ctSpan} style={{fontFamily: AstroConst.NormalFont}}>
											{starsDom}
										</Col>
									</Row>	
								)
							}
						</Card>
					</Col>
				</Row>

			);
			doms.push(dom);
		}
		return doms;
	}


	render(){
		let chart = this.props.value;
		let dom = this.genLotsDom(chart);

		let height = this.props.height ? this.props.height : '100%';
		let style = {
			height: (height-130) + 'px',
			overflowY:'auto', 
			overflowX:'hidden',
		};

		return (
			<div className={styles.scrollbar} style={style}>
				{dom}
			</div>
		);
	}
}

export default AstroLots;
