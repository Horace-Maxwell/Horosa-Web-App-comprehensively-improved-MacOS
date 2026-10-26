
import { ChartData, PalaceData, Star, Gender, AppSettings } from '../types';
import { getLunarDetails, getZodiacYearStemIndex, getZodiacYearBranchIndex, getLunarDateObj, getTrueSolarTime } from './lunarService';

// --- Constants ---

export const PALACE_NAMES = [
  '命宫', '兄弟', '夫妻', '子女', 
  '财帛', '疾厄', '迁移', '交友', 
  '官禄', '田宅', '福德', '父母'
];

export const PALACE_ABBR: Record<string, string> = {
  '命宫': '命', '兄弟': '兄', '夫妻': '夫', '子女': '子',
  '财帛': '财', '疾厄': '疾', '迁移': '迁', '交友': '友',
  '官禄': '官', '田宅': '田', '福德': '福', '父母': '父'
};

export const CHINESE_MONTH_NAMES = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊'];

export const STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
const BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];

// --- Helper Functions ---

const fix = (i: number) => {
  const r = i % 12;
  return r < 0 ? r + 12 : r;
};

// --- Star Calculation Helpers (Shared between Base and Flow) ---

const getLuPos = (stemIdx: number) => {
    // Rule 12: Jia->Yin, Yi->Mao, Bing/Wu->Si, Ding/Ji->Wu, Geng->Shen, Xin->You, Ren->Hai, Gui->Zi
    const luCunMap: Record<number, number> = { 0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0 };
    return luCunMap[stemIdx];
}

const getKuiYuePos = (stemIdx: number, settings: AppSettings) => {
    // Rule 11 (Diagram 9):
    // Jia Wu Geng -> Chou(1) Wei(7)
    // Yi Ji -> Zi(0) Shen(8)
    // Bing Ding -> Hai(11) You(9)
    // Ren Gui -> Mao(3) Si(5)
    // Xin -> Wu(6) Yin(2)
    
    // Note: Standard mapping is often Yang Noble (Day) first, Yin Noble (Night) second.
    // Diagram: Kui (Day) Yue (Night)
    
    if ([0, 4, 6].includes(stemIdx)) { return [1, 7]; } // Jia Wu Geng -> Chou Wei
    else if ([1, 5].includes(stemIdx)) { return [0, 8]; } // Yi Ji -> Zi Shen
    else if ([2, 3].includes(stemIdx)) { return [11, 9]; } // Bing Ding -> Hai You
    else if ([8, 9].includes(stemIdx)) { return [3, 5]; } // Ren Gui -> Mao Si
    else if (stemIdx === 7) { return [6, 2]; } // Xin -> Wu Yin
    
    return [0, 0];
}

const getTianMaPos = (branchIdx: number) => {
    // Rule 18 (Diagram 15):
    // Yin Wu Xu -> Shen(8)
    // Shen Zi Chen -> Yin(2)
    // Si You Chou -> Hai(11)
    // Hai Mao Wei -> Si(5)
    const maMap: Record<number, number> = { 2: 8, 6: 8, 10: 8, 8: 2, 0: 2, 4: 2, 5: 11, 9: 11, 1: 11, 11: 5, 3: 5, 7: 5 };
    return maMap[branchIdx];
}

const getHongXiPos = (branchIdx: number) => {
    // Rule 20 (Diagram 17):
    // Hong Luan: Start Mao(3), Reverse to Year Branch
    const hong = fix(3 - branchIdx);
    // Tian Xi: Opposite of Hong Luan
    const xi = fix(hong + 6);
    return [hong, xi];
}

const getHuoLingPos = (branchIdx: number, hourIdx: number) => {
    // Rule 13 (Diagram 11):
    // Huo Xing:
    // Yin Wu Xu -> Start Chou(1), Clockwise
    // Shen Zi Chen -> Start Yin(2), Clockwise
    // Si You Chou -> Start Mao(3), Clockwise
    // Hai Mao Wei -> Start You(9), Clockwise
    
    // Ling Xing:
    // Yin Wu Xu -> Start Mao(3), Clockwise
    // Shen Zi Chen -> Start Xu(10), Clockwise
    // Si You Chou -> Start Xu(10), Clockwise
    // Hai Mao Wei -> Start Xu(10), Clockwise

    let huoStart = 0;
    let lingStart = 0;

    // Determine Triad
    if ([2, 6, 10].includes(branchIdx)) { // Yin Wu Xu
        huoStart = 1; lingStart = 3;
    } else if ([8, 0, 4].includes(branchIdx)) { // Shen Zi Chen
        huoStart = 2; lingStart = 10;
    } else if ([5, 9, 1].includes(branchIdx)) { // Si You Chou
        huoStart = 3; lingStart = 10;
    } else { // Hai Mao Wei (11, 3, 7)
        huoStart = 9; lingStart = 10;
    }
    
    return [fix(huoStart + hourIdx), fix(lingStart + hourIdx)];
}

// Flow Chang/Qu (Rule 42: "Bu Yong Si Mu Gong")
// Mapping logic: Start at Si(5)/You(9). Move by Stem Index. Skip 1,4,7,10 (Chou, Chen, Wei, Xu).
// Non-Grave Seq: Zi(0), Yin(2), Mao(3), Si(5), Wu(6), Shen(8), You(9), Hai(11).
const NON_GRAVE_SEQ = [0, 2, 3, 5, 6, 8, 9, 11];
const getFlowChangQuPos = (stemIdx: number) => {
    // Determine target index in the non-grave sequence
    // Start for Chang is Si (Index 3 in seq).
    // Start for Qu is You (Index 6 in seq).
    const seqLen = NON_GRAVE_SEQ.length;
    
    // Chang: Shun (Forward)
    const changStartIdx = 3; // Si
    const changTargetIdx = (changStartIdx + stemIdx) % seqLen;
    const changPos = NON_GRAVE_SEQ[changTargetIdx];

    // Qu: Ni (Backward) -> Wait, Rule 42 says "Liu Qu Qi You Wei...". 
    // Usually Qu is also derived from year stem. Some schools say Reverse.
    // Image says: "Jia Yi Shun Liu Qu..." (Jia Yi Flow Qu follows sequence?)
    // Zhong Zhou text usually implies Chang is Forward, Qu is Reverse?
    // Let's stick to standard map which is often Chang Forward, Qu Reverse or specific mapping.
    // Based on "Bu Yong Si Mu":
    
    const quStartIdx = 6; // You
    // Assuming Reverse for Qu as per common An Xing Jue
    // JS modulo bug with negative numbers: ((n % m) + m) % m
    const quTargetIdx = ((quStartIdx - stemIdx) % seqLen + seqLen) % seqLen;
    const quPos = NON_GRAVE_SEQ[quTargetIdx];

    return [changPos, quPos];
}

