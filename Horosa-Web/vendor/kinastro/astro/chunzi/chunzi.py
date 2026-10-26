# -*- coding: utf-8 -*-
"""
蠢子數纏度 起盤與結構化解讀模組

蠢子數以二十八宿 + 七政四餘 + 度數為核心的傳統詩詞命理系統，
特別擅長女命婚姻、子息、父母、事業的交叉驗證。

資料庫：data/chunzi_verse.csv（4574 筆詩詞）

主要類別：
    ChunZiVerse  — 單條詩詞及其結構化解析結果（dataclass）
    ChunZiShu    — 資料庫查詢與解析引擎
    ChunZiChart  — 完整命例（支援 summary/to_dict/print_summary）
"""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

# ── 地支常數 ────────────────────────────────────────────────────────────────

BRANCHES: List[str] = [
    "子", "丑", "寅", "卯", "辰", "巳",
    "午", "未", "申", "酉", "戌", "亥",
]
"""十二地支列表（子→亥順序）。"""

BRANCH_ZODIAC: Dict[str, str] = {
    "子": "鼠", "丑": "牛", "寅": "虎", "卯": "兔",
    "辰": "龍", "巳": "蛇", "午": "馬", "未": "羊",
    "申": "猴", "酉": "雞", "戌": "狗", "亥": "豬",
}
"""地支 → 十二生肖屬相對照表。"""

ZODIAC_BRANCH: Dict[str, str] = {v: k for k, v in BRANCH_ZODIAC.items()}
"""十二生肖屬相 → 地支對照表（BRANCH_ZODIAC 的逆映射）。"""

CHINESE_NUM: Dict[str, int] = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
}
"""中文數字（一至十）→ 整數對照表。"""

INT_TO_CN: Dict[int, str] = {v: k for k, v in CHINESE_NUM.items()}
"""整數（1–10）→ 中文數字對照表（CHINESE_NUM 的逆映射）。"""

MANSIONS_28: List[str] = [
    "角", "亢", "氐", "房", "心", "尾", "箕",   # 東方青龍七宿
    "斗", "牛", "女", "虛", "危", "室", "壁",   # 北方玄武七宿
    "奎", "婁", "胃", "昴", "畢", "觜", "參",   # 西方白虎七宿
    "井", "鬼", "柳", "星", "張", "翼", "軫",   # 南方朱雀七宿
]
"""二十八宿名稱列表（東→北→西→南順序）。"""

# ── 內部常數 ─────────────────────────────────────────────────────────────────

_ZODIAC_CHARS = "鼠牛虎兔龍蛇馬羊猴雞狗豬"
_BRANCH_CHARS = "".join(BRANCHES)
_CN_DIGIT_PAT = "[一二三四五六七八九十]"
_CN_AGE_PAT = "[一二三四五六七八九十]{2,3}"

# 月份中文名稱對照（1–12），詩詞習慣以「正月」代一月
_MONTH_CN: Dict[int, str] = {
    1: "正", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六",
    7: "七", 8: "八", 9: "九", 10: "十", 11: "十一", 12: "十二",
}

# 模組預設 CSV 路徑（使用絕對路徑，避免受 CWD 影響）
_DEFAULT_CSV: Path = Path(__file__).parent / "data" / "chunzi_verse.csv"


# ── 工具函式 ─────────────────────────────────────────────────────────────────

def _cn_to_int(text: str) -> Optional[int]:
    """將中文數字字串轉換為阿拉伯整數（支援一至九十九）。

    Args:
        text: 中文數字字串，例如「七十八」、「六十」、「十五」。

    Returns:
        對應的整數；若無法解析則回傳 None。
    """
    text = text.strip()
    if not text:
        return None
    if text == "十":
        return 10
    if len(text) == 1:
        return CHINESE_NUM.get(text)
    if len(text) == 2:
        if text[0] == "十":                        # 十X → 10 + X
            return 10 + CHINESE_NUM.get(text[1], 0)
        if text[1] == "十":                        # X十 → X * 10
            return CHINESE_NUM.get(text[0], 0) * 10
    if len(text) == 3 and text[1] == "十":        # X十Y → X*10 + Y
        return CHINESE_NUM.get(text[0], 0) * 10 + CHINESE_NUM.get(text[2], 0)
    return None


def _build_day_cn(day: int) -> str:
    """將 1–30 的日期轉換為傳統詩詞中使用的中文日期字串。

    Args:
        day: 1–30 之間的整數。

    Returns:
        中文日期字串，例如 1→「初一」、10→「初十」、11→「十一」、20→「二十」。
        輸入超出範圍時回傳空字串。
    """
    if day <= 0 or day > 30:
        return ""
    if day == 10:
        return "初十"
    if day < 10:
        return f"初{INT_TO_CN.get(day, '')}"
    tens = day // 10
    ones = day % 10
    tens_cn = INT_TO_CN.get(tens, "")
    # ones == 0 means a multiple of 10 (e.g. 20 → "二十"), so no trailing digit
    ones_cn = INT_TO_CN.get(ones, "") if ones else ""
    return f"{tens_cn}十{ones_cn}"


