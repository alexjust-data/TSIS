from __future__ import annotations

import numpy as np
import pandas as pd

from .contracts import AtlasConfig, SESSION_KEY


RAW_COLUMNS = ["o", "h", "l", "c", "v"]
NORMALIZED_COLUMNS = [
    "o_split_normalized",
    "h_split_normalized",
    "l_split_normalized",
    "c_split_normalized",
]


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.where(denominator.ne(0))
    result = numerator / denominator
    return result.replace([np.inf, -np.inf], np.nan)


def _validate_input(frame: pd.DataFrame) -> None:
    required = {"ticker", "date", *RAW_COLUMNS, *NORMALIZED_COLUMNS}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if frame[list(SESSION_KEY)].duplicated().any():
        raise ValueError("Input contains duplicate ticker-date rows")


def compute_session_observables(
    frame: pd.DataFrame,
    config: AtlasConfig | None = None,
) -> pd.DataFrame:
    """Build X-like daily observables from current and strictly prior sessions.

    The function never shifts data backwards. Retrospective episode outcomes are
    built in ``episodes.py`` and are not returned here.
    """

    cfg = config or AtlasConfig()
    _validate_input(frame)
    out = frame.copy()
    for column in [*RAW_COLUMNS, *NORMALIZED_COLUMNS]:
        out[column] = pd.to_numeric(out[column], errors="raise").astype("float64")
    out["date"] = pd.to_datetime(out["date"], errors="raise").dt.normalize()
    out = out.sort_values(SESSION_KEY, kind="mergesort").reset_index(drop=True)

    positive = out[NORMALIZED_COLUMNS].gt(0).all(axis=1)
    coherent = (
        out["h_split_normalized"].ge(out[["o_split_normalized", "c_split_normalized"]].max(axis=1))
        & out["l_split_normalized"].le(out[["o_split_normalized", "c_split_normalized"]].min(axis=1))
        & out["h_split_normalized"].ge(out["l_split_normalized"])
    )
    out["analysis_eligible"] = positive & coherent & out["v"].ge(0)
    out["quality_state"] = np.where(out["analysis_eligible"], "eligible", "invalid_ohlcv")

    grouped = out.groupby("ticker", sort=False, observed=True)
    out["prev_o"] = grouped["o_split_normalized"].shift(1)
    out["prev_h"] = grouped["h_split_normalized"].shift(1)
    out["prev_l"] = grouped["l_split_normalized"].shift(1)
    out["prev_c"] = grouped["c_split_normalized"].shift(1)
    out["prev_v"] = grouped["v"].shift(1)

    out["gap_pct"] = _safe_divide(out["o_split_normalized"], out["prev_c"]) - 1.0
    out["open_close_pct"] = _safe_divide(out["c_split_normalized"], out["o_split_normalized"]) - 1.0
    out["close_close_pct"] = _safe_divide(out["c_split_normalized"], out["prev_c"]) - 1.0
    out["open_high_pct"] = _safe_divide(out["h_split_normalized"], out["o_split_normalized"]) - 1.0
    out["open_low_pct"] = _safe_divide(out["l_split_normalized"], out["o_split_normalized"]) - 1.0
    out["high_close_pct"] = _safe_divide(out["c_split_normalized"], out["h_split_normalized"]) - 1.0
    out["range_pct"] = _safe_divide(
        out["h_split_normalized"] - out["l_split_normalized"], out["prev_c"]
    )
    candle_range = out["h_split_normalized"] - out["l_split_normalized"]
    out["close_location"] = _safe_divide(
        out["c_split_normalized"] - out["l_split_normalized"], candle_range
    )
    out.loc[candle_range.eq(0), "close_location"] = np.nan

    out["is_red_candle"] = out["c_split_normalized"].lt(out["o_split_normalized"])
    out["is_green_candle"] = out["c_split_normalized"].gt(out["o_split_normalized"])
    out["is_lower_close"] = out["c_split_normalized"].lt(out["prev_c"])
    out["is_higher_close"] = out["c_split_normalized"].gt(out["prev_c"])
    out["is_lower_high"] = out["h_split_normalized"].lt(out["prev_h"])
    out["is_higher_high"] = out["h_split_normalized"].gt(out["prev_h"])
    state_columns = [
        "is_red_candle", "is_green_candle", "is_lower_close",
        "is_higher_close", "is_lower_high", "is_higher_high",
    ]
    out.loc[~out["analysis_eligible"], state_columns] = False

    prior_volume_median = grouped["v"].transform(
        lambda s: s.shift(1).rolling(cfg.relative_volume_sessions, min_periods=cfg.relative_volume_sessions).median()
    )
    out[f"volume_median_prior_{cfg.relative_volume_sessions}"] = prior_volume_median
    out["relative_volume"] = _safe_divide(out["v"], prior_volume_median)

    for name, sessions in cfg.resistance_sessions.items():
        prior_high = grouped["h_split_normalized"].transform(
            lambda s, n=sessions: s.shift(1).rolling(n, min_periods=n).max()
        )
        out[f"prior_high_{name}"] = prior_high
        out[f"high_breakout_{name}"] = out["h_split_normalized"].gt(prior_high)
        out[f"close_breakout_{name}"] = out["c_split_normalized"].gt(prior_high)
        out[f"distance_to_{name}_high_pct"] = _safe_divide(
            out["c_split_normalized"], prior_high
        ) - 1.0

    breakout_columns = [
        c for c in out.columns if c.startswith("high_breakout_") or c.startswith("close_breakout_")
    ]
    out.loc[~out["analysis_eligible"], breakout_columns] = False

    out = out.drop(columns=["future_split_factor"], errors="ignore")
    out["knowledge_role"] = "observable"
    out["price_view"] = "massive_adjusted_true_split_adjusted_v0_1"
    return out