// --- Data Maps ---

// Ming Zhu (Rule 36): Based on Ming Palace Branch
// Zi=TanLang, Chou=JuMen, Yin=LuCun, Mao=WenQu, Chen=LianZhen, Si=WuQu
// Wu=PoJun, Wei=WuQu, Shen=LianZhen, You=WenQu, Xu=LuCun, Hai=JuMen
const MING_ZHU_MAP = [
    '贪狼', // Zi
    '巨门', // Chou
    '禄存', // Yin
    '文曲', // Mao
    '廉贞', // Chen
    '武曲', // Si
    '破军', // Wu
    '武曲', // Wei
    '廉贞', // Shen
    '文曲', // You
    '禄存', // Xu
    '巨门'  // Hai
]; 

// Shen Zhu (Rule 37): Based on Birth Year Branch
// Zi=HuoXing, Chou=TianXiang, Yin=TianLiang, Mao=TianTong, Chen=WenChang, Si=TianJi
// Wu=HuoXing, Wei=TianXiang, Shen=TianLiang, You=TianTong, Xu=WenChang, Hai=TianJi
const SHEN_ZHU_MAP = [
    '火星', // Zi
    '天相', // Chou
    '天梁', // Yin
    '天同', // Mao
    '文昌', // Chen
    '天机', // Si
    '火星', // Wu
    '天相', // Wei
    '天梁', // Shen
    '天同', // You
    '文昌', // Xu
    '天机'  // Hai
]; 

// 12 Gods Lists
const CHANG_SHENG_12 = ['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养'];
const SUI_JIAN_12 = ['太岁', '晦气', '丧门', '贯索', '官符', '小耗', '大耗', '龙德', '白虎', '天德', '吊客', '病符'];
const BO_SHI_12 = ['博士', '力士', '青龙', '小耗', '将军', '奏书', '飞廉', '喜神', '病符', '大耗', '伏兵', '官府'];
const JIANG_QIAN_12 = ['将星', '攀鞍', '岁驿', '息神', '华盖', '劫煞', '灾煞', '天煞', '指背', '咸池', '月煞', '亡神'];

// --- Brightness Tables ---

// Zhong Zhou (Middle State School)
const BRIGHTNESS_ZHONG_ZHOU: Record<string, string[]> = {
    '紫微': ['平', '庙', '旺', '旺', '得', '旺', '庙', '庙', '旺', '旺', '得', '旺'],
    '天机': ['庙', '陷', '得', '旺', '利', '平', '庙', '陷', '得', '旺', '利', '平'],
    '太阳': ['陷', '不', '旺', '庙', '旺', '旺', '旺', '得', '得', '陷', '不', '陷'],
    '武曲': ['旺', '庙', '得', '利', '庙', '平', '旺', '庙', '得', '利', '庙', '平'],
    '天同': ['旺', '不', '利', '平', '平', '庙', '陷', '不', '旺', '平', '平', '庙'],
    '廉贞': ['平', '利', '庙', '平', '利', '陷', '平', '利', '庙', '平', '利', '陷'],
    '天府': ['庙', '庙', '庙', '得', '庙', '得', '旺', '庙', '得', '旺', '庙', '得'],
    '太阴': ['庙', '庙', '旺', '陷', '陷', '陷', '不', '不', '利', '不', '旺', '庙'],
    '贪狼': ['旺', '庙', '平', '利', '庙', '陷', '旺', '庙', '平', '利', '庙', '陷'],
    '巨门': ['旺', '不', '庙', '庙', '陷', '旺', '旺', '不', '庙', '庙', '陷', '旺'],
    '天相': ['庙', '庙', '庙', '陷', '得', '得', '庙', '得', '庙', '陷', '得', '得'],
    '天梁': ['庙', '旺', '庙', '庙', '庙', '陷', '庙', '旺', '陷', '得', '庙', '陷'],
    '七杀': ['旺', '庙', '庙', '旺', '庙', '平', '旺', '庙', '庙', '庙', '庙', '平'],
    '破军': ['庙', '旺', '得', '陷', '旺', '平', '庙', '旺', '得', '陷', '旺', '平'],
    '文昌': ['陷', '利', '陷', '利', '得', '庙', '陷', '利', '得', '庙', '陷', '利'],
    '文曲': ['得', '庙', '平', '旺', '得', '庙', '陷', '旺', '得', '庙', '陷', '旺'],
    '火星': ['陷', '得', '庙', '利', '陷', '得', '庙', '利', '陷', '得', '庙', '利'],
    '铃星': ['陷', '得', '庙', '利', '陷', '得', '庙', '利', '陷', '得', '庙', '利'],
    '擎羊': ['平', '陷', '庙', '平', '陷', '庙', '平', '陷', '庙', '平', '陷', '庙'],
    '陀罗': ['陷', '平', '庙', '陷', '平', '庙', '陷', '平', '庙', '陷', '平', '庙'],
};

const BRIGHTNESS_QUAN_SHU: Record<string, string[]> = {
    ...BRIGHTNESS_ZHONG_ZHOU 
};

// Five Elements Color Mapping
export const getElementColor = (char: string): string => {
    const stems: Record<string, string> = {
        '甲': 'text-green-600', '乙': 'text-green-600', 
        '丙': 'text-ziwei-red', '丁': 'text-ziwei-red', 
        '戊': 'text-amber-700', '己': 'text-amber-700', 
        '庚': 'text-blue-600', '辛': 'text-blue-600', 
        '壬': 'text-gray-900', '癸': 'text-gray-900'  
    };
    const branches: Record<string, string> = {
        '寅': 'text-green-600', '卯': 'text-green-600', 
        '巳': 'text-ziwei-red', '午': 'text-ziwei-red', 
        '辰': 'text-amber-700', '戌': 'text-amber-700', '丑': 'text-amber-700', '未': 'text-amber-700',
        '申': 'text-blue-600', '酉': 'text-blue-600', 
        '亥': 'text-gray-900', '子': 'text-gray-900'  
    };
    return stems[char] || branches[char] || 'text-gray-800';
};

