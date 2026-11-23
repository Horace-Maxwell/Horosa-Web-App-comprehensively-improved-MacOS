// 六壬页 · 取数:神煞 / 行年参数与请求、本命年干支、步进预取
// 从 LiuRengMain.js 按职责拆出的 LiuRengMain 方法:this 仍是 LiuRengMain 实例,门面里 mixinMethods(LiuRengMain, …) 原样挂回原型(与写在类里等价)。
// 读源码的检查读「子模块 + 门面」全集(scripts/source-sets.json)。
import { Modal } from 'antd';
import * as Constants from '../../../utils/constants';
import request from '../../../utils/request';
import * as LRConst from '../../liureng/LRConst';
import DateTime from '../../comp/DateTime';
import { clearModuleAISnapshot } from '../../../utils/moduleAiSnapshot';
import { castSourceKey, castFailureKeeps } from '../../../utils/derivedChartSource';
import { getBirthGanzhiLocalCache, getLiurengRunyearLocalCache, setBirthGanzhiLocalCache, setLiurengRunyearLocalCache } from '../../../utils/localCalcCache';
import { defaultLateZiHourUseNextDay } from '../../../utils/dayBoundary';
import { resolveAfter23NewDay } from '../../../utils/dayBoundaryResolve';
import { stepPrefetchEnabled, stepSelectPrefetchEnabled } from '../../../utils/perfFlags';
import { armStepPrefetch } from '../../../utils/stepPrefetchArm';
import { buildBirthFields, extractGanZi, resolveGuaYearGanZi, MaleRunYearList, FemaleRunYearList, calcRunYearLocal, getSolarYearFromField } from './birthRunYear';
import { getAppliedBirth, clonePlain, buildCacheKey, pushCache } from './panData';

