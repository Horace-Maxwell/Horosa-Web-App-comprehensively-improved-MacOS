// 分至盘 · 操作手册(帮助页内容组件,分至页右上角「帮助」打开)。
// 覆盖左栏(年份/黄道/分宫制/地点)+ 右栏全部标签(二十四节气 + 四分至各 星盘/宿盘/3D盘)。
// 中性表述,纯展示零后端;选项名/取值与界面 label 一致。绝不写章节号「§」或来源书名/软件名;专名(Placidus 等)与 label 一致,可用。
import { Component } from 'react';
import { Tabs } from 'antd';
import { MUTED, h, p, ul, li, card, ct, body, title } from './helpDocStyle';

const { TabPane } = Tabs;
const kv = (k, v) => <div style={{ margin: '1px 0', lineHeight: 1.55 }}><span style={{ color: MUTED }}>{k}：</span>{v}</div>;

class JieqiHelpDoc extends Component{
	render(){
		return (
			<div style={{ marginTop: 6, borderTop: '1px solid var(--horosa-border, rgba(120,120,120,0.25))', paddingTop: 8 }}>
				<div style={title}>分至盘 · 操作手册</div>
				<Tabs defaultActiveKey="overview" size="small">

					{/* ───────────────────────── 总览 ───────────────────────── */}
					<TabPane tab="总览" key="overview">
						<div style={body}>
							<p style={p}>分至盘以<b>太阳进入二分二至(春分、夏至、秋分、冬至)的精确时刻</b>为某地起盘,用于看一年四季节令的天象格局。先选年份与地点,再切到某一分至,即可查看那一刻的星盘 / 宿盘 / 3D 盘。</p>
							<div style={h}>怎么用</div>
							<ul style={ul}>
								<li style={li}>左栏选<b>年份</b>与<b>地点</b>(并可设黄道、分宫制)。</li>
								<li style={li}>默认进入<b>二十四节气</b>总览卡片;点右侧某一分至的标签即按其入境时刻起盘。</li>
								<li style={li}>每个分至都提供三种盘:<b>星盘 · 宿盘 · 3D 盘</b>。</li>
								<li style={li}>底部「快捷功能」条放页面上没有的动词:<b>二十四节气</b>总览主键、<b>上一年 / 回今年 / 下一年</b>年份翻页、以及当前节气的 <b>星盘 / 宿盘 / 3D 盘</b> 视图切换(不在分至盘标签上时三视图键置灰)。切到某盘会按需计算并缓存。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>分至入境时刻是天文事件,与你所选地点无关;地点只影响该时刻的上升、宫位等落地信息。</p>
							<div style={h}>向 AI 挂载</div>
							<p style={p}>排盘完成后自动向「AI 分析」备好两份快照:<b>整年二十四节气总览</b>与<b>当前所看盘</b>(随你切到哪个分至 / 哪种盘而变),便于在 AI 分析页就分至格局提问。</p>
						</div>
					</TabPane>

					{/* ───────────────────────── 排盘设置 ───────────────────────── */}
					<TabPane tab="排盘设置" key="input">
						<div style={body}>
							<p style={{ ...p, color: MUTED }}>左栏工具条(查看宿盘时会自动隐藏,以免与宿盘自身设置重复)。</p>
							<div style={card}><div style={ct}>年份</div>
								{kv('取值', '只选年份的日期选择器')}
								{kv('默认', '当前年份')}
								{kv('作用', '决定计算哪一年的二十四节气与四分至时刻')}</div>
							<div style={card}><div style={ct}>黄道</div>
								{kv('取值', '回归黄道 / 恒星黄道(恒星黄道下分档选择岁差基准)')}
								{kv('默认', '回归黄道')}
								{kv('作用', '行星按回归还是恒星坐标落座')}</div>
							<div style={card}><div style={ct}>分宫制</div>
								{kv('取值', '常见分宫制列表(Placidus 等)')}
								{kv('默认', '系统默认档')}
								{kv('作用', '决定十二宫的划分方式')}</div>
							<div style={card}><div style={ct}>经纬度选择</div>
								{kv('操作', '点按钮打开地图选择器选地点(城市搜索 / 地图点选)')}
								{kv('附带', '自动推断时区;下方只读显示当前经纬度')}
								{kv('作用', '决定入境时刻在该地的上升、宫位等')}</div>
							<p style={{ ...p, color: MUTED }}>改年份 / 黄道 / 分宫制 / 地点都会触发重新取节气与重排盘。</p>
						</div>
					</TabPane>

					{/* ───────────────────────── 二十四节气 ───────────────────────── */}
					<TabPane tab="二十四节气" key="jieqi24">
						<div style={body}>
							<p style={p}>页面默认标签,以网格卡片列出所选年份的<b>全部二十四节气</b>,作为一年节令的总览。</p>
							<div style={h}>每张卡片</div>
							<ul style={ul}>
								<li style={li}><b>节气名</b>:按节气顺序排列(小寒、大寒、立春、雨水……直到冬至)。</li>
								<li style={li}><b>交节时刻</b>:该节气太阳到达对应黄经的精确日期时间。</li>
								<li style={li}><b>四柱干支</b>:有干支信息时,列出年 / 月 / 日 / 时的干支与纳音(四列对照)。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>二十四节气里的春分、夏至、秋分、冬至四个分至,可在右侧各自的星盘 / 宿盘 / 3D 盘标签深入查看;底部「快捷功能」条也按分至列出全部入口。</p>
						</div>
					</TabPane>

					{/* ───────────────────────── 分至星盘 ───────────────────────── */}
					<TabPane tab="分至星盘" key="charts">
						<div style={body}>
							<p style={p}>春分 / 夏至 / 秋分 / 冬至四个分至,各有一个标准星盘标签,按该分至的入境时刻、在所选地点起盘。</p>
							<div style={h}>盘面与右栏</div>
							<ul style={ul}>
								<li style={li}>采用标准二维星盘;黄道、分宫制、日期已在左栏统一设定,盘内不再单独显示这几项。</li>
								<li style={li}>右栏沿用标准星盘信息面板(行星宫位、相位、释义等),呈现该时刻的格局。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>四张分至盘合看,可观察一年四季的主轴与转折。</p>
						</div>
					</TabPane>

					{/* ───────────────────────── 分至宿盘 ───────────────────────── */}
					<TabPane tab="分至宿盘" key="su28">
						<div style={body}>
							<p style={p}>每个分至另有一个<b>宿盘</b>标签,以二十八宿体系呈现该入境时刻的星曜分布。</p>
							<ul style={ul}>
								<li style={li}>查看宿盘时左栏工具条自动隐藏,改用宿盘自身内嵌的<b>「宿盘设置」</b>面板——含<b>外盘 / 盘型 / 宿法 / 人事十二宫起盘</b>等选项,避免与左栏重复。</li>
								<li style={li}>给出各宫的宿次分布与星曜落点,适合用东方星宿视角解读分至格局。</li>
							</ul>
						</div>
					</TabPane>

					{/* ───────────────────────── 分至3D盘 ───────────────────────── */}
					<TabPane tab="分至3D盘" key="chart3d">
						<div style={body}>
							<p style={p}>每个分至还有一个<b>3D 盘</b>标签,以三维球面方式展示该入境时刻的天象,可旋转、缩放观察。</p>
							<ul style={ul}>
								<li style={li}>黄道、分宫制、日期同样取自左栏统一设定,盘内不单独显示。</li>
								<li style={li}>适合直观感受分至时刻行星在天球上的真实分布。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>星盘 / 宿盘 / 3D 盘是同一入境时刻的三种呈现,可按需切换对照。</p>
						</div>
					</TabPane>
				</Tabs>
			</div>
		);
	}
}

export default JieqiHelpDoc;
