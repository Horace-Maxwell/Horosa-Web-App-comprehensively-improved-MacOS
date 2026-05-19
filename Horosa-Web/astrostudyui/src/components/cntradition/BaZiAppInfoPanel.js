import { Component } from 'react';
import { BaZiMsg } from '../../msg/bazimsg';

const PILLAR_KEYS = [
	['year', '年柱'],
	['month', '月柱'],
	['day', '日柱'],
	['time', '时柱'],
];

function getGanzi(item){
	if(!item){
		return '';
	}
	return item.ganzi || item.ganZhi || `${item.stem && item.stem.cell ? item.stem.cell : ''}${item.branch && item.branch.cell ? item.branch.cell : ''}`;
}

function hiddenText(item){
	const stems = item && Array.isArray(item.stemInBranch) ? item.stemInBranch : [];
	return stems.map((stem)=>`${stem.cell || ''}${stem.relative || ''}`).filter(Boolean).join(' ');
}

function collectGods(item){
	if(!item){
		return [];
	}
	const gods = [];
	if(Array.isArray(item.shenSha)){
		gods.push(...item.shenSha);
	}
	if(Array.isArray(item.goodGods)){
		gods.push(...item.goodGods);
	}
	if(Array.isArray(item.neutralGods)){
		gods.push(...item.neutralGods);
	}
	if(Array.isArray(item.badGods)){
		gods.push(...item.badGods);
	}
	return Array.from(new Set(gods.filter(Boolean)));
}

function infoPair(label, value){
	if(value === undefined || value === null || value === ''){
		return null;
	}
	return (
		<div className="horosa-bazi-info-pair" key={label}>
			<span>{label}</span>
			<strong>{value}</strong>
		</div>
	);
}

class BaZiAppInfoPanel extends Component{
	renderBasic(bazi, fields){
		const nongli = bazi.nongli || {};
		const name = fields && fields.name ? fields.name.value : '';
		const gender = BaZiMsg[bazi.gender] || '';
		const lunarText = nongli.year ? `${nongli.year}年${nongli.leap ? '闰' : ''}${nongli.month || ''}${nongli.day || ''}` : '';
		return (
			<section className="horosa-bazi-info-card horosa-bazi-info-card-hero">
				<div className="horosa-bazi-info-name">{name || '无名氏'}{gender ? `（${gender}）` : ''}</div>
				<div className="horosa-bazi-info-grid">
					{infoPair('阳历', fields && fields.date && fields.time ? `${fields.date.value.format('YYYY-MM-DD')} ${fields.time.value.format('HH:mm')}` : '')}
					{infoPair('阴历', lunarText)}
					{infoPair('真太阳时', nongli.birth)}
					{infoPair('节气', nongli.jiedelta)}
					{infoPair('起运', bazi.directInfo)}
					{infoPair('交运', bazi.directTime)}
				</div>
			</section>
		);
	}

	renderPillars(four){
		return (
			<section className="horosa-bazi-info-card">
				<h3>四柱信息</h3>
				<div className="horosa-bazi-info-table">
					{PILLAR_KEYS.map(([key, label])=>{
						const item = four[key] || {};
						return (
							<div className="horosa-bazi-info-table-row" key={key}>
								<span>{label}</span>
								<strong>{getGanzi(item)}</strong>
								<em>{item.naying || ''}</em>
								<em>{item.xunEmpty ? `空亡 ${item.xunEmpty}` : ''}</em>
							</div>
						);
					})}
				</div>
			</section>
		);
	}

	renderHidden(four){
		return (
			<section className="horosa-bazi-info-card">
				<h3>藏干</h3>
				<div className="horosa-bazi-info-lines">
					{PILLAR_KEYS.map(([key, label])=>(
						<p key={key}><span>{label}</span>{hiddenText(four[key]) || '—'}</p>
					))}
				</div>
			</section>
		);
	}

	renderGods(four){
		return (
			<section className="horosa-bazi-info-card">
				<h3>神煞</h3>
				<div className="horosa-bazi-info-lines">
					{PILLAR_KEYS.map(([key, label])=>{
						const gods = collectGods(four[key]);
						return <p key={key}><span>{label}</span>{gods.length ? gods.join('、') : '—'}</p>;
					})}
				</div>
			</section>
		);
	}

	renderAux(four){
		const aux = [
			['胎元', four.tai],
			['命宫', four.ming],
			['身宫', four.shen],
			['串宫', four.ming12],
		];
		return (
			<section className="horosa-bazi-info-card">
				<h3>三元宫位</h3>
				<div className="horosa-bazi-info-mini-grid">
					{aux.map(([label, item])=>(
						<div key={label}>
							<span>{label}</span>
							<strong>{label === '串宫' ? (item && item.zhi ? item.zhi : '') : getGanzi(item)}</strong>
						</div>
					))}
				</div>
			</section>
		);
	}

	render(){
		const bazi = this.props.value || {};
		const four = bazi.fourColumns || {};
		return (
			<div className="horosa-bazi-app-info-panel">
				{this.renderBasic(bazi, this.props.fields || {})}
				{this.renderPillars(four)}
				{this.renderHidden(four)}
				{this.renderGods(four)}
				{this.renderAux(four)}
			</div>
		);
	}
}

export default BaZiAppInfoPanel;
