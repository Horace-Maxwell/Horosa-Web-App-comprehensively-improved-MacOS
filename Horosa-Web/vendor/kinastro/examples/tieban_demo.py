#!/usr/bin/env python3
"""
examples/tieban_demo.py — 鐵板神數使用示例

Tie Ban Shen Shu Demo Script

展示如何使用鐵板神數模組進行完整推算
"""

import sys
import os
from datetime import datetime

# 添加專案根目錄到路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from astro.tieban import TieBanShenShu, TieBanBirthData
from astro.tieban.tieban_calculator import Ganzhi


def example_basic_usage():
    """基本使用示例"""
    print("=" * 70)
    print("鐵板神數基本使用示例")
    print("=" * 70)
    print()
    
    # 創建實例
    tbss = TieBanShenShu()
    
    # 準備出生資料
    birth_data = TieBanBirthData(
        birth_dt=datetime(1990, 5, 15, 14, 30),
        year_gz=Ganzhi('庚', '午'),
        month_gz=Ganzhi('辛', '巳'),
        day_gz=Ganzhi('戊', '辰'),
        hour_gz=Ganzhi('己', '未'),
        gender="男",
    )
    
    # 計算
    result = tbss.calculate(birth_data)
    
    # 顯示結果
    print(f"出生時間：{birth_data.birth_dt}")
    print(f"八字：{birth_data.year_gz} {birth_data.month_gz} {birth_data.day_gz} {birth_data.hour_gz}")
    print()
    print(f"命宮：{result.ming_palace}")
    print(f"身宮：{result.shen_palace}")
    print(f"五行局：{result.wuxing_ju}")
    print()
    print(f"考刻分：{result.ke}刻{result.fen}分")
    print(f"河洛數：{result.he_luo_number}")
    print()
    print(f"神數號碼：{result.tieban_number}")
    print(f"密碼：{result.secret_code}")
    print()
    print(f"條文：{result.verse}")
    print()
    
    if isinstance(result.verse_data, dict):
        print(f"分類：{result.verse_data.get('category', '未知')}")
        if result.verse_data.get('tags'):
            print(f"標籤：{' · '.join(result.verse_data['tags'])}")
    
    print()


def example_full_report():
    """完整報告示例"""
    print("=" * 70)
    print("鐵板神數完整報告示例")
    print("=" * 70)
    print()
    
    tbss = TieBanShenShu()
    
    birth_data = TieBanBirthData(
        birth_dt=datetime(1985, 8, 20, 9, 15),
        year_gz=Ganzhi('乙', '丑'),
        month_gz=Ganzhi('甲', '申'),
        day_gz=Ganzhi('壬', '寅'),
        hour_gz=Ganzhi('乙', '巳'),
        gender="女",
    )
    
    report = tbss.get_full_report(birth_data)
    print(report)


def example_verse_search():
    """條文搜索示例"""
    print("=" * 70)
    print("鐵板神數條文搜索示例")
    print("=" * 70)
    print()
    
    from astro.tieban.tieban_calculator import VerseDatabase
    
    db = VerseDatabase()
    
    # 示例 1：按號碼查詢
    print("【按號碼查詢】")
    verse = db.lookup('0001')
    print(f"0001 號：{verse.get('verse', '')}")
    print(f"分類：{verse.get('category', '未知')}")
    print(f"標籤：{verse.get('tags', [])}")
    print()
    
    # 示例 2：按標籤搜索
    print("【按標籤搜索：父母雙全】")
    results = db.search_by_tag('父母雙全')
    for result in results[:5]:  # 顯示前 5 個
        print(f"{result['number']}號：{result['verse'][:50]}...")
    print(f"共找到 {len(results)} 條")
    print()
    
    # 示例 3：獲取所有分類
    print("【所有分類】")
    categories = db.get_categories()
    for cat in categories:
        print(f"  - {cat}")
    print()


