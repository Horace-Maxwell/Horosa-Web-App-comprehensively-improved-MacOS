"""
股票資料擷取模組 (Stock Data Fetcher)

使用 yfinance 擷取股票資訊：
- 中英文名稱
- 當前股價、漲跌幅
- 上市日期（IPO date）
- 52 週高低、近期均線
- 支援 .HK / .SS / .SZ / US stocks
"""

from __future__ import annotations

import re
import json
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st


@dataclass
class StockInfo:
    """股票基本資訊"""
    ticker: str                           # 輸入的股票代碼
    normalized_ticker: str                # 規範化後代碼（含交易所後綴）
    name_zh: str = ""                     # 中文名稱（若有）
    name_en: str = ""                     # 英文名稱
    exchange: str = ""                    # 交易所名稱
    currency: str = ""                    # 幣別
    current_price: Optional[float] = None # 當前股價
    prev_close: Optional[float] = None    # 上一收盤價
    price_change: Optional[float] = None  # 漲跌幅（%）
    week52_high: Optional[float] = None   # 52 週最高
    week52_low: Optional[float] = None    # 52 週最低
    ipo_date: Optional[date] = None       # 上市日期
    market_cap: Optional[float] = None    # 市值
    sector: str = ""                      # 行業板塊
    error: str = ""                       # 錯誤訊息（若有）
    raw_info: dict = field(default_factory=dict)  # yfinance raw info


# 常見 A 股/港股中文名稱簡短後綴映射
_EXCHANGE_SUFFIXES = {
    "hk": ".HK",
    "ss": ".SS",
    "sz": ".SZ",
    "us": "",
    "": "",
}

# 常用 A 股交易所代碼識別
_SS_SZ_PATTERN = re.compile(r"^(\d{6})(?:\.(ss|sz))?$", re.IGNORECASE)
_HK_PATTERN    = re.compile(r"^(\d{4,5})(?:\.hk)?$", re.IGNORECASE)
A_SHARE_CODE_LENGTH = 6
HK_STOCK_CODE_LENGTH = 5


def _normalize_ticker(raw: str) -> str:
    """
    將使用者輸入的股票代碼規範化，自動補全交易所後綴。

    規則：
    - 6 位數字且以 6 開頭 → 上交所 .SS
    - 6 位數字且以 0/3 開頭 → 深交所 .SZ
    - 4~5 位純數字 → 港交所 .HK（補零至 4 位）
    - 其他 → 直接回傳（美股等）
    """
    t = raw.strip().upper()
    # 已包含後綴則直接回傳
    if "." in t:
        return t
    # A 股
    if re.match(r"^\d{6}$", t):
        if t.startswith("6"):
            return f"{t}.SS"
        return f"{t}.SZ"
    # 港股（純數字 4-5 位）
    if re.match(r"^\d{4,5}$", t):
        return f"{t.zfill(4)}.HK"
    return t


def _extract_zh_name(info: dict) -> str:
    """
    嘗試從 yfinance info 中找到中文名稱。
    優先序：displayName → shortName（若含中文字元）→ longName（若含中文字元）
    """
    for key in ("displayName", "shortName", "longName"):
        val = info.get(key, "") or ""
        # 含 CJK 統一漢字則視為中文名稱
        if any("\u4e00" <= c <= "\u9fff" for c in val):
            return val
    return ""


def _contains_cjk(text: str) -> bool:
    normalized_text = text if text is not None else ""
    return any("\u4e00" <= c <= "\u9fff" for c in normalized_text)


def _iter_table_records(table) -> list[dict]:
    """將 pandas-like/list 轉為 dict records。"""
    if table is None:
        return []
    if isinstance(table, list):
        return [row for row in table if isinstance(row, dict)]
    if hasattr(table, "to_dict"):
        try:
            records = table.to_dict("records")
            if isinstance(records, list):
                return [row for row in records if isinstance(row, dict)]
        except Exception:
            pass
    return []


