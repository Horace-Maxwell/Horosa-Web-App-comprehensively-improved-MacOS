"""金融占星特徵回測 MVP。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

import numpy as np
import pandas as pd

MIN_SAMPLE_SIZE_FOR_CORR = 3


@dataclass
class BacktestSummary:
    sample_size: int
    ic: float
    rank_ic: float
    hit_rate: float
    long_short_spread: float


def _safe_corr(a: pd.Series, b: pd.Series, method: str = "pearson") -> float:
    if len(a) < MIN_SAMPLE_SIZE_FOR_CORR or len(b) < MIN_SAMPLE_SIZE_FOR_CORR:
        return 0.0
    try:
        corr = a.corr(b, method=method)
        return float(corr) if pd.notna(corr) else 0.0
    except Exception:
        return 0.0


def _build_forward_returns(price_df: pd.DataFrame, horizons: tuple[int, ...]) -> pd.DataFrame:
    close = price_df["Close"].astype(float)
    out = price_df.copy()
    for h in horizons:
        out[f"fwd_ret_{h}d"] = close.shift(-h) / close - 1.0
    return out


def build_feature_frame(
    price_df: pd.DataFrame,
    feature_fn: Callable[[datetime], dict],
    *,
    min_step: int = 5,
) -> pd.DataFrame:
    """根據日期序列建立 astro feature dataframe。"""
    if price_df.empty:
        return pd.DataFrame()

    rows: list[dict] = []
    indexed = price_df.copy()
    indexed = indexed.sort_index()
    for ts in indexed.index[::min_step]:
        when = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
        features = feature_fn(when)
        if not isinstance(features, dict):
            continue
        row = {"date": ts, **features}
        rows.append(row)

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).set_index("date").sort_index()


def evaluate_feature_vs_returns(
    merged_df: pd.DataFrame,
    *,
    feature_col: str,
    return_col: str,
) -> BacktestSummary:
    """評估單一特徵對 forward return 的預測能力。"""
    df = merged_df[[feature_col, return_col]].dropna().copy()
    if df.empty:
        return BacktestSummary(0, 0.0, 0.0, 0.0, 0.0)

    ic = _safe_corr(df[feature_col], df[return_col], method="pearson")
    rank_ic = _safe_corr(df[feature_col], df[return_col], method="spearman")

    signal = np.sign(df[feature_col])
    realized = np.sign(df[return_col])
    hit_rate = float((signal == realized).mean())

    q80 = df[feature_col].quantile(0.8)
    q20 = df[feature_col].quantile(0.2)
    long_ret = df.loc[df[feature_col] >= q80, return_col].mean()
    short_ret = df.loc[df[feature_col] <= q20, return_col].mean()
    spread = float((long_ret - short_ret) if pd.notna(long_ret) and pd.notna(short_ret) else 0.0)

    return BacktestSummary(
        sample_size=int(len(df)),
        ic=float(ic),
        rank_ic=float(rank_ic),
        hit_rate=hit_rate,
        long_short_spread=spread,
    )


def run_backtest_mvp(
    price_df: pd.DataFrame,
    feature_fn: Callable[[datetime], dict],
    *,
    horizons: tuple[int, ...] = (5, 10, 20),
    feature_col: str = "astro_score",
) -> dict:
    """執行最小可用回測流程。"""
    if price_df.empty or "Close" not in price_df.columns:
        return {"features": pd.DataFrame(), "returns": pd.DataFrame(), "metrics": []}

    price_with_ret = _build_forward_returns(price_df, horizons)
    feature_df = build_feature_frame(price_with_ret, feature_fn)
    if feature_df.empty:
        return {"features": feature_df, "returns": price_with_ret, "metrics": []}

    merged = feature_df.join(price_with_ret, how="left")

    metrics: list[dict] = []
    for h in horizons:
        col = f"fwd_ret_{h}d"
        summary = evaluate_feature_vs_returns(merged, feature_col=feature_col, return_col=col)
        metrics.append(
            {
                "horizon_days": h,
                "sample_size": summary.sample_size,
                "ic": round(summary.ic, 4),
                "rank_ic": round(summary.rank_ic, 4),
                "hit_rate": round(summary.hit_rate, 4),
                "long_short_spread": round(summary.long_short_spread, 4),
            }
        )

    return {
        "features": feature_df,
        "returns": price_with_ret,
        "merged": merged,
        "metrics": metrics,
    }
