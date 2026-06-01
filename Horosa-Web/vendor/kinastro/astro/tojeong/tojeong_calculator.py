"""
土亭數計算引擎 (Tojeong Shu Calculator)

核心算法：
1. 先天數：甲己子午九、乙庚丑未八、丙辛寅申七、丁壬卯酉六、戊癸辰戌五、己亥四
2. 後天數：壬子一、丁巳二、甲寅三、辛酉四、戊辰戊五、癸亥六、丙午七、乙卯八、庚申九、丑未十、己百
3. 計算：先天數（干順支逆，除十取零）× 後天數（順計干支，除百十取零）
4. 去首尾兩位，得格局代碼
5. 查 129 格局斷語
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import streamlit as st

# 天干地支
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 先天數 (Pre-heaven Numbers)
# 甲己子午九、乙庚丑未八、丙辛寅申七、丁壬卯酉六、戊癸辰戌五、己亥四
PREHEAVEN_NUMS = {
    "甲": 9, "己": 9, "子": 9, "午": 9,
    "乙": 8, "庚": 8, "丑": 8, "未": 8,
    "丙": 7, "辛": 7, "寅": 7, "申": 7,
    "丁": 6, "壬": 6, "卯": 6, "酉": 6,
    "戊": 5, "癸": 5, "辰": 5, "戌": 5,
    "己": 4, "亥": 4,
}

# 修正：己亥屬之四
PREHEAVEN_NUMS["己"] = 4
PREHEAVEN_NUMS["亥"] = 4

# 後天數 (Post-heaven Numbers)
# 壬子一、丁巳二、甲寅三、辛酉四、戊辰戊五、癸亥六、丙午七、乙卯八、庚申九、丑未十、己百
POSTHEAVEN_NUMS = {
    "壬": 1, "子": 1,
    "丁": 2, "巳": 2,
    "甲": 3, "寅": 3,
    "辛": 4, "酉": 4,
    "戊": 5, "辰": 5,
    "癸": 6, "亥": 6,
    "丙": 7, "午": 7,
    "乙": 8, "卯": 8,
    "庚": 9, "申": 9,
    "丑": 10, "未": 10,
    "己": 100,
}


@st.cache_data(ttl=3600, show_spinner=False)
def load_patterns_data() -> Dict[str, Any]:
    """載入 129 格局數據"""
    pattern_path = os.path.join(os.path.dirname(__file__), "patterns_129.json")
    with open(pattern_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_gangzhi(year: int, month: int, day: int, hour: int) -> Dict[str, str]:
    """
    取得年月日時干支
    使用 sxtwl 計算，月柱按節氣推算（五虎遁）
    """
    try:
        import sxtwl
        d = sxtwl.fromSolar(year, month, day)
        
        # 年柱
        year_gz_obj = d.getYearGZ()
        year_gz = TIANGAN[year_gz_obj.tg] + DIZHI[year_gz_obj.dz]
        year_tg = year_gz_obj.tg
        
        # 日柱
        day_gz_obj = d.getDayGZ()
        day_gz = TIANGAN[day_gz_obj.tg] + DIZHI[day_gz_obj.dz]
        day_tg = day_gz_obj.tg
        
        # 月柱：根據公曆日期判斷節氣月（地支），再用五虎遁求月干
        # 節氣對應（近似日期）：寅月 (2/4 立春)、卯月 (3/6 驚蟄)、辰月 (4/5 清明)、巳月 (5/6 立夏)
        #                      午月 (6/6 芒種)、未月 (7/7 小暑)、申月 (8/8 立秋)、酉月 (9/8 白露)
        #                      戌月 (10/8 寒露)、亥月 (11/7 立冬)、子月 (12/7 大雪)、丑月 (1/6 小寒)
        # 節氣月以「節」為界，例如 8/8 立秋後為申月
        
        # 判斷當前屬於哪個節氣月（從最後一個節氣開始往前找）
        # 1985 年 8 月 26 日：在 8/8 立秋之後，9/8 白露之前 → 申月 (索引 8)
        if month < 2 or (month == 2 and day < 4):
            month_zhi_idx = 1  # 丑月 (1 月小寒前)
        elif month < 3 or (month == 3 and day < 6):
            month_zhi_idx = 2  # 寅月 (立春)
        elif month < 4 or (month == 4 and day < 5):
            month_zhi_idx = 3  # 卯月 (驚蟄)
        elif month < 5 or (month == 5 and day < 6):
            month_zhi_idx = 4  # 辰月 (清明)
        elif month < 6 or (month == 6 and day < 6):
            month_zhi_idx = 5  # 巳月 (立夏)
        elif month < 7 or (month == 7 and day < 7):
            month_zhi_idx = 6  # 午月 (芒種)
        elif month < 8 or (month == 8 and day < 8):
            month_zhi_idx = 7  # 未月 (小暑)
        elif month < 9 or (month == 9 and day < 8):
            month_zhi_idx = 8  # 申月 (立秋)
        elif month < 10 or (month == 10 and day < 8):
            month_zhi_idx = 9  # 酉月 (白露)
        elif month < 11 or (month == 11 and day < 7):
            month_zhi_idx = 10  # 戌月 (寒露)
        elif month < 12 or (month == 12 and day < 7):
            month_zhi_idx = 11  # 亥月 (立冬)
        else:
            month_zhi_idx = 0  # 子月 (大雪)
        
        # 五虎遁：甲己之年丙作首，乙庚之歲戊為頭，丙辛之年尋庚上，丁壬壬寅順水流，戊癸之年甲寅起
        if year_tg in (0, 5):  # 甲己
            month_tg_start = 2  # 丙寅
        elif year_tg in (1, 6):  # 乙庚
            month_tg_start = 4  # 戊寅
        elif year_tg in (2, 7):  # 丙辛
            month_tg_start = 6  # 庚寅
        elif year_tg in (3, 8):  # 丁壬
            month_tg_start = 8  # 壬寅
        else:  # 戊癸 (4, 9)
            month_tg_start = 0  # 甲寅
        
        # 從寅月 (索引 2) 開始數，月干 = (起始干 + 月支 - 2) % 10
        month_tg = (month_tg_start + month_zhi_idx - 2) % 10
        month_gz = TIANGAN[month_tg] + DIZHI[month_zhi_idx]
        
        # 時干支（五鼠遁：根據日干推算時干）
        # 甲己還加甲，乙庚丙作初，丙辛從戊起，丁壬庚子居，戊癸何方發，壬子是真途
        hour_zhi_idx = (hour + 1) // 2 % 12
        if day_tg in (0, 5):  # 甲己
            hour_tg_start = 0  # 甲子
        elif day_tg in (1, 6):  # 乙庚
            hour_tg_start = 2  # 丙子
        elif day_tg in (2, 7):  # 丙辛
            hour_tg_start = 4  # 戊子
        elif day_tg in (3, 8):  # 丁壬
            hour_tg_start = 6  # 庚子
        else:  # 戊癸 (4, 9)
            hour_tg_start = 8  # 壬子
        
        hour_tg = (hour_tg_start + hour_zhi_idx) % 10
        hour_gz = TIANGAN[hour_tg] + DIZHI[hour_zhi_idx]
        
        return {
            "year_gz": year_gz,
            "month_gz": month_gz,
            "day_gz": day_gz,
            "hour_gz": hour_gz
        }
    except Exception as e:
        # 簡化版本（粗略估算）
        year_gz = TIANGAN[(year - 4) % 10] + DIZHI[(year - 4) % 12]
        # 月干支（粗略，實際需考慮節氣）
        month_gan_idx = ((year % 10) * 2 + (month - 1)) % 10
        month_gz = TIANGAN[month_gan_idx] + DIZHI[month - 1 + 2]  # 寅月為正月
        # 日干支（需要曆法計算，此處簡化）
        day_gz = TIANGAN[day % 10] + DIZHI[day % 12]
        # 時干支
        hour_gan_idx = ((day % 10) * 2 + hour // 2) % 10
        hour_gz = TIANGAN[hour_gan_idx] + DIZHI[hour // 2 + 1]
        
        return {
            "year_gz": year_gz,
            "month_gz": month_gz,
            "day_gz": day_gz,
            "hour_gz": hour_gz
        }


def get_preheaven_number(gz: str) -> int:
    """取得先天數（干支各取，除十取零）"""
    gan = gz[0]
    zhi = gz[1]
    
    gan_num = PREHEAVEN_NUMS.get(gan, 0)
    zhi_num = PREHEAVEN_NUMS.get(zhi, 0)
    
    # 干順支逆：干數 + 支數，除 10 取餘（零則作 10）
    total = gan_num + zhi_num
    remainder = total % 10
    return remainder if remainder != 0 else 10


def get_postheaven_number(gz: str, position: int) -> int:
    """
    取得後天數（順計干支，除百十取零）
    position: 第幾位（1-4）
    """
    gan = gz[0]
    zhi = gz[1]
    
    gan_num = POSTHEAVEN_NUMS.get(gan, 0)
    zhi_num = POSTHEAVEN_NUMS.get(zhi, 0)
    
    # 順計：干數 + 支數 + 位置調整
    total = gan_num + zhi_num + (position - 1) * 10
    remainder = total % 110  # 除百十（110）
    return remainder if remainder != 0 else 110


def compute_tojeong_code(year: int, month: int, day: int, hour: int) -> Dict[str, Any]:
    """
    計算土亭數格局代碼
    
    算法：
    1. 取得四柱干支
    2. 先天數：位位除十取零 → 實
    3. 後天數：位位除百十取零 → 法
    4. 實 × 法，位位相乘
    5. 去首尾兩位，得格局代碼
    """
    gz = get_gangzhi(year, month, day, hour)
    four_pillars = [gz["year_gz"], gz["month_gz"], gz["day_gz"], gz["hour_gz"]]
    
    # 先天數（實）
    shi = []
    for i, pillar in enumerate(four_pillars):
        num = get_preheaven_number(pillar)
        shi.append(num)
    
    # 後天數（法）
    fa = []
    for i, pillar in enumerate(four_pillars):
        num = get_postheaven_number(pillar, i + 1)
        fa.append(num)
    
    # 位位相乘
    products = []
    for s, f in zip(shi, fa):
        products.append(s * f)
    
    # 合併成數字串
    product_str = ''.join(str(p) for p in products)
    
    # 去首尾兩位
    if len(product_str) > 2:
        code_str = product_str[1:-1]
    else:
        code_str = product_str
    
    # 取後 6-8 位作為代碼
    code_str = code_str[-8:] if len(code_str) > 8 else code_str
    
    return {
        "four_pillars": gz,
        "shi": shi,
        "fa": fa,
        "products": products,
        "product_str": product_str,
        "code": code_str
    }


def get_tojeong_pattern(code: str, four_pillars: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    """
    根據代碼或四柱查找格局
    返回格局信息（包含三元斷語）
    
    由於 patterns_129.json 中 code 字段為空，改用格局名作為 key 直接查找
    或根據四柱干支的某種規則匹配
    """
    patterns = load_patterns_data()
    
    # 如果有代碼，嘗試匹配（但目前所有 code 都是空的）
    if code:
        for name, data in patterns.items():
            if data.get("code") == code:
                return {
                    "name": name,
                    "id": data["id"],
                    "code": code,
                    "上元": data.get("上元", ""),
                    "中元": data.get("中元", ""),
                    "下元": data.get("下元", ""),
                    "卞元": data.get("卞元", ""),
                    "status": data.get("status", "unknown")
                }
    
    # 如果找不到精確匹配，根據四柱干支計算格局索引
    # 土亭數傳統算法：根據先天數×後天數的乘積去首尾後查表
    # 由於 129 格局沒有 code，我們用 id 來匹配
    # 這裡使用簡化方法：根據代碼數字串的最後幾位取模來選擇格局
    
    if code and len(code) > 0:
        try:
            # 取代碼的最後 2-3 位數字作為索引
            code_num = int(code[-3:]) if len(code) >= 3 else int(code)
            pattern_id = (code_num % 129) + 1  # 1-129
            
            # 根據 id 查找格局
            for name, data in patterns.items():
                if data.get("id") == pattern_id:
                    return {
                        "name": name,
                        "id": pattern_id,
                        "code": code,
                        "上元": data.get("上元", ""),
                        "中元": data.get("中元", ""),
                        "下元": data.get("下元", ""),
                        "卞元": data.get("卞元", ""),
                        "status": "approximate"  # 因為是近似匹配
                    }
        except ValueError:
            pass
    
    # 如果還是找不到，返回第一個完整格局
    for name, data in patterns.items():
        if data.get("status") == "complete":
            return {
                "name": name,
                "id": data["id"],
                "code": code,
                "上元": data.get("上元", ""),
                "中元": data.get("中元", ""),
                "下元": data.get("下元", ""),
                "卞元": data.get("卞元", ""),
                "status": "approximate"
            }
    
    return None


def compute_tojeong_chart(year: int, month: int, day: int, hour: int, 
                          gender: str = "male", 
                          solar_term: Optional[str] = None) -> Dict[str, Any]:
    """
    計算完整的土亭數命盤
    
    參數：
    - year, month, day, hour: 出生時間（農曆）
    - gender: 性別（"male" / "female"）
    - solar_term: 節氣（用於確定三元）
    
    返回：
    - 完整的命盤信息
    """
    # 計算格局代碼
    code_result = compute_tojeong_code(year, month, day, hour)
    
    # 查找格局
    pattern = get_tojeong_pattern(code_result["code"])
    
    # 確定三元（上元/中元/下元）
    # 簡化：根據年份或節氣確定
    if solar_term:
        if "冬至" in solar_term or "小寒" in solar_term or "大寒" in solar_term:
            yuan = "上元"
        elif "春分" in solar_term or "清明" in solar_term or "穀雨" in solar_term:
            yuan = "中元"
        else:
            yuan = "下元"
    else:
        # 簡化：根據年份
        yuan = "上元" if (year % 3) == 0 else ("中元" if (year % 3) == 1 else "下元")
    
    # 性別調整（卞元）
    if gender == "female":
        # 女命用卞元
        bian_yuan = pattern.get("卞元", "") if pattern else ""
    else:
        bian_yuan = ""
    
    return {
        "birth_info": {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "gender": gender,
            "solar_term": solar_term
        },
        "four_pillars": code_result["four_pillars"],
        "calculation": {
            "shi": code_result["shi"],
            "fa": code_result["fa"],
            "products": code_result["products"],
            "product_str": code_result["product_str"],
            "code": code_result["code"]
        },
        "pattern": pattern,
        "yuan": yuan,
        "interpretation": {
            "上元": pattern.get("上元", "") if pattern else "",
            "中元": pattern.get("中元", "") if pattern else "",
            "下元": pattern.get("下元", "") if pattern else "",
            "卞元": bian_yuan
        }
    }
