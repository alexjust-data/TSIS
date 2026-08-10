#!/usr/bin/env python3
"""Build the frozen TA-3 stratified development sample."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

DATASET_ID = "trading_activity_ta3_stratified_development_sample_v0_1"
SCHEMA_VERSION = "trading_activity_ta3_sample_manifest_v0_1"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--memory-limit", default="12GB")
    parser.add_argument("--temp-directory", type=Path)
    parser.add_argument("--stop-file", type=Path)
    return parser


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _progress(stage: str, message: str) -> None:
    print(
        json.dumps(
            {
                "at_utc": datetime.now(UTC).isoformat(),
                "stage": stage,
                "message": message,
            }
        ),
        flush=True,
    )


def _stop_if_requested(stop_file: Path | None) -> None:
    if stop_file is not None and stop_file.exists():
        raise RuntimeError(f"Cooperative stop requested through {stop_file}")


def _sql_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def _parquet_glob(path: Path) -> str:
    return _sql_path(path).rstrip("/") + "/**/*.parquet"


def _cohort_case(cohorts: list[dict[str, str]], column: str = "session_date") -> str:
    branches = "\n".join(
        f"WHEN {column} BETWEEN DATE '{item['start']}' AND DATE '{item['end']}' "
        f"THEN '{item['cohort_id']}'"
        for item in cohorts
    )
    return f"CASE {branches} END"


def _price_case(column: str) -> str:
    return f"""
    CASE
      WHEN {column} >= 0.50 AND {column} < 1.00 THEN 'P1'
      WHEN {column} >= 1.00 AND {column} < 2.00 THEN 'P2'
      WHEN {column} >= 2.00 AND {column} < 5.00 THEN 'P3'
      WHEN {column} >= 5.00 AND {column} < 10.00 THEN 'P4'
      WHEN {column} >= 10.00 AND {column} <= 20.00 THEN 'P5'
    END
    """


def _cap_case(column: str) -> str:
    return f"""
    CASE
      WHEN {column} >= 0 AND {column} < 10000000.0 THEN 'M1'
      WHEN {column} >= 10000000.0 AND {column} < 25000000.0 THEN 'M2'
      WHEN {column} >= 25000000.0 AND {column} < 50000000.0 THEN 'M3'
      WHEN {column} >= 50000000.0 AND {column} < 100000000.0 THEN 'M4'
    END
    """


def _verify_source(path: Path, expected_sha256: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = _sha256(path)
    if actual.lower() != expected_sha256.lower():
        raise ValueError(f"Hash mismatch for {path}: {actual} != {expected_sha256}")
    return {"path": str(path), "sha256": actual, "size_bytes": path.stat().st_size}


def _hard_targets(
    frame: pd.DataFrame,
    *,
    price_minimum: int,
    cap_minimum: int,
    metadata_minimum: int,
) -> dict[str, dict[str, int]]:
    targets: dict[str, dict[str, int]] = {}
    for column, requested in (
        ("price_band", price_minimum),
        ("market_cap_band", cap_minimum),
        ("foundation_quality_label", metadata_minimum),
        ("local_audit_disposition", metadata_minimum),
    ):
        counts = frame[column].fillna("UNAVAILABLE").value_counts().to_dict()
        targets[column] = {
            str(value): min(requested, int(count))
            for value, count in counts.items()
            if int(count) >= requested or column in {"price_band", "market_cap_band"}
        }
    return targets


def _soft_targets(frame: pd.DataFrame, capacity: int) -> dict[str, dict[str, float]]:
    targets: dict[str, dict[str, float]] = {}
    for column in ("activity_stratum", "zero_prevalence_stratum"):
        values = sorted(str(item) for item in frame[column].dropna().unique())
        target = capacity / len(values) if values else 0.0
        targets[column] = {value: target for value in values}
    return targets


def _compatible(
    row: dict[str, Any],
    *,
    selected_indices: set[int],
    composite_starts: dict[str, list[int]],
    bare_counts: Counter[str],
    max_composite: int,
    max_bare: int,
    minimum_separation: int,
) -> bool:
    if int(row["_candidate_index"]) in selected_indices:
        return False
    composite = str(row["instrument_context_key"])
    bare = str(row["instrument_id"])
    starts = composite_starts.get(composite, [])
    if len(starts) >= max_composite or bare_counts[bare] >= max_bare:
        return False
    start = int(row["block_start_governed_index"])
    return all(abs(start - prior) >= minimum_separation for prior in starts)


def select_cohort_blocks(
    frame: pd.DataFrame,
    *,
    capacity: int,
    price_minimum: int,
    cap_minimum: int,
    metadata_minimum: int,
    max_composite: int,
    max_bare: int,
    minimum_separation: int,
    selected_indices: set[int] | None = None,
    composite_starts: dict[str, list[int]] | None = None,
    bare_counts: Counter[str] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Deterministically select one cohort under marginal and reuse constraints."""
    if frame.empty:
        raise ValueError("Cannot select from an empty cohort")
    working = frame.sort_values(
        ["selection_hash", "ticker_as_of_session", "block_start_population_context_id"],
        kind="mergesort",
    ).reset_index(drop=True)
    working["_candidate_index"] = range(len(working))
    records = working.to_dict("records")
    chosen_indices = selected_indices if selected_indices is not None else set()
    starts = composite_starts if composite_starts is not None else defaultdict(list)
    instrument_counts = bare_counts if bare_counts is not None else Counter()
    hard = _hard_targets(
        working,
        price_minimum=price_minimum,
        cap_minimum=cap_minimum,
        metadata_minimum=metadata_minimum,
    )
    soft = _soft_targets(working, capacity)
    selected_counts: dict[str, Counter[str]] = {
        column: Counter() for column in (*hard.keys(), *soft.keys())
    }
    selected: list[dict[str, Any]] = []

    while len(selected) < capacity:
        best: dict[str, Any] | None = None
        best_score: tuple[float, ...] | None = None
        for row in records:
            if not _compatible(
                row,
                selected_indices=chosen_indices,
                composite_starts=starts,
                bare_counts=instrument_counts,
                max_composite=max_composite,
                max_bare=max_bare,
                minimum_separation=minimum_separation,
            ):
                continue
            hard_hits = 0
            hard_deficit = 0.0
            for column, targets in hard.items():
                value = str(row.get(column) or "UNAVAILABLE")
                target = targets.get(value, 0)
                deficit = max(0, target - selected_counts[column][value])
                if deficit:
                    hard_hits += 1
                    hard_deficit += deficit / max(1, target)
            soft_hits = 0
            soft_deficit = 0.0
            for column, targets in soft.items():
                value = str(row.get(column) or "UNAVAILABLE")
                target = targets.get(value, 0.0)
                deficit = max(0.0, target - selected_counts[column][value])
                if deficit > 0:
                    soft_hits += 1
                    soft_deficit += deficit / max(1.0, target)
            score = (
                float(hard_hits),
                hard_deficit,
                float(soft_hits),
                soft_deficit,
            )
            if best is None or score > best_score:
                best = row
                best_score = score
        if best is None:
            break
        candidate_index = int(best["_candidate_index"])
        chosen_indices.add(candidate_index)
        composite = str(best["instrument_context_key"])
        bare = str(best["instrument_id"])
        starts[composite].append(int(best["block_start_governed_index"]))
        instrument_counts[bare] += 1
        for column in selected_counts:
            selected_counts[column][str(best.get(column) or "UNAVAILABLE")] += 1
        best = dict(best)
        best["selected_rank_in_cohort"] = len(selected) + 1
        selected.append(best)

    selected_frame = pd.DataFrame(selected).drop(columns=["_candidate_index"], errors="ignore")
    shortfalls: list[dict[str, Any]] = []
    for column, targets in hard.items():
        for value, target in sorted(targets.items()):
            actual = selected_counts[column][value]
            if actual < target:
                shortfalls.append(
                    {
                        "dimension": column,
                        "stratum": value,
                        "target": target,
                        "actual": actual,
                        "shortfall": target - actual,
                    }
                )
    audit = {
        "capacity_requested": capacity,
        "capacity_selected": len(selected_frame),
        "hard_targets": hard,
        "soft_targets": soft,
        "selected_counts": {
            column: dict(sorted(counter.items())) for column, counter in selected_counts.items()
        },
        "shortfalls": shortfalls,
    }
    return selected_frame, audit


