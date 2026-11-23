// 策天页 · 时间 / 地点改值、步进预取、起盘载荷与取盘、AI 快照刷新、页签切换
// 从 KinAstroMain.js 按职责拆出的 KinAstroMain 方法:this 仍是 KinAstroMain 实例,门面里 mixinMethods(KinAstroMain, …) 原样挂回原型(与写在类里等价)。
// 读源码的检查读「子模块 + 门面」全集(scripts/source-sets.json)。
import { claimTrigger, settleTrigger } from '../../../utils/singleTrigger';
import DateTime from '../../comp/DateTime';
import { convertLatToStr, convertLonToStr } from '../../astro/AstroHelper';
import { resolveGeoZone } from '../../../utils/timezone';
import { geoNameFieldPatch } from '../../../utils/geoName';
import { buildYanqinYanfaSnapshot } from '../../yanqin/yanqinSnapshot';
import { saveModuleAISnapshot } from '../../../utils/moduleAiSnapshot';
import { normBinaryGender, parseFieldsDateTime } from '../../../utils/kinAstroFieldsSync';
import { stepPrefetchEnabled, kentangCacheEnabled, stepSelectPrefetchEnabled } from '../../../utils/perfFlags';
import { notePendingTime, pendingTimePatch } from '../../../utils/pendingTimeDraft';
import { chartDayBoundary } from '../../../utils/dayBoundaryResolve';
import { postKinAstro, buildSnapshotText, kinAstroSnapshotMeta, saveKinAstroAISnapshots } from './snapshot';
import { normalizeGanzhiInput } from './ziweiChart';

