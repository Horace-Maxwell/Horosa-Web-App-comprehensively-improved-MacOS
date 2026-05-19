import { Component } from 'react';
import { Popover } from 'antd';
import Zhu from './Zhu';
import ZhuMing12 from './ZhuMing12';
import { BaZiMsg, BaZiColor } from '../../msg/bazimsg';

class FourZhu extends Component{
	constructor(props) {
		super(props);
		this.state = {};
	}

	getZhuTitle(rec){
		if(!rec){
			return '';
		}
		let zhu = rec.zhu;
		if(zhu === '年' || zhu === '月' || zhu === '日' || zhu === '时'){
			return zhu + '柱';
		}
		if(zhu === '胎'){
			return zhu + '元';
		}
		return zhu ? zhu + '宫' : '';
	}

	getGanzi(rec){
		if(!rec || !rec.stem || !rec.branch){
			return '';
		}
		return `${rec.stem.cell || ''}${rec.branch.cell || ''}`;
	}

	getGong12Text(gong12){
		if(!gong12){
			return '';
		}
		const gan = gong12['干'] && gong12['干'].name ? gong12['干'].name : '';
		const zhi = gong12['支'] && gong12['支'].name ? gong12['支'].name : '';
		return gan || zhi ? `${gan}・${zhi}` : '';
	}

	getRelativeText(item){
		if(!item){
			return '';
		}
		return `${BaZiMsg[item.polar] || ''}${BaZiMsg[item.element] || ''}・${BaZiMsg[item.relative] || item.relative || ''}`;
	}

	getHiddenStemLines(rec){
		const stems = rec && rec.stemInBranch ? rec.stemInBranch : [];
		return stems
			.map((item)=>`${BaZiMsg[item.polar] || ''}${item.cell || ''}${BaZiMsg[item.element] || ''}・${BaZiMsg[item.relative] || item.relative || ''}`)
			.filter(Boolean);
	}

	getPillarDetailRows(rec){
		if(!rec){
			return [];
		}
		const gua = rec.zhiStarGod && rec.zhiStarGod.gua ? rec.zhiStarGod.gua : '';
		return [
			this.getRelativeText(rec.branch),
			...this.getHiddenStemLines(rec),
			rec.xunEmpty ? `旬空・${rec.xunEmpty}` : '',
			rec.ganziPhase ? `干支・${rec.ganziPhase}` : '',
			rec.naying || rec.nayingPhase ? `${rec.naying || ''}${rec.naying && rec.nayingPhase ? '・' : ''}${rec.nayingPhase || ''}` : '',
			gua,
		].filter(Boolean);
	}

	renderPillarDetail(rec, title){
		const rows = this.getPillarDetailRows(rec);
		return (
			<div className="horosa-bazi-pillar-detail-card">
				<div className="horosa-bazi-pillar-detail-title">{title}细信息</div>
				{rows.map((row, idx)=>(
					<div className="horosa-bazi-pillar-detail-row" key={`${title}-${idx}`}>{row}</div>
				))}
			</div>
		);
	}

	getElementColor(item){
		if(!item){
			return undefined;
		}
		const fallback = BaZiColor[item.polar + item.element] || BaZiColor[item.element];
		const colorMap = {
			Wood: 'var(--horosa-bazi-wood, #2f9b55)',
			Fire: 'var(--horosa-bazi-fire, #d9362a)',
			Earth: 'var(--horosa-bazi-earth, #9a6a2d)',
			Metal: 'var(--horosa-bazi-metal, #b8893f)',
			Water: 'var(--horosa-bazi-water, #2f6df6)',
		};
		return colorMap[item.element] || fallback;
	}

