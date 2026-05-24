#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
examples/chunzi_demo.py — 蠢子數纏度完整命例示範

示範兩個真實命例的完整蠢子數查詢流程：
  命例一：丁丑 乙巳 甲子 辛未（未時三刻生）女命
  命例二：癸丑 壬戌 庚寅 丁丑 女命

執行方式：
    cd <project_root>
    python examples/chunzi_demo.py
"""

import sys
import os

# 確保能找到 astro 套件
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chunzi import ChunZiShu


def print_section(title: str) -> None:
    """輸出分節標題。"""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def example_case_one(czs: ChunZiShu) -> None:
    """
    命例一：丁丑年 乙巳月 甲子日 辛未時（未時三刻生）女命
    ────────────────────────────────────────────────────────
    已知資訊：
      - 父早逝（父逝年份可驗證）
      - 婚姻曲折，有過離異
      - 生育情況：需由詩詞交叉比對
    代碼組合：室巨9未、角陰13酉、柳計6巳、虛陽7午、女火5辰
    """
    print_section("命例一：丁丑 乙巳 甲子 辛未（未時三刻）女命")

    codes = ["室巨9未", "角陰13酉", "柳計6巳", "虛陽7午", "女火5辰"]
    results = czs.batch_lookup(codes)

    print("\n── 詩詞批量查詢 ──\n")
    for v in results:
        print(czs.interpret(v["code"]))

    print("\n── 結構化解析（關鍵資訊提取）──\n")
    for v in results:
        code = v["code"]
        info = czs.explain(code)
        if "error" in info:
            print(f"  {code}: ⚠️ {info['error']}")
            continue
        parts = []
        if info["father_zodiac"]:
            parts.append(f"父：{info['father_zodiac']}")
        if info["mother_zodiac"]:
            parts.append(f"母：{info['mother_zodiac']}")
        if info["spouse_zodiac"]:
            parts.append(f"配偶：{info['spouse_zodiac']}")
        if info["children_count"] is not None:
            parts.append(f"子息：{info['children_count']}人")
        if info["birth_hour"]:
            parts.append(f"生時：{info['birth_hour']}時")
        if info["longevity"]:
            parts.append(f"壽元：{info['longevity']}歲")
        if info["flags"]:
            parts.append(f"標記：{'、'.join(info['flags'])}")
        summary = "　".join(parts) if parts else "（詩詞未含可解析欄位）"
        print(f"  {code}: {summary}")

    print("\n── 未時生人交叉驗證 ──")
    hour_results = czs.get_verses_by_hour("未")
    print(f"  資料庫中含「未時生人」詩詞共 {len(hour_results)} 筆")
    matching = [r for r in hour_results if r["code"] in codes]
    if matching:
        print("  命例一代碼中命中：")
        for r in matching:
            print(f"    {r['code']}: {r['verse'][:50]}...")


def example_case_two(czs: ChunZiShu) -> None:
    """
    命例二：癸丑年 壬戌月 庚寅日 丁丑時 女命
    ────────────────────────────────────────────────────────
    已知資訊：
      - 已確認存在：畢龍6巳
      - 婚姻、事業待補全代碼後交叉比對
    """
    print_section("命例二：癸丑 壬戌 庚寅 丁丑 女命")

    confirmed_code = "畢龍6巳"

    print("\n── 已確認代碼查詢 ──\n")
    print(czs.interpret(confirmed_code))

    info = czs.explain(confirmed_code)
    print("── 結構化解析 ──\n")
    if "error" not in info:
        print(f"  詩詞：{info['verse']}")
        print(f"  父親屬相：{info['father_zodiac'] or '未能解析'}")
        print(f"  母親屬相：{info['mother_zodiac'] or '未能解析'}")
        print(f"  配偶屬相：{info['spouse_zodiac'] or '未能解析'}")
        print(f"  子息數　：{info['children_count'] if info['children_count'] is not None else '未能解析'}")
        print(f"  命理標記：{'、'.join(info['flags']) if info['flags'] else '（無）'}")

    print("\n── 畢宿詩詞概況 ──")
    mansion_results = czs.get_verses_by_mansion("畢")
    print(f"  畢宿（category=畢）詩詞共 {len(mansion_results)} 筆")
    print("  前 3 筆：")
    for r in mansion_results[:3]:
        print(f"    {r['code']}: {r['verse'][:55]}...")


def example_search_features(czs: ChunZiShu) -> None:
    """示範搜尋功能。"""
    print_section("搜尋功能示範")

    # 單關鍵字搜尋
    print("\n── 單關鍵字搜尋「先去父」──")
    results = czs.search("先去父", limit=5)
    print(f"  共找到 {len(czs.search('先去父', limit=9999))} 筆，顯示前 5 筆：")
    for r in results:
        print(f"  {r['code']}: {r['verse'][:55]}...")

    # 多標籤 AND 搜尋
    print("\n── 多標籤 AND 搜尋：[「先去父」AND「石皮」] ──")
    and_results = czs.search_by_tags(["先去父", "石皮"])
    print(f"  共找到 {len(and_results)} 筆")
    for r in and_results[:3]:
        print(f"  {r['code']}: {r['verse'][:55]}...")

    # 依 28 宿查詢
    print("\n── 依 28 宿查詢：室宿 ──")
    mansion = czs.get_verses_by_mansion("室")
    print(f"  室宿詩詞共 {len(mansion)} 筆，前 3 筆：")
    for r in mansion[:3]:
        print(f"  {r['code']}: {r['verse'][:55]}...")


def main() -> None:
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "蠢子數纏度命例示範" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")

    czs = ChunZiShu()

    demos = [
        ("命例一（丁丑 乙巳 甲子 辛未）", example_case_one),
        ("命例二（癸丑 壬戌 庚寅 丁丑）", example_case_two),
        ("搜尋功能示範", example_search_features),
    ]

    for name, func in demos:
        try:
            func(czs)
        except Exception as exc:
            print(f"\n❌ {name} 執行失敗：{exc}")
            import traceback
            traceback.print_exc()

    print()
    print("=" * 70)
    print("  所有示範完成")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
