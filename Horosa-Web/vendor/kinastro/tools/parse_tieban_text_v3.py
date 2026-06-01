#!/usr/bin/env python3
"""
tools/parse_tieban_text_v3.py — 從《鐵板神數清刻足本.txt》提取條文（最終版）

解析原文文件，提取所有有意義的條文，嚴格過濾密碼表代碼
確保 100% 內容來自原文
"""

import json
import re
import os
from collections import defaultdict

# 天乾地支集合（用於檢測純代碼行）
HEAVENLY_STEMS = set('甲乙丙丁戊己庚辛壬癸')
EARTHLY_BRANCHES = set('子丑寅卯辰巳午未申酉戌亥')
GUA_NAMES = set('乾坤屯蒙需訟師比小畜履泰否同人大有謙豫隨蠱臨觀噬嗑賁剝復无妄大畜頤大過坎離咸恆遯大壯晉明夷家人睽蹇損益夬姤萃升困井革鼎震艮漸歸妹豐旅巽兌渙節中孚小過既濟未濟')


def is_meaningful_verse(text):
    """
    判斷是否為有意義的條文
    
    過濾條件：
    - 純天乾地支代碼
    - 純卦象代碼
    - 太短（少於 5 字）
    - 純數字
    - 密碼表格式
    """
    if not text or len(text) < 5:
        return False
    
    # 移除空格後檢查
    text_no_space = text.replace(' ', '').replace(' ', '')
    
    # 過濾純天乾地支組合
    stem_branch_chars = set(text_no_space)
    if stem_branch_chars.issubset(HEAVENLY_STEMS | EARTHLY_BRANCHES | {' ', ' ', ' ', ' ', ' ', ' '}):
        return False
    
    # 過濾純卦象
    if stem_branch_chars.issubset(GUA_NAMES | {' ', ' '}):
        return False
    
    # 過濾密碼表格式（如：甲己子午 乙壬丁庚）
    if re.match(r'^[甲乙丙丁][子丑寅卯][甲乙丙丁][甲乙丙丁]\s+[甲乙丙丁]', text):
        return False
    
    # 過濾純數字和符號
    if re.match(r'^[一二三四五六七八九十丗世共卩曲]+$', text_no_space):
        return False
    
    # 過濾太短的代碼行
    if len(text_no_space) < 5:
        return False
    
    return True


def clean_verse_text(text):
    """
    清理條文文本，移除多餘空格和符號
    """
    # 移除多餘空格
    text = re.sub(r'\s+', '', text)
    
    # 移除特殊符號（如：丗、世、等代碼標記）
    text = re.sub(r'^[丗世共卩曲艽囗黑芸辛癸丱咒丩哭莽仾秊誕禿地靈章平花蓋罷完]', '', text)
    
    return text.strip()


def parse_tieban_text(file_path):
    """
    解析鐵板神數原文文件
    """
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    verses = {}
    verse_counter = 1
    
    # 按行解析
    lines = content.split('\n')
    
    print(f"總行數：{len(lines)}")
    
    # 跳過的關鍵字
    skip_keywords = [
        '【原文】', '===', '鐵板神數', '心一堂', '版權', '定價', '出版',
        '書名：', '作者：', '系列：', '主編', '責任編輯', '版次：',
        '國際書號', 'ISBN', '發行者', '地址', '電話', '網址', '電郵',
        '港幣', '人民幣', '新台幣', '定價：', '平裝：', '三冊不分售'
    ]
    
    for line_idx, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        # 跳過標題和版權信息
        if any(keyword in line for keyword in skip_keywords):
            continue
        
        # 匹配條文行
        # 格式：一、丗 條文內容 或 一 世 條文內容 或 一 條文內容
        match = re.match(r'^([一二三四五六七八九十]+)[、\s]+([^\s]*)\s*(.*)$', line)
        
        if match:
            num_str = match.group(1)
            code = match.group(2).strip()
            text = match.group(3).strip()
            
            # 如果第 3 組為空，嘗試第 2 組作為內容
            if not text and code:
                if is_meaningful_verse(code):
                    text = clean_verse_text(code)
                    code = ''
            
            # 清理文本
            if text:
                text = clean_verse_text(text)
            
            # 驗證是否為有意義的條文
            if is_meaningful_verse(text):
                verse_key = f"{verse_counter:04d}"
                
                verses[verse_key] = {
                    'verse': text,
                    'category': '待分類',
                    'tags': [code] if code and len(code) <= 4 and not any(c in code for c in HEAVENLY_STEMS | EARTHLY_BRANCHES) else [],
                    'line_num': line_idx,
                    'code': code
                }
                
                verse_counter += 1
                
                if verse_counter % 1000 == 0:
                    print(f"已處理 {verse_counter} 條...")
    
    return verses


