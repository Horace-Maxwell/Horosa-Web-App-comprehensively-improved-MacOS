import importlib.util
import sys
import types
from pathlib import Path


def _load_stock_fetcher_module():
    fake_st = types.ModuleType("streamlit")
    fake_st.cache_data = lambda *args, **kwargs: (lambda fn: fn)
    sys.modules["streamlit"] = fake_st

    file_path = (
        Path(__file__).resolve().parents[1]
        / "astro"
        / "qizheng"
        / "financial"
        / "stock_fetcher.py"
    )
    spec = importlib.util.spec_from_file_location("stock_fetcher_under_test", file_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_fetch_stock_info_uses_chart_fallback_when_info_rate_limited(monkeypatch):
    stock_fetcher = _load_stock_fetcher_module()

    class FakeTicker:
        @property
        def info(self):
            raise Exception("Too Many Requests. Rate limited.")

        @property
        def fast_info(self):
            return {}

    fake_yf = types.SimpleNamespace(Ticker=lambda _: FakeTicker())
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)
    monkeypatch.setattr(
        stock_fetcher,
        "_fetch_chart_quote_fallback",
        lambda _: (
            {
                "symbol": "AAPL",
                "quoteType": "EQUITY",
                "shortName": "Apple Inc.",
                "currentPrice": 210.5,
                "previousClose": 208.0,
                "fiftyTwoWeekHigh": 237.23,
                "fiftyTwoWeekLow": 164.08,
                "currency": "USD",
            },
            "",
        ),
    )

    stock = stock_fetcher.fetch_stock_info("AAPL")
    assert stock.error == ""
    assert stock.current_price == 210.5
    assert stock.prev_close == 208.0
    assert stock.week52_high == 237.23
    assert stock.week52_low == 164.08
    assert stock.currency == "USD"


def test_fetch_stock_info_reports_error_when_primary_and_fallback_fail(monkeypatch):
    stock_fetcher = _load_stock_fetcher_module()

    class FakeTicker:
        @property
        def info(self):
            raise Exception("Too Many Requests. Rate limited.")

        @property
        def fast_info(self):
            return {}

    fake_yf = types.SimpleNamespace(Ticker=lambda _: FakeTicker())
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)
    monkeypatch.setattr(stock_fetcher, "_fetch_chart_quote_fallback", lambda _: ({}, "fallback failed"))

    stock = stock_fetcher.fetch_stock_info("AAPL")
    assert "Cannot connect to Yahoo Finance" in stock.error
    assert "fallback also failed" in stock.error


def test_fetch_stock_info_derives_52w_range_from_history_when_missing(monkeypatch):
    stock_fetcher = _load_stock_fetcher_module()

    class FakeHistory:
        empty = False

        def __init__(self):
            self._cols = {
                "High": [101.2, 110.5, 108.3],
                "Low": [89.6, 92.1, 91.3],
                "Close": [95.0, 109.2, 100.8],
            }

        def get(self, key, default=None):
            return self._cols.get(key, default)

    class FakeTicker:
        @property
        def info(self):
            return {
                "symbol": "AAPL",
                "quoteType": "EQUITY",
                "shortName": "Apple Inc.",
                "longName": "Apple Inc.",
                "currentPrice": 100.8,
                "previousClose": 99.0,
                "currency": "USD",
                "firstTradeDateEpochUtc": 1_200_000_000,
                # fiftyTwoWeekHigh / fiftyTwoWeekLow intentionally missing
            }

        @property
        def fast_info(self):
            return {}

        def history(self, period="1y", auto_adjust=False):
            return FakeHistory()

    fake_yf = types.SimpleNamespace(Ticker=lambda _: FakeTicker())
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)

    stock = stock_fetcher.fetch_stock_info("AAPL")
    assert stock.error == ""
    assert stock.week52_high == 110.5
    assert stock.week52_low == 89.6


def test_fetch_stock_info_falls_back_to_akshare_for_a_share_zh_name(monkeypatch):
    stock_fetcher = _load_stock_fetcher_module()

    class FakeFrame:
        def __init__(self, rows):
            self._rows = rows

        def to_dict(self, orient):
            assert orient == "records"
            return self._rows

    class FakeTicker:
        @property
        def info(self):
            return {
                "symbol": "600519.SS",
                "quoteType": "EQUITY",
                "shortName": "Kweichow Moutai",
                "longName": "Kweichow Moutai Co., Ltd.",
                "currentPrice": 1000.0,
                "previousClose": 990.0,
            }

        @property
        def fast_info(self):
            return {}

        def history(self, period="1y", auto_adjust=False):
            class EmptyHistory:
                empty = True

            return EmptyHistory()

    fake_yf = types.SimpleNamespace(Ticker=lambda _: FakeTicker())
    fake_ak = types.SimpleNamespace(
        stock_info_a_code_name=lambda: FakeFrame(
            [
                {"code": "600519", "name": "貴州茅台"},
                {"code": "000001", "name": "平安銀行"},
            ]
        )
    )

    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)
    monkeypatch.setitem(sys.modules, "akshare", fake_ak)

    stock = stock_fetcher.fetch_stock_info("600519")
    assert stock.error == ""
    assert stock.name_zh == "貴州茅台"
