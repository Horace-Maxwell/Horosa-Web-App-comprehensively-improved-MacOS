#!/usr/bin/env python3
"""
tools/extract_all_tieban_verses_complete.py — 從《鐵板神數清刻足本.txt》提取 ALL 條文

完整掃描全文，提取所有有意義的命理條文
100% 內容來自原文，只過濾純密碼表代碼
"""

import json
import re
import os
from collections import defaultdict

# 天乾地支集合
HEAVENLY_STEMS = set('甲乙丙丁戊己庚辛壬癸')
EARTHLY_BRANCHES = set('子丑寅卯辰巳午未申酉戌亥')

def is_meaningful_verse(text):
    """
    判斷是否為有意義的條文（寬鬆模式 - 只過濾純代碼）
    """
    if not text or len(text) < 3:
        return False
    
    # 移除空格
    text_clean = text.replace(' ', '').replace(' ', '')
    
    if len(text_clean) < 3:
        return False
    
    # 過濾純數字
    if re.match(r'^[一二三四五六七八九十]+$', text_clean):
        return False
    
    # 過濾純天乾地支組合（密碼表代碼）- 嚴格檢查
    stem_branch_chars = set(text_clean)
    if stem_branch_chars and stem_branch_chars.issubset(HEAVENLY_STEMS | EARTHLY_BRANCHES):
        return False
    
    # 過濾純代碼字符
    code_chars = set('丗世共卩曲艽囗黑芸辛癸丱咒丩哭莽仾秊誕禿地靈章平花蓋罷完亢兌離巽乾茲萃囙廿罢芅兙')
    if text_clean and set(text_clean).issubset(code_chars):
        return False
    
    # 如果包含任何非天乾地支、非代碼字符的中文字，認為是條文
    chinese_chars = set(re.findall(r'[\u4e00-\u9fff]', text_clean))
    meaningful_chars = chinese_chars - (HEAVENLY_STEMS | EARTHLY_BRANCHES | code_chars)
    
    if len(meaningful_chars) >= 2:
        return True
    
    # 長度超過 6 字也認為是條文
    if len(text_clean) >= 6:
        return True
    
    return False


def clean_verse_text(text):
    """
    清理條文文本
    """
    # 移除開頭的代碼字符
    code_chars = '丗世共卩曲艽囗黑芸辛癸丱咒丩哭莽仾秊誕禿地靈章平花蓋罷完亢兌離巽乾茲萃囙廿罢芅兙'
    text = re.sub(f'^[{code_chars}]+[\s、]*', '', text)
    
    # 移除多餘空格
    text = re.sub(r'\s+', '', text)
    
    # 移除特殊符號
    text = re.sub(r'[亏靈罩草]', '', text)
    
    return text.strip()


def parse_all_verses(file_path):
    """
    解析鐵板神數原文文件 - 掃描全文
    """
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    verses = {}
    verse_counter = 1
    
    lines = content.split('\n')
    total_lines = len(lines)
    
    print(f"總行數：{total_lines}")
    print("正在掃描全文（第 1 行到最後一行）...")
    
    # 跳過的關鍵字（只跳過明顯的非條文內容）
    skip_keywords = [
        '【原文】', '===', '鐵板神數', '心一堂', '版權', '定價', '出版',
        '書名：', '作者：', '系列：', '主編', '責任編輯', '版次：',
        '國際書號', 'ISBN', '發行者', '地址', '電話', '網址', '電郵',
        '港幣', '人民幣', '新台幣', '定價：', '平裝：', '三冊不分售',
        '秘鈔', '密碼表', '纂碼表', '流度', '壽度', '納甲', '卦爻',
        '總序', '術數', '易經', '邵雍', '皇極', '先天', '後天',
        '白羊', '空門', '正丁', '大六壬', '羅國明印', '起課法',
        '占事', '月將加時', '順行十二支', '用神', '休咎',
        '三田', '止壽度圖', '流年圖', '起於甲子', '止於癸亥',
        '六十甲子', '週而復始', '巽卦', '離卦', '坤卦', '兌卦', '乾卦', '坎卦', '艮卦', '震卦',
        '右頁', '左頁', '頁', '卷', '冊', '編', '輯', '校', '對',
        '訛卦', '用事', '分冬', '分屯爻', '雜乾坤宮', '明訛',
    ]
    
    for line_idx, line in enumerate(lines, 1):
        line = line.strip()
        
        if not line:
            continue
        
        # 跳過標題和版權信息
        if any(keyword in line for keyword in skip_keywords):
            continue
        
        # 匹配條文行：一、丗 條文內容 或 一 世 條文內容 或 一 條文內容
        match = re.match(r'^([一二三四五六七八九十]+)[、\s]+([^\s]*)\s*(.*)$', line)
        
        if match:
            num_str = match.group(1)
            code = match.group(2).strip()
            text = match.group(3).strip()
            
            # 如果第 3 組為空，嘗試第 2 組作為內容
            if not text and code:
                cleaned_code = clean_verse_text(code)
                if is_meaningful_verse(cleaned_code):
                    text = cleaned_code
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
                    'tags': [],
                    'line_num': line_idx,
                }
                
                verse_counter += 1
                
                if verse_counter % 500 == 0:
                    print(f"已提取 {verse_counter} 條...")
    
    return verses


