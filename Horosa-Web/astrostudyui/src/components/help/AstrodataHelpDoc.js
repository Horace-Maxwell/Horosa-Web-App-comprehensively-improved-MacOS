// 名人星盘数据库 · 操作手册(帮助页内容组件,「工具 · 数据库」页右上角「帮助」打开)。
// 逐控件写清「怎么用 + 看哪里」;中性表述,纯展示零后端。页面本体为离线内嵌目录(iframe)。
import { Component } from 'react';
import { Tabs } from 'antd';

const { TabPane } = Tabs;
import { MUTED, h, p, ul, li, card, ct, body, title } from './helpDocStyle';

const kv = (k, v) => <div style={{ margin: '1px 0', lineHeight: 1.55 }}><span style={{ color: MUTED }}>{k}：</span>{v}</div>;

class AstrodataHelpDoc extends Component{
	render(){
		return (
			<div style={{ marginTop: 10, borderTop: '1px solid var(--horosa-border, rgba(120,120,120,0.25))', paddingTop: 8 }}>
				<div style={title}>名人星盘数据库 · 操作手册</div>
				<Tabs defaultActiveKey="overview" size="small">
					<TabPane tab="总览" key="overview">
						<div style={body}>
							<p style={p}><b>数据库</b>是一份内置的名人出生资料目录:可按姓名 / 分类 / 星座 / 数据可信度等条件检索名人,查看其出生盘与生平资料,并<b>一键把某人的出生数据加入命盘列表</b>——之后在任一技法页(占星 / 七政 / 紫微 / 八字 …)的「星盘列表」里点选,即按该名人出生资料排盘。</p>
							<div style={h}>怎么用(三步)</div>
							<ul style={ul}>
								<li style={li}><b>检索</b>:顶部搜索框输入姓名或关键词,配合下方筛选(性别 / 出生年 / Rodden 可信度 / 太阳星座 / 分类)缩小范围。</li>
								<li style={li}><b>查看</b>:点结果卡打开详情抽屉——出生黄道星盘轮 + 出生资料 + 数据可信度 + 生平事件与分类标签。</li>
								<li style={li}><b>加入命盘</b>:详情抽屉点「导入为命盘」→ 静默写入你的「星盘列表」(不弹窗、不跳转);到任一技法页选该人即排盘。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>本页全程<b>离线</b>(浏览器内数据库查询,不联网);首次点开该标签需载入约 38MB 数据,之后即时。切换其它标签不卸载。明暗跟随 App 主题。</p>
						</div>
					</TabPane>

					<TabPane tab="检索与筛选" key="search">
						<div style={body}>
							<p style={{ ...p, color: MUTED }}>下列控件在顶部工具区,任改一项即时刷新结果与统计。</p>
							<div style={card}><div style={ct}>关键词搜索</div>
								{kv('搜索框', '输入姓名或关键词(按「/」键可快速聚焦搜索框)')}
								{kv('匹配模式', '包含(子串命中) / 前缀(开头命中) / 精确(整字段相等)')}
								{kv('搜索范围', '全部 / 姓名 / 标题 / 传记(限定关键词在哪些字段里找)')}</div>
							<div style={card}><div style={ct}>条件筛选</div>
								{kv('性别', '全部 / 男 / 女 / 未知')}
								{kv('出生年', '按出生年份过滤')}
								{kv('Rodden 可信度', 'A+AA(最高) / AA / A —— 出生时间数据的来源可信度等级')}
								{kv('太阳星座', '十二星座图标单选,筛出太阳落该星座者')}
								{kv('分类', '分类搜索框 + 分类词条(facet)标签,按人物领域/主题过滤')}
								{kv('清空', '「清空全部」一键复位所有筛选与关键词')}</div>
							<div style={card}><div style={ct}>排序 / 分页 / 统计</div>
								{kv('排序', '相关度 / 姓名 / 生日↑(早→晚) / 生日↓(晚→早)')}
								{kv('每页', '24 / 48 / 96 条;底部上一页 / 下一页 + 跳页输入')}
								{kv('统计条', '当前结果的人物数 / 含 Wikipedia 传记数 / 分类维度')}</div>
							<p style={{ ...p, color: MUTED }}>结果卡上以 ☉☽↑ 三点速览太阳 / 月亮 / 上升星座;点卡片开详情。</p>
						</div>
					</TabPane>

					<TabPane tab="详情与导入" key="detail">
						<div style={body}>
							<div style={h}>详情抽屉</div>
							<div style={card}><div style={ct}>星盘与资料</div>
								{kv('出生星盘轮', '该人出生黄道星盘的 SVG 轮图')}
								{kv('出生资料', 'Rodden 评级 / 数据来源 / 收集者 / 时间精度')}
								{kv('生平', '关系、生平事件、分类标签')}
								{kv('时间未知提示', '出生时间未知者会提示:上升与宫位不可用(仅星体黄经可靠)')}</div>
							<div style={h}>把某人加入命盘</div>
							<ul style={ul}>
								<li style={li}><b>导入为命盘</b>(App 内嵌时):点一下即静默写入「星盘列表」——不弹抽屉、不跳转;到任一技法页点选该名人即排盘。</li>
								<li style={li}><b>复制命盘数据</b>(独立浏览器打开本目录时):按钮改为复制出生数据文本,可粘贴到别处。</li>
							</ul>
							<div style={h}>外部链接</div>
							<p style={p}>原始出处 Astro-Databank 页与 Wikipedia 词条为外链,点击在系统浏览器打开(桌面版已处理 target=_blank 无反应问题)。</p>
						</div>
					</TabPane>

					<TabPane tab="数据与版权" key="meta">
						<div style={body}>
							<div style={h}>Rodden 可信度分级</div>
							<p style={p}>Rodden Rating 是占星界通行的出生时间数据可信度标记:<b>AA</b> 来自出生证明 / 官方记录,<b>A</b> 来自本人或家属陈述,可信度依次递减。本页只收录较高等级(A / AA / A+AA)以保排盘可靠。出生时间未知者,其上升与宫位不参与排盘。</p>
							<div style={h}>离线与载入</div>
							<p style={p}>目录数据打包在应用内,查询全程在本机进行、不联网;首次点开「数据库」标签需解压载入约 38MB,之后检索即时。明暗主题跟随 App。</p>
							<div style={h}>版权说明</div>
							<ul style={ul}>
								<li style={li}>人物出生数据来自 Astro-Databank,供非商业研究使用,保留其 Rodden 评级与来源标注。</li>
								<li style={li}>Wikipedia 传记摘要按 CC BY-SA 4.0 授权。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>本页为查阅 + 导入工具,不改动任何已有命盘;导入只是把出生资料加进你的星盘列表,排盘仍由各技法页完成。</p>
						</div>
					</TabPane>
				</Tabs>
			</div>
		);
	}
}

export default AstrodataHelpDoc;
