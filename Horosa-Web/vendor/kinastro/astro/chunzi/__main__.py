# -*- coding: utf-8 -*-
"""
astro/chunzi/__main__.py — 蠢子數命令列介面

支援直接執行：
    python -m astro.chunzi lookup 室巨9未
    python -m astro.chunzi search "未時生人" --limit 10
    python -m astro.chunzi batch 室巨9未,角陰13酉,柳計6巳
    python -m astro.chunzi mansion 室
    python -m astro.chunzi tags "未時生人" "先去父"
    python -m astro.chunzi explain 室巨9未
    python -m astro.chunzi cast 坤 丁丑 乙巳 甲子 辛未 --ke 3
    python -m astro.chunzi cast 坤 癸丑 壬戌 庚寅 丁丑 --ke 6 --lunar-month 5 --lunar-day 9
"""

import argparse
import json
import sys

from .chunzi import ChunZiShu


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m astro.chunzi",
        description="蠢子數纏度查詢工具",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # lookup：依代碼查詢
    p_lookup = sub.add_parser("lookup", help="依代碼查單條詩詞")
    p_lookup.add_argument("code", help="詩詞代碼，例如：室巨9未")
    p_lookup.add_argument(
        "--json", action="store_true", dest="as_json", help="以 JSON 格式輸出"
    )

    # search：關鍵字搜尋
    p_search = sub.add_parser("search", help="關鍵字搜尋詩詞")
    p_search.add_argument("keyword", help="搜尋關鍵字，例如：未時生人")
    p_search.add_argument(
        "--limit", type=int, default=10, help="最多顯示筆數（預設 10）"
    )
    p_search.add_argument(
        "--json", action="store_true", dest="as_json", help="以 JSON 格式輸出"
    )

    # batch：批量查詢
    p_batch = sub.add_parser("batch", help="批量查詢多個代碼（逗號分隔）")
    p_batch.add_argument("codes", help="代碼列表，例如：室巨9未,角陰13酉")
    p_batch.add_argument(
        "--json", action="store_true", dest="as_json", help="以 JSON 格式輸出"
    )

    # mansion：依 28 宿查詢
    p_mansion = sub.add_parser("mansion", help="依 28 宿查詢詩詞")
    p_mansion.add_argument("name", help="28 宿名稱，例如：室")
    p_mansion.add_argument(
        "--limit", type=int, default=20, help="最多顯示筆數（預設 20）"
    )
    p_mansion.add_argument(
        "--json", action="store_true", dest="as_json", help="以 JSON 格式輸出"
    )

    # tags：多標籤 AND 搜尋
    p_tags = sub.add_parser("tags", help="多關鍵字 AND 搜尋（所有標籤都須出現）")
    p_tags.add_argument("tags", nargs="+", help="關鍵字列表（空格分隔）")
    p_tags.add_argument(
        "--limit", type=int, default=20, help="最多顯示筆數（預設 20）"
    )
    p_tags.add_argument(
        "--json", action="store_true", dest="as_json", help="以 JSON 格式輸出"
    )

    # explain：結構化解析
    p_explain = sub.add_parser("explain", help="結構化解析詩詞（父母屬相、妻宮、子息等）")
    p_explain.add_argument("code", help="詩詞代碼，例如：室巨9未")

    # cast：半自動起盤
    p_cast = sub.add_parser(
        "cast",
        help="半自動起盤（性別 + 八字 → 自動找條文）",
        description=(
            "根據性別與四柱八字自動搜尋候選詩詞，輸出命例總覽。\n"
            "範例：python -m astro.chunzi cast 坤 丁丑 乙巳 甲子 辛未 --ke 3"
        ),
    )
    p_cast.add_argument("gender", help="性別：乾（男）或坤（女）")
    p_cast.add_argument("year", help="年柱，例如：丁丑")
    p_cast.add_argument("month", help="月柱，例如：乙巳")
    p_cast.add_argument("day", help="日柱，例如：甲子")
    p_cast.add_argument("hour", help="時柱，例如：辛未")
    p_cast.add_argument("--ke", type=int, default=None, help="出生刻數（整數 1–10，可選）")
    p_cast.add_argument(
        "--lunar-month", type=int, default=None, dest="lunar_month",
        help="農曆出生月份（整數 1–12，可選；啟用 Phase 2 月日搜尋）",
    )
    p_cast.add_argument(
        "--lunar-day", type=int, default=None, dest="lunar_day",
        help="農曆出生日（整數 1–30，可選；需與 --lunar-month 同時使用）",
    )
    p_cast.add_argument(
        "--json", action="store_true", dest="as_json", help="以 JSON 格式輸出"
    )
    p_cast.add_argument(
        "--limit", type=int, default=None,
        help="顯示的最大條文數（預設不限）",
    )

    return parser