def _extract_branch(pillar: str) -> str:
    """從八字柱（天干地支組合）中提取地支。

    Args:
        pillar: 八字柱，例如「辛未」（天干+地支）或單一地支「未」。

    Returns:
        地支字元，例如「未」；若無法識別則回傳原字串。

    Examples:
        >>> _extract_branch("辛未")
        '未'
        >>> _extract_branch("未")
        '未'
    """
    pillar = pillar.strip()
    if len(pillar) >= 2 and pillar[1] in BRANCHES:
        return pillar[1]
    if pillar and pillar[0] in BRANCHES:
        return pillar[0]
    return pillar


# ── ChunZiVerse dataclass ────────────────────────────────────────────────────

@dataclass
class ChunZiVerse:
    """蠢子數單條詩詞及其結構化解析結果。

    Attributes:
        code: 詩詞代碼，格式「宿名 + 星曜 + 度數 + 地支」，例如「室巨9未」。
        category: 所屬分類（通常為二十八宿名）。
        star: 星曜名稱（如巨門、太陰、天機等）。
        degree: 度數（整數）。
        branch: 地支（子、丑、…亥）。
        verse: 原始詩詞文本。
        parents: 父母資訊字典，可含 father/mother（屬相）、
            father_first/mother_first（先亡標記）。
        spouse: 妻宮資訊字典，可含 zodiac（屬相）、concubine（側室）、
            remarriage（再娶）。
        children: 子息資訊字典，可含 count（子息數量）、stone_skin（石皮）。
        career: 事業相關標記列表（例如「文業/科舉」、「手藝」）。
        conflicts: 刑沖相關標記列表（例如「刑沖」、「破財」）。
        longevity: 壽元（整數歲），若詩詞可解析則填入，否則為 None。
        flags: 其他命理標記列表（例如「孤獨」、「再娶」、「科舉」）。
        confidence: 解析信心分數（0.0–1.0），依成功解析的字段數量估算。
    """

    code: str
    category: str
    star: str
    degree: int
    branch: str
    verse: str
    parents: Dict[str, Any] = field(default_factory=dict)
    spouse: Dict[str, Any] = field(default_factory=dict)
    children: Dict[str, Any] = field(default_factory=dict)
    career: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    longevity: Optional[int] = None
    flags: List[str] = field(default_factory=list)
    confidence: float = 0.0


# ── ChunZiShu ────────────────────────────────────────────────────────────────

