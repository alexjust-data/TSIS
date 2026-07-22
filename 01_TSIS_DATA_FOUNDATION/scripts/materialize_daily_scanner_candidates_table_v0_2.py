from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import yaml


MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parent

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

CONTRACTS = {
    "schema": "01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md",
    "target_contract": (
        "01_foundations/module_contracts/outputs/"
        "daily_scanner_candidates_table_target_contract_v0_2.md"
    ),
    "dataset_contract": (
        "01_foundations/contract_registry/dataset_contracts/"
        "daily_scanner_candidates_table_dataset_contract_v0_1.md"
    ),
    "consumption_policy": (
        "01_foundations/data_consumption_policies/"
        "daily_scanner_candidates_table_consumption_policy.md"
    ),
    "registry": "01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml",
    "validators": "01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md",
    "scanner_framework": (
        "01_foundations/module_contracts/outputs/"
        "scanner_framework_and_definitions_contract_v0_2.md"
    ),
}

DATASET_ID = "daily_scanner_candidates_table_v0_2"
DATASET_DIR_NAME = "daily_scanner_candidates_table_v0_2_candidate_replay"
SCHEMA_VERSION = "daily_scanner_candidates_table_v0_2_candidate_extension"
QUALITY_POLICY_VERSION = "daily_scanner_candidates_table_policy_v0_2"
SCANNER_POLICY_VERSION = "scanner_framework_v0_2"
SCANNER_SEMANTIC_ALIGNMENT_VERSION = "v0_2_1_contract_aligned"
BASE_SCANNER_ID = "base_in_play_universe_scanner_v0_2"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id() -> str:
    return "daily_scanner_candidates_replay_v0_2_" + datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def _as_posix(path: Path) -> str:
    return path.as_posix()


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


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


