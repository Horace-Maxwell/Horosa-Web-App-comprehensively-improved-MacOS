// 黄历 · 操作手册(帮助页内容组件,黄历页右上角「帮助」打开)。
// 逐选项写清「怎么用 + 看哪里」;中性表述,纯展示零后端。
import { Component } from 'react';
import { Tabs } from 'antd';

const { TabPane } = Tabs;
import { MUTED, h, p, ul, li, card, ct, body, title } from './helpDocStyle';

const kv = (k, v) => <div style={{ margin: '1px 0', lineHeight: 1.55 }}><span style={{ color: MUTED }}>{k}：</span>{v}</div>;

class CalendarHelpDoc extends Component{
	render(){
		return (
			<div style={{ marginTop: 10, borderTop: '1px solid var(--horosa-border, rgba(120,120,120,0.25))', paddingTop: 8 }}>
				<div style={title}>黄历 · 操作手册</div>
				<Tabs defaultActiveKey="overview" size="small">
					<TabPane tab="总览" key="overview">
						<div style={body}>
							<p style={p}><b>黄历</b>提供整月的农历对照:左侧月历可逐日点选,右侧即时给出该日的农历、干支、纳音、节气与朔望等详细信息。是一份不依赖出生信息的<b>纯查历工具</b>,用于随手核对某日的历法细目。</p>
							<div style={h}>怎么用</div>
							<ul style={ul}>
								<li style={li}>右上时间条切换月份(可逐月前后翻),左侧月历随之刷新。</li>
								<li style={li}>点选某一天 → 右侧展开该日全部历法细目;再点其它日即时切换。</li>
								<li style={li}>右侧若该日所属年份配有奇门年卦,可点「奇门年卦」查看该年卦象图与卦义。</li>
								<li style={li}>左侧月历会同时显示当月与上月衔接的少量日期,便于看月初的过渡。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>本页不需出生信息,也不必专门选地点;默认以通用经度计历,日期/节气/朔望按精确天文时刻给出。</p>
						</div>
					</TabPane>

					<TabPane tab="操作" key="ops">
						<div style={body}>
							<div style={h}>月份切换</div>
							<p style={p}>右上时间条仅按月调整;前后箭头逐月翻动,月历区显示当月及上月衔接日。<b>切月后需重新点选日期</b>——换月会清空当前选中,右侧回到「选择日期」提示,月历高亮随焦点日移动。</p>
							<div style={h}>点选日期</div>
							<p style={p}>点中某日后,右侧出现该日详情;再点其它日即时切换。未选时提示「选择日期查看详细农历、干支与节气信息」。</p>
							<div style={h}>悬停速览</div>
							<p style={p}>鼠标移到月历里任一日格,即弹出小浮窗速览该日:年纳音、四柱干支、节气进退与物候、当日若逢朔 / 望的月相时刻——不必点开也能快速扫读。</p>
							<div style={h}>日格显示规则</div>
							<p style={p}>格内上行公历日、下行农历日;<b>每月初一格改显月名</b>(如「正月」「闰四月」)、<b>交节当日改显节气名</b>,便于一眼定位月首与节气;<b>周末(周六、周日)以红色标示</b>。</p>
							<div style={h}>奇门年卦</div>
							<p style={p}>当所选日所属年份配有奇门年卦时,右侧详情会出现「奇门年卦」链接,点开即在下方展开该年卦象图;卦义说明为外部链接,点击在浏览器新标签打开。</p>
							<p style={{ ...p, color: MUTED }}>月历、详情联动即时刷新,无需手动「确认」;所有信息均为查阅性质,不写入任何排盘。</p>
						</div>
					</TabPane>

					<TabPane tab="右栏看什么" key="right">
						<div style={body}>
							<p style={{ ...p, color: MUTED }}>选中某日后,右侧按下列分块依次列出该日历法细目(无对应数据的行自动省略)。</p>
							<div style={card}><div style={ct}>历法基本</div>
								{kv('公历 / 星期', '所选日的公历日期与星期')}
								{kv('农历', '农历年月日;遇闰月在月名前标「闰」')}
								{kv('年纳音', '该农历年的纳音五行')}</div>
							<div style={card}><div style={ct}>干支(四柱)</div>
								{kv('年 / 月 / 日 / 时干支', '该日四柱干支')}
								{kv('月干支定法', '月干支以当天正午十二点是否已跨节气来决定(节气是月令分界,非初一)')}
								{kv('节气进退', '距最近节气的日数,及对应物候(七十二候)提示')}</div>
							<div style={card}><div style={ct}>节气 / 朔望</div>
								{kv('节气', '当日若交节气,给出节气名称、精确交节时刻,并附该刻的儒略日(jdn)读数')}
								{kv('朔月 / 望月', '农历初一为朔、十五前后为望,给出精确月相时刻并附其儒略日(jdn)读数')}</div>
							<div style={card}><div style={ct}>奇门年卦</div>
								{kv('年卦', '所属年份配有年卦时出现「奇门年卦」链接,点开在下方展开卦象图;卦义说明为外部链接,点击在浏览器新标签打开')}</div>
						</div>
					</TabPane>

					<TabPane tab="历法概念" key="concept">
						<div style={body}>
							<p style={{ ...p, color: MUTED }}>下列是右栏字段背后的通用历法概念,便于看懂各项含义。</p>
							<div style={h}>农历与闰月</div>
							<p style={p}>农历为阴阳合历:月以朔望(月相)为准,年以节气调和回归年。为对齐回归年会置闰,闰月在月名前冠「闰」字(如「闰四月」)。</p>
							<div style={h}>干支与四柱</div>
							<p style={p}>以十天干、十二地支两两相配得六十甲子,循环纪年、月、日、时。年月日时各取一组干支即为「四柱」。</p>
							<div style={h}>节气与月令</div>
							<p style={p}>二十四节气把太阳黄经按 15° 均分,既是农时节点,也是干支历的月令分界——故月干支按是否已交节气定,而非按农历初一。本页对每日标注距节气的进退与物候。</p>
							<div style={h}>纳音</div>
							<p style={p}>六十甲子按古法配五行,称纳音(如「海中金」「炉中火」)。本页给出年纳音,逐柱纳音可在右栏干支区对照。</p>
							<div style={h}>朔望</div>
							<p style={p}>朔为日月黄经相同(月初一前后)、望为相对(月十五前后),本页给出该日若逢朔/望的精确月相时刻。</p>
							<p style={{ ...p, color: MUTED }}>以上为通用历法常识;本页所有数据按精确天文算法给出,可作排盘前的历法核对底册。</p>
						</div>
					</TabPane>
				</Tabs>
			</div>
		);
	}
}

export default CalendarHelpDoc;
