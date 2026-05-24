#!/usr/bin/env python3
"""
tools/parse_tieban_text.py — 從《鐵板神數清刻足本.txt》提取條文

解析原文文件，提取所有條文並生成 verses.json
確保 100% 內容來自原文
"""

import json
import re
import os
from collections import defaultdict

def parse_tieban_text(file_path):
    """
    解析鐵板神數原文文件
    
    條文格式：
    一、丗 鼓盆之歌是年之咎
    二、丗 闺中顺遂
    三、丗 雌雄失恨凄匕
    ...
    
    或：
    一 世 得無斷弦之悲乎
    二 共 輪輻財來安居順利
    ...
    """
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    verses = {}
    verse_counter = 1
    
    # 分割為不同區塊（按【原文】標記）
    sections = re.split(r'={10,}\n.*?【原文】.*?\n={10,}', content)
    
    print(f"找到 {len(sections)} 個區塊")
    
    for section_idx, section in enumerate(sections):
        if not section.strip():
            continue
        
        # 查找條文模式
        # 模式 1: 一、丗 條文內容
        # 模式 2: 一 世 條文內容
        # 模式 3: 一 丗 條文內容
        
        lines = section.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 匹配條文行
            # 一、丗 或 一 丗 或 一 世 等
            match = re.match(r'^([一二三四五六七八九十]+)[、\s]+([丗世共卩曲艽囗黑芸辛癸艽丱咒丩哭莽仾秊誕秃地靈章平花蓋罷完坎兌離巽乾壬戊己甲乙丙丁庚]*)\s*(.*)$', line)
            
            if match:
                num_str = match.group(1)
                code = match.group(2).strip()
                text = match.group(3).strip()
                
                # 轉換中文數字為阿拉伯數字
                num_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
                          '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
                num = num_map.get(num_str, 0)
                
                if text:  # 只有有內容的條文才保存
                    # 生成條文號碼（簡化版，實際需根據密碼表）
                    verse_key = f"{verse_counter:04d}"
                    
                    verses[verse_key] = {
                        'verse': text,
                        'category': '原文條文',
                        'tags': [code] if code else [],
                        'section': section_idx,
                        'line_num': num,
                        'code': code
                    }
                    
                    verse_counter += 1
    
    return verses


def categorize_verses(verses):
    """
    根據條文內容自動分類
    
    分類規則：
    - 父母：父、母、考、妣
    - 兄弟：兄、弟、昆、仲
    - 夫妻：妻、夫、婦、婚、嫁、娶、鸞
    - 子女：子、女、兒、嗣、孕
    - 事業：科、考、名、官、祿、業
    - 財運：財、富、貧、金
    - 健康：病、疾、康、壽
    - 災厄：災、厄、刑、剋、喪、死、亡
    - 遷移：遷、移、遠、行
    - 綜合：其他
    """
    
    category_keywords = {
        '父母': ['父', '母', '考', '妣', '雙親', '椿萱'],
        '兄弟': ['兄', '弟', '昆', '仲', '叔', '伯', '手足'],
        '夫妻': ['妻', '夫', '婦', '婚', '嫁', '娶', '鸞', '弦', '鼓盆', '斷弦', '閨'],
        '子女': ['子', '女', '兒', '嗣', '孕', '妊', '弄璋', '弄瓦'],
        '事業': ['科', '考', '名', '官', '祿', '業', '功名', '登科', '庠序'],
        '財運': ['財', '富', '貧', '金', '銀', '庫'],
        '健康': ['病', '疾', '康', '壽', '醫', '藥'],
        '災厄': ['災', '厄', '刑', '剋', '喪', '死', '亡', '凶', '悲', '嘆'],
        '遷移': ['遷', '移', '遠', '行', '離', '別'],
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
                    if keyword not in tags:
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
            "description": "鐵板神數條文資料庫 - 100% 來自原文",
            "version": "4.0",
            "total_verses": len(verses),
            "categories": list(categories.keys()),
            "parser": "tools/parse_tieban_text.py",
            "category_stats": dict(categories)
        },
        **verses
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 生成 {len(verses)} 條條文")
    print(f"📁 保存到：{output_path}")
    print(f"\n📊 分類統計:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}條")
    
    return categories


def main():
    """主函數"""
    print("=" * 70)
    print("鐵板神數原文條文提取工具")
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
    
    if not verses:
        print("⚠️  未找到條文，嘗試其他解析方法...")
        # 備用解析方法
        verses = parse_alternative(input_path)
    
    # 分類
    print("正在分類...")
    verses = categorize_verses(verses)
    
    # 生成 JSON
    categories = generate_json(verses, output_path)
    
    print()
    print("=" * 70)
    print("完成！")
    print("=" * 70)


def parse_alternative(file_path):
    """
    備用解析方法：直接查找所有條文行
    """
    verses = {}
    verse_counter = 1
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 匹配更多格式
        patterns = [
            r'^([一二三四五六七八九十]+)[、\s]+([^\s]+)\s+(.+)$',
            r'^([一二三四五六七八九十]+)[、\s]+(.+)$',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    num_str, code, text = groups
                else:
                    num_str, text = groups
                    code = ''
                
                if text and len(text) > 1:  # 過濾太短的
                    verse_key = f"{verse_counter:04d}"
                    verses[verse_key] = {
                        'verse': text,
                        'category': '原文條文',
                        'tags': [code] if code else [],
                        'code': code
                    }
                    verse_counter += 1
                break
    
    return verses


if __name__ == "__main__":
    main()
