// 大六壬 各选项「真正差异化案例」验证:同一盘,切换选项 → 引擎输出确实不同且符合古籍。
// 此文件即「逐技术差异化」报告的可执行凭证。
import { getYueJiangByMethod, liurengAyanamsa } from '../LiuRengMain';
import ChuangChart from '../../liureng/ChuangChart';
import * as LRConst from '../../liureng/LRConst';
import { detectJianChuan } from '../../liureng/LRJianChuanDoc';
import { liurengWangXiang, judgeKongWang } from '../../liureng/LRZhangSheng';
import { analyzeDunGan, analyzeNianMing, analyzeKongLocations } from '../../liureng/LRKongDunNianDoc';

const SIGNZI = ['戌', '酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑', '子', '亥'];
const Z = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
const JIGONG = { 甲: '寅', 乙: '辰', 丙: '巳', 丁: '未', 戊: '巳', 己: '未', 庚: '申', 辛: '戌', 壬: '亥', 癸: '丑' };
const sunChart = (lon, signIdx) => ({ objects: [{ id: 'Sun', lon, sign: ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'][signIdx] }], nongli: { time: '子' } });
function makeLayout(yue, timezi){ const d = Z.indexOf(yue) - Z.indexOf(timezi); return { downZi: Z.slice(), upZi: Z.map((_,i)=>Z[((i+d)%12+12)%12]), houseTianJiang: LRConst.TianJiang.slice() }; }
function shang(l,z){ return l.upZi[l.downZi.indexOf(z)]; }
function makeKe(l,g,z){ const c1=shang(l,JIGONG[g]),c2=shang(l,c1),c3=shang(l,z),c4=shang(l,c3); return [['',c1,g],['',c2,c1],['',c3,z],['',c4,c3]]; }
function faYong(yue,timezi,gan,zhi,seHaiOpts){ const l=makeLayout(yue,timezi); return new ChuangChart({ chartObj:{nongli:{dayGanZi:gan+zhi}}, nongli:{dayGanZi:gan+zhi}, ke:makeKe(l,gan,zhi), seHaiOpts:seHaiOpts||null, liuRengChart:l, x:0,y:0,width:0,height:0 }).getSangCuang(); }
const guiChart = (gan, diurnal) => ({ nongli: { dayGanZi: gan + '子' }, isDiurnal: diurnal });

describe('差异化案例报告', ()=>{
	it('① 月将三派:黄经20° → 中气戌 / 节气酉 / 日躔亥(三派各异)', ()=>{
		expect(getYueJiangByMethod(sunChart(20,0),'zhongqi',2026)).toBe('戌');
		expect(getYueJiangByMethod(sunChart(20,0),'jieqi',2026)).toBe('酉');
		expect(getYueJiangByMethod(sunChart(20,0),'richan',2026)).toBe('亥');
	});
	it('② 贵人体系:庚日昼 → 正法A丑 / B派午(不同)', ()=>{
		expect(LRConst.getGuiZi(guiChart('庚',true),0)).toBe('丑');
		expect(LRConst.getGuiZi(guiChart('庚',true),3)).toBe('午');
	});
	it('③ 昼夜阳阴归属(六壬法A·甲日昼):旦暮系丑 / 阳阴系未(翻昼夜)', ()=>{
		expect(LRConst.getGuiZi(guiChart('甲',true),0,undefined,'danmu')).toBe('丑');
		expect(LRConst.getGuiZi(guiChart('甲',true),0,undefined,'yinyang')).toBe('未');
	});
	it('④ 涉害取舍:默认法发用锁定;扫描寻 app≠standard 之盘', ()=>{
		// 默认法(WP-0 golden 锁):辰将子时癸未日 → 发用酉
		expect(faYong('辰','子','癸','未',{method:'app',boundary:'app',shiRuKe:false}).cuang[0]).toBe('酉');
		// 扫描:存在某盘 app 与 standard 发用不同(证明选项真切换计算)
		let found = null;
		const cases = [['辰','子','癸','未'],['午','卯','甲','辰'],['辰','子','戊','寅'],['巳','寅','丁','亥'],['午','巳','丙','辰'],['戌','亥','辛','酉'],['酉','子','甲','寅'],['卯','子','乙','丑'],['未','寅','庚','午'],['申','卯','壬','戌']];
		for(const [y,t,g,z] of cases){
			const a = faYong(y,t,g,z,{method:'app',boundary:'app',shiRuKe:false}).cuang[0];
			const s = faYong(y,t,g,z,{method:'standard',boundary:'app',shiRuKe:false}).cuang[0];
			if(a !== s){ found = { case:`${y}将${t}时${g}${z}日`, app:a, standard:s }; break; }
		}
		// 记录到全局供报告;无论是否找到都不应抛
		// 实测:申将卯时壬戌日 → 默认法发用申、标准两向发用辰(选项确实切换计算)。
		expect(found).not.toBeNull();
		expect(found.app).not.toBe(found.standard);
	});
	it('⑤ 旺相休囚死:火 子月(冬)=死 / 午月(夏)=旺(随月令变)', ()=>{
		expect(liurengWangXiang('火','子','siji')).toBe('死');
		expect(liurengWangXiang('火','午','siji')).toBe('旺');
	});
	it('⑥ 空亡真假:水 子月(旺)=假空 / 巳月(囚)=真空', ()=>{
		expect(judgeKongWang('水','子','siji').kind).toBe('假空');
		expect(judgeKongWang('水','巳','siji').kind).toBe('真空');
	});
	it('⑦ 间传:寅辰午=顺间 / 午辰寅=逆间(方向不同)', ()=>{
		const a = detectJianChuan(['寅','辰','午']); const b = detectJianChuan(['午','辰','寅']);
		expect(a && a.dir).toBe('顺'); expect(b && b.dir).toBe('逆');
	});
	it('⑧ 遁干特殊(甲子旬·甲日):午遁庚=遁鬼(官鬼) / 卯遁丁=遁丁', ()=>{
		const XUN = { '子':'甲','丑':'乙','寅':'丙','卯':'丁','辰':'戊','巳':'己','午':'庚','未':'辛','申':'壬','酉':'癸','戌':'','亥':'' };
		const r = analyzeDunGan({ sanChuanBranches:['午','卯','子'], xunGanMap:XUN, dayGan:'甲', xunKongBranches:['戌','亥'] });
		expect(r.find(x=>x.branch==='午').flags).toContain('遁鬼');
		expect(r.find(x=>x.branch==='卯').flags).toContain('遁丁');
	});
	it('⑨ 旬空落点+陷空(甲子旬戌亥空):初传戌=斩首 / 戌亥上神落陷空', ()=>{
		const r = analyzeKongLocations({ xunKongBranches:['戌','亥'], sanChuanBranches:['戌','寅','午'], ke1Up:'子', ke3Up:'丑', branchUpMap:{'戌':'午','亥':'未'} });
		expect(r.hits.find(h=>h.pos==='初传').note).toContain('斩首');
		expect(r.xianKong.map(x=>x.god)).toEqual(expect.arrayContaining(['午','未']));
	});
	it('⑩ 年命上神:行年未·上神戌(空)=一年无成', ()=>{
		const r = analyzeNianMing({ runYearBranch:'未', branchUpMap:{'未':'戌'}, xunKongBranches:['戌','亥'], sanChuanBranches:['午','卯','子'], courseBranches:[] });
		expect(r.find(x=>x.label==='行年').note).toContain('一年无成');
	});
});
