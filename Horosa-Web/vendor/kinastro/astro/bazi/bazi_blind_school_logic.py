#!/usr/bin/env python3
"""
盲派八字命學模組（BlindSchoolBazi）

理論依據：
  1. 《盲派大師夏仲奇命學精粹》（陳秉志著，華夏文藝出版社2016年版）
  2. 《盲派-入门-整理》

核心原則：
  - 六親以宮位為主（年父母、月兄弟、日夫妻、時子女）
  - 「穿」（穿破）殺傷力遠大於沖，是盲派最強破壞象
  - 重視墓的詳細用法（入墓、沖墓、刑墓、墓中藏神）
  - 天干扎根特性：甲陽木高聳、乙陰木蔓延、丙丁火炎、庚辛金硬、壬癸水流
  - 以病取用：先找病（穿破、墓沖、過旺過弱），再論制用
  - 時辰斷法：兄弟姐妹數、臉型、睡姿
  - 大限以日柱為基點起限，結合虛歲
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ==================== 基礎數據 ====================

STEMS: List[str] = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
BRANCHES: List[str] = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 天干五行
STEM_ELEMENT: Dict[str, str] = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}

# 地支五行
BRANCH_ELEMENT: Dict[str, str] = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

# 天干陰陽（True=陽）
STEM_YIN_YANG: Dict[str, bool] = {s: (i % 2 == 0) for i, s in enumerate(STEMS)}

# 地支藏干（人元）
# 依據《三命通會》卷一「論地支藏干」
HIDDEN_STEMS: Dict[str, List[str]] = {
    '子': ['壬', '癸'],
    '丑': ['己', '癸', '辛'],
    '寅': ['甲', '丙', '戊'],
    '卯': ['甲', '乙'],
    '辰': ['戊', '癸', '乙'],
    '巳': ['丙', '戊', '庚'],
    '午': ['丙', '丁', '己'],
    '未': ['己', '乙', '丁'],
    '申': ['庚', '壬', '戊'],
    '酉': ['庚', '辛'],
    '戌': ['戊', '辛', '丁'],
    '亥': ['壬', '甲'],
}

# 五行相生（木生火→火生土→土生金→金生水→水生木）
ELEMENT_SHENG: Dict[str, str] = {
    '木': '火', '火': '土', '土': '金', '金': '水', '水': '木',
}

# 五行相克（木克土→土克水→水克火→火克金→金克木）
ELEMENT_KE: Dict[str, str] = {
    '木': '土', '土': '水', '水': '火', '火': '金', '金': '木',
}

# 地支六合
SIX_COMBINE: Dict[str, str] = {
    '子': '丑', '丑': '子',
    '寅': '亥', '亥': '寅',
    '卯': '戌', '戌': '卯',
    '辰': '酉', '酉': '辰',
    '巳': '申', '申': '巳',
    '午': '未', '未': '午',
}

# 地支六沖
SIX_CLASH: Dict[str, str] = {
    '子': '午', '午': '子',
    '丑': '未', '未': '丑',
    '寅': '申', '申': '寅',
    '卯': '酉', '酉': '卯',
    '辰': '戌', '戌': '辰',
    '巳': '亥', '亥': '巳',
}

# 地支相穿（盲派最重視，殺傷力最強）
# 陳秉志《盲派大師夏仲奇命學精粹》：穿破之力遠勝六沖
PIERCE: Dict[str, str] = {
    '子': '未', '未': '子',
    '丑': '午', '午': '丑',
    '寅': '巳', '巳': '寅',
    '卯': '辰', '辰': '卯',
    '申': '亥', '亥': '申',
    '酉': '戌', '戌': '酉',
}

# 六破
BREAK: Dict[str, str] = {
    '子': '酉', '酉': '子',
    '卯': '午', '午': '卯',
    '巳': '申', '申': '巳',
    '寅': '亥', '亥': '寅',
    '辰': '丑', '丑': '辰',
    '未': '戌', '戌': '未',
}

# 三刑（寅巳申無恩之刑、丑未戌持勢之刑、子卯無禮之刑）
PUNISH_GROUPS: List[List[str]] = [
    ['寅', '巳', '申'],
    ['丑', '未', '戌'],
    ['子', '卯'],
]

# 三合局（申子辰水局、寅午戌火局、巳酉丑金局、亥卯未木局）
THREE_COMBINE: List[Tuple[List[str], str]] = [
    (['申', '子', '辰'], '水'),
    (['寅', '午', '戌'], '火'),
    (['巳', '酉', '丑'], '金'),
    (['亥', '卯', '未'], '木'),
]

# 三會方（寅卯辰木局、巳午未火局、申酉戌金局、亥子丑水局）
THREE_ASSEMBLY: List[Tuple[List[str], str]] = [
    (['寅', '卯', '辰'], '木'),
    (['巳', '午', '未'], '火'),
    (['申', '酉', '戌'], '金'),
    (['亥', '子', '丑'], '水'),
]

# 五行墓庫（木墓未、火墓戌、金墓丑、水墓辰、土墓辰戌）
ELEMENT_TOMB: Dict[str, str] = {
    '木': '未',
    '火': '戌',
    '金': '丑',
    '水': '辰',
    '土': '辰',
}

# 天干扎根特性（盲派象法，以地支藏干透出為「扎根」）
# 甲扎寅亥（臨官、長生），乙扎卯寅，丙扎午巳，丁扎午巳未
# 庚扎申酉，辛扎酉申，壬扎子亥，癸扎子丑亥
STEM_ROOTING: Dict[str, List[str]] = {
    '甲': ['寅', '卯', '亥'],
    '乙': ['卯', '寅', '未'],
    '丙': ['午', '巳', '寅'],
    '丁': ['午', '巳', '未'],
    '戊': ['辰', '戌', '巳', '午'],
    '己': ['未', '丑', '辰', '午'],
    '庚': ['申', '酉', '巳'],
    '辛': ['酉', '申', '丑'],
    '壬': ['子', '亥', '申'],
    '癸': ['子', '亥', '丑'],
}

# 完整長生十二宮表
# 陽干順佈，陰干逆佈；以枝序配12狀態
_SHENG_STATES = ['長生', '沐浴', '冠帶', '臨官', '帝旺', '衰', '病', '死', '墓', '絕', '胎', '養']
_DZ_IDX = {b: i for i, b in enumerate(BRANCHES)}


def _build_changsheng_table(start_branch: str, forward: bool) -> Dict[str, str]:
    """建立某干的長生十二宮表。start_branch 為長生所在地支，forward 為順逆。"""
    start = _DZ_IDX[start_branch]
    result = {}
    for i, state in enumerate(_SHENG_STATES):
        if forward:
            idx = (start + i) % 12
        else:
            idx = (start - i) % 12
        result[BRANCHES[idx]] = state
    return result


SHENG_WANG_TABLE: Dict[str, Dict[str, str]] = {
    '甲': _build_changsheng_table('亥', True),   # 甲木長生在亥，順佈
    '乙': _build_changsheng_table('午', False),  # 乙木長生在午，逆佈
    '丙': _build_changsheng_table('寅', True),   # 丙火長生在寅，順佈
    '丁': _build_changsheng_table('酉', False),  # 丁火長生在酉，逆佈
    '戊': _build_changsheng_table('寅', True),   # 戊土同丙火
    '己': _build_changsheng_table('酉', False),  # 己土同丁火
    '庚': _build_changsheng_table('巳', True),   # 庚金長生在巳，順佈
    '辛': _build_changsheng_table('子', False),  # 辛金長生在子，逆佈
    '壬': _build_changsheng_table('申', True),   # 壬水長生在申，順佈
    '癸': _build_changsheng_table('卯', False),  # 癸水長生在卯，逆佈
}

# 完整六十甲子納音表
NA_YIN: Dict[str, str] = {
    '甲子': '海中金', '乙丑': '海中金',
    '丙寅': '爐中火', '丁卯': '爐中火',
    '戊辰': '大林木', '己巳': '大林木',
    '庚午': '路旁土', '辛未': '路旁土',
    '壬申': '劍鋒金', '癸酉': '劍鋒金',
    '甲戌': '山頭火', '乙亥': '山頭火',
    '丙子': '澗下水', '丁丑': '澗下水',
    '戊寅': '城頭土', '己卯': '城頭土',
    '庚辰': '白蠟金', '辛巳': '白蠟金',
    '壬午': '楊柳木', '癸未': '楊柳木',
    '甲申': '泉中水', '乙酉': '泉中水',
    '丙戌': '屋上土', '丁亥': '屋上土',
    '戊子': '霹靂火', '己丑': '霹靂火',
    '庚寅': '松柏木', '辛卯': '松柏木',
    '壬辰': '長流水', '癸巳': '長流水',
    '甲午': '砂中金', '乙未': '砂中金',
    '丙申': '山下火', '丁酉': '山下火',
    '戊戌': '平地木', '己亥': '平地木',
    '庚子': '壁上土', '辛丑': '壁上土',
    '壬寅': '金箔金', '癸卯': '金箔金',
    '甲辰': '覆燈火', '乙巳': '覆燈火',
    '丙午': '天河水', '丁未': '天河水',
    '戊申': '大驛土', '己酉': '大驛土',
    '庚戌': '釵釧金', '辛亥': '釵釧金',
    '壬子': '桑柘木', '癸丑': '桑柘木',
    '甲寅': '大溪水', '乙卯': '大溪水',
    '丙辰': '沙中土', '丁巳': '沙中土',
    '戊午': '天上火', '己未': '天上火',
    '庚申': '石榴木', '辛酉': '石榴木',
    '壬戌': '大海水', '癸亥': '大海水',
}

# 宮位名稱
PALACE_NAMES = ['年', '月', '日', '時']
PALACE_ROLES = {
    '年': '父母宮（兼論祖上）',
    '月': '兄弟宮（兼論命主早年）',
    '日': '夫妻宮（命主本宮）',
    '時': '子女宮（兼論晚運）',
}

# ==================== 工具函數 ====================

def get_element(item: str) -> str:
    """獲取天干或地支的五行。"""
    if item in STEM_ELEMENT:
        return STEM_ELEMENT[item]
    return BRANCH_ELEMENT.get(item, '')


def get_yin_yang(stem: str) -> bool:
    """返回天干陰陽，True=陽。"""
    return STEM_YIN_YANG.get(stem, True)


def get_hidden_stems(branch: str) -> List[str]:
    """地支藏干。"""
    return HIDDEN_STEMS.get(branch, [])


def get_branch_state(stem: str, branch: str) -> str:
    """返回某天干在某地支的長生十二宮狀態。"""
    table = SHENG_WANG_TABLE.get(stem, {})
    return table.get(branch, '未知')


def check_enter_tomb(stem: str, branch: str) -> bool:
    """天干是否入墓於該地支。"""
    elem = get_element(stem)
    return ELEMENT_TOMB.get(elem) == branch


def get_ten_god(day_stem: str, target_stem: str) -> str:
    """
    計算目標天干相對於日干的十神。

    規則（《子平真詮》）：
      同我同性=比肩、同我異性=劫財
      我生同性=食神、我生異性=傷官
      我克異性=正財、我克同性=偏財
      克我異性=正官、克我同性=七殺
      生我異性=正印、生我同性=偏印
    """
    if day_stem == target_stem:
        return '比肩'
    day_elem = get_element(day_stem)
    target_elem = get_element(target_stem)
    day_yang = get_yin_yang(day_stem)
    target_yang = get_yin_yang(target_stem)
    same_polarity = day_yang == target_yang

    if day_elem == target_elem:
        return '比肩' if same_polarity else '劫財'
    if ELEMENT_SHENG.get(day_elem) == target_elem:
        return '食神' if same_polarity else '傷官'
    if ELEMENT_KE.get(day_elem) == target_elem:
        return '偏財' if same_polarity else '正財'
    if ELEMENT_KE.get(target_elem) == day_elem:
        return '七殺' if same_polarity else '正官'
    if ELEMENT_SHENG.get(target_elem) == day_elem:
        return '偏印' if same_polarity else '正印'
    return '未知'


# ==================== 數據類 ====================

@dataclass
class Pillar:
    """一柱干支。"""
    stem: str
    branch: str

    def __post_init__(self):
        if self.stem not in STEMS or self.branch not in BRANCHES:
            raise ValueError(f"無效干支：{self.stem}{self.branch}")

    @property
    def ganzhi(self) -> str:
        return self.stem + self.branch

    @property
    def element(self) -> str:
        return get_element(self.stem)

    @property
    def hidden(self) -> List[str]:
        return get_hidden_stems(self.branch)

    @property
    def nayin(self) -> str:
        return NA_YIN.get(self.ganzhi, '')

    def get_state(self, target_stem: Optional[str] = None) -> str:
        """地支對某天干的長生宮狀態；默認對本柱天干。"""
        s = target_stem or self.stem
        return get_branch_state(s, self.branch)

    def __str__(self) -> str:
        return self.ganzhi


@dataclass
class Bazi:
    """四柱八字輸入資料模型（盲派用）。"""
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar

    day_master: str = field(init=False)

    def __post_init__(self):
        self.day_master = self.day.stem

    def pillars(self) -> List[Pillar]:
        """返回四柱列表 [年, 月, 日, 時]。"""
        return [self.year, self.month, self.day, self.hour]

    # 別名，保持向後相容
    def all_pillars(self) -> List[Pillar]:
        return self.pillars()

    def get_branches(self) -> List[str]:
        return [p.branch for p in self.pillars()]

    def get_stems(self) -> List[str]:
        return [p.stem for p in self.pillars()]

    def to_dict(self) -> Dict:
        """序列化為字典。"""
        pillars = self.pillars()
        names = PALACE_NAMES
        return {
            names[i]: {
                'ganzhi': str(pillars[i]),
                'stem': pillars[i].stem,
                'branch': pillars[i].branch,
                'nayin': pillars[i].nayin,
            }
            for i in range(4)
        }

    # ---------- 地支作用關係 ----------

    def analyze_interactions(self) -> Dict[Tuple[str, ...], List[str]]:
        """分析全盤地支兩兩作用關係（穿破合沖刑）。"""
        branches = self.get_branches()
        result: Dict[Tuple[str, ...], List[str]] = {}
        for i in range(4):
            for j in range(i + 1, 4):
                acts = _branch_interactions(branches[i], branches[j])
                if acts:
                    result[(branches[i], branches[j])] = acts
        # 三合局
        for members, elem in THREE_COMBINE:
            if all(b in branches for b in members):
                result[tuple(members)] = [f"三合{elem}局"]
        # 三會方
        for members, elem in THREE_ASSEMBLY:
            if all(b in branches for b in members):
                result[tuple(members)] = [f"三會{elem}局"]
        return result

    def find_pierce_break(self) -> List[str]:
        """找出所有穿破（盲派重點）。"""
        branches = self.get_branches()
        findings = []
        positions = {b: [] for b in BRANCHES}
        for idx, b in enumerate(branches):
            positions[b].append(PALACE_NAMES[idx])
        for i in range(4):
            for j in range(i + 1, 4):
                b1, b2 = branches[i], branches[j]
                if PIERCE.get(b1) == b2:
                    p1 = PALACE_NAMES[i]
                    p2 = PALACE_NAMES[j]
                    findings.append(f"{p1}支{b1}穿{p2}支{b2}（殺傷力最強，宮位受損）")
                if BREAK.get(b1) == b2:
                    p1 = PALACE_NAMES[i]
                    p2 = PALACE_NAMES[j]
                    findings.append(f"{p1}支{b1}破{p2}支{b2}")
        return findings

    def check_tombs(self) -> List[str]:
        """檢查天干入墓與地支墓庫。"""
        findings = []
        for idx, p in enumerate(self.pillars()):
            palace = PALACE_NAMES[idx]
            if check_enter_tomb(p.stem, p.branch):
                findings.append(f"{palace}柱 {p} 天干{p.stem}入墓於{p.branch}（{get_element(p.stem)}墓）")
            if p.branch in ('辰', '戌', '丑', '未'):
                findings.append(f"{palace}支{p.branch}為墓庫宮（{BRANCH_ELEMENT[p.branch]}土）")
        return findings

    # ---------- 盲派特定斷法（內嵌於 Bazi） ----------

    def analyze_hour_for_siblings_face_sleep(self) -> Dict[str, str]:
        """
        時辰斷兄弟姐妹數、臉型、睡姿。
        來源：《盲派-入门-整理》「時辰斷法」章節。
        四正（子午卯酉）、四生（寅申巳亥）、四庫（辰戌丑未）三組各有不同判斷。
        """
        h = self.hour.branch
        result: Dict[str, str] = {}

        # 兄弟姐妹數
        if h in ('子', '午', '卯', '酉'):
            result['兄弟姐妹數'] = '1人（月令旺或月支見比劫可增至2人）'
        elif h in ('寅', '申', '巳', '亥'):
            result['兄弟姐妹數'] = '3人（月令旺可達5人）'
        else:  # 辰戌丑未
            result['兄弟姐妹數'] = '獨生子女或相差3歲以上（四庫為孤）'

        # 臉型（夏仲奇斷法）
        if h in ('子', '午', '卯', '酉'):
            result['臉型'] = '四方臉，顴骨略尖'
        elif h in ('寅', '申', '巳', '亥'):
            result['臉型'] = '長臉（臉型修長）'
        else:
            result['臉型'] = '圓臉（圓潤豐滿）'

        # 睡姿
        if h in ('子', '午', '卯', '酉'):
            result['睡姿'] = '仰面睡（直身仰臥）'
        elif h in ('寅', '申', '巳', '亥'):
            result['睡姿'] = '側身睡（左右側臥）'
        else:
            result['睡姿'] = '俯面睡（趴臥）'

        return result

    def check_parents_ke(self) -> List[str]:
        """
        少年克父母斷法。
        正印為母（生我異性），偏財為父（我克同性）。
        父母宮（年月柱）坐死病墓絕 → 早年克父母；
        父母星坐長生旺地，流年見合沖 → 父母有事。
        《盲派大師夏仲奇命學精粹》：「宮位坐死病墓絕，六親受損；穿破尤甚。」
        """
        findings = []
        dm = self.day_master

        # 年月宮位狀態檢查（以日主長生宮判斷）
        for idx, label in [(0, '年'), (1, '月')]:
            pillar = self.pillars()[idx]
            branch = pillar.branch
            state = get_branch_state(dm, branch)

            if state in ('死', '病', '墓', '絕'):
                findings.append(
                    f"{label}支{branch}對日主{dm}臨{state}，父母宮坐衰地，"
                    f"早年父母緣薄或有克損"
                )

            # 穿破
            other_branches = [self.pillars()[k].branch for k in range(4) if k != idx]
            for ob in other_branches:
                if PIERCE.get(branch) == ob:
                    findings.append(
                        f"{label}支{branch}被穿（{branch}穿{ob}），"
                        f"父母宮受穿最烈，早年父母有損"
                    )
                if SIX_CLASH.get(branch) == ob:
                    findings.append(
                        f"{label}支{branch}逢沖（{branch}沖{ob}），"
                        f"父母宮動盪，少年見事"
                    )

            # 入墓
            if check_enter_tomb(pillar.stem, branch):
                findings.append(
                    f"{label}柱{pillar}天干入墓，{label}宮主星受困，父母緣薄"
                )

        return findings or ['父母宮穩定，未見明顯克損，需結合大限流年細斷']

    def check_first_child_gender(self) -> str:
        """
        頭二胎男孩女孩斷法（盲派月上子孫星法）。
        男命（陽日干）：時支藏干以傷官（陰）主女、食神（陽）主男；官殺亦可參斷。
        女命（陰日干）：月支藏干以傷官主男、食神主女；沖穿則換相。
        「沖穿換相」：月支受沖穿，子孫星換為對宮，男女性別亦換。
        """
        dm = self.day_master
        dm_yang = get_yin_yang(dm)
        month_branch = self.month.branch
        hour_branch = self.hour.branch

        # 以時支子孫星為主（「月上子孫星」原則）
        # 這裡以月支藏干配日主計算
        month_hidden = get_hidden_stems(month_branch)
        child_gods = [get_ten_god(dm, h) for h in month_hidden]

        # 是否有穿沖（換相）
        has_pierce = PIERCE.get(month_branch) in self.get_branches()
        has_clash = SIX_CLASH.get(month_branch) in self.get_branches()
        switched = has_pierce or has_clash
        switch_note = '（月支受穿/沖，換相判斷）' if switched else ''

        if dm_yang:  # 陽日干（男命多）
            if '食神' in child_gods:
                gender = '女孩' if switched else '男孩'
            elif '傷官' in child_gods:
                gender = '男孩' if switched else '女孩'
            elif '偏財' in child_gods or '正財' in child_gods:
                gender = '男孩（財星入時，多子）'
            else:
                gender = '需結合流年細斷'
        else:  # 陰日干（女命多）
            if '傷官' in child_gods:
                gender = '男孩' if not switched else '女孩'
            elif '食神' in child_gods:
                gender = '女孩' if not switched else '男孩'
            else:
                gender = '需結合流年細斷'

        return f"頭胎{switch_note}：{gender}"

    def get_six_qin_from_palace(self) -> Dict[str, str]:
        """
        六親以宮位為主（盲派核心原則）。
        年宮父母，月宮兄弟，日宮夫妻/自己，時宮子女。
        """
        pillars = self.pillars()
        states = [get_branch_state(self.day_master, p.branch) for p in pillars]
        result = {}
        for i, (name, role) in enumerate(PALACE_ROLES.items()):
            p = pillars[i]
            state = states[i]
            pierce_target = PIERCE.get(p.branch)
            pierce_note = ''
            if pierce_target and pierce_target in self.get_branches():
                pierce_note = f'，被穿（→{pierce_target}，宮位受損）'
            result[f'{name}宮（{role}）'] = (
                f"{p}，支{p.branch}對日主{self.day_master}臨{state}{pierce_note}"
            )
        return result


# ==================== 地支作用引擎（獨立函數）====================

def _branch_interactions(b1: str, b2: str) -> List[str]:
    """
    計算兩地支間所有作用關係，依盲派優先順序排列：穿 > 沖 > 合 > 破 > 刑。
    """
    acts = []
    if PIERCE.get(b1) == b2:
        acts.append('穿（最強破壞）')
    if SIX_CLASH.get(b1) == b2:
        acts.append('六沖')
    if SIX_COMBINE.get(b1) == b2:
        acts.append('六合')
    if BREAK.get(b1) == b2:
        acts.append('六破')
    for group in PUNISH_GROUPS:
        if b1 in group and b2 in group and b1 != b2:
            acts.append('三刑')
            break
    return acts


def find_pierce_and_break(bazi: Bazi) -> List[Dict]:
    """
    獨立函數：檢測穿破（盲派重點）。
    返回列表，每項含 type / branches / positions / note。
    """
    branches = bazi.get_branches()
    results = []
    for i in range(4):
        for j in range(i + 1, 4):
            b1, b2 = branches[i], branches[j]
            if PIERCE.get(b1) == b2:
                results.append({
                    'type': '穿',
                    'branches': f'{b1}穿{b2}',
                    'positions': f'{PALACE_NAMES[i]}支穿{PALACE_NAMES[j]}支',
                    'note': '盲派最強破壞象，宮位六親必損',
                })
            if BREAK.get(b1) == b2:
                results.append({
                    'type': '破',
                    'branches': f'{b1}破{b2}',
                    'positions': f'{PALACE_NAMES[i]}支破{PALACE_NAMES[j]}支',
                    'note': '破傷六親宮位',
                })
    return results


# ==================== 十神系統 ====================

def calculate_ten_gods(bazi: Bazi) -> Dict[str, Dict]:
    """
    完整十神計算：逐柱計算天干十神，地支本氣及藏干十神。
    """
    day_stem = bazi.day_master
    gods: Dict[str, Dict] = {}
    for i, (name, pillar) in enumerate(zip(PALACE_NAMES, bazi.pillars())):
        stem_god = get_ten_god(day_stem, pillar.stem) if i != 2 else '日主'
        branch_hidden_gods = [
            {'stem': h, 'god': get_ten_god(day_stem, h)}
            for h in get_hidden_stems(pillar.branch)
        ]
        gods[name] = {
            '天干': pillar.stem,
            '天干十神': stem_god,
            '地支': pillar.branch,
            '地支五行': BRANCH_ELEMENT[pillar.branch],
            '藏干十神': branch_hidden_gods,
            '長生宮': get_branch_state(day_stem, pillar.branch),
            '宮位': PALACE_ROLES[name],
        }
    return gods


# ==================== 以病取用 ====================

def detect_illness(bazi: Bazi) -> Dict:
    """
    以病取用核心引擎——檢測命局病處。
    盲派「以病取用」：先找病，後立用，病重則用重。

    病的主要類型（按輕重）：
      1. 穿破（最重）
      2. 沖墓入墓
      3. 五行偏枯（過旺過弱）
      4. 刑
    """
    branches = bazi.get_branches()
    stems = bazi.get_stems()

    # 1. 穿破（最重）
    pierce_break = find_pierce_and_break(bazi)

    # 2. 入墓
    tomb_issues = []
    for idx, p in enumerate(bazi.pillars()):
        if check_enter_tomb(p.stem, p.branch):
            tomb_issues.append({
                'pillar': str(p),
                'palace': PALACE_NAMES[idx],
                'desc': f'{p.stem}({get_element(p.stem)})入墓於{p.branch}，主事受困',
            })
        # 被沖墓（墓庫被另一支沖開）
        if p.branch in ('辰', '戌', '丑', '未'):
            clash_branch = SIX_CLASH.get(p.branch)
            if clash_branch and clash_branch in branches:
                tomb_issues.append({
                    'pillar': str(p),
                    'palace': PALACE_NAMES[idx],
                    'desc': f'{p.branch}（墓庫）被{clash_branch}沖開，藏干受衝擾',
                })

    # 3. 五行偏枯
    elem_count: Dict[str, int] = {e: 0 for e in ('木', '火', '土', '金', '水')}
    for s in stems:
        elem_count[get_element(s)] += 1
    for b in branches:
        elem_count[get_element(b)] += 1
    bias = []
    for e, cnt in elem_count.items():
        if cnt >= 4:
            bias.append({'element': e, 'count': cnt, 'type': '過旺', 'desc': f'{e}過旺（{cnt}個），為命局之病'})
        elif cnt == 0:
            bias.append({'element': e, 'count': 0, 'type': '缺失', 'desc': f'命局無{e}，為空缺之病'})

    # 4. 三刑
    punish_found = []
    for group in PUNISH_GROUPS:
        matched = [b for b in group if b in branches]
        if len(matched) >= 2:
            punish_found.append({'members': matched, 'desc': f"{''.join(matched)}三刑"})

    has_disease = bool(pierce_break or tomb_issues or bias or punish_found)
    severity = '無病' if not has_disease else (
        '重病' if pierce_break else '中等' if tomb_issues else '輕病'
    )

    return {
        '穿破': pierce_break,
        '入墓': tomb_issues,
        '五行偏枯': bias,
        '三刑': punish_found,
        '病情輕重': severity,
        '總述': (
            f"命局病處：穿破{len(pierce_break)}處，入墓{len(tomb_issues)}處，"
            f"五行偏枯{len(bias)}項，三刑{len(punish_found)}組。"
            f"病情：{severity}。"
        ),
    }


def recommend_use_god(bazi: Bazi, illness: Optional[Dict] = None) -> Dict:
    """
    以病取用推薦用神。
    盲派：病在哪宮，用神制那宮；穿破用合或印化；過旺用洩；過弱用扶。
    「用神者，制病之藥也」——陳秉志解析夏仲奇原文。
    """
    if illness is None:
        illness = detect_illness(bazi)

    day_stem = bazi.day_master
    day_elem = get_element(day_stem)
    day_yang = get_yin_yang(day_stem)

    use_gods = []

    # 針對穿破
    for pb in illness.get('穿破', []):
        if pb['type'] == '穿':
            use_gods.append({
                'god': '六合或正印（制穿）',
                'reason': f"{pb['branches']}穿破最烈，宜用六合封住穿源，或正印生扶受損宮位",
            })

    # 針對五行偏枯
    for b in illness.get('五行偏枯', []):
        if b['type'] == '過旺':
            drain_elem = ELEMENT_SHENG.get(b['element'], '')
            use_gods.append({
                'god': f"洩{b['element']}之{drain_elem}（食傷）",
                'reason': f"{b['element']}旺，以{drain_elem}洩秀為用",
            })
        elif b['type'] == '缺失':
            use_gods.append({
                'god': f"補{b['element']}（印比）",
                'reason': f"命局缺{b['element']}，以補入流年大限為用",
            })

    # 日主旺衰基本用神
    day_rooting = [b for b in bazi.get_branches() if b in STEM_ROOTING.get(day_stem, [])]
    if len(day_rooting) >= 2:
        base_god = f"日主{day_stem}根深，宜官殺制衡或財星流通"
    elif len(day_rooting) == 0:
        base_god = f"日主{day_stem}無根，宜印比扶身"
    else:
        base_god = f"日主{day_stem}中和，依病取用"

    return {
        '日主': day_stem,
        '日主五行': day_elem,
        '日主陰陽': '陽' if day_yang else '陰',
        '日主扎根地支': day_rooting,
        '基本用神方向': base_god,
        '病對應用神': use_gods,
        '總結': (
            use_gods[0]['god'] if use_gods
            else base_god
        ),
    }


# ==================== 六親宮位分析 ====================

def analyze_six_qin(bazi: Bazi) -> Dict:
    """
    六親宮位完整分析（盲派核心）。
    逐宮分析穿破合沖、長生狀態、入墓等。
    「宮位坐支死病墓絕、穿破沖合克，是最重要判斷依據。」——陳秉志
    """
    dm = bazi.day_master
    branches = bazi.get_branches()
    result: Dict = {}

    for idx, (name, role) in enumerate(PALACE_ROLES.items()):
        p = bazi.pillars()[idx]
        state = get_branch_state(dm, p.branch)
        notes = []

        # 穿
        pierce_target = PIERCE.get(p.branch)
        if pierce_target and pierce_target in branches:
            notes.append(f"❗穿（{p.branch}穿{pierce_target}），宮位主星受損最烈")

        # 沖
        clash_target = SIX_CLASH.get(p.branch)
        if clash_target and clash_target in branches:
            notes.append(f"⚡沖（{p.branch}沖{clash_target}），六親動盪")

        # 合
        combine_target = SIX_COMBINE.get(p.branch)
        if combine_target and combine_target in branches:
            notes.append(f"🤝合（{p.branch}合{combine_target}），有利有弊看化神")

        # 破
        break_target = BREAK.get(p.branch)
        if break_target and break_target in branches:
            notes.append(f"破（{p.branch}破{break_target}），宮位受損")

        # 長生狀態
        if state in ('死', '病', '墓', '絕'):
            notes.append(f"⚠️宮支{p.branch}對日主臨{state}，六親緣薄")
        elif state in ('長生', '帝旺', '臨官'):
            notes.append(f"✅宮支{p.branch}對日主臨{state}，六親有力")

        # 天干入墓
        if check_enter_tomb(p.stem, p.branch):
            notes.append(f"天干{p.stem}入墓於{p.branch}，主星受困")

        result[f'{name}宮'] = {
            '宮位職司': role,
            '干支': str(p),
            '納音': p.nayin,
            '宮支長生狀態': state,
            '藏干': get_hidden_stems(p.branch),
            '注意事項': notes or ['此宮無明顯凶象'],
        }

    return result


# ==================== 婚姻專斷 ====================

def analyze_marriage(bazi: Bazi) -> Dict:
    """
    婚姻專斷。
    日支為夫妻宮，是婚姻最直接的象。
    穿破日支 → 婚姻破裂或不順；
    日支入墓 → 配偶體弱或婚姻困；
    財官入墓 → 晚婚或終生未婚風險；
    日支被合 → 有情但易因第三者。
    「日支見穿，婚姻必損；見墓，配偶多病；逢合，情感複雜。」——夏仲奇
    """
    dm = bazi.day_master
    day_branch = bazi.day.branch
    branches = bazi.get_branches()
    dm_yang = get_yin_yang(dm)
    dm_elem = get_element(dm)

    issues = []
    good_signs = []

    # 日支穿
    pierce_target = PIERCE.get(day_branch)
    if pierce_target and pierce_target in branches:
        issues.append(f"日支{day_branch}被穿（→{pierce_target}），婚姻破損風險極高")

    # 日支沖
    clash_target = SIX_CLASH.get(day_branch)
    if clash_target and clash_target in branches:
        issues.append(f"日支{day_branch}被沖（→{clash_target}），婚姻動盪，易離合")

    # 日支入墓
    if check_enter_tomb(bazi.day.stem, day_branch):
        issues.append(f"日干{dm}入墓於日支{day_branch}，命主與配偶緣分困局")

    # 配偶星（男命以財為妻，女命以官殺為夫）
    if dm_yang:  # 男命
        spouse_stars = ['正財', '偏財']
        spouse_desc = '財星為妻'
    else:  # 女命
        spouse_stars = ['正官', '七殺']
        spouse_desc = '官殺為夫'

    # 配偶星入墓
    for idx, p in enumerate(bazi.pillars()):
        hidden_gods = [get_ten_god(dm, h) for h in get_hidden_stems(p.branch)]
        stem_god = get_ten_god(dm, p.stem)
        if any(g in spouse_stars for g in hidden_gods + [stem_god]):
            state = get_branch_state(dm, p.branch)
            if state in ('墓', '死', '絕'):
                issues.append(
                    f"{PALACE_NAMES[idx]}柱{p}含{spouse_desc}，"
                    f"坐支臨{state}，晚婚或婚姻困難"
                )

    # 日支合
    combine_target = SIX_COMBINE.get(day_branch)
    if combine_target and combine_target in branches:
        good_signs.append(f"日支{day_branch}見六合（→{combine_target}），情感有緣")

    # 日支長生旺狀態
    day_state = get_branch_state(dm, day_branch)
    if day_state in ('長生', '帝旺', '臨官'):
        good_signs.append(f"日支{day_branch}對日主臨{day_state}，婚姻有力")

    # 再婚跡象（日支同時見沖穿，且年月有財官）
    remarriage = len([i for i in issues if '沖' in i or '穿' in i]) >= 2
    marriage_timing = '早婚（日支旺）' if day_state in ('長生', '帝旺') else (
        '晚婚（日支衰死）' if day_state in ('衰', '死', '墓', '絕') else '適齡婚'
    )

    return {
        '夫妻宮（日支）': day_branch,
        '日支長生狀態': day_state,
        '配偶星類型': spouse_desc,
        '婚姻凶象': issues or ['無明顯婚姻凶象'],
        '婚姻吉象': good_signs or ['無特別吉象'],
        '婚姻時機': marriage_timing,
        '再婚跡象': '有再婚跡象' if remarriage else '無明顯再婚象',
        '總評': (
            f"日支{day_branch}為夫妻宮，{marriage_timing}，"
            + ('婚姻凶象顯著，需謹慎。' if issues else '婚姻基本穩定。')
        ),
    }


# ==================== 財運分析 ====================

def analyze_wealth(bazi: Bazi) -> Dict:
    """
    財運初步分析。
    男命偏財為父亦為橫財，正財為穩定收入；
    女命財星主財帛，亦關夫運。
    財星入墓、被穿破 → 財運不順或破財。
    """
    dm = bazi.day_master
    dm_elem = get_element(dm)

    # 財星五行（我克者）
    wealth_elem = ELEMENT_KE.get(dm_elem, '')
    results = []

    for idx, p in enumerate(bazi.pillars()):
        hidden_gods = [(h, get_ten_god(dm, h)) for h in get_hidden_stems(p.branch)]
        stem_god = get_ten_god(dm, p.stem)
        wealth_gods = [(p.stem, stem_god)] + hidden_gods

        for stem_val, god in wealth_gods:
            if god in ('正財', '偏財'):
                state = get_branch_state(dm, p.branch)
                pierce_target = PIERCE.get(p.branch)
                pierce_note = (
                    f'，但地支{p.branch}被穿（→{pierce_target}），財受損'
                    if pierce_target and pierce_target in bazi.get_branches()
                    else ''
                )
                tomb_note = (
                    f'，天干入墓，財被困'
                    if check_enter_tomb(p.stem, p.branch)
                    else ''
                )
                results.append({
                    '柱': PALACE_NAMES[idx],
                    '干支': str(p),
                    '財神': f'{stem_val}（{god}）',
                    '坐支狀態': state,
                    '評述': f"{god}在{PALACE_NAMES[idx]}柱，坐支{state}{pierce_note}{tomb_note}",
                })

    return {
        '日主': dm,
        '財星五行': wealth_elem,
        '財星分佈': results or [{'評述': f'四柱中未見明顯財星，財運需靠大限流年引動'}],
        '總評': (
            f"日主{dm}（{dm_elem}），財星為{wealth_elem}，"
            + (f"共{len(results)}處財星" if results else "四柱財星稀少，財運偏薄")
        ),
    }


# ==================== 大限（限運）計算 ====================

def calculate_limits(bazi: Bazi) -> List[Dict]:
    """
    盲派大限計算——以日柱為基點起限。
    陳秉志解析夏仲奇：「盲派不用傳統大運，以日柱干支為起點，
    每宮主10年，按十神循環推演，結合虛歲定交限。」

    基本規則：
      - 第一限（自限）：日干本身主事，管0-10歲；
      - 後續依十神次序：食傷→財→官殺→印→比劫→食傷…（陽干順，陰干逆）；
      - 每限干支引動對應宮位，結合流年判吉凶。
    """
    dm = bazi.day_master
    dm_yang = get_yin_yang(dm)
    dm_elem = get_element(dm)

    # 十神循環順序（陽干）：比肩→食神→偏財→七殺→偏印→比肩…（簡化10神輪轉）
    ten_gods_cycle_yang = ['比肩', '劫財', '食神', '傷官', '偏財', '正財', '七殺', '正官', '偏印', '正印']
    ten_gods_cycle = ten_gods_cycle_yang if dm_yang else list(reversed(ten_gods_cycle_yang))

    limits = []
    # 日干在STEMS中的索引，用以確定起限干支
    dm_idx = STEMS.index(dm)

    for i in range(8):  # 計算8段大限（約80年）
        # 每段限干：從日干起，陽干順推，陰干逆推
        if dm_yang:
            limit_stem = STEMS[(dm_idx + i) % 10]
            limit_branch = BRANCHES[(BRANCHES.index(bazi.day.branch) + i) % 12]
        else:
            limit_stem = STEMS[(dm_idx - i) % 10]
            limit_branch = BRANCHES[(BRANCHES.index(bazi.day.branch) - i) % 12]

        age_start = i * 10
        age_end = age_start + 9
        god = get_ten_god(dm, limit_stem)
        elem = get_element(limit_stem)

        # 限干引動宮位
        activated_palaces = []
        for idx, p in enumerate(bazi.pillars()):
            if get_element(p.stem) == elem or get_element(p.branch) == elem:
                activated_palaces.append(
                    f"{PALACE_NAMES[idx]}宮（{PALACE_ROLES[PALACE_NAMES[idx]]}）"
                )

        # 大限吉凶初判
        limit_state = get_branch_state(dm, limit_branch)
        if limit_state in ('帝旺', '臨官', '長生'):
            luck = '旺運（事業婚姻多成）'
        elif limit_state in ('衰', '病', '死'):
            luck = '衰運（注意健康與六親）'
        elif limit_state in ('墓', '絕'):
            luck = '困運（謹防重大變故）'
        else:
            luck = '平穩（進退皆宜審慎）'

        limits.append({
            '限段': f"第{i + 1}限",
            '虛歲': f"{age_start}—{age_end}歲",
            '限干支': f"{limit_stem}{limit_branch}",
            '十神': god,
            '五行': elem,
            '限支長生狀態': limit_state,
            '引動宮位': activated_palaces or ['無直接引動'],
            '運勢初判': luck,
            '注意': (
                f"限干{limit_stem}為{god}，{luck}；"
                f"此限主{('財帛豐' if god in ('正財','偏財') else '官貴顯' if god in ('正官','七殺') else '身心修養')}"
            ),
        })

    return limits


# ==================== 流年應期框架 ====================

def analyze_liunian_framework(bazi: Bazi) -> Dict:
    """
    流年應期框架（大限 + 流年引動 + 犯太歲）。
    「流年如月，大限如季，命局如年；三者疊加方能論應期。」——陳秉志
    重點：
      - 流年天干引動命局同類五行宮位；
      - 流年地支與命局地支見穿沖合破，應期最準；
      - 犯太歲（流年與日支同支）主命主本身有大事。
    """
    dm = bazi.day_master
    day_branch = bazi.day.branch

    # 描述框架（無出生年份時只給規則）
    framework = {
        '應期規則': [
            '流年天干與命局天干同五行 → 引動對應宮位六親',
            '流年地支穿命局地支 → 當年有重大破損事件（最烈）',
            '流年地支沖命局日支 → 婚姻、健康有動盪',
            '流年地支合命局地支 → 有情有緣之年，宮位主事',
            f'犯太歲（流年支={day_branch}） → 命主本人有大變動，需格外謹慎',
        ],
        '重點年份特徵': {
            '穿太歲': f"流年地支穿日支{day_branch}（即{PIERCE.get(day_branch)}年），婚姻最危",
            '沖太歲': f"流年地支沖日支{day_branch}（即{SIX_CLASH.get(day_branch)}年），動盪之年",
            '合太歲': f"流年地支合日支{day_branch}（即{SIX_COMBINE.get(day_branch)}年），有緣有助之年",
        },
        '使用說明': '請結合實際出生年份查對大限表，找出當年大限干支，再配流年干支疊加判斷。',
    }
    return framework


# ==================== BlindSchoolBazi 主類 ====================

class BlindSchoolBazi:
    """
    盲派八字命學完整分析類（BlindSchoolBazi）。

    繼承盲派夏仲奇體系，嚴格依據《盲派大師夏仲奇命學精粹》
    及《盲派-入门-整理》兩書。

    使用方式：
        bazi = Bazi(
            year=Pillar('壬', '辰'),
            month=Pillar('壬', '子'),
            day=Pillar('甲', '辰'),
            hour=Pillar('丁', '卯'),
        )
        bs = BlindSchoolBazi(bazi)
        report = bs.full_report()

    亦可從 kinastro BaziChart 創建：
        bs = BlindSchoolBazi.from_bazi_chart(chart)
    """

    def __init__(self, bazi: Bazi):
        self.bazi = bazi
        self._illness: Optional[Dict] = None

    # ---------- 工廠方法 ----------

    @classmethod
    def from_pillars(
        cls,
        year_gz: str,
        month_gz: str,
        day_gz: str,
        hour_gz: str,
    ) -> 'BlindSchoolBazi':
        """
        直接用干支字串創建。
        year_gz / month_gz / day_gz / hour_gz 均為兩字干支，如 '壬辰'。
        """
        def _p(gz: str) -> Pillar:
            if len(gz) != 2 or gz[0] not in STEMS or gz[1] not in BRANCHES:
                raise ValueError(
                    f"無效干支：{gz!r}。"
                    f"干支必須為兩字，第一字為天干（{''.join(STEMS)}），"
                    f"第二字為地支（{''.join(BRANCHES)}）。"
                )
            return Pillar(gz[0], gz[1])

        return cls(Bazi(_p(year_gz), _p(month_gz), _p(day_gz), _p(hour_gz)))

    @classmethod
    def from_bazi_chart(cls, chart: object) -> 'BlindSchoolBazi':
        """
        從 kinastro 原有 BaziChart 物件創建，保持完整整合。
        chart 須含 year_pillar / month_pillar / day_pillar / hour_pillar 屬性，
        各屬性須含 stem / branch 字段（str，天干/地支各一字）。
        """
        def _adapt(p: object, name: str) -> Pillar:
            stem = getattr(p, 'stem', None)
            branch = getattr(p, 'branch', None)
            if not isinstance(stem, str) or not isinstance(branch, str):
                raise ValueError(
                    f"{name}柱必須具備 stem（天干）和 branch（地支）屬性，"
                    f"實際得到 stem={stem!r}, branch={branch!r}"
                )
            return Pillar(stem, branch)

        bazi = Bazi(
            year=_adapt(getattr(chart, 'year_pillar', None), '年'),
            month=_adapt(getattr(chart, 'month_pillar', None), '月'),
            day=_adapt(getattr(chart, 'day_pillar', None), '日'),
            hour=_adapt(getattr(chart, 'hour_pillar', None), '時'),
        )
        return cls(bazi)

    # ---------- 分析方法（代理到模組函數）----------

    def illness(self) -> Dict:
        """以病取用：檢測命局病處（結果緩存）。"""
        if self._illness is None:
            self._illness = detect_illness(self.bazi)
        return self._illness

    def branch_interactions(self) -> Dict:
        """地支作用關係（穿破合沖刑等）。"""
        return self.bazi.analyze_interactions()

    def hour_analysis(self) -> Dict[str, str]:
        """時辰斷法（兄弟數、臉型、睡姿）。"""
        return self.bazi.analyze_hour_for_siblings_face_sleep()

    def parents_analysis(self) -> List[str]:
        """少年克父母斷法。"""
        return self.bazi.check_parents_ke()

    def first_child_gender(self) -> str:
        """頭胎男孩女孩斷法。"""
        return self.bazi.check_first_child_gender()

    def ten_gods(self) -> Dict:
        """完整十神系統。"""
        return calculate_ten_gods(self.bazi)

    def use_god(self) -> Dict:
        """以病取用推薦用神。"""
        return recommend_use_god(self.bazi, self.illness())

    def limits(self) -> List[Dict]:
        """大限（限運）計算。"""
        return calculate_limits(self.bazi)

    def six_qin_palaces(self) -> Dict:
        """六親宮位完整分析。"""
        return analyze_six_qin(self.bazi)

    def marriage(self) -> Dict:
        """婚姻專斷。"""
        return analyze_marriage(self.bazi)

    def wealth(self) -> Dict:
        """財運初步分析。"""
        return analyze_wealth(self.bazi)

    def liunian_framework(self) -> Dict:
        """流年應期框架。"""
        return analyze_liunian_framework(self.bazi)

    def full_report(self) -> Dict:
        """全盤盲派分析報告（結構化 JSON 相容字典）。"""
        return analyze_bazi_full(self.bazi)

    def print_report(self) -> None:
        """列印可讀文字報告。"""
        print_bazi_analysis(self.bazi)


# ==================== 統一入口函數 ====================

def analyze_bazi_full(bazi: Bazi) -> Dict:
    """
    完整盲派八字分析——統一入口函數。

    返回結構化字典，包含：
      bazi_info / ten_gods / branch_interactions / hour_analysis /
      six_qin_palaces / parents_analysis / first_child / illness /
      use_god / marriage / wealth / limits / liunian_framework / summary

    報告風格依夏仲奇、陳秉志斷語：簡潔有力，象意豐富。
    """
    ill = detect_illness(bazi)
    ug = recommend_use_god(bazi, ill)
    lims = calculate_limits(bazi)

    # 命局總述
    dm = bazi.day_master
    dm_elem = get_element(dm)
    dm_yang = get_yin_yang(dm)
    pierce_count = len(ill['穿破'])
    tomb_count = len(ill['入墓'])

    if pierce_count >= 2:
        overall = f"日主{dm}，命局穿破重（{pierce_count}處），六親多損，需重點制化"
    elif pierce_count == 1:
        overall = f"日主{dm}，命局有穿（1處），宮位受損，論事需察穿所在宮位"
    elif tomb_count >= 2:
        overall = f"日主{dm}，命局多入墓，主事受困，宜靜不宜動"
    else:
        overall = f"日主{dm}（{dm_elem}，{'陽' if dm_yang else '陰'}），命局基本穩定，按限運細斷"

    return {
        'bazi_info': bazi.to_dict(),
        'ten_gods': calculate_ten_gods(bazi),
        'branch_interactions': {
            str(k): v for k, v in bazi.analyze_interactions().items()
        },
        'pierce_break_detail': find_pierce_and_break(bazi),
        'tomb_check': bazi.check_tombs(),
        'hour_analysis': bazi.analyze_hour_for_siblings_face_sleep(),
        'six_qin_palaces': analyze_six_qin(bazi),
        'parents_analysis': bazi.check_parents_ke(),
        'first_child': bazi.check_first_child_gender(),
        'illness': ill,
        'use_god': ug,
        'marriage': analyze_marriage(bazi),
        'wealth': analyze_wealth(bazi),
        'limits': lims,
        'liunian_framework': analyze_liunian_framework(bazi),
        'summary': overall,
    }


# ==================== 可讀文字報告 ====================

def print_bazi_analysis(bazi: Bazi) -> None:
    """
    列印盲派風格文字報告（仿夏仲奇/陳秉志斷語風格）。
    """
    dm = bazi.day_master
    sep = '=' * 60
    div = '-' * 60

    print(sep)
    print(f"  盲派八字命盤  ·  {bazi.year} {bazi.month} {bazi.day} {bazi.hour}")
    print(f"  日主：{dm}（{get_element(dm)}，{'陽' if get_yin_yang(dm) else '陰'}）")
    print(div)

    print("\n【宮位速覽】")
    for i, (name, p) in enumerate(zip(PALACE_NAMES, bazi.pillars())):
        state = get_branch_state(dm, p.branch)
        print(f"  {name}宮 {p}（{PALACE_ROLES[name]}）坐支{state}  納音：{p.nayin}")

    print("\n【地支作用（穿 > 沖 > 合 > 破 > 刑）】")
    inters = bazi.analyze_interactions()
    if inters:
        for k, v in inters.items():
            print(f"  {''.join(k) if isinstance(k, tuple) else k}：{'、'.join(v)}")
    else:
        print("  無明顯作用關係")

    print("\n【穿破專項】（盲派重點）")
    pb_list = bazi.find_pierce_break()
    if pb_list:
        for item in pb_list:
            print(f"  ❗{item}")
    else:
        print("  無穿破")

    print("\n【天干入墓 / 墓庫宮】")
    tombs = bazi.check_tombs()
    if tombs:
        for t in tombs:
            print(f"  ⚠️ {t}")
    else:
        print("  無明顯入墓")

    print("\n【十神】")
    tg = calculate_ten_gods(bazi)
    for name, info in tg.items():
        hidden_str = '、'.join(
            f"{h['stem']}({h['god']})" for h in info['藏干十神']
        )
        print(f"  {name}柱 {info['天干']}({info['天干十神']}) / {info['地支']} [{hidden_str}]  {info['長生宮']}")

    print("\n【以病取用】")
    ill = detect_illness(bazi)
    print(f"  {ill['總述']}")
    ug = recommend_use_god(bazi, ill)
    print(f"  用神建議：{ug['總結']}")

    print("\n【時辰斷法】")
    h_info = bazi.analyze_hour_for_siblings_face_sleep()
    for k, v in h_info.items():
        print(f"  {k}：{v}")

    print("\n【少年克父母】")
    for line in bazi.check_parents_ke():
        print(f"  {line}")

    print("\n【頭胎子女】")
    print(f"  {bazi.check_first_child_gender()}")

    print("\n【六親宮位】")
    sq = analyze_six_qin(bazi)
    for palace, info in sq.items():
        print(f"  {palace}：{info['干支']}  {info['宮支長生狀態']}")
        for note in info['注意事項']:
            if note != '此宮無明顯凶象':
                print(f"    → {note}")

    print("\n【婚姻專斷】")
    m = analyze_marriage(bazi)
    print(f"  {m['總評']}")
    for issue in m['婚姻凶象']:
        if issue != '無明顯婚姻凶象':
            print(f"  ❗{issue}")

    print("\n【財運】")
    w = analyze_wealth(bazi)
    print(f"  {w['總評']}")

    print("\n【大限概覽（以日柱起限）】")
    for lim in calculate_limits(bazi)[:5]:
        print(f"  {lim['限段']} {lim['虛歲']}  {lim['限干支']}（{lim['十神']}）  {lim['運勢初判']}")

    print(sep)


# ==================== 示例 ====================

if __name__ == '__main__':
    # 書中經典命例：壬壬甲丁 / 辰子辰卯
    # 陳秉志《盲派大師夏仲奇命學精粹》例一
    example = Bazi(
        year=Pillar('壬', '辰'),
        month=Pillar('壬', '子'),
        day=Pillar('甲', '辰'),
        hour=Pillar('丁', '卯'),
    )

    # 方式一：直接使用 Bazi 分析函數
    print_bazi_analysis(example)

    # 方式二：使用 BlindSchoolBazi 類
    bs = BlindSchoolBazi(example)
    print("\n【BlindSchoolBazi 全報告（節選）】")
    report = bs.full_report()
    print(f"命局總述：{report['summary']}")
    print(f"婚姻：{report['marriage']['總評']}")
    print(f"用神：{report['use_god']['總結']}")

    # 方式三：從干支字串快速創建
    bs2 = BlindSchoolBazi.from_pillars('壬辰', '壬子', '甲辰', '丁卯')
    print(f"\n（from_pillars 創建）日主：{bs2.bazi.day_master}")
