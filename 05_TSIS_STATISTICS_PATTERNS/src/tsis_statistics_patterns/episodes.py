from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .contracts import AtlasConfig


@dataclass(frozen=True)
class AtlasTables:
    sessions: pd.DataFrame
    activations: pd.DataFrame
    episodes: pd.DataFrame
    trajectories: pd.DataFrame
    events: pd.DataFrame


def _threshold_label(prefix: str, value: float) -> str:
    scaled = int(round(value)) if prefix == "relative_volume" else int(round(value * 100))
    suffix = "x" if prefix == "relative_volume" else "pct"
    return f"{prefix}_ge_{scaled}{suffix}"


def build_activation_labels(sessions: pd.DataFrame, cfg: AtlasConfig) -> pd.DataFrame:
    """Create a long activation table with vectorized threshold evaluation."""
    parts: list[pd.DataFrame] = []
    families = (
        ("gap", "gap_pct", cfg.gap_thresholds),
        ("close_advance", "close_close_pct", cfg.close_advance_thresholds),
        ("relative_volume", "relative_volume", cfg.relative_volume_thresholds),
        ("range", "range_pct", cfg.range_thresholds),
    )
    for family, value_col, thresholds in families:
        for threshold in thresholds:
            matched = sessions.loc[
                sessions["analysis_eligible"] & sessions[value_col].ge(threshold), ["ticker", "date", value_col]
            ].copy()
            if matched.empty:
                continue
            matched = matched.rename(columns={value_col: "observed_value"})
            matched["activation_family"] = family
            matched["activation_label"] = _threshold_label(family, threshold)
            matched["threshold"] = float(threshold)
            matched["knowledge_role"] = "observable"
            parts.append(matched)

    breakout_columns = [c for c in sessions.columns if c.startswith("high_breakout_")]
    for column in breakout_columns:
        prior_column = column.replace("high_breakout", "prior_high")
        matched = sessions.loc[
            sessions["analysis_eligible"] & sessions[column].fillna(False),
            ["ticker", "date", "h_split_normalized", prior_column],
        ].copy()
        if matched.empty:
            continue
        matched = matched.rename(
            columns={"h_split_normalized": "observed_value", prior_column: "threshold"}
        )
        matched["activation_family"] = "resistance_breakout"
        matched["activation_label"] = column
        matched["knowledge_role"] = "observable"
        parts.append(matched)

    columns = [
        "ticker",
        "date",
        "activation_family",
        "activation_label",
        "observed_value",
        "threshold",
        "knowledge_role",
    ]
    if not parts:
        return pd.DataFrame(columns=columns)
    return (
        pd.concat(parts, ignore_index=True)[columns]
        .sort_values(
            ["ticker", "date", "activation_family", "activation_label"],
            kind="mergesort",
        )
        .reset_index(drop=True)
    )

def _episode_id(ticker: str, date: pd.Timestamp, version: str) -> str:
    raw = f"{ticker}|{date.date().isoformat()}|{version}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


def _event_record(
    episode_id: str,
    label: str,
    row: pd.Series,
    offset: int,
    role: str,
) -> dict:
    return {
        "episode_id": episode_id,
        "event_label": label,
        "event_date": row["date"],
        "offset_session": int(offset),
        "knowledge_role": role,
    }


