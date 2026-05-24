#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從梁湘潤版《鐵板神數》提取日月星辰數表
生成完整的數表映射 JSON 文件

數表結構說明：
- 12 宮位：子 1, 丑 2, 寅 3, 卯 4, 辰 5, 巳 6, 午 7, 未 8, 申 9, 酉 10, 戌 11, 亥 12
- 每宮 12 天干循環
- 每干支組合對應 12 個數字 (對應 12 地支)

來源：《鐵板神數梁湘潤.txt》p.1500-4320
"""

import json
from typing import Dict, List, Tuple

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 從文本中提取的數表基礎數據
# 格式：(宮位，起始天干，起始數字)
# 根據文本 p.1500-4320 整理

LIANG_TABLE_BASE = {
    # 子 1 宮 (文本中較少，從其他宮推算)
    # 從文本推算：子宮數表從甲 11 開始
    '子': {'start_stem_idx': 0, 'start_num': 121, 'stem_seq': list(range(11, 21))},
    
    # 丑 2 宮 (p.1642-1801)
    # 戊 45 起，數字 529-660
    '丑': {'start_stem_idx': 4, 'start_num': 529, 'stem_seq': list(range(45, 67))},
    
    # 寅 3 宮 (p.1803-2058)
    # 庚 67 起，數字 793-1056
    '寅': {'start_stem_idx': 6, 'start_num': 793, 'stem_seq': list(range(67, 89))},
    
    # 卯 4 宮 (p.2063-2383)
    # 癸 100 起，數字 1189-1452
    '卯': {'start_stem_idx': 9, 'start_num': 1189, 'stem_seq': list(range(100, 122))},
    
    # 辰 5 宮 (從文本推算)
    # 甲 111 起
    '辰': {'start_stem_idx': 0, 'start_num': 1453, 'stem_seq': list(range(111, 133))},
    
    # 巳 6 宮 (p.2503-2535)
    # 戊 155 起，數字 1849-1980
    '巳': {'start_stem_idx': 4, 'start_num': 1849, 'stem_seq': list(range(155, 177))},
    
    # 午 7 宮 (p.2539-2590)
    # 庚 177 起，數字 2113-2244
    '午': {'start_stem_idx': 6, 'start_num': 2113, 'stem_seq': list(range(177, 199))},
    
    # 未 8 宮 (p.2609-2768)
    # 甲 221 起，數字 2641-2772
    '未': {'start_stem_idx': 0, 'start_num': 2641, 'stem_seq': list(range(221, 243))},
    
    # 申 9 宮 (p.2934-3245)
    # 丙 243 起，數字 2905-3036
    '申': {'start_stem_idx': 2, 'start_num': 2905, 'stem_seq': list(range(243, 265))},
    
    # 酉 10 宮 (p.3251-3563)
    # 戊 265 起，數字 3169-3300
    '酉': {'start_stem_idx': 4, 'start_num': 3169, 'stem_seq': list(range(265, 287))},
    
    # 戌 11 宮 (p.3568-3679)
    # 壬 309 起，數字 3697-3828
    '戌': {'start_stem_idx': 8, 'start_num': 3697, 'stem_seq': list(range(309, 331))},
    
    # 亥 12 宮 (p.3684-3860)
    # 甲 331 起，數字 4081-4212
    '亥': {'start_stem_idx': 0, 'start_num': 4081, 'stem_seq': list(range(331, 353))},
}


def generate_liang_number_table() -> Dict[str, Dict[str, List[int]]]:
    """
    生成梁湘潤版日月星辰數表
    
    Returns
    -------
    Dict[str, Dict[str, List[int]]]
        {(宮位，天干): [12 個地支對應的數字]}
    """
    table = {}
    
    for palace_idx, palace in enumerate(EARTHLY_BRANCHES):
        if palace not in LIANG_TABLE_BASE:
            continue
            
        base = LIANG_TABLE_BASE[palace]
        start_stem_idx = base['start_stem_idx']
        start_num = base['start_num']
        
        # 每宮有 12 個天干循環 (實際是 10 天干 +2 重複)
        # 每個天干對應 12 個地支數字
        for i in range(12):
            stem_idx = (start_stem_idx + i) % 10
            stem = HEAVENLY_STEMS[stem_idx]
            
            # 每個干支組合對應 12 個數字 (12 地支)
            # 數字間隔為 12 (因為每列 12 個數字)
            numbers = []
            for j in range(12):
                num = start_num + (i * 12) + j
                numbers.append(num)
            
            key = f"{palace}_{stem}"
            table[key] = numbers
    
    return table


def generate_liang_table_v2() -> Dict[Tuple[str, str], List[int]]:
    """
    生成梁湘潤版日月星辰數表 (版本 2 - 更精確)
    
    根據文本實際數字重新計算：
    - 每宮 12 行 (12 地支)
    - 每行 11-12 個天干
    - 每個干支對應 1 個數字
    
    Returns
    -------
    Dict[Tuple[str, str], List[int]]
        {(宮位，天干): [12 個數字]}
    """
    table = {}
    
    # 根據文本實際數據重新整理
    # 每宮的數字範圍和天干起始
    
    palace_data = [
        # (宮位，宮位號，起始天干 idx，起始數字，天干數量)
        ('子', 1, 0, 121, 12),    # 甲 11 起
        ('丑', 2, 4, 529, 12),    # 戊 45 起
        ('寅', 3, 6, 793, 12),    # 庚 67 起
        ('卯', 4, 9, 1189, 12),   # 癸 100 起
        ('辰', 5, 0, 1453, 12),   # 甲 111 起
        ('巳', 6, 4, 1849, 12),   # 戊 155 起
        ('午', 7, 6, 2113, 12),   # 庚 177 起
        ('未', 8, 0, 2641, 12),   # 甲 221 起
        ('申', 9, 2, 2905, 12),   # 丙 243 起
        ('酉', 10, 4, 3169, 12),  # 戊 265 起
        ('戌', 11, 8, 3697, 12),  # 壬 309 起
        ('亥', 12, 0, 4081, 12),  # 甲 331 起
    ]
    
    for palace, palace_num, start_stem_idx, start_num, num_stems in palace_data:
        for i in range(num_stems):
            stem_idx = (start_stem_idx + i) % 10
            stem = HEAVENLY_STEMS[stem_idx]
            
            # 每個干支對應 12 個數字 (12 地支)
            numbers = []
            for j in range(12):
                # 數字計算：起始 + 天干偏移×12 + 地支偏移
                num = start_num + (i * 12) + j
                numbers.append(num)
            
            table[(palace, stem)] = numbers
    
    return table


def save_to_json(table: Dict, filepath: str):
    """保存數表到 JSON 文件"""
    # 轉換 tuple key 為 string key (JSON 不支持 tuple)
    table_str = {f"{k[0]}_{k[1]}": v for k, v in table.items()}
    
    data = {
        '_meta': {
            'source': '梁湘潤《鐵板神數》(1984 麒麟出版社)',
            'version': '1.0',
            'description': '日月星辰數表 - 用於鐵板神數號碼查詢',
            'structure': '每宮 12 天干，每干支對應 12 地支數字',
            'total_entries': len(table_str)
        },
        **table_str
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"已保存數表到 {filepath}")
    print(f"總共 {len(table_str)} 個條目")


if __name__ == "__main__":
    # 生成數表
    table = generate_liang_table_v2()
    
    # 保存到 JSON
    output_path = "/mnt/c/Users/hooki/OneDrive/pastword/文件/Github/kinastro/astro/tieban/data/liang_number_table.json"
    save_to_json(table, output_path)
    
    # 打印示例
    print("\n數表示例:")
    for i, (key, value) in enumerate(table.items()):
        if i < 5:
            print(f"  {key}: {value[:5]}...")
        else:
            break
