"""
命令列介面 (CLI)

支援單場預測、批量預測、歷史查詢。

使用方式:
    python -m kinastro_vs.cli predict --home "Liverpool" --away "Arsenal" \\
        --date 2025-04-12 --time 15:00 --tz 0 --lat 53.4308 --lon -2.9608 \\
        --location "Anfield"

    python -m kinastro_vs.cli batch --file matches.json

    python -m kinastro_vs.cli history
"""

import argparse
import json
import sys
from .models import MatchInput
from .prediction_engine import predict_match, format_prediction_report
from .storage import (
    save_prediction_json, save_prediction_db,
    list_predictions_db,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="kinastro_vs",
        description="⚽ 足球比賽占星預測工具 (Football Match Astrology Predictor)",
        epilog="⚠️ 僅供娛樂與學習用途。投注有風險，請謹慎理財。",
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # --- predict ---
    pred = subparsers.add_parser("predict", help="預測單場比賽")
    pred.add_argument("--home", required=True, help="主場球隊名稱")
    pred.add_argument("--away", required=True, help="客場球隊名稱")
    pred.add_argument("--date", required=True,
                      help="比賽日期 (YYYY-MM-DD)")
    pred.add_argument("--time", required=True,
                      help="比賽開始時間 (HH:MM)")
    pred.add_argument("--tz", type=float, required=True,
                      help="時區 UTC 偏移 (例如: +8, -5, 0)")
    pred.add_argument("--lat", type=float, required=True,
                      help="球場緯度")
    pred.add_argument("--lon", type=float, required=True,
                      help="球場經度")
    pred.add_argument("--location", default="",
                      help="球場名稱/地點描述")
    pred.add_argument("--favorite", choices=["home", "away"],
                      default=None,
                      help="哪隊是熱門 (影響宮位分配)")
    pred.add_argument("--save-json", action="store_true",
                      help="儲存結果為 JSON")
    pred.add_argument("--save-db", action="store_true",
                      help="儲存結果至 SQLite")
    pred.add_argument("--brief", action="store_true",
                      help="只顯示簡短結果")
    pred.add_argument("--home-odds", type=float, default=None,
                      help="主勝歐賠 (例如: 1.85)")
    pred.add_argument("--draw-odds", type=float, default=None,
                      help="和局歐賠 (例如: 3.40)")
    pred.add_argument("--away-odds", type=float, default=None,
                      help="客勝歐賠 (例如: 4.50)")

    # --- batch ---
    batch = subparsers.add_parser("batch", help="批量預測多場比賽")
    batch.add_argument("--file", required=True,
                       help="JSON 檔案路徑 (含多場比賽資料)")
    batch.add_argument("--save-db", action="store_true",
                       help="儲存結果至 SQLite")

    # --- history ---
    hist = subparsers.add_parser("history", help="查看歷史預測記錄")
    hist.add_argument("--limit", type=int, default=20,
                      help="顯示筆數 (預設 20)")

    return parser.parse_args(argv)


def cmd_predict(args):
    """執行單場預測"""
    # Parse date and time
    date_parts = args.date.split("-")
    time_parts = args.time.split(":")

    match = MatchInput(
        year=int(date_parts[0]),
        month=int(date_parts[1]),
        day=int(date_parts[2]),
        hour=int(time_parts[0]),
        minute=int(time_parts[1]),
        timezone=args.tz,
        latitude=args.lat,
        longitude=args.lon,
        home_team=args.home,
        away_team=args.away,
        location_name=args.location,
        favorite=args.favorite,
        home_odds=args.home_odds,
        draw_odds=args.draw_odds,
        away_odds=args.away_odds,
    )

    result = predict_match(match)

    if args.brief:
        print(result.combined_summary)
    else:
        report = format_prediction_report(result)
        print(report)

    if args.save_json:
        path = save_prediction_json(result)
        print(f"\n💾 已儲存 JSON: {path}")

    if args.save_db:
        row_id = save_prediction_db(match, result)
        print(f"\n💾 已儲存至資料庫 (ID: {row_id})")


def cmd_batch(args):
    """批量預測"""
    with open(args.file, "r", encoding="utf-8") as f:
        matches_data = json.load(f)

    if not isinstance(matches_data, list):
        matches_data = [matches_data]

    print(f"📋 批量預測: 共 {len(matches_data)} 場比賽\n")

    for i, m in enumerate(matches_data, 1):
        date_parts = m["date"].split("-")
        time_parts = m["time"].split(":")

        match = MatchInput(
            year=int(date_parts[0]),
            month=int(date_parts[1]),
            day=int(date_parts[2]),
            hour=int(time_parts[0]),
            minute=int(time_parts[1]),
            timezone=m.get("timezone", 0),
            latitude=m["latitude"],
            longitude=m["longitude"],
            home_team=m["home_team"],
            away_team=m["away_team"],
            location_name=m.get("location", ""),
            favorite=m.get("favorite"),
            home_odds=m.get("home_odds"),
            draw_odds=m.get("draw_odds"),
            away_odds=m.get("away_odds"),
        )

        result = predict_match(match)
        print(f"{'='*60}")
        print(f"比賽 {i}/{len(matches_data)}")
        print(result.combined_summary)
        print()

        if args.save_db:
            row_id = save_prediction_db(match, result)
            print(f"  💾 已儲存至資料庫 (ID: {row_id})")
            print()


def cmd_history(args):
    """查看歷史記錄"""
    records = list_predictions_db(args.limit)

    if not records:
        print("📭 尚無歷史記錄")
        return

    print(f"📋 最近 {len(records)} 筆預測記錄:\n")
    print(f"{'ID':>4s} | {'日期':10s} | {'主隊':15s} | {'客隊':15s} | "
          f"{'預測':6s} | {'信心':6s} | {'主勝%':>5s} | {'客勝%':>5s} | {'平%':>4s}")
    print("-" * 95)

    for r in records:
        winner = {"home": "主勝", "away": "客勝", "draw": "平局"}.get(
            r["predicted_winner"], "?")
        print(f"{r['id']:4d} | {r['match_date']:10s} | "
              f"{r['home_team']:15s} | {r['away_team']:15s} | "
              f"{winner:6s} | {r['confidence']:6s} | "
              f"{r['home_win_pct']:5.1f} | {r['away_win_pct']:5.1f} | "
              f"{r['draw_pct']:4.1f}")


def main(argv=None):
    args = parse_args(argv)

    if args.command == "predict":
        cmd_predict(args)
    elif args.command == "batch":
        cmd_batch(args)
    elif args.command == "history":
        cmd_history(args)
    else:
        parse_args(["--help"])


if __name__ == "__main__":
    main()