def build_atlas_tables(
    sessions: pd.DataFrame,
    config: AtlasConfig | None = None,
) -> AtlasTables:
    cfg = config or AtlasConfig()
    sessions = sessions.sort_values(["ticker", "date"], kind="mergesort").reset_index(drop=True)
    activations = build_activation_labels(sessions, cfg)
    activation_dates = set(zip(activations["ticker"], activations["date"]))

    episode_records: list[dict] = []
    trajectory_records: list[dict] = []
    event_records: list[dict] = []

    for ticker, group in sessions.groupby("ticker", sort=False, observed=True):
        group = group.reset_index(drop=True)
        candidate_positions = [
            idx for idx, date in enumerate(group["date"]) if (ticker, date) in activation_dates
        ]
        last_anchor = -cfg.episode_cooldown_sessions - 1
        for anchor in candidate_positions:
            if anchor - last_anchor <= cfg.episode_cooldown_sessions:
                continue
            last_anchor = anchor
            window = group.iloc[anchor : anchor + cfg.trajectory_sessions + 1].copy()
            if window.empty:
                continue
            episode_id = _episode_id(str(ticker), window.iloc[0]["date"], cfg.atlas_version)
            window["offset_session"] = np.arange(len(window), dtype=int)
            anchor_row = window.iloc[0]
            anchor_close = anchor_row["c_split_normalized"]
            anchor_high = anchor_row["h_split_normalized"]
            eligible = window["analysis_eligible"]
            eligible_close = window["c_split_normalized"].where(eligible)
            eligible_high = window["h_split_normalized"].where(eligible)
            window["close_from_anchor_pct"] = eligible_close / anchor_close - 1.0
            window["high_from_anchor_pct"] = eligible_high / anchor_high - 1.0
            window["running_episode_high"] = eligible_high.cummax()
            window["drawdown_from_running_high_pct"] = (
                eligible_close / window["running_episode_high"] - 1.0
            )
            prior_running_high = window["running_episode_high"].shift(1)
            window["is_new_episode_high"] = eligible_high.gt(prior_running_high) & eligible
            window.loc[window.index[0], "is_new_episode_high"] = True
            window["episode_id"] = episode_id
            window["knowledge_role"] = "outcome"
            trajectory_records.extend(
                window[
                    [
                        "episode_id",
                        "ticker",
                        "date",
                        "offset_session",
                        "o",
                        "h",
                        "l",
                        "c",
                        "v",
                        "o_split_normalized",
                        "h_split_normalized",
                        "l_split_normalized",
                        "c_split_normalized",
                        "close_from_anchor_pct",
                        "high_from_anchor_pct",
                        "running_episode_high",
                        "drawdown_from_running_high_pct",
                        "is_new_episode_high",
                        "analysis_eligible",
                        "quality_state",
                        "is_red_candle",
                        "is_lower_close",
                        "is_lower_high",
                        "knowledge_role",
                    ]
                ].to_dict("records")
            )

            peak_index = eligible_high.idxmax()
            peak_offset = int(window.index.get_loc(peak_index))
            peak_row = window.loc[peak_index]
            complete = len(window) == cfg.trajectory_sessions + 1
            episode_records.append(
                {
                    "episode_id": episode_id,
                    "ticker": ticker,
                    "anchor_date": anchor_row["date"],
                    "observed_sessions": int(len(window)),
                    "complete_horizon": bool(complete),
                    "right_censored": not complete,
                    "horizon_peak_date": peak_row["date"],
                    "horizon_peak_offset": peak_offset,
                    "horizon_peak_high": float(peak_row["h_split_normalized"]),
                    "anchor_close": float(anchor_close),
                    "horizon_peak_from_anchor_close_pct": float(
                        peak_row["h_split_normalized"] / anchor_close - 1.0
                    ),
                    "knowledge_role": "episode_summary",
                }
            )
            event_records.append(
                _event_record(episode_id, "horizon_peak", peak_row, peak_offset, "outcome")
            )

            event_definitions = {
                "first_red_candle": "is_red_candle",
                "first_lower_close": "is_lower_close",
                "first_lower_high": "is_lower_high",
            }
            after_d0_red = window.iloc[1:][window.iloc[1:]["analysis_eligible"] & window.iloc[1:]["is_red_candle"]]
            if not after_d0_red.empty:
                idx = after_d0_red.index[0]
                event_records.append(
                    _event_record(
                        episode_id,
                        "first_red_candle_after_d0",
                        window.loc[idx],
                        int(window.index.get_loc(idx)),
                        "outcome",
                    )
                )

            for label, column in event_definitions.items():
                matches = window.index[window[column].fillna(False)]
                if len(matches):
                    positional = int(window.index.get_loc(matches[0]))
                    event_records.append(
                        _event_record(episode_id, label, window.loc[matches[0]], positional, "outcome")
                    )

            no_new = window.iloc[1:][window.iloc[1:]["analysis_eligible"] & ~window.iloc[1:]["is_new_episode_high"]]
            if not no_new.empty:
                idx = no_new.index[0]
                positional = int(window.index.get_loc(idx))
                event_records.append(
                    _event_record(
                        episode_id,
                        "first_day_without_new_episode_high",
                        window.loc[idx],
                        positional,
                        "outcome",
                    )
                )

    episodes = pd.DataFrame.from_records(episode_records)
    trajectories = pd.DataFrame.from_records(trajectory_records)
    events = pd.DataFrame.from_records(event_records)
    return AtlasTables(sessions, activations, episodes, trajectories, events)
