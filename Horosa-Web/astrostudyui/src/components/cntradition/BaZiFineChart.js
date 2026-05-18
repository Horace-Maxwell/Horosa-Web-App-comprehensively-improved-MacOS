import { Component } from 'react';
import { BaZiMsg } from '../../msg/bazimsg';

const GAN_HE = [
	['甲', '己', '土'], ['乙', '庚', '金'], ['丙', '辛', '水'], ['丁', '壬', '木'], ['戊', '癸', '火'],
];
const GAN_CHONG = [
	['甲', '庚'], ['乙', '辛'], ['丙', '壬'], ['丁', '癸'],
];
const ZHI_LIUHE = [
	['子', '丑', '土'], ['寅', '亥', '木'], ['卯', '戌', '火'], ['辰', '酉', '金'], ['巳', '申', '水'], ['午', '未', '土'],
];
const ZHI_CHONG = [
	['子', '午'], ['丑', '未'], ['寅', '申'], ['卯', '酉'], ['辰', '戌'], ['巳', '亥'],
];
const ZHI_SANHE = [
	[['申', '子', '辰'], '水'], [['亥', '卯', '未'], '木'], [['寅', '午', '戌'], '火'], [['巳', '酉', '丑'], '金'],
];
const ZHI_SANHUI = [
	[['寅', '卯', '辰'], '木'], [['巳', '午', '未'], '火'], [['申', '酉', '戌'], '金'], [['亥', '子', '丑'], '水'],
];

function shortRel(item){
	if(!item){
		return '';
	}
	if(item.relative === '日元'){
		return '日元';
	}
	return BaZiMsg[item.relative] || item.relative || '';
}

function hiddenStemText(rec){
	const stems = rec && rec.stemInBranch ? rec.stemInBranch : [];
	return stems.map((item)=>`${item.cell || ''}${item.relative || ''}`).filter(Boolean);
}

function elementClass(label){
	const map = {
		木: 'wood',
		火: 'fire',
		土: 'earth',
		金: 'metal',
		水: 'water',
		冲: 'clash',
		刑: 'clash',
		害: 'clash',
		破: 'clash',
	};
	return map[label] || 'neutral';
}

function makeColumn(title, rec, kind){
	const item = rec || {};
	return {
		title,
		kind,
		rec: item,
		stem: item.stem && item.stem.cell ? item.stem.cell : '',
		branch: item.branch && item.branch.cell ? item.branch.cell : '',
		stemRel: shortRel(item.stem),
		hidden: hiddenStemText(item),
		naying: item.naying || '',
		nayingPhase: item.nayingPhase || '',
		ganziPhase: item.ganziPhase || '',
		xunEmpty: item.xunEmpty || '',
	};
}

function getCurrentDirection(rec){
	const dirs = rec && Array.isArray(rec.direction) ? rec.direction : [];
	const nowYear = new Date().getFullYear();
	let selected = null;
	for(let i=0; i<dirs.length; i++){
		const block = dirs[i] || {};
		const start = Number(block.startYear);
		const subs = Array.isArray(block.subDirect) ? block.subDirect : [];
		if(Number.isFinite(start) && subs.length && nowYear >= start && nowYear < start + subs.length){
			selected = {
				block,
				sub: subs[nowYear - start],
			};
			break;
		}
	}
	if(!selected && dirs.length){
		const block = dirs[0] || {};
		const subs = Array.isArray(block.subDirect) ? block.subDirect : [];
		selected = {
			block,
			sub: subs[0],
		};
	}
	return selected || {};
}

function relationKey(start, end, label, type){
	return `${type}-${start}-${end}-${label}`;
}

function pairRelations(values, pairs, type, relationLabel){
	const rels = [];
	for(let i=0; i<values.length; i++){
		for(let j=i + 1; j<values.length; j++){
			const a = values[i];
			const b = values[j];
			if(!a || !b){
				continue;
			}
			for(let k=0; k<pairs.length; k++){
				const pair = pairs[k];
				if(pair.indexOf(a) >= 0 && pair.indexOf(b) >= 0){
					const label = relationLabel || pair[2] || '';
					rels.push({
						key: relationKey(i, j, label, type),
						start: i,
						end: j,
						label,
						type,
					});
				}
			}
		}
	}
	return rels;
}

function groupRelations(values, groups, type){
	const rels = [];
	groups.forEach((group)=>{
		const branches = group[0];
		const label = group[1];
		const idxs = branches.map((branch)=>values.indexOf(branch)).filter((idx)=>idx >= 0);
		if(idxs.length === branches.length){
			const start = Math.min(...idxs);
			const end = Math.max(...idxs);
			rels.push({
				key: relationKey(start, end, label, type),
				start,
				end,
				label,
				type,
			});
		}
	});
	return rels;
}

function compactRelations(rels, limit){
	const seen = new Set();
	return rels
		.filter((item)=>{
			if(seen.has(item.key)){
				return false;
			}
			seen.add(item.key);
			return true;
		})
		.sort((a, b)=>(b.end - b.start) - (a.end - a.start))
		.slice(0, limit);
}

class BaZiFineChart extends Component{
	buildColumns(){
		const rec = this.props.value || {};
		const four = rec.fourColumns || {};
		const current = getCurrentDirection(rec);
		return [
			makeColumn('流年', current.sub, 'flow'),
			makeColumn('大运', current.block ? current.block.mainDirect : null, 'luck'),
			makeColumn('年柱', four.year, 'natal'),
			makeColumn('月柱', four.month, 'natal'),
			makeColumn('日柱', four.day, 'day'),
			makeColumn('时柱', four.time, 'natal'),
		];
	}

