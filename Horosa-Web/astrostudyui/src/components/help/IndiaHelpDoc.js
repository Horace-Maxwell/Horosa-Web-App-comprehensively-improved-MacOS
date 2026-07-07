// 印度占星 / 吠陀 · 操作手册（帮助页内容组件，印占页右上角「帮助」打开）。
// 穷举式讲透左栏全部输入/设置选项（取值/含义/区别/默认）+ 右栏每个 tab 的每张卡；中性表述，纯展示零后端。
// 共享样式见 helpDocStyle；kv 行本组件自渲染（避免 JSX 进 .js 样式文件）。绝不写章节号或来源书名/软件名。
import { Component } from 'react';
import { Tabs } from 'antd';
import { MUTED, h, p, ul, li, card, ct, body, title } from './helpDocStyle';

const { TabPane } = Tabs;
const kv = (k, v) => <div style={{ margin: '1px 0', lineHeight: 1.55 }}><span style={{ color: MUTED }}>{k}：</span>{v}</div>;

class IndiaHelpDoc extends Component {
	render() {
		return (
			<div style={{ marginTop: 10, borderTop: '1px solid var(--horosa-border, rgba(120,120,120,0.25))', paddingTop: 8 }}>
				<div style={title}>印度占星 · 操作手册</div>
				<Tabs defaultActiveKey="overview" size="small">

					{/* ============================== 总览 ============================== */}
					<TabPane tab="总览" key="overview">
						<div style={body}>
							<p style={p}>左栏填<b>出生时间 + 地点</b>，系统据此立<b>恒星黄道（Sidereal）</b>本命盘：布七政与罗计、安二十七星宿与十二宫、按规则细分十六张分盘；右栏十三个标签分别查看分盘、五支、大运、星曜状态、八分点、KP、格局、副星、映象、行运、年度、化解、敌友。</p>
							<div style={h}>印占与西占的根本差别</div>
							<ul style={ul}>
								<li style={li}>印占用<b>恒星黄道</b>（扣除岁差，星座钉在真实星空背景），西占多用<b>回归黄道</b>（春分点起算）。同一行星的黄经，两者一般相差约 24 度——这个差值就是「岁差量 Ayanāṃśa」。</li>
								<li style={li}>印占以<b>月亮</b>为重（大运起于月宿、五支以月相为骨），西占以太阳为重。</li>
								<li style={li}>印占特有的<b>星宿 Nakshatra</b>（27 宿）与<b>分盘 Varga</b>（16 衍生盘）两套体系，是其断事的核心抓手，西占没有对应物。</li>
							</ul>
							<div style={h}>核心三层坐标</div>
							<ul style={ul}>
								<li style={li}><b>星座 Rashi</b>：黄道 30 度等分十二宫，定大局与宫位归属。</li>
								<li style={li}><b>星宿 Nakshatra</b>：黄道二十七等分，每宿 13°20′，又各分四脚 Pada（每脚 3°20′）。宿主行星决定大运次序。</li>
								<li style={li}><b>分盘 Varga</b>：把每宫再按 N 等分映射到一张新盘（D2…D60），专审某一人生领域。</li>
							</ul>
							<div style={h}>操作要点</div>
							<ul style={ul}>
								<li style={li}>左栏「流派」是<b>软预设</b>：切派会带出该派常用的岁差、分宫、相位范式与右栏可见标签子集，但每一项仍可单独覆盖。</li>
								<li style={li}>切任一会改盘的设置（流派 / 岁差 / 分宫 / 交点 / 起运点 / 过运日期 / 年度盘年份）→ <b>实时全盘重算</b>（盘面 + 右栏各面板 + AI 挂载）。</li>
								<li style={li}>「星体」「显示方向」「完整度数」「第1宫参照」「盘式」属<b>纯显示层</b>，不改黄经、不重新起盘，切换即时生效不发请求。</li>
							</ul>
							<div style={h}>中栏交互:点星高亮相映宫</div>
							<ul style={ul}>
								<li style={li}><b>点盘中任一行星</b>→ 盘上高亮该曜按当前相位范式(七政相映 / 星座相映…)所照射的宫位;<b>再点同一星</b>取消高亮,<b>点另一星</b>切换到那颗星。纯高亮显示,不改盘、不重算。</li>
							</ul>
						</div>
					</TabPane>

					{/* ============================== 排盘设置 ============================== */}
					<TabPane tab="排盘设置" key="setup">
						<div style={body}>
							<p style={{ ...p, color: MUTED }}>左栏「选项」区每一项：取值 / 含义 / 默认 / 区别。会改盘的在前，纯显示的在后。</p>

							<div style={card}><div style={ct}>流派（学派）</div>
								{kv('取值', 'Parāśarī 帕拉萨拉（默认）/ Jaimini 贾米尼 / Tājika 塔吉卡（年盘）/ KP 系统 / Nāḍī 纳迪')}
								{kv('作用', '一键套该派常用配置（岁差 + 分宫 + 中栏相位范式 + 右栏可见标签子集），软联动可再逐项覆盖')}
								{kv('Parāśarī', '最通用、全功能：七政相映、十六分盘、Shadbala 六力、大运体系齐备。默认即此派，零行为差异')}
								{kv('Jaimini', '重映象与星座大运：用星座相映（Rashi Drishti）、Chara Karaka 指示星、Arudha 映象宫、座位大运。可见标签精简到分盘/五支/大运/Yoga/映象/敌友')}
								{kv('Tājika', '年度盘体系：以太阳回归年盘（Varshaphal）逐年论运，重年度合相与 Saham 敏感点。岁差默认 Lahiri')}
								{kv('KP', '细分宫主与真分宫：默认 Krishnamurti 岁差 + Placidus 真象限分宫，重副主（sub-lord）与意义者。可见标签精简到分盘/大运/八分/KP/行运')}
								{kv('Nāḍī', '宿系断法：重星宿层与纳地盘。可见标签精简到分盘/大运/星曜')}</div>

							<div style={card}><div style={ct}>岁差制（Ayanāṃśa）</div>
								{kv('默认', 'Lahiri / Chitrapaksha（印度官方主流）')}
								{kv('含义', '决定恒星黄道零点位置，即把回归黄经扣除多少岁差。不同岁差制令全盘黄经整体平移，临界度数的行星可能跨座/跨宿/跨脚')}
								{kv('印度主流', 'Lahiri 族（含官定 ICRC 2022、1940、VP285）/ Raman / Krishnamurti(KP) / Yukteshwar / J.N.Bhasin / Usha-Shashi / De Luce 等')}
								{kv('真星·古典', 'True Citra（角宿真星定标）/ True Revati（娄宿）/ True Pushya / True Mula / Surya Siddhanta / Aryabhata 系——以某颗恒星或古历法书为零点锚')}
								{kv('西占恒星', 'Fagan/Bradley / Djwhal Khul / Vettius Valens——西方恒星占星常用')}
								{kv('银道/银心', 'Galactic Center 0°Sag / Galactic Equator(IAU1958/true/mid-Mula) 等——以银河系结构为零点锚')}
								{kv('历史/历元', 'Hipparchos / Sassanian / Babylonian(Kugler/Huber/Britton) / J2000 / J1900 / B1950——天文历元或历史古零点')}
								{kv('提示', '差异最大的是「印度主流」内部各派（Lahiri ↔ Raman ↔ KP 零点相差若干角分），跨大组（如银道）可差数度')}</div>

							<div style={card}><div style={ct}>分宫制（House System）</div>
								{kv('默认', '整宫制 Whole Sign（整座为一宫，吠陀传统主流）')}
								{kv('Vedic 常用', '整宫制 / 等宫·命起宫 Equal / Vehlow 等宫·命居宫中 / Sripati（Bhāva Chalit）/ Porphyry 波菲 / KP·Placidus')}
								{kv('其他象限·等分', 'Koch / Campanus / Regiomontanus / Alcabitus / Morinus / Meridian / Polich-Page / Equal MC / Azimuthal 等多种')}
								{kv('整宫制', '宫界=星座界，一座即一宫，行星所在座即所在宫。吠陀第一选择')}
								{kv('Sripati/Bhāva Chalit', '按度均分的不等宫：宫头 cusp 落在座中而非座界，居星可能因 cusp 重归到相邻宫')}
								{kv('KP·Placidus', '真象限分宫：按上升、天顶分割时间弧。KP 派必用，宫头次主星（CSL）即据此真 cusp 求得')}</div>

							<div style={card}><div style={ct}>交点（罗睺/计都）</div>
								{kv('取值', '平交点（默认）/ 真交点')}
								{kv('平交点', '走匀速平均轨道点，多数古典派沿用，结果平滑稳定')}
								{kv('真交点', '瞬时真实交点，含月球轨道摄动微摆，与平交点可差约 ±1.5 度')}
								{kv('说明', '计都恒为罗睺对冲 180 度，二者永远反向。换交点口径会重算大运（若起运点取节点）与一切节点相关项')}</div>

							<div style={card}><div style={ct}>当前分盘</div>
								{kv('取值', '命盘 D1 + 已算出的各分盘（D2…D60）')}
								{kv('作用', '切换中间主盘当前显示的是本命盘还是某张分盘')}
								{kv('联动', '与右栏「分盘」标签内的分盘按钮联动，选哪张这里就显示哪张；右栏各面板默认随当前显示盘口径计算')}</div>

							<div style={card}><div style={ct}>完整度数（纯显示）</div>
								{kv('取值', '只度数 / 度数+分数')}
								{kv('作用', '盘面行星标注是否带角分。纯显示，不影响计算')}</div>

							<div style={card}><div style={ct}>分盘集（单盘 ↔ 并列 2×2）</div>
								{kv('作用', '从单盘切为同屏对比，最多选 4 张分盘并列成网格')}
								{kv('默认四盘', '命盘 D1 / 合作 D9（婚配核心）/ 事业 D10 / 父辈 D12——印度盘最常对照组')}
								{kv('提示', '每格盘同步当前岁差/分宫/盘式/交点；多盘时盘内字体自动缩小保证完整不裁切')}</div>

							<div style={card}><div style={ct}>盘式（纯显示）</div>
								{kv('取值', '北印 / 南印 / 东印')}
								{kv('南印', '方形固定座位：星座位置固定不动，宫号在格内随上升旋转。十二格沿边排，中央空')}
								{kv('北印', '钻石形固定宫位：宫位格固定不动（第1宫居顶中央三角），座号写在格内随盘转。菱形 + 四角三角')}
								{kv('东印', '另一种方形排布。三者数据同源，仅排版读法不同')}</div>

							<div style={card}><div style={ct}>第1宫参照（重参照 · 纯显示）</div>
								{kv('默认', '上升 Lagna')}
								{kv('七政为第1宫', '把太阳(Sūrya Lagna)/月亮(Chandra Lagna)/水金火木土任一星所在座当第1宫重排宫号，以「月亮盘/太阳盘」视角审视')}
								{kv('虚点为第1宫', '把罗睺或计都所在座当第1宫')}
								{kv('某宫为第1宫', '把第 1–12 宫任一旋转到第1宫位（派生宫/转宫读法）')}
								{kv('作用', '纯显示重参照：只换宫号起点，不改任何行星黄经。中间盘与右栏星曜/宫子表/宫位力等所有宫号统一随之重数，保证一致')}</div>

							<div style={card}><div style={ct}>星体（符号样式 · 纯显示）</div>
								{kv('取值', '文字（Su/Mo… 缩写）/ 符号（占星字形 glyph）')}
								{kv('作用', '盘面行星以缩写文字还是符号呈现。纯显示')}</div>

							<div style={card}><div style={ct}>显示方向（纯显示）</div>
								{kv('取值', '逆时针（默认）/ 顺时针')}
								{kv('作用', '盘面宫位排列方向。南印为固定座位排版，故此项仅对北印/东印显示')}</div>
						</div>
					</TabPane>

					{/* ============================== 岁差与分宫 ============================== */}
					<TabPane tab="岁差·分宫" key="ayan">
						<div style={body}>
							<p style={p}>这两项决定<b>盘的几何底座</b>：岁差制定「星座钉在星空哪儿」，分宫制定「宫界划在哪儿」。换它们会整盘重算，影响行星落座/落宿/落宫，连带所有右栏面板。</p>

							<div style={h}>岁差制 Ayanāṃśa 五大分组速览</div>
							<div style={card}><div style={ct}>印度主流（Lahiri 族）</div>
								{kv('代表', 'Lahiri / Chitrapaksha（官方）')}
								{kv('零点', '以角宿一（Spica/Chitra）约处于天秤 0° 附近为定标思路')}
								{kv('用途', '现代吠陀占星绝大多数实践、印度官方历法、本应用默认')}</div>
							<div style={card}><div style={ct}>真星·古典</div>
								{kv('代表', 'True Citra / True Revati / Surya Siddhanta / Aryabhata')}
								{kv('零点', '严格钉某颗真实恒星（角宿/娄宿等）或采用古历法书的岁差值')}
								{kv('用途', '考据派、还原古典文献口径时用，与 Lahiri 多在角分级差异')}</div>
							<div style={card}><div style={ct}>西占恒星</div>
								{kv('代表', 'Fagan/Bradley')}
								{kv('用途', '西方恒星占星（Sidereal Astrology）标准，与印度派零点略有出入')}</div>
							<div style={card}><div style={ct}>银道 / 银心</div>
								{kv('代表', 'Galactic Center 0°Sag / Galactic Equator')}
								{kv('零点', '以银河系中心或银道面为锚，与黄道派可差数度')}</div>
							<div style={card}><div style={ct}>历史 / 历元</div>
								{kv('代表', 'Babylonian 系 / J2000 / B1950')}
								{kv('用途', '巴比伦古天文复原、或以某天文历元（如 J2000）为零点的研究用途')}</div>

							<div style={h}>分宫制 House System 在印占语境下的意义</div>
							<ul style={ul}>
								<li style={li}><b>整宫制（默认）</b>：一座即一宫，宫界与座界重合。吠陀传统主流，断宫位归属最直接。</li>
								<li style={li}><b>等宫 / Vehlow</b>：从上升起每 30° 一宫（Vehlow 让上升居首宫中点），宫界落在座中。</li>
								<li style={li}><b>Sripati / Bhāva Chalit</b>：按度均分的不等宫，专为「居星到底算哪宫」的精细判读——星虽在某座，若过了下一宫 cusp 即归下一宫。</li>
								<li style={li}><b>KP·Placidus</b>：真象限分宫，按上升天顶切时间弧，宫弧不等。KP 派宫头次主星（CSL）的根基。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>右栏「五支」标签里的「宫子表」会标注当前 cusp 模式（整宫 / 不等宫），并给每宫的真 cusp 度数；选 Śrīpati/Placidus 即看到不等宫界。</p>
						</div>
					</TabPane>

					{/* ============================== 十六分盘 ============================== */}
					<TabPane tab="十六分盘" key="varga">
						<div style={body}>
							<p style={p}><b>分盘（Varga）</b>=把每宫按 N 等分映射出的衍生盘，专审某一人生领域，是吠陀占星核心方法。每张分盘里行星重新落座，读法与本命盘相同，但语境只看对应主题。可单盘看，也可「分盘集」并列 2×2 对比。</p>

							<div style={h}>十六分盘与所主领域</div>
							<div style={card}><div style={ct}>常用主盘</div>
								{kv('D1 Rashi', '命盘——整体、命主本人，一切基底')}
								{kv('D9 Navamsa', '合作·婚姻——最重要的辅盘，复看配偶/福分/行星真实强弱（与 D1 同座=Vargottama 增力）')}
								{kv('D10 Dasamsa', '事业——职业、地位、声望')}
								{kv('D12 Dwadasamsa', '父辈——父母、家世、祖荫')}
								{kv('D7 Saptamsa', '子嗣——子女、生育')}
								{kv('D3 Drekkana', '兄妹——手足、勇气、主动力')}</div>
							<div style={card}><div style={ct}>财产·资质·杂项</div>
								{kv('D2 Hora', '财产——财富、积蓄、物质获取')}
								{kv('D4 Chaturthamsa', '资质·田宅——不动产、母亲、固定资产')}
								{kv('D5 Panchamsa', '世俗——智识、名望、善业')}
								{kv('D6 Shashthamsa', '疾病——病、敌、诉讼')}
								{kv('D8 Ashtamsa', '困难——寿、遗产、隐秘')}
								{kv('D11 Rudramsa', '增长——所得、收益、友辈')}</div>
							<div style={card}><div style={ct}>灵性·精细盘</div>
								{kv('D16 Shodasamsa', '座驾——车马、安乐、动产享受')}
								{kv('D20 Vimsamsa', '灵魂——灵修、宗教精进、解脱')}
								{kv('D24 Chaturvimsamsa', '教育——学问、学习能力')}
								{kv('D27 Nakshatramsa', '生命——体力、宿内强弱、生命力')}
								{kv('D30 Trimsamsa', '厄运——灾病、astro 危机、不吉')}
								{kv('D40 Khavedamsa', '母系——母方福荫、综合善恶')}
								{kv('D45 Akshavedamsa', '父系——父方福荫、品行')}
								{kv('D60 Shashtyamsa', '业力——最精细，前世业、定吉凶细节')}</div>

							<div style={h}>分盘集（左栏 · 并列对比）</div>
							<ul style={ul}>
								<li style={li}>单盘 ↔ 并列 2×2 切换，最多选 4 张同屏排布；常用于 D1+D9+D10+D12 同看。</li>
							</ul>

							<div style={h}>分盘加权与集网格（右栏「星曜」标签内）</div>
							<div style={card}><div style={ct}>分盘吉位 Vimśopaka</div>
								{kv('看什么', '某曜在四组分盘集（六盘/七盘/十盘/十六盘）里，落入自宫/友宫/旺宫的分盘数。越多越吉，会给「吉位名」')}
								{kv('分组', '六盘 Shadvarga（D1/2/3/9/12/30）· 七盘 Saptavarga（加 D7）· 十盘 Dasavarga · 十六盘 Shodasavarga')}</div>
							<div style={card}><div style={ct}>Vimśopaka 20 分力</div>
								{kv('看什么', '四组分盘按行星在每张分盘的尊位（旺/庙/友/中/敌）加权求和，满分 20。越高，该曜跨分盘越强')}
								{kv('阈值', '≥15 显强（绿）/ <7 显弱（橙）')}</div>

							<div style={h}>分盘变体与精细盘（右栏「分盘」标签内）</div>
							<ul style={ul}>
								<li style={li}><b>D60 六十分盘吉凶</b>：每座分 60 段（每段 0.5°），24 段为 Krūra 恶段（凶），余为吉段；列各曜本命落第几段及吉凶，统计吉/凶曜数。</li>
								<li style={li}><b>分盘变体对照</b>：D2/D3/D24/D30 各流派算法（标准 Parāśara 为默认 + Kashinatha/Jagannatha/Somanatha 等变体）下各曜落座差异，仅列有差异的曜。</li>
								<li style={li}><b>Nāḍī · D150 纳地盘</b>：每座分 150 段（每格 0°12′），列各曜 nāḍiāṃśa 号位（Nāḍī 流派用）。</li>
							</ul>
							<p style={{ ...p, color: MUTED }}>所有分盘以本命盘黄经为基底按规则细分，凡改岁差/交点/分宫的设置都会一并重算全部分盘。</p>
						</div>
					</TabPane>

					{/* ============================== 大运体系 ============================== */}
					<TabPane tab="大运体系" key="dasha">
						<div style={body}>
							<p style={p}>大运把一生切成若干由某行星（或星座）掌运的时段，逐层细分定流年应期。右栏「大运」标签内选「体系 + 起点」，时间线可逐级点开钻取。印占大运极丰富，分<b>宿系大运</b>（按星宿主排）、<b>条件大运</b>（满足特定条件才主用）、<b>座位大运</b>（Jaimini，按星座排）三大类。</p>

							<div style={h}>宿系大运（按星宿主排，可选起点）</div>
							<div style={card}><div style={ct}>Vimshottari（默认）</div>
								{kv('周期', '120 年九曜大运（计7·金20·日6·月10·火7·罗18·木16·土19·水17）')}
								{kv('地位', '吠陀通用第一体系，绝大多数实践用它。AI 与摘要默认引用此盘')}</div>
							<div style={card}><div style={ct}>Yogini</div>
								{kv('周期', '36 年八女神（八位 Yoginī 各掌一段）')}</div>
							<div style={card}><div style={ct}>Ashtottari</div>
								{kv('周期', '108 年（Ārdrādi，自参宿起的八曜）')}</div>
							<div style={card}><div style={ct}>Tribhāgī</div>
								{kv('周期', 'Vimśottarī ÷ 3 → 每曜年数三分之一，3 遍 × 40 = 120 年')}</div>

							<div style={h}>条件大运（仅起算条件满足时为「主用」，否则仍列全表备览）</div>
							<div style={card}><div style={ct}>八条件大运</div>
								{kv('Shodashottari', '116 年（昼/黑分 或 夜/白分 条件）')}
								{kv('Dvadashottari', '112 年（命主九分盘落金牛/天秤）')}
								{kv('Panchottari', '105 年（命宫巨蟹 + D12 命亦巨蟹）')}
								{kv('Shatabdika', '100 年（命宫 Vargottama，D1=D9 同座）')}
								{kv('Chaturashiti-sama', '84 年（第10宫主落第10宫）')}
								{kv('Dwisaptati-sama', '72 年（命主落第1或第7宫）')}
								{kv('Shashtihayani', '60 年（太阳落命宫）')}
								{kv('Shattrimsha-sama', '36 年（昼生命落日时/夜生命落月时）')}
								{kv('说明', '面板顶部标注条件是否满足；未满足时仍可看全表，但视为备览不作主断')}</div>

							<div style={h}>座位大运（Jaimini · 按星座推，非按宿）</div>
							<div style={card}><div style={ct}>Chara（耆那派 · 左栏体系下拉可选）</div>
								{kv('方法', '每运是一个星座，从命宫起依序排；座的年数 = 该座数到其主星座的距离。命宫奇座顺行、偶座逆行')}</div>
							<div style={card}><div style={ct}>更多座位大运（右栏「大运」末尾自动附）</div>
								{kv('Narayana', '种子取命/七宫强者，按盘型定 Brahma/Shiva/Vishnu 走法')}
								{kv('Lagna Kendrādi', '角宫→续宫→果宫分组排列')}
								{kv('Sudaśā', '锚定吉祥上升 Sree Lagna，论福运')}
								{kv('Dṛg', '基于座相照（三组四座）')}
								{kv('Śūla / Niryāṇa Śūla', '论凶险与死亡应期（Maraka 杀主）')}
								{kv('Kālachakra', '时轮大运，按月宿×脚分四组推')}
								{kv('Tāra / Sthira / Yogārdha / Maṇḍūka', '均匀座运 / 固定座运（动7固8变9）/ 平均座运 /蛙跳座运')}</div>

							<div style={card}><div style={ct}>Sthira 固定座运 · 起座切换</div>
								{kv('起座', '在 Sthira（固定座运）盘内可切「命宫」或「Brahma」为起座:命宫=从上升所在座起排;Brahma=从盘型定出的 Brahma 座起排(会标出 Brahma 所在星与座)')}
								{kv('作用', '改起座后重排该大运,首运与后续座运随之变;仅影响 Sthira 座运,不动其他体系')}</div>

							<div style={h}>起运点 Seed（右栏「大运」内选 · 仅宿系/条件大运用）</div>
							<div style={card}><div style={ct}>取哪点所在宿起运</div>
								{kv('七政', '月亮（默认·标准）/ 太阳 / 火 / 水 / 木 / 金 / 土')}
								{kv('节点·上升', '罗睺 / 计都 / 上升 Lagna')}
								{kv('特殊上升', 'Bhava Lagna 命运上升 / Hora Lagna 时上升 / Ghati Lagna 漏刻上升 / Sree Lagna 吉祥上升')}
								{kv('副星·虚点', 'Gulika / Maandi / Dhuma / Vyatipata / Parivesha / Indrachapa / Upaketu')}
								{kv('说明', '默认月亮宿即标准 Vimshottari；改起点后端重算全体系大运，出生余额与首运随之变')}</div>

							<div style={h}>五级钻取</div>
							<ul style={ul}>
								<li style={li}><b>大运 Mahā → 小运 Antar → 子运 Pratyantar → 微运 Sūkṣma → 息运 Prāṇa</b>，逐级点开细分（子时长 = 父时长 × 子主年 ÷ 120）。含「今日」的运段金色高亮，面包屑可回溯任意级。微运/息运极短，精确到时:分。</li>
							</ul>

							<div style={h}>大运标签内的辅助盘</div>
							<div style={card}><div style={ct}>附带项（随盘自动展示）</div>
								{kv('Naisargika 自然大运', '七曜固定年龄段（成熟序，合计 120 年）——按生理年龄段论该曜主事')}
								{kv('Āyurdāya 寿命', 'Piṇḍāyu 度式 / Aṁśāyu 九分式 / Nisargāyu 自然寿三法，及 haraṇa 减算（流派选项）。仅寿命基础推算，非定论')}
								{kv('Mūla 大运', 'Lagna Kendrādi Graha，数到本三角座定年，二轮补足 120')}
								{kv('Sudarśana Chakra', '日轮/月轮/升轮三盘合参，每宫 1 太阳年、12 年循环，三轮并读，当前年高亮')}</div>
						</div>
					</TabPane>

					{/* ============================== KP 系统 ============================== */}
					<TabPane tab="KP 系统" key="kp">
						<div style={body}>
							<p style={p}><b>KP（Krishnamurti Paddhati）</b>把黄道做<b>三级细分</b>，靠最细的「副主星」精确定事，是现代印占最精密的应期体系。在左栏「流派」选 KP 会自动套 Krishnamurti 岁差 + Placidus 真分宫；右栏「KP/择时」标签集中展示。</p>

							<div style={h}>三级（细分到六级）划分</div>
							<div style={card}><div style={ct}>星座主 → 星宿主 → 副主</div>
								{kv('星座主 Sign Lord', '行星所在 30° 星座的主星')}
								{kv('星宿主 Star Lord', '所在 13°20′ 星宿的主星（即大运主曜）')}
								{kv('副主 Sub Lord', '把该宿再按九曜大运年数比例分成 9 段，行星落哪段即取那段主星——KP 断事的关键')}
								{kv('再细', '副主之下还可续分 Prati（子副）→ Sookshma → Praana → Deha 共六级')}</div>

							<div style={h}>249 副主体系</div>
							<ul style={ul}>
								<li style={li}>27 宿 × 9 副主 = 243 段，再加 6 处跨 30° 座界的切分 = <b>249 段</b>。每段有唯一的「座主/宿主/副主」组合，KP 查表即据此。</li>
							</ul>

							<div style={h}>右栏「KP/择时」标签内容</div>
							<div style={card}><div style={ct}>各项</div>
								{kv('KP Sublord', '各点（七政/上升等）的星宿主 / 副主 + 所在宿·脚')}
								{kv('KP 六级细分', '每曜的 Nak ⊃ Sub ⊃ Prati ⊃ Sook ⊃ Praana ⊃ Deha 六层链')}
								{kv('宫头次主星 CSL', '十二宫头 cusp 各自的星宿主 / 副主 + cusp 度数（按真分宫求）')}
								{kv('当令星 Ruling Planets', '命主座主 / 命宫宿主 / 月座主 / 月宿主 / 星期主 五元——问时定应期常用')}
								{kv('意义者 Significators', '每曜按四重强弱 A>B>C>D 列其所司之宫（A 最强）')}
								{kv('Praśna 卜卦', '输入 1–249 问数 → 该数对应的问时上升，查 KP249 静态表')}</div>
						</div>
					</TabPane>

					{/* ============================== 六力·格局 ============================== */}
					<TabPane tab="六力·格局" key="strength">
						<div style={body}>
							<p style={p}>评估行星<b>强弱</b>（Shadbala 六力 + 多重 Avastha 状态）与盘面<b>格局</b>（Yoga 组合）。前者在右栏「星曜」「八分」标签，后者在「Yoga」标签。</p>

							<div style={h}>Shadbala 六力（行星强度量化，七政各算）</div>
							<div style={card}><div style={ct}>六个分量（单位 Virupa，60 Virupa = 1 Rupa）</div>
								{kv('Sthāna 位置力', '旺度 + 七分位尊贵 + 奇偶 + 角宫 + 旬，共五子项——靠尊贵地位给力')}
								{kv('Dig 方向力', '各曜在其旺方最强（日火南/木水东/月金北/土西）')}
								{kv('Kāla 时间力', '昼夜 + 月相 + 三分时 + 日主 + 时主 + 年月主 + 至点（赤纬），共多子项——靠出生时辰给力')}
								{kv('Cheshta 运动力', '按速度档给（逆60/留15/缓/速45…）。日月以至点/月相力代之')}
								{kv('Naisargika 自然力', '固定先天值：日60>月>金>木>水>火>土')}
								{kv('Drik 相位力', '受吉相加、凶相减，净值 ÷4')}</div>
							<div style={card}><div style={ct}>怎么看</div>
								{kv('合计', '六分量相加 = 总 Virupa；÷60 = Rupa')}
								{kv('够不够', '各曜有「所需 Rupa」基准（如水7/木6.5/日5），实得 ÷ 所需 ≥1 即「力足」，否则「力弱」')}
								{kv('吉果/凶果', 'Ishta（吉果）/ Kashta（凶果）值——综合旺度与运动力，越高越能显吉/显凶')}
								{kv('展开表', '右栏「八分」标签给 Sthāna/Kāla 各分量逐曜逐列明细表')}</div>

							<div style={h}>行星状态 Avastha（右栏「星曜」标签内随各曜标）</div>
							<div style={card}><div style={ct}>多层状态</div>
								{kv('Baladi 婴老', '婴/童/青/老/死五态——按度数在座内位置')}
								{kv('Jagradadi 觉态', '醒（旺/庙·全力）/ 梦（友/中·中力）/ 睡（敌/弱·微力）')}
								{kv('Deeptadi 情态', '明耀/安住/欢喜/安详/愤激/残损/凶恶/苦恼/困弱九态——情绪质地')}
								{kv('Sayanadi 态', '卧/坐/行/食…十二活动姿态 + 活跃/中等/微弱三档效力')}
								{kv('Lajjitādi', '羞/傲/饥/渴/喜/扰六种可并存特态（如落第5宫合凶=羞）')}
								{kv('其他标记', 'Vargottama（D1=D9 同座增力）/ 逆 R / 燃 Asta（近日燃烧）/ 功能吉凶（Yogakaraka/Maraka/Badhaka）')}</div>

							<div style={h}>Yoga 格局（右栏「Yoga」标签 · 按类归并 + 强中弱评分）</div>
							<div style={card}><div style={ct}>主要类别</div>
								{kv('五大人瑜伽', 'Ruchaka(火)/Bhadra(水)/Hamsa(木)/Malavya(金)/Shasha(土)——某曜居角宫且强，赋予对应禀赋')}
								{kv('王瑜伽 Raja', '角宫主与三方宫主结合——权位、显达')}
								{kv('财富瑜伽 Dhana', '2/5/9/11 财宫主结合——富')}
								{kv('月亮瑜伽', 'Gaja Kesari / Sunapha / Anapha / Durudhara / Kemadruma 等——月之资源与扶助')}
								{kv('太阳瑜伽', 'Budha-Aditya / Vesi / Vosi 等——表达与权威')}
								{kv('逆转王瑜伽 Viparita', 'Harsha/Sarala/Vimala——凶宫主互处凶宫，逆境生机')}
								{kv('交换瑜伽 Parivartana', '两宫主互换星座——绑定的责任与回报')}
								{kv('形态瑜伽 Nabhasa', '按七曜星座分布形态（绳/杵/花环/蛇…）与几何形定命格')}
								{kv('挑战/煞', 'Kuja(火星煞·婚)/Grahana(食)/Kartari(夹击)/Kala Sarpa(蛇煞) 等')}
								{kv('评分', '每格 1–100 分，标强(76+)/中/弱，并给成因证据')}</div>
							<div style={card}><div style={ct}>同标签其他格局</div>
								{kv('Kartari 夹击', '某星/宫被两侧吉星夹（Shubha 吉）或凶星夹（Papa 凶）')}
								{kv('Sudarshana 三盘合参', '以命宫/太阳/月亮分别起第1宫，三盘并看某曜落第几宫')}</div>
						</div>
					</TabPane>

					{/* ============================== 择时·流年 ============================== */}
					<TabPane tab="择时·流年" key="timing">
						<div style={body}>
							<p style={p}>当下与流年层：<b>过运 Gochara</b>（行运标签）、<b>年度盘 Tājika</b>（年度标签）、<b>择时 Muhurta/Choghadia/Hora</b>（KP/择时标签）。</p>

							<div style={h}>行运 Gochara（右栏「行运」标签）</div>
							<div style={card}><div style={ct}>过运日期</div>
								{kv('默认', '今日；可用日期选择器改任一天，按该日重排过运盘')}</div>
							<div style={card}><div style={ct}>土星专题</div>
								{kv('Sade Sati', '土星过运月亮 12/1/2 宫的七年半，分起/峰/落三段')}
								{kv('Kantaka / Ashtama', '土星过月 4/8 宫（Ardhāṣṭama）/ 过月 8 宫的不利期')}</div>
							<div style={card}><div style={ct}>逐曜过运</div>
								{kv('从月 / 从命', '各曜过运到月亮/上升起第几宫，吉位或凶位')}
								{kv('Vedha 遮断', '某吉位被对位星遮断则失效（标「被遮 Vedha」）')}
								{kv('八分点判读', '过运座的 SAV（综合点）≥30 顺 / ≤25 受阻；BAV（该曜自身点）一并标')}</div>

							<div style={h}>年度盘 Tājika / Varshaphal（右栏「年度」标签）</div>
							<div style={card}><div style={ct}>输入与基本</div>
								{kv('年份', '输入年份点「计算」生成该年太阳回归年盘（默认当年）')}
								{kv('要素', '年度上升 / 满岁 / 昼夜生')}</div>
							<div style={card}><div style={ct}>核心项</div>
								{kv('Muntha', '逐年推进的敏感点，所在座、距本命命宫第几宫、年盘第几宫')}
								{kv('年主 Year Lord', '主管该年的行星及取用法、Pancha-Vargeeya 力')}
								{kv('年度合相 Tajaka Yogas', 'Ishkavala/Induvara 等位置格 + 逐对相位（Ithasala 入相 / Eesarpha 出相）+ 高阶 Nakta/Yamaya/Kamboola 传光集光月助')}
								{kv('Tajika 16 瑜伽名录', '塔吉卡专有十六合相格参考')}
								{kv('Sahams 敏感点', '36 个 Saham（财/婚/子/病…各类敏感点）所在座与度数')}
								{kv('Harsha Bala', '年盘喜悦力（满 20）')}
								{kv('Pancha-Vargeeya Bala', '五分量力（界/旺/宫/旬/九分）')}
								{kv('年内大运', 'Mudda（按 Vimshottari 比例缩到一年）/ Patyāyinī（按年命与七政分天）')}</div>

							<div style={h}>民用择时（右栏「KP/择时」标签）</div>
							<div style={card}><div style={ct}>Muhurta 与时段</div>
								{kv('日出日落', '当日真日出/日落时刻')}
								{kv('凶时段', 'Rahu Kalam / Yamaganda / Gulika 三段不利时')}
								{kv('出生须臾', '出生落第几须臾及吉/凶（Abhijit 为大吉）')}
								{kv('Panchaka 五忌', '是否犯五种忌时')}</div>
							<div style={card}><div style={ct}>时段表</div>
								{kv('Hora 行星时', '昼夜各 12 段，日出首段=当日星期主，按 Chaldean 序循环')}
								{kv('Choghadia 民用择时', '昼夜各 8 段；吉:甘露/吉/利/动，凶:病/时/扰')}</div>
						</div>
					</TabPane>

					{/* ============================== 右栏标签总览 ============================== */}
					<TabPane tab="右栏标签" key="tabs">
						<div style={body}>
							<p style={{ ...p, color: MUTED }}>右栏共十三个标签（实际可见数量随所选流派精简，如 KP 派只显其中 5 个）。逐一速查：</p>
							<div style={card}><div style={ct}>1 分盘</div>
								{kv('内容', 'D1 与各分盘切换按钮 + 各分盘的领域要点卡 + D60 吉凶 / 分盘变体对照 / D150 纳地盘')}</div>
							<div style={card}><div style={ct}>2 五支 Panchanga</div>
								{kv('内容', '基本参数 + 宫子表（座/cusp/宫主/居星/Karaka/分类）+ 星座属性参考 + 五支（星期 Vara / 月相 Tithi / 月宿 Nakshatra 含脚 / 日合 Yoga / 半日 Karana）+ 月宿详情 + 大运摘要')}</div>
							<div style={card}><div style={ct}>3 大运 Dasha</div>
								{kv('内容', '体系 + 起点选择 + 五级钻取时间线（今日高亮）+ Naisargika 自然大运 / Āyurdāya 寿命 / Mūla / Sudarśana / 各座位大运')}</div>
							<div style={card}><div style={ct}>4 星曜 Planet State</div>
								{kv('内容', '行星表（经度/顺逆/宫/宿脚/Karaka）+ 分盘吉位 + Vimśopaka 20 分 + Graha 多层状态 + Shadbala + 宫位力 Bhava Bala + 星曜战 + Chara/Sthira Karaka + Graha Drishti 七政相照')}</div>
							<div style={card}><div style={ct}>5 八分 Ashtakavarga</div>
								{kv('内容', 'Sarva 综合点（SAV 和=337）+ Bhinna 各曜 12宫×7曜矩阵 + Sodhana 缩减（Trikona+Ekadhipatya）+ Sodhya Pinda 凝量 + Kakshya 分区 + 古典六力及分量表')}</div>
							<div style={card}><div style={ct}>6 KP/择时</div>
								{kv('内容', 'KP 副主/六级/宫头次主星/当令星/意义者 + Praśna 卜卦 + Muhurta 择时 + Hora 行星时 + Choghadia 民用择时')}</div>
							<div style={card}><div style={ct}>7 Yoga</div>
								{kv('内容', '命盘组合格局按类归并（五大人/王/财/月/日/逆转/交换/形态/挑战…）+ 强中弱评分 + Kartari 夹击 + Sudarshana 三盘合参')}</div>
							<div style={card}><div style={ct}>8 副星 Upagraha</div>
								{kv('内容', '外行星(天海冥·信息性) + 特殊上升 + 日基/时基副星（Gulika/Maandi…）+ 补充上升（Chandra/Paaka/Karakamsa/Indu/Varṇada）+ Bhrigu Bindu 福点')}</div>
							<div style={card}><div style={ct}>9 映象 Jaimini</div>
								{kv('内容', 'Arudha 映象（AL/UL）+ 12 宫 Arudha Pada + 12 宫 Argala 干涉/反制')}</div>
							<div style={card}><div style={ct}>10 行运 Gochara</div>
								{kv('内容', '过运日期 + Sade Sati/Kantaka/Ashtama + 逐曜过运（从月/从命）含 Vedha 遮断与八分点判读')}</div>
							<div style={card}><div style={ct}>11 年度 Tājaka</div>
								{kv('内容', '输入年份生成年度盘 Varshaphal + Muntha/年主/年度合相/Sahams/Harsha·Pancha-Vargeeya 力/年内大运')}</div>
							<div style={card}><div style={ct}>12 化解 Remedies</div>
								{kv('内容', '依弱曜给宝石建议 + 九曜化解全表（宝石/金属/指/真言/守护神/善行/谷物）。仅信息·非处方')}</div>
							<div style={card}><div style={ct}>13 敌友 Maitri</div>
								{kv('内容', '复合五分敌友矩阵（自然·临时·复合三层，非对称）+ Jaimini 座相 Rāśi Dṛṣṭi')}</div>
						</div>
					</TabPane>

					{/* ============================== 流派分歧 ============================== */}
					<TabPane tab="流派分歧" key="schools">
						<div style={body}>
							<p style={{ ...p, color: MUTED }}>同一出生数据，不同流派的取舍点（可在左栏「流派」一键套，或逐项手动覆盖）。</p>
							<div style={card}><div style={ct}>岁差零点</div>
								{kv('分歧', 'Lahiri（官方）/ Raman / KP / Yukteshwar / True Citra·Revati（真星定标）各派零点不同')}
								{kv('影响', '整体平移黄经，临界度数的行星可能跨座/跨宿/跨脚，进而改大运起点')}</div>
							<div style={card}><div style={ct}>宫位口径</div>
								{kv('分歧', '整宫制（座=宫）vs Sripati/Bhāva Chalit（按度均分）vs KP·Placidus（真象限分宫）')}
								{kv('影响', '行星落第几宫、宫主取谁随之不同；KP 派必用真分宫，CSL 才有意义')}</div>
							<div style={card}><div style={ct}>相位范式（中栏连线）</div>
								{kv('分歧', '七政相映 Graha Drishti（Parāśarī）/ 星座相映 Rāśi Drishti（Jaimini）/ 年盘相映（Tājika）/ KP 范式')}</div>
							<div style={card}><div style={ct}>交点与大运起点</div>
								{kv('分歧', '平交点 vs 真交点；起运点取月亮（主流）或七政/节点/特殊上升/副星任一；条件大运是否启用')}</div>
							<div style={card}><div style={ct}>分盘算法变体</div>
								{kv('分歧', 'D2/D3/D24/D30 等有标准 Parāśara 与 Kashinatha/Jagannatha/Somanatha 等变体')}
								{kv('查看', '右栏「分盘」标签的「分盘变体对照」列出落座差异')}</div>
							<div style={card}><div style={ct}>寿命减算 / Bharaṇa 分组</div>
								{kv('分歧', 'Āyurdāya 的 haraṇa 减算、Aṁśāyu 的 Bharaṇa 分组有多派算法')}
								{kv('查看', '右栏「大运」标签的 Āyurdāya 卡内以流派选项并列对照')}</div>
							<div style={card}><div style={ct}>断法侧重</div>
								{kv('分歧', 'Parāśarī 重七政与分盘 / Jaimini 重映象与星座大运 / Tājika 重逐年年盘 / Nāḍī 重宿系')}</div>
						</div>
					</TabPane>
				</Tabs>
			</div>
		);
	}
}

export default IndiaHelpDoc;
