
export enum Gender {
  MALE = '男',
  FEMALE = '女',
}

export interface AppSettings {
  leapMonth: 'current' | 'next' | 'split';
  earlyLateZi: boolean; // True for Early/Late distinction
  trueSolarTime: boolean;
  
  // Star Placement Rules (An Xing Jue)
  anXing: {
    tianMa: 'year' | 'month'; // Year Branch (Default) or Month Branch
    tianKong: 'year' | 'seq'; // Year Branch+1 (Regular) or Sequential
    jieKong: 'dual' | 'single'; // Main/Deputy (Default) or Single
    tianShiShang: 'regular' | 'zhongzhou';
    kuiYue: 'xin_hu_ma' | 'geng_ma_hu' | 'geng_hu_ma' | 'xin_ma_hu';
    mingZhu: 'quan' | 'zhongzhou';
    changSheng: 'water_earth' | 'fire_earth'; // Water/Earth shared (Default) or Fire/Earth
    brightness: 'zhongzhou' | 'quan'; // Zhong Zhou (Default for this app) or Quan Shu
  };

  // Si Hua Variations
  siHua: {
    geng: 'yang_wu_yin_tong' | 'yang_wu_tong_yin' | 'yang_wu_fu_tong' | 'yang_wu_fu_xiang' | 'yang_wu_tong_xiang';
    wu: 'tan_yin_you_ji' | 'tan_yin_yang_ji';
    ren: 'liang_zi_zuo_wu' | 'liang_zi_fu_wu' | 'liang_zi_xiang_wu';
    gui: 'po_ju_yin_tan' | 'po_ju_yang_tan';
  };

  display: {
    showLiuNian: boolean;
    showXiaoXian: boolean;
    showLiuYue: boolean;
    showArrows: boolean;
    compactMode: boolean; // Flat vs Compact
    showFlowStars: boolean; // Master toggle for flow stars in list
    showFlowMa: boolean;
    showFlowHuoLing: boolean;
    showFlowHongXi: boolean;
    showFlowChangQu: boolean;
  };
}

export const DEFAULT_SETTINGS: AppSettings = {
  leapMonth: 'current',
  earlyLateZi: true,
  trueSolarTime: false,
  anXing: {
    tianMa: 'year',
    tianKong: 'year',
    jieKong: 'dual',
    tianShiShang: 'regular',
    kuiYue: 'xin_hu_ma', // 6 Xin meets Tiger Horse (Default)
    mingZhu: 'quan',
    changSheng: 'water_earth',
    brightness: 'zhongzhou',
  },
  siHua: {
    geng: 'yang_wu_yin_tong',
    wu: 'tan_yin_you_ji', // Default: Tan Yin You Ji (Right Assistant)
    ren: 'liang_zi_zuo_wu',
    gui: 'po_ju_yin_tan',
  },
  display: {
    showLiuNian: false,
    showXiaoXian: true,
    showLiuYue: false,
    showArrows: true,
    compactMode: false,
    showFlowStars: true,
    showFlowMa: true,
    showFlowHuoLing: true,
    showFlowHongXi: true,
    showFlowChangQu: true,
  }
};

export type ProfileCategory = '家人' | '朋友' | '同学' | '同事' | '客户' | '名人' | '其他' | '分组';

export interface SavedProfile {
  id: string;
  name: string;
  gender: Gender;
  birthDate: string; // ISO Date String
  birthTimeIndex: number;
  category: ProfileCategory;
  notes: string;
  longitude?: number; // Add Longitude support
}

export interface Star {
  name: string;
  type: 'major' | 'minor' | 'bad' | 'good' | 'aux' | 'flow' | 'sui' | 'bo' | 'chang' | 'jiang'; 
  brightness?: '庙' | '旺' | '得' | '利' | '平' | '陷' | '不'; 
  modifier?: '禄' | '权' | '科' | '忌';
  layer?: 'daxian' | 'liunian' | 'liuyue' | 'liuri' | 'liushi'; // Track origin for Flow Stars
}

export interface PalaceData {
  index: number; // 0-11
  earthlyBranch: string; // 子, 丑...
  heavenlyStem: string; // 甲, 乙...
  name: string; // 命宫, 兄弟...
  isBodyPalace: boolean; // 身宫
  majorStars: Star[];
  minorStars: Star[]; // Regular minor stars
  auxStars: Star[]; // Left/Right, Wen/Chang etc
  badStars: Star[]; // Sha stars
  godsStars: Star[]; // Chang Sheng 12, Sui Jian 12, Bo Shi 12, Jiang Qian 12
  flowStars: Star[]; // Calculated Flow Stars
  ageRange: [number, number]; // [Start, End]
  smallRange: number[]; // Xiao Xian Ages (1, 13, 25...)
}

export interface ChartData {
  lunarDateStr: string;
  solarDateStr: string;
  trueSolarDateStr?: string; // Add True Solar Time string
  bureau: string;
  mingPalaceIndex: number;
  shenPalaceIndex: number;
  gender: Gender;
  yinYang: '阴' | '阳';
  palaces: PalaceData[];
  name: string;
  baZi: {
    year: string;
    month: string;
    day: string;
    time: string;
  };
  mingZhu: string;
  shenZhu: string;
  ziDou: string;
  yearStemIndex: number;
  birthMonthIndex: number;
  birthHourIndex: number;
}

export const EARTHLY_BRANCHES = [
  '子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'
];

export const HEAVENLY_STEMS = [
  '甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'
];
