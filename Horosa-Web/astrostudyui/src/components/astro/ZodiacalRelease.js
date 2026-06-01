import { Component } from 'react';
import { Tree, } from 'antd';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import { randomStr, } from '../../utils/helper';
import styles from '../../css/styles.less';

const { TreeNode } = Tree;

class ZodiacalRelease extends Component{
	constructor(props) {
		super(props);
		this.colors = [
			'var(--horosa-direction-level-1, #275fc7)',
			'var(--horosa-direction-level-2, #c72d22)',
			'var(--horosa-direction-level-3, #237a45)',
			'var(--horosa-direction-level-4, #805526)',
		];
		this.bgColors = [
			'var(--horosa-direction-node-highlight, rgba(184, 137, 63, 0.14))',
			'var(--horosa-direction-node-highlight, rgba(184, 137, 63, 0.14))',
			'var(--horosa-direction-node-highlight, rgba(184, 137, 63, 0.14))',
		];

		this.genZRSubLevelDom = this.genZRSubLevelDom.bind(this);
	}

	genZRSubLevelDom(list, parentSignIdx){
		let cnt = 0;
		let spans = list.map((item, idx)=>{
			let subdom = null;
			let sigIdx = AstroConst.LIST_SIGNS.indexOf(item.sign);
			if(item.sublevel && item.sublevel.length){
				subdom = this.genZRSubLevelDom(item.sublevel, sigIdx);
			}

			let divstyle = {};
			if(item.level === 1){
				divstyle = {
					color: this.colors[item.level - 1],
				};
			}else if(((sigIdx + 6) % 12) === parentSignIdx){
				cnt = cnt + 1;
				divstyle = {
					color: this.colors[item.level - 1],
				};
				if(cnt === 2){
					divstyle = {
						color: this.colors[item.level - 1],
						background: this.bgColors[item.level - 2],
					};	
				}
			}

			let titledom = (
				<div style={divstyle}>
					<span style={{fontFamily: AstroConst.NormalFont}}>{'L' + item.level}&nbsp;</span>
					<span style={{fontFamily: AstroConst.AstroFont}}>{AstroText.AstroMsg[item.sign]}&nbsp;</span>
					<span style={{fontFamily: AstroConst.NormalFont}}>{item.date}&nbsp;</span>
				</div>
			);

			return (
				<TreeNode key={randomStr(8)} title={titledom}>
					{subdom}
				</TreeNode>
			);
		});

		return spans;
	}


	render(){
		let height = this.props.height ? this.props.height : '100%';
		let mainCont = document.getElementById('mainContent');
		if(mainCont){
			height = mainCont.clientHeight;
		}
		if(height === '100%'){
			height = 'calc(100% - 70px)'
		}else{
			height = height - 100
		}
		let style = {
			height: height,
			overflowY:'auto', 
			overflowX:'hidden',
		};

		let dom = null;
		if(this.props.value){
			dom = this.genZRSubLevelDom(this.props.value, -1);
		}
		return (
			<div className={`${styles.scrollbar} horosa-direction-tree-scroll horosa-zodiacal-release-tree-scroll`} style={style}>
				<Tree className="horosa-direction-tree horosa-zodiacal-release-tree">
					{dom}
				</Tree>
			</div>
		);
	}
}

export default ZodiacalRelease