export const requestMethods = {
	genRunYearParams(){
		let flds = getAppliedBirth(this.state);
		const calcFields = this.state.calcFields ? this.state.calcFields : this.props.fields;
		const guaDate = calcFields && calcFields.date && calcFields.date.value ? calcFields.date.value.format('YYYY-MM-DD') : '';
		const guaTime = calcFields && calcFields.time && calcFields.time.value ? calcFields.time.value.format('HH:mm:ss') : '';
		const guaAd = calcFields && calcFields.ad && calcFields.ad.value !== undefined
			? calcFields.ad.value
			: (calcFields && calcFields.date && calcFields.date.value ? calcFields.date.value.ad : 1);
		const guaZone = calcFields && calcFields.zone && calcFields.zone.value
			? calcFields.zone.value
			: (calcFields && calcFields.date && calcFields.date.value ? calcFields.date.value.zone : '');
		const guaLon = calcFields && calcFields.lon ? calcFields.lon.value : '';
		const guaLat = calcFields && calcFields.lat ? calcFields.lat.value : '';
		// 缺键取全局现值(此前写死 0 = 24 点换日,与页面初值 / 全局缺省不同)
		const guaAfter23 = resolveAfter23NewDay(calcFields && calcFields.after23NewDay && calcFields.after23NewDay.value);
		const params = {
			ad: flds.date.value.ad,
			date: flds.date.value.format('YYYY-MM-DD'),
			time: flds.time.value.format('HH:mm:ss'),
			zone: flds.date.value.zone,
			lon: flds.lon.value,
			lat: flds.lat.value,
			gender: flds.gender.value,
			after23NewDay: flds.after23NewDay.value,
			lateZiHourUseNextDay: flds.lateZiHourUseNextDay && flds.lateZiHourUseNextDay.value !== undefined ? flds.lateZiHourUseNextDay.value : defaultLateZiHourUseNextDay(),
			guaYearGanZi: resolveGuaYearGanZi(this.state.liureng),
			guaDate: guaDate,
			guaTime: guaTime,
			guaAd: guaAd,
			guaZone: guaZone,
			guaLon: guaLon,
			guaLat: guaLat,
			guaAfter23NewDay: guaAfter23,
		}
		return params;
	},

	genGodsParams(fields){
		let params = null;
		let flds = fields ? fields : this.props.fields;
		if(flds.params){
			let dtparts = flds.params.birth.split(' ');
			params = {
				...flds.params,
				date: dtparts[0],
				time: dtparts[1],
			};

		}else{
			params = {
				date: flds.date.value.format('YYYY-MM-DD'),
				time: flds.time.value.format('HH:mm:ss'),
				zone: flds.date.value.zone,
				ad: flds.date.value.ad,
				lon: flds.lon.value,
				lat: flds.lat.value,
			};
		}
		// 起课时间算法随参送出(后端缺省 RealSun;三条取盘路径共用本函数,缓存键随之同构)。
		// 择日内嵌恒真太阳时(扫描口径;旧存案带来的直接时间只用于照存档显示)
		params.timeAlg = this.props.techniqueScope ? 0 : (this.state.timeAlg === 1 ? 1 : 0);
		// 关键: backend liureng/gods 缺这个会用 默认值 1, 导致 dropdown 切换无效。
		if(flds.after23NewDay && flds.after23NewDay.value !== undefined){
			params.after23NewDay = flds.after23NewDay.value;
		}
		if(flds.guaAfter23NewDay && flds.guaAfter23NewDay.value !== undefined){
			params.guaAfter23NewDay = flds.guaAfter23NewDay.value;
		}
		// v2.2.1 第二全局开关·晚子时·时柱起干
		if(flds.lateZiHourUseNextDay && flds.lateZiHourUseNextDay.value !== undefined){
			params.lateZiHourUseNextDay = flds.lateZiHourUseNextDay.value;
		}else{
			params.lateZiHourUseNextDay = defaultLateZiHourUseNextDay();
		}

		return params;
	},

	// R4-B2(S3 收敛):选步长即预取改走武装引擎 —— ±depth 全窗任务(gods 经登记表构造 +
	// /chart 主链)统一由共享调度器排队(享白名单闸/latest-wins/预算/连点保底),不再本地
	// 裸发(的 ±1 双向裸 request 语义被 ±depth 超集覆盖;5s 去重由武装线沿用)。
	prefetchStepSelect(unit){
		try{
			if(!stepPrefetchEnabled() || !stepSelectPrefetchEnabled() || !unit){ return; }
			const now = Date.now();
			if(this._lastStepSel && this._lastStepSel.unit === unit && (now - this._lastStepSel.at) < 5000){ return; }
			this._lastStepSel = { unit, at: now };
			armStepPrefetch('unit-select', { unit });
		}catch(e){ /* 预取失败无害 */ }
	},

	async requestBirthYearGanZi(){
		const flds = getAppliedBirth(this.state);
		if(!flds || !flds.date || !flds.time){
			return '';
		}
		const key = [
			flds.date.value.format('YYYY-MM-DD'),
			flds.time.value.format('HH:mm:ss'),
			flds.date.value.ad,
			flds.date.value.zone,
			flds.lon.value,
			flds.lat.value,
			flds.after23NewDay.value,
		].join('|');
		if(this.birthYearGanZiCache[key]){
			return this.birthYearGanZiCache[key];
		}
		const localHit = getBirthGanzhiLocalCache(key);
		if(localHit){
			this.birthYearGanZiCache[key] = localHit;
			return localHit;
		}
		const params = {
			ad: flds.date.value.ad,
			date: flds.date.value.format('YYYY-MM-DD'),
			time: flds.time.value.format('HH:mm:ss'),
			zone: flds.date.value.zone,
			lon: flds.lon.value,
			lat: flds.lat.value,
			after23NewDay: flds.after23NewDay.value,
			lateZiHourUseNextDay: flds.lateZiHourUseNextDay && flds.lateZiHourUseNextDay.value !== undefined ? flds.lateZiHourUseNextDay.value : defaultLateZiHourUseNextDay(),
		};
		try{
			const data = await request(`${Constants.ServerRoot}/liureng/gods`, {
				body: JSON.stringify(params),
				silent: true,
			});
			const lr = data && data[Constants.ResultKey] ? data[Constants.ResultKey].liureng : null;
			const ganzi = extractGanZi(
				lr && lr.fourColumns && lr.fourColumns.year ? lr.fourColumns.year.ganzi : ''
			) || extractGanZi(lr && lr.nongli ? (lr.nongli.yearGanZi || lr.nongli.yearJieqi || lr.nongli.year) : '');
			if(ganzi){
				this.birthYearGanZiCache[key] = ganzi;
				setBirthGanzhiLocalCache(key, ganzi);
			}
			return ganzi;
		}catch(e){
			return '';
		}
	},

	async requestGods(fields, castChart){
		if(fields === undefined || fields === null){
			return;
		}
		const chart = this.lessonChartFor(fields, castChart);
		// 择日内嵌重起:本页时间算法回到真太阳时(旧存案照存档显示的直接时间到此为止)
		if(this.props.techniqueScope && this.state.timeAlg !== 0){
			this.setState({ timeAlg: 0 });
		}
		// 请求代次:只认最后一次起课(在途的起课晚回,会盖掉之后载入的存档课 / 之后再起的课);载入存案复原课时同样推进代次
		const seq = (this._godsReqSeq = (this._godsReqSeq || 0) + 1);
		const params = this.genGodsParams(fields);
		const godsKey = buildCacheKey(params);
		let result = null;
		if(godsKey && this.godsCache.has(godsKey)){
			result = clonePlain(this.godsCache.get(godsKey));
		}else if(godsKey && this.godsInflight.has(godsKey)){
			result = clonePlain(await this.godsInflight.get(godsKey));
		}else{
			const req = request(`${Constants.ServerRoot}/liureng/gods`, {
				body: JSON.stringify(params),
				silent: true,
			}).then((data)=>{
				return data && data[Constants.ResultKey] ? data[Constants.ResultKey] : null;
			}).finally(()=>{
				if(godsKey){
					this.godsInflight.delete(godsKey);
				}
			});
			if(godsKey){
				this.godsInflight.set(godsKey, req);
			}
			result = await req;
			if(godsKey && result){
				pushCache(this.godsCache, godsKey, clonePlain(result), 72);
			}
		}
		if(seq !== this._godsReqSeq){
			return;
		}
		if(!result || !result.liureng){
			// 取失败:与屏上那一课同一起课时刻地点(只改了设置)→ 留存;换了时刻 / 地点 → 屏上那一课是上一课,
			// 清掉(连同本页 AI 快照槽),盘面回到「这一刻的底盘、课还没起出来」;之后同一组参数照常重取
			if(!castFailureKeeps(castSourceKey(this.state.calcFields), castSourceKey(fields))){
				this.setState({ liureng: null, runyear: null, calcFields: fields, calcChart: chart });
				clearModuleAISnapshot(this.props.techniqueScope || 'liureng');
			}
			return;
		}
		
		let dayGanZi = result.liureng.nongli.dayGanZi;
		let dayGan = dayGanZi.substr(0, 1);
		// 缺省随日干五行;但用户手选过(或载档带来存档值)之后不得再覆盖 —— 此前每次
		// 起课(含改时间、步进一格)都无条件重置,所选五行守不住,右栏十二长生表与取象卡随之跳回。
		let wx = this.state.wuxingUserSet ? this.state.wuxing : LRConst.GanZiWuXing[dayGan];
		const appliedBirth = buildBirthFields(this.state.birth, new DateTime());
		const st = {
			liureng: result.liureng,
			calcBirth: appliedBirth,
			wuxing: wx,
			calcFields: fields,
			calcChart: chart,
		};

		this.setState(st, ()=>{
			this.requestRunYear();
			this.saveLiuRengAISnapshot(params, result.liureng, this.state.runyear, wx, this.state.guireng);
		});
	},

	async requestRunYear(){
		if(this.state.liureng === null){
			return;
		}
		// 请求代次(与起课同法):只认最后一次取行年 —— 连点步进跨年 / 连改出生档时,旧参数的行年晚回不得盖掉新值;
		// 每个 await 之后都判,载入存案复原行年时同样推进代次
		const seq = (this._runYearReqSeq = (this._runYearReqSeq || 0) + 1);
		const stale = ()=>seq !== this._runYearReqSeq || this.unmounted;
		
		const params = this.genRunYearParams();
		const fields = this.state.calcFields ? this.state.calcFields : this.props.fields;
		if(!fields || !fields.date || !fields.date.value){
			return;
		}
		const birthFields = getAppliedBirth(this.state);
		if(!birthFields || !birthFields.date || !birthFields.date.value){
			return;
		}
		const birthSolarYear = getSolarYearFromField(birthFields.date);
		const guaSolarYear = getSolarYearFromField(fields.date);
		// 带符号天文年比较(公元前 3044 早于公元前 3040):绝不能用 abs 年,BC 侧会反向误判
		if(Number.isFinite(birthSolarYear) && Number.isFinite(guaSolarYear) && birthSolarYear > guaSolarYear){
			Modal.error({
				title: '出生年份必须小于卜卦年份'
			});
			return;
		}
		const genderVal = birthFields && birthFields.gender ? birthFields.gender.value : 1;
		let fallbackRunYear = null;
		if(Number.isFinite(birthSolarYear) && Number.isFinite(guaSolarYear) && guaSolarYear >= birthSolarYear){
			const age = guaSolarYear - birthSolarYear;
			const ageCycle = ((age % 60) + 60) % 60;
			const yearList = `${genderVal}` === '0' ? FemaleRunYearList : MaleRunYearList;
			fallbackRunYear = {
				age: age,
				ageCycle: ageCycle,
				year: yearList[ageCycle] || '',
			};
		}
		if(!params.guaYearGanZi && !fallbackRunYear){
			Modal.error({
				title: '无法识别卜卦年份干支，请先起课后再试',
			});
			return;
		}

		let result = fallbackRunYear ? { ...fallbackRunYear } : {};
		const runyearKey = buildCacheKey(params);
		try{
			let serverRes = {};
			const localRunyearHit = runyearKey ? getLiurengRunyearLocalCache(runyearKey) : null;
			if(runyearKey && this.runYearServerCache.has(runyearKey)){
				serverRes = clonePlain(this.runYearServerCache.get(runyearKey)) || {};
			}else if(runyearKey && this.runYearServerInflight.has(runyearKey)){
				serverRes = clonePlain(await this.runYearServerInflight.get(runyearKey)) || {};
				if(stale()){ return; }
			}else if(localRunyearHit){
				serverRes = clonePlain(localRunyearHit) || {};
				pushCache(this.runYearServerCache, runyearKey, clonePlain(serverRes), 96);
			}else{
				const req = request(`${Constants.ServerRoot}/liureng/runyear`, {
					body: JSON.stringify(params),
					silent: true,
				}).then((data)=>{
					return data && data[Constants.ResultKey] ? { ...data[Constants.ResultKey] } : {};
				}).finally(()=>{
					if(runyearKey){
						this.runYearServerInflight.delete(runyearKey);
					}
				});
				if(runyearKey){
					this.runYearServerInflight.set(runyearKey, req);
				}
				serverRes = await req;
				if(runyearKey){
					pushCache(this.runYearServerCache, runyearKey, clonePlain(serverRes), 96);
					setLiurengRunyearLocalCache(runyearKey, clonePlain(serverRes));
				}
				if(stale()){ return; }
			}
			result = {
				...serverRes,
				...result,
			};
			const guaGanZi = extractGanZi(params.guaYearGanZi) || resolveGuaYearGanZi(this.state.liureng);
			const birthGanZi = await this.requestBirthYearGanZi();
			if(stale()){ return; }
			let localRunYear = calcRunYearLocal(
				birthGanZi,
				guaGanZi,
				genderVal,
				birthSolarYear,
				guaSolarYear
			);
			if(!localRunYear && fallbackRunYear){
				localRunYear = fallbackRunYear;
			}
			if(!localRunYear && serverRes.age !== undefined && serverRes.age !== null){
				const age = Number(serverRes.age);
				if(Number.isFinite(age)){
					const ageCycle = ((age % 60) + 60) % 60;
					const yearList = `${genderVal}` === '0' ? FemaleRunYearList : MaleRunYearList;
					localRunYear = {
						age: age,
						ageCycle: ageCycle,
						year: yearList[ageCycle] || serverRes.year || '',
					};
				}
			}
			if(localRunYear){
				result.year = localRunYear.year;
				result.age = localRunYear.age;
				result.ageCycle = localRunYear.ageCycle;
			}
		}catch(e){
			if(fallbackRunYear){
				result = {
					...result,
					...fallbackRunYear,
				};
			}
		}
		if(fallbackRunYear){
			if(result.year === undefined || result.year === null || result.year === ''){
				result.year = fallbackRunYear.year;
			}
			if(result.age === undefined || result.age === null || Number.isNaN(Number(result.age))){
				result.age = fallbackRunYear.age;
			}
			if(result.ageCycle === undefined || result.ageCycle === null || Number.isNaN(Number(result.ageCycle))){
				result.ageCycle = fallbackRunYear.ageCycle;
			}
		}
		
		if(stale()){ return; }
		const st = {
			runyear: result,
		};

		this.setState(st, ()=>{
			this.saveLiuRengAISnapshot(null, this.state.liureng, result, this.state.wuxing, this.state.guireng);
		});
	},
};
