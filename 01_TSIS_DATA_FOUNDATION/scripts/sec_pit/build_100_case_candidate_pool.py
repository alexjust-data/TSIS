#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd


COHORTS = (
    ("2005_2008", 2005, 2008),
    ("2009_2012", 2009, 2012),
    ("2013_2016", 2013, 2016),
    ("2017_2020", 2017, 2020),
    ("2021_2023", 2021, 2023),
    ("2024_2026", 2024, 2026),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_rank(seed: str, ticker: str) -> str:
    # Fixed-width hexadecimal preserves SHA-256 ordering without overflowing
    # Parquet's signed 64-bit integer representation.
    return hashlib.sha256(f"{seed}|{ticker}".encode()).hexdigest()


def shard_for(instrument_id: str, count: int) -> int:
    return int(hashlib.sha256(instrument_id.encode()).hexdigest(), 16) % count


def cohort_for_year(year: int) -> str:
    for label, first, last in COHORTS:
        if first <= year <= last:
            return label
    raise ValueError(f"first_seen year outside governed cohorts: {year}")


def _action_counts(actions: pd.DataFrame) -> pd.DataFrame:
    scoped = actions.copy()
    scoped["action_date"] = pd.to_datetime(scoped["action_date"])
    scoped["event_key"] = (
        scoped["ticker"].astype(str)
        + "|"
        + scoped["action_type"].astype(str)
        + "|"
        + scoped["action_date"].astype(str)
        + "|"
        + scoped["split_ratio"].astype(str)
        + "|"
        + scoped["ticker_change_ticker"].astype(str)
    )
    scoped = scoped.drop_duplicates("event_key")
    split = scoped.loc[scoped["action_type"].eq("split")].copy()
    split["is_reverse"] = pd.to_numeric(split["split_ratio"], errors="coerce").lt(1.0)
    split_counts = split.groupby("ticker").agg(
        split_event_count=("event_key", "size"),
        reverse_split_event_count=("is_reverse", "sum"),
    )
    ticker_changes = (
        scoped.loc[scoped["action_type"].eq("ticker_change")]
        .groupby("ticker")["event_key"]
        .size()
        .rename("ticker_change_action_count")
    )
    return split_counts.join(ticker_changes, how="outer").fillna(0).reset_index()


def build_frame(
    universe: pd.DataFrame,
    master: pd.DataFrame,
    actions: pd.DataFrame,
    *,
    anchors: set[str],
    seed: str,
    shard_count: int,
) -> pd.DataFrame:
    if len(universe) != 4824 or universe["ticker"].nunique() != 4824:
        raise ValueError("parent universe must contain exactly 4,824 unique tickers")
    if master["ticker"].duplicated().any():
        raise ValueError("instrument master must have one row per ticker for this gate")
    frame = universe[["ticker", "first_seen_date", "last_observed_date", "status_rebuilt"]].merge(
        master[[
            "instrument_id", "ticker", "cik", "name", "primary_exchange",
            "share_class_figi", "is_common_stock", "active_in_reference",
            "ticker_change_event_count",
        ]],
        on="ticker",
        how="left",
        validate="one_to_one",
    )
    if frame["instrument_id"].isna().any() or frame["cik"].isna().any():
        raise ValueError("every parent-universe ticker requires instrument identity and CIK")
    frame = frame.merge(_action_counts(actions), on="ticker", how="left")
    for column in ("split_event_count", "reverse_split_event_count", "ticker_change_action_count"):
        frame[column] = frame[column].fillna(0).astype(int)
    frame["first_seen_date"] = pd.to_datetime(frame["first_seen_date"])
    frame["last_observed_date"] = pd.to_datetime(frame["last_observed_date"])
    frame["first_seen_year"] = frame["first_seen_date"].dt.year
    frame["last_observed_year"] = frame["last_observed_date"].dt.year
    frame["observed_span_days"] = (frame["last_observed_date"] - frame["first_seen_date"]).dt.days
    frame["temporal_cohort"] = frame["first_seen_year"].map(cohort_for_year)
    frame["shard"] = frame["instrument_id"].map(lambda value: shard_for(str(value), shard_count))
    frame["stable_rank"] = frame["ticker"].map(lambda value: stable_rank(seed, str(value)))
    frame["tag_anchor"] = frame["ticker"].isin(anchors)
    frame["tag_longitudinal_2005_to_2025"] = frame["first_seen_year"].le(2005) & frame["last_observed_year"].ge(2025)
    frame["tag_multiple_ticker_changes"] = frame[["ticker_change_event_count", "ticker_change_action_count"]].max(axis=1).ge(2)
    frame["tag_heavy_reverse_split_history"] = frame["reverse_split_event_count"].ge(4)
    frame["tag_spac_name_candidate"] = frame["name"].fillna("").str.contains(
        r"acquisition|blank check", case=False, regex=True
    )
    frame["tag_inactive_or_delisted_candidate"] = (
        frame["status_rebuilt"].astype(str).str.lower().eq("inactive")
        | ~frame["active_in_reference"].fillna(False)
    )
    frame["tag_recent_listing_candidate"] = frame["first_seen_year"].ge(2023)
    return frame


TAG_COLUMNS = {
    "ANCHOR_7_CASE": "tag_anchor",
    "LONGITUDINAL_2005_TO_2025": "tag_longitudinal_2005_to_2025",
    "MULTIPLE_TICKER_CHANGES": "tag_multiple_ticker_changes",
    "HEAVY_REVERSE_SPLIT_HISTORY": "tag_heavy_reverse_split_history",
    "SPAC_NAME_CANDIDATE": "tag_spac_name_candidate",
    "INACTIVE_OR_DELISTED_CANDIDATE": "tag_inactive_or_delisted_candidate",
    "RECENT_LISTING_CANDIDATE": "tag_recent_listing_candidate",
}


def select_pool(
    frame: pd.DataFrame,
    *,
    cohort_quotas: dict[str, int],
    tag_targets: dict[str, int],
    anchors: set[str],
) -> pd.DataFrame:
    selected: list[int] = []
    selected_set: set[int] = set()
    tag_counts = {tag: 0 for tag in tag_targets}
    cohort_counts = {cohort: 0 for cohort in cohort_quotas}

    def add(index: int) -> None:
        if index in selected_set:
            return
        row = frame.loc[index]
        cohort = str(row["temporal_cohort"])
        if cohort_counts[cohort] >= int(cohort_quotas[cohort]):
            raise ValueError(f"cohort quota cannot admit required row {row['ticker']}")
        selected.append(index)
        selected_set.add(index)
        cohort_counts[cohort] += 1
        for tag, column in TAG_COLUMNS.items():
            tag_counts[tag] += int(bool(row[column]))

    anchor_rows = frame.loc[frame["ticker"].isin(anchors)].sort_values("ticker")
    if set(anchor_rows["ticker"]) != anchors:
        raise ValueError("all governed anchors must exist in the parent universe")
    for index in anchor_rows.index:
        add(int(index))

    while len(selected) < sum(int(value) for value in cohort_quotas.values()):
        candidates = frame.loc[~frame.index.isin(selected_set)].copy()
        candidates = candidates.loc[candidates.apply(
            lambda row: cohort_counts[str(row["temporal_cohort"])] < int(cohort_quotas[str(row["temporal_cohort"])]),
            axis=1,
        )]
        if candidates.empty:
            raise ValueError("candidate pool exhausted before satisfying cohort quotas")
        scores = pd.Series(0.0, index=candidates.index)
        for tag, target in tag_targets.items():
            deficit = max(0, int(target) - tag_counts[tag])
            if deficit:
                scores += candidates[TAG_COLUMNS[tag]].astype(float) * (deficit / max(1, int(target)))
        candidates["selection_score"] = scores
        chosen = candidates.sort_values(
            ["selection_score", "stable_rank"], ascending=[False, True]
        ).index[0]
        add(int(chosen))

    result = frame.loc[selected].copy()
    result["selection_order"] = range(1, len(result) + 1)
    result["local_tags_json"] = result.apply(
        lambda row: json.dumps(
            [tag for tag, column in TAG_COLUMNS.items() if bool(row[column])],
            separators=(",", ":"),
        ),
        axis=1,
    )
    return result.sort_values(["temporal_cohort", "selection_order"]).reset_index(drop=True)


def execute(config_path: Path, output: Path) -> Path:
    config_path = config_path.resolve()
    output = output.resolve()
    if output.exists():
        raise FileExistsError(output)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output.mkdir(parents=True)
    source_paths = {
        key: Path(config[key]).resolve()
        for key in ("parent_universe_path", "instrument_master_path", "corporate_actions_path")
    }
    pre_manifest = {
        "run_id": output.name,
        "status": "RUNNING",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "config_path": config_path.as_posix(),
        "config_sha256": sha256_file(config_path),
        "network_access": "PROHIBITED_AND_NOT_USED",
        "primary_document_download": "NOT_AUTHORIZED",
        "source_hashes": {key: sha256_file(path) for key, path in source_paths.items()},
    }
    (output / "pre_manifest.json").write_text(json.dumps(pre_manifest, indent=2) + "\n", encoding="utf-8")
    universe = pd.read_parquet(source_paths["parent_universe_path"])
    master = pd.read_parquet(source_paths["instrument_master_path"])
    actions = pd.read_parquet(source_paths["corporate_actions_path"])
    frame = build_frame(
        universe,
        master,
        actions,
        anchors=set(config["anchors"]),
        seed=config["selection_seed"],
        shard_count=int(config["shard_count"]),
    )
    pool = select_pool(
        frame,
        cohort_quotas=config["temporal_cohort_quotas"],
        tag_targets=config["candidate_local_tag_targets"],
        anchors=set(config["anchors"]),
    )
    if len(pool) != int(config["candidate_pool_size"]):
        raise ValueError("candidate pool size does not match governed config")
    pool_path = output / "candidate_pool.parquet"
    pool.to_parquet(pool_path, index=False)
    pool.to_csv(output / "candidate_pool.csv", index=False)
    year_rows = []
    for year in range(
        int(config["required_calendar_years"]["first"]),
        int(config["required_calendar_years"]["last"]) + 1,
    ):
        year_rows.append({
            "calendar_year": year,
            "interval_covering_candidate_count": int(
                (pool["first_seen_year"].le(year) & pool["last_observed_year"].ge(year)).sum()
            ),
        })
    year_frame = pd.DataFrame(year_rows)
    year_frame.to_csv(output / "calendar_year_coverage.csv", index=False)
    summary = {
        "run_id": output.name,
        "status": "COMPLETE",
        "completed_at_utc": datetime.now(UTC).isoformat(),
        "parent_universe_count": len(frame),
        "candidate_pool_count": len(pool),
        "cohort_counts": pool["temporal_cohort"].value_counts().sort_index().to_dict(),
        "shard_counts": {str(key): int(value) for key, value in pool["shard"].value_counts().sort_index().items()},
        "tag_counts": {tag: int(pool[column].sum()) for tag, column in TAG_COLUMNS.items()},
        "minimum_calendar_year_coverage": int(year_frame["interval_covering_candidate_count"].min()),
        "next_gate": "SEC_SUBMISSIONS_METADATA_ONLY_PROFILE",
        "primary_document_download": "NOT_AUTHORIZED",
        "outputs": {
            "candidate_pool.parquet": sha256_file(pool_path),
            "candidate_pool.csv": sha256_file(output / "candidate_pool.csv"),
            "calendar_year_coverage.csv": sha256_file(output / "calendar_year_coverage.csv"),
        },
    }
    (output / "final_manifest.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(execute(args.config, args.output))