export const computeMethods = {
	// AI 导出/挂载实时取数:导出侧派发 refresh 事件,这里用当前盘即时构建快照并回填,
	// 保证「显示什么就导出什么」——不依赖懒存缓存是否已物化(rehydrate/未重排时缓存可能为空,
	// 缺此监听 → 显示有盘却报「当前页面没有可导出文本」)。
	// 本组件渲染整个铁板神数家族,每实例按 this.config 对应一个技法;
	// 导出侧对 kinastro 走 kinastro-{serviceKey},故 kinKey 与 moduleKey 两个键都响应。
	handleSnapshotRefreshRequest(evt){
		const moduleName = evt && evt.detail ? evt.detail.module : '';
		const cfg = this.config || {};
		const kinKey = `kinastro-${cfg.serviceKey || 'unknown'}`;
		if(moduleName !== kinKey && moduleName !== cfg.moduleKey){
			return;
		}
		const pan = this.state ? this.state.pan : null;
		if(!pan){
			return;
		}
		let text = '';
		try{
			const suffix = this.tiebanFrameworkSuffix(pan);
			text = `${buildSnapshotText(pan) || ''}${suffix ? `\n\n${suffix}` : ''}`.trim();
			// refresh 路径同构补演法段(与 saveKinAstroAISnapshots/无头同律):
			// 实时导出走此处,不补则「当前页导出」也缺 [演法]。同步 lunar-js 域内即全对。
			if(cfg.serviceKey === 'xianqin' && text && this.props.fields){
				try{
					const yf = buildYanqinYanfaSnapshot(parseFieldsDateTime(this.props.fields));
					if(yf){ text = `${text}\n\n${yf}`; }
				}catch(e2){ /* 演法失败不拖主快照 */ }
			}
		}catch(e){
			text = '';
		}
		if(text && text !== '暂无 kinastro 数据'){
			// 与平时写槽同一份 meta(此前只传两个参数:刷新一次槽的 meta 就变成 {},读盘方丢了服务键 / 段目录)
			saveModuleAISnapshot(moduleName, text, kinAstroSnapshotMeta(cfg, pan, this.props.hostModuleKey || cfg.moduleKey));
			if(evt && evt.detail && typeof evt.detail === 'object'){
				evt.detail.snapshotText = text;
			}
		}
	},

	onFieldsChange(field){
		if(this.props.dispatch){
			const flds = { ...(this.props.fields || {}), ...field };
			this.props.dispatch({ type: 'astro/fetchByFields', payload: flds });
		}
	},

	changeGeo(rec){
		// 策天飞星(cetian)选地点 → 坐标 + 时区自动校正 → onFieldsChange → fetchByFields 实时重排
		const f = this.props.fields || {};
		const dDt = f.date && f.date.value;
		const tDt = f.time && f.time.value;
		const ds = (dDt && dDt.format) ? dDt.format('YYYY-MM-DD') : null;
		const z = resolveGeoZone(rec, ds);
		const payload = {
			lon: { value: convertLonToStr(rec.lng) },
			lat: { value: convertLatToStr(rec.lat) },
			gpsLon: { value: rec.gpsLng },
			gpsLat: { value: rec.gpsLat },
		};
		if(z){
			payload.zone = { value: z };
			// 重锚 date/time 到新时区(保留钟面时刻、瞬时随之偏移),否则排盘仍用旧时区算瞬时
			if(dDt && dDt.clone){ const nd = dDt.clone(); nd.setZone(z); payload.date = { value: nd }; payload.ad = { value: nd.ad }; }
			if(tDt && tDt.clone){ const nt = tDt.clone(); nt.setZone(z); payload.time = { value: nt }; }
		}
		Object.assign(payload, geoNameFieldPatch(rec));
		this.onFieldsChange(payload);
	},

	onTimeChanged(value){
		notePendingTime(this, value && (value.time || value.value));
		const dt = value.time;
		this.onFieldsChange({
			date: { value: dt.clone() },
			time: { value: dt.clone() },
			ad: { value: dt.ad },
			zone: { value: dt.zone },
			// 步进方向提示:驱动 astro model settle 后 /chart ±步预取(消费后即剥离)
			...(value.step ? { __stepHint: value.step } : {}),
		});
		this.prefetchNextStepPan(dt, value.step);
	},

	// 顺向 +1 步 pan 预取:当前步 T 由正式请求(hook 联动)落 kentangCache,此处
	// 静默备下 T+1 —— 连点下一下即命中。payload 走 buildPayload 单源 → 键逐字节等。
	// native 子技法(本地引擎)零网络,直接跳过;失败静默;开关关=零行为。
	prefetchNextStepPan(dt, stepHint){
		try{
			if(!stepPrefetchEnabled() || !kentangCacheEnabled()){ return; }
			if(this.config.native){ return; }
			if(!stepHint || !stepHint.dir || !dt || typeof dt.clone !== 'function'){ return; }
			if(this.prefetchStepTimer){ clearTimeout(this.prefetchStepTimer); }
			this.prefetchStepTimer = setTimeout(()=>{
				this.prefetchStepTimer = null;
				if(this.unmounted){ return; }
				this._prefetchPanAtStep(dt, stepHint.unit || 'm', stepHint.dir);
			}, 150);
		}catch(e){ /* 预取失败无害 */ }
	},

	// 取数内核:以 dt 为基按 unit 走 1 步×dir,buildPayload 单源构包预取该时刻 pan。
	// settle 链(+1 同向)与选步长(±1 双向)共用,防两处步进加法漂移。
	_prefetchPanAtStep(dt, unit, dir){
		try{
			const dt2 = dt.clone();
			if(unit === 'y'){ dt2.addYear(dir); }
			else if(unit === 'M'){ dt2.addMonth(dir); }
			else if(unit === 'd'){ dt2.addDate(dir); }
			else if(unit === 'h'){ dt2.addHour(dir); }
			else { dt2.addMinute(4 * dir); }
			const flds2 = {
				...(this.props.fields || {}),
				date: { value: dt2.clone() },
				time: { value: dt2.clone() },
				ad: { value: dt2.ad },
				zone: { value: dt2.zone },
			};
			const payload = this.buildPayload(flds2);
			if(!payload){ return; }
			postKinAstro(this.config.serviceKey, payload).catch(()=>null);
		}catch(e){ /* 预取失败无害 */ }
	},

	// 选步长即预取:/chart 面由全局 handler 罩(时间走 store),pan 面(本页主耗时)
	// 此处以当前时间 ±1 双向预热 —— 选完步长第一下步进 pan 即命中。同 unit 5s 去重。
	prefetchStepSelect(unit){
		try{
			if(!stepPrefetchEnabled() || !kentangCacheEnabled() || !stepSelectPrefetchEnabled() || !unit){ return; }
			if(this.config && this.config.native){ return; }
			const now = Date.now();
			if(this._lastStepSel && this._lastStepSel.unit === unit && (now - this._lastStepSel.at) < 5000){ return; }
			this._lastStepSel = { unit, at: now };
			const flds = this.getTimeFieldsFromSelector(this.props.fields) || this.props.fields || {};
			const dt = flds.date && flds.date.value;
			if(!dt || typeof dt.clone !== 'function'){ return; }
			this._prefetchPanAtStep(dt, unit, 1);
			this._prefetchPanAtStep(dt, unit, -1);
		}catch(e){ /* 预取失败无害 */ }
	},

	getTimeFieldsFromSelector(baseFields){
		const _pend = pendingTimePatch(this);   // 改了时间还没等到全局盘回来:以最新改动为准(见 utils/pendingTimeDraft)
		if(_pend){ return { ...(baseFields || {}), ..._pend }; }
		if(!this.timeHook || !this.timeHook.getValue){
			return null;
		}
		const raw = this.timeHook.getValue();
		const dt = raw && raw.value && raw.value instanceof DateTime
			? raw.value
			: (raw && raw.time && raw.time instanceof DateTime ? raw.time : null);
		if(!dt){
			return null;
		}
		const patch = {
			date: { value: dt.clone() },
			time: { value: dt.clone() },
			ad: { value: dt.ad },
			zone: { value: dt.zone },
		};
		return { ...(baseFields || {}), ...patch };
	},

	clickPlot(){
		const nextFields = this.getTimeFieldsFromSelector(this.props.fields) || this.props.fields;
		if(nextFields && nextFields.date && nextFields.time && nextFields.zone){
			// 单路触发:派发 fields → astro/fetchByFields → save(props 变→didUpdate)+doHook(hook 回调)
			// 经 fetchPan 重排;此处不再显式 fetchPan(否则同一起盘打 2~3 次后端,fetchPan 去重虽能收敛,
			// 但从源头单路更干净)。若可派发(date/time/zone 齐),交由 dispatch 驱动。
			this.onFieldsChange({
				date: nextFields.date,
				time: nextFields.time,
				ad: nextFields.ad,
				zone: nextFields.zone,
			});
			return;
		}
		// 兜底:fields 不全(无法走 dispatch 重锚)时,仍直接起盘,避免按钮无反应。
		this.fetchPan(nextFields);
	},

	buildPayload(fields){
		const dt = parseFieldsDateTime(fields);
		if(!dt){
			return null;
		}
		const payload = {
			...dt,
			// 日界 / 晚子时:本盘有值用本盘,没有才用全局(与八字 / 七政 / 正传页面、AI 无头同一函数)
			...chartDayBoundary(fields),
			gender: normBinaryGender(this.state.gender),
			ke: this.state.ke,
			useKey: this.state.useKey === '1',
			method: this.state.tiebanMethod,
			startAge: this.state.tiebanStartAge,
			dayunSteps: this.state.tiebanDayunSteps,
			fatherBirthYear: this.state.fatherBirthYear,
			fatherDeathYear: this.state.fatherDeathYear,
			motherBirthYear: this.state.motherBirthYear,
			motherDeathYear: this.state.motherDeathYear,
			siblingsInfo: this.state.siblingsInfo,
			maritalStatus: this.state.maritalStatus,
			childrenInfo: this.state.childrenInfo,
			calendarMode: this.state.calendarMode,
			lunarYear: this.state.lunarYear,
			lunarMonth: this.state.lunarMonth,
			lunarDay: this.state.lunarDay,
				stemOverride: this.state.fendjingStemOverride === '1',
				yearStem: this.state.fendjingYearStem,
				hourStem: this.state.fendjingHourStem,
				keMode: this.state.beijiKeMode,
				beijiKeMode: this.state.beijiKeMode,
				beijiKe: this.state.beijiKe,
				beijiLookupCode: this.state.beijiLookupCode,
				beijiKeyword: this.state.beijiKeyword,
				useKe: this.state.beijiKeMode === 'manual',
				nanjiMode: this.state.nanjiMode,
				nanjiAfterLichun: this.state.nanjiAfterLichun,
				nanjiLunarYear: this.state.nanjiLunarYear,
				nanjiSolarMonth: this.state.nanjiSolarMonth,
				nanjiDay: this.state.nanjiDay,
				nanjiHourZhi: this.state.nanjiHourZhi,
				nanjiDayGan: this.state.nanjiDayGan,
				nanjiDayZhi: this.state.nanjiDayZhi,
				nanjiSection: this.state.nanjiSection,
				nanjiJianchu: this.state.nanjiJianchu,
				nanjiXiu: this.state.nanjiXiu,
				nanjiPasswordCode: this.state.nanjiPasswordCode,
				nanjiChart: this.state.nanjiChart,
				nanjiPalace: this.state.nanjiPalace,
				nanjiDegree: this.state.nanjiDegree,
				chunziKeMode: this.state.chunziKeMode,
				chunziKe: this.state.chunziKe,
				chunziLunarMode: this.state.chunziLunarMode,
				chunziLunarMonth: this.state.chunziLunarMonth,
				chunziLunarDay: this.state.chunziLunarDay,
				chunziLookupCode: this.state.chunziLookupCode,
				chunziKeyword: this.state.chunziKeyword,
				chunziTags: this.state.chunziTags,
				chunziMansion: this.state.chunziMansion,
				chunziHourBranch: this.state.chunziHourBranch,
				chunziResultLimit: this.state.chunziResultLimit,
			};
		if(this.config.serviceKey === 'cetian'){
			// 策天双法:覆盖 method(避免与铁板 tiebanMethod 混用)+ 原法子选项
			payload.method = this.state.cetianMethod || 'book';
			payload.lunarMode = this.state.cetianLunarMode || 'sxtwl';
			payload.starOrder = this.state.cetianStarOrder || 'reverse';
			// 5 显示开关随盘请求下发(后端按 show_* 过滤输出段/行;默认 1=现状)
			payload.showWuXingJu = this.state.cetianShowWuXingJu;
			payload.showSihua = this.state.cetianShowSihua;
			payload.showFlying = this.state.cetianShowFlying;
			payload.showBrightness = this.state.cetianShowBrightness;
			payload.showSolarTerm = this.state.cetianShowSolarTerm;
			// 书法(移语本)口径/流年/显示开关(原法后端自动忽略,统一透传保持键集单源)
			payload.brightnessSchool = this.state.cetianBrightnessSchool || 'yiyu';
			payload.shenGongMode = this.state.cetianShenGongMode || 'yizheng';
			payload.daxianMode = this.state.cetianDaxianMode || 'yiyu';
			payload.tianluoMode = this.state.cetianTianluoMode || 'benshu';
			payload.palaceNameMode = this.state.cetianPalaceNameMode || 'common';
			payload.liunianYear = this.state.cetianLiunianYear || new Date().getFullYear();
			payload.liunianQishaMode = this.state.cetianLiunianQishaMode || 'shengshi';
			payload.showLiunian = this.state.cetianShowLiunian;
			payload.showShensha = this.state.cetianShowShensha;
			payload.showZaYao = this.state.cetianShowZaYao;
			payload.showDuanjue = this.state.cetianShowDuanjue;
			payload.showXiu = this.state.cetianShowXiu;
			payload.showBianyao = this.state.cetianShowBianyao;
		}
		if(this.state.pillarOverride === '1'){
			const yearGz = normalizeGanzhiInput(this.state.yearGz);
			const monthGz = normalizeGanzhiInput(this.state.monthGz);
			const dayGz = normalizeGanzhiInput(this.state.dayGz);
			const hourGz = normalizeGanzhiInput(this.state.hourGz);
			if(yearGz){
				payload.yearGz = yearGz;
			}
			if(monthGz){
				payload.monthGz = monthGz;
			}
			if(dayGz){
				payload.dayGz = dayGz;
			}
			if(hourGz){
				payload.hourGz = hourGz;
			}
		}
		return payload;
	},

	async fetchPan(fields){
		if(this.config.native){
			this.requestSeq += 1;
			this.setState({ loading: false, pan: null });
			return;
		}
		const payload = this.buildPayload(fields);
		if(!payload){
			return;
		}
		// 同输入去重:若一模一样的请求(serviceKey+payload)已在途,跳过(在途那次的结果会落到当前盘)。
		// 起盘一次会经 clickPlot→onFieldsChange→dispatch→save(props 变 didUpdate)+doHook(hook 回调)两路
		// 对同一 payload 重复触发;此处把真正的网络请求收敛为 1 次。输入任何变化 → sig 变 → 照常重排。
		const sig = `${this.config.serviceKey}|${JSON.stringify(payload)}`;
		if(this._inFlightSig === sig){
			return;
		}
		// 双触发收敛:上面只挡「在途」同签名;缓存命中时第一路瞬间落地,挂钩 / 更新钩子的后几路仍会整套重来 →
		// 同签名在同一拍(见 utils/singleTrigger 时间窗)内再次触发也跳过。
		const panTrig = claimTrigger(this, 'fetchPan', sig);
		if(!panTrig){
			return;
		}
		const reqSeq = ++this.requestSeq;
		this._inFlightSig = sig;
		this.setState({ loading: true });
		try{
			const pan = await postKinAstro(this.config.serviceKey, payload);
			if(this._inFlightSig === sig){
				this._inFlightSig = null;
			}
			if(this.unmounted || reqSeq !== this.requestSeq){
				return;
			}
			this.setState({ pan, loading: false }, ()=>{
				saveKinAstroAISnapshots(this.config, pan, this.tiebanFrameworkSuffix(pan), this.props.hostModuleKey, this.props.fields);
			});
		}catch(e){
			if(this._inFlightSig === sig){
				this._inFlightSig = null;
			}
			settleTrigger(this, 'fetchPan', panTrig, false);
			console.warn('kinastro backend failed', this.config.serviceKey, e);
			if(!this.unmounted && reqSeq === this.requestSeq){
				this.setState({ loading: false });
			}
		}
	},

	setRightPanelTab(key){
		this.setState({ rightPanelTab: key });
	},

	// 一掌经右栏页签由它自己的组件画;这里记当前页,底部快捷栏才能点得到、亮得对。
	setYizhangjingTab(key){
		this.setState({ yizhangjingTab: key });
	},
};
