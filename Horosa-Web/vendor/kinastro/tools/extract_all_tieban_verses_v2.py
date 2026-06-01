#!/usr/bin/env python3
"""
tools/extract_all_tieban_verses_v2.py — 從《鐵板神數清刻足本.txt》提取 ALL 條文

完整掃描全文（第 1 行到最後一行），提取所有有意義的命理條文
100% 內容來自原文，嚴格過濾密碼表代碼
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
    判斷是否為有意義的條文（嚴格模式）
    """
    if not text or len(text) < 4:
        return False
    
    # 移除空格
    text_clean = text.replace(' ', '').replace(' ', '')
    
    if len(text_clean) < 4:
        return False
    
    # 過濾純數字
    if re.match(r'^[一二三四五六七八九十]+$', text_clean):
        return False
    
    # 過濾純天乾地支組合（密碼表代碼）
    stem_branch_chars = set(text_clean)
    if stem_branch_chars.issubset(HEAVENLY_STEMS | EARTHLY_BRANCHES | {' ', ' ', ' ', ' ', ' '}):
        return False
    
    # 過濾純代碼字符
    code_chars = '丗世共卩曲艽囗黑芸辛癸丱咒丩哭莽仾秊誕禿地靈章平花蓋罷完亢兌離巽乾茲萃囙廿'
    if re.match(f'^[{code_chars}]+$', text_clean):
        return False
    
    # 必須包含有意義的中文詞彙或長度足夠
    meaningful_words = [
        '之年', '之悲', '之喜', '不幸', '難免', '定見', '必高列',
        '再嫁', '刑夫', '鼓盆', '斷弦', '卜商', '姻緣', '前定', '注定',
        '兄弟', '父母', '夫妻', '子女', '生子', '一胎', '父亡', '母逝',
        '妻命', '玉人', '再娶', '科考', '歲考', '功名', '高列', '前茅',
        '財運', '破財', '家業', '經營', '遷移', '遠行', '健康', '壽限',
        '災厄', '喪亡', '紅鸞', '天喜', '採芹', '入泮', '名登', '庠序',
        '良人', '閨中', '琴瑟', '鴛鴦', '斷腸', '瑤池', '考妣', '手足',
        '棠棣', '雁行', '弄璋', '弄瓦', '古稀', '六旬', '回祿', '喪明',
        '困于蒺藜', '不見其妻', '宜家貞吉', '閨門順遂', '納寵之喜',
        '斯時無所求', '終日得優游', '春色慘淡', '欄杆暗去', '中饋人亡',
        '清風為友', '明月相知', '琵琶撥出', '斷腸聲', '古稀之崇',
        '命犯白虎', '喪門相炤', '輪輻財來', '安居順利', '霏匕細雨',
        '桃面無顏', '子規啼落', '樓臺月', '一枕鴛鴦', '夢不成',
        '白虎相照', '難免刑妻', '老年失妻', '科甲兩考', '必然高列',
        '樂意悠悠', '閨中無求', '隨處可安身', '一束詩囊', '一束經',
        '鵡鳥別却', '雄鳥去', '今朝料想', '再會難', '仾是仾非',
        '閨中叶吉', '門外事如海', '吾師心若灰', '老年妻喪', '何用悲也',
        '必死其夫', '是年难免', '雌雄失恨', '凄匕', '有安危之楽',
        '门外去', '大小之爱', '父死非命', '老年丧子', '哭声不出',
        '得名斷絃', '自天祐之', '吉無不利', '琴失其音', '皆因絃斷',
        '克勤克儉', '能內助', '天上玉書召', '地下失英雄', '易數',
        '姻緣注定', '前喙注之', '強弱不一', '垂匕至三載', '難酬怙恃恩',
        '榮身之年', '災星難免', '陰功可保', '數該生子', '湖海僅至千金',
        '田土交爭', '兄弟轉成仇敵', '老年生子', '人之大幸', '人之不幸',
        '手足桔据', '爭奈不求人', '數奏幾般音', '樂奏幾般音', '秦楚干戈',
        '弓馬入泮', '喜又生兒', '數當尽貴', '二人', '三人', '四人',
        '五人', '六人', '七人', '八人', '九人', '十人',
        '兄弟', '妻妾', '子女', '財帛', '遷移', '奴僕', '官祿', '田宅',
        '父母', '命宮', '福德', '衣祿', '壽元', '基業', '行藏',
        '收成', '天災', '人禍', '祖業', '自立', '成家', '破敗', '興隆',
        '何如', '獨守', '為難', '意外', '含哺', '輕借', '運通',
        '剛斷', '任事', '流俗', '無端', '忽生', '偏房', '不結',
        '天賜', '正室', '暖日', '春回', '百花', '及時', '中流',
        '不行', '仔細', '正直', '有餘', '名登', '身赴', '儒林',
        '中天', '何期', '掩其', '光華', '小運', '稍利', '順遂',
        '大有', '富麗', '時光', '自立', '門戶', '家業', '消耗',
        '連宵', '行人', '現濘', '紗窗', '紫艷', '柳鶯', '新春',
        '家室', '亨通', '心安', '意穩', '卜君', '壽元', '未滿',
        '元用', '而有', '成事', '能剛', '而任', '決不', '頹流',
    ]
    
    for word in meaningful_words:
        if word in text:
            return True
    
    # 如果長度超過 8 字，也認為是條文
    if len(text_clean) >= 8:
        return True
    
    return False


def clean_verse_text(text):
    """
    清理條文文本
    """
    # 移除開頭的代碼字符
    code_chars = '丗世共卩曲艽囗黑芸辛癸丱咒丩哭莽仾秊誕禿地靈章平花蓋罷完亢兌離巽乾茲萃囙廿'
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
    
    # 跳過的關鍵字（更嚴格）
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
            "description": "鐵板神數條文資料庫 - 100% 來自原文（完整版，所有條文，已過濾密碼表）",
            "version": "12.0",
            "total_verses": len(verses),
            "categories": list(categories.keys()),
            "parser": "tools/extract_all_tieban_verses_v2.py",
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
    print("鐵板神數原文條文提取工具（完整版 v2 - 嚴格過濾）")
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
