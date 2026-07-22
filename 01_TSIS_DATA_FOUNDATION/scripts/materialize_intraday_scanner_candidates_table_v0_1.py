from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import yaml


MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parent

DEFAULT_MINUTE_ROOT = Path("E:/TSIS/data/ohlcv_1m")
DEFAULT_MASTER_DAILY_ROOT = Path(
    "E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1"
)
DEFAULT_MASTER_DAILY_MANIFEST = Path(
    "E:/TSIS/data/data_foundation_outputs/master_daily_table/_master_daily_table_manifest_v0_1.json"
)
DEFAULT_INSTRUMENT_MASTER = Path(
    "E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet"
)
DEFAULT_INSTRUMENT_MANIFEST = Path(
    "E:/TSIS/data/data_foundation_outputs/instrument_master/_instrument_master_manifest_v0_1.json"
)
DEFAULT_MARKET_CALENDAR = Path(
    "E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet"
)
DEFAULT_MARKET_CALENDAR_MANIFEST = Path(
    "E:/TSIS/data/data_foundation_outputs/market_calendar/_market_calendar_manifest_v0_1.json"
)
DEFAULT_SCANNER_DEFINITIONS_DIR = (
    MODULE_ROOT / "configs" / "data_foundation_outputs" / "scanner_definitions"
)

DATASET_ID = "intraday_scanner_candidates_table_v0_1"
DATASET_DIR_NAME = "intraday_scanner_candidates_table_v0_1_candidate_replay"
SCHEMA_VERSION = "intraday_scanner_candidates_table_v0_1"
QUALITY_POLICY_VERSION = "intraday_scanner_candidates_policy_v0_1"
SCANNER_POLICY_VERSION = "intraday_scanner_framework_v0_1"
SCANNER_DEFINITION_ID = "intraday_in_play_momentum_candidate_denominator_v0_1"
BASE_SCANNER_ID = "base_eligible_smallcap_denominator_v0_3"