const getNayinBureau = (stemIdx: number, branchIdx: number): { name: string; num: number } => {
  const stemPair = Math.floor(stemIdx / 2);
  const branchPair = Math.floor(branchIdx / 2);
  const matrix = [
    [4, 2, 6, 4, 2, 6], // Jia/Yi
    [2, 6, 5, 2, 6, 5], // Bing/Ding
    [6, 5, 3, 6, 5, 3], // Wu/Ji
    [5, 3, 4, 5, 3, 4], // Geng/Xin
    [3, 4, 2, 3, 4, 2], // Ren/Gui
  ];
  const val = matrix[stemPair][branchPair];
  const names: Record<number, string> = { 2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局" };
  return { name: names[val], num: val };
};

export const getSiHua = (stemIndex: number, settings: AppSettings): Record<string, '禄'|'权'|'科'|'忌'> => {
  let lu = '', quan = '', ke = '', ji = '';

  // Rule 10 (Image 8): An Si Hua
  switch(stemIndex) {
      case 0: [lu, quan, ke, ji] = ['廉贞', '破军', '武曲', '太阳']; break; // 甲廉破武阳
      case 1: [lu, quan, ke, ji] = ['天机', '天梁', '紫微', '太阴']; break; // 乙机梁紫阴
      case 2: [lu, quan, ke, ji] = ['天同', '天机', '文昌', '廉贞']; break; // 丙同机昌廉
      case 3: [lu, quan, ke, ji] = ['太阴', '天同', '天机', '巨门']; break; // 丁阴同机巨
      case 4: 
        if (settings.siHua.wu === 'tan_yin_yang_ji') [lu, quan, ke, ji] = ['贪狼', '太阴', '太阳', '天机']; // 戊贪阴阳机 (Config option)
        else [lu, quan, ke, ji] = ['贪狼', '太阴', '右弼', '天机']; // Default: Tan Yin You Ji
        break;
      case 5: [lu, quan, ke, ji] = ['武曲', '贪狼', '天梁', '文曲']; break; // 己武贪梁曲
      case 6: 
        if (settings.siHua.geng === 'yang_wu_tong_yin') [lu, quan, ke, ji] = ['太阳', '武曲', '太阴', '天同']; // 庚阳武阴同 (Image 8)
        else if (settings.siHua.geng === 'yang_wu_yin_tong') [lu, quan, ke, ji] = ['太阳', '武曲', '天同', '太阴'];
        else [lu, quan, ke, ji] = ['太阳', '武曲', '天同', '天相']; // Fallback
        break;
      case 7: [lu, quan, ke, ji] = ['巨门', '太阳', '文曲', '文昌']; break; // 辛巨阳曲昌
      case 8: 
        if (settings.siHua.ren === 'liang_zi_zuo_wu') [lu, quan, ke, ji] = ['天梁', '紫微', '左辅', '武曲']; // 壬梁紫左武 (Image 8)
        else [lu, quan, ke, ji] = ['天梁', '紫微', '天府', '武曲'];
        break;
      case 9: 
        if (settings.siHua.gui === 'po_ju_yin_tan') [lu, quan, ke, ji] = ['破军', '巨门', '太阴', '贪狼']; // 癸破巨阴贪 (Image 8)
        else [lu, quan, ke, ji] = ['破军', '巨门', '太阳', '贪狼']; 
        break;
  }
  
  const result: Record<string, '禄'|'权'|'科'|'忌'> = {};
  if (lu) result[lu] = '禄';
  if (quan) result[quan] = '权';
  if (ke) result[ke] = '科';
  if (ji) result[ji] = '忌';
  return result;
};

export const getMonthStem = (yearStemIdx: number, monthIdx: number): number => {
  const startStemMap: Record<number, number> = { 0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0 };
  const startStem = startStemMap[yearStemIdx % 5];
  return (startStem + (monthIdx - 1)) % 10;
};

// Calculate Flow Stars based on current time state
export const calculateFlowStars = (
    chart: ChartData,
    flowState: any, 
    settings: AppSettings,
    activeLevel: 'birth' | 'daxian' | 'year' | 'month' | 'day' | 'hour'
): Record<number, Star[]> => {
    
    const flowMap: Record<number, Star[]> = {};
    const addStar = (idx: number, star: Star) => {
        const i = fix(idx);
        if (!flowMap[i]) flowMap[i] = [];
        flowMap[i].push(star);
    };

    const levels = ['daxian', 'year', 'month', 'day', 'hour'];
    // Determine which layers are active based on view level
    const activeIdx = levels.indexOf(activeLevel === 'birth' ? 'none' : activeLevel);
    
    // Configs for each layer
    const layers = [
        { key: 'daxian', stem: flowState.stems.daxian, branch: chart.palaces.find(p=>p.index===flowState.daXianIndex)?.earthlyBranch ? BRANCHES.indexOf(chart.palaces.find(p=>p.index===flowState.daXianIndex)!.earthlyBranch) : 0, label: '大', active: activeIdx >= 0 },
        { key: 'liunian', stem: flowState.stems.liunian, branch: flowState.liuNianIndex, label: '年', active: activeIdx >= 1 },
        { key: 'liuyue', stem: flowState.stems.liuyue, branch: flowState.liuYueIndex, label: '月', active: activeIdx >= 2 },
        { key: 'liuri', stem: flowState.stems.liuri, branch: flowState.liuRiIndex, label: '日', active: activeIdx >= 3 },
        { key: 'liushi', stem: flowState.stems.liushi, branch: flowState.liuShiIndex, label: '时', active: activeIdx >= 4 },
    ];

    layers.forEach(layer => {
        if (!layer.active) return;
        const { stem, branch, label, key } = layer;

        // 1. Lu / Yang / Tuo
        const luPos = getLuPos(stem);
        addStar(luPos, { name: `${label}禄`, type: 'flow', layer: key as any });
        addStar(luPos + 1, { name: `${label}羊`, type: 'flow', layer: key as any });
        addStar(luPos - 1, { name: `${label}陀`, type: 'flow', layer: key as any });

        // 2. Kui / Yue
        const [kui, yue] = getKuiYuePos(stem, settings);
        addStar(kui, { name: `${label}魁`, type: 'flow', layer: key as any });
        addStar(yue, { name: `${label}钺`, type: 'flow', layer: key as any });

        // 3. Flow Chang / Qu (If enabled)
        if (settings.display.showFlowChangQu) {
            const [chang, qu] = getFlowChangQuPos(stem);
            addStar(chang, { name: `${label}昌`, type: 'flow', layer: key as any });
            addStar(qu, { name: `${label}曲`, type: 'flow', layer: key as any });
        }

        // 4. Flow Ma (If enabled)
        if (settings.display.showFlowMa) {
            const maPos = getTianMaPos(branch);
            addStar(maPos, { name: `${label}马`, type: 'flow', layer: key as any });
        }

        // 5. Flow Hong / Xi (If enabled)
        if (settings.display.showFlowHongXi) {
            const [hong, xi] = getHongXiPos(branch);
            addStar(hong, { name: `${label}鸾`, type: 'flow', layer: key as any });
            addStar(xi, { name: `${label}喜`, type: 'flow', layer: key as any });
        }
    });

    return flowMap;
}

export const calculateChart = (
  name: string,
  date: Date,
  timeIndex: number,
  gender: Gender,
  settings: AppSettings,
  longitude?: number // Add longitude parameter
): ChartData => {
  
  // Calculate True Solar Time if longitude is provided
  let effectiveDate = date;
  let trueSolarDateStr: string | undefined;

  if (longitude !== undefined && !isNaN(longitude)) {
      effectiveDate = getTrueSolarTime(date, longitude);
      const hStr = effectiveDate.getHours().toString().padStart(2, '0');
      const mStr = effectiveDate.getMinutes().toString().padStart(2, '0');
      trueSolarDateStr = `真太阳时 ${hStr}:${mStr}`;

      // Recalculate Time Index based on True Solar Time
      // Use the helper logic from InputForm (or similar simple logic): (h+1)/2 % 12
      timeIndex = Math.floor((effectiveDate.getHours() + 1) / 2) % 12;
  }

  const lunarData = getLunarDetails(effectiveDate, timeIndex);
  const monthIdx = Math.abs(lunarData.lunarMonth); 
  const hourIdx = timeIndex; 
  const dayIdx = lunarData.lunarDay; 

  const mingPos = fix(2 + (monthIdx - 1) - hourIdx);
  const shenPos = fix(2 + (monthIdx - 1) + hourIdx);

  const palaces: PalaceData[] = Array.from({ length: 12 }).map((_, i) => ({
    index: i,
    earthlyBranch: BRANCHES[i],
    heavenlyStem: '',
    name: '',
    isBodyPalace: i === shenPos,
    majorStars: [],
    minorStars: [],
    auxStars: [],
    badStars: [],
    godsStars: [],
    flowStars: [],
    ageRange: [0, 0],
    smallRange: [],
  }));

  PALACE_NAMES.forEach((n, i) => {
    const idx = fix(mingPos - i);
    palaces[idx].name = n;
  });

  const lunarYearStemIdx = Math.floor(getZodiacYearStemIndex(lunarData.lunarYear)); 
  const startStemMap: Record<number, number> = { 0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0 };
  const yinStemStart = startStemMap[lunarYearStemIdx % 5];
  for (let i = 0; i < 12; i++) {
    const stemAtYin = yinStemStart;
    const currentStem = (stemAtYin + fix(i - 2)) % 10;
    palaces[i].heavenlyStem = STEMS[currentStem];
  }

  const mingStemName = palaces[mingPos].heavenlyStem;
  const mingStemIdx = STEMS.indexOf(mingStemName);
  const mingBranchIdx = mingPos;
  const bureau = getNayinBureau(mingStemIdx, mingBranchIdx);

  const isYangYear = (lunarYearStemIdx % 2) === 0;
  const isMale = gender === Gender.MALE;
  const isClockwise = (isYangYear && isMale) || (!isYangYear && !isMale);
  
  let maxAge = 0;
  for (let i = 0; i < 12; i++) {
    const steps = i;
    const pIdx = isClockwise ? fix(mingPos + steps) : fix(mingPos - steps);
    const startAge = bureau.num + (i * 10);
    palaces[pIdx].ageRange = [startAge, startAge + 9];
    if (startAge + 9 > maxAge) maxAge = startAge + 9;
  }

  // --- Xiao Xian (Small Limit) Logic ---
  const yearBranch = getZodiacYearBranchIndex(lunarData.lunarYear);
  let xiaoXianStartIdx = 0;
  // Rule:
  // Yin(2), Wu(6), Xu(10) -> Chen(4)
  if ([2, 6, 10].includes(yearBranch)) xiaoXianStartIdx = 4;
  // Shen(8), Zi(0), Chen(4) -> Xu(10)
  else if ([8, 0, 4].includes(yearBranch)) xiaoXianStartIdx = 10;
  // Si(5), You(9), Chou(1) -> Wei(7)
  else if ([5, 9, 1].includes(yearBranch)) xiaoXianStartIdx = 7;
  // Hai(11), Mao(3), Wei(7) -> Chou(1)
  else xiaoXianStartIdx = 1;

  // Direction: Male = Clockwise (+1), Female = Counter-Clockwise (-1)
  const xxDirection = isMale ? 1 : -1;

  // Calculate ages up to maxAge (end of last Da Xian)
  for (let age = 1; age <= maxAge; age++) {
      const steps = age - 1;
      const idx = fix(xiaoXianStartIdx + (steps * xxDirection));
      palaces[idx].smallRange.push(age);
  }

  // Calculate Zi Wei Star Position
  // Based on specific An Xing Jue algorithm (5 Cases)
  const getZiWeiIndex = (day: number, b: number): number => {
     const remainder = day % b;
     const quotient = Math.floor(day / b);

     let pos = 0;
     let direction = 1; // 1 for clockwise, -1 for counter-clockwise

     if (remainder === 0) {
        // Case 1: Divisible
        // "Integer quotient is location"
        pos = quotient;
        direction = 1;
     } else {
        const x = b - remainder;
        const y = (day + x) / b; // This is quotient + 1

        if (x % 2 === 0) {
           // Case 2: X is Even
           // "X + Y = Location"
           pos = x + y;
           direction = 1;
        } else {
           // X is Odd
           if (y > x) {
              // Case 3: Y > X
              // "Y - X = Location"
              pos = y - x;
              direction = 1;
           } else if (x > y) {
              // Case 4: X > Y
              // "X - Y = Location (Counter-Clockwise)"
              pos = x - y;
              direction = -1;
           } else {
              // Case 5: X = Y
              // "X - Y = 0 ... In Chou Palace (Index 1)"
              return 1;
           }
        }
     }

     // Calculate actual index relative to Yin (Index 2)
     // Steps are 1-based (e.g., pos 1 = Yin)
     // Clockwise: 2 + (pos - 1)
     // Counter: 2 - (pos - 1)
     if (direction === 1) {
         return fix(2 + (pos - 1));
     } else {
         return fix(2 - (pos - 1));
     }
  };
  
  const ziWeiPos = getZiWeiIndex(dayIdx, bureau.num);
  
  // Tian Fu Placement: Converges with Zi Wei at Yin(2) and Shen(8)
  // Standard Formula: (4 - ZiWei) % 12  (Or 16 - ZiWei % 12) relative to Zi=0
  const tianFuPos = fix(4 - ziWeiPos); 

  const placeMajor = (base: number, offset: number, name: string) => {
    palaces[fix(base + offset)].majorStars.push({ name, type: 'major' });
  };
  
  // Zi Wei Series (Counter-Clockwise)
  // Zi Wei, Tian Ji, (Empty), Tai Yang, Wu Qu, Tian Tong, (Empty), (Empty), Lian Zhen
  placeMajor(ziWeiPos, 0, '紫微');
  placeMajor(ziWeiPos, -1, '天机');
  placeMajor(ziWeiPos, -3, '太阳');
  placeMajor(ziWeiPos, -4, '武曲');
  placeMajor(ziWeiPos, -5, '天同');
  placeMajor(ziWeiPos, -8, '廉贞');

  // Tian Fu Series (Clockwise)
  // Tian Fu, Tai Yin, Tan Lang, Ju Men, Tian Xiang, Tian Liang, Qi Sha, (Empty 3), Po Jun
  placeMajor(tianFuPos, 0, '天府');
  placeMajor(tianFuPos, 1, '太阴');
  placeMajor(tianFuPos, 2, '贪狼');
  placeMajor(tianFuPos, 3, '巨门');
  placeMajor(tianFuPos, 4, '天相');
  placeMajor(tianFuPos, 5, '天梁');
  placeMajor(tianFuPos, 6, '七杀');
  placeMajor(tianFuPos, 10, '破军');

  // Wen Chang / Wen Qu
  const wenChangPos = fix(10 - hourIdx);
  const wenQuPos = fix(4 + hourIdx);
  palaces[wenChangPos].auxStars.push({ name: '文昌', type: 'aux' });
  palaces[wenQuPos].auxStars.push({ name: '文曲', type: 'aux' });

  // Zuo Fu / You Bi
  const zuoFuPos = fix(4 + (monthIdx - 1));
  const youBiPos = fix(10 - (monthIdx - 1));
  palaces[zuoFuPos].auxStars.push({ name: '左辅', type: 'aux' });
  palaces[youBiPos].auxStars.push({ name: '右弼', type: 'aux' });

  // Huo Xing / Ling Xing (Rule 13)
  const [huoPos, lingPos] = getHuoLingPos(yearBranch, hourIdx);
  palaces[huoPos].badStars.push({ name: '火星', type: 'bad' });
  palaces[lingPos].badStars.push({ name: '铃星', type: 'bad' });

  // Lu Cun / Qing Yang / Tuo Luo (Rule 12)
  const luPos = getLuPos(lunarYearStemIdx);
  palaces[luPos].auxStars.push({ name: '禄存', type: 'aux' });
  palaces[fix(luPos + 1)].badStars.push({ name: '擎羊', type: 'bad' }); // Qian (Clockwise)
  palaces[fix(luPos - 1)].badStars.push({ name: '陀罗', type: 'bad' }); // Hou (Counter-Clockwise)

  // Tian Kui / Tian Yue (Rule 11)
  const [kui, yue] = getKuiYuePos(lunarYearStemIdx, settings);
  palaces[kui].auxStars.push({ name: '天魁', type: 'aux' });
  palaces[yue].auxStars.push({ name: '天钺', type: 'aux' });

  const placeMinor = (idx: number, name: string, type: Star['type'] = 'minor') => 
      palaces[fix(idx)].minorStars.push({ name, type });

  // Tian Ma (Rule 18)
  const maBase = settings.anXing.tianMa === 'month' ? (monthIdx - 1) : yearBranch; 
  const maPos = getTianMaPos(maBase % 12) || getTianMaPos(yearBranch);
  palaces[maPos].auxStars.push({ name: '天马', type: 'aux' });

  // Di Kong / Di Jie (Rule 13 - Wait, Di Kong/Jie are Rule 13 in text? No, standard logic from previous context or image not provided for Kong/Jie in this set?
  // Actually Image 18 mentions Tian Kong. Image 15 mentions Tian Kong and Ma.
  // Standard Di Kong/Di Jie is based on Hour.
  // Jie: Hai(11) CW to Hour. Kong: Hai(11) CCW to Hour.
  const jiePos = fix(11 + hourIdx);
  const kongPos = fix(11 - hourIdx);
  palaces[jiePos].badStars.push({ name: '地劫', type: 'bad' });
  palaces[kongPos].badStars.push({ name: '地空', type: 'bad' });

  // Tian Kong (Rule 18 / Image 15): "Jia Qian Yi Wei" -> Year Branch + 1 (Clockwise)
  const tianKongPos = fix(yearBranch + 1);
  placeMinor(tianKongPos, '天空', 'bad');

  // Xun Kong (Rule 17): Based on Year Stem/Branch.
  // Find where Gui is relative to current year. The next two are void.
  // E.g. Jia Zi (0,0). Gui is at You (9). Empty are Xu(10), Hai(11).
  const distToGui = (9 - lunarYearStemIdx + 10) % 10; // Steps from Stem to Gui
  const guiBranch = (yearBranch + distToGui) % 12; // Branch where Gui falls
  placeMinor(guiBranch + 1, '旬空', 'bad');
  placeMinor(guiBranch + 2, '旬空', 'bad');

  // Jie Kong (Rule 16 / Image 14):
  // Based on Year Stem. Divides into Zheng and Pang.
  const jieKongMap: Record<number, [number, number]> = {
      0: [8, 9], // Jia -> Shen You
      5: [9, 8], // Ji -> You Shen (Sequence reversed in image?) Image: Ji -> You(Zheng) Shen(Fu). My array: [Zheng, Fu] logic needed.
      // Let's store [YangBranch, YinBranch] for the pair usually.
      // Map based on Image 14 text:
      // Jia(0): Shen(8), You(9). 0 is Yang. 8 is Yang (Zheng). 9 is Yin (Fu).
      // Yi(1): Wu(6), Wei(7). 1 is Yin. 7 is Yin (Zheng). 6 is Yang (Fu).
      // Bing(2): Chen(4), Si(5). 2 is Yang. 4 is Yang (Zheng). 5 is Yin (Fu).
      // Ding(3): Yin(2), Mao(3). 3 is Yin. 3 is Yin (Zheng). 2 is Yang (Fu).
      // Wu(4): Zi(0), Chou(1). 4 is Yang. 0 is Yang (Zheng). 1 is Yin (Fu).
      // Ji(5): You(9), Shen(8). 5 is Yin. 9 is Yin (Zheng). 8 is Yang (Fu).
      // Geng(6): Wu(6), Wei(7). 6 is Yang. 6 is Yang (Zheng). 7 is Yin (Fu).
      // Xin(7): Chen(4), Si(5). 7 is Yin. 5 is Yin (Zheng). 4 is Yang (Fu).
      // Ren(8): Yin(2), Mao(3). 8 is Yang. 2 is Yang (Zheng). 3 is Yin (Fu).
      // Gui(9): Zi(0), Chou(1). 9 is Yin. 1 is Yin (Zheng). 0 is Yang (Fu).
  };
  
  // Revised Map storing [Zheng, Fu]
  const jieKongCorrect: Record<number, [number, number]> = {
      0: [8, 9], 1: [7, 6], 2: [4, 5], 3: [3, 2], 4: [0, 1],
      5: [9, 8], 6: [6, 7], 7: [5, 4], 8: [2, 3], 9: [1, 0]
  };

  const [jkZheng, jkFu] = jieKongCorrect[lunarYearStemIdx];
  placeMinor(jkZheng, '截空', 'bad'); // Mark as Zheng? Or just name it Jie Kong.
  // Optional: Distinguish visual if needed, currently both named Jie Kong.
  // Only Zheng Kong is "Heavy".
  if (settings.anXing.jieKong === 'single') {
       placeMinor(jkZheng, '截空', 'bad');
  } else {
       placeMinor(jkZheng, '截空', 'bad');
       placeMinor(jkFu, '截空', 'bad'); // Deputy
  }

  // Tai Fu / Feng Gao (Rule 28): Based on Hour
  // Tai Fu: Wu(6) CW to Hour
  placeMinor(6 + hourIdx, '台辅', 'good');
  // Feng Gao: Yin(2) CW to Hour
  placeMinor(2 + hourIdx, '封诰', 'good');

  // Tian Xing / Tian Yao (Rule 29): Based on Month
  // Tian Xing: You(9) CW to Month
  placeMinor(9 + (monthIdx - 1), '天刑', 'bad');
  // Tian Yao: Chou(1) CW to Month
  placeMinor(1 + (monthIdx - 1), '天姚', 'bad');

  // Jie Shen (Rule 30 / Image 26):
  // Single Month: Shen(8). Double Month: Shen(8)? No, see list.
  // Jan/Feb -> Shen(8)
  // Mar/Apr -> Xu(10)
  // May/Jun -> Zi(0)
  // Jul/Aug -> Yin(2)
  // Sep/Oct -> Chen(4)
  // Nov/Dec -> Wu(6)
  const jieShenPos = fix(8 + (Math.floor((monthIdx - 1) / 2) * 2));
  placeMinor(jieShenPos, '解神', 'good');
  
  // Nian Jie (Rule 25 / Image 22): Xu(10) CCW to Year Branch
  placeMinor(10 - yearBranch, '年解', 'good');

  // Tian Wu (Rule 30 / Image 26 text):
  // 1,5,9 (ShenZiChen) -> Si(5)
  // 2,6,10 (HaiMaoWei) -> Shen(8)
  // 3,7,11 (YinWuXu) -> Hai(11)
  // 4,8,12 (SiYouChou) -> Yin(2)
  const tianWuMap: Record<number, number> = { 1:5, 5:5, 9:5, 2:8, 6:8, 10:8, 3:11, 7:11, 11:11, 4:2, 8:2, 12:2 };
  placeMinor(tianWuMap[monthIdx], '天巫', 'good');

  // Tian Yue (Rule 31 / Image 25):
  const tianYueStarMap: Record<number, number> = { 1:10, 2:5, 3:4, 4:2, 5:7, 6:3, 7:11, 8:7, 9:2, 10:6, 11:10, 12:2 };
  placeMinor(tianYueStarMap[monthIdx], '天月', 'bad');

  // Yin Sha (Rule 32 / Image 26):
  const yinShaMap: Record<number, number> = { 1:2, 7:2, 2:0, 8:0, 3:10, 9:10, 4:8, 10:8, 5:6, 11:6, 6:4, 12:4 };
  placeMinor(yinShaMap[monthIdx], '阴煞', 'bad');

  // Tian Guan / Tian Fu (Rule 14 / Image 12):
  const tianGuanMap: Record<number, number> = { 0:7, 1:4, 2:5, 3:2, 4:3, 5:9, 6:11, 7:9, 8:10, 9:6 };
  const tianFuMap: Record<number, number> = { 0:9, 1:8, 2:0, 3:11, 4:3, 5:2, 6:6, 7:5, 8:6, 9:5 };
  placeMinor(tianGuanMap[lunarYearStemIdx], '天官', 'good');
  placeMinor(tianFuMap[lunarYearStemIdx], '天福', 'good');

  // Tian Ku / Tian Xu (Rule 19 / Image 16):
  // Ku: Wu(6) CCW to Year
  placeMinor(6 - yearBranch, '天哭', 'bad');
  // Xu: Wu(6) CW to Year
  placeMinor(6 + yearBranch, '天虚', 'bad');

  // Long Chi / Feng Ge (Rule 27 / Image 21):
  // Long: Chen(4) CW to Year
  placeMinor(4 + yearBranch, '龙池', 'good');
  // Feng: Xu(10) CCW to Year
  placeMinor(10 - yearBranch, '凤阁', 'good');

  // Hong Luan / Tian Xi (Rule 20)
  const [hongLuan, tianXi] = getHongXiPos(yearBranch);
  placeMinor(hongLuan, '红鸾', 'good');
  placeMinor(tianXi, '天喜', 'good');

  // Gu Chen / Gua Su (Rule 21 / Image 18)
  // YinMaoChen(2,3,4) -> Si(5), Chou(1)
  // SiWuWei(5,6,7) -> Shen(8), Chen(4)
  // ShenYouXu(8,9,10) -> Hai(11), Wei(7)
  // HaiZiChou(11,0,1) -> Yin(2), Xu(10)
  const guMap: Record<number, number> = { 2:5, 3:5, 4:5, 5:8, 6:8, 7:8, 8:11, 9:11, 10:11, 11:2, 0:2, 1:2 };
  const guaMap: Record<number, number> = { 2:1, 3:1, 4:1, 5:4, 6:4, 7:4, 8:7, 9:7, 10:7, 11:10, 0:10, 1:10 };
  placeMinor(guMap[yearBranch], '孤辰', 'bad');
  placeMinor(guaMap[yearBranch], '寡宿', 'bad');

  // Fei Lian (Rule 24 / Image 20):
  // Zi(0)->Shen(8), Chou(1)->You(9). Year Branch + 8.
  placeMinor(yearBranch + 8, '蜚廉', 'bad');

  // Po Sui (Rule 24 / Image 20):
  // Zi Wu Mao You -> Si(5)
  // Chen Xu Chou Wei -> Chou(1)
  // Yin Shen Si Hai -> You(9)
  let poSuiPos = 0;
  if ([0,6,3,9].includes(yearBranch)) poSuiPos = 5;
  else if ([4,10,1,7].includes(yearBranch)) poSuiPos = 1;
  else poSuiPos = 9;
  placeMinor(poSuiPos, '破碎', 'bad');

  // Hua Gai (Rule 24):
  let huaGaiPos = 0;
  if ([0,4,8].includes(yearBranch)) huaGaiPos = 4; // ShenZiChen -> Chen
  else if ([5,9,1].includes(yearBranch)) huaGaiPos = 1; // SiYouChou -> Chou
  else if ([2,6,10].includes(yearBranch)) huaGaiPos = 10; // YinWuXu -> Xu
  else huaGaiPos = 7; // HaiMaoWei -> Wei
  placeMinor(huaGaiPos, '华盖', 'good');

  // Xian Chi (Rule 24):
  let xianChiPos = 0;
  if ([0,4,8].includes(yearBranch)) xianChiPos = 9; // ShenZiChen -> You
  else if ([5,9,1].includes(yearBranch)) xianChiPos = 6; // SiYouChou -> Wu
  else if ([2,6,10].includes(yearBranch)) xianChiPos = 3; // YinWuXu -> Mao
  else xianChiPos = 0; // HaiMaoWei -> Zi
  placeMinor(xianChiPos, '咸池', 'bad');
  
  // Tian De (Rule 25 / Image 22): You(9) CW to Year
  placeMinor(9 + yearBranch, '天德', 'good');

  // Tian Cai / Tian Shou (Rule 26 / Image 22):
  // Cai: Ming CW to Year
  placeMinor(mingPos + yearBranch, '天才', 'good');
  // Shou: Shen CW to Year
  placeMinor(shenPos + yearBranch, '天寿', 'good');

  // San Tai / Ba Zuo (Rule 34 / Image 27):
  // San Tai: Zuo Fu CW to Day
  placeMinor(zuoFuPos + dayIdx - 1, '三台', 'good');
  // Ba Zuo: You Bi CCW to Day
  placeMinor(youBiPos - (dayIdx - 1), '八座', 'good');

  // En Guang / Tian Gui (Rule 35 / Image 28):
  // En Guang: Wen Chang CW to Day, Back 1
  placeMinor(wenChangPos + dayIdx - 2, '恩光', 'good');
  // Tian Gui: Wen Qu CW to Day, Back 1
  placeMinor(wenQuPos + dayIdx - 2, '天贵', 'good');

  // Tian Chu (Rule 15 / Image 13):
  // Jia Ding -> Si(5)
  // Yi Wu Xin -> Wu(6)
  // Bing -> Zi(0)
  // Ji -> Shen(8)
  // Geng -> Yin(2)
  // Ren -> You(9)
  // Gui -> Hai(11)
  const tianChuMap: Record<number, number> = { 0:5, 3:5, 1:6, 4:6, 7:6, 2:0, 5:8, 6:2, 8:9, 9:11 };
  placeMinor(tianChuMap[lunarYearStemIdx], '天厨', 'good');

  // Tian Shang / Tian Shi (Rule 33 / Image 27 Text):
  // Shang in Friend (8), Shi in Health (6) relative to Ming (1).
  const friendPos = fix(mingPos - 7); // Ming is 0 offset. 1, 2, 3... 8 is -7 steps.
  const healthPos = fix(mingPos - 5); // Health is 6. -5 steps.
  placeMinor(friendPos, '天伤', 'bad');
  placeMinor(healthPos, '天使', 'bad');

  // Da Hao (Rule 23 / Image 20):
  // Yang Year: Opposite + 1
  // Yin Year: Opposite - 1
  const oppYearPos = fix(yearBranch + 6);
  const isYangBranch = [0,2,4,6,8,10].includes(yearBranch);
  const daHaoPos = isYangBranch ? fix(oppYearPos + 1) : fix(oppYearPos - 1);
  // Note: Da Hao is distinct from Sui Jian's "Da Hao". This is "Year Branch Da Hao".
  // Usually this star is just called "Da Hao" in minor stars.
  placeMinor(daHaoPos, '大耗', 'bad');
  
  // Jie Sha (Rule 22 / Image 20):
  // ShenZiChen->Si, YinWuXu->Hai, SiYouChou->Yin, HaiMaoWei->Shen
  let jieShaPos = 0;
  if ([8,0,4].includes(yearBranch)) jieShaPos = 5;
  else if ([2,6,10].includes(yearBranch)) jieShaPos = 11;
  else if ([5,9,1].includes(yearBranch)) jieShaPos = 2;
  else jieShaPos = 8;
  placeMinor(jieShaPos, '劫煞', 'bad');


  // --- 12 Gods ---

  // Chang Sheng 12 (Rule 38)
  let csStart = 0;
  // Rule 41: Earth (5) -> Shen (8).
  if (bureau.num === 5) { 
       csStart = 8; 
  } else {
      const changShengStartMap: any = { 2: 8, 3: 11, 4: 5, 6: 2 };
      csStart = changShengStartMap[bureau.num];
  }
  
  const csClockwise = (isMale && isYangYear) || (!isMale && !isYangYear);
  for (let i = 0; i < 12; i++) {
    const idx = csClockwise ? fix(csStart + i) : fix(csStart - i);
    palaces[idx].godsStars.push({ name: CHANG_SHENG_12[i], type: 'chang' });
  }

  // Sui Jian 12 (Rule 39)
  for (let i = 0; i < 12; i++) {
    const idx = fix(yearBranch + i);
    palaces[idx].godsStars.push({ name: SUI_JIAN_12[i], type: 'sui' });
  }

  // Bo Shi 12 (Rule 41)
  for (let i = 0; i < 12; i++) {
    const idx = csClockwise ? fix(luPos + i) : fix(luPos - i);
    palaces[idx].godsStars.push({ name: BO_SHI_12[i], type: 'bo' });
  }

  // Jiang Qian 12 (Rule 40)
  let jiangStart = 0;
  if ([2,6,10].includes(yearBranch)) jiangStart = 6; // YinWuXu -> Wu
  else if ([8,0,4].includes(yearBranch)) jiangStart = 0; // ShenZiChen -> Zi
  else if ([5,9,1].includes(yearBranch)) jiangStart = 9; // SiYouChou -> You
  else jiangStart = 3; // HaiMaoWei -> Mao
  for (let i = 0; i < 12; i++) {
    const idx = fix(jiangStart + i);
    palaces[idx].godsStars.push({ name: JIANG_QIAN_12[i], type: 'jiang' });
  }

  const brightnessMap = settings.anXing.brightness === 'quan' ? BRIGHTNESS_QUAN_SHU : BRIGHTNESS_ZHONG_ZHOU;
  palaces.forEach(p => {
      [...p.majorStars, ...p.auxStars, ...p.badStars, ...p.minorStars].forEach(s => {
          if (brightnessMap[s.name]) {
              const bIndex = p.index; 
              s.brightness = brightnessMap[s.name][bIndex] as any;
          }
      });
  });

  const trans = getSiHua(lunarYearStemIdx, settings);
  palaces.forEach(p => {
    [...p.majorStars, ...p.auxStars, ...p.badStars].forEach(s => {
      if (trans[s.name]) s.modifier = trans[s.name];
    });
  });

  const mingZhu = MING_ZHU_MAP[mingPos]; 
  const shenZhu = SHEN_ZHU_MAP[yearBranch]; 
  
  // Zi Dou: Zi Year Dou Jun = 0 (Zi) - (Month-1) + Hour
  const ziDouIdx = fix(0 - (monthIdx - 1) + hourIdx);
  const ziDou = BRANCHES[ziDouIdx] + '宫';

  // Solar Time String (Exact match from input date)
  const timeStr = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  
  return {
    lunarDateStr: `农历 ${lunarData.lunarYear}年 ${lunarData.lunarMonthChinese} ${lunarData.lunarDayChinese} ${lunarData.timeGanZhi}时`,
    solarDateStr: `阳历 ${date.getFullYear()}年${date.getMonth()+1}月${date.getDate()}日 ${timeStr}`,
    trueSolarDateStr, // Return True Solar String
    bureau: bureau.name,
    mingPalaceIndex: mingPos,
    shenPalaceIndex: shenPos,
    gender,
    yinYang: isYangYear ? '阳' : '阴',
    palaces,
    name,
    baZi: {
      year: lunarData.ganZhiYear,
      month: lunarData.ganZhiMonth,
      day: lunarData.ganZhiDay,
      time: lunarData.timeGanZhi
    },
    mingZhu,
    shenZhu,
    ziDou,
    yearStemIndex: lunarYearStemIdx,
    birthMonthIndex: monthIdx,
    birthHourIndex: hourIdx,
  };
};

export const getFlowState = (chart: ChartData, flowDate: Date, birthDate: Date, flowTimeIdx: number, settings: AppSettings) => {
    const birthYear = birthDate.getFullYear();
    const flowYear = flowDate.getFullYear();
    const age = flowYear - birthYear + 1;
    
    const lunar = getLunarDateObj(flowDate, flowTimeIdx);
    const flowYearStem = getZodiacYearStemIndex(lunar.getYear());
    const flowYearBranch = getZodiacYearBranchIndex(lunar.getYear());
    const flowMonth = lunar.getMonth();
    const flowDay = lunar.getDay();
    const flowHour = flowTimeIdx;
    
    // Get Day and Hour GanZhi for Stems
    const dayGanZhi = lunar.getDayInGanZhi();
    const timeGanZhi = lunar.getTimeInGanZhi();
    // Parse the Stem characters (First char)
    const liuRiStem = STEMS.indexOf(dayGanZhi.charAt(0));
    const liuShiStem = STEMS.indexOf(timeGanZhi.charAt(0));

    const daXianPalace = chart.palaces.find(p => age >= p.ageRange[0] && age <= p.ageRange[1]);
    const daXianIndex = daXianPalace ? daXianPalace.index : 0;
    
    // Flow Month Algorithm (Dou Jun)
    // 1. Calculate Flow Year Dou Jun (Jan Position)
    // Formula: FlowYearBranch - (BirthMonth - 1) + BirthHour
    const liuNianDouJun = fix(flowYearBranch - (chart.birthMonthIndex - 1) + chart.birthHourIndex);
    
    // 2. Calculate Current Flow Month Index
    // Start from Dou Jun (Jan), move clockwise
    const liuYueIndex = fix(liuNianDouJun + (Math.abs(flowMonth) - 1));

    const liuNianIndex = fix(flowYearBranch); 
    const liuRiIndex = fix(liuYueIndex + (flowDay - 1));
    const liuShiIndex = fix(liuRiIndex + (flowHour));

    const daXianStem = daXianPalace ? STEMS.indexOf(daXianPalace.heavenlyStem) : 0;
    const liuNianStem = flowYearStem;
    const liuYueStem = getMonthStem(flowYearStem, Math.abs(flowMonth));

    const daXianLabel = daXianPalace ? `${daXianPalace.ageRange[0]}~${daXianPalace.ageRange[1]} ${daXianPalace.heavenlyStem}${daXianPalace.earthlyBranch}限` : '大限';
    const liuNianLabel = `${lunar.getYear()} ${lunar.getYearInGanZhi()} ${age}岁`;
    const liuYueLabel = `${lunar.getMonthInChinese()}月 ${lunar.getMonthInGanZhi()}`;
    const liuRiLabel = `${lunar.getDayInChinese()} ${lunar.getDayInGanZhi()}`;
    const liuShiLabel = `${lunar.getTimeInGanZhi()}时`;

    return {
        daXianIndex,
        liuNianIndex,
        liuYueIndex,
        liuRiIndex,
        liuShiIndex,
        stems: {
            daxian: daXianStem,
            liunian: liuNianStem,
            liuyue: liuYueStem,
            liuri: liuRiStem,
            liushi: liuShiStem
        },
        labels: {
            daxian: daXianLabel,
            year: liuNianLabel,
            month: liuYueLabel,
            day: liuRiLabel,
            hour: liuShiLabel
        }
    };
}
