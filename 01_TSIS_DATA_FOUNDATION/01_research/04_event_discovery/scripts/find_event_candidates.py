"""Find exploratory event candidates in 1m OHLCV data.

This module is intentionally exploratory. It finds observable candidate moments;
it does not define promoted events, strategies, trades, or edge.
"""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import pyarrow.parquet as pq


AREA_ROOT = Path(__file__).resolve().parents[1]
MODULE_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_ROOT = Path(r"E:\TSIS\data\ohlcv_1m")
DEFAULT_REFERENCE_OVERVIEW_ROOT = Path(r"E:\TSIS\data\reference\overview")
DEFAULT_RUNS_ROOT = AREA_ROOT / "runs"
DEFAULT_LT1B_UNIVERSE_PATH = (
    MODULE_ROOT
    / "runs"
    / "backtest"
    / "market_cap_last_observed_cutoff"
    / "20260320_market_cap_last_observed_cutoff"
    / "market_cap_cutoff_lt_1b_active_inactive.parquet"
)
LT1B_UNIVERSE_DATASET_ID = "lt1b_universe_v0_1"
LT1B_UNIVERSE_RUN_ID = "20260320_market_cap_last_observed_cutoff"
LT1B_UNIVERSE_FILTER_POLICY = "ticker_plus_pti_window"
LT1B_UNIVERSE_ROWS = 4824
QUERY_NAME = "first_day_3bar_push_gt_20pct"
ET_TZ = "America/New_York"
TRADINGVIEW_EXCHANGE_PREFIX = {
    "XNAS": "NASDAQ",
    "XNYS": "NYSE",
    "ARCX": "AMEX",
    "XASE": "AMEX",
    "BATS": "BATS",
    "IEXG": "IEX",
}


@dataclass(frozen=True)
class FindConfig:
    data_root: str = str(DEFAULT_DATA_ROOT)
    reference_overview_root: str = str(DEFAULT_REFERENCE_OVERVIEW_ROOT)
    output_root: str = str(DEFAULT_RUNS_ROOT)
    universe_path: str = str(DEFAULT_LT1B_UNIVERSE_PATH)
    use_lt1b_universe: bool = True
    query_name: str = QUERY_NAME
    tickers: tuple[str, ...] = ()
    years: tuple[int, ...] = ()
    start_date: str | None = None
    end_date: str | None = None
    push_pct: float = 20.0
    min_session_volume: float = 500_000.0
    min_price: float = 0.5
    max_market_cap: float | None = 100_000_000.0
    missing_market_cap_policy: str = "exclude"
    session_scope: str = "premarket_regular"
    selection_mode: str = "first_push_of_day"
    price_view: str = "raw"
    require_rising_highs: bool = True
    require_close_above_prev_high: bool = True
    require_same_segment: bool = False
    max_candidates: int | None = None
    progress_every: int = 50
    partial_flush_every: int = 1
    workers: int = 1
    write_outputs: bool = True