CONTRACTS = {
    "target_contract": (
        "01_foundations/module_contracts/outputs/"
        "intraday_scanner_candidates_table_target_contract_v0_1.md"
    ),
    "scanner_contract": (
        "01_foundations/module_contracts/outputs/"
        "intraday_scanner_framework_and_definitions_contract_v0_1.md"
    ),
    "cto_contract": (
        "00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/"
        "00_SCANNER_CANDIDATE_SELECTION/intraday_scanner_candidates_contract_v0_1.md"
    ),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id() -> str:
    return "intraday_scanner_candidates_replay_v0_1_" + datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def _as_posix(path: Path) -> str:
    return path.as_posix()


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _read_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_parquet_tree(root: Path) -> dict[str, int | str]:
    digest = hashlib.sha256()
    files = sorted(path for path in root.glob("*.parquet") if path.is_file())
    total_bytes = 0
    for path in files:
        size = path.stat().st_size
        file_hash = _sha256_file(path)
        total_bytes += size
        digest.update(path.name.encode("utf-8"))
        digest.update(str(size).encode("ascii"))
        digest.update(file_hash.encode("ascii"))
    return {
        "parquet_file_count": len(files),
        "total_bytes": total_bytes,
        "tree_sha256": digest.hexdigest(),
    }


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _month_keys(start_date: str, end_date: str) -> list[tuple[int, int]]:
    start = _parse_date(start_date)
    end = _parse_date(end_date)
    keys: list[tuple[int, int]] = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        keys.append((year, month))
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    return keys


def _minute_files(minute_root: Path, start_date: str, end_date: str) -> list[Path]:
    files: list[Path] = []
    for year, month in _month_keys(start_date, end_date):
        pattern = minute_root / "ticker=*" / f"year={year}" / f"month={month:02d}" / "*.parquet"
        files.extend(Path(path) for path in glob.glob(str(pattern)))
    return sorted(files)


def _sql_path_list(paths: list[Path]) -> str:
    return "[" + ", ".join(_sql_literal(_as_posix(path)) for path in paths) + "]"


def _scanner_config_paths(scanner_definitions_dir: Path) -> list[Path]:
    paths = [
        scanner_definitions_dir / "base_eligible_smallcap_denominator_v0_3.yaml",
        scanner_definitions_dir / "intraday_in_play_momentum_candidate_denominator_v0_1.yaml",
    ]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing scanner definition config(s): {missing}")
    return paths


def _default_output_root(run_id: str) -> Path:
    date_key = datetime.now().strftime("%Y-%m-%d")
    return REPO_ROOT / "tests" / "test_runs" / date_key / run_id


def _validate_args(args: argparse.Namespace) -> None:
    if args.start_date > args.end_date:
        raise ValueError("--start-date must be <= --end-date")
    for path in (
        args.minute_root,
        args.master_daily_root,
        args.instrument_master,
        args.market_calendar,
        args.scanner_definitions_dir,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    if args.output_root.exists() and any(args.output_root.iterdir()) and not args.overwrite:
        raise FileExistsError(
            f"Output root already exists and is not empty: {args.output_root}. Use --overwrite."
        )


def _build_sql(
    args: argparse.Namespace,
    configs: dict[str, dict[str, Any]],
    minute_files: list[Path],
) -> str:
    minute_paths = _sql_path_list(minute_files)
    master_glob = _as_posix(args.master_daily_root / "**" / "*.parquet")
    instrument_path = _as_posix(args.instrument_master)
    calendar_path = _as_posix(args.market_calendar)

    base_cfg = configs[BASE_SCANNER_ID]
    intraday_cfg = configs[SCANNER_DEFINITION_ID]

    eligibility = base_cfg["base_universe_eligibility"]
    market_cap_max = float(eligibility["market_cap_max_usd"])
    price_min = float(eligibility["last_price_min_exclusive"])
    price_max = float(eligibility["last_price_max_inclusive"])

    movement = intraday_cfg["movement_policy"]
    threshold_pct = float(movement["minimum_push_move_pct"])
    tradability = intraday_cfg["tradability_policy"]
    volume_min = float(tradability["minimum_volume_to_time"])
    dollar_min = float(tradability["minimum_dollar_volume_to_time"])

    scanner_run_id = _sql_literal(args.run_id)
    created_at_utc = _sql_literal(args.created_at_utc)
    price_view = _sql_literal(args.price_view)
    start_date = _sql_literal(args.start_date)
    end_date = _sql_literal(args.end_date)
    source_minute_root = _sql_literal(_as_posix(args.minute_root))
    source_master_root = _sql_literal(_as_posix(args.master_daily_root))
    source_master_manifest = _sql_literal(_as_posix(args.master_daily_manifest))
    source_instrument_manifest = _sql_literal(_as_posix(args.instrument_master_manifest))
    source_market_calendar_manifest = _sql_literal(_as_posix(args.market_calendar_manifest))

    return f"""
create or replace table intraday_scanner_rows as
with minutes_source as (
    select
        upper(ticker) as ticker,
        cast(ts_utc as timestamptz) as ts_utc_tz,
        timezone('America/New_York', cast(ts_utc as timestamptz)) as ts_et,
        cast(timezone('America/New_York', cast(ts_utc as timestamptz)) as date) as session_date,
        cast(o as double) as o,
        cast(h as double) as h,
        cast(l as double) as l,
        cast(c as double) as c,
        cast(v as double) as v,
        cast(vw as double) as vw,
        cast(n as bigint) as n,
        cast(t as bigint) as source_t_epoch_ms,
        filename as source_ohlcv_1m_file
    from read_parquet({minute_paths}, hive_partitioning=true, filename=true)
),
minutes_segmented as (
    select
        *,
        extract(hour from ts_et) * 60 + extract(minute from ts_et) as minute_of_day_et,
        case
            when extract(hour from ts_et) * 60 + extract(minute from ts_et) >= 240
             and extract(hour from ts_et) * 60 + extract(minute from ts_et) < 570
                then 'premarket'
            when extract(hour from ts_et) * 60 + extract(minute from ts_et) >= 570
             and extract(hour from ts_et) * 60 + extract(minute from ts_et) < 960
                then 'regular'
            when extract(hour from ts_et) * 60 + extract(minute from ts_et) >= 960
             and extract(hour from ts_et) * 60 + extract(minute from ts_et) <= 1200
                then 'afterhours'
            else 'outside_extended'
        end as session_segment
    from minutes_source
    where cast(session_date as date) between cast({start_date} as date) and cast({end_date} as date)
),
minutes_extended as (
    select *
    from minutes_segmented
    where session_segment <> 'outside_extended'
      and o is not null and h is not null and l is not null and c is not null
      and h > 0 and l > 0 and c > 0
),
instrument_source as (
    select * exclude (rn)
    from (
        select
            upper(ticker) as instrument_ticker,
            *,
            row_number() over (
                partition by upper(ticker)
                order by
                    coalesce(active_in_reference, false) desc,
                    valid_to desc nulls last,
                    reference_last_updated_utc desc nulls last
            ) as rn
        from read_parquet('{instrument_path}')
    )
    where rn = 1
),
daily_source as (
    select *
    from read_parquet('{master_glob}', hive_partitioning=true)
    where price_view = {price_view}
      and cast(session_date as date) between cast({start_date} as date) and cast({end_date} as date)
),
daily_dedup as (
    select * exclude (rn)
    from (
        select
            upper(ticker) as daily_ticker,
            *,
            row_number() over (
                partition by upper(ticker), cast(session_date as date), price_view
                order by
                    coalesce(data_present, false) desc,
                    coalesce(backtest_core_row_candidate, false) desc,
                    dollar_volume desc nulls last,
                    instrument_id asc
            ) as rn
        from daily_source
    )
    where rn = 1
),
calendar_source as (
    select
        cast(session_date as date) as calendar_session_date,
        true as expected_session,
        'calendar_session_present' as expected_reason,
        *
    from read_parquet('{calendar_path}')
),
joined as (
    select
        m.*,
        coalesce(d.instrument_id, i.instrument_id) as instrument_id,
        i.name as instrument_name,
        coalesce(i.is_common_stock, false) as is_common_stock,
        coalesce(i.lt1b_market_cap_t, i.overview_market_cap) as market_cap_usd,
        i.overview_weighted_shares_outstanding as shares_outstanding_context,
        i.primary_exchange,
        i.exchange_acronym,
        i.active_in_reference,
        i.reference_last_updated_utc,
        d.prior_close,
        d.open as daily_open,
        d.high as daily_high,
        d.low as daily_low,
        d.close as daily_close,
        d.volume as daily_volume,
        d.dollar_volume as daily_dollar_volume,
        d.rvol_20d,
        d.gap_pct,
        d.daily_return_pct,
        d.family_data_quality_verdict,
        d.data_present,
        d.backtest_core_row_candidate,
        d.build_run_id as master_daily_build_run_id,
        cal.expected_session,
        cal.expected_reason
    from minutes_extended m
    left join instrument_source i
      on m.ticker = i.instrument_ticker
    left join daily_dedup d
      on m.ticker = d.daily_ticker
     and cast(m.session_date as date) = cast(d.session_date as date)
    left join calendar_source cal
      on cast(m.session_date as date) = cal.calendar_session_date
),
metrics as (
    select
        *,
        first_value(o) over (
            partition by ticker, session_date, session_segment
            order by ts_utc_tz
            rows between unbounded preceding and unbounded following
        ) as segment_open,
        sum(coalesce(v, 0)) over (
            partition by ticker, session_date
            order by ts_utc_tz
            rows between unbounded preceding and current row
        ) as volume_to_time,
        sum(coalesce(v, 0) * coalesce(vw, c)) over (
            partition by ticker, session_date
            order by ts_utc_tz
            rows between unbounded preceding and current row
        ) as dollar_volume_to_time,
        row_number() over (
            partition by ticker, session_date
            order by ts_utc_tz
        ) as bars_observed_to_time,
        case
            when prior_close > 0 then ((h / prior_close) - 1.0) * 100.0
            else null
        end as move_vs_prev_close_pct,
        case
            when first_value(o) over (
                partition by ticker, session_date, session_segment
                order by ts_utc_tz
                rows between unbounded preceding and unbounded following
            ) > 0
            then ((h / first_value(o) over (
                partition by ticker, session_date, session_segment
                order by ts_utc_tz
                rows between unbounded preceding and unbounded following
            )) - 1.0) * 100.0
            else null
        end as move_vs_segment_open_pct
    from joined
),
session_agg as (
    select
        ticker,
        session_date,
        any_value(instrument_id) as instrument_id,
        any_value(instrument_name) as instrument_name,
        bool_or(is_common_stock) as is_common_stock,
        max(market_cap_usd) as market_cap_usd,
        max(shares_outstanding_context) as shares_outstanding_context,
        any_value(primary_exchange) as primary_exchange,
        any_value(exchange_acronym) as exchange_acronym,
        bool_or(coalesce(active_in_reference, false)) as active_in_reference,
        any_value(reference_last_updated_utc) as reference_last_updated_utc,
        any_value(prior_close) as prior_close,
        any_value(daily_open) as daily_open,
        any_value(daily_high) as daily_high,
        any_value(daily_low) as daily_low,
        any_value(daily_close) as daily_close,
        any_value(daily_volume) as daily_volume,
        any_value(daily_dollar_volume) as daily_dollar_volume,
        any_value(rvol_20d) as rvol_20d,
        any_value(gap_pct) as gap_pct,
        any_value(daily_return_pct) as daily_return_pct,
        any_value(family_data_quality_verdict) as family_data_quality_verdict,
        bool_or(coalesce(data_present, false)) as data_present,
        bool_or(coalesce(backtest_core_row_candidate, false)) as backtest_core_row_candidate,
        any_value(master_daily_build_run_id) as master_daily_build_run_id,
        bool_or(coalesce(expected_session, false)) as expected_session,
        any_value(expected_reason) as expected_reason,
        min(ts_utc_tz) as first_bar_ts_utc,
        max(ts_utc_tz) as last_bar_ts_utc,
        count(*) as extended_bar_count,
        sum(coalesce(v, 0)) as extended_volume,
        sum(coalesce(v, 0) * coalesce(vw, c)) as extended_dollar_volume,
        max(move_vs_prev_close_pct) as max_move_vs_prev_close_pct,
        max(move_vs_segment_open_pct) as max_move_vs_segment_open_pct,
        max(case when session_segment = 'premarket' then move_vs_prev_close_pct end) as premarket_high_vs_prev_close_pct,
        max(case when session_segment = 'regular' then move_vs_prev_close_pct end) as regular_high_vs_prev_close_pct,
        max(case when session_segment = 'afterhours' then move_vs_prev_close_pct end) as afterhours_high_vs_prev_close_pct,
        arg_max(session_segment, move_vs_prev_close_pct) as max_move_segment
    from metrics
    group by ticker, session_date
),
first_cross_candidates as (
    select
        *,
        row_number() over (
            partition by ticker, session_date
            order by ts_utc_tz
        ) as cross_rank
    from metrics
    where move_vs_prev_close_pct >= {threshold_pct}
),
first_cross as (
    select
        ticker,
        session_date,
        ts_utc_tz as first_cross_50_ts_utc,
        ts_et as first_cross_50_ts_et,
        session_segment as first_cross_50_segment,
        h as first_cross_price,
        move_vs_prev_close_pct as first_cross_move_vs_prev_close_pct,
        move_vs_segment_open_pct as first_cross_move_vs_segment_open_pct,
        volume_to_time as volume_to_time_at_first_cross,
        dollar_volume_to_time as dollar_volume_to_time_at_first_cross,
        bars_observed_to_time as bars_observed_to_first_cross,
        source_ohlcv_1m_file as first_cross_source_ohlcv_1m_file
    from first_cross_candidates
    where cross_rank = 1
),
final_rows as (
    select
        md5({scanner_run_id} || '|' || s.ticker || '|' || cast(s.session_date as varchar)) as intraday_scanner_candidate_id,
        {scanner_run_id} as scanner_run_id,
        {created_at_utc} as created_at_utc,
        '{DATASET_ID}' as dataset_id,
        '{SCHEMA_VERSION}' as schema_version,
        '{QUALITY_POLICY_VERSION}' as quality_policy_version,
        '{SCANNER_POLICY_VERSION}' as scanner_policy_version,
        '{SCANNER_DEFINITION_ID}' as scanner_definition_id,
        '{BASE_SCANNER_ID}' as base_scanner_definition_id,
        'candidate_replay' as materialization_scope,
        false as full_universe_claim,
        s.instrument_id,
        s.ticker,
        cast(s.session_date as date) as session_date,
        coalesce(f.first_cross_50_ts_utc, s.last_bar_ts_utc) as as_of_utc,
        'first_cross_when_selected_else_last_extended_bar_for_evaluated_rows' as as_of_policy,
        s.instrument_name,
        s.primary_exchange,
        s.exchange_acronym,
        s.active_in_reference,
        s.reference_last_updated_utc,
        s.is_common_stock as common_stock_filter_passed,
        s.market_cap_usd,
        s.market_cap_usd < {market_cap_max} as market_cap_filter_passed,
        s.shares_outstanding_context,
        cast(null as double) as float_shares,
        'float_context_table_not_materialized_point_in_time_float_unavailable' as float_unavailable_reason,
        s.prior_close,
        s.daily_open,
        s.daily_high,
        s.daily_low,
        s.daily_close,
        s.daily_volume,
        s.daily_dollar_volume,
        s.rvol_20d,
        s.gap_pct,
        s.daily_return_pct,
        s.family_data_quality_verdict,
        coalesce(s.data_present, false) as data_present,
        coalesce(s.backtest_core_row_candidate, false) as backtest_core_row_candidate,
        s.expected_session,
        s.expected_reason,
        s.first_bar_ts_utc,
        s.last_bar_ts_utc,
        s.extended_bar_count,
        s.extended_volume,
        s.extended_dollar_volume,
        s.max_move_vs_prev_close_pct,
        s.max_move_vs_segment_open_pct,
        s.premarket_high_vs_prev_close_pct,
        s.regular_high_vs_prev_close_pct,
        s.afterhours_high_vs_prev_close_pct,
        s.max_move_segment,
        f.first_cross_50_ts_utc,
        f.first_cross_50_ts_et,
        f.first_cross_50_segment,
        f.first_cross_price,
        f.first_cross_move_vs_prev_close_pct,
        f.first_cross_move_vs_segment_open_pct,
        f.volume_to_time_at_first_cross,
        f.dollar_volume_to_time_at_first_cross,
        f.bars_observed_to_first_cross,
        f.first_cross_source_ohlcv_1m_file,
        f.first_cross_50_ts_utc is not null as motion_threshold_passed,
        (
            coalesce(f.volume_to_time_at_first_cross, 0) >= {volume_min}
            or coalesce(f.dollar_volume_to_time_at_first_cross, 0) >= {dollar_min}
        ) as tradability_threshold_passed,
        (
            f.first_cross_price > {price_min}
            and f.first_cross_price <= {price_max}
        ) as price_filter_passed_at_first_cross,
        (
            s.is_common_stock
            and s.market_cap_usd < {market_cap_max}
            and s.family_data_quality_verdict in (
                'usable_for_declared_scope',
                'good',
                'review',
                'review_with_flag'
            )
            and coalesce(s.data_present, false)
        ) as base_eligible_smallcap_denominator_passed,
        (
            s.is_common_stock
            and s.market_cap_usd < {market_cap_max}
            and s.family_data_quality_verdict in (
                'usable_for_declared_scope',
                'good',
                'review',
                'review_with_flag'
            )
            and coalesce(s.data_present, false)
            and f.first_cross_50_ts_utc is not null
            and (
                coalesce(f.volume_to_time_at_first_cross, 0) >= {volume_min}
                or coalesce(f.dollar_volume_to_time_at_first_cross, 0) >= {dollar_min}
            )
            and f.first_cross_price > {price_min}
            and f.first_cross_price <= {price_max}
        ) as selected_intraday_in_play_candidate,
        case
            when (
                s.is_common_stock
                and s.market_cap_usd < {market_cap_max}
                and s.family_data_quality_verdict in (
                    'usable_for_declared_scope',
                    'good',
                    'review',
                    'review_with_flag'
                )
                and coalesce(s.data_present, false)
                and f.first_cross_50_ts_utc is not null
                and (
                    coalesce(f.volume_to_time_at_first_cross, 0) >= {volume_min}
                    or coalesce(f.dollar_volume_to_time_at_first_cross, 0) >= {dollar_min}
                )
                and f.first_cross_price > {price_min}
                and f.first_cross_price <= {price_max}
            ) then 'selected_intraday_in_play'
            when f.first_cross_50_ts_utc is not null then 'motion_threshold_seen_not_selected'
            when (
                s.is_common_stock
                and s.market_cap_usd < {market_cap_max}
                and s.family_data_quality_verdict in (
                    'usable_for_declared_scope',
                    'good',
                    'review',
                    'review_with_flag'
                )
                and coalesce(s.data_present, false)
            ) then 'base_eligible_not_in_play'
            else 'evaluated_not_base_eligible'
        end as scanner_selection_state,
        concat_ws('|',
            case when f.first_cross_50_ts_utc is not null then 'move_vs_prev_close_pct_gte_50' end,
            case when f.first_cross_50_segment = 'premarket' then 'first_cross_premarket' end,
            case when f.first_cross_50_segment = 'regular' then 'first_cross_regular' end,
            case when f.first_cross_50_segment = 'afterhours' then 'first_cross_afterhours' end,
            case when coalesce(f.volume_to_time_at_first_cross, 0) >= {volume_min} then 'volume_to_time_gte_min' end,
            case when coalesce(f.dollar_volume_to_time_at_first_cross, 0) >= {dollar_min} then 'dollar_volume_to_time_gte_min' end
        ) as candidate_reasons,
        {source_minute_root} as source_ohlcv_1m_root,
        {source_master_root} as source_master_daily_root,
        {source_master_manifest} as source_master_daily_manifest,
        {source_instrument_manifest} as source_instrument_master_manifest,
        {source_market_calendar_manifest} as source_market_calendar_manifest,
        s.master_daily_build_run_id
    from session_agg s
    left join first_cross f
      on s.ticker = f.ticker
     and cast(s.session_date as date) = cast(f.session_date as date)
)
select *
from final_rows;
"""


def _write_summary_csv(path: Path, stats: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for key, value in stats.items():
            writer.writerow([key, value])


def _build(args: argparse.Namespace) -> dict[str, Any]:
    _validate_args(args)
    minute_files = _minute_files(args.minute_root, args.start_date, args.end_date)
    if not minute_files:
        raise FileNotFoundError(
            f"No OHLCV 1m parquet files found for {args.start_date}..{args.end_date} "
            f"under {args.minute_root}"
        )

    if args.output_root.exists() and args.overwrite:
        shutil.rmtree(args.output_root)
    args.output_root.mkdir(parents=True, exist_ok=True)

    dataset_root = args.output_root / DATASET_DIR_NAME
    dataset_root.mkdir(parents=True, exist_ok=True)
    dataset_path = dataset_root / "data.parquet"
    manifest_path = args.output_root / "_intraday_scanner_candidates_table_manifest_v0_1_candidate_replay.json"
    summary_path = args.output_root / "_intraday_scanner_candidates_table_summary_v0_1_candidate_replay.csv"
    run_summary_path = args.output_root / "_run_summary.json"

    config_paths = _scanner_config_paths(args.scanner_definitions_dir)
    configs = {path.stem: _read_yaml(path) for path in config_paths}

    con = duckdb.connect()
    sql = _build_sql(args, configs, minute_files)
    con.execute(sql)

    con.execute(
        f"COPY intraday_scanner_rows TO {_sql_literal(_as_posix(dataset_path))} "
        "(FORMAT PARQUET, COMPRESSION ZSTD)"
    )

    stats = con.sql(
        """
        select
            count(*) as rows,
            count(distinct ticker) as tickers,
            count(distinct session_date) as session_dates,
            sum(cast(base_eligible_smallcap_denominator_passed as integer)) as base_eligible_rows,
            sum(cast(motion_threshold_passed as integer)) as motion_threshold_rows,
            sum(cast(tradability_threshold_passed as integer)) as tradability_pass_rows,
            sum(cast(selected_intraday_in_play_candidate as integer)) as selected_intraday_in_play_candidate_rows,
            min(first_cross_move_vs_prev_close_pct) filter (where selected_intraday_in_play_candidate) as min_selected_first_cross_move_pct,
            max(first_cross_move_vs_prev_close_pct) filter (where selected_intraday_in_play_candidate) as max_selected_first_cross_move_pct,
            sum(cast(first_cross_50_segment = 'premarket' as integer)) as first_cross_premarket_rows,
            sum(cast(first_cross_50_segment = 'regular' as integer)) as first_cross_regular_rows,
            sum(cast(first_cross_50_segment = 'afterhours' as integer)) as first_cross_afterhours_rows
        from intraday_scanner_rows
        """
    ).fetchone()
    columns = [
        "rows",
        "tickers",
        "session_dates",
        "base_eligible_rows",
        "motion_threshold_rows",
        "tradability_pass_rows",
        "selected_intraday_in_play_candidate_rows",
        "min_selected_first_cross_move_pct",
        "max_selected_first_cross_move_pct",
        "first_cross_premarket_rows",
        "first_cross_regular_rows",
        "first_cross_afterhours_rows",
    ]
    stats_dict = dict(zip(columns, stats, strict=True))

    duplicate_count = con.sql(
        """
        select count(*)
        from (
            select ticker, session_date, count(*) as n
            from intraday_scanner_rows
            group by ticker, session_date
            having count(*) > 1
        )
        """
    ).fetchone()[0]
    stats_dict["duplicate_ticker_session_keys"] = duplicate_count
    stats_dict["source_ohlcv_1m_file_count"] = len(minute_files)
    stats_dict["full_universe_claim"] = False
    stats_dict["materialization_scope"] = "candidate_replay"

    _write_summary_csv(summary_path, stats_dict)
    tree_hash = _sha256_parquet_tree(dataset_root)
    manifest = {
        "dataset_id": DATASET_ID,
        "dataset_dir_name": DATASET_DIR_NAME,
        "schema_version": SCHEMA_VERSION,
        "scanner_definition_id": SCANNER_DEFINITION_ID,
        "base_scanner_definition_id": BASE_SCANNER_ID,
        "scanner_policy_version": SCANNER_POLICY_VERSION,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "run_id": args.run_id,
        "created_at_utc": args.created_at_utc,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "price_view": args.price_view,
        "materialization_scope": "candidate_replay",
        "full_universe_claim": False,
        "output_root": _as_posix(args.output_root),
        "dataset_path": _as_posix(dataset_path),
        "summary_path": _as_posix(summary_path),
        "source_roots": {
            "ohlcv_1m": _as_posix(args.minute_root),
            "master_daily": _as_posix(args.master_daily_root),
            "instrument_master": _as_posix(args.instrument_master),
            "market_calendar": _as_posix(args.market_calendar),
        },
        "source_manifests": {
            "master_daily": _as_posix(args.master_daily_manifest),
            "instrument_master": _as_posix(args.instrument_master_manifest),
            "market_calendar": _as_posix(args.market_calendar_manifest),
        },
        "scanner_configs": [_as_posix(path) for path in config_paths],
        "contract_refs": CONTRACTS,
        "stats": stats_dict,
        "parquet_tree": tree_hash,
        "notes": [
            "This table is intraday candidate detection, not market_state, event_state, label, reward or strategy signal.",
            "Selection is based on first 1m bar crossing +50% vs previous close in extended hours 04:00-20:00 New York.",
            "Float is not used as a filter because point-in-time float_context_table is not materialized.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    run_summary = {
        "run_id": args.run_id,
        "status": "completed",
        "dataset_id": DATASET_ID,
        "created_at_utc": args.created_at_utc,
        "completed_at_utc": _utc_now(),
        "manifest_path": _as_posix(manifest_path),
        "dataset_path": _as_posix(dataset_path),
        "summary_path": _as_posix(summary_path),
        "stats": stats_dict,
    }
    run_summary_path.write_text(json.dumps(run_summary, indent=2, sort_keys=True), encoding="utf-8")
    return run_summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize intraday_scanner_candidates_table_v0_1 candidate replay."
    )
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--minute-root", type=Path, default=DEFAULT_MINUTE_ROOT)
    parser.add_argument("--master-daily-root", type=Path, default=DEFAULT_MASTER_DAILY_ROOT)
    parser.add_argument("--master-daily-manifest", type=Path, default=DEFAULT_MASTER_DAILY_MANIFEST)
    parser.add_argument("--instrument-master", type=Path, default=DEFAULT_INSTRUMENT_MASTER)
    parser.add_argument("--instrument-master-manifest", type=Path, default=DEFAULT_INSTRUMENT_MANIFEST)
    parser.add_argument("--market-calendar", type=Path, default=DEFAULT_MARKET_CALENDAR)
    parser.add_argument("--market-calendar-manifest", type=Path, default=DEFAULT_MARKET_CALENDAR_MANIFEST)
    parser.add_argument("--scanner-definitions-dir", type=Path, default=DEFAULT_SCANNER_DEFINITIONS_DIR)
    parser.add_argument("--price-view", default="daily_raw")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    args.run_id = args.run_id or _run_id()
    args.created_at_utc = _utc_now()
    args.output_root = args.output_root or _default_output_root(args.run_id)
    result = _build(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
