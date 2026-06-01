#!/usr/bin/env python3
"""
北極神數 (Beiji Shenshu) CLI 工具
命令列起盤與條文查詢介面，使用 astro.beiji 核心模組。

使用方法：
    python beiji_shenshu_calculator.py
"""

import sys
import os

# 若從獨立目錄執行，自動加入專案根路徑
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(_here, "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from astro.beiji.calculator import (
    BeijiInput,
    BeijiShenshu,
    TiaowenDatabase,
    compute_ke,
    get_hour_branch,
    get_year_ganzhi,
)
from astro.beiji.constants import DIZHI_SHENGXIAO, KE_LABELS, PALACE_INFO


def print_result_summary(result) -> None:
    """打印起盤結果摘要。"""
    print(f"\n{'='*60}")
    print(f"  北極神數起盤結果")
    print(f"{'='*60}")
    print(f"  出生年：{result.year_stem}{result.year_branch}年（{result.year_shengxiao}）")
    print(f"  時辰：{result.hour_branch}時  刻：{result.ke_label}")
    print(f"  性別：{result.birth_input.gender}")  # noqa: S106 gender is a calculation parameter (男/女), not a credential
    print(f"{'='*60}")

    for qr in result.queries:
        palace = PALACE_INFO[qr.palace_code]
        print(f"\n【{palace['hex']} {palace['name']}宮】{qr.query_label}")
        if qr.surname:
            print(f"  姓氏：{qr.surname}")
        if qr.extra.get("siblings_desc"):
            print(f"  {qr.extra['siblings_desc']}")
        print(f"  代碼：{qr.code}")
        print(f"  條文：{qr.verse}")


def main() -> None:
    print("=" * 60)
    print("  北極神數 起盤與條文查詢工具（CLI）")
    print("  Beiji Shenshu Fortune Calculator")
    print("=" * 60)

    calc = BeijiShenshu()
    if not calc.db.loaded:
        print("警告：條文庫未能載入，查詢結果可能不完整。")

    print(f"已載入 {len(calc.db)} 條條文。")

    while True:
        print("\n選擇功能:")
        print("1. 完整起盤（輸入出生年月日時刻）")
        print("2. 直接查詢條文（輸入4位代碼）")
        print("3. 關鍵字搜尋條文")
        print("4. 系統說明")
        print("0. 退出")

        choice = input("請輸入選項：").strip()

        if choice == "1":
            try:
                year = int(input("出生年份（公曆，例如 1990）："))
                month = int(input("出生月份（1-12）："))
                day = int(input("出生日（1-31）："))
                hour = int(input("出生時（0-23，24小時制）："))
                minute = int(input("出生分（0-59，可輸入 0）：") or "0")
                gender = input("性別（男/女，預設男）：").strip() or "男"

                ke_str = input("刻（1-8，預設自動計算）：").strip()
                if ke_str.isdigit():
                    ke_val = int(ke_str)
                    ke = ke_val if 1 <= ke_val <= 8 else compute_ke(hour, minute)
                else:
                    ke = compute_ke(hour, minute)

                inp = BeijiInput(
                    year=year, month=month, day=day,
                    hour=hour, minute=minute, gender=gender, ke=ke,
                )
                result = calc.calculate_all(inp)
                print_result_summary(result)

                # 大運
                print("\n" + "=" * 60)
                print("  大運推算")
                print("=" * 60)
                dayun_list = calc.calculate_dayun(inp)
                for dy in dayun_list:
                    print(f"  第{dy['index']}運 {dy['stem_branch']}（{dy['start_age']}-{dy['end_age']}歲）"
                          f"  代碼：{dy['code']}")
                    print(f"    {dy['verse']}")

            except ValueError as exc:
                print(f"輸入無效：{exc}，請輸入正確數字。")

        elif choice == "2":
            code = input("輸入4位代碼（例如 1111）：").strip()
            if len(code) == 4 and code.isdigit():
                verse = calc.lookup(code)
                print(f"\n【{code}】條文：\n  {verse}")
            else:
                print("請輸入有效的4位數字代碼。")

        elif choice == "3":
            keyword = input("輸入搜尋關鍵字（例如：屬鼠）：").strip()
            if len(keyword) < 1:
                print("請輸入至少1個字符。")
                continue
            results = calc.search_verses(keyword)
            if results:
                print(f"\n找到 {len(results)} 條包含「{keyword}」的條文：")
                for code, verse in results[:20]:
                    print(f"  [{code}] {verse}")
                if len(results) > 20:
                    print(f"  （僅顯示前20條，共 {len(results)} 條）")
            else:
                print(f"未找到包含「{keyword}」的條文。")

        elif choice == "4":
            print("""
【北極神數簡介】
  宋代邵康節（邵雍）五大神數之一，以北斗七星（破軍星）為核心，
  結合奇門九星、六十四卦、二十八宿。特色：簡單、神奇、快而準。

【起盤邏輯】
  1. 以出生年干支確定地支（千支/年支），用於選行。
  2. 計算「拾位數」（由月、日、時辰、刻等綜合推算），用於選列。
  3. 在對應宮位表格中定位行列，得到4位條文代碼。
  4. 查詢條文庫，返回預測條文。

【宮位說明】
  乾宮（1xxx）：父母屬相壽亡、學業官貴
  兌宮（2xxx）：婚姻、口舌
  離宮（3xxx）：性格特點、文書
  震宮（4xxx）：兄弟姐妹、官運
  巽宮（5xxx）：財運、商業
  坎宮（6xxx）：婚姻、健康、牢獄
  艮宮（7xxx）：田宅、陰宅風水
  坤宮（8xxx）：子息、母親

【刻的意義】
  每時辰分8刻（每刻15分鐘），用於區分相同八字但不同命運的人。
  子初一刻 ~ 子正四刻，刻越精確，預測越準確。
""")

        elif choice == "0":
            print("感謝使用北極神數工具！再見。")
            break

        else:
            print("無效選項，請重新輸入。")


if __name__ == "__main__":
    main()