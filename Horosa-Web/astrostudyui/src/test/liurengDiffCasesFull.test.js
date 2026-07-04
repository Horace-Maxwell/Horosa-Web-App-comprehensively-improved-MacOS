// 大六壬 全选项「差异化案例」综合验证(引擎实算·多案例·逐条锁值)。同盘切选项 → 输出确不同且合古籍。
import { getYueJiangByMethod, liurengAyanamsa } from '../components/lrzhan/LiuRengMain';
import ChuangChart from '../components/liureng/ChuangChart';
import * as LRConst from '../components/liureng/LRConst';
import { detectJianChuan } from '../components/liureng/LRJianChuanDoc';
import { liurengWangXiang, judgeKongWang } from '../components/liureng/LRZhangSheng';
import { analyzeDunGan, analyzeNianMing, analyzeKongLocations } from '../components/liureng/LRKongDunNianDoc';

const SIGN=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const Z=['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'];
const JIGONG={甲:'寅',乙:'辰',丙:'巳',丁:'未',戊:'巳',己:'未',庚:'申',辛:'戌',壬:'亥',癸:'丑'};
const sun=(lon)=>({objects:[{id:'Sun',lon,sign:SIGN[Math.floor(lon/30)%12]}],nongli:{time:'子'}});
const lay=(y,t)=>{const d=Z.indexOf(y)-Z.indexOf(t);return{downZi:Z.slice(),upZi:Z.map((_,i)=>Z[((i+d)%12+12)%12]),houseTianJiang:LRConst.TianJiang.slice()};};
const sh=(l,z)=>l.upZi[l.downZi.indexOf(z)];
const mk=(l,g,z)=>{const c1=sh(l,JIGONG[g]),c2=sh(l,c1),c3=sh(l,z),c4=sh(l,c3);return[['',c1,g],['',c2,c1],['',c3,z],['',c4,c3]];};
const fy=(y,t,g,z,o)=>{const l=lay(y,t);return new ChuangChart({chartObj:{nongli:{dayGanZi:g+z}},nongli:{dayGanZi:g+z},ke:mk(l,g,z),seHaiOpts:o||null,liuRengChart:l,x:0,y:0,width:0,height:0}).getSangCuang();};
const gui=(g,t,yy)=>LRConst.getGuiZi({nongli:{dayGanZi:g+'子'},isDiurnal:true},t,undefined,yy||'danmu');

describe('① 月将三派(中气/节气/日躔)', ()=>{
	it('黄经各异点:三派输出不同', ()=>{
		expect([getYueJiangByMethod(sun(20),'zhongqi',2026),getYueJiangByMethod(sun(20),'jieqi',2026),getYueJiangByMethod(sun(20),'richan',2026)]).toEqual(['戌','酉','亥']);
		expect([getYueJiangByMethod(sun(50),'zhongqi',2026),getYueJiangByMethod(sun(50),'jieqi',2026),getYueJiangByMethod(sun(50),'richan',2026)]).toEqual(['酉','申','戌']);
		expect([getYueJiangByMethod(sun(340),'zhongqi',2026),getYueJiangByMethod(sun(340),'jieqi',2026),getYueJiangByMethod(sun(340),'richan',2026)]).toEqual(['亥','亥','子']);
	});
	it('日躔含岁差:同黄经24°,1900年=戌 / 2026年=亥(岁差过宫)', ()=>{
		expect(liurengAyanamsa(2026)).toBeGreaterThan(liurengAyanamsa(1900));
		expect(getYueJiangByMethod(sun(24),'richan',1900)).toBe('戌');
		expect(getYueJiangByMethod(sun(24),'richan',2026)).toBe('亥');
	});
});

describe('② 贵人体系(五系)', ()=>{
	it('庚日昼:甲戊兼牛羊=午,余系=丑(仅该系异)', ()=>{
		expect([gui('庚',0),gui('庚',1),gui('庚',2),gui('庚',3),gui('庚',4)]).toEqual(['丑','丑','丑','午','丑']);
	});
	it('戊日昼:星占法=午,六壬法A=丑(系间分歧)', ()=>{
		expect(gui('戊',0)).toBe('丑');
		expect(gui('戊',2)).toBe('午');
	});
	it('壬日昼:六壬法A=巳 / 干合阳阴贵=卯(系间分歧)', ()=>{
		expect(gui('壬',0)).toBe('巳');
		expect(gui('壬',4)).toBe('卯');
	});
});

describe('③ 昼夜阳阴归属(六壬法A·昼)', ()=>{
	it('甲乙丙辛壬癸 翻昼夜 / 丁庚 不翻', ()=>{
		expect(gui('甲',0,'danmu')).toBe('丑'); expect(gui('甲',0,'yinyang')).toBe('未');
		expect(gui('丙',0,'danmu')).toBe('亥'); expect(gui('丙',0,'yinyang')).toBe('酉');
		expect(gui('丁',0,'danmu')).toBe(gui('丁',0,'yinyang')); // 不翻
		expect(gui('庚',0,'danmu')).toBe(gui('庚',0,'yinyang')); // 不翻
	});
});