class ChunZiShu:
    """蠢子數纏度資料庫與解析引擎。

    從 CSV 載入詩詞資料，提供查詢、搜尋、結構化解析等功能。

    Attributes:
        df: 原始 DataFrame（4574 筆詩詞）。
        code_index: 以代碼為鍵的字典索引，加快查詢速度。

    Example:
        >>> czs = ChunZiShu()
        >>> result = czs.get_verse("畢龍6巳")
        >>> print(result["verse"])
    """

    def __init__(self, csv_path: Optional[str] = None) -> None:
        """初始化蠢子數資料庫。

        Args:
            csv_path: CSV 檔案路徑。若為 None，使用模組內建預設路徑。

        Raises:
            FileNotFoundError: 當指定的 CSV 檔案不存在時。
        """
        path = Path(csv_path) if csv_path is not None else _DEFAULT_CSV
        if not path.exists():
            raise FileNotFoundError(f"找不到蠢子數資料檔：{path}")
        self.df: pd.DataFrame = pd.read_csv(str(path), encoding="utf-8-sig")
        # 去除代碼欄兩端空白，確保查詢一致性
        self.df["code"] = self.df["code"].astype(str).str.strip()
        # 去除重複代碼（保留首筆），確保索引唯一
        self.df = self.df.drop_duplicates(subset="code", keep="first")
        self.code_index: Dict[str, dict] = self.df.set_index("code").to_dict("index")

    # ── 公開查詢方法 ─────────────────────────────────────────────────────────

    def get_verse(self, code: str) -> Optional[dict]:
        """依代碼查詢單條詩詞，回傳字典格式。

        Args:
            code: 詩詞代碼，例如「室巨9未」。兩端空白會自動去除。

        Returns:
            包含 code、category、star、degree、branch、verse、mansion28、
            seven_governors 欄位的字典；若代碼不存在則回傳 None。
        """
        code = code.strip()
        if code not in self.code_index:
            return None
        row = self.code_index[code]
        return {
            "code": code,
            "category": row.get("category", ""),
            "star": row.get("star", ""),
            "degree": int(row["degree"]) if pd.notna(row.get("degree")) else 0,
            "branch": row.get("branch", ""),
            "verse": row.get("verse", ""),
            "mansion28": row.get("mansion28", ""),
            "seven_governors": row.get("seven_governors", ""),
        }

    def interpret(self, code: str) -> str:
        """格式化輸出單條詩詞。

        Args:
            code: 詩詞代碼。

        Returns:
            格式化字串，包含代碼、分類、星曜及詩詞文本；
            若代碼不存在則回傳提示訊息。
        """
        result = self.get_verse(code)
        if result is None:
            return f"⚠️  找不到代碼「{code}」，請確認格式，例如：室巨9未"
        return (
            f"【{result['code']}】{result['category']} · {result['star']} · "
            f"{result['degree']}度 · {result['branch']}\n"
            f"{result['verse']}"
        )

    def explain(self, code: str) -> dict:
        """結構化解析單條詩詞，提取父母屬相、妻宮、子息等資訊。

        Args:
            code: 詩詞代碼。

        Returns:
            包含以下欄位的字典：

            - code, verse
            - father_zodiac, mother_zodiac（父母屬相，可為 None）
            - spouse_zodiac（配偶屬相，可為 None）
            - children_count（子息數量，可為 None）
            - birth_hour（出生時辰地支，可為 None）
            - birth_ke（出生刻數整數，可為 None）
            - longevity（壽元整數，可為 None）
            - flags（命理標記字串列表）

            若代碼不存在，回傳含 ``error`` 欄位的字典。
        """
        obj = self._get_verse_obj(code)
        if obj is None:
            return {"error": f"找不到代碼「{code}」"}

        text = obj.verse

        # 出生時辰（搜尋「X時生人」）
        birth_hour: Optional[str] = None
        if m := re.search(rf"([{_BRANCH_CHARS}])時生人", text):
            birth_hour = m.group(1)

        # 出生刻數（搜尋「X刻生」）
        birth_ke: Optional[int] = None
        if m := re.search(rf"({_CN_DIGIT_PAT})刻生", text):
            birth_ke = CHINESE_NUM.get(m.group(1))

        return {
            "code": obj.code,
            "verse": obj.verse,
            "father_zodiac": obj.parents.get("father"),
            "mother_zodiac": obj.parents.get("mother"),
            "spouse_zodiac": obj.spouse.get("zodiac"),
            "children_count": obj.children.get("count"),
            "birth_hour": birth_hour,
            "birth_ke": birth_ke,
            "longevity": obj.longevity,
            "flags": list(obj.flags),
        }

    def search(self, keyword: str, limit: int = 10) -> List[dict]:
        """關鍵字全文搜尋詩詞。

        Args:
            keyword: 搜尋關鍵字。
            limit: 最多回傳筆數，預設 10。

        Returns:
            符合條件的詩詞字典列表；若無符合結果，回傳空列表。
        """
        keyword = keyword.strip()
        if not keyword:
            return []
        mask = self.df["verse"].str.contains(keyword, regex=False, na=False)
        return self._rows_to_dicts(self.df[mask].head(limit))

    def get_verses_by_mansion(self, name: str, limit: Optional[int] = None) -> List[dict]:
        """依二十八宿名稱查詢詩詞。

        同時比對 ``category`` 欄與 ``mansion28`` 欄，取聯集結果。

        Args:
            name: 宿名，例如「室」、「角」。兩端空白會自動去除。
            limit: 最多回傳筆數；None 表示回傳全部。

        Returns:
            屬於該宿的詩詞字典列表。
        """
        name = name.strip()
        if not name:
            return []
        mask = (self.df["category"] == name) | (self.df["mansion28"] == name)
        subset = self.df[mask]
        if limit is not None:
            subset = subset.head(limit)
        return self._rows_to_dicts(subset)

    def search_by_tags(self, tags: List[str], limit: int = 20) -> List[dict]:
        """多標籤 AND 搜尋（所有標籤都必須出現在詩詞中）。

        Args:
            tags: 關鍵字列表，所有關鍵字都必須同時出現。
            limit: 最多回傳筆數，預設 20。

        Returns:
            同時包含所有標籤的詩詞字典列表；空列表 tags 回傳空列表。
        """
        tags = [t.strip() for t in tags if t.strip()]
        if not tags:
            return []
        mask = pd.Series([True] * len(self.df), index=self.df.index)
        for tag in tags:
            mask &= self.df["verse"].str.contains(tag, regex=False, na=False)
        return self._rows_to_dicts(self.df[mask].head(limit))

    def get_verses_by_hour(self, branch: str) -> List[dict]:
        """依出生時辰（地支）查詢詩詞。

        搜尋詩詞文本中含「X時生人」的所有條目。

        Args:
            branch: 地支，例如「未」、「子」。

        Returns:
            詩詞中含「X時生人」的字典列表；無效地支回傳空列表。
        """
        branch = branch.strip()
        if not branch or branch not in BRANCHES:
            return []
        return self.search(f"{branch}時生人", limit=len(self.df))

    def batch_lookup(self, codes: List[str]) -> List[dict]:
        """批量查詢多個代碼，回傳與輸入等長的列表。

        找不到的代碼會以含提示訊息的佔位字典替代，不會縮短結果列表。

        Args:
            codes: 代碼列表。

        Returns:
            與輸入等長的字典列表；缺失代碼的字典 verse 欄位含警告提示。
        """
        results: List[dict] = []
        for code in codes:
            row = self.get_verse(code)
            if row is None:
                results.append({
                    "code": code,
                    "verse": f"⚠️  無此代碼：「{code}」",
                    "category": "", "star": "", "degree": 0, "branch": "",
                    "mansion28": "", "seven_governors": "",
                })
            else:
                results.append(row)
        return results

    def batch_get(self, codes: List[str]) -> List[ChunZiVerse]:
        """批量查詢，回傳 ChunZiVerse 物件列表（略過不存在的代碼）。

        供 ChunZiChart 內部使用。

        Args:
            codes: 代碼列表。

        Returns:
            成功找到的 ChunZiVerse 物件列表；不存在的代碼會被略過。
        """
        return [v for c in codes if (v := self._get_verse_obj(c)) is not None]

    def determine_codes(
        self,
        gender: str,
        bazi: str,
        ke: Optional[int] = None,
    ) -> List[str]:
        """【考時法 Hook】根據性別與八字推算詩詞代碼列表。

        此方法目前為預留介面（stub），未來可接入完整考時法邏輯。

        Args:
            gender: 性別，「乾」（男）或「坤」（女）。
            bazi: 八字，例如「丁丑 乙巳 甲子 辛未」。
            ke: 出生刻數（可選）。

        Returns:
            推算出的詩詞代碼列表；目前版本回傳空列表。
        """
        # TODO: 接入真正的考時法推算邏輯
        return []

    def get_hour_codes(
        self,
        gender: str,
        hour_branch: str,
        ke: Optional[int] = None,
    ) -> List[str]:
        """【Phase 1】根據性別、時辰地支（與可選刻數）找出候選詩詞代碼。

        搜尋資料庫中含有「X時生人」文字的詩詞，並依性別與刻數進行篩選與排序：

        - 坤造（女命）：優先回傳 category == "女" 的詩詞，其次為其他宿分類。
        - 乾造（男命）：優先回傳 category != "女" 的詩詞。
        - 若提供 ke，同時搜尋含「X刻生」的詩詞；若有交集則優先回傳；
          若交集為空，則改回傳單純時辰匹配的結果。

        Args:
            gender: 性別，「乾」（男）或「坤」（女）。
            hour_branch: 出生時辰地支，例如「未」、「子」。
              可接受完整八字柱（如「辛未」），自動提取地支。
            ke: 出生刻數（整數 1–10，可選）。

        Returns:
            符合條件的詩詞代碼列表；無符合結果時回傳空列表。

        Examples:
            >>> czs = ChunZiShu()
            >>> czs.get_hour_codes("坤", "未", ke=3)
            [...]
            >>> czs.get_hour_codes("乾", "辛未")  # 自動提取地支「未」
            [...]
        """
        branch = _extract_branch(hour_branch)
        if not branch or branch not in BRANCHES:
            return []

        hour_pattern = f"{branch}時生人"
        hour_mask = self.df["verse"].str.contains(hour_pattern, regex=False, na=False)
        hour_df = self.df[hour_mask].copy()

        if hour_df.empty:
            return []

        # 依性別排序：坤造優先「女」分類，乾造優先非「女」分類
        if gender == "坤":
            hour_df = pd.concat([
                hour_df[hour_df["category"] == "女"],
                hour_df[hour_df["category"] != "女"],
            ])
        else:
            hour_df = pd.concat([
                hour_df[hour_df["category"] != "女"],
                hour_df[hour_df["category"] == "女"],
            ])

        hour_codes = hour_df["code"].tolist()

        if ke is not None:
            ke_cn = INT_TO_CN.get(ke)
            if ke_cn:
                ke_pattern = f"{ke_cn}刻生"
                ke_mask = self.df["verse"].str.contains(ke_pattern, regex=False, na=False)
                ke_codes = set(self.df[ke_mask]["code"].tolist())
                # 時 + 刻 交集優先；若交集為空則回退至純時辰結果
                intersection = [c for c in hour_codes if c in ke_codes]
                if intersection:
                    return intersection

        return hour_codes

    def get_month_day_codes(
        self,
        gender: str,
        month: int,
        day: int,
    ) -> List[str]:
        """【Phase 2 Hook】根據性別、農曆月份與日期找出候選詩詞代碼。

        搜尋資料庫中含有「X月...X日」文字的詩詞。
        此功能目前仍處於 Phase 2 階段，邏輯尚未完整，
        可依需求擴充月份/日期的模糊匹配規則。

        Args:
            gender: 性別，「乾」（男）或「坤」（女）。
            month: 農曆出生月份（整數 1–12）。
            day: 農曆出生日（整數 1–30）。

        Returns:
            符合條件的詩詞代碼列表；無符合結果或月日超出範圍時回傳空列表。

        Note:
            本方法為 Phase 2 Hook，子類別可覆寫此方法以接入完整規則。
            目前實作採用基礎文字比對，尚未支援閏月或農曆換算。
        """
        month_cn = _MONTH_CN.get(month, "")
        day_cn = _build_day_cn(day)
        if not month_cn or not day_cn:
            return []

        # 搜尋「X月...X日」或「X月生X日」等常見格式
        # 詩詞範例：「生辰五月初九日」、「閏三月生二十七」
        month_pat = f"{month_cn}月"
        day_pat = day_cn

        mask_month = self.df["verse"].str.contains(month_pat, regex=False, na=False)
        mask_day = self.df["verse"].str.contains(day_pat, regex=False, na=False)
        combined = self.df[mask_month & mask_day].copy()

        if combined.empty:
            return []

        # 依性別排序
        if gender == "坤":
            combined = pd.concat([
                combined[combined["category"] == "女"],
                combined[combined["category"] != "女"],
            ])
        else:
            combined = pd.concat([
                combined[combined["category"] != "女"],
                combined[combined["category"] == "女"],
            ])

        return combined["code"].tolist()

    def cast_chart(
        self,
        gender: str,
        year: str,
        month: str,
        day: str,
        hour: str,
        ke: Optional[int] = None,
        lunar_month: Optional[int] = None,
        lunar_day: Optional[int] = None,
    ) -> "ChunZiChart":
        """根據性別、八字與刻數，自動找出候選詩詞並回傳 ChunZiChart 物件。

        此方法為主要起盤入口（Phase 1 + Phase 2 合併）：

        - **Phase 1**：依時辰地支（從 ``hour`` 柱提取）與刻數搜尋時辰條文。
        - **Phase 2**：若同時提供 ``lunar_month`` 和 ``lunar_day``，
          則額外搜尋月日條文並合併至結果中。

        多來源代碼會去重合併，坤造優先保留「女」分類詩詞的順序。

        Args:
            gender: 性別，「乾」（男）或「坤」（女）。
            year: 年柱，例如「丁丑」。
            month: 月柱，例如「乙巳」。
            day: 日柱，例如「甲子」。
            hour: 時柱，例如「辛未」。地支將自動提取。
            ke: 出生刻數（整數 1–10，可選）。
            lunar_month: 農曆出生月份（整數 1–12，可選；提供時啟用 Phase 2）。
            lunar_day: 農曆出生日（整數 1–30，可選；需與 lunar_month 同時提供）。

        Returns:
            已載入候選詩詞的 ChunZiChart 物件。
            若未找到任何代碼，ChunZiChart.codes 為空列表，
            並會發出 UserWarning 提示。

        Raises:
            ValueError: 當 gender 不為「乾」或「坤」時。

        Examples:
            >>> czs = ChunZiShu()
            >>> chart = czs.cast_chart("坤", "丁丑", "乙巳", "甲子", "辛未", ke=3)
            >>> chart.print_summary()

            >>> # 同時提供農曆月日（Phase 2）
            >>> chart = czs.cast_chart(
            ...     "坤", "癸丑", "壬戌", "庚寅", "丁丑",
            ...     ke=6, lunar_month=5, lunar_day=9
            ... )
        """
        if gender not in ("乾", "坤"):
            raise ValueError(f"gender 必須為「乾」或「坤」，收到：「{gender}」")

        bazi = f"{year} {month} {day} {hour}"

        # Phase 1：依時辰（+ 刻數）找候選代碼
        hour_codes = self.get_hour_codes(gender, hour, ke=ke)

        # Phase 2：依農曆月日找候選代碼（需明確提供）
        month_day_codes: List[str] = []
        if lunar_month is not None and lunar_day is not None:
            month_day_codes = self.get_month_day_codes(gender, lunar_month, lunar_day)

        # 合併去重（保留來源順序：時辰優先，月日補充）
        merged_codes = list(dict.fromkeys(hour_codes + month_day_codes))

        if not merged_codes:
            warnings.warn(
                f"cast_chart：未能從資料庫中找到符合條件的詩詞代碼。"
                f"（gender={gender}, hour={hour}, ke={ke}"
                + (f", lunar={lunar_month}/{lunar_day}" if lunar_month else "")
                + "）建議手動呼叫 add_codes() 補充代碼。",
                UserWarning,
                stacklevel=2,
            )

        chart = ChunZiChart(gender=gender, bazi=bazi, ke=ke, codes=merged_codes)
        chart.add_codes(merged_codes, self)
        return chart

    # ── 私有方法 ─────────────────────────────────────────────────────────────

    def _get_verse_obj(self, code: str) -> Optional[ChunZiVerse]:
        """內部：依代碼取得已解析的 ChunZiVerse 物件。"""
        code = code.strip()
        if code not in self.code_index:
            return None
        row = self.code_index[code]
        v = ChunZiVerse(
            code=code,
            category=row.get("category", ""),
            star=row.get("star", ""),
            degree=int(row["degree"]) if pd.notna(row.get("degree")) else 0,
            branch=row.get("branch", ""),
            verse=row.get("verse", ""),
        )
        self._parse(v)
        return v

    def _parse(self, v: ChunZiVerse) -> None:
        """結構化解析詩詞，填入 ChunZiVerse 各字段。

        解析項目：父母屬相、妻宮屬相、子息數量、壽元、事業（科舉/手藝）、
        刑沖、再娶、孤獨等，並根據成功解析字段數估算信心分數。

        Args:
            v: 待解析的 ChunZiVerse 物件（就地修改）。
        """
        text = v.verse
        parsed = 0
        total = 7  # 父、母、妻、子、壽、時辰、刻數

        # ── 父親屬相（多模式匹配，由嚴格到寬鬆）
        for pat in (
            rf"父[是命]?屬([{_ZODIAC_CHARS}])",
            rf"父親屬([{_ZODIAC_CHARS}])",
            rf"父屬([{_ZODIAC_CHARS}])",
        ):
            if m := re.search(pat, text):
                v.parents["father"] = m.group(1)
                parsed += 1
                break

        # ── 母親屬相
        for pat in (
            rf"母[是命]?屬([{_ZODIAC_CHARS}])",
            rf"母親屬([{_ZODIAC_CHARS}])",
            rf"母屬([{_ZODIAC_CHARS}])",
        ):
            if m := re.search(pat, text):
                v.parents["mother"] = m.group(1)
                parsed += 1
                break

        if "先去父" in text:
            v.parents["father_first"] = True
        if "母先" in text or "先去母" in text:
            v.parents["mother_first"] = True

        # ── 妻宮屬相
        for pat in (
            rf"妻宮屬([{_ZODIAC_CHARS}])",
            rf"妻[命]?屬([{_ZODIAC_CHARS}])",
            rf"配偶屬([{_ZODIAC_CHARS}])",
        ):
            if m := re.search(pat, text):
                v.spouse["zodiac"] = m.group(1)
                parsed += 1
                break

        if "側室" in text:
            v.spouse["concubine"] = True
        if "再娶" in text:
            v.spouse["remarriage"] = True

        # ── 子息數量
        for pat in (
            rf"[育生]([{_CN_DIGIT_PAT[1:-1]}])子",
            rf"子息([{_CN_DIGIT_PAT[1:-1]}])[個名]?",
        ):
            if m := re.search(pat, text):
                n = CHINESE_NUM.get(m.group(1))
                if n:
                    v.children["count"] = n
                    parsed += 1
                    break

        if "石皮" in text or "帶破" in text:
            v.children["stone_skin"] = True

        # ── 壽元
        v.longevity = self._parse_longevity(text)
        if v.longevity:
            parsed += 1

        # ── 出生時辰（計入信心分數）
        if re.search(rf"[{_BRANCH_CHARS}]時生人", text):
            parsed += 1

        # ── 出生刻數（計入信心分數）
        if re.search(rf"{_CN_DIGIT_PAT}刻生", text):
            parsed += 1

        # ── 事業標記
        if any(kw in text for kw in ("折桂", "入泮", "封章", "及第", "功名")):
            v.career.append("文業/科舉")
        if any(kw in text for kw in ("手藝", "工匠", "技藝")):
            v.career.append("手藝")

        # ── 刑沖標記
        if any(kw in text for kw in ("刑冲", "刑沖", "沖克")):
            v.conflicts.append("刑沖")
        if "破財" in text:
            v.conflicts.append("破財")

        # ── 其他命理標記
        if "孤獨" in text:
            v.flags.append("孤獨")
        if "再娶" in text:
            v.flags.append("再娶")
        if any(kw in text for kw in ("折桂", "及第", "功名", "科舉", "入泮")):
            v.flags.append("科舉")
        if any(kw in text for kw in ("手藝", "工匠")):
            v.flags.append("手藝")

        # ── 信心分數（0.0–1.0）
        v.confidence = round(min(parsed, total) / total, 2)

    @staticmethod
    def _parse_longevity(text: str) -> Optional[int]:
        """從詩詞文本中提取壽元年齡（整數）。

        Args:
            text: 詩詞文本。

        Returns:
            壽元整數（歲）；無法解析則回傳 None。
        """
        for pat in (
            rf"壽[享元]?({_CN_AGE_PAT})歲",
            rf"享壽({_CN_AGE_PAT})歲",
            rf"壽到({_CN_AGE_PAT})歲",
            rf"壽至({_CN_AGE_PAT})歲",
        ):
            if m := re.search(pat, text):
                val = _cn_to_int(m.group(1))
                if val and 30 <= val <= 130:
                    return val
        return None

    def _rows_to_dicts(self, subset: pd.DataFrame) -> List[dict]:
        """將 DataFrame subset 轉換為標準字典列表。

        Args:
            subset: 篩選後的 DataFrame。

        Returns:
            每列對應一個包含標準欄位的字典列表。
        """
        results: List[dict] = []
        for _, row in subset.iterrows():
            code = str(row.get("code", "")).strip()
            results.append({
                "code": code,
                "category": row.get("category", ""),
                "star": row.get("star", ""),
                "degree": int(row["degree"]) if pd.notna(row.get("degree")) else 0,
                "branch": row.get("branch", ""),
                "verse": row.get("verse", ""),
                "mansion28": row.get("mansion28", ""),
                "seven_governors": row.get("seven_governors", ""),
            })
        return results