def _find_name_by_code(
    table,
    *,
    target_code: str,
    code_keys: tuple[str, ...],
    name_keys: tuple[str, ...],
) -> str:
    target = (target_code or "").strip().upper()
    if not target:
        return ""

    norm_len = max(len(target), 1)

    for row in _iter_table_records(table):
        code_val = ""
        for key in code_keys:
            if key in row and row.get(key) is not None:
                code_val = str(row.get(key)).strip().upper()
                break
        if not code_val:
            continue
        cmp_len = max(norm_len, len(code_val))
        if code_val.zfill(cmp_len) != target.zfill(cmp_len):
            continue

        for key in name_keys:
            name = str(row.get(key) or "").strip()
            if name and _contains_cjk(name):
                return name
    return ""


def _extract_zh_name_via_akshare(normalized_ticker: str) -> str:
    """
    用 akshare 後備抓取中文公司名（主要覆蓋 A 股/港股）。
    """
    if "." not in normalized_ticker:
        return ""
    code, suffix = normalized_ticker.split(".", 1)
    suffix = suffix.upper()
    if not code.isdigit() or suffix not in {"SS", "SZ", "HK"}:
        return ""

    try:
        import akshare as ak  # lazy import
    except Exception:
        return ""

    try:
        if suffix in {"SS", "SZ"}:
            table = ak.stock_info_a_code_name()
            return _find_name_by_code(
                table,
                target_code=code.zfill(A_SHARE_CODE_LENGTH),
                code_keys=("code", "代码"),
                name_keys=("name", "名称"),
            )
        if suffix == "HK":
            table = ak.stock_hk_spot_em()
            return _find_name_by_code(
                table,
                target_code=code.zfill(HK_STOCK_CODE_LENGTH),
                code_keys=("代码", "symbol", "code"),
                name_keys=("名称", "name"),
            )
    except Exception:
        pass
    return ""


def _is_rate_limited(msg: str) -> bool:
    text = (msg or "").lower()
    return "too many requests" in text or "429" in text or "rate limit" in text


def _to_finite_float(value) -> Optional[float]:
    """將數值安全轉為 float，非數值或 NaN 則回傳 None。"""
    if not isinstance(value, (int, float)):
        return None
    val = float(value)
    if math.isnan(val):
        return None
    return val


def _series_numeric_values(series) -> list[float]:
    """從 pandas-like 序列抽取有效數值清單。"""
    if series is None:
        return []
    try:
        raw_values = series.dropna().tolist()
    except Exception:
        try:
            raw_values = list(series)
        except Exception:
            return []

    values: list[float] = []
    for raw in raw_values:
        val = _to_finite_float(raw)
        if val is not None:
            values.append(val)
    return values


def _fetch_chart_quote_fallback(normalized_ticker: str) -> tuple[dict, str]:
    """
    後備方案：使用 Yahoo chart API 取得基礎報價資訊。
    """
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{normalized_ticker}"
        "?range=1mo&interval=1d&includePrePost=false"
    )
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        return {}, f"Yahoo chart fallback HTTP {exc.code}: {exc.reason}"
    except URLError as exc:
        return {}, f"Yahoo chart fallback network error: {exc.reason}"
    except Exception as exc:
        return {}, f"Yahoo chart fallback parse error: {exc}"

    chart = payload.get("chart") or {}
    result = chart.get("result") or []
    if not result:
        err = chart.get("error") or {}
        desc = err.get("description") or "no chart data"
        return {}, f"Yahoo chart fallback failed: {desc}"

    first = result[0] if result[0] is not None else {}
    meta = first.get("meta") or {}
    indicators = first.get("indicators") or {}
    quote_list = indicators.get("quote") or [{}]
    quote = quote_list[0] or {}
    closes = quote.get("close") or []
    last_close = next((v for v in reversed(closes) if isinstance(v, (int, float))), None)

    fallback_info = {
        "symbol": meta.get("symbol") or normalized_ticker,
        "quoteType": meta.get("instrumentType") or "EQUITY",
        "shortName": meta.get("shortName") or meta.get("symbol") or normalized_ticker,
        "longName": meta.get("longName") or meta.get("shortName") or normalized_ticker,
        "exchange": meta.get("exchangeName") or meta.get("fullExchangeName") or "",
        "currency": meta.get("currency") or "",
        "currentPrice": meta.get("regularMarketPrice") or last_close,
        "previousClose": meta.get("chartPreviousClose") or meta.get("previousClose"),
        "fiftyTwoWeekHigh": meta.get("fiftyTwoWeekHigh"),
        "fiftyTwoWeekLow": meta.get("fiftyTwoWeekLow"),
        "firstTradeDateEpochUtc": meta.get("firstTradeDate"),
        "marketCap": meta.get("marketCap"),
    }
    return fallback_info, ""