def main() -> None:
    parser = _make_parser()
    args = parser.parse_args()
    czs = ChunZiShu()

    if args.command == "lookup":
        result = czs.get_verse(args.code)
        if result is None:
            print(f"⚠️  找不到代碼：「{args.code}」", file=sys.stderr)
            sys.exit(1)
        if args.as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(czs.interpret(args.code))

    elif args.command == "search":
        results = czs.search(args.keyword, limit=args.limit)
        if args.as_json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"搜尋「{args.keyword}」共 {len(results)} 筆：\n")
            for r in results:
                print(f"  {r['code']}: {r['verse'][:60]}...")

    elif args.command == "batch":
        raw_codes = args.codes.split(",")
        codes = [c.strip() for c in raw_codes if c.strip()]
        skipped = [c for c in raw_codes if not c.strip()]
        if skipped:
            print(f"⚠️  已略過 {len(skipped)} 個空白代碼項目", file=sys.stderr)
        if not codes:
            print("⚠️  未提供任何有效代碼", file=sys.stderr)
            sys.exit(1)
        results = czs.batch_lookup(codes)
        if args.as_json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            for v in results:
                print(czs.interpret(v["code"]))

    elif args.command == "mansion":
        results = czs.get_verses_by_mansion(args.name)
        display = results[: args.limit]
        if args.as_json:
            print(json.dumps(display, ensure_ascii=False, indent=2))
        else:
            print(f"{args.name}宿詩詞共 {len(results)} 筆（顯示前 {len(display)} 筆）：\n")
            for r in display:
                print(f"  {r['code']}: {r['verse'][:60]}...")

    elif args.command == "tags":
        results = czs.search_by_tags(args.tags, limit=args.limit)
        if args.as_json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            tag_str = "」+「".join(args.tags)
            print(f"同時含「{tag_str}」共 {len(results)} 筆：\n")
            for r in results:
                print(f"  {r['code']}: {r['verse'][:60]}...")

    elif args.command == "explain":
        info = czs.explain(args.code)
        if "error" in info:
            print(f"⚠️  {info['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"\n【{info['code']}】結構化解析\n")
        print(f"詩詞：{info['verse']}\n")
        print(f"父親屬相：{info['father_zodiac'] or '未能解析'}")
        print(f"母親屬相：{info['mother_zodiac'] or '未能解析'}")
        print(f"配偶屬相：{info['spouse_zodiac'] or '未能解析'}")
        print(f"子息數　：{info['children_count'] if info['children_count'] is not None else '未能解析'}")
        print(f"出生時辰：{info['birth_hour'] or '未能解析'}")
        print(f"出生刻數：{info['birth_ke'] if info['birth_ke'] is not None else '未能解析'}")
        print(f"壽元　　：{str(info['longevity']) + '歲' if info['longevity'] else '未能解析'}")
        if info["flags"]:
            print(f"命理標記：{'、'.join(info['flags'])}")
        else:
            print("命理標記：（無特殊標記）")

    elif args.command == "cast":
        import warnings
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                chart = czs.cast_chart(
                    gender=args.gender,
                    year=args.year,
                    month=args.month,
                    day=args.day,
                    hour=args.hour,
                    ke=args.ke,
                    lunar_month=args.lunar_month,
                    lunar_day=args.lunar_day,
                )
            except ValueError as exc:
                print(f"⚠️  {exc}", file=sys.stderr)
                sys.exit(1)
        for w in caught:
            print(f"⚠️  {w.message}", file=sys.stderr)

        if not chart.codes:
            print("⚠️  未找到任何候選條文，請手動補充代碼。", file=sys.stderr)
            sys.exit(1)

        # 可選：限制顯示數量（不截斷 codes，只影響 verses 列印）
        display_codes = chart.codes[: args.limit] if args.limit else chart.codes
        if args.as_json:
            data = chart.to_dict()
            if args.limit:
                data["codes"] = display_codes
                analysis = data.get("analysis") or {}
                analysis["verses"] = analysis.get("verses", [])[: args.limit]
                data["analysis"] = analysis
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            if args.limit and len(chart.codes) > args.limit:
                print(
                    f"共找到 {len(chart.codes)} 條條文，顯示前 {args.limit} 條：",
                    file=sys.stderr,
                )
            chart.print_summary()


if __name__ == "__main__":
    main()