describe('④ 涉害取舍(默认法/标准两向/孟仲季 + 起讫 + 始入课)', ()=>{
	it('申将卯时壬戌日:默认法发用申 ≠ 标准两向辰', ()=>{
		expect(fy('申','卯','壬','戌',{method:'app',boundary:'app',shiRuKe:false}).cuang[0]).toBe('申');
		expect(fy('申','卯','壬','戌',{method:'standard',boundary:'app',shiRuKe:false}).cuang[0]).toBe('辰');
		expect(fy('申','卯','壬','戌',{method:'mengzhongji',boundary:'app',shiRuKe:false}).cuang[0]).toBe('辰');
	});
	it('辰将子时癸未日:三法皆收敛于酉(此盘无分歧)', ()=>{
		['app','standard','mengzhongji'].forEach(m=>expect(fy('辰','子','癸','未',{method:m,boundary:'app',shiRuKe:false}).cuang[0]).toBe('酉'));
	});
	it('始入课开关:午将卯时甲辰日 重审课 → 始入课(单下贼上改名)', ()=>{
		expect(fy('午','卯','甲','辰',{method:'app',boundary:'app',shiRuKe:false}).name).toBe('重审课');
		expect(fy('午','卯','甲','辰',{method:'app',boundary:'app',shiRuKe:true}).name).toBe('始入课');
	});
});

describe('⑤ 旺相休囚死(随月令)', ()=>{
	it('木:春旺/夏休/秋死/冬相/季囚', ()=>{
		expect(['寅','午','申','子','辰'].map(m=>liurengWangXiang('木',m,'siji'))).toEqual(['旺','休','死','相','囚']);
	});
	it('土旺衰:寅月 四季制=死 / 火土同宫=相(开关切换)', ()=>{
		expect(liurengWangXiang('土','寅','siji')).toBe('死');
		expect(liurengWangXiang('土','寅','huotu')).toBe('相');
	});
});

describe('⑥ 空亡真假(旺空假/衰空真)', ()=>{
	it('水:子月旺=假空 / 巳月囚=真空;火:午旺=假空 / 子死=真空', ()=>{
		expect(judgeKongWang('水','子','siji').kind).toBe('假空');
		expect(judgeKongWang('水','巳','siji').kind).toBe('真空');
		expect(judgeKongWang('火','午','siji').kind).toBe('假空');
		expect(judgeKongWang('火','子','siji').kind).toBe('真空');
	});
});

describe('⑦ 间传/全局(§17)', ()=>{
	it('寅辰午=出阳(顺间) / 午辰寅=顾祖(逆间) / 申子辰=润下(全局)', ()=>{
		expect(detectJianChuan(['寅','辰','午']).dir).toBe('顺');
		expect(detectJianChuan(['午','辰','寅']).dir).toBe('逆');
		expect(detectJianChuan(['申','子','辰']).name).toBe('润下格');
		expect(detectJianChuan(['亥','卯','未']).name).toBe('曲直格');
	});
});

describe('⑧ 遁干特殊(甲子旬·甲日)', ()=>{
	const XUN={'子':'甲','丑':'乙','寅':'丙','卯':'丁','辰':'戊','巳':'己','午':'庚','未':'辛','申':'壬','酉':'癸','戌':'','亥':''};
	it('午遁庚=遁鬼(官鬼)/子遁甲=遁甲/卯遁丁=遁丁;戌(空)=空无遁', ()=>{
		const r=analyzeDunGan({sanChuanBranches:['午','子','卯'],xunGanMap:XUN,dayGan:'甲',xunKongBranches:['戌','亥']});
		expect(r.find(x=>x.branch==='午').flags).toContain('遁鬼');
		expect(r.find(x=>x.branch==='子').flags).toContain('遁甲');
		expect(r.find(x=>x.branch==='卯').flags).toContain('遁丁');
		const r2=analyzeDunGan({sanChuanBranches:['戌','午','寅'],xunGanMap:XUN,dayGan:'甲',xunKongBranches:['戌','亥']});
		expect(r2.find(x=>x.branch==='戌').gan).toBe('');
	});
});

describe('⑨ 旬空落点+陷空(甲子旬戌亥空)', ()=>{
	it('干上戌空+初传亥空逐位断;陷空午临戌·未临亥', ()=>{
		const r=analyzeKongLocations({xunKongBranches:['戌','亥'],ke1Up:'戌',ke3Up:'子',sanChuanBranches:['亥','寅','午'],branchUpMap:{'戌':'午','亥':'未'},runYearBranch:'丑'});
		expect(r.hits.map(h=>h.pos)).toEqual(expect.arrayContaining(['干上神','初传']));
		expect(r.xianKong).toEqual(expect.arrayContaining([{seat:'戌',god:'午'},{seat:'亥',god:'未'}]));
	});
});

describe('⑩ 年命上神(行年/本命空亡)', ()=>{
	it('行年未上神戌(空)=一年无成;行年午入传=重参', ()=>{
		expect(analyzeNianMing({runYearBranch:'未',branchUpMap:{'未':'戌'},xunKongBranches:['戌','亥'],sanChuanBranches:['午','卯','子'],courseBranches:[]}).find(x=>x.label==='行年').note).toContain('一年无成');
		expect(analyzeNianMing({runYearBranch:'午',branchUpMap:{'午':'寅'},xunKongBranches:['戌','亥'],sanChuanBranches:['午','卯','子'],courseBranches:[]}).find(x=>x.label==='行年').entered).toBe(true);
	});
});