@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_info(ticker_input: str) -> StockInfo:
    """
    從 yfinance 擷取股票資訊。

    Parameters:
        ticker_input: 使用者輸入的股票代碼（支援 AAPL / 00700 / 700.HK / 600519.SS 等格式）

    Returns:
        StockInfo dataclass；若出錯則 .error 欄位有說明。

    Note:
        使用 @st.cache_data(ttl=300) 快取 5 分鐘，避免頻繁呼叫 Yahoo Finance API。
    """
    try:
        import yfinance as yf  # lazy import
    except ImportError:
        return StockInfo(
            ticker=ticker_input,
            normalized_ticker=ticker_input,
            error="yfinance 未安裝 / yfinance not installed. Run: pip install yfinance",
        )

    normalized = _normalize_ticker(ticker_input)

    tkr = None
    info: dict = {}
    primary_err = ""
    try:
        tkr = yf.Ticker(normalized)
        info = tkr.info or {}
    except Exception as exc:
        primary_err = str(exc)

    if tkr is not None:
        try:
            fast_info = dict(tkr.fast_info or {})
        except Exception:
            fast_info = {}
        if fast_info:
            info.setdefault("currentPrice", fast_info.get("lastPrice"))
            info.setdefault("previousClose", fast_info.get("previousClose"))
            info.setdefault("fiftyTwoWeekHigh", fast_info.get("fiftyTwoWeekHigh"))
            info.setdefault("fiftyTwoWeekLow", fast_info.get("fiftyTwoWeekLow"))
            info.setdefault("currency", fast_info.get("currency"))
            info.setdefault("exchange", fast_info.get("exchange"))
            info.setdefault("marketCap", fast_info.get("marketCap"))
            info.setdefault("quoteType", "EQUITY")
            info.setdefault("symbol", normalized)

    needs_fallback = (
        not info
        or (not info.get("shortName") and not info.get("longName"))
        or (
            info.get("currentPrice") is None
            and info.get("regularMarketPrice") is None
            and info.get("quoteType") is None
        )
    )
    if needs_fallback:
        fb_info, fb_err = _fetch_chart_quote_fallback(normalized)
        if fb_info:
            for key, val in fb_info.items():
                if info.get(key) in (None, "") and val not in (None, ""):
                    info[key] = val
        elif primary_err:
            primary_err = f"{primary_err}; {fb_err}" if fb_err else primary_err
        elif fb_err:
            primary_err = fb_err

    # 檢查是否取得有效資訊
    if not info or (
        info.get("trailingPegRatio") is None
        and not info.get("shortName")
        and info.get("currentPrice") is None
        and info.get("regularMarketPrice") is None
    ):
        # 有些股票只有 quoteType 但沒有詳細資訊
        if not info.get("quoteType") and not info.get("symbol"):
            if primary_err:
                msg = f"無法連接 Yahoo Finance / Cannot connect to Yahoo Finance: {primary_err}"
                if _is_rate_limited(primary_err):
                    msg += "（已嘗試後備方案仍失敗 / fallback also failed）"
                return StockInfo(
                    ticker=ticker_input,
                    normalized_ticker=normalized,
                    error=msg,
                )
            return StockInfo(
                ticker=ticker_input,
                normalized_ticker=normalized,
                error=(
                    f"找不到股票代碼 '{normalized}' 的資訊。"
                    f"請確認代碼格式（如 700.HK / AAPL / 600519.SS）。"
                    f" / Cannot find stock '{normalized}'. "
                    f"Please check the ticker format (e.g. 700.HK / AAPL / 600519.SS)."
                ),
            )

    # ── 名稱 ─────────────────────────────────────────────
    name_zh = _extract_zh_name(info)
    if not name_zh:
        name_zh = _extract_zh_name_via_akshare(normalized)
    name_en = info.get("longName") or info.get("shortName") or normalized

    # ── 股價 ─────────────────────────────────────────────
    current_price = (
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("navPrice")
    )
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
    price_change: Optional[float] = None
    if current_price and prev_close and prev_close != 0:
        price_change = (current_price - prev_close) / prev_close * 100.0

    week52_high = info.get("fiftyTwoWeekHigh")
    week52_low  = info.get("fiftyTwoWeekLow")
    if tkr is not None and (week52_high is None or week52_low is None):
        try:
            hist_1y = tkr.history(period="1y", auto_adjust=False)
        except Exception:
            hist_1y = None

        if hist_1y is not None and not getattr(hist_1y, "empty", True):
            highs = _series_numeric_values(hist_1y.get("High"))
            lows = _series_numeric_values(hist_1y.get("Low"))
            closes = _series_numeric_values(hist_1y.get("Close"))

            if week52_high is None:
                base_highs = highs or closes
                if base_highs:
                    week52_high = max(base_highs)
            if week52_low is None:
                base_lows = lows or closes
                if base_lows:
                    week52_low = min(base_lows)

    # ── 上市日期 ─────────────────────────────────────────
    ipo_date: Optional[date] = None
    # yfinance 提供 ipoExpectedDate（即將上市）或 firstTradeDateEpochUtc
    raw_ipo = info.get("ipoExpectedDate")
    if raw_ipo:
        try:
            ipo_date = datetime.strptime(raw_ipo, "%Y-%m-%d").date()
        except Exception:
            pass

    if ipo_date is None:
        first_epoch = info.get("firstTradeDateEpochUtc")
        if first_epoch:
            try:
                ipo_date = datetime.fromtimestamp(first_epoch, tz=timezone.utc).date()
            except Exception:
                pass

    return StockInfo(
        ticker=ticker_input,
        normalized_ticker=normalized,
        name_zh=name_zh,
        name_en=name_en,
        exchange=info.get("exchange", "") or info.get("fullExchangeName", ""),
        currency=info.get("currency", ""),
        current_price=current_price,
        prev_close=prev_close,
        price_change=price_change,
        week52_high=week52_high,
        week52_low=week52_low,
        ipo_date=ipo_date,
        market_cap=info.get("marketCap"),
        sector=info.get("sector") or info.get("industry") or "",
        raw_info=info,
    )


