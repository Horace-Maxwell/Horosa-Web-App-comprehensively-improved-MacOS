// 六壬页 · 左栏起课设置面板与底部快捷栏
// 从 LiuRengMain.js 按职责拆出的 LiuRengMain 方法:this 仍是 LiuRengMain 实例,门面里 mixinMethods(LiuRengMain, …) 原样挂回原型(与写在类里等价)。
// 读源码的检查读「子模块 + 门面」全集(scripts/source-sets.json)。
import { sideSectionIcon } from '../../../constants/sideSectionIcons';
import { XQButton as Button, XQSelect as Select, XQSideSection, XQInputNumber } from '../../xq-ui';
import * as LRConst from '../../liureng/LRConst';
import { ZSList, ZhangSheng } from '../../liureng/LRZhangSheng';
import { ZHANDUAN_CATEGORIES } from '../../liureng/LRZhanDuanDoc';
import LiuRengInput from '../LiuRengInput';
import LiuRengBirthInput from '../LiuRengBirthInput';
import QuickDockBar from '../../common/QuickDockBar';
import { extractBranch, buildMetaRows } from './birthRunYear';
import { QI_METHODS, YUE_JIANG_METHODS, FEN_ZHOU_YE_METHODS } from './castLayout';
import { getAppliedBirth } from './panData';
import { zeriLockProps } from '../../../divination/zeri/zeriPageCalibre';
const {Option} = Select;