# ── ChunZiChart ──────────────────────────────────────────────────────────────

class ChunZiChart:
    """蠢子數命例，代表一個完整的起盤結果。

    整合性別、八字、起盤代碼與詩詞解析結果，提供命例總覽與結構化輸出。

    Attributes:
        gender: 性別，「乾」（男）或「坤」（女）。
        bazi: 八字，格式「年柱 月柱 日柱 時柱」，例如「丁丑 乙巳 甲子 辛未」。
        ke: 出生刻數（可選）。
        codes: 起盤代碼列表。
        verses: 解析後的 ChunZiVerse 物件列表。
        analysis: 彙整後的分析結果字典。

    Example:
        >>> czs = ChunZiShu()
        >>> chart = ChunZiChart("坤", "丁丑 乙巳 甲子 辛未", ke=3)
        >>> chart.add_codes(["室巨9未", "角陰13酉"], czs)
        >>> chart.print_summary()
    """

    def __init__(
        self,
        gender: str,
        bazi: str,
        ke: Optional[int] = None,
        codes: Optional[List[str]] = None,
    ) -> None:
        """初始化命例。

        Args:
            gender: 性別，「乾」或「坤」。
            bazi: 八字字串。
            ke: 出生刻數（可選）。
            codes: 可直接傳入已知代碼（可選）；傳入後仍需呼叫 add_codes 載入詩詞。
        """
        self.gender = gender
        self.bazi = bazi
        self.ke = ke
        self.codes: List[str] = list(codes) if codes else []
        self.verses: List[ChunZiVerse] = []
        self.analysis: Dict[str, Any] = {}

    def add_codes(self, codes: List[str], czs: ChunZiShu) -> None:
        """載入起盤代碼並進行結構化彙整分析。

        不存在的代碼會被略過並發出 UserWarning 提示。

        Args:
            codes: 詩詞代碼列表。
            czs: ChunZiShu 資料庫實例。
        """
        self.codes = list(codes)
        missing = [c for c in codes if czs.get_verse(c) is None]
        if missing:
            warnings.warn(
                f"以下代碼不存在，已略過：{missing}",
                UserWarning,
                stacklevel=2,
            )
        self.verses = czs.batch_get(codes)
        self._analyze()

    def _analyze(self) -> None:
        """內部：彙整所有詩詞的解析結果至 self.analysis。

        坤造（女命）優先採用分類為「女」的詩詞解析結果。
        """
        result: Dict[str, Any] = {
            "parents": {},
            "spouse": {},
            "children": {},
            "career": [],
            "conflicts": [],
            "flags": [],
            "verses": [],
            "longevity": None,
        }

        # 坤造優先排序「女」分類詩詞
        if self.gender == "坤":
            primary = [v for v in self.verses if v.category == "女"]
            secondary = [v for v in self.verses if v.category != "女"]
            ordered = primary + secondary
        else:
            ordered = list(self.verses)

        for v in ordered:
            result["verses"].append({
                "code": v.code,
                "text": v.verse,
                "confidence": v.confidence,
            })
            # 字典型欄位：不覆蓋已有值（優先保留較高信心度的首筆資料）
            for key in ("parents", "spouse", "children"):
                existing: dict = result[key]
                for k, val in getattr(v, key).items():
                    if k not in existing:
                        existing[k] = val
            # 列表型欄位：去重合併（保留順序）
            result["career"].extend(v.career)
            result["conflicts"].extend(v.conflicts)
            result["flags"].extend(v.flags)
            # 壽元：取首筆非 None
            if result["longevity"] is None and v.longevity:
                result["longevity"] = v.longevity

        result["career"] = list(dict.fromkeys(result["career"]))
        result["conflicts"] = list(dict.fromkeys(result["conflicts"]))
        result["flags"] = list(dict.fromkeys(result["flags"]))
        self.analysis = result

    def determine_codes(
        self,
        czs: Optional[ChunZiShu] = None,
        ke: Optional[int] = None,
    ) -> List[str]:
        """【考時法 Hook】根據命例的性別與八字推算詩詞代碼。

        此方法目前為預留介面（stub），未來可接入完整考時法邏輯。
        若 self.codes 已設定，則回傳目前代碼副本。

        Args:
            czs: ChunZiShu 資料庫實例（可選，未來考時法邏輯可能需要）。
            ke: 覆蓋刻數（可選，預設使用 self.ke）。

        Returns:
            推算出的詩詞代碼列表；目前版本回傳 self.codes 的副本。
        """
        # TODO: 接入真正的考時法推算邏輯
        return list(self.codes)

    def summary(self) -> str:
        """產生漂亮的命例總覽字串。

        Returns:
            包含性別、八字、刻數、代碼、父母、妻宮、子息、事業、刑沖、
            壽元、特記及原始詩詞的命例總覽字串。
        """
        ke_str = f"第{self.ke}刻" if self.ke is not None else ""
        separator = "─" * 42
        lines = [
            f"┌{separator}┐",
            f"│  蠢子數命例總覽",
            f"│  {'乾造' if self.gender == '乾' else '坤造'}：{self.bazi}　{ke_str}",
            f"│  代碼：{'、'.join(self.codes) if self.codes else '（未設定）'}",
            f"├{separator}┤",
        ]

        parents = self.analysis.get("parents", {})
        spouse = self.analysis.get("spouse", {})
        children = self.analysis.get("children", {})
        career = self.analysis.get("career", [])
        conflicts = self.analysis.get("conflicts", [])
        flags = self.analysis.get("flags", [])
        longevity = self.analysis.get("longevity")

        # 父母欄位格式化
        parent_parts: List[str] = []
        if "father" in parents:
            parent_parts.append(f"父屬{parents['father']}")
        if "mother" in parents:
            parent_parts.append(f"母屬{parents['mother']}")
        if parents.get("father_first"):
            parent_parts.append("父先亡")
        if parents.get("mother_first"):
            parent_parts.append("母先亡")
        parent_str = "、".join(parent_parts) if parent_parts else "未能解析"

        # 妻宮欄位格式化
        spouse_parts: List[str] = []
        if "zodiac" in spouse:
            spouse_parts.append(f"屬{spouse['zodiac']}")
        if spouse.get("concubine"):
            spouse_parts.append("有側室")
        if spouse.get("remarriage"):
            spouse_parts.append("有再娶")
        spouse_str = "、".join(spouse_parts) if spouse_parts else "未能解析"

        # 子息欄位格式化
        children_parts: List[str] = []
        if "count" in children:
            children_parts.append(f"{children['count']}子")
        if children.get("stone_skin"):
            children_parts.append("帶石皮")
        children_str = "、".join(children_parts) if children_parts else "未能解析"

        lines += [
            f"│  父母：{parent_str}",
            f"│  妻宮：{spouse_str}",
            f"│  子息：{children_str}",
            f"│  事業：{'、'.join(career) if career else '無特別記錄'}",
            f"│  刑沖：{'、'.join(conflicts) if conflicts else '無特別記錄'}",
        ]

        if longevity:
            lines.append(f"│  壽元：{longevity}歲")
        if flags:
            lines.append(f"│  特記：{'、'.join(flags)}")

        verses = self.analysis.get("verses", [])
        if verses:
            lines.append(f"├{separator}┤")
            lines.append(f"│  詩詞（共{len(verses)}首）：")
            for vd in verses:
                snippet = vd["text"][:38]
                lines.append(f"│    【{vd['code']}】{snippet}")

        lines.append(f"└{separator}┘")
        return "\n".join(lines)

    def print_summary(self) -> None:
        """直接在終端機印出漂亮的命例總覽。"""
        print(self.summary())

    def to_dict(self) -> Dict[str, Any]:
        """將命例轉換為 JSON 可序列化的字典。

        Returns:
            包含 gender、bazi、ke、codes 及完整 analysis 的字典，
            可直接用於 json.dumps() 或存入資料庫。
        """
        return {
            "gender": self.gender,
            "bazi": self.bazi,
            "ke": self.ke,
            "codes": list(self.codes),
            "analysis": self.analysis,
        }

    def to_json(self, indent: int = 2, ensure_ascii: bool = False) -> str:
        """將命例序列化為 JSON 字串。

        Args:
            indent: JSON 縮排空格數，預設 2。
            ensure_ascii: 是否將非 ASCII 字元轉義；預設 False（保留中文）。

        Returns:
            格式化的 JSON 字串，包含命例所有資料。

        Example:
            >>> chart.to_json()
            '{"gender": "坤", "bazi": "...", ...}'
        """
        import json
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)