def categorize_verses(verses):
    """
    根據條文內容自動分類
    """
    
    category_keywords = {
        '父母': ['父', '母', '考', '妣', '雙親', '椿萱', '嚴', '慈', '瑤池'],
        '兄弟': ['兄', '弟', '昆', '仲', '叔', '伯', '手足', '棠棣', '雁行'],
        '夫妻': ['妻', '夫', '婦', '婚', '嫁', '娶', '鸞', '弦', '鼓盆', '斷弦', '閨', '鴛鴦', '琴瑟', '再嫁', '刑夫', '良人', '紅鸞'],
        '子女': ['子', '女', '兒', '嗣', '孕', '妊', '弄璋', '弄瓦', '採芹', '入泮', '生子'],
        '事業': ['科', '考', '名', '官', '祿', '業', '功名', '登科', '庠序', '高列', '超等', '前茅', '名登'],
        '財運': ['財', '富', '貧', '金', '銀', '庫', '家業', '經營'],
        '健康': ['病', '疾', '康', '壽', '醫', '藥', '古稀', '六旬'],
        '災厄': ['災', '厄', '刑', '剋', '喪', '死', '亡', '凶', '悲', '嘆', '卜商', '斷腸', '回祿'],
        '遷移': ['遷', '移', '遠', '行', '離', '別', '行人', '遠行'],
    }
    
    for verse_key, verse_data in verses.items():
        text = verse_data.get('verse', '')
        tags = verse_data.get('tags', [])
        
        # 根據內容分類
        assigned = False
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    verse_data['category'] = category
                    if keyword not in tags and len(keyword) >= 2:
                        tags.append(keyword)
                    assigned = True
                    break
            if assigned:
                break
        
        if not assigned:
            verse_data['category'] = '綜合'
        
        verse_data['tags'] = tags
    
    return verses


def generate_json(verses, output_path):
    """生成 JSON 文件"""
    
    # 統計
    categories = defaultdict(int)
    for verse_data in verses.values():
        categories[verse_data.get('category', '未知')] += 1
    
    output_data = {
        "_meta": {
            "source": "鐵板神數清刻足本（心一堂術數珍本古籍叢刊·星命類·神數類，2013）",
            "base_text": "虛白廬藏清中葉「貞元書屋」刻本",
            "description": "鐵板神數條文資料庫 - 100% 來自原文（已過濾密碼表代碼）",
            "version": "6.0",
            "total_verses": len(verses),
            "categories": list(categories.keys()),
            "parser": "tools/parse_tieban_text_v3.py",
            "category_stats": dict(categories)
        },
        **verses
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 生成 {len(verses)} 條條文")
    print(f"📁 保存到：{output_path}")
    print(f"📄 文件大小：{os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
    print(f"\n📊 分類統計:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}條")
    
    return categories


def main():
    """主函數"""
    print("=" * 70)
    print("鐵板神數原文條文提取工具（最終版）")
    print("=" * 70)
    print()
    
    # 文件路徑
    input_path = os.path.join(
        os.path.dirname(__file__),
        '..', '鐵板神數清刻足本.txt'
    )
    
    output_path = os.path.join(
        os.path.dirname(__file__),
        '..', 'astro', 'tieban', 'data', 'verses.json'
    )
    
    print(f"輸入文件：{input_path}")
    print(f"輸出文件：{output_path}")
    print()
    
    # 檢查文件
    if not os.path.exists(input_path):
        print(f"❌ 文件不存在：{input_path}")
        return
    
    # 解析原文
    print("正在解析原文...")
    verses = parse_tieban_text(input_path)
    
    # 分類
    print("正在分類...")
    verses = categorize_verses(verses)
    
    # 生成 JSON
    categories = generate_json(verses, output_path)
    
    # 顯示示例條文
    print("\n📜 示例條文:")
    sample_keys = list(verses.keys())[:15]
    for key in sample_keys:
        verse = verses[key]
        verse_text = verse['verse'][:60] + '...' if len(verse['verse']) > 60 else verse['verse']
        print(f"  {key}: {verse_text} [{verse['category']}]")
    
    print()
    print("=" * 70)
    print("完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