export const inputPanelMethods = {
	genWuXingDoms(){
		let res = LRConst.WuXing.map((item, idx)=>{
			return (
				<Option key={idx} value={item.elem} label={`${item.elem}（${item.ganzi}）`}>十二长生：{item.elem}--{item.ganzi}</Option>
			);
		});
		return res;

	},

	renderInputPanel(wxdoms){
		return (
			<div className="horosa-liureng-input-stack">
				<div className="horosa-side-panel-heading">
					<div>
						<div className="horosa-side-panel-title">六壬设置</div>
						<div className="horosa-side-panel-subtitle">时间、地点与起课选项</div>
					</div>
				</div>
				{/* [择日宿主] 左栏插槽(主六壬页不传=零渲染) */}
				{typeof this.props.renderLeftExtra === 'function' ? this.props.renderLeftExtra() : null}
				<XQSideSection iconName={sideSectionIcon('time')} title="时间与地点" collapsible={false}>
					<LiuRengInput
						fields={this.props.fields}
						onFieldsChange={this.onFieldsChange}
						onStepSelect={this.prefetchStepSelect}
						timeHook={this.timeHook}
						chartType={this.state.chartType}
						onChartTypeChange={this.onChartTypeChange}
					/>
				</XQSideSection>
				<XQSideSection iconName={sideSectionIcon('time')} title="卜卦人出生时间" storageKey="liureng.s1" className="horosa-liureng-input-section">
					<LiuRengBirthInput
						fields={this.state.birth}
						onFieldsChange={this.onBirthChange}
						requireConfirm={true}
					/>
				</XQSideSection>
				<XQSideSection iconName={sideSectionIcon('switches')} title="选项" storageKey="liureng.s2" className="horosa-liureng-input-section">
					<div className="horosa-liureng-select-grid">
							<label className="horosa-liureng-select-field">
								<span>十二长生</span>
								<Select value={this.state.wuxing} optionLabelProp="label" onChange={this.onWuXingChange} dropdownMatchSelectWidth={false}>
									{wxdoms}
								</Select>
							</label>
							<label className="horosa-liureng-select-field">
								<span>贵人体系</span>
								<Select value={this.state.guireng} onChange={this.onGuiRengChange} dropdownMatchSelectWidth={false}>
									<Option value={0}>六壬法贵人</Option>
									<Option value={1}>遁甲法贵人</Option>
									<Option value={2}>星占法贵人</Option>
									<Option value={3}>甲戊兼牛羊</Option>
									<Option value={4}>干合阳阴贵</Option>
								</Select>
							</label>
							{/* 起课时间算法:缺省真太阳时=后端历来口径(字节零回归);
							    选「直接时间」即与三式合一六壬层(时柱取自吃 timeAlg 的奇门)同口径。
							    择日里内嵌的这份不出:扫描引擎恒按真太阳时判,内嵌盘改了只会「所见≠所判」。 */}
							{this.usesSavedSettings() ? (
								<label className="horosa-liureng-select-field">
									<span>时间算法</span>
									<Select value={this.state.timeAlg} onChange={this.onTimeAlgChange} dropdownMatchSelectWidth={false}>
										<Option value={0}>真太阳时（默认）</Option>
										<Option value={1}>直接时间</Option>
									</Select>
								</label>
							) : null}
							<label className="horosa-liureng-select-field" title={zeriLockProps(this.props.zeriLocked, 'castMethod', this.state.castMethod, this._zeriRestoredLocks).title}>
								<span>起课法</span>
								{/* 择日内嵌:扫描只按正时正将起课,宿主传 zeriLocked 置灰(点结果行时回写锁定值) */}
								<Select value={this.state.castMethod} optionLabelProp="label" onChange={this.onCastMethodChange} dropdownMatchSelectWidth={false} disabled={!!zeriLockProps(this.props.zeriLocked, 'castMethod', this.state.castMethod, this._zeriRestoredLocks).disabled}>
									{QI_METHODS.map((m)=>(<Option key={m.key} value={m.key} label={m.short || m.name}>{m.name}</Option>))}
								</Select>
							</label>
							<label className="horosa-liureng-select-field">
								<span>换将</span>
								<Select value={this.state.yueJiangMethod} optionLabelProp="label" onChange={(v)=>this.handleCastField('yueJiangMethod', v)} dropdownMatchSelectWidth={false}>
									{YUE_JIANG_METHODS.map((m)=>(<Option key={m.key} value={m.key} label={m.short || m.name}>{m.name}</Option>))}
								</Select>
							</label>
							{this.state.castMethod === 'xuanshi' ? (
							<label className="horosa-liureng-select-field horosa-liureng-select-field-wide">
								<span>选时·时辰</span>
								<Select value={this.state.xuanShiZhi || ''} onChange={(v)=>this.handleCastField('xuanShiZhi', v)} dropdownMatchSelectWidth={false}>
									<Option value=''>用正时</Option>
									{LRConst.ZiList.map((z)=>(<Option key={z} value={z}>{z}时</Option>))}
								</Select>
							</label>
							) : null}
							{(this.state.castMethod === 'yanshu' || this.state.castMethod === 'baoshu') ? (
							<label className="horosa-liureng-select-field horosa-liureng-select-field-wide">
								<span>{this.state.castMethod === 'baoshu' ? '报数/字数/笔画' : '演数·随感之数'}</span>
								<XQInputNumber value={this.state.yanShuNum === '' || this.state.yanShuNum === null || this.state.yanShuNum === undefined ? null : Number(this.state.yanShuNum)} onChange={(v)=>this.handleCastField('yanShuNum', v === null || v === undefined ? '' : String(v))} placeholder='输入数字' style={{ width: '100%' }} />
							</label>
							) : null}
							<label className="horosa-liureng-select-field">
								<span>分昼夜</span>
								<Select value={this.state.fenZhouYe} onChange={(v)=>this.handleCastField('fenZhouYe', v)} dropdownMatchSelectWidth={false}>
									{FEN_ZHOU_YE_METHODS.map((m)=>(<Option key={m.key} value={m.key}>{m.name}</Option>))}
								</Select>
							</label>
							<label className="horosa-liureng-select-field">
								<span>涉害取舍</span>
								<Select value={this.state.seHaiMethod} onChange={(v)=>this.handleCastField('seHaiMethod', v)} dropdownMatchSelectWidth={false}>
									<Option value="app">仅下贼上(默认)</Option>
									<Option value="standard">标准深浅两向</Option>
									<Option value="mengzhongji">直取孟仲季</Option>
								</Select>
							</label>
							<label className="horosa-liureng-select-field">
								<span>涉害起讫</span>
								<Select value={this.state.seHaiBoundary} onChange={(v)=>this.handleCastField('seHaiBoundary', v)} dropdownMatchSelectWidth={false}>
									<Option value="app">计起点不计本家(默认)</Option>
									<Option value="both">两端皆计</Option>
									<Option value="neither">皆不计</Option>
								</Select>
							</label>
							<label className="horosa-liureng-select-field">
								<span>始入课</span>
								<Select value={this.state.shiRuKe ? '1' : '0'} onChange={(v)=>this.handleCastField('shiRuKe', v === '1')} dropdownMatchSelectWidth={false}>
									<Option value='0'>并入重审(默认)</Option>
									<Option value='1'>单列·九法变十法</Option>
								</Select>
							</label>
							<label className="horosa-liureng-select-field">
								<span>取象</span>
								<Select value={this.state.xiangOn ? '1' : '0'} onChange={(v)=>this.onToggleXiang(v === '1')} dropdownMatchSelectWidth={false}>
									<Option value='0'>关闭</Option>
									<Option value='1'>开启</Option>
								</Select>
							</label>
							<label className="horosa-liureng-select-field">
								<span>占事类型</span>
								<Select value={this.state.zhanCategory} onChange={this.onZhanCategoryChange} dropdownMatchSelectWidth={false}>
									{ZHANDUAN_CATEGORIES.map((c)=>(<Option key={c.key} value={c.key}>{c.name}</Option>))}
								</Select>
							</label>
							<label className="horosa-liureng-select-field">
								<span>年神排序</span>
								<Select value={this.state.yearShenShaSort} onChange={(v)=>this.handleCastField('yearShenShaSort', v)} dropdownMatchSelectWidth={false}>
									<Option value="sanyuan">四利三元序(默认)</Option>
									<Option value="suigui">太岁排轮(太阴异)</Option>
								</Select>
							</label>
							<label className="horosa-liureng-select-field" title={this.state.guireng !== 0 ? '星历阳阴系只在贵人体系=六壬法贵人时生效(甲乙丙辛壬癸昼夜互换);当前贵人体系下两档恒同' : undefined}>
								<span>昼夜阳阴归属</span>
								{/* 贵人≠六壬法时置灰:LRConst 只在 guirengType===0 时按此键互换昼夜 */}
								<Select value={this.state.yinyangSystem} disabled={this.state.guireng !== 0} onChange={(v)=>this.handleCastField('yinyangSystem', v)} dropdownMatchSelectWidth={false}>
									<Option value="danmu">旦暮系(默认)</Option>
									<Option value="yinyang">星历阳阴系</Option>
								</Select>
							</label>
							<label className="horosa-liureng-select-field">
								<span>土旺衰</span>
								<Select value={this.state.tuWangShuai} onChange={(v)=>this.handleCastField('tuWangShuai', v)} dropdownMatchSelectWidth={false}>
									<Option value="siji">四季月土旺(默认)</Option>
									<Option value="huotu">火土同宫(土随火)</Option>
								</Select>
							</label>
						</div>
						<div className="horosa-liureng-action-row">
						<Button type='primary' onClick={this.clickStartPaiPan}>起课</Button>
						<Button onClick={this.clickSaveCase}>保存</Button>
					</div>
				</XQSideSection>
			</div>
		);
	},

	buildQuickMetaItems(displayRunYear){
		const liureng = this.state.liureng;
		if(!liureng){
			return [];
		}
		const appliedBirth = getAppliedBirth(this.state);
		const genderVal = appliedBirth && appliedBirth.gender
			? appliedBirth.gender.value
			: -1;
		const genderText = genderVal === 0 || genderVal === '0' ? '女' : '男';
		const runyear = displayRunYear || {};
		const dunDing = liureng.xun ? (liureng.xun['遁丁'] || extractBranch(liureng.xun['旬丁'])) : '';
		const yearGods = [];
		const taisui1 = liureng.godsYear ? liureng.godsYear.taisui1 : null;
		for(let i=0; i<LRConst.TaiSui.length; i++){
			const key = LRConst.TaiSui[i];
			yearGods.push({
				key,
				value: taisui1 && taisui1[key] ? taisui1[key] : '—',
			});
		}
		const zhangsheng = ZSList.map((item)=>({
			key: item,
			value: ZhangSheng.wxphase[`${this.state.wuxing}_${item}`],
		}));
		return [{
			title: '行年',
			rows: [{
				key: '行年',
				value: runyear.year ? runyear.year : '—',
			}, {
				key: '年龄',
				value: runyear.age !== undefined && runyear.age !== null ? `${runyear.age}岁` : '—',
			}, {
				key: '性别',
				value: genderText,
			}],
		}, {
			title: '旬日',
			rows: [{
				key: '旬空',
				value: liureng.xun ? liureng.xun['旬空'] : '—',
			}, {
				key: '旬首',
				value: liureng.xun ? liureng.xun['旬首'] : '—',
			}, {
				key: '旬尾',
				value: liureng.xun ? liureng.xun['旬尾'] : '—',
			}, {
				key: '遁丁',
				value: dunDing || '—',
			}],
		}, {
			title: '旺衰',
			rows: buildMetaRows(liureng.season),
		}, {
			title: '基础神煞',
			rows: buildMetaRows(liureng.gods),
		}, {
			title: '干煞',
			rows: buildMetaRows(liureng.godsGan),
		}, {
			title: '月煞',
			rows: buildMetaRows(liureng.godsMonth),
		}, {
			title: '支煞',
			rows: buildMetaRows(liureng.godsZi),
		}, {
			title: '年煞',
			rows: yearGods,
		}, {
			title: `${this.state.wuxing}十二长生`,
			rows: zhangsheng,
		}];
	},

	// 神煞/旬空/长生等信息不再走栏内速查弹层——全部常驻右栏「信息」tab(信息不得仅在快捷栏可见)。
	renderQuickDock(){
		return (
			<QuickDockBar
				page="lrzhan"
				className="horosa-liureng-quick-dock"
				hasResult={!!this.state.liureng}
				primary={{ key: 'paipan', label: '起课', onClick: ()=>this.clickStartPaiPan() }}
				extras={[
					{ key: 'nowCast', label: '此刻起课', icon: 'quickTransit', needsResult: false, onClick: ()=>this.clickStartNowPaiPan() },
				]}
				save={()=>this.clickSaveCase()}
				dispatch={this.props.dispatch}
			/>
		);
	},
};
