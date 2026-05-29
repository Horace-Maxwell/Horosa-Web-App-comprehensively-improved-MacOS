import { Component } from 'react';
import { XQSelect } from '../xq-ui';
import DivinationChartShell from '../divination/DivinationChartShell';
import HoraryJudgment from './HoraryJudgment';

const Option = XQSelect.Option;

// 卜卦问题类别（按宫位/转宫归类）。完整规则库于 M3 接入；此处先用于左栏选择 + 右栏占位。
export const HORARY_CATEGORIES = [
	{ value: 'general', label: '综合 · 能否成事' },
	{ value: 'wealth', label: '财物 · 借贷（二宫）' },
	{ value: 'family', label: '兄弟 · 亲属（三宫）' },
	{ value: 'property', label: '房产 · 田宅（四宫）' },
	{ value: 'pregnancy', label: '子嗣 · 怀孕（五宫）' },
	{ value: 'health', label: '疾病 · 健康（六宫）' },
	{ value: 'marriage', label: '婚姻 · 感情（七宫）' },
	{ value: 'lawsuit', label: '诉讼 · 合伙 · 战争（七宫）' },
	{ value: 'theft', label: '盗窃 · 失物 · 走失（七宫/转宫）' },
	{ value: 'death', label: '死生 · 遗产（八宫）' },
	{ value: 'travel', label: '旅行 · 远行 · 学问（九宫）' },
	{ value: 'career', label: '职位 · 事业（十宫）' },
	{ value: 'hope', label: '愿望 · 朋友（十一宫）' },
	{ value: 'enemy', label: '私敌 · 囚禁（十二宫）' },
];

class HoraryMain extends Component{

	renderLeftExtra({ extra, setExtra }){
		return (
			<div className="horosa-field-block">
				<div className="horosa-field-label">问题类别</div>
				<XQSelect style={{ width: '100%' }} size="small"
					value={extra.questionCategory || 'general'}
					onChange={(val)=>setExtra({ questionCategory: val })}>
					{HORARY_CATEGORIES.map((c)=>(<Option key={c.value} value={c.value}>{c.label}</Option>))}
				</XQSelect>
			</div>
		);
	}

	renderRight({ chart, extra }){
		return <HoraryJudgment chart={chart} category={extra.questionCategory || 'general'} />;
	}

	render(){
		return (
			<DivinationChartShell
				title="卜卦盘"
				kicker="起卦设置"
				pageClass="horosa-horary-page"
				castNowLabel="此刻起卦"
				defaults={{ tradition: 1, zodiacal: 0, hsys: 0 }}
				initialExtra={{ questionCategory: 'general' }}
				fields={this.props.fields}
				height={this.props.height}
				chartDisplay={this.props.chartDisplay}
				planetDisplay={this.props.planetDisplay}
				lotsDisplay={this.props.lotsDisplay}
				showAstroMeaning={this.props.showAstroMeaning}
				dispatch={this.props.dispatch}
				saveModule="horary"
				renderLeftExtra={(args)=>this.renderLeftExtra(args)}
				renderRight={(args)=>this.renderRight(args)}
			/>
		);
	}
}

export default HoraryMain;