def _parse_csv(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(part.strip().upper() for part in value.split(",") if part.strip())


def _parse_years(value: str | None) -> tuple[int, ...]:
    if not value:
        return ()
    years: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            years.extend(range(int(start), int(end) + 1))
        else:
            years.append(int(part))
    return tuple(sorted(set(years)))


def load_lt1b_universe(universe_path: Path) -> pd.DataFrame:
    required = {"ticker", "first_seen_date", "last_observed_date", "classification_1b"}
    schema_names = set(pq.ParquetFile(universe_path).schema_arrow.names)
    missing = required - schema_names
    if missing:
        raise ValueError(f"{universe_path} lacks required universe columns: {sorted(missing)}")

    df = pq.ParquetFile(universe_path).read(columns=sorted(required)).to_pandas()
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["first_seen_date"] = pd.to_datetime(df["first_seen_date"], errors="coerce")
    df["last_observed_date"] = pd.to_datetime(df["last_observed_date"], errors="coerce")
    df = df.dropna(subset=["ticker", "first_seen_date", "last_observed_date"])

    allowed_classes = {"active_lt_1b_last_classifiable", "inactive_died_lt_1b"}
    df = df[df["classification_1b"].isin(allowed_classes)].copy()
    df = df.drop_duplicates(subset=["ticker"], keep="last")
    return df.set_index("ticker", drop=False).sort_index()


def _iter_parquet_files(
    data_root: Path,
    tickers: Iterable[str],
    years: Iterable[int],
    universe: pd.DataFrame | None,
) -> Iterable[Path]:
    requested_ticker_filter = {t.upper() for t in tickers}
    ticker_filter = set(requested_ticker_filter)
    year_filter = {int(y) for y in years}
    if universe is not None:
        universe_tickers = set(universe.index.astype(str))
        if requested_ticker_filter:
            ticker_filter = requested_ticker_filter & universe_tickers
            if not ticker_filter:
                return
        else:
            ticker_filter = universe_tickers

    for ticker_dir in sorted(data_root.glob("ticker=*")):
        if not ticker_dir.is_dir():
            continue
        ticker = ticker_dir.name.split("=", 1)[-1].upper()
        if ticker_filter and ticker not in ticker_filter:
            continue

        year_dirs = sorted(ticker_dir.glob("year=*"))
        for year_dir in year_dirs:
            if not year_dir.is_dir():
                continue
            try:
                year = int(year_dir.name.split("=", 1)[-1])
            except ValueError:
                continue
            if year_filter and year not in year_filter:
                continue
            if universe is not None:
                row = universe.loc[ticker]
                first_year = int(row["first_seen_date"].year)
                last_year = int(row["last_observed_date"].year)
                if year < first_year or year > last_year:
                    continue
            yield from sorted(year_dir.glob("month=*/*.parquet"))


def _read_1m_file(path: Path, price_view: str) -> pd.DataFrame:
    schema_names = set(pq.ParquetFile(path).schema_arrow.names)
    base_cols = ["ticker", "ts_utc", "date", "o", "h", "l", "c", "v"]
    split_cols = [
        "o_split_normalized",
        "h_split_normalized",
        "l_split_normalized",
        "c_split_normalized",
        "vw_split_normalized",
    ]
    cols = [c for c in base_cols + split_cols if c in schema_names]
    table = pq.ParquetFile(path).read(columns=cols)
    df = table.to_pandas()
    if df.empty:
        return df

    if price_view == "split_normalized":
        required = {
            "o_split_normalized",
            "h_split_normalized",
            "l_split_normalized",
            "c_split_normalized",
        }
        if required.issubset(df.columns):
            df["px_o"] = df["o_split_normalized"]
            df["px_h"] = df["h_split_normalized"]
            df["px_l"] = df["l_split_normalized"]
            df["px_c"] = df["c_split_normalized"]
        else:
            raise ValueError(f"{path} lacks split-normalized price columns")
    elif price_view == "raw":
        df["px_o"] = df["o"]
        df["px_h"] = df["h"]
        df["px_l"] = df["l"]
        df["px_c"] = df["c"]
    else:
        raise ValueError(f"Unsupported price_view: {price_view}")

    df["ts_utc_dt"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce", format="ISO8601")
    df = df.dropna(subset=["ts_utc_dt", "px_o", "px_h", "px_l", "px_c", "v"]).copy()
    df["ts_et"] = df["ts_utc_dt"].dt.tz_convert(ET_TZ)
    df["session_date"] = df["ts_et"].dt.date.astype(str)
    df["session_segment"] = _session_segment(df["ts_et"])
    return df.sort_values("ts_utc_dt").reset_index(drop=True)


def _session_segment(ts_et: pd.Series) -> pd.Series:
    minutes = ts_et.dt.hour * 60 + ts_et.dt.minute
    pre_start = 4 * 60
    regular_start = 9 * 60 + 30
    regular_end = 16 * 60
    after_end = 20 * 60
    out = pd.Series("overnight", index=ts_et.index, dtype="object")
    out[(minutes >= pre_start) & (minutes < regular_start)] = "premarket"
    out[(minutes >= regular_start) & (minutes < regular_end)] = "regular"
    out[(minutes >= regular_end) & (minutes < after_end)] = "afterhours"
    return out


def _scope_mask(df: pd.DataFrame, session_scope: str) -> pd.Series:
    if session_scope == "premarket_regular":
        return df["session_segment"].isin(["premarket", "regular"])
    if session_scope == "full_extended":
        return df["session_segment"].isin(["premarket", "regular", "afterhours"])
    if session_scope == "regular":
        return df["session_segment"].eq("regular")
    if session_scope == "premarket":
        return df["session_segment"].eq("premarket")
    if session_scope == "afterhours":
        return df["session_segment"].eq("afterhours")
    if session_scope == "all":
        return pd.Series(True, index=df.index)
    raise ValueError(f"Unsupported session_scope: {session_scope}")


def _load_market_cap_history(overview_root: Path, ticker: str) -> pd.DataFrame:
    ticker_dir = overview_root / f"ticker={ticker.upper()}"
    files = sorted(ticker_dir.glob("*.parquet"))
    rows: list[pd.DataFrame] = []
    for path in files:
        schema_names = set(pq.ParquetFile(path).schema_arrow.names)
        if "request_date" not in schema_names:
            continue
        cols = [
            c
            for c in ["ticker", "market_cap", "request_date", "market", "primary_exchange", "name"]
            if c in schema_names
        ]
        df = pq.ParquetFile(path).read(columns=cols).to_pandas()
        if not df.empty:
            rows.append(df)
    if not rows:
        return pd.DataFrame(
            columns=["ticker", "market_cap", "request_date", "market", "primary_exchange", "name"]
        )
    hist = pd.concat(rows, ignore_index=True)
    hist["request_date"] = pd.to_datetime(hist["request_date"], errors="coerce").dt.date.astype(str)
    if "market_cap" not in hist.columns:
        hist["market_cap"] = pd.NA
    hist["market_cap"] = pd.to_numeric(hist["market_cap"], errors="coerce")
    for col in ["market", "primary_exchange", "name"]:
        if col not in hist.columns:
            hist[col] = pd.NA
    hist = hist.dropna(subset=["request_date"])
    return hist.sort_values("request_date").reset_index(drop=True)


def _market_cap_asof(hist: pd.DataFrame, event_date: str) -> tuple[float | None, str | None]:
    if hist.empty or "market_cap" not in hist.columns:
        return None, None
    cap_hist = hist[hist["market_cap"].notna()]
    if cap_hist.empty:
        return None, None
    prior = cap_hist[cap_hist["request_date"] <= event_date]
    if not prior.empty:
        row = prior.iloc[-1]
    else:
        row = cap_hist.iloc[0]
    return float(row["market_cap"]), str(row["request_date"])


def _reference_asof(hist: pd.DataFrame, event_date: str) -> dict:
    if hist.empty:
        return {}
    prior = hist[hist["request_date"] <= event_date]
    row = prior.iloc[-1] if not prior.empty else hist.iloc[0]
    return row.to_dict()


def _tradingview_symbol(ticker: str, primary_exchange: str | None) -> str:
    exchange = str(primary_exchange or "").strip().upper()
    prefix = TRADINGVIEW_EXCHANGE_PREFIX.get(exchange)
    if prefix:
        return f"{prefix}:{ticker.upper()}"
    return ticker.upper()


def _apply_universe_filter(out: pd.DataFrame, universe: pd.DataFrame) -> pd.DataFrame:
    meta = universe[
        ["ticker", "first_seen_date", "last_observed_date", "classification_1b"]
    ].reset_index(drop=True).rename(
        columns={
            "first_seen_date": "universe_first_seen_date",
            "last_observed_date": "universe_last_observed_date",
            "classification_1b": "universe_classification_1b",
        }
    )
    out = out.merge(meta, on="ticker", how="left")
    event_dates = pd.to_datetime(out["session_date"], errors="coerce")
    first_seen = pd.to_datetime(out["universe_first_seen_date"], errors="coerce")
    last_seen = pd.to_datetime(out["universe_last_observed_date"], errors="coerce")
    out["universe_dataset_id"] = LT1B_UNIVERSE_DATASET_ID
    out["universe_run_id"] = LT1B_UNIVERSE_RUN_ID
    out["universe_filter_policy"] = LT1B_UNIVERSE_FILTER_POLICY
    out["universe_filter_pass"] = (
        event_dates.notna()
        & first_seen.notna()
        & last_seen.notna()
        & (event_dates >= first_seen)
        & (event_dates <= last_seen)
    )
    out = out[out["universe_filter_pass"]].copy()
    out["universe_first_seen_date"] = pd.to_datetime(out["universe_first_seen_date"]).dt.date.astype(str)
    out["universe_last_observed_date"] = pd.to_datetime(out["universe_last_observed_date"]).dt.date.astype(str)
    return out


def _candidate_rows_for_session(
    session_df: pd.DataFrame,
    session_volume: float,
    config: FindConfig,
) -> list[dict]:
    if config.selection_mode not in {"first_push_of_day", "all_pushes"}:
        raise ValueError(f"Unsupported selection_mode: {config.selection_mode}")

    rows: list[dict] = []
    if len(session_df) < 3:
        return rows

    sdf = session_df.reset_index(drop=True)
    ts = sdf["ts_utc_dt"]

    consecutive = (
        (ts.shift(-1) - ts).eq(pd.Timedelta(minutes=1))
        & (ts.shift(-2) - ts.shift(-1)).eq(pd.Timedelta(minutes=1))
    )
    same_segment = (
        sdf["session_segment"].eq(sdf["session_segment"].shift(-1))
        & sdf["session_segment"].eq(sdf["session_segment"].shift(-2))
    )
    rising_highs = (
        sdf["px_h"].shift(-1).gt(sdf["px_h"])
        & sdf["px_h"].shift(-2).gt(sdf["px_h"].shift(-1))
    )
    close_above_prev_high = (
        sdf["px_c"].shift(-1).gt(sdf["px_h"])
        & sdf["px_c"].shift(-2).gt(sdf["px_h"].shift(-1))
    )
    event_high = pd.concat(
        [sdf["px_h"], sdf["px_h"].shift(-1), sdf["px_h"].shift(-2)],
        axis=1,
    ).max(axis=1)
    event_start_price = sdf["px_o"]
    push_pct = (event_high / event_start_price - 1.0) * 100.0

    mask = consecutive & event_start_price.gt(0)
    if config.require_same_segment:
        mask &= same_segment
    if config.require_rising_highs:
        mask &= rising_highs
    if config.require_close_above_prev_high:
        mask &= close_above_prev_high
    mask &= push_pct.ge(config.push_pct)
    mask &= event_start_price.ge(config.min_price)

    positions = mask[mask].index.tolist()
    if config.selection_mode == "first_push_of_day":
        positions = positions[:1]

    for i in positions:
        a = sdf.iloc[i]
        b = sdf.iloc[i + 1]
        c = sdf.iloc[i + 2]

        row_event_start_price = float(a["px_o"])
        row_event_high = float(max(a["px_h"], b["px_h"], c["px_h"]))
        event_end_price = float(c["px_c"])
        row_push_pct = (row_event_high / row_event_start_price - 1.0) * 100.0

        rows.append(
            {
                "ticker": str(a["ticker"]).upper(),
                "event_ts_utc": a["ts_utc_dt"].isoformat(),
                "event_end_ts_utc": c["ts_utc_dt"].isoformat(),
                "event_ts_et": a["ts_et"].isoformat(),
                "event_end_ts_et": c["ts_et"].isoformat(),
                "session_date": str(a["session_date"]),
                "session_segment": str(a["session_segment"]),
                "query_name": config.query_name,
                "price_view": config.price_view,
                "session_scope": config.session_scope,
                "push_window_bars": 3,
                "selection_mode": config.selection_mode,
                "qualifying_push_rank_in_day": len(rows) + 1,
                "push_pct": round(row_push_pct, 6),
                "event_start_price": row_event_start_price,
                "event_end_price": event_end_price,
                "event_high": row_event_high,
                "bar1_open": float(a["px_o"]),
                "bar1_high": float(a["px_h"]),
                "bar1_low": float(a["px_l"]),
                "bar1_close": float(a["px_c"]),
                "bar1_volume": float(a["v"]),
                "bar2_open": float(b["px_o"]),
                "bar2_high": float(b["px_h"]),
                "bar2_low": float(b["px_l"]),
                "bar2_close": float(b["px_c"]),
                "bar2_volume": float(b["v"]),
                "bar3_open": float(c["px_o"]),
                "bar3_high": float(c["px_h"]),
                "bar3_low": float(c["px_l"]),
                "bar3_close": float(c["px_c"]),
                "bar3_volume": float(c["v"]),
                "session_volume": float(session_volume),
                "required_rising_highs": config.require_rising_highs,
                "required_close_above_prev_high": config.require_close_above_prev_high,
                "required_same_segment": config.require_same_segment,
            }
        )
    return rows


def _candidate_rows_for_file(
    file_path: Path,
    config: FindConfig,
    start_date: str | None,
    end_date: str | None,
) -> list[dict]:
    df = _read_1m_file(file_path, config.price_view)
    if df.empty:
        return []
    mask = _scope_mask(df, config.session_scope)
    df = df[mask].copy()
    if df.empty:
        return []

    if start_date:
        df = df[df["session_date"] >= start_date]
    if end_date:
        df = df[df["session_date"] <= end_date]
    if df.empty:
        return []

    rows: list[dict] = []
    for _, session_df in df.groupby("session_date", sort=True):
        session_volume = float(session_df["v"].sum())
        if session_volume < config.min_session_volume:
            continue
        rows.extend(_candidate_rows_for_session(session_df, session_volume, config))
    return rows


def _postprocess_candidates(
    candidates: list[dict],
    config: FindConfig,
    overview_root: Path,
    universe: pd.DataFrame | None,
    market_cap_cache: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    out = pd.DataFrame(candidates)
    if out.empty:
        return out

    if universe is not None:
        out = _apply_universe_filter(out, universe)
        if out.empty:
            return out

    market_caps: list[float | None] = []
    market_cap_dates: list[str | None] = []
    primary_exchanges: list[str | None] = []
    markets: list[str | None] = []
    security_names: list[str | None] = []
    tradingview_symbols: list[str] = []
    for row in out.itertuples(index=False):
        ticker = row.ticker
        if ticker not in market_cap_cache:
            market_cap_cache[ticker] = _load_market_cap_history(overview_root, ticker)
        ref_hist = market_cap_cache[ticker]
        cap, cap_date = _market_cap_asof(ref_hist, row.session_date)
        ref = _reference_asof(ref_hist, row.session_date)
        primary_exchange = ref.get("primary_exchange")
        market_caps.append(cap)
        market_cap_dates.append(cap_date)
        primary_exchanges.append(primary_exchange if pd.notna(primary_exchange) else None)
        markets.append(ref.get("market") if pd.notna(ref.get("market")) else None)
        security_names.append(ref.get("name") if pd.notna(ref.get("name")) else None)
        tradingview_symbols.append(_tradingview_symbol(ticker, primary_exchange))
    out["market_cap"] = market_caps
    out["market_cap_request_date"] = market_cap_dates
    out["primary_exchange"] = primary_exchanges
    out["market"] = markets
    out["security_name"] = security_names
    out["tradingview_symbol"] = tradingview_symbols

    if config.max_market_cap is not None:
        has_cap = out["market_cap"].notna()
        cap_ok = has_cap & (out["market_cap"] < config.max_market_cap)
        if config.missing_market_cap_policy == "exclude":
            out = out[cap_ok].copy()
        elif config.missing_market_cap_policy == "include":
            out = out[cap_ok | ~has_cap].copy()
        elif config.missing_market_cap_policy == "flag":
            out["market_cap_filter_pass"] = cap_ok
            out["market_cap_missing"] = ~has_cap
        else:
            raise ValueError(f"Unsupported missing_market_cap_policy: {config.missing_market_cap_policy}")

    out = out.sort_values(["session_date", "ticker", "event_ts_utc"]).reset_index(drop=True)
    out.insert(
        0,
        "candidate_id",
        [
            f"{config.query_name}:{r.ticker}:{r.event_ts_utc}:{idx}"
            for idx, r in enumerate(out.itertuples(index=False))
        ],
    )
    return out


def _write_running_manifest(
    run_dir: Path,
    config: FindConfig,
    files_scanned: int,
    total_files: int,
    raw_candidate_count: int,
    candidate_count: int,
    partial_output: str | None,
) -> None:
    manifest = _run_manifest(
        run_dir.name,
        config,
        run_status="running",
        candidate_count=candidate_count,
    )
    manifest = _preserve_manifest_fields(run_dir, manifest)
    manifest["files_scanned"] = int(files_scanned)
    manifest["total_files"] = int(total_files)
    manifest["raw_candidate_count"] = int(raw_candidate_count)
    manifest["last_update_utc"] = datetime.now(timezone.utc).isoformat()
    if partial_output is not None:
        manifest["partial_output"] = partial_output
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _raw_partial_candidates(candidates: list[dict], config: FindConfig) -> pd.DataFrame:
    out = pd.DataFrame(candidates)
    if out.empty:
        return out
    out = out.sort_values(["session_date", "ticker", "event_ts_utc"]).reset_index(drop=True)
    if "candidate_id" not in out.columns:
        out.insert(
            0,
            "candidate_id",
            [
                f"{config.query_name}:partial:{r.ticker}:{r.event_ts_utc}:{idx}"
                for idx, r in enumerate(out.itertuples(index=False))
            ],
        )
    return out


def _flush_partial_run(
    run_dir: Path,
    candidates: list[dict],
    config: FindConfig,
    files_scanned: int,
    total_files: int,
) -> pd.DataFrame:
    partial = _raw_partial_candidates(candidates, config)
    partial_path = run_dir / "candidate_events_partial.csv"
    if not partial.empty:
        partial.to_csv(partial_path, index=False)
    else:
        pd.DataFrame().to_csv(partial_path, index=False)
    _write_running_manifest(
        run_dir,
        config,
        files_scanned=files_scanned,
        total_files=total_files,
        raw_candidate_count=len(candidates),
        candidate_count=len(partial),
        partial_output=partial_path.name,
    )
    return partial


def find_candidates(config: FindConfig, run_dir: Path | None = None) -> pd.DataFrame:
    data_root = Path(config.data_root)
    overview_root = Path(config.reference_overview_root)
    universe = load_lt1b_universe(Path(config.universe_path)) if config.use_lt1b_universe else None
    start_date = pd.to_datetime(config.start_date).date().isoformat() if config.start_date else None
    end_date = pd.to_datetime(config.end_date).date().isoformat() if config.end_date else None
    market_cap_cache: dict[str, pd.DataFrame] = {}
    candidates: list[dict] = []

    files = list(_iter_parquet_files(data_root, config.tickers, config.years, universe))
    if config.progress_every > 0:
        print(f"files_to_scan={len(files)}", flush=True)
    if run_dir is not None:
        _write_running_manifest(
            run_dir,
            config,
            files_scanned=0,
            total_files=len(files),
            raw_candidate_count=0,
            candidate_count=0,
            partial_output=None,
        )

    files_scanned = 0
    last_flushed_raw_candidates = 0

    def _maybe_flush_partial(force: bool = False) -> None:
        nonlocal last_flushed_raw_candidates
        if run_dir is None:
            return
        new_candidates = len(candidates) - last_flushed_raw_candidates
        should_flush_candidates = (
            config.partial_flush_every > 0
            and new_candidates >= config.partial_flush_every
        )
        if not force and not should_flush_candidates:
            return
        _flush_partial_run(
            run_dir,
            candidates,
            config,
            files_scanned,
            len(files),
        )
        last_flushed_raw_candidates = len(candidates)

    def _record_progress(file_index: int, file_path: Path) -> None:
        if config.progress_every > 0 and (
            file_index == 1 or file_index % config.progress_every == 0
        ):
            print(
                f"progress files_scanned={file_index}/{len(files)} "
                f"raw_candidates={len(candidates)} current={file_path}",
                flush=True,
            )
            _maybe_flush_partial(force=True)

    if config.workers <= 1:
        for file_index, file_path in enumerate(files, start=1):
            files_scanned = file_index
            _record_progress(file_index, file_path)
            candidates.extend(_candidate_rows_for_file(file_path, config, start_date, end_date))
            _maybe_flush_partial()
            if config.max_candidates is not None and len(candidates) >= config.max_candidates:
                candidates = candidates[: config.max_candidates]
                _maybe_flush_partial(force=True)
                break
    else:
        with ThreadPoolExecutor(max_workers=config.workers) as executor:
            futures = {
                executor.submit(_candidate_rows_for_file, file_path, config, start_date, end_date): file_path
                for file_path in files
            }
            for future in as_completed(futures):
                file_path = futures[future]
                files_scanned += 1
                candidates.extend(future.result())
                _record_progress(files_scanned, file_path)
                _maybe_flush_partial()

    if config.progress_every > 0:
        print(
            f"scan_complete files_scanned={files_scanned}/{len(files)} "
            f"raw_candidates={len(candidates)}",
            flush=True,
        )
    _maybe_flush_partial(force=True)

    return _postprocess_candidates(candidates, config, overview_root, universe, market_cap_cache)


def _run_manifest(
    run_id: str,
    config: FindConfig,
    run_status: str,
    candidate_count: int | None = None,
    error: str | None = None,
) -> dict:
    manifest = {
        "run_id": run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "config": asdict(config),
        "universe": {
            "enabled": bool(config.use_lt1b_universe),
            "universe_dataset_id": LT1B_UNIVERSE_DATASET_ID,
            "universe_run_id": LT1B_UNIVERSE_RUN_ID,
            "universe_filter_policy": LT1B_UNIVERSE_FILTER_POLICY,
            "universe_rows": LT1B_UNIVERSE_ROWS,
            "universe_physical_path": str(DEFAULT_LT1B_UNIVERSE_PATH).replace("\\", "/"),
        },
        "run_status": run_status,
        "source_role": "event_discovery_runtime_output",
        "institutional_status": "exploratory_not_source_of_truth",
    }
    if candidate_count is not None:
        manifest["candidate_count"] = int(candidate_count)
    if error is not None:
        manifest["error"] = error
    return manifest


def _existing_manifest(run_dir: Path) -> dict:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _preserve_manifest_fields(run_dir: Path, manifest: dict) -> dict:
    existing = _existing_manifest(run_dir)
    for key in [
        "created_utc",
        "files_scanned",
        "total_files",
        "raw_candidate_count",
        "partial_output",
        "last_update_utc",
    ]:
        if key in existing:
            manifest[key] = existing[key]
    return manifest


def create_run_dir(config: FindConfig) -> Path:
    run_id = f"{config.query_name}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = Path(config.output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "case_panels").mkdir(exist_ok=True)
    (run_dir / "manifest.json").write_text(
        json.dumps(_run_manifest(run_id, config, run_status="running"), indent=2),
        encoding="utf-8",
    )
    (run_dir / "query_config.json").write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")
    return run_dir


def finalize_run(run_dir: Path, candidates: pd.DataFrame, config: FindConfig) -> Path:
    if not candidates.empty:
        candidates.to_parquet(run_dir / "candidate_events.parquet", index=False)
        candidates.to_csv(run_dir / "candidate_events.csv", index=False)
    else:
        pd.DataFrame().to_csv(run_dir / "candidate_events.csv", index=False)
    run_id = run_dir.name
    manifest = _run_manifest(
        run_id,
        config,
        run_status="completed",
        candidate_count=int(len(candidates)),
    )
    manifest = _preserve_manifest_fields(run_dir, manifest)
    manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return run_dir


def mark_run_failed(run_dir: Path, config: FindConfig, error: str) -> None:
    manifest = _run_manifest(
        run_dir.name,
        config,
        run_status="failed",
        error=error,
    )
    manifest = _preserve_manifest_fields(run_dir, manifest)
    manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_run(candidates: pd.DataFrame, config: FindConfig) -> Path:
    run_dir = create_run_dir(config)
    finalize_run(run_dir, candidates, config)
    return run_dir


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Find 3-bar push candidates in 1m data.")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--reference-overview-root", default=str(DEFAULT_REFERENCE_OVERVIEW_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_RUNS_ROOT))
    parser.add_argument("--universe-path", default=str(DEFAULT_LT1B_UNIVERSE_PATH))
    parser.add_argument(
        "--no-lt1b-universe-filter",
        action="store_true",
        help="Debug only: scan the physical data root without the certified LT1B universe filter.",
    )
    parser.add_argument("--tickers", default="")
    parser.add_argument("--years", default="")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--push-pct", type=float, default=20.0)
    parser.add_argument("--min-session-volume", type=float, default=500_000.0)
    parser.add_argument("--min-price", type=float, default=0.5)
    parser.add_argument("--max-market-cap", type=float, default=100_000_000.0)
    parser.add_argument("--missing-market-cap-policy", choices=["exclude", "include", "flag"], default="exclude")
    parser.add_argument(
        "--session-scope",
        choices=["premarket_regular", "full_extended", "regular", "premarket", "afterhours", "all"],
        default="premarket_regular",
    )
    parser.add_argument("--selection-mode", choices=["first_push_of_day", "all_pushes"], default="first_push_of_day")
    parser.add_argument("--price-view", choices=["split_normalized", "raw"], default="raw")
    parser.add_argument("--no-rising-highs", action="store_true")
    parser.add_argument("--no-close-above-prev-high", action="store_true")
    parser.add_argument(
        "--allow-cross-segment-window",
        action="store_true",
        help="Backward-compatible no-op. Cross-segment 3-bar windows are allowed by default.",
    )
    parser.add_argument("--max-candidates", type=int)
    parser.add_argument(
        "--progress-every",
        type=int,
        default=50,
        help="Print progress every N parquet files. Use 0 to disable.",
    )
    parser.add_argument(
        "--partial-flush-every",
        type=int,
        default=1,
        help="Rewrite candidate_events_partial.csv every N new raw candidates. Use 0 to only update on progress batches/end.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of parquet files to scan in parallel. Start with 4 or 8 for large terminal runs.",
    )
    parser.add_argument("--no-write", action="store_true")
    return parser


def config_from_args(args: argparse.Namespace) -> FindConfig:
    return FindConfig(
        data_root=args.data_root,
        reference_overview_root=args.reference_overview_root,
        output_root=args.output_root,
        universe_path=args.universe_path,
        use_lt1b_universe=not args.no_lt1b_universe_filter,
        tickers=_parse_csv(args.tickers),
        years=_parse_years(args.years),
        start_date=args.start_date,
        end_date=args.end_date,
        push_pct=args.push_pct,
        min_session_volume=args.min_session_volume,
        min_price=args.min_price,
        max_market_cap=args.max_market_cap,
        missing_market_cap_policy=args.missing_market_cap_policy,
        session_scope=args.session_scope,
        selection_mode=args.selection_mode,
        price_view=args.price_view,
        require_rising_highs=not args.no_rising_highs,
        require_close_above_prev_high=not args.no_close_above_prev_high,
        require_same_segment=False,
        max_candidates=args.max_candidates,
        progress_every=args.progress_every,
        partial_flush_every=args.partial_flush_every,
        workers=args.workers,
        write_outputs=not args.no_write,
    )


def main() -> int:
    args = build_arg_parser().parse_args()
    config = config_from_args(args)
    run_dir: Path | None = None
    if config.write_outputs:
        run_dir = create_run_dir(config)
        print(f"run_dir={run_dir}", flush=True)
        print("run_status=running", flush=True)
    try:
        candidates = find_candidates(config, run_dir=run_dir)
    except Exception as exc:
        if run_dir is not None:
            mark_run_failed(run_dir, config, error=repr(exc))
            print("run_status=failed", flush=True)
        raise
    print(f"candidates={len(candidates)}")
    if run_dir is not None:
        finalize_run(run_dir, candidates, config)
        print("run_status=completed", flush=True)
    elif not candidates.empty:
        print(candidates.head(20).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