def _scanner_config_paths(scanner_definitions_dir: Path) -> list[Path]:
    paths = [
        scanner_definitions_dir / "base_in_play_universe_scanner_v0_2.yaml",
        scanner_definitions_dir / "trade_station_like_profile_v0_2.yaml",
        scanner_definitions_dir / "relative_volume_profile_v0_2.yaml",
        scanner_definitions_dir / "percent_change_profile_v0_2.yaml",
        scanner_definitions_dir / "dollar_volume_tradability_profile_v0_2.yaml",
        scanner_definitions_dir / "das_research_profile_v0_2.yaml",
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


def _build_sql(args: argparse.Namespace, configs: dict[str, dict[str, Any]]) -> str:
    master_glob = _as_posix(args.master_daily_root / "**" / "*.parquet")
    instrument_path = _as_posix(args.instrument_master)
    calendar_path = _as_posix(args.market_calendar)

    base_cfg = configs["base_in_play_universe_scanner_v0_2"]
    ts_profile = configs["trade_station_like_profile_v0_2"]
    pct_profile = configs["percent_change_profile_v0_2"]
    dollar_profile = configs["dollar_volume_tradability_profile_v0_2"]
    das_profile = configs["das_research_profile_v0_2"]

    eligibility = base_cfg["base_universe_eligibility"]
    market_cap_max = float(eligibility["market_cap_max_usd"])
    price_min = float(eligibility["last_price_min_exclusive"])
    price_max = float(eligibility["last_price_max_inclusive"])

    ts_volume_min = float(ts_profile["hard_filters"]["volume_today_min"])
    ts_top_n = int(ts_profile["ranking"]["top_n"])
    pct_top_n = int(pct_profile["ranking"]["top_n"])
    dollar_top_n = int(dollar_profile["ranking"]["top_n"])
    das_top_n = int(das_profile["selection_sets"]["top_n_by_composite_in_play_score"])

    pct_threshold = float(pct_profile["thresholds"]["reason_pct_chg_1d_move_min_pct"])
    gap_threshold = float(das_profile["in_play_reasons"]["reason_gap_pct_move"]["threshold_pct"])
    dollar_min = float(dollar_profile["thresholds"]["min_dollar_volume_to_time"])

    scanner_run_id = _sql_literal(args.run_id)
    created_at_utc = _sql_literal(args.created_at_utc)
    price_view = _sql_literal(args.price_view)
    start_date = _sql_literal(args.start_date)
    end_date = _sql_literal(args.end_date)
    source_master_path = _sql_literal(_as_posix(args.master_daily_root))
    source_master_manifest = _sql_literal(_as_posix(args.master_daily_manifest))
    source_instrument_manifest = _sql_literal(_as_posix(args.instrument_master_manifest))
    source_market_calendar_manifest = _sql_literal(_as_posix(args.market_calendar_manifest))

    profile_ids = "|".join(
        [
            "trade_station_like_profile_v0_2",
            "relative_volume_profile_v0_2",
            "percent_change_profile_v0_2",
            "dollar_volume_tradability_profile_v0_2",
            "das_research_profile_v0_2",
        ]
    )

    return f"""
create or replace table scanner_rows as
with master_daily_source as (
    select *
    from read_parquet('{master_glob}', hive_partitioning=true)
    where price_view = {price_view}
      and cast(session_date as date) between cast({start_date} as date) and cast({end_date} as date)
),
master_daily_dedup as (
    select * exclude (rn)
    from (
        select
            *,
            row_number() over (
                partition by instrument_id, cast(session_date as date), price_view
                order by
                    coalesce(data_present, false) desc,
                    coalesce(backtest_core_row_candidate, false) desc,
                    dollar_volume desc nulls last,
                    ticker asc
            ) as rn
        from master_daily_source
    )
    where rn = 1
),
instrument_master_dedup as (
    select * exclude (rn)
    from (
        select
            *,
            row_number() over (
                partition by instrument_id
                order by
                    coalesce(active_in_reference, false) desc,
                    reference_last_updated_utc desc nulls last,
                    overview_request_date desc nulls last,
                    ticker asc
            ) as rn
        from read_parquet('{instrument_path}')
    )
    where rn = 1
),
market_calendar_dedup as (
    select * exclude (rn)
    from (
        select
            *,
            row_number() over (
                partition by cast(session_date as date)
                order by close_utc desc nulls last
            ) as rn
        from read_parquet('{calendar_path}')
    )
    where rn = 1
),
base_raw as (
    select
        d.master_daily_id,
        d.instrument_id,
        d.ticker,
        cast(d.session_date as date) as session_date,
        d.price_view,
        d.open as open_price,
        d.close as last_price,
        d.prior_close as previous_close,
        d.volume as volume_today,
        d.dollar_volume as dollar_volume_today,
        d.volume as volume_to_time,
        d.volume as volume_since_04_00,
        cast(null as double) as volume_last_5m,
        cast(null as double) as volume_last_15m,
        d.dollar_volume as dollar_volume_to_time,
        d.rvol_20d as volume_acceleration,
        d.rvol_20d as rvol_to_time,
        d.daily_return_pct * 100.0 as pct_chg_1d,
        d.gap_pct * 100.0 as gap_pct,
        d.daily_range_pct * 100.0 as daily_range_pct,
        d.data_present,
        d.family_data_quality_verdict,
        d.backtest_core_row_candidate,
        d.build_run_id as source_master_daily_table_build_run_id,
        coalesce(i.is_common_stock, false) as is_common_stock,
        coalesce(i.is_lt1b_operational, false) as is_lt1b_operational,
        coalesce(i.lt1b_market_cap_t, i.overview_market_cap) as market_cap_usd,
        cast(coalesce(i.lt1b_anchor_date_used, i.lt1b_shares_observed_date, i.overview_request_date) as varchar)
            as market_cap_asof_date,
        case
            when i.lt1b_market_cap_t is not null then 'lt1b_market_cap_t'
            when i.overview_market_cap is not null then 'overview_market_cap'
            else 'missing'
        end as market_cap_source,
        coalesce(i.primary_exchange, i.exchange_acronym, 'UNKNOWN') as exchange,
        i.build_run_id as source_instrument_master_build_run_id,
        cast(c.close_utc as varchar) as as_of_utc,
        c.build_run_id as source_market_calendar_build_run_id,
        c.calendar as source_calendar,
        c.timezone as source_calendar_timezone
    from master_daily_dedup d
    left join instrument_master_dedup i
        on d.instrument_id = i.instrument_id
    left join market_calendar_dedup c
        on cast(d.session_date as date) = cast(c.session_date as date)
),
base as (
    select
        *,
        data_present
            and last_price is not null
            and previous_close is not null
            and volume_today is not null
            and market_cap_usd is not null
            and as_of_utc is not null as scanner_input_available,
        coalesce(family_data_quality_verdict, '') in (
            'usable_for_declared_scope', 'good', 'review', 'review_with_flag'
        ) as source_quality_allowed,
        is_common_stock as asset_type_filter_passed,
        last_price > {price_min} and last_price <= {price_max} as price_filter_passed,
        market_cap_usd < {market_cap_max} as market_cap_filter_passed,
        volume_today >= {ts_volume_min} as trade_station_volume_filter_passed,
        true as exchange_filter_passed,
        case
            when volume_today is null then 'missing'
            when volume_today < 100000 then 'lt_100k'
            when volume_today < 250000 then '100k_250k'
            when volume_today < 500000 then '250k_500k'
            when volume_today < 1000000 then '500k_1m'
            else 'gt_1m'
        end as volume_tier,
        coalesce(pct_chg_1d, 0.0)
            + coalesce(gap_pct, 0.0) * 0.25
            + least(coalesce(rvol_to_time, 0.0), 100.0) * 2.0
            + case
                when dollar_volume_to_time > 0 then ln(dollar_volume_to_time + 1.0) / ln(10.0)
                else 0.0
            end as composite_in_play_score
    from base_raw
),
reasoned as (
    select
        *,
        asset_type_filter_passed
            and price_filter_passed
            and market_cap_filter_passed
            and source_quality_allowed as base_all_filters_passed,
        pct_chg_1d >= {pct_threshold} as reason_pct_chg_1d_move,
        gap_pct >= {gap_threshold} as reason_gap_pct_move,
        false as reason_volume_acceleration,
        false as reason_rvol_to_time,
        false as reason_afterhours_breakout,
        false as reason_premarket_new_high,
        false as reason_prior_day_high_reclaim,
        false as reason_unusual_range_expansion,
        false as reason_news_context,
        false as reason_halt_or_reopen_context
    from base
    where scanner_input_available
),
rank_inputs as (
    select *
    from reasoned
    where base_all_filters_passed
),
rank_pct as (
    select
        master_daily_id,
        row_number() over (
            partition by session_date
            order by pct_chg_1d desc nulls last, dollar_volume_today desc nulls last, ticker asc
        ) as rank_pct_chg_1d
    from rank_inputs
),
rank_rvol as (
    select
        master_daily_id,
        row_number() over (
            partition by session_date
            order by rvol_to_time desc nulls last, pct_chg_1d desc nulls last, ticker asc
        ) as rank_rvol_to_time
    from rank_inputs
),
rank_volume_accel as (
    select
        master_daily_id,
        row_number() over (
            partition by session_date
            order by volume_acceleration desc nulls last, dollar_volume_today desc nulls last, ticker asc
        ) as rank_volume_acceleration
    from rank_inputs
),
rank_dollar as (
    select
        master_daily_id,
        row_number() over (
            partition by session_date
            order by dollar_volume_to_time desc nulls last, pct_chg_1d desc nulls last, ticker asc
        ) as rank_dollar_volume_to_time
    from rank_inputs
),
rank_composite as (
    select
        master_daily_id,
        row_number() over (
            partition by session_date
            order by composite_in_play_score desc nulls last, ticker asc
        ) as rank_composite_in_play
    from rank_inputs
),
ts_rank as (
    select
        master_daily_id,
        row_number() over (
            partition by session_date
            order by pct_chg_1d desc nulls last, dollar_volume_today desc nulls last, ticker asc
        ) as trade_station_rank_pct_chg_1d
    from rank_inputs
    where trade_station_volume_filter_passed
),
joined as (
    select
        r.*,
        p.rank_pct_chg_1d,
        va.rank_volume_acceleration,
        d.rank_dollar_volume_to_time,
        rv.rank_rvol_to_time,
        c.rank_composite_in_play,
        ts.trade_station_rank_pct_chg_1d
    from reasoned r
    left join rank_pct p using (master_daily_id)
    left join rank_volume_accel va using (master_daily_id)
    left join rank_dollar d using (master_daily_id)
    left join rank_rvol rv using (master_daily_id)
    left join rank_composite c using (master_daily_id)
    left join ts_rank ts using (master_daily_id)
),
profiled as (
    select
        *,
        base_all_filters_passed
            and trade_station_volume_filter_passed
            and trade_station_rank_pct_chg_1d <= {ts_top_n}
            as selected_trade_station_like_profile,
        base_all_filters_passed
            and reason_pct_chg_1d_move
            and rank_pct_chg_1d <= {pct_top_n}
            as selected_percent_change_profile,
        false as selected_relative_volume_profile,
        base_all_filters_passed
            and dollar_volume_to_time >= {dollar_min}
            and rank_dollar_volume_to_time <= {dollar_top_n}
            as selected_dollar_volume_tradability_profile,
        base_all_filters_passed
            and (
                reason_pct_chg_1d_move
                or reason_gap_pct_move
                or rank_composite_in_play <= {das_top_n}
            ) as selected_das_research_profile
    from joined
),
with_reasons as (
    select
        *,
        nullif(concat_ws('|',
            case when reason_pct_chg_1d_move then 'reason_pct_chg_1d_move' end,
            case when reason_gap_pct_move then 'reason_gap_pct_move' end,
            case when reason_volume_acceleration then 'reason_volume_acceleration' end,
            case when reason_rvol_to_time then 'reason_rvol_to_time' end,
            case when reason_afterhours_breakout then 'reason_afterhours_breakout' end,
            case when reason_premarket_new_high then 'reason_premarket_new_high' end,
            case when reason_prior_day_high_reclaim then 'reason_prior_day_high_reclaim' end,
            case when reason_unusual_range_expansion then 'reason_unusual_range_expansion' end,
            case when reason_news_context then 'reason_news_context' end,
            case when reason_halt_or_reopen_context then 'reason_halt_or_reopen_context' end,
            case when selected_trade_station_like_profile then 'profile_trade_station_like_top25' end,
            case when selected_percent_change_profile then 'profile_percent_change_top_n' end,
            case when selected_relative_volume_profile then 'profile_relative_volume_top_n' end,
            case when selected_dollar_volume_tradability_profile then 'profile_dollar_volume_tradability' end,
            case when selected_das_research_profile then 'profile_das_research_candidate' end
        ), '') as candidate_reasons,
        (
            case when reason_pct_chg_1d_move then 1 else 0 end
            + case when reason_gap_pct_move then 1 else 0 end
            + case when reason_volume_acceleration then 1 else 0 end
            + case when reason_rvol_to_time then 1 else 0 end
            + case when reason_afterhours_breakout then 1 else 0 end
            + case when reason_premarket_new_high then 1 else 0 end
            + case when reason_prior_day_high_reclaim then 1 else 0 end
            + case when reason_unusual_range_expansion then 1 else 0 end
            + case when reason_news_context then 1 else 0 end
            + case when reason_halt_or_reopen_context then 1 else 0 end
            + case when selected_trade_station_like_profile then 1 else 0 end
            + case when selected_percent_change_profile then 1 else 0 end
            + case when selected_relative_volume_profile then 1 else 0 end
            + case when selected_dollar_volume_tradability_profile then 1 else 0 end
            + case when selected_das_research_profile then 1 else 0 end
        ) as candidate_reason_count,
        (
            selected_trade_station_like_profile
            or selected_percent_change_profile
            or selected_relative_volume_profile
            or selected_dollar_volume_tradability_profile
            or selected_das_research_profile
        ) as selected_any_profile
    from profiled
),
with_counts as (
    select
        *,
        count(*) over (partition by session_date) as population_denominator_count,
        count(*) over (partition by session_date) as evaluated_candidate_count,
        sum(case when selected_any_profile then 1 else 0 end) over (partition by session_date)
            as selected_candidate_count
    from with_reasons
)
select
    md5({scanner_run_id} || '|' || '{BASE_SCANNER_ID}' || '|' || cast(session_date as varchar)
        || '|' || coalesce(as_of_utc, '') || '|' || instrument_id) as scanner_candidate_id,
    {scanner_run_id} as scanner_run_id,
    '{BASE_SCANNER_ID}' as scanner_definition_id,
    'v0_2' as scanner_definition_version,
    'daily_in_play' as scanner_family,
    'smallcap_base_in_play_profile_scanner' as scanner_name,
    'historical_replay' as scanner_mode,
    'base_universe_plus_profiles' as scanner_role,
    instrument_id,
    ticker,
    session_date,
    as_of_utc,
    'America/New_York' as market_timezone,
    exchange,
    is_common_stock,
    is_lt1b_operational,
    'smallcap_common_stock_under_100m_daily_in_play_v0_2' as universe_definition_id,
    'smallcap_common_stock_under_100m_daily_in_play_v0_2' as base_universe_definition_id,
    'v0_2' as base_universe_definition_version,
    'scanner_profile_set_v0_2' as scanner_profile_set_id,
    '{profile_ids}' as scanner_profile_ids,
    '{SCANNER_SEMANTIC_ALIGNMENT_VERSION}' as scanner_semantic_alignment_version,
    'base_eligible_smallcap_denominator' as base_denominator_semantic_id,
    'parallel_flags_not_sequential_filters' as scanner_profile_semantics,
    false as profiles_are_sequential_funnel,
    'unavailable_without_intraday_asof' as relative_volume_profile_status,
    true as percent_change_min_threshold_applied,
    {pct_threshold}::double as percent_change_min_threshold_pct,
    'tradability_not_alpha' as dollar_volume_profile_semantic_role,
    'provisional_strategy_overlay_seed_not_final_scanner' as das_research_profile_status,
    'controlled_daily_replay' as population_scope,
    population_denominator_count,
    evaluated_candidate_count,
    selected_candidate_count,
    false as full_universe_claim,
    {das_top_n}::integer as top_n,
    rank_composite_in_play as rank,
    'composite_in_play_score' as rank_metric,
    composite_in_play_score as rank_metric_value,
    rank_composite_in_play <= {das_top_n} as included_in_top_n,
    rank_pct_chg_1d,
    rank_volume_acceleration,
    rank_dollar_volume_to_time,
    rank_rvol_to_time,
    rank_composite_in_play,
    selected_trade_station_like_profile as selected_trade_station_like_top25,
    selected_das_research_profile as selected_broad_discovery,
    selected_percent_change_profile as selected_by_pct_chg_rank,
    selected_relative_volume_profile as selected_by_volume_acceleration_rank,
    selected_dollar_volume_tradability_profile as selected_by_dollar_volume_rank,
    selected_das_research_profile as selected_by_composite_in_play_rank,
    selected_trade_station_like_profile,
    selected_relative_volume_profile,
    selected_percent_change_profile,
    selected_dollar_volume_tradability_profile,
    selected_das_research_profile,
    selected_any_profile,
    market_cap_usd,
    market_cap_asof_date,
    market_cap_source,
    'not_used_until_point_in_time_float_source_exists' as float_filter_state,
    cast(null as double) as float_shares,
    cast(null as varchar) as float_asof_date,
    cast(null as varchar) as float_source,
    last_price,
    previous_close,
    open_price,
    pct_chg_1d,
    gap_pct,
    volume_today,
    dollar_volume_today,
    volume_to_time,
    volume_since_04_00,
    volume_last_5m,
    volume_last_15m,
    volume_acceleration,
    dollar_volume_to_time,
    rvol_to_time,
    volume_tier,
    {price_min}::double as price_min_filter,
    {price_max}::double as price_max_filter,
    {ts_volume_min}::double as volume_min_filter,
    {market_cap_max}::double as market_cap_max_filter,
    price_filter_passed,
    trade_station_volume_filter_passed as volume_filter_passed,
    market_cap_filter_passed,
    asset_type_filter_passed,
    exchange_filter_passed,
    base_all_filters_passed as all_filters_passed,
    candidate_reasons,
    candidate_reason_count,
    reason_pct_chg_1d_move,
    reason_gap_pct_move,
    reason_volume_acceleration,
    reason_rvol_to_time,
    reason_afterhours_breakout,
    reason_premarket_new_high,
    reason_prior_day_high_reclaim,
    reason_unusual_range_expansion,
    reason_news_context,
    reason_halt_or_reopen_context,
    {source_master_path} as source_master_daily_table_path,
    source_master_daily_table_build_run_id,
    source_instrument_master_build_run_id,
    source_market_calendar_build_run_id,
    cast(null as varchar) as source_intraday_table_path,
    cast(null as varchar) as source_intraday_table_build_run_id,
    cast(null as varchar) as source_live_snapshot_id,
    cast(null as varchar) as source_vendor,
    cast(null as varchar) as source_vendor_dataset,
    cast(null as varchar) as source_snapshot_received_at_utc,
    cast(null as bigint) as source_snapshot_latency_ms,
    {source_master_manifest} as source_manifest,
    case
        when not source_quality_allowed then 'review'
        when not base_all_filters_passed then 'review'
        else 'good'
    end as scanner_quality_state,
    true as scanner_replayable,
    true as requires_asof_filter,
    false as contains_future_information_without_event_filter,
    'daily_eod_replay_available' as data_availability_state,
    market_cap_asof_date is null as market_cap_stale_flag,
    last_price is not null as price_available,
    volume_today is not null as volume_available,
    instrument_id is not null as instrument_identity_temporal_match,
    as_of_utc is not null as calendar_session_valid,
    selected_any_profile as valid_for_event_discovery_candidate,
    selected_any_profile as valid_for_market_state_seed_candidate,
    true as valid_for_sampling_lineage,
    false as valid_for_ml_feature_candidate,
    false as valid_for_rl_state_candidate,
    false as valid_for_live_downstream_candidate,
    case
        when not base_all_filters_passed then 'evaluated_not_base_eligible'
        when selected_any_profile and rank_composite_in_play <= {das_top_n} then 'selected_in_top_n'
        when selected_any_profile then 'selected_by_profile_without_composite_top_n'
        else 'base_eligible_not_selected'
    end as scanner_selection_state,
    false as manual_research_seed,
    true as historical_replay_candidate,
    false as live_scanner_candidate,
    selected_any_profile and not (rank_composite_in_play <= {das_top_n})
        as selected_by_threshold_without_top_n,
    source_calendar,
    source_calendar_timezone,
    '{SCHEMA_VERSION}' as schema_version,
    '{QUALITY_POLICY_VERSION}' as quality_policy_version,
    '{SCANNER_POLICY_VERSION}' as scanner_policy_version,
    {scanner_run_id} as build_run_id,
    {created_at_utc} as created_at_utc,
    {source_instrument_manifest} as source_instrument_manifest,
    {source_market_calendar_manifest} as source_market_calendar_manifest
from with_counts
order by session_date, selected_any_profile desc, rank_composite_in_play nulls last, ticker
"""


def _write_summary(con: duckdb.DuckDBPyConnection, path: Path) -> list[dict[str, Any]]:
    rows = con.sql(
        """
        select
            scanner_definition_id,
            min(session_date)::varchar as first_session,
            max(session_date)::varchar as last_session,
            count(*)::bigint as rows,
            count(distinct session_date)::integer as sessions,
            count(distinct instrument_id)::integer as instruments,
            sum(case when selected_any_profile then 1 else 0 end)::bigint as selected_rows,
            sum(case when selected_trade_station_like_profile then 1 else 0 end)::bigint
                as trade_station_like_profile_rows,
            sum(case when selected_relative_volume_profile then 1 else 0 end)::bigint
                as relative_volume_profile_rows,
            sum(case when selected_percent_change_profile then 1 else 0 end)::bigint
                as percent_change_profile_rows,
            sum(case when selected_dollar_volume_tradability_profile then 1 else 0 end)::bigint
                as dollar_volume_tradability_profile_rows,
            sum(case when selected_das_research_profile then 1 else 0 end)::bigint
                as das_research_profile_rows,
            sum(case when selected_any_profile and volume_today < 500000 then 1 else 0 end)::bigint
                as selected_below_500k_volume_rows,
            sum(case when valid_for_ml_feature_candidate then 1 else 0 end)::bigint
                as ml_feature_candidate_rows,
            sum(case when valid_for_rl_state_candidate then 1 else 0 end)::bigint
                as rl_state_candidate_rows
        from scanner_rows
        group by 1
        order by 1
        """
    ).fetchall()
    columns = [
        "scanner_definition_id",
        "first_session",
        "last_session",
        "rows",
        "sessions",
        "instruments",
        "selected_rows",
        "trade_station_like_profile_rows",
        "relative_volume_profile_rows",
        "percent_change_profile_rows",
        "dollar_volume_tradability_profile_rows",
        "das_research_profile_rows",
        "selected_below_500k_volume_rows",
        "ml_feature_candidate_rows",
        "rl_state_candidate_rows",
    ]
    records = [dict(zip(columns, row)) for row in rows]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)
    return records