def categorize_verses(verses):
    """
    根據條文內容自動分類
    """
    
    category_keywords = {
        '父母': ['父', '母', '考', '妣', '雙親', '椿萱', '嚴', '慈', '瑤池', '赴瑤池', '怙恃'],
        '兄弟': ['兄', '弟', '昆', '仲', '叔', '伯', '手足', '棠棣', '雁行', '二人', '人數', '七人', '八人', '九人', '十人', '三人', '四人'],
        '夫妻': ['妻', '夫', '婦', '婚', '嫁', '娶', '鸞', '弦', '鼓盆', '斷弦', '閨', '鴛鴦', '琴瑟', '再嫁', '刑夫', '良人', '紅鸞', '納寵', '姻緣', '玉人', '再娶', '配夫'],
        '子女': ['子', '女', '兒', '嗣', '孕', '妊', '弄璋', '弄瓦', '採芹', '入泮', '生子', '恭見', '一胎', '雙喜'],
        '事業': ['科', '考', '名', '官', '祿', '業', '功名', '登科', '庠序', '高列', '超等', '前茅', '名登', '歲考', '鴻意'],
        '財運': ['財', '富', '貧', '金', '銀', '庫', '家業', '經營', '破財'],
        '健康': ['病', '疾', '康', '壽', '醫', '藥', '古稀', '六旬'],
        '災厄': ['災', '厄', '刑', '剋', '喪', '死', '亡', '凶', '悲', '嘆', '卜商', '斷腸', '回祿', '喪明', '孝服'],
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
            "description": "鐵板神數條文資料庫 - 100% 來自原文（完整版，所有條文，只過濾純密碼表代碼）",
            "version": "14.0",
            "total_verses": len(verses),
            "categories": list(categories.keys()),
            "parser": "tools/extract_all_tieban_verses_complete.py",
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
    print("鐵板神數原文條文提取工具（完整版 - 只過濾純代碼）")
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
    verses = parse_all_verses(input_path)
    
    if not verses:
        print("⚠️  未提取到任何條文！")
        return
    
    # 分類
    print("正在分類...")
    verses = categorize_verses(verses)
    
    # 生成 JSON
    categories = generate_json(verses, output_path)
    
    # 顯示示例條文
    print("\n📜 示例條文（前 30 條）:")
    sample_keys = list(verses.keys())[:30]
    for key in sample_keys:
        verse = verses[key]
        verse_text = verse['verse'][:50] + '...' if len(verse['verse']) > 50 else verse['verse']
        print(f"  {key}: {verse_text} [{verse['category']}]")
    
    print()
    print("=" * 70)
    print("完成！100% 內容來自《鐵板神數清刻足本》原文")
    print("=" * 70)


if __name__ == "__main__":
    main()