def example_different_birth_times():
    """不同出生時辰示例"""
    print("=" * 70)
    print("鐵板神數不同出生時辰對比示例")
    print("=" * 70)
    print()
    
    tbss = TieBanShenShu()
    
    # 同一日期，不同時辰
    test_cases = [
        (datetime(1990, 5, 15, 1, 30), "丑時"),
        (datetime(1990, 5, 15, 5, 30), "卯時"),
        (datetime(1990, 5, 15, 9, 30), "巳時"),
        (datetime(1990, 5, 15, 13, 30), "未時"),
        (datetime(1990, 5, 15, 17, 30), "酉時"),
        (datetime(1990, 5, 15, 21, 30), "亥時"),
    ]
    
    print(f"日期：1990 年 5 月 15 日")
    print(f"年柱：庚午 月柱：辛巳 日柱：戊辰")
    print()
    print(f"{'時辰':<8} {'命宮':<6} {'身宮':<6} {'刻分':<10} {'神數號碼':<10}")
    print("-" * 50)
    
    for birth_dt, shi_name in test_cases:
        birth_data = TieBanBirthData(
            birth_dt=birth_dt,
            year_gz=Ganzhi('庚', '午'),
            month_gz=Ganzhi('辛', '巳'),
            day_gz=Ganzhi('戊', '辰'),
            hour_gz=Ganzhi.from_index(0, birth_dt.hour // 2),  # 簡化計算
            gender="男",
        )
        
        result = tbss.calculate(birth_data)
        
        print(f"{shi_name:<8} {result.ming_palace:<6} {result.shen_palace:<6} "
              f"{result.ke}刻{result.fen}分  {result.tieban_number:<10}")
    
    print()


def example_verse_categories():
    """條文分類統計示例"""
    print("=" * 70)
    print("鐵板神數條文分類統計示例")
    print("=" * 70)
    print()
    
    from astro.tieban.tieban_calculator import VerseDatabase
    
    db = VerseDatabase()
    
    # 統計各分類條文數
    category_counts = {}
    for verse_data in db.verses.values():
        cat = verse_data.get('category', '未知')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print(f"總條文數：{len(db.verses)}")
    print(f"分類數：{len(category_counts)}")
    print()
    print(f"{'分類':<10} {'條文數':>8} {'佔比':>10}")
    print("-" * 30)
    
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(db.verses) * 100
        print(f"{cat:<10} {count:>8} {percentage:>9.1f}%")
    
    print()
    
    # 統計標籤
    all_tags = []
    for verse_data in db.verses.values():
        if 'tags' in verse_data:
            all_tags.extend(verse_data['tags'])
    
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("熱門標籤 Top 10：")
    for tag, count in top_tags:
        print(f"  {tag}: {count}次")
    
    print()


def example_svg_rendering():
    """SVG 渲染示例"""
    print("=" * 70)
    print("鐵板神數 SVG 渲染示例")
    print("=" * 70)
    print()
    
    from astro.tieban import render_tieban_chart_svg
    
    tbss = TieBanShenShu()
    
    birth_data = TieBanBirthData(
        birth_dt=datetime(1990, 5, 15, 14, 30),
        year_gz=Ganzhi('庚', '午'),
        month_gz=Ganzhi('辛', '巳'),
        day_gz=Ganzhi('戊', '辰'),
        hour_gz=Ganzhi('己', '未'),
        gender="男",
    )
    
    result = tbss.calculate(birth_data)
    
    # 渲染 SVG
    svg = render_tieban_chart_svg(result, language='zh')
    
    print(f"SVG 長度：{len(svg)} 字元")
    print(f"命宮：{result.ming_palace}, 身宮：{result.shen_palace}")
    print(f"神數號碼：{result.tieban_number}")
    print(f"條文：{result.verse[:50]}...")
    print()
    print("✅ SVG 渲染成功，可在 Streamlit 中使用 st.components.v1.html(svg, height=650) 顯示")
    print()


def example_suanpan_basic():
    """算盤打數基本使用示例（曹展碩實務版）"""
    print("=" * 70)
    print("鐵板算盤數基本使用示例（曹展碩實務版）")
    print("=" * 70)
    print()

    from astro.tieban import TieBanDiviner

    diviner = TieBanDiviner(method="suanpan")

    birth_data = TieBanBirthData(
        birth_dt=datetime(1982, 12, 15, 10, 30),
        year_gz=Ganzhi("壬", "戌"),
        month_gz=Ganzhi("甲", "子"),
        day_gz=Ganzhi("戊", "午"),
        hour_gz=Ganzhi("庚", "午"),
        gender="男",
    )

    result = diviner.calculate(birth_data)

    print(f"八字：{birth_data.year_gz} {birth_data.month_gz} {birth_data.day_gz} {birth_data.hour_gz}")
    print(f"性別：{birth_data.gender}")
    print()
    print(f"納音：{result.nayin}　→　五行部：{result.department}")
    print()
    print("【算盤打數計算步驟】")
    for step in result.calculation_steps:
        print(f"  {step}")
    print()
    print(f"條文鍵：{result.tiaowen_key}")
    if result.tiaowen:
        print(f"條文：{result.tiaowen.get('text', '')}")
        raw_key = result.tiaowen.get("raw_key", "")
        if raw_key:
            print(f"原始鍵：{raw_key}")
    else:
        print("（條文暫無資料）")
    print()


def example_suanpan_female():
    """算盤打數女命示例"""
    print("=" * 70)
    print("鐵板算盤數女命示例")
    print("=" * 70)
    print()

    from astro.tieban import TieBanDiviner

    diviner = TieBanDiviner(method="suanpan")

    birth_data = TieBanBirthData(
        birth_dt=datetime(1995, 3, 8, 8, 0),
        year_gz=Ganzhi("乙", "亥"),
        month_gz=Ganzhi("丁", "卯"),
        day_gz=Ganzhi("甲", "申"),
        hour_gz=Ganzhi("甲", "辰"),
        gender="女",
    )

    result = diviner.calculate(birth_data)

    print(f"八字：{birth_data.year_gz} {birth_data.month_gz} {birth_data.day_gz} {birth_data.hour_gz}")
    print(f"性別：{birth_data.gender}")
    print(f"納音：{result.nayin}　五行部：{result.department}")
    print(f"算盤總數：{result.total_number}　條文鍵：{result.tiaowen_key}")
    if result.tiaowen:
        print(f"條文：{result.tiaowen.get('text', '')}")
    print()


def example_suanpan_dayun():
    """算盤打數大運推算示例"""
    print("=" * 70)
    print("鐵板算盤數大運推算示例")
    print("=" * 70)
    print()

    from astro.tieban import TieBanDiviner

    diviner = TieBanDiviner(method="suanpan")

    birth_data = TieBanBirthData(
        birth_dt=datetime(1990, 5, 15, 14, 30),
        year_gz=Ganzhi("庚", "午"),
        month_gz=Ganzhi("辛", "巳"),
        day_gz=Ganzhi("戊", "辰"),
        hour_gz=Ganzhi("己", "未"),
        gender="男",
    )

    dayun_list = diviner.get_dayun(birth_data, start_age=5, steps=8)

    print(f"八字：{birth_data.year_gz} {birth_data.month_gz} {birth_data.day_gz} {birth_data.hour_gz}")
    print(f"納音：{dayun_list[0].nayin}　五行部：{dayun_list[0].department}")
    print()
    print(f"{'大運':<6} {'起運年齡':<10} {'算盤總數':<12} {'條文'}")
    print("-" * 60)
    for step_idx, d in enumerate(dayun_list, start=1):
        tiaowen_text = ""
        if d.tiaowen:
            tiaowen_text = d.tiaowen.get("text", "")[:20]
        print(f"第{step_idx}步  "
              f"{d.dayun_number or '?'} 歲      "
              f"{d.total_number:<12} {tiaowen_text}")
    print()


def example_suanpan_method_switch():
    """兩種鐵板神數版本切換示例"""
    print("=" * 70)
    print("鐵板神數兩版本切換示例（扣入法 ↔ 算盤數）")
    print("=" * 70)
    print()

    from astro.tieban import TieBanDiviner

    birth_data = TieBanBirthData(
        birth_dt=datetime(1990, 5, 15, 14, 30),
        year_gz=Ganzhi("庚", "午"),
        month_gz=Ganzhi("辛", "巳"),
        day_gz=Ganzhi("戊", "辰"),
        hour_gz=Ganzhi("己", "未"),
        gender="男",
    )

    # 扣入法
    kunji_diviner = TieBanDiviner(method="kunji")
    kunji_result = kunji_diviner.calculate(birth_data)
    print("【扣入法（kunji）版本】")
    print(f"  神數號碼：{kunji_result.tieban_number}")
    print(f"  條文：{kunji_result.verse[:40]}...")
    print()

    # 算盤數
    suanpan_diviner = kunji_diviner.switch_method("suanpan")
    suanpan_result = suanpan_diviner.calculate(birth_data)
    print("【算盤打數（suanpan）版本】")
    print(f"  納音：{suanpan_result.nayin}  五行部：{suanpan_result.department}")
    print(f"  算盤總數：{suanpan_result.total_number}")
    if suanpan_result.tiaowen:
        print(f"  條文：{suanpan_result.tiaowen.get('text', '')}")
    print()

    # 完整報告
    print("【算盤數完整報告】")
    print(suanpan_diviner.get_full_report(birth_data))


def example_suanpan_tiaowen_query():
    """算盤打數五部條文查詢示例"""
    print("=" * 70)
    print("鐵板算盤數五部條文查詢示例")
    print("=" * 70)
    print()

    from astro.tieban import SuanpanTiaowenDatabase, TieBanDiviner

    db = SuanpanTiaowenDatabase()

    # 統計各部條文
    stats = db.stats()
    print("【各部條文統計】")
    for dept, gender_stats in stats.items():
        total = sum(gender_stats.values())
        print(f"  {dept}部：{total} 條（" + "　".join(f"{k}:{v}" for k, v in gender_stats.items()) + "）")
    print()

    # 查詢特定條文
    print("【水部男命條文範例】")
    all_shui_nan = db.get_all("水", "男命")
    for key, entry in list(all_shui_nan.items())[:5]:
        print(f"  {key}：{entry.get('text', '')} （{entry.get('raw_key', '')}）")
    print()

    # 使用 TieBanDiviner 查詢
    diviner = TieBanDiviner(method="suanpan")
    tiaowen = diviner.get_tiaowen("水", gender_type="男命", number="2241")
    if tiaowen:
        print(f"【直接查詢 水部/男命/2241】：{tiaowen.get('text', '')}")
    print()


def main():
    """運行所有示例"""
    print()
    print("╔" + "═" * 69 + "╗")
    print("║" + " " * 20 + "鐵板神數模組使用示例" + " " * 24 + "║")
    print("╚" + "═" * 69 + "╝")
    print()

    examples = [
        ("基本使用（扣入法）", example_basic_usage),
        ("完整報告（扣入法）", example_full_report),
        ("條文搜索", example_verse_search),
        ("時辰對比", example_different_birth_times),
        ("分類統計", example_verse_categories),
        ("SVG 渲染", example_svg_rendering),
        ("算盤數基本使用", example_suanpan_basic),
        ("算盤數女命", example_suanpan_female),
        ("算盤數大運", example_suanpan_dayun),
        ("兩版本切換", example_suanpan_method_switch),
        ("算盤數條文查詢", example_suanpan_tiaowen_query),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"❌ {name} 示例失敗：{e}")
            import traceback
            traceback.print_exc()
            print()

    print("=" * 70)
    print("所有示例運行完成")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