def _validations(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    row = con.sql(
        """
        with dupes as (
            select count(*)::bigint as duplicate_key_groups
            from (
                select scanner_run_id, scanner_definition_id, session_date, as_of_utc, instrument_id, count(*) as n
                from scanner_rows
                group by 1, 2, 3, 4, 5
                having count(*) > 1
            )
        )
        select
            count(*)::bigint as row_count,
            count(distinct scanner_definition_id)::integer as scanner_definition_count,
            count(distinct session_date)::integer as session_count,
            min(session_date)::varchar as first_session,
            max(session_date)::varchar as last_session,
            count(distinct instrument_id)::integer as instrument_count,
            sum(case when scanner_selection_state = 'evaluated_not_base_eligible' then 1 else 0 end)::bigint
                as evaluated_not_base_eligible_rows,
            sum(case when scanner_selection_state = 'base_eligible_not_selected' then 1 else 0 end)::bigint
                as base_eligible_not_selected_rows,
            sum(case when selected_any_profile then 1 else 0 end)::bigint as selected_any_profile_rows,
            sum(case when selected_trade_station_like_profile then 1 else 0 end)::bigint
                as selected_trade_station_like_profile_rows,
            sum(case when selected_relative_volume_profile then 1 else 0 end)::bigint
                as selected_relative_volume_profile_rows,
            sum(case when selected_percent_change_profile then 1 else 0 end)::bigint
                as selected_percent_change_profile_rows,
            sum(case when selected_dollar_volume_tradability_profile then 1 else 0 end)::bigint
                as selected_dollar_volume_tradability_profile_rows,
            sum(case when selected_das_research_profile then 1 else 0 end)::bigint
                as selected_das_research_profile_rows,
            sum(case when selected_any_profile and volume_today < 500000 then 1 else 0 end)::bigint
                as selected_below_500k_volume_rows,
            sum(case when full_universe_claim then 1 else 0 end)::bigint as full_universe_claim_true_rows,
            sum(case when valid_for_ml_feature_candidate then 1 else 0 end)::bigint as ml_feature_candidate_rows,
            sum(case when valid_for_rl_state_candidate then 1 else 0 end)::bigint as rl_state_candidate_rows,
            sum(case when valid_for_live_downstream_candidate then 1 else 0 end)::bigint
                as live_downstream_candidate_rows,
            sum(case when contains_future_information_without_event_filter then 1 else 0 end)::bigint
                as future_information_flagged_rows,
            sum(case when float_filter_state <> 'not_used_until_point_in_time_float_source_exists' then 1 else 0 end)::bigint
                as float_filter_used_rows,
            (select duplicate_key_groups from dupes)::bigint as duplicate_key_groups
        from scanner_rows
        """
    ).fetchdf().iloc[0].to_dict()
    return {key: (value.item() if hasattr(value, "item") else value) for key, value in row.items()}


def _source_duplicate_alias_stats(con: duckdb.DuckDBPyConnection, args: argparse.Namespace) -> dict[str, Any]:
    master_glob = _as_posix(args.master_daily_root / "**" / "*.parquet")
    row = con.sql(
        f"""
        with source_rows as (
            select instrument_id, cast(session_date as date) as session_date, price_view
            from read_parquet('{master_glob}', hive_partitioning=true)
            where price_view = {_sql_literal(args.price_view)}
              and cast(session_date as date) between cast({_sql_literal(args.start_date)} as date)
                  and cast({_sql_literal(args.end_date)} as date)
        ),
        grouped as (
            select instrument_id, session_date, price_view, count(*) as n
            from source_rows
            group by 1, 2, 3
        )
        select
            (select count(*) from source_rows)::bigint as source_rows_before_dedup,
            count(*)::bigint as source_duplicate_alias_groups,
            coalesce(sum(n - 1), 0)::bigint as source_duplicate_alias_excess_rows,
            ((select count(*) from source_rows) - coalesce(sum(n - 1), 0))::bigint
                as source_rows_after_dedup_policy
        from grouped
        where n > 1
        """
    ).fetchdf().iloc[0].to_dict()
    return {key: (value.item() if hasattr(value, "item") else value) for key, value in row.items()}


def build(args: argparse.Namespace) -> dict[str, Any]:
    _validate_args(args)

    scanner_paths = _scanner_config_paths(args.scanner_definitions_dir)
    scanner_configs = {path.stem: _read_yaml(path) for path in scanner_paths}

    if args.output_root.exists() and args.overwrite:
        shutil.rmtree(args.output_root)
    args.output_root.mkdir(parents=True, exist_ok=True)
    dataset_dir = args.output_root / DATASET_DIR_NAME
    dataset_dir.mkdir(parents=True, exist_ok=True)
    output_parquet = dataset_dir / "data.parquet"
    summary_path = args.output_root / "_daily_scanner_candidates_table_summary_v0_2_candidate_replay.csv"
    manifest_path = args.output_root / "_daily_scanner_candidates_table_manifest_v0_2_candidate_replay.json"

    con = duckdb.connect()
    con.execute(_build_sql(args, scanner_configs))
    con.execute(f"copy scanner_rows to {_sql_literal(_as_posix(output_parquet))} (format parquet)")

    summary_records = _write_summary(con, summary_path)
    validations = _validations(con)
    validations.update(_source_duplicate_alias_stats(con, args))
    output_tree = _sha256_parquet_tree(dataset_dir)

    source_manifests = {
        "master_daily": _read_json(args.master_daily_manifest),
        "instrument_master": _read_json(args.instrument_master_manifest),
        "market_calendar": _read_json(args.market_calendar_manifest),
    }

    manifest = {
        "dataset_id": DATASET_ID,
        "physical_dataset_id": DATASET_DIR_NAME,
        "promotion_level": "controlled_replay_candidate",
        "status": "materialized_controlled_replay_not_official",
        "schema_version": SCHEMA_VERSION,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "scanner_policy_version": SCANNER_POLICY_VERSION,
        "scanner_semantic_alignment_version": SCANNER_SEMANTIC_ALIGNMENT_VERSION,
        "scanner_run_id": args.run_id,
        "build_run_id": args.run_id,
        "created_at_utc": args.created_at_utc,
        "output_path": str(dataset_dir),
        "manifest_path": str(manifest_path),
        "summary_path": str(summary_path),
        "output_tree": output_tree,
        "replay_scope": {
            "start_date": args.start_date,
            "end_date": args.end_date,
            "price_view": args.price_view,
            "as_of_policy": "session_close_utc_from_market_calendar",
            "intraday_decision_allowed": False,
            "full_universe_claim": False,
            "population_scope": "controlled_daily_replay",
        },
        "contract_alignment": {
            "base_denominator_semantics": "base_eligible_smallcap_denominator",
            "profile_semantics": "parallel_flags_not_sequential_filters",
            "relative_volume_profile_status": "unavailable_without_intraday_asof",
            "percent_change_min_threshold_applied": True,
            "percent_change_min_threshold_source": (
                "configs/data_foundation_outputs/scanner_definitions/"
                "percent_change_profile_v0_2.yaml"
            ),
            "dollar_volume_profile_semantic_role": "tradability_not_alpha",
            "das_research_profile_status": "provisional_strategy_overlay_seed_not_final_scanner",
            "strategy_overlays_allowed": True,
            "strategy_overlay_promotion_required_before_official_strategy_scanner": True,
        },
        "source_inputs": {
            "master_daily_root": str(args.master_daily_root),
            "master_daily_manifest": str(args.master_daily_manifest),
            "instrument_master": str(args.instrument_master),
            "instrument_master_manifest": str(args.instrument_master_manifest),
            "market_calendar": str(args.market_calendar),
            "market_calendar_manifest": str(args.market_calendar_manifest),
            "scanner_definitions_dir": str(args.scanner_definitions_dir),
        },
        "source_build_run_ids": {
            "master_daily": source_manifests["master_daily"].get("build_run_id"),
            "instrument_master": source_manifests["instrument_master"].get("build_run_id"),
            "market_calendar": source_manifests["market_calendar"].get("build_run_id"),
        },
        "scanner_definitions": {
            path.stem: {
                "path": str(path),
                "sha256": _sha256_file(path),
                "definition_id": scanner_configs[path.stem].get("scanner_definition_id")
                or scanner_configs[path.stem].get("profile_id"),
                "definition_version": scanner_configs[path.stem].get("scanner_definition_version")
                or scanner_configs[path.stem].get("profile_version"),
                "role": scanner_configs[path.stem].get("scanner_role")
                or scanner_configs[path.stem].get("profile_role"),
            }
            for path in scanner_paths
        },
        "contracts": CONTRACTS,
        "summary": summary_records,
        "validations": validations,
        "deduplication_policies": {
            "master_daily_grain": "instrument_id + session_date + price_view",
            "master_daily_policy": (
                "When source aliases create multiple ticker rows for the same instrument/session/price_view, "
                "keep one deterministic row ordered by data_present, backtest_core_row_candidate, "
                "dollar_volume desc and ticker asc."
            ),
            "instrument_master_grain": "instrument_id",
            "instrument_master_policy": (
                "Keep one deterministic dimensional row ordered by active_in_reference, "
                "reference_last_updated_utc, overview_request_date and ticker."
            ),
            "market_calendar_grain": "session_date",
            "market_calendar_policy": "Keep one deterministic session row ordered by close_utc desc.",
        },
        "limitations": [
            "This is a controlled daily EOD replay, not an intraday/live scanner.",
            "Afterhours, premarket, news and halt candidate reasons are false until scoped sources are joined.",
            "Relative-volume and volume-acceleration profiles require intraday/as-of bars; this replay marks them unavailable rather than using daily RVOL as a substitute.",
            "Percent-change selection requires the configured minimum threshold before ranking/top-N selection.",
            "Dollar-volume selection is a tradability/economic-activity profile, not an alpha or setup-quality signal.",
            "DAS fields are provisional strategy-overlay seed lineage, not a final DAS scanner.",
            "Float is not used as a hard filter because no point-in-time float source has passed coverage audit.",
            "Rows are candidate/evaluation rows only; they are not market states, labels, rewards, signals, orders, fills or PnL.",
            "ML/RL/live downstream flags remain false by contract.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize controlled daily scanner candidate replay v0.2."
    )
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--price-view", default="daily_raw")
    parser.add_argument("--run-id", default=_run_id())
    parser.add_argument("--created-at-utc", default=_utc_now())
    parser.add_argument("--master-daily-root", type=Path, default=DEFAULT_MASTER_DAILY_ROOT)
    parser.add_argument("--master-daily-manifest", type=Path, default=DEFAULT_MASTER_DAILY_MANIFEST)
    parser.add_argument("--instrument-master", type=Path, default=DEFAULT_INSTRUMENT_MASTER)
    parser.add_argument("--instrument-master-manifest", type=Path, default=DEFAULT_INSTRUMENT_MANIFEST)
    parser.add_argument("--market-calendar", type=Path, default=DEFAULT_MARKET_CALENDAR)
    parser.add_argument("--market-calendar-manifest", type=Path, default=DEFAULT_MARKET_CALENDAR_MANIFEST)
    parser.add_argument("--scanner-definitions-dir", type=Path, default=DEFAULT_SCANNER_DEFINITIONS_DIR)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    if args.output_root is None:
        args.output_root = _default_output_root(args.run_id)
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    manifest = build(args)
    validations = manifest["validations"]
    print("Daily scanner candidates replay v0.2 completed.")
    print(f"Run ID: {manifest['scanner_run_id']}")
    print(f"Output: {manifest['output_path']}")
    print(f"Manifest: {manifest['manifest_path']}")
    print(f"Summary: {manifest['summary_path']}")
    print(f"Rows: {validations['row_count']}")
    print(f"Selected any profile rows: {validations['selected_any_profile_rows']}")
    print(f"Selected TradeStation-like profile rows: {validations['selected_trade_station_like_profile_rows']}")
    print(f"Selected DAS research profile rows: {validations['selected_das_research_profile_rows']}")


if __name__ == "__main__":
    main()
