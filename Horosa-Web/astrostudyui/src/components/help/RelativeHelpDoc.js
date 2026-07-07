// 合盘 · 操作手册(帮助页内容组件,合盘页右上角「帮助」打开)。
// 覆盖六种关系盘 + 共享左栏(黄道/分宫制/恒星岁差)+ 起盘流程。中性表述,纯展示零后端;盘型名/取值与界面 label 一致。
// 绝不写章节号「§」或来源书名/软件名;专名(Davison / Placidus 等)与界面 label 一致,可用。
import { Component } from 'react';
import { Tabs } from 'antd';
import { MUTED, h, p, ul, li, card, ct, body, title } from './helpDocStyle';

const { TabPane } = Tabs;
const kv = (k, v) => <div style={{ margin: '1px 0', lineHeight: 1.55 }}><span style={{ color: MUTED }}>{k}：</span>{v}</div>;

class RelativeHelpDoc extends Component{
	render(){
		return (
			<div style={{ marginTop: 6, borderTop: '1px solid var(--horosa-border, rgba(120,120,120,0.25))', paddingTop: 8 }}>
				<div style={title}>合盘 · 操作手册</div>
				<Tabs defaultActiveKey="overview" size="small">

					{/* ───────────────────────── 总览 ───────────────────────── */}
					<TabPane tab="总览" key="overview">
						<div style={body}>
							<p style={p}>合盘页用来<b>比较两个人的星盘</b>,分析两人之间的关系。先各选一张星盘,再切到不同的盘型从不同角度看两人的互动、契合与合成关系。</p>
							<div style={h}>起盘三步</div>
							<ul style={ul}>
								<li style={li}><b>选星盘 A</b>:点「星盘A」搜索框,从已存档的盘里挑第一人。</li>
								<li style={li}><b>选星盘 B</b>:同样挑第二人。</li>
								<li style={li}><b>排盘</b>:两张都选好后会自动排;也可点「排盘」手动重排。切换盘型时若两盘已选,会自动重算。</li>
							</ul>
							<div style={h}>布局</div>
							<ul style={ul}>
								<li style={li}><b>上方</b>:星盘A / 星盘B 选择框 + 「排盘」按钮。</li>
								<li style={li}><b>右侧竖排标签</b>:六种盘型 — 比较盘 / 组合盘 / 影响盘 / 时空中点盘 / 马克斯盘 / 关系量化。</li>
								<li style={li}>各盘型内部多设左栏(排盘参数)、中央(盘面)与信息表。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>盘型大致分两类:一类把两人盘<b>叠看</b>(比较盘、影响盘、马克斯盘),另一类把两人盘<b>合成一张</b>(组合盘、时空中点盘);关系量化则只给评分。</p>
						</div>
					</TabPane>

					{/* ───────────────────────── 排盘设置 ───────────────────────── */}
					<TabPane tab="排盘设置" key="input">
						<div style={body}>
							<p style={p}>合盘的<b>黄道、分宫制、恒星岁差</b>是两盘共用的——改任一项,两人盘都按同一口径重算,中央盘随之刷新。</p>
							<div style={card}><div style={ct}>控件归属哪些盘型（重要）</div>
								{kv('有这些控件', '组合盘 / 影响盘 / 时空中点盘 / 马克斯盘——它们的左栏才有黄道、分宫制、恒星岁差、星盘样式等排盘/显示控件')}
								{kv('比较盘无控件', '比较盘(默认打开的第一个盘型)是一张无控件的双圈盘,只呈现两盘叠看,不在此处放黄道/分宫/岁差/样式控件;要改这些口径请在其它盘型的左栏调整')}
								{kv('两盘同步', '在有控件的盘型改了黄道/分宫/岁差,属两盘共用口径,一并按新口径重算')}</div>

								<div style={card}><div style={ct}>流派预设</div>
									{kv('作用', '与本命盘共用同一档预设:一档套齐黄道、分宫、界系、三分体系等;软预设,选后仍可逐项手改')}
									{kv('同步', '改预设两人盘一并按新口径重算')}</div>
							<div style={card}><div style={ct}>黄道</div>
								{kv('取值', '回归黄道 / 恒星黄道(及配套的恒星岁差档)')}
								{kv('作用', '决定行星按回归坐标还是恒星坐标落座;两人同步')}</div>
							<div style={card}><div style={ct}>恒星岁差</div>
								{kv('取值', '选恒星黄道时可选具体岁差档(多种学派任选)')}
								{kv('作用', '恒星黄道下星座起点的具体口径')}</div>
							<div style={card}><div style={ct}>分宫制</div>
								{kv('取值', '常见分宫制列表(Placidus 等)')}
								{kv('作用', '决定十二宫的划分方式;两人同步')}</div>
							<p style={p}>星盘A、星盘B 的<b>出生时间与地点</b>取自各自档案,合盘内不单独修改;若要改某人的出生数据,请回本命盘存档修订后再选回来。</p>
								<p style={{ ...p, color: MUTED }}>在<b>组合盘 / 影响盘 / 时空中点盘 / 马克斯盘</b>里,盘面上方/左栏还有与本命盘同款的显示控件:星盘组件(显示星体)、相位设置(选参与相位)、快捷显示开关(相位线 / 四角 / 度数 / 界限)、星盘样式——这些只改呈现,不改两盘底层数据。<b>比较盘无这些控件</b>(见「比较盘」页)。</p>
						</div>
					</TabPane>

					{/* ───────────────────────── 比较盘 ───────────────────────── */}
					<TabPane tab="比较盘" key="comp">
						<div style={body}>
							<p style={p}><b>比较盘</b>是合盘<b>默认打开的第一个盘型</b>,把两人盘以双圈叠看:一人居内圈、一人居外圈,直观呈现两盘星体彼此的落位与接触,是看两人互动最直接的一张。</p>
							<div style={h}>给出的内容</div>
							<ul style={ul}>
								<li style={li}><b>右栏两个页签:「星盘A」/「星盘B」</b>——分别以 A、B 为内圈视角各出一张双圈盘与其信息,切页签即换主视角。</li>
								<li style={li}>盘内含双向接触(相位、中点、映点/反映点)的连线与标注,双向对照看清「谁触动了谁」。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}><b>比较盘是一张无控件盘</b>:此盘型左栏不放黄道 / 分宫制 / 岁差 / 星盘样式等控件(要改这些口径,去组合盘 / 影响盘 / 时空中点盘 / 马克斯盘的左栏);右栏只有「星盘A / 星盘B」两个双圈页签,不是「相位 / 映点 / 中点」分页。</p>
						</div>
					</TabPane>

					{/* ───────────────────────── 组合盘 ───────────────────────── */}
					<TabPane tab="组合盘" key="composite">
						<div style={body}>
							<p style={p}><b>组合盘(Composite)</b>把两人每颗对应行星取<b>中点</b>,合成出一张代表「这段关系本身」的单盘,看关系作为一个整体呈现什么样貌。</p>
							<div style={h}>给出的内容</div>
							<ul style={ul}>
								<li style={li}>一张合成星盘 + 与本命盘同款的完整信息面板(信息 / 相位 / 行星 / 古典 / 可能性 / 格局 / 埃及)。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>组合盘看的是「关系这个第三者」的性格与走向,而非某一方。</p>
						</div>
					</TabPane>

					{/* ───────────────────────── 影响盘 ───────────────────────── */}
					<TabPane tab="影响盘" key="synastry">
						<div style={body}>
							<p style={p}><b>影响盘</b>以双圈形式把两人盘内外并置(一人在内圈、一人在外圈),直观看两盘星体彼此的相位影响。</p>
							<div style={h}>给出的内容</div>
							<ul style={ul}>
								<li style={li}><b>影响图盘 · 星盘A / 星盘B</b>:内外两圈各自的盘面与信息。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>与比较盘相比,影响盘更偏「整体叠看」的盘面呈现。</p>
						</div>
					</TabPane>

					{/* ───────────────────────── 时空中点盘 ───────────────────────── */}
					<TabPane tab="时空中点盘" key="timespace">
						<div style={body}>
							<p style={p}><b>时空中点盘(Davison)</b>取两人出生<b>时间的正中</b>与<b>地理位置的正中</b>,以这个时空中点真实起一张盘。它和组合盘都代表关系,但时空中点盘是一张「真实存在过的时刻地点」的盘。</p>
							<div style={h}>给出的内容</div>
							<ul style={ul}>
								<li style={li}>一张合成星盘 + 与本命盘同款的完整信息面板(信息 / 相位 / 行星 / 古典 / 可能性 / 格局 / 埃及)。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>组合盘取中点位置、时空中点盘取中点时刻与地点——两者常对照着看。</p>
						</div>
					</TabPane>

					{/* ───────────────────────── 马克斯盘 / 关系量化 ───────────────────────── */}
					<TabPane tab="马克斯盘 · 关系量化" key="marksscore">
						<div style={body}>
							<div style={h}>马克斯盘</div>
							<ul style={ul}>
								<li style={li}>以双圈形式(内圈/外圈)叠看两人盘,呈现另一套关系盘视角。</li>
								<li style={li}>给出内外两圈的盘面与信息。需先选定星盘A、星盘B 才能查看。</li>
							</ul>
							<div style={h}>关系量化</div>
							<ul style={ul}>
								<li style={li}><b>用途</b>:给两人关系打一个整体契合分数,并列出加分/减分的相位依据。</li>
								<li style={li}><b>顺畅连接</b>:和谐相位列表(含双方星体、相位、误差、权重)。</li>
								<li style={li}><b>张力连接</b>:挑战相位列表(同上字段)。</li>
								<li style={li}><b>全部权重相位</b>:纳入计算的所有相位,按权重排序。</li>
								<li style={li}><b>重新计算</b>:手动刷新评分结果。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>评分是把相位按权重汇总的量化参考,宜与各盘型的具体盘面结合判读。</p>
						</div>
					</TabPane>
				</Tabs>
			</div>
		);
	}
}

export default RelativeHelpDoc;
