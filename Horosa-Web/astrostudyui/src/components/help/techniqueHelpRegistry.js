// 各技法「操作手册」帮助文档注册表:currentTab → HelpDoc 组件。
// PageHeader 帮助弹窗按当前页查本表渲染对应古籍;新增技法手册=加一行,无需改 PageHeader。
import GuoLaoHelpDoc from '../guolao/GuoLaoHelpDoc';
import AstroHelpDoc from './AstroHelpDoc';
import GermanyHelpDoc from './GermanyHelpDoc';
import ZiweiHelpDoc from './ZiweiHelpDoc';
import BaziHelpDoc from './BaziHelpDoc';
import IndiaHelpDoc from './IndiaHelpDoc';
import LiurengHelpDoc from './LiurengHelpDoc';
import DunjiaHelpDoc from './DunjiaHelpDoc';
import GuazhanHelpDoc from './GuazhanHelpDoc';
import TaiyiHelpDoc from './TaiyiHelpDoc';
import FengshuiHelpDoc from './FengshuiHelpDoc';
import CnyibuHelpDoc from './CnyibuHelpDoc';
import SanshiHelpDoc from './SanshiHelpDoc';
import DirectionHelpDoc from './DirectionHelpDoc';
import AuxchartHelpDoc from './AuxchartHelpDoc';
import RelativeHelpDoc from './RelativeHelpDoc';
import JieqiHelpDoc from './JieqiHelpDoc';
import ShusuanHelpDoc from './ShusuanHelpDoc';
import YanqinHelpDoc from './YanqinHelpDoc';
import CalendarHelpDoc from './CalendarHelpDoc';
import PlanetariumHelpDoc from './PlanetariumHelpDoc';
import CntraditionHelpDoc from './CntraditionHelpDoc';
import Astro3DHelpDoc from './Astro3DHelpDoc';
import XuanshiHelpDoc from './XuanshiHelpDoc';
import AIAnalysisHelpDoc from './AIAnalysisHelpDoc';

export const TECHNIQUE_HELP_DOCS = {
	astrochart: AstroHelpDoc,
	germanytech: GermanyHelpDoc,
	guolao: GuoLaoHelpDoc,
	ziwei: ZiweiHelpDoc,
	bazi: BaziHelpDoc,
	indiachart: IndiaHelpDoc,
	liureng: LiurengHelpDoc,
	dunjia: DunjiaHelpDoc,
	guazhan: GuazhanHelpDoc,
	taiyi: TaiyiHelpDoc,
	fengshui: FengshuiHelpDoc,
	cnyibu: CnyibuHelpDoc,
	sanshiunited: SanshiHelpDoc,
	direction: DirectionHelpDoc,
	auxchart: AuxchartHelpDoc,
	relativechart: RelativeHelpDoc,
	jieqichart: JieqiHelpDoc,
	shusuan: ShusuanHelpDoc,
	yanqin: YanqinHelpDoc,
	calendar: CalendarHelpDoc,
	planetarium: PlanetariumHelpDoc,
	cntradition: CntraditionHelpDoc,
	astrochart3D: Astro3DHelpDoc,
	xuanshi: XuanshiHelpDoc,
	aianalysis: AIAnalysisHelpDoc,
};

export function getTechniqueHelpDoc(currentTab){
	return TECHNIQUE_HELP_DOCS[currentTab] || null;
}