# ── 使用範例 ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    czs = ChunZiShu()

    print("=" * 50)
    print("【手動模式】直接傳入已知代碼")
    print("=" * 50)

    # === 第一命例（手動模式）===
    chart1 = ChunZiChart("坤", "丁丑 乙巳 甲子 辛未", ke=3)
    chart1.add_codes(
        ["室巨9未", "角陰13酉", "柳計6巳", "虛陽7午", "女火5辰", "壁紫3未"],
        czs,
    )
    chart1.print_summary()

    # === 第二命例（手動模式）===
    chart2 = ChunZiChart("坤", "癸丑 壬戌 庚寅 丁丑", ke=6)
    chart2.add_codes(["畢龍6巳"], czs)
    chart2.print_summary()

    print()
    print("=" * 50)
    print("【半自動模式】cast_chart() 從時辰自動搜尋條文")
    print("=" * 50)

    # === 第一命例（半自動模式）：坤造，辛未時，第3刻 ===
    chart3 = czs.cast_chart("坤", "丁丑", "乙巳", "甲子", "辛未", ke=3)
    print(f"\n自動找到 {len(chart3.codes)} 條時辰條文：{chart3.codes[:5]}")
    chart3.print_summary()

    # === 第二命例（半自動模式 + Phase 2）：坤造，丁丑時，第6刻，農曆五月初九 ===
    chart4 = czs.cast_chart(
        "坤", "癸丑", "壬戌", "庚寅", "丁丑",
        ke=6, lunar_month=5, lunar_day=9,
    )
    print(f"\n自動找到 {len(chart4.codes)} 條條文（時辰+月日）：{chart4.codes[:5]}")
    chart4.print_summary()

    # === 展示 to_json() ===
    print("\n=== to_json() 輸出範例（前 300 字）===")
    print(chart3.to_json()[:300])