def _write_query(
    connection: duckdb.DuckDBPyConnection,
    sql: str,
    path: Path,
    compression: str,
) -> dict[str, Any]:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    connection.execute(
        f"COPY ({sql}) TO '{_sql_path(path)}' (FORMAT PARQUET, COMPRESSION {compression.upper()})"
    )
    return {
        "path": str(path),
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size,
        "rows": connection.execute(f"SELECT COUNT(*) FROM ({sql})").fetchone()[0],
    }


def _state_counts(connection: duckdb.DuckDBPyConnection, sql: str) -> dict[str, int]:
    return {str(key): int(value) for key, value in connection.execute(sql).fetchall()}


def build(
    config_path: Path,
    output_root: Path,
    threads: int,
    memory_limit: str,
    temp_directory: Path | None,
    stop_file: Path | None = None,
) -> dict[str, Any]:
    if output_root.exists() and any(output_root.iterdir()):
        raise FileExistsError(f"Refusing to use non-empty output root: {output_root}")
    output_root.mkdir(parents=True, exist_ok=True)
    config = _read_json(config_path)
    sources = config["sources"]
    source_bindings = {
        "population_candidate": _verify_source(
            Path(sources["population_candidate"]), sources["population_candidate_sha256"]
        ),
        "population_manifest": _verify_source(
            Path(sources["population_manifest"]), sources["population_manifest_sha256"]
        ),
        "master_daily_manifest": _verify_source(
            Path(sources["master_daily_manifest"]), sources["master_daily_manifest_sha256"]
        ),
        "market_calendar": _verify_source(
            Path(sources["market_calendar"]), sources["market_calendar_sha256"]
        ),
        "foundation_quality_manifest": _verify_source(
            Path(sources["foundation_quality_manifest"]),
            sources["foundation_quality_manifest_sha256"],
        ),
    }
    _progress("STAGE_1", "source hashes verified")
    _stop_if_requested(stop_file)
    scope = config["scope"]
    block = config["block"]
    strata = config["strata"]
    compression = config["outputs"]["parquet_compression"]
    cohort_case = _cohort_case(scope["cohorts"])

    connection = duckdb.connect(database=":memory:")
    connection.execute(f"SET threads={max(1, threads)}")
    connection.execute(f"SET memory_limit='{memory_limit}'")
    if temp_directory is not None:
        temp_directory.mkdir(parents=True, exist_ok=True)
        connection.execute(f"SET temp_directory='{_sql_path(temp_directory)}'")
    connection.execute(
        f"CREATE VIEW population AS SELECT * FROM read_parquet('{_sql_path(Path(sources['population_candidate']))}')"
    )
    connection.execute(
        f"""
        CREATE VIEW master_daily AS
        SELECT * FROM read_parquet(
            '{_parquet_glob(Path(sources["master_daily_root"]))}',
            hive_partitioning=true,
            union_by_name=true
        ) WHERE price_view='daily_raw'
        """
    )
    connection.execute(
        f"CREATE VIEW calendar AS SELECT * FROM read_parquet('{_sql_path(Path(sources['market_calendar']))}')"
    )
    connection.execute(
        f"""
        CREATE VIEW foundation_quality_all AS
        SELECT * FROM read_parquet(
            '{_parquet_glob(Path(sources["foundation_quality_shards"]))}',
            union_by_name=true
        )
        """
    )

    development_end = scope["development_end"]
    development_start = scope["development_start"]
    prior_rows = int(strata["prior_activity_sessions"])
    connection.execute(
        f"""
        CREATE TEMP TABLE governed_contexts AS
        WITH joined AS (
          SELECT
            p.*,
            m.transaction_count,
            m.dollar_volume,
            ROW_NUMBER() OVER (
              PARTITION BY p.instrument_id, p.ticker_as_of_session
              ORDER BY p.session_date
            ) AS governed_index,
            COUNT(m.transaction_count) OVER (
              PARTITION BY p.instrument_id, p.ticker_as_of_session
              ORDER BY p.session_date
              ROWS BETWEEN {prior_rows} PRECEDING AND 1 PRECEDING
            ) AS prior_20_observed_session_count,
            COUNT(*) FILTER (WHERE m.transaction_count > 0) OVER (
              PARTITION BY p.instrument_id, p.ticker_as_of_session
              ORDER BY p.session_date
              ROWS BETWEEN {prior_rows} PRECEDING AND 1 PRECEDING
            ) AS prior_20_positive_session_count,
            MEDIAN(m.transaction_count) FILTER (WHERE m.transaction_count IS NOT NULL) OVER (
              PARTITION BY p.instrument_id, p.ticker_as_of_session
              ORDER BY p.session_date
              ROWS BETWEEN {prior_rows} PRECEDING AND 1 PRECEDING
            ) AS prior_20_median_transaction_count,
            MEDIAN(m.transaction_count) FILTER (WHERE m.transaction_count > 0) OVER (
              PARTITION BY p.instrument_id, p.ticker_as_of_session
              ORDER BY p.session_date
              ROWS BETWEEN {prior_rows} PRECEDING AND 1 PRECEDING
            ) AS prior_20_positive_median_transaction_count,
            MEDIAN(m.dollar_volume) FILTER (WHERE m.dollar_volume IS NOT NULL) OVER (
              PARTITION BY p.instrument_id, p.ticker_as_of_session
              ORDER BY p.session_date
              ROWS BETWEEN {prior_rows} PRECEDING AND 1 PRECEDING
            ) AS prior_20_median_dollar_volume,
            SUM(CASE WHEN m.transaction_count = 0 THEN 1 ELSE 0 END) OVER (
              PARTITION BY p.instrument_id, p.ticker_as_of_session
              ORDER BY p.session_date
              ROWS BETWEEN {prior_rows} PRECEDING AND 1 PRECEDING
            )::DOUBLE /
              NULLIF(COUNT(m.transaction_count) OVER (
                PARTITION BY p.instrument_id, p.ticker_as_of_session
                ORDER BY p.session_date
                ROWS BETWEEN {prior_rows} PRECEDING AND 1 PRECEDING
              ), 0) AS prior_20_zero_transaction_session_fraction
          FROM population p
          INNER JOIN master_daily m USING (master_daily_id)
          WHERE p.session_date <= DATE '{development_end}'
        )
        SELECT
          joined.*,
          instrument_id || '|' || ticker_as_of_session AS instrument_context_key,
          governed_index - 1 AS prior_governed_session_count,
          {cohort_case} AS cohort_id
        FROM joined
        """
    )
    connection.execute(
        f"""
        CREATE TEMP TABLE development_context_accounting AS
        SELECT
          *,
          CASE
            WHEN population_membership_state = '{config["population_binding"]["eligible_membership_state"]}'
             AND prior_governed_session_count >= {block["prior_governed_sessions"]}
              THEN 'ELIGIBLE_INVENTORY_CONTEXT'
            WHEN population_membership_state = '{config["population_binding"]["eligible_membership_state"]}'
              THEN 'BLOCKED_INSUFFICIENT_BASELINE_SUPPORT'
            WHEN population_membership_state IN (
              'INELIGIBLE_PRICE', 'INELIGIBLE_MARKET_CAP_PROXY',
              'OUTSIDE_INSTRUMENT_VALIDITY'
            ) THEN 'EXCLUDED_POPULATION_RULE'
            ELSE 'BLOCKED_SOURCE_OR_REVIEW'
          END AS sample_accounting_state
        FROM governed_contexts
        WHERE session_date BETWEEN DATE '{development_start}' AND DATE '{development_end}'
        """
    )
    connection.execute(
        f"""
        CREATE TEMP TABLE eligible_contexts AS
        SELECT
          *,
          ROW_NUMBER() OVER (
            PARTITION BY instrument_id, ticker_as_of_session
            ORDER BY session_date
          ) AS eligible_sequence_index
        FROM governed_contexts
        WHERE cohort_id IS NOT NULL
          AND population_membership_state = '{config["population_binding"]["eligible_membership_state"]}'
        """
    )
    target_count = int(block["target_eligible_contexts"])
    lead_offset = target_count - 1
    connection.execute(
        f"""
        CREATE TEMP TABLE block_windows AS
        SELECT
          *,
          LEAD(population_context_id, {lead_offset}) OVER w AS block_end_population_context_id,
          LEAD(session_date, {lead_offset}) OVER w AS block_end_session,
          LEAD(governed_index, {lead_offset}) OVER w AS block_end_governed_index,
          LEAD(cohort_id, {lead_offset}) OVER w AS block_end_cohort_id
        FROM eligible_contexts
        WINDOW w AS (
          PARTITION BY instrument_id, ticker_as_of_session
          ORDER BY eligible_sequence_index
        )
        """
    )
    connection.execute(
        f"""
        CREATE TEMP TABLE foundation_quality AS
        SELECT * EXCLUDE (quality_rank)
        FROM (
          SELECT
            ticker,
            CAST(date AS DATE) AS session_date,
            acceptance_label,
            severity,
            file AS foundation_source_file,
            COUNT(*) OVER (PARTITION BY ticker, CAST(date AS DATE)) AS quality_source_rows,
            ROW_NUMBER() OVER (
              PARTITION BY ticker, CAST(date AS DATE)
              ORDER BY file, acceptance_label
            ) AS quality_rank
          FROM foundation_quality_all
          WHERE CAST(date AS DATE) BETWEEN DATE '{development_start}' AND DATE '{development_end}'
        )
        WHERE quality_rank=1
        """
    )
    seed = config["sample_seed"]
    connection.execute(
        f"""
        CREATE TEMP TABLE feasible_blocks_raw AS
        SELECT
          'ta3b:' || md5(
            '{DATASET_ID}|' || b.population_context_id || '|{seed}'
          ) AS block_id,
          b.cohort_id,
          b.instrument_id,
          b.ticker_as_of_session,
          b.instrument_context_key,
          b.population_context_id AS block_start_population_context_id,
          b.session_date AS block_start_session,
          b.governed_index AS block_start_governed_index,
          b.eligible_sequence_index AS block_start_eligible_sequence_index,
          b.block_end_population_context_id,
          b.block_end_session,
          b.block_end_governed_index,
          w.session_date AS warmup_start_session,
          w.governed_index AS warmup_start_governed_index,
          b.block_end_governed_index - w.governed_index + 1 AS work_scope_session_count,
          {target_count} AS target_context_count,
          b.presession_reference_price,
          b.presession_reference_market_cap_proxy,
          {_price_case("b.presession_reference_price")} AS price_band,
          {_cap_case("b.presession_reference_market_cap_proxy")} AS market_cap_band,
          b.prior_20_observed_session_count,
          b.prior_20_positive_session_count,
          b.prior_20_median_transaction_count,
          b.prior_20_positive_median_transaction_count,
          b.prior_20_median_dollar_volume,
          b.prior_20_zero_transaction_session_fraction,
          COALESCE(q.acceptance_label, 'NO_FOUNDATION_EVIDENCE') AS foundation_quality_label,
          q.severity AS foundation_severity,
          q.foundation_source_file,
          COALESCE(q.quality_source_rows, 0) AS foundation_quality_source_rows,
          b.local_audit_disposition,
          b.family_data_quality_verdict,
          b.fundamental_quality_state,
          sha256(
            '{seed}' || '|' || b.cohort_id || '|' || b.instrument_id || '|' ||
            CAST(b.session_date AS VARCHAR)
          ) AS selection_hash
        FROM block_windows b
        INNER JOIN governed_contexts w
          ON b.instrument_id = w.instrument_id
         AND b.ticker_as_of_session = w.ticker_as_of_session
         AND w.governed_index = b.governed_index - {block["prior_governed_sessions"]}
        LEFT JOIN foundation_quality q
          ON b.ticker_as_of_session = q.ticker
         AND b.session_date = q.session_date
        WHERE b.block_end_population_context_id IS NOT NULL
          AND b.block_end_cohort_id = b.cohort_id
          AND b.prior_governed_session_count >= {block["prior_governed_sessions"]}
        """
    )
    connection.execute(
        """
        CREATE TEMP TABLE activity_thresholds AS
        SELECT
          cohort_id,
          quantile_cont(prior_20_positive_median_transaction_count, 0.33)
            FILTER (WHERE prior_20_observed_session_count = 20
                          AND prior_20_positive_session_count > 0) AS activity_p33,
          quantile_cont(prior_20_positive_median_transaction_count, 0.67)
            FILTER (WHERE prior_20_observed_session_count = 20
                          AND prior_20_positive_session_count > 0) AS activity_p67
        FROM feasible_blocks_raw
        GROUP BY cohort_id
        """
    )
    connection.execute(
        """
        CREATE TEMP TABLE feasible_blocks AS
        SELECT
          b.*,
          t.activity_p33,
          t.activity_p67,
          CASE
            WHEN b.prior_20_observed_session_count < 20 THEN 'AU'
            WHEN b.prior_20_positive_session_count = 0 THEN 'A0'
            WHEN b.prior_20_positive_median_transaction_count <= t.activity_p33 THEN 'A1'
            WHEN b.prior_20_positive_median_transaction_count <= t.activity_p67 THEN 'A2'
            ELSE 'A3'
          END AS activity_stratum,
          CASE
            WHEN b.prior_20_observed_session_count < 20 THEN 'ZU'
            WHEN b.prior_20_zero_transaction_session_fraction >= 0.90 THEN 'Z1'
            WHEN b.prior_20_zero_transaction_session_fraction >= 0.50 THEN 'Z2'
            ELSE 'Z3'
          END AS zero_prevalence_stratum
        FROM feasible_blocks_raw b
        INNER JOIN activity_thresholds t USING (cohort_id)
        """
    )

    _progress("STAGE_4", "feasible block inventory and frozen strata built")
    _stop_if_requested(stop_file)
    feasible_frame = connection.execute(
        """
        SELECT * FROM feasible_blocks
        ORDER BY cohort_id, selection_hash, ticker_as_of_session,
                 block_start_population_context_id
        """
    ).fetch_df()
    selected_frames: list[pd.DataFrame] = []
    cohort_audits: dict[str, Any] = {}
    global_bare_counts: Counter[str] = Counter()
    global_composite_starts: dict[str, list[int]] = defaultdict(list)
    for cohort in scope["cohorts"]:
        cohort_id = cohort["cohort_id"]
        cohort_frame = feasible_frame.loc[feasible_frame["cohort_id"] == cohort_id].copy()
        selected, audit = select_cohort_blocks(
            cohort_frame,
            capacity=int(block["blocks_per_cohort"]),
            price_minimum=int(strata["price_minimum_per_feasible_band_per_cohort"]),
            cap_minimum=int(strata["market_cap_minimum_per_feasible_band_per_cohort"]),
            metadata_minimum=int(strata["quality_minimum_when_feasible_count_at_least"]),
            max_composite=int(block["maximum_blocks_per_composite_instrument"]),
            max_bare=int(block["maximum_blocks_per_bare_instrument_id"]),
            minimum_separation=int(block["minimum_reuse_separation_governed_sessions"]),
            composite_starts=global_composite_starts,
            bare_counts=global_bare_counts,
        )
        if len(selected) != int(block["blocks_per_cohort"]):
            raise RuntimeError(f"Could select only {len(selected)} blocks for {cohort_id}")
        selected_frames.append(selected)
        cohort_audits[cohort_id] = audit
        _progress("STAGE_5", f"selected {len(selected)} blocks for {cohort_id}")
        _stop_if_requested(stop_file)
    selected_blocks = pd.concat(selected_frames, ignore_index=True)
    selected_blocks["sample_seed"] = seed
    selected_blocks["selection_status"] = "SELECTED_FOR_TA3_DEVELOPMENT"
    selected_blocks["block_id"] = selected_blocks["block_id"].astype(str)
    connection.register("selected_blocks_frame", selected_blocks)
    connection.execute("CREATE TEMP TABLE selected_blocks AS SELECT * FROM selected_blocks_frame")

    connection.execute(
        f"""
        CREATE TEMP TABLE selected_targets AS
        SELECT
          b.block_id,
          b.cohort_id,
          b.selected_rank_in_cohort,
          e.eligible_sequence_index - b.block_start_eligible_sequence_index + 1
            AS target_ordinal,
          e.population_context_id,
          e.instrument_id,
          e.ticker_as_of_session,
          e.instrument_context_key,
          e.session_date,
          e.governed_index,
          e.eligible_sequence_index,
          e.presession_cutoff_utc,
          e.presession_reference_price,
          e.presession_reference_market_cap_proxy,
          e.population_membership_state,
          e.population_membership_reason,
          e.local_audit_disposition,
          e.family_data_quality_verdict,
          e.fundamental_quality_state,
          e.master_daily_id,
          c.session_minutes,
          c.is_early_close,
          c.session_minutes * 60 AS decision_seconds,
          c.session_minutes * 60 * {config["binding_a_row_projection"]["current_state_rows_per_decision_second"]}
            AS expected_current_state_rows,
          c.session_minutes * 60 * {config["binding_a_row_projection"]["multiscale_contrast_rows_per_decision_second"]}
            AS expected_multiscale_contrast_rows,
          c.session_minutes * 60 * {config["binding_a_row_projection"]["pit_baseline_rows_per_decision_second"]}
            AS expected_pit_baseline_rows
        FROM selected_blocks b
        INNER JOIN eligible_contexts e
          ON b.instrument_id = e.instrument_id
         AND b.ticker_as_of_session = e.ticker_as_of_session
         AND e.eligible_sequence_index BETWEEN b.block_start_eligible_sequence_index
                                           AND b.block_start_eligible_sequence_index + {lead_offset}
        INNER JOIN calendar c USING (session_date)
        """
    )
    raw_root = _sql_path(Path(sources["raw_trade_root"])).rstrip("/")
    connection.execute(
        f"""
        CREATE TEMP TABLE selected_scope_sessions_base AS
        SELECT
          b.block_id,
          b.cohort_id,
          b.selected_rank_in_cohort,
          g.instrument_id,
          g.ticker_as_of_session,
          g.instrument_context_key,
          g.session_date,
          g.governed_index,
          CASE
            WHEN t.population_context_id IS NOT NULL THEN 'TARGET'
            WHEN g.governed_index < b.block_start_governed_index THEN 'WARMUP'
            ELSE 'INTERVENING_NON_TARGET'
          END AS scope_role,
          t.target_ordinal,
          g.population_context_id,
          g.population_membership_state,
          COALESCE(q.acceptance_label, 'NO_FOUNDATION_EVIDENCE') AS foundation_quality_label,
          q.severity AS foundation_severity,
          '{raw_root}/' || g.ticker_as_of_session ||
            '/year=' || strftime(g.session_date, '%Y') ||
            '/month=' || strftime(g.session_date, '%m') ||
            '/day=' || strftime(g.session_date, '%Y-%m-%d') ||
            '/market.parquet' AS source_path
        FROM selected_blocks b
        INNER JOIN governed_contexts g
          ON b.instrument_id = g.instrument_id
         AND b.ticker_as_of_session = g.ticker_as_of_session
         AND g.governed_index BETWEEN b.warmup_start_governed_index
                                  AND b.block_end_governed_index
        LEFT JOIN selected_targets t
          ON b.block_id = t.block_id
         AND g.population_context_id = t.population_context_id
        LEFT JOIN foundation_quality q
          ON g.ticker_as_of_session = q.ticker
         AND g.session_date = q.session_date
        """
    )
    scope_frame = connection.execute(
        "SELECT * FROM selected_scope_sessions_base ORDER BY block_id, governed_index"
    ).fetch_df()
    source_paths = [Path(item) for item in scope_frame["source_path"].astype(str)]
    scope_frame["source_exists"] = [path.is_file() for path in source_paths]
    scope_frame["source_bytes"] = [
        path.stat().st_size if path.is_file() else None for path in source_paths
    ]
    connection.register("selected_scope_sessions_frame", scope_frame)
    connection.execute(
        "CREATE TEMP TABLE selected_scope_sessions AS SELECT * FROM selected_scope_sessions_frame"
    )

    _progress("STAGE_6", "selected target and governed source scopes audited")
    _stop_if_requested(stop_file)
    outputs: dict[str, dict[str, Any]] = {}
    outputs["development_context_accounting"] = _write_query(
        connection,
        "SELECT * FROM development_context_accounting ORDER BY instrument_id, ticker_as_of_session, session_date",
        output_root / "development_context_accounting_v0_1.parquet",
        compression,
    )
    outputs["feasible_blocks"] = _write_query(
        connection,
        "SELECT * FROM feasible_blocks ORDER BY cohort_id, selection_hash, ticker_as_of_session, block_start_session",
        output_root / "feasible_blocks_v0_1.parquet",
        compression,
    )
    outputs["selected_blocks"] = _write_query(
        connection,
        "SELECT * FROM selected_blocks ORDER BY cohort_id, selected_rank_in_cohort",
        output_root / "selected_blocks_v0_1.parquet",
        compression,
    )
    outputs["selected_targets"] = _write_query(
        connection,
        "SELECT * FROM selected_targets ORDER BY cohort_id, selected_rank_in_cohort, target_ordinal",
        output_root / "selected_target_contexts_v0_1.parquet",
        compression,
    )
    outputs["selected_scope_sessions"] = _write_query(
        connection,
        "SELECT * FROM selected_scope_sessions ORDER BY block_id, governed_index",
        output_root / "selected_block_scope_sessions_v0_1.parquet",
        compression,
    )

    _progress("STAGE_7", "sample parquet artifacts written and hashed")
    _stop_if_requested(stop_file)
    accounting_counts = _state_counts(
        connection,
        "SELECT sample_accounting_state, COUNT(*) FROM development_context_accounting GROUP BY 1 ORDER BY 1",
    )
    feasible_counts = _state_counts(
        connection,
        "SELECT cohort_id, COUNT(*) FROM feasible_blocks GROUP BY 1 ORDER BY 1",
    )
    selected_counts = _state_counts(
        connection,
        "SELECT cohort_id, COUNT(*) FROM selected_blocks GROUP BY 1 ORDER BY 1",
    )
    target_counts = _state_counts(
        connection,
        "SELECT cohort_id, COUNT(*) FROM selected_targets GROUP BY 1 ORDER BY 1",
    )
    projection = connection.execute(
        """
        SELECT
          SUM(expected_current_state_rows),
          SUM(expected_multiscale_contrast_rows),
          SUM(expected_pit_baseline_rows),
          SUM(expected_current_state_rows + expected_multiscale_contrast_rows + expected_pit_baseline_rows),
          SUM(decision_seconds),
          COUNT(*) FILTER (WHERE is_early_close)
        FROM selected_targets
        """
    ).fetchone()
    missing_scope_rows = connection.execute(
        "SELECT COUNT(*) FROM selected_scope_sessions WHERE NOT source_exists"
    ).fetchone()[0]
    missing_target_rows = connection.execute(
        "SELECT COUNT(*) FROM selected_scope_sessions WHERE scope_role='TARGET' AND NOT source_exists"
    ).fetchone()[0]
    summary = {
        "dataset_id": DATASET_ID,
        "sample_seed": seed,
        "scope_id": config["scope"]["scope_id"],
        "development_range": [development_start, development_end],
        "accounting_state_counts": accounting_counts,
        "feasible_block_counts": feasible_counts,
        "selected_block_counts": selected_counts,
        "selected_target_counts": target_counts,
        "selected_blocks_total": int(len(selected_blocks)),
        "selected_targets_total": int(sum(target_counts.values())),
        "cohort_selection_audits": cohort_audits,
        "expected_binding_a_rows": {
            "current_state": int(projection[0]),
            "multiscale_contrast": int(projection[1]),
            "pit_baseline_and_surprise": int(projection[2]),
            "total": int(projection[3]),
            "decision_seconds": int(projection[4]),
            "early_close_target_sessions": int(projection[5]),
        },
        "selected_scope_sessions_total": int(len(scope_frame)),
        "selected_scope_missing_source_rows": int(missing_scope_rows),
        "selected_target_missing_source_rows": int(missing_target_rows),
        "official_trade_source_root": str(Path(sources["raw_trade_root"])),
        "legacy_root_fallback": "PROHIBITED",
        "missing_source_semantics": "UNAVAILABLE_G_OFFICIAL_RETAINED_IN_DENOMINATOR",
        "sample_manifest_gate_candidate": (
            "PASS_WITH_RESTRICTIONS"
            if len(selected_blocks) == 240 and sum(target_counts.values()) == 2400
            else "FAIL"
        ),
    }
    summary_path = output_root / "sample_design_summary_v0_1.json"
    _atomic_json(summary_path, summary)
    outputs["summary"] = {
        "path": str(summary_path),
        "sha256": _sha256(summary_path),
        "size_bytes": summary_path.stat().st_size,
    }
    manifest = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "promotion_state": "FROZEN_EXPERIMENTAL_SAMPLE_NOT_CANONICAL",
        "config_path": str(config_path),
        "config_sha256": _sha256(config_path),
        "source_bindings": source_bindings,
        "outputs": outputs,
        "summary": summary,
        "claims": {
            "development_only": True,
            "validation_lockbox_opened": False,
            "final_test_lockbox_opened": False,
            "full_historical_us_lt100m_population": False,
            "canonical_feature_promotion": False,
            "wake_up_detection": False,
        },
    }
    manifest_path = output_root / "sample_manifest_v0_1.json"
    _atomic_json(manifest_path, manifest)
    _progress("STAGE_8", "sample summary and manifest frozen")
    connection.close()
    return manifest


def main() -> int:
    args = _parser().parse_args()
    manifest = build(
        args.config,
        args.output_root,
        args.threads,
        args.memory_limit,
        args.temp_directory,
        args.stop_file,
    )
    print(json.dumps(manifest["summary"], indent=2, default=str))
    return 0 if manifest["summary"]["sample_manifest_gate_candidate"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
