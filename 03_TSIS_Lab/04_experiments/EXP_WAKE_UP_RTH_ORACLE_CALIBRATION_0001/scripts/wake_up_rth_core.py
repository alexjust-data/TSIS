#!/usr/bin/env python3
"""Shared, representation-neutral machinery for Wake-up RTH oracle calibration.

This module deliberately does not import Binding A or Binding B outputs.  It
uses the governed TA-3 target manifest, the legacy trade tape and the exact
Trading Activity trade-condition policy only.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


UTC = timezone.utc
DEVELOPMENT_END = pd.Timestamp("2022-12-30")
PROHIBITED_VALIDATION_START = pd.Timestamp("2023-01-01")


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def sha256_file(path: Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    return config


def as_path(value: str) -> Path:
    return Path(value.replace("/", os.sep))


def verify_file(path: Path, expected_sha256: str | None, label: str) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"{label} missing: {path}")
    actual = sha256_file(path)
    if expected_sha256 and actual.lower() != expected_sha256.lower():
        raise ValueError(
            f"{label} SHA-256 mismatch: expected={expected_sha256} actual={actual}"
        )
    return actual


def load_policy_module(script_path: Path):
    spec = importlib.util.spec_from_file_location("tsis_trade_eligibility", script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import policy helper: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class SessionContext:
    target_ordinal: int
    block_id: str
    cohort_id: str
    instrument_id: str
    ticker: str
    session_date: str
    open_utc: pd.Timestamp
    close_utc: pd.Timestamp
    expected_decision_seconds: int
    manifest_declared_decision_seconds: int
    presession_reference_price: float
    presession_reference_market_cap_proxy: float

    @property
    def target_file_key(self) -> str:
        digest = hashlib.sha256(
            f"{self.block_id}|{self.target_ordinal}|{self.instrument_id}|{self.session_date}".encode(
                "utf-8"
            )
        ).hexdigest()[:20]
        return f"target_{digest}"


def raw_trade_path(root: Path, ticker: str, session_date: str) -> Path:
    date_value = pd.Timestamp(session_date)
    return (
        root
        / ticker
        / f"year={date_value.year:04d}"
        / f"month={date_value.month:02d}"
        / f"day={session_date}"
        / "market.parquet"
    )


def load_targets_and_calendar(config: dict[str, Any]) -> list[SessionContext]:
    data = config["sources"]
    target_path = as_path(data["target_contexts"])
    calendar_path = as_path(data["market_calendar"])
    verify_file(target_path, data.get("target_contexts_sha256"), "target manifest")
    verify_file(calendar_path, data.get("market_calendar_sha256"), "calendar")

    targets = pd.read_parquet(target_path)
    required = {
        "target_ordinal",
        "block_id",
        "cohort_id",
        "instrument_id",
        "ticker_as_of_session",
        "session_date",
        "decision_seconds",
    }
    missing = required.difference(targets.columns)
    if missing:
        raise ValueError(f"Target manifest missing columns: {sorted(missing)}")
    targets["session_date"] = pd.to_datetime(targets["session_date"]).dt.normalize()
    if (targets["session_date"] >= PROHIBITED_VALIDATION_START).any():
        bad = targets.loc[
            targets["session_date"] >= PROHIBITED_VALIDATION_START,
            ["ticker_as_of_session", "session_date"],
        ].head(3)
        raise ValueError(f"OOS/validation target entered calibration input:\n{bad}")
    if targets.duplicated(["instrument_id", "session_date"]).any():
        raise ValueError("Target manifest has duplicate instrument-session identities")

    calendar = pd.read_parquet(calendar_path)
    calendar["session_date"] = pd.to_datetime(calendar["session_date"]).dt.normalize()
    for column in ("open_utc", "close_utc"):
        if column not in calendar.columns:
            raise ValueError(f"Calendar missing {column}")
        calendar[column] = pd.to_datetime(calendar[column], utc=True)
    merged = targets.merge(
        calendar[["session_date", "open_utc", "close_utc"]],
        on="session_date",
        how="left",
        validate="many_to_one",
    )
    if merged[["open_utc", "close_utc"]].isna().any().any():
        raise ValueError("Calendar coverage is incomplete for target sessions")

    result: list[SessionContext] = []
    for row in merged.sort_values("target_ordinal").itertuples(index=False):
        manifest_declared = int(row.decision_seconds)
        calendar_expected = int((row.close_utc - row.open_utc).total_seconds()) - 1
        # The frozen sampling manifest predates the corrected Binding A
        # cardinality authority and declares close-open seconds (23,400 on a
        # full session). The production engine and exact run plan emit the
        # legal open+1 ... close-1 grid (23,399). Accept only this known,
        # explicit one-second legacy discrepancy; fail on every other delta.
        if manifest_declared not in {calendar_expected, calendar_expected + 1}:
            raise ValueError(
                f"Decision-grid mismatch {row.ticker_as_of_session} {row.session_date}: "
                f"manifest={manifest_declared} authority={calendar_expected}"
            )
        result.append(
            SessionContext(
                target_ordinal=int(row.target_ordinal),
                block_id=str(row.block_id),
                cohort_id=str(row.cohort_id),
                instrument_id=str(row.instrument_id),
                ticker=str(row.ticker_as_of_session),
                session_date=pd.Timestamp(row.session_date).date().isoformat(),
                open_utc=pd.Timestamp(row.open_utc),
                close_utc=pd.Timestamp(row.close_utc),
                expected_decision_seconds=calendar_expected,
                manifest_declared_decision_seconds=manifest_declared,
                presession_reference_price=float(row.presession_reference_price),
                presession_reference_market_cap_proxy=float(
                    row.presession_reference_market_cap_proxy
                ),
            )
        )
    return result


def choose_probe_targets(
    contexts: Iterable[SessionContext], per_cohort: int
) -> list[SessionContext]:
    counts: dict[str, int] = {}
    selected: list[SessionContext] = []
    for context in sorted(
        contexts, key=lambda item: (item.cohort_id, item.block_id, item.target_ordinal)
    ):
        count = counts.get(context.cohort_id, 0)
        if count < per_cohort:
            selected.append(context)
            counts[context.cohort_id] = count + 1
    return selected


def _coerce_conditions(value: Any) -> list[int] | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, np.ndarray):
        return [int(item) for item in value.tolist()]
    if isinstance(value, (list, tuple)):
        return [int(item) for item in value]
    return value


def build_session_second_metrics(
    context: SessionContext,
    raw_root: Path,
    policy_module: Any,
    condition_matrix: dict[int, dict[str, str]],
    simulated_latency_ms: int,
) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    """Return dense decision-second metrics, audit summary and eligible events."""

    source_path = raw_trade_path(raw_root, context.ticker, context.session_date)
    grid = pd.date_range(
        context.open_utc + pd.Timedelta(seconds=1),
        context.close_utc - pd.Timedelta(seconds=1),
        freq="1s",
        tz="UTC",
    )
    if len(grid) != context.expected_decision_seconds:
        raise ValueError(f"Decision-grid cardinality mismatch for {context}")
    base = pd.DataFrame({"decision_timestamp_utc": grid})
    for column in (
        "trade_count",
        "share_volume",
        "dollar_volume",
        "distinct_timestamp_clusters",
        "duplicate_trade_count",
        "restricted_or_unknown_trade_count",
    ):
        base[column] = 0.0 if "volume" in column else 0

    common = {
        "target_file_key": context.target_file_key,
        "target_ordinal": context.target_ordinal,
        "block_id": context.block_id,
        "cohort_id": context.cohort_id,
        "instrument_id": context.instrument_id,
        "ticker": context.ticker,
        "session_date": context.session_date,
        "session_open_utc": context.open_utc,
        "presession_reference_price": context.presession_reference_price,
        "presession_reference_market_cap_proxy": (
            context.presession_reference_market_cap_proxy
        ),
    }
    for key, value in reversed(list(common.items())):
        base.insert(0, key, value)

    if not source_path.is_file():
        base["source_state"] = "UNAVAILABLE_SOURCE_FILE"
        audit = {
            **common,
            "source_path": str(source_path),
            "source_state": "UNAVAILABLE_SOURCE_FILE",
            "raw_rows": 0,
            "rth_rows": 0,
            "activity_eligible_rows": 0,
            "notional_eligible_rows": 0,
            "unknown_or_ineligible_rows": 0,
            "exact_duplicate_rows": 0,
            "decision_seconds": len(base),
        }
        return base, audit, pd.DataFrame()

    trades = pd.read_parquet(
        source_path,
        columns=["ticker", "date", "timestamp", "price", "size", "exchange", "conditions"],
    )
    raw_rows = len(trades)
    trades["timestamp"] = pd.to_datetime(trades["timestamp"], utc=True, errors="coerce")
    trades = trades.loc[
        (trades["timestamp"] > context.open_utc)
        & (trades["timestamp"] < context.close_utc)
    ].copy()
    rth_rows = len(trades)
    if trades.empty:
        base["source_state"] = "OBSERVED_ZERO"
        audit = {
            **common,
            "source_path": str(source_path),
            "source_state": "OBSERVED_ZERO",
            "raw_rows": raw_rows,
            "rth_rows": 0,
            "activity_eligible_rows": 0,
            "notional_eligible_rows": 0,
            "unknown_or_ineligible_rows": 0,
            "exact_duplicate_rows": 0,
            "decision_seconds": len(base),
        }
        return base, audit, trades

    duplicate_frame = trades.copy()
    duplicate_frame["conditions"] = duplicate_frame["conditions"].map(
        lambda value: tuple(_coerce_conditions(value) or [])
    )
    duplicate_mask = duplicate_frame.duplicated(
        ["ticker", "date", "timestamp", "price", "size", "exchange", "conditions"],
        keep=False,
    )
    activity_ok = np.zeros(len(trades), dtype=bool)
    notional_ok = np.zeros(len(trades), dtype=bool)
    restricted_or_unknown = np.zeros(len(trades), dtype=bool)
    for position, row in enumerate(trades.itertuples(index=False)):
        payload = row._asdict()
        payload["conditions"] = _coerce_conditions(payload.get("conditions"))
        result = policy_module.evaluate_trade(
            payload,
            condition_matrix,
            in_rth=True,
            source_available=True,
            exact_duplicate_research_flag=bool(duplicate_mask.iloc[position]),
        )
        activity_ok[position] = result["trade_activity_eligibility_state"].startswith(
            "ELIGIBLE"
        )
        notional_ok[position] = result["trade_notional_eligibility_state"].startswith(
            "ELIGIBLE"
        )
        restricted_or_unknown[position] = not activity_ok[position]

    trades["activity_eligible"] = activity_ok
    trades["notional_eligible"] = notional_ok
    trades["exact_duplicate_flag"] = duplicate_mask.to_numpy()
    trades["restricted_or_unknown"] = restricted_or_unknown
    # Availability is source timestamp + governed simulated latency.  The row is
    # emitted on the first decision second at or after that availability time.
    trades["available_timestamp_utc"] = trades["timestamp"] + pd.to_timedelta(
        simulated_latency_ms, unit="ms"
    )
    trades["decision_timestamp_utc"] = trades["available_timestamp_utc"].dt.ceil("s")
    trades = trades.loc[
        (trades["decision_timestamp_utc"] >= grid[0])
        & (trades["decision_timestamp_utc"] <= grid[-1])
    ].copy()
    eligible = trades.loc[trades["activity_eligible"]].copy()
    eligible["eligible_shares"] = pd.to_numeric(eligible["size"], errors="coerce")
    eligible["eligible_dollar"] = np.where(
        eligible["notional_eligible"],
        pd.to_numeric(eligible["price"], errors="coerce") * eligible["eligible_shares"],
        0.0,
    )
    eligible["cluster_key"] = eligible["timestamp"].astype("int64")

    if not eligible.empty:
        grouped = eligible.groupby("decision_timestamp_utc", sort=True).agg(
            trade_count=("activity_eligible", "size"),
            share_volume=("eligible_shares", "sum"),
            dollar_volume=("eligible_dollar", "sum"),
            distinct_timestamp_clusters=("cluster_key", "nunique"),
            duplicate_trade_count=("exact_duplicate_flag", "sum"),
        )
        restricted = trades.groupby("decision_timestamp_utc")[
            "restricted_or_unknown"
        ].sum()
        grouped["restricted_or_unknown_trade_count"] = restricted.reindex(
            grouped.index, fill_value=0
        )
        base = base.set_index("decision_timestamp_utc")
        base.update(grouped)
        base = base.reset_index()
    base["source_state"] = "OBSERVED"
    audit = {
        **common,
        "source_path": str(source_path),
        "source_state": "OBSERVED",
        "raw_rows": raw_rows,
        "rth_rows": rth_rows,
        "activity_eligible_rows": int(activity_ok.sum()),
        "notional_eligible_rows": int(notional_ok.sum()),
        "unknown_or_ineligible_rows": int(restricted_or_unknown.sum()),
        "exact_duplicate_rows": int(duplicate_mask.sum()),
        "decision_seconds": len(base),
    }
    return base, audit, eligible


def _future_sum(series: pd.Series, horizon: int) -> pd.Series:
    return series.iloc[::-1].rolling(horizon, min_periods=1).sum().iloc[::-1]


def discover_candidates(
    metrics: pd.DataFrame,
    dormancy_windows: list[int],
    confirmation_windows: list[int],
    minimum_trades: int,
    minimum_clusters: int,
    top_per_window_pair: int,
    maximum_per_session: int,
    merge_gap_seconds: int,
) -> pd.DataFrame:
    """Generate a high-recall candidate set without assigning Wake-up labels."""

    if metrics["source_state"].iloc[0] != "OBSERVED":
        return pd.DataFrame()
    candidates: list[pd.DataFrame] = []
    trade_count = metrics["trade_count"].astype(float)
    clusters = metrics["distinct_timestamp_clusters"].astype(float)
    dollars = metrics["dollar_volume"].astype(float)
    for prior_window in dormancy_windows:
        prior_trade = trade_count.shift(1).rolling(prior_window, min_periods=1).sum()
        prior_cluster = clusters.shift(1).rolling(prior_window, min_periods=1).sum()
        prior_dollar = dollars.shift(1).rolling(prior_window, min_periods=1).sum()
        prior_observed = np.minimum(np.arange(len(metrics)), prior_window)
        prior_observed = np.maximum(prior_observed, 1)
        for confirmation_window in confirmation_windows:
            future_trade = _future_sum(trade_count, confirmation_window)
            future_cluster = _future_sum(clusters, confirmation_window)
            future_dollar = _future_sum(dollars, confirmation_window)
            # Compare rates, not raw window totals. This is candidate reduction,
            # never the label definition or an A/B input.
            expected_trade = prior_trade * confirmation_window / prior_observed
            expected_cluster = prior_cluster * confirmation_window / prior_observed
            expected_dollar = prior_dollar * confirmation_window / prior_observed
            score = (
                np.log1p(future_trade) - np.log1p(expected_trade)
                + np.log1p(future_cluster) - np.log1p(expected_cluster)
                + np.log1p(future_dollar) - np.log1p(expected_dollar)
            )
            valid = (
                (future_trade >= minimum_trades)
                & (future_cluster >= minimum_clusters)
                & (np.arange(len(metrics)) >= min(60, prior_window))
            )
            if not valid.any():
                continue
            local = pd.DataFrame(
                {
                    "row_position": np.arange(len(metrics)),
                    "candidate_timestamp_utc": metrics["decision_timestamp_utc"],
                    "dormancy_window_seconds": prior_window,
                    "confirmation_window_seconds": confirmation_window,
                    "candidate_reduction_score": score,
                    "prior_trade_count": prior_trade,
                    "prior_cluster_count": prior_cluster,
                    "prior_dollar_volume": prior_dollar,
                    "confirmation_trade_count": future_trade,
                    "confirmation_cluster_count": future_cluster,
                    "confirmation_dollar_volume": future_dollar,
                }
            ).loc[valid]
            local = local.nlargest(top_per_window_pair, "candidate_reduction_score")
            candidates.append(local)
    if not candidates:
        return pd.DataFrame()
    combined = pd.concat(candidates, ignore_index=True)
    combined = combined.sort_values(
        ["candidate_reduction_score", "candidate_timestamp_utc"],
        ascending=[False, True],
    )
    kept: list[pd.Series] = []
    kept_times: list[pd.Timestamp] = []
    for _, row in combined.iterrows():
        timestamp = pd.Timestamp(row["candidate_timestamp_utc"])
        if any(abs((timestamp - other).total_seconds()) <= merge_gap_seconds for other in kept_times):
            continue
        kept.append(row)
        kept_times.append(timestamp)
        if len(kept) >= maximum_per_session:
            break
    output = pd.DataFrame(kept).reset_index(drop=True)
    if output.empty:
        return output
    for column in (
        "target_file_key",
        "target_ordinal",
        "block_id",
        "cohort_id",
        "instrument_id",
        "ticker",
        "session_date",
        "session_open_utc",
        "presession_reference_price",
        "presession_reference_market_cap_proxy",
    ):
        output.insert(0, column, metrics[column].iloc[0])
    output["candidate_rank_in_session"] = np.arange(1, len(output) + 1)
    output["candidate_state"] = "UNLABELED_CANDIDATE_REDUCTION_ONLY"
    return output


def stable_case_id(row: pd.Series) -> str:
    raw = "|".join(
        [
            str(row.get("instrument_id", "")),
            str(row.get("session_date", "")),
            str(row.get("candidate_timestamp_utc", "")),
            str(row.get("panel_role", "")),
        ]
    )
    return "wucase:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