	buildStemRelations(cols){
		const values = cols.map((item)=>item.stem);
		return compactRelations([
			...pairRelations(values, GAN_HE, 'stem-he'),
			...pairRelations(values, GAN_CHONG, 'stem-chong', '冲'),
		], 4);
	}

	buildBranchRelations(cols){
		const values = cols.map((item)=>item.branch);
		return compactRelations([
			...groupRelations(values, ZHI_SANHE, 'branch-sanhe'),
			...groupRelations(values, ZHI_SANHUI, 'branch-sanhui'),
			...pairRelations(values, ZHI_LIUHE, 'branch-liuhe'),
			...pairRelations(values, ZHI_CHONG, 'branch-chong', '冲'),
		], 5);
	}

	getElementColor(rec){
		const element = rec && rec.element;
		const map = {
			Wood: 'var(--horosa-bazi-wood)',
			Fire: 'var(--horosa-bazi-fire)',
			Earth: 'var(--horosa-bazi-earth)',
			Metal: 'var(--horosa-bazi-metal)',
			Water: 'var(--horosa-bazi-water)',
		};
		return map[element] || undefined;
	}

	renderHeader(cols){
		return (
			<div className="horosa-bazi-fine-row horosa-bazi-fine-header">
				<div className="horosa-bazi-fine-label" />
				{cols.map((item, idx)=>(
					<div className={`horosa-bazi-fine-cell ${idx === 2 ? 'horosa-bazi-fine-natal-start' : ''}`} key={item.title}>{item.title}</div>
				))}
			</div>
		);
	}

	renderSimpleRow(label, cols, getter, className){
		return (
			<div className={`horosa-bazi-fine-row ${className || ''}`}>
				<div className="horosa-bazi-fine-label">{label}</div>
				{cols.map((item, idx)=>(
					<div className={`horosa-bazi-fine-cell ${idx === 2 ? 'horosa-bazi-fine-natal-start' : ''}`} key={`${label}-${idx}`}>
						{getter(item, idx)}
					</div>
				))}
			</div>
		);
	}

	renderRelationLayer(rels, className){
		return (
			<div className={`horosa-bazi-fine-row horosa-bazi-fine-relation-row ${className || ''}`}>
				<div className="horosa-bazi-fine-label" />
				<div className="horosa-bazi-fine-relation-grid">
					{rels.map((item)=>(
						<div
							className={`horosa-bazi-fine-relation horosa-bazi-fine-relation-${elementClass(item.label)}`}
							style={{ gridColumn: `${item.start + 1} / ${item.end + 2}` }}
							key={item.key}
						>
							<span>{item.label}</span>
						</div>
					))}
				</div>
			</div>
		);
	}

	renderHiddenRow(cols){
		return (
			<div className="horosa-bazi-fine-row horosa-bazi-fine-hidden-row">
				<div className="horosa-bazi-fine-label">藏干</div>
				{cols.map((item, idx)=>(
					<div className={`horosa-bazi-fine-cell ${idx === 2 ? 'horosa-bazi-fine-natal-start' : ''}`} key={`hidden-${idx}`}>
						{item.hidden.map((txt, subIdx)=>(
							<span key={`${txt}-${subIdx}`}>{txt}</span>
						))}
					</div>
				))}
			</div>
		);
	}

	render(){
		const cols = this.buildColumns();
		const stemRelations = this.buildStemRelations(cols);
		const branchRelations = this.buildBranchRelations(cols);
		return (
			<div className="horosa-bazi-fine-chart">
				{this.renderHeader(cols)}
				{this.renderSimpleRow('主星', cols, (item)=><strong>{item.stemRel}</strong>, 'horosa-bazi-fine-main-star-row')}
				{this.renderRelationLayer(stemRelations, 'horosa-bazi-fine-stem-relations')}
				{this.renderSimpleRow('天干', cols, (item)=>(
					<span className="horosa-bazi-fine-glyph" style={{ color: this.getElementColor(item.rec.stem) }}>{item.stem}</span>
				), 'horosa-bazi-fine-stem-row')}
				{this.renderSimpleRow('地支', cols, (item)=>(
					<span className="horosa-bazi-fine-glyph" style={{ color: this.getElementColor(item.rec.branch) }}>{item.branch}</span>
				), 'horosa-bazi-fine-branch-row')}
				{this.renderRelationLayer(branchRelations, 'horosa-bazi-fine-branch-relations')}
				{this.renderHiddenRow(cols)}
				{this.renderSimpleRow('纳音', cols, (item)=><strong>{item.naying}</strong>, 'horosa-bazi-fine-info-row')}
				{this.renderSimpleRow('星运', cols, (item)=><strong>{item.nayingPhase}</strong>, 'horosa-bazi-fine-info-row')}
				{this.renderSimpleRow('自坐', cols, (item)=><strong>{item.ganziPhase}</strong>, 'horosa-bazi-fine-info-row')}
				{this.renderSimpleRow('空亡', cols, (item)=><strong>{item.xunEmpty}</strong>, 'horosa-bazi-fine-info-row')}
			</div>
		);
	}
}

export default BaZiFineChart;