def get_display_name(stock: StockInfo) -> str:
    """回傳優先使用中文的顯示名稱"""
    if stock.name_zh:
        return f"{stock.name_zh} ({stock.name_en})" if stock.name_en else stock.name_zh
    return stock.name_en or stock.normalized_ticker


def get_price_ratio(stock: StockInfo) -> Optional[float]:
    """
    計算當前股價在 52 週高低範圍中的百分比位置（0~100%）。
    類似命宮強弱度：0-20% 弱宮，80-100% 旺相。

    Returns None if data is insufficient.
    """
    if (
        stock.current_price is not None
        and stock.week52_high is not None
        and stock.week52_low is not None
        and stock.week52_high != stock.week52_low
    ):
        ratio = (stock.current_price - stock.week52_low) / (stock.week52_high - stock.week52_low)
        return max(0.0, min(1.0, ratio)) * 100.0
    return None


def get_strength_label(ratio: Optional[float]) -> tuple[str, str, str]:
    """
    根據股價比例返回七政四餘強弱判斷標籤。

    Returns:
        (label_zh, label_en, color_hex)
    """
    if ratio is None:
        return "資料不足", "Insufficient Data", "#9090b8"
    if ratio >= 80:
        return "旺相（強勢）", "Wang Xiang — Strong", "#FFD700"
    if ratio >= 60:
        return "得令（偏強）", "De Ling — Above Average", "#86efac"
    if ratio >= 40:
        return "中和（平穩）", "Zhong He — Neutral", "#60a5fa"
    if ratio >= 20:
        return "失令（偏弱）", "Shi Ling — Below Average", "#fb923c"
    return "休囚（弱宮）", "Xiu Qiu — Weak", "#f87171"