	renderPillar(rec, gong12, isDayMaster){
		const stemColor = rec && rec.stem ? this.getElementColor(rec.stem) : undefined;
		const branchColor = rec && rec.branch ? this.getElementColor(rec.branch) : undefined;
		const title = this.getZhuTitle(rec);
		const gong12Text = this.getGong12Text(gong12);
		const stemText = this.getRelativeText(rec && rec.stem);
		const branchText = this.getRelativeText(rec && rec.branch);
		const hiddenStemLines = this.getHiddenStemLines(rec);
		const hiddenStemText = hiddenStemLines.join(' / ');
		const detailRows = this.getPillarDetailRows(rec);
		const detailPreview = detailRows.slice(0, 2);
		const detailContent = this.renderPillarDetail(rec, title);

		return (
			<div className={`horosa-bazi-pillar-card horosa-bazi-core-pillar-card ${isDayMaster ? 'horosa-bazi-day-master-card' : ''}`}>
				<div className="horosa-bazi-pillar-title">{title}</div>
				<div className="horosa-bazi-pillar-meta">
					<span>{gong12Text}</span>
					<span>{stemText}</span>
				</div>
				<div className="horosa-bazi-core-glyphs" aria-label={`${title}${this.getGanzi(rec)}`}>
					<span style={{color: stemColor}}>{rec && rec.stem ? rec.stem.cell : ''}</span>
					<span style={{color: branchColor}}>{rec && rec.branch ? rec.branch.cell : ''}</span>
				</div>
				<Popover
					trigger={['hover', 'click']}
					placement="top"
					overlayClassName="horosa-bazi-detail-popover horosa-bazi-pillar-info-popover"
					content={detailContent}
				>
					<button className="horosa-bazi-pillar-foot" type="button" aria-label={`${title}细信息`}>
						{detailPreview.map((item, idx)=><span key={`${title}-preview-${idx}`}>{item}</span>)}
						{detailPreview.length === 0 && <span>&nbsp;</span>}
						<em>细信息</em>
					</button>
				</Popover>
			</div>
		);
	}

	renderCompactZhu(rec, gong12){
		const title = this.getZhuTitle(rec);
		const ganzi = this.getGanzi(rec);
		const content = (
			<div className="horosa-bazi-detail-card">
				<Zhu value={rec} baziOpt={this.props.baziOpt} gong12={gong12} />
			</div>
		);

		return (
			<Popover
				trigger="hover"
				placement="top"
				overlayClassName="horosa-bazi-detail-popover"
				content={content}
			>
				<button className="horosa-bazi-aux-chip" type="button">
					<span>{title}</span>
					<strong>{ganzi}</strong>
				</button>
			</Popover>
		);
	}

	renderCompactMing12(rec){
		const zhi = rec && rec.zhi ? rec.zhi : '';
		const content = (
			<div className="horosa-bazi-detail-card">
				<ZhuMing12 value={rec} />
			</div>
		);

		return (
			<Popover
				trigger="hover"
				placement="top"
				overlayClassName="horosa-bazi-detail-popover"
				content={content}
			>
				<button className="horosa-bazi-aux-chip" type="button">
					<span>串宫</span>
					<strong>{zhi}</strong>
				</button>
			</Popover>
		);
	}

	render(){
		let rec = this.props.value ? this.props.value : {};
		let gong12 = this.props.gong12God ? this.props.gong12God : {};

		return (
			<div className="horosa-bazi-four-pillars">
				<div className="horosa-bazi-core-grid">
					{this.renderPillar(rec.year, gong12['年'])}
					{this.renderPillar(rec.month, gong12['月'])}
					{this.renderPillar(rec.day, gong12['日'], true)}
					{this.renderPillar(rec.time, gong12['时'])}
				</div>
				<div className="horosa-bazi-aux-grid">
					{this.renderCompactZhu(rec.tai, gong12['胎'])}
					{this.renderCompactZhu(rec.ming, gong12['命'])}
					{this.renderCompactZhu(rec.shen, gong12['身'])}
					{this.renderCompactMing12(rec.ming12)}
				</div>
			</div>
		);
	}
}

export default FourZhu;
