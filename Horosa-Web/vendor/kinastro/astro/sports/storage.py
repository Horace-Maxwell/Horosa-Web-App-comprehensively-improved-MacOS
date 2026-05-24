"""
儲存模組 (Storage Module)

支援：
- JSON 檔案儲存/載入
- SQLite 資料庫儲存/查詢
- 歷史預測記錄
"""

import json
import sqlite3
import os
from datetime import datetime
from .models import MatchInput, PredictionResult, TeamProfile


# ============================================================
# JSON 儲存
# ============================================================

def save_prediction_json(result: PredictionResult, filepath: str = None) -> str:
    """儲存預測結果為 JSON 檔案

    Args:
        result: PredictionResult
        filepath: 可選的檔案路徑; 若未提供，自動生成

    Returns: 儲存的檔案路徑
    """
    if filepath is None:
        os.makedirs("predictions", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_home = result.home_team.replace(" ", "_")[:20]
        safe_away = result.away_team.replace(" ", "_")[:20]
        filepath = f"predictions/{ts}_{safe_home}_vs_{safe_away}.json"

    data = _prediction_to_dict(result)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath


def load_prediction_json(filepath: str) -> dict:
    """載入 JSON 預測記錄"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _prediction_to_dict(result: PredictionResult) -> dict:
    """將 PredictionResult 轉換為可序列化的字典"""
    d = {
        "home_team": result.home_team,
        "away_team": result.away_team,
        "home_win_pct": result.home_win_pct,
        "away_win_pct": result.away_win_pct,
        "draw_pct": result.draw_pct,
        "predicted_winner": result.predicted_winner,
        "confidence": result.confidence,
        "score_trend": result.score_trend,
        "frawley_summary": result.frawley_summary,
        "vedic_summary": result.vedic_summary,
        "combined_summary": result.combined_summary,
        "bet_recommendation": result.bet_recommendation,
        "timestamp": datetime.now().isoformat(),
        "frawley_evidences": [
            {"description": e.description, "favors": e.favors,
             "weight": e.weight, "category": e.category}
            for e in result.frawley_evidences
        ],
        "vedic_evidences": [
            {"description": e.description, "favors": e.favors,
             "tier": e.tier, "points": e.points, "category": e.category}
            for e in result.vedic_evidences
        ],
    }
    return d


# ============================================================
# SQLite 儲存
# ============================================================

_DB_PATH = "predictions/history.db"


def _get_db():
    """取得資料庫連線 (自動建立表格)"""
    db_dir = os.path.dirname(_DB_PATH) or "."
    os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            match_date TEXT,
            match_time TEXT,
            location TEXT,
            latitude REAL,
            longitude REAL,
            home_win_pct REAL,
            away_win_pct REAL,
            draw_pct REAL,
            predicted_winner TEXT,
            confidence TEXT,
            score_trend TEXT,
            frawley_summary TEXT,
            vedic_summary TEXT,
            bet_recommendation TEXT,
            full_json TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS team_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sport TEXT NOT NULL,
            country TEXT,
            founded_year INTEGER,
            home_stadium TEXT,
            tags_json TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_prediction_db(match: MatchInput, result: PredictionResult) -> int:
    """儲存預測結果至 SQLite

    Returns: inserted row id
    """
    conn = _get_db()
    full_json = json.dumps(_prediction_to_dict(result), ensure_ascii=False)
    cursor = conn.execute("""
        INSERT INTO predictions
        (timestamp, home_team, away_team, match_date, match_time,
         location, latitude, longitude,
         home_win_pct, away_win_pct, draw_pct,
         predicted_winner, confidence, score_trend,
         frawley_summary, vedic_summary, bet_recommendation, full_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        match.home_team, match.away_team,
        f"{match.year}-{match.month:02d}-{match.day:02d}",
        f"{match.hour:02d}:{match.minute:02d}",
        match.location_name, match.latitude, match.longitude,
        result.home_win_pct, result.away_win_pct, result.draw_pct,
        result.predicted_winner, result.confidence, result.score_trend,
        result.frawley_summary, result.vedic_summary,
        result.bet_recommendation, full_json,
    ))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def list_predictions_db(limit: int = 20) -> list:
    """列出最近的預測記錄"""
    conn = _get_db()
    rows = conn.execute("""
        SELECT id, timestamp, home_team, away_team, match_date,
               predicted_winner, confidence, home_win_pct, away_win_pct, draw_pct
        FROM predictions
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [
        {
            "id": r[0], "timestamp": r[1],
            "home_team": r[2], "away_team": r[3],
            "match_date": r[4], "predicted_winner": r[5],
            "confidence": r[6],
            "home_win_pct": r[7], "away_win_pct": r[8], "draw_pct": r[9],
        }
        for r in rows
    ]


def get_prediction_db(prediction_id: int) -> dict:
    """取得單筆預測的完整 JSON"""
    conn = _get_db()
    row = conn.execute(
        "SELECT full_json FROM predictions WHERE id = ?",
        (prediction_id,)
    ).fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return {}


def save_team_profile(profile: TeamProfile) -> int:
    """儲存或更新球隊/選手資料。"""
    conn = _get_db()
    now = datetime.now().isoformat()
    found = conn.execute(
        "SELECT id FROM team_profiles WHERE name = ? AND sport = ?",
        (profile.name, profile.sport),
    ).fetchone()
    tags_json = json.dumps(profile.tags, ensure_ascii=False)

    if found:
        row_id = int(found[0])
        conn.execute(
            """
            UPDATE team_profiles
            SET country=?, founded_year=?, home_stadium=?, tags_json=?, updated_at=?
            WHERE id=?
            """,
            (
                profile.country,
                profile.founded_year,
                profile.home_stadium,
                tags_json,
                now,
                row_id,
            ),
        )
    else:
        cursor = conn.execute(
            """
            INSERT INTO team_profiles
            (name, sport, country, founded_year, home_stadium, tags_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile.name,
                profile.sport,
                profile.country,
                profile.founded_year,
                profile.home_stadium,
                tags_json,
                now,
            ),
        )
        row_id = int(cursor.lastrowid)

    conn.commit()
    conn.close()
    return row_id


def list_team_profiles(sport: str = "", limit: int = 50) -> list[dict]:
    """列出球隊/選手資料。"""
    conn = _get_db()
    if sport:
        rows = conn.execute(
            """
            SELECT id, name, sport, country, founded_year, home_stadium, tags_json, updated_at
            FROM team_profiles
            WHERE sport = ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (sport, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT id, name, sport, country, founded_year, home_stadium, tags_json, updated_at
            FROM team_profiles
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append(
            {
                "id": r[0],
                "name": r[1],
                "sport": r[2],
                "country": r[3] or "",
                "founded_year": r[4],
                "home_stadium": r[5] or "",
                "tags": json.loads(r[6] or "[]"),
                "updated_at": r[7],
            }
        )
    return out
