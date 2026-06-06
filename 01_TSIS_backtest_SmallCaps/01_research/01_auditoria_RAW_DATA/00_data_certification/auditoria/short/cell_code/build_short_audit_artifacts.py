from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_universe(universe_parquet: Path) -> set[str]:
    df = pd.read_parquet(universe_parquet, columns=["ticker"])
    return set(df["ticker"].dropna().astype(str).str.upper().unique())


def file_stats(path: Path, date_col: str, provider: str, dataset: str) -> dict:
    try:
        t = pq.read_table(path)
        rows = t.num_rows
        cols = t.schema.names
        if rows:
            if date_col in cols:
                s = t.column(cols.index(date_col)).to_pandas()
                min_date = s.min()
                max_date = s.max()
            else:
                min_date = None
                max_date = None
        else:
            min_date = None
            max_date = None
        return {
            "provider": provider,
            "dataset": dataset,
            "ticker": path.stem.upper(),
            "path": str(path),
            "rows": rows,
            "columns": cols,
            "min_date": min_date,
            "max_date": max_date,
        }
    except Exception as exc:
        return {
            "provider": provider,
            "dataset": dataset,
            "ticker": path.stem.upper(),
            "path": str(path),
            "rows": -1,
            "columns": [],
            "min_date": None,
            "max_date": None,
            "error": repr(exc),
        }


def collect_inventory(root: Path, provider: str, dataset: str, date_col: str) -> pd.DataFrame:
    rows = [file_stats(p, date_col, provider, dataset) for p in sorted(root.glob("*.parquet"))]
    return pd.DataFrame(rows)


def compare_inventory(poly: pd.DataFrame, finra: pd.DataFrame) -> pd.DataFrame:
    cols = ["ticker", "rows", "min_date", "max_date"]
    p = poly[cols].rename(columns={"rows": "poly_rows", "min_date": "poly_min_date", "max_date": "poly_max_date"})
    f = finra[cols].rename(columns={"rows": "finra_rows", "min_date": "finra_min_date", "max_date": "finra_max_date"})
    out = p.merge(f, on="ticker", how="outer")
    out["present_polygon"] = out["poly_rows"].notna()
    out["present_finra"] = out["finra_rows"].notna()
    out["only_polygon"] = out["present_polygon"] & ~out["present_finra"]
    out["only_finra"] = out["present_finra"] & ~out["present_polygon"]
    out["shared"] = out["present_polygon"] & out["present_finra"]
    return out.sort_values("ticker").reset_index(drop=True)


def arithmetic_checks_short_interest(root: Path, provider: str) -> pd.DataFrame:
    rows: list[dict] = []
    for p in sorted(root.glob("*.parquet")):
        df = pq.read_table(p).to_pandas()
        if df.empty:
            rows.append({"provider": provider, "ticker": p.stem.upper(), "rows": 0})
            continue
        implied = df["short_interest"] / df["avg_daily_volume"].replace(0, pd.NA)
        abs_err = (implied - df["days_to_cover"]).abs()
        rows.append(
            {
                "provider": provider,
                "ticker": p.stem.upper(),
                "rows": len(df),
                "zero_adv_rows": int((df["avg_daily_volume"] == 0).sum()),
                "negative_short_interest_rows": int((df["short_interest"] < 0).sum()),
                "negative_days_to_cover_rows": int((df["days_to_cover"] < 0).sum()),
                "days_to_cover_abs_err_mean": float(abs_err.dropna().mean()) if abs_err.notna().any() else None,
                "days_to_cover_abs_err_p95": float(abs_err.dropna().quantile(0.95)) if abs_err.notna().any() else None,
                "days_to_cover_abs_err_max": float(abs_err.dropna().max()) if abs_err.notna().any() else None,
            }
        )
    return pd.DataFrame(rows)


def arithmetic_checks_short_volume(root: Path, provider: str) -> pd.DataFrame:
    rows: list[dict] = []
    for p in sorted(root.glob("*.parquet")):
        df = pq.read_table(p).to_pandas()
        if df.empty:
            rows.append({"provider": provider, "ticker": p.stem.upper(), "rows": 0})
            continue
        if "orf_short_volume" not in df.columns:
            df["orf_short_volume"] = 0.0
            df["orf_short_volume_exempt"] = 0.0
        short_err = (df["short_volume"] - (df["exempt_volume"] + df["non_exempt_volume"])).abs()
        ratio_err = (((df["short_volume"] / df["total_volume"].replace(0, pd.NA)) * 100.0) - df["short_volume_ratio"]).abs()
        venue_sum = (
            df["nyse_short_volume"].fillna(0)
            + df["nasdaq_carteret_short_volume"].fillna(0)
            + df["nasdaq_chicago_short_volume"].fillna(0)
            + df["adf_short_volume"].fillna(0)
            + df["orf_short_volume"].fillna(0)
        )
        venue_err = (df["short_volume"] - venue_sum).abs()
        rows.append(
            {
                "provider": provider,
                "ticker": p.stem.upper(),
                "rows": len(df),
                "negative_total_rows": int((df["total_volume"] < 0).sum()),
                "negative_short_rows": int((df["short_volume"] < 0).sum()),
                "short_split_err_max": float(short_err.max()),
                "ratio_err_mean": float(ratio_err.dropna().mean()) if ratio_err.notna().any() else None,
                "ratio_err_p95": float(ratio_err.dropna().quantile(0.95)) if ratio_err.notna().any() else None,
                "venue_err_mean": float(venue_err.dropna().mean()) if venue_err.notna().any() else None,
                "venue_err_p95": float(venue_err.dropna().quantile(0.95)) if venue_err.notna().any() else None,
            }
        )
    return pd.DataFrame(rows)


def load_reference_identity(reference_cache_root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ident = pq.read_table(reference_cache_root / "reference_identity_snapshot.parquet").to_pandas()
    listing = pq.read_table(reference_cache_root / "reference_listing_snapshots.parquet").to_pandas()
    remap = pq.read_table(reference_cache_root / "reference_remap_candidates.parquet").to_pandas()
    events = pq.read_table(reference_cache_root / "reference_events_exploded.parquet").to_pandas()
    return ident, listing, remap, events


def build_reference_identity_summary(
    ident: pd.DataFrame,
    listing: pd.DataFrame,
    remap: pd.DataFrame,
    events: pd.DataFrame,
) -> pd.DataFrame:
    ident_sum = (
        ident.sort_values(["ticker", "request_date"])
        .groupby("ticker", as_index=False)
        .agg(
            identity_rows=("ticker", "size"),
            identity_request_min=("request_date", "min"),
            identity_request_max=("request_date", "max"),
            identity_bucket_mode=("identity_bucket", lambda s: s.mode().iat[0] if not s.mode().empty else None),
            instrument_family_mode=("instrument_family", lambda s: s.mode().iat[0] if not s.mode().empty else None),
            type_mode=("type", lambda s: s.mode().iat[0] if not s.mode().empty else None),
            primary_exchange_mode=("primary_exchange", lambda s: s.mode().iat[0] if not s.mode().empty else None),
            transient_symbol_any=("transient_symbol_flag", "max"),
            suffix_variant_any=("suffix_variant_flag", "max"),
            list_date_min=("list_date", "min"),
        )
    )
    listing_sum = (
        listing.sort_values(["ticker", "snapshot_date"])
        .groupby("ticker", as_index=False)
        .agg(
            listing_rows=("ticker", "size"),
            listing_min_date=("snapshot_date", "min"),
            listing_max_date=("snapshot_date", "max"),
            listing_active_any=("active", "max"),
            listing_active_all=("active", "min"),
            listing_type_mode=("type", lambda s: s.mode().iat[0] if not s.mode().empty else None),
            listing_exchange_mode=("primary_exchange", lambda s: s.mode().iat[0] if not s.mode().empty else None),
        )
    )
    remap_sum = (
        remap.groupby("ticker", as_index=False)
        .agg(
            remap_candidate_flag=("remap_candidate_flag", "max"),
            ticker_base_mode=("ticker_base", lambda s: s.dropna().astype(str).mode().iat[0] if not s.dropna().empty else None),
        )
    )
    ev = events[events["event_type"] == "ticker_change"].copy()
    event_sum = (
        ev.groupby("ticker", as_index=False)
        .agg(
            ticker_change_event_count=("event_type", "size"),
            first_ticker_change_date=("event_date", "min"),
            last_ticker_change_date=("event_date", "max"),
        )
    )
    out = ident_sum.merge(listing_sum, on="ticker", how="outer")
    out = out.merge(remap_sum, on="ticker", how="left")
    out = out.merge(event_sum, on="ticker", how="left")
    return out


def classify_identity_links(comparison: pd.DataFrame, ref_sum: pd.DataFrame) -> pd.DataFrame:
    df = comparison.merge(ref_sum, on="ticker", how="left")
    poly_min = pd.to_datetime(df["poly_min_date"], errors="coerce")
    poly_max = pd.to_datetime(df["poly_max_date"], errors="coerce")
    list_min = pd.to_datetime(df.get("list_date_min"), errors="coerce")
    listing_min = pd.to_datetime(df.get("listing_min_date"), errors="coerce")
    listing_max = pd.to_datetime(df.get("listing_max_date"), errors="coerce")

    no_ref = df["identity_rows"].isna() & df["listing_rows"].isna()
    transient = df.get("transient_symbol_any", False).fillna(False) | df.get("suffix_variant_any", False).fillna(False) | df.get("remap_candidate_flag", False).fillna(False)
    before_life = poly_max.notna() & listing_min.notna() & (poly_max < listing_min)
    after_life = poly_min.notna() & listing_max.notna() & (poly_min > listing_max)
    crossing_life = poly_min.notna() & poly_max.notna() & listing_min.notna() & listing_max.notna() & ((poly_min < listing_min) | (poly_max > listing_max))
    has_ticker_change = df.get("ticker_change_event_count").fillna(0) > 0

    bucket = pd.Series("review_unclassified_only_polygon", index=df.index, dtype="object")
    bucket[no_ref] = "bad_no_reference_presence"
    bucket[~no_ref & transient] = "review_transient_or_remap_candidate"
    bucket[~no_ref & (before_life | after_life)] = "review_outside_life_window"
    bucket[~no_ref & crossing_life] = "review_crossing_life_window"
    bucket[~no_ref & ~transient & ~before_life & ~after_life & ~crossing_life & has_ticker_change] = "review_ticker_change_overlap"
    bucket[~no_ref & ~transient & ~before_life & ~after_life & ~crossing_life & ~has_ticker_change] = "review_provider_coverage_gap"
    df["identity_link_bucket"] = bucket
    df["polygon_before_listing_window"] = before_life.fillna(False)
    df["polygon_after_listing_window"] = after_life.fillna(False)
    df["polygon_crossing_listing_window"] = crossing_life.fillna(False)
    df["reference_absent"] = no_ref.fillna(False)
    return df


def load_market_current_subset(parquet_path: Path, keep_cols: list[str]) -> pd.DataFrame:
    table = pq.read_table(parquet_path, columns=keep_cols)
    return table.to_pandas()


def build_short_volume_causal_links(
    finra_short_volume_all: Path,
    halts_visual_cases: Path,
    quotes_current: Path,
    trades_current: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sv = pq.read_table(finra_short_volume_all).to_pandas()
    sv["ticker"] = sv["ticker"].astype(str).str.upper()
    sv["date"] = pd.to_datetime(sv["date"]).dt.normalize()
    sv = sv.sort_values(["ticker", "date"]).reset_index(drop=True)
    sv["short_ratio_global_p95"] = sv["short_volume_ratio"].quantile(0.95)
    sv["short_ratio_global_p99"] = sv["short_volume_ratio"].quantile(0.99)
    sv["ticker_ratio_p95"] = sv.groupby("ticker")["short_volume_ratio"].transform(lambda s: s.quantile(0.95))
    sv["ticker_ratio_mean"] = sv.groupby("ticker")["short_volume_ratio"].transform("mean")
    sv["ticker_ratio_std"] = sv.groupby("ticker")["short_volume_ratio"].transform("std")
    sv["short_ratio_z"] = ((sv["short_volume_ratio"] - sv["ticker_ratio_mean"]) / sv["ticker_ratio_std"].replace(0, pd.NA)).astype(float)
    candidates = sv[
        (sv["total_volume"] >= 1000)
        & (
            (sv["short_volume_ratio"] >= 90.0)
            | (sv["short_ratio_z"].fillna(0) >= 3.0)
        )
    ].copy()
    candidates["short_signal_bucket"] = "ratio_ge_90"
    candidates.loc[(candidates["short_volume_ratio"] < 90.0) & (candidates["short_ratio_z"].fillna(0) >= 3.0), "short_signal_bucket"] = "z_ge_3"

    h = pq.read_table(halts_visual_cases, columns=["ticker", "visual_date", "visual_case_bucket", "events_in_visual", "rank_score"]).to_pandas()
    h["ticker"] = h["ticker"].astype(str).str.upper()
    h["date"] = pd.to_datetime(h["visual_date"]).dt.normalize()
    h = h.rename(columns={"visual_case_bucket": "halt_visual_bucket", "events_in_visual": "halt_events_in_visual", "rank_score": "halt_rank_score"})
    h = h.drop(columns=["visual_date"])

    q = load_market_current_subset(quotes_current, ["ticker", "date", "severity", "issues", "warns", "action", "rows"])
    q["ticker"] = q["ticker"].astype(str).str.upper()
    q["date"] = pd.to_datetime(q["date"]).dt.normalize()
    q = q.rename(columns={"severity": "quotes_severity", "issues": "quotes_issues", "warns": "quotes_warns", "action": "quotes_action", "rows": "quotes_rows"})

    t = load_market_current_subset(trades_current, ["ticker", "date", "severity", "issues", "warns", "action", "rows"])
    t["ticker"] = t["ticker"].astype(str).str.upper()
    t["date"] = pd.to_datetime(t["date"]).dt.normalize()
    t = t.rename(columns={"severity": "trades_severity", "issues": "trades_issues", "warns": "trades_warns", "action": "trades_action", "rows": "trades_rows"})

    out = candidates.merge(h, on=["ticker", "date"], how="left")
    out = out.merge(q, on=["ticker", "date"], how="left")
    out = out.merge(t, on=["ticker", "date"], how="left")
    out["has_halt_link"] = out["halt_visual_bucket"].notna()
    out["quotes_problem"] = out["quotes_severity"].fillna("MISSING").isin(["SOFT_FAIL", "HARD_FAIL"])
    out["trades_problem"] = out["trades_severity"].fillna("MISSING").isin(["SOFT_FAIL", "HARD_FAIL"])
    out["market_link_bucket"] = "short_flow_market_clean"
    out.loc[out["has_halt_link"], "market_link_bucket"] = "short_flow_near_halt"
    out.loc[~out["has_halt_link"] & (out["quotes_problem"] | out["trades_problem"]), "market_link_bucket"] = "short_flow_near_market_anomaly"
    out.loc[~out["has_halt_link"] & ~out["quotes_problem"] & ~out["trades_problem"], "market_link_bucket"] = "short_flow_market_clean"

    halt_links = out[out["has_halt_link"]].copy()
    market_links = out[(out["quotes_problem"] | out["trades_problem"])].copy()
    summary = (
        out.groupby("market_link_bucket", as_index=False)
        .agg(
            cases=("ticker", "size"),
            tickers=("ticker", "nunique"),
            mean_short_ratio=("short_volume_ratio", "mean"),
            p95_short_ratio=("short_volume_ratio", lambda s: s.quantile(0.95)),
        )
    )
    return out, halt_links, summary


def build_short_interest_context(
    finra_short_interest_all: Path,
    halts_visual_cases: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    si = pq.read_table(finra_short_interest_all).to_pandas()
    si["ticker"] = si["ticker"].astype(str).str.upper()
    si["settlement_date"] = pd.to_datetime(si["settlement_date"]).dt.normalize()
    si = si.sort_values(["ticker", "settlement_date"]).reset_index(drop=True)
    si["ticker_dtc_p95"] = si.groupby("ticker")["days_to_cover"].transform(lambda s: s.quantile(0.95))
    si["ticker_dtc_mean"] = si.groupby("ticker")["days_to_cover"].transform("mean")
    si["ticker_dtc_std"] = si.groupby("ticker")["days_to_cover"].transform("std")
    si["dtc_z"] = pd.to_numeric((si["days_to_cover"] - si["ticker_dtc_mean"]) / si["ticker_dtc_std"].replace(0, pd.NA), errors="coerce")
    candidates = si[(si["days_to_cover"] >= si["ticker_dtc_p95"]) | (si["dtc_z"].fillna(0) >= 2.0) | (si["days_to_cover"] >= 10.0)].copy()

    h = pq.read_table(halts_visual_cases, columns=["ticker", "visual_date", "visual_case_bucket", "events_in_visual"]).to_pandas()
    h["ticker"] = h["ticker"].astype(str).str.upper()
    h["visual_date"] = pd.to_datetime(h["visual_date"]).dt.normalize()

    rows: list[dict] = []
    for ticker, g in candidates.groupby("ticker", sort=False):
        hg = h[h["ticker"] == ticker]
        if hg.empty:
            continue
        halt_dates = hg["visual_date"].dropna().drop_duplicates().sort_values()
        for _, row in g.iterrows():
            diffs = (halt_dates - row["settlement_date"]).dt.days.abs()
            if diffs.empty:
                continue
            idx = diffs.idxmin()
            min_days = int(diffs.loc[idx])
            if min_days <= 15:
                hrow = hg.loc[idx]
                rows.append(
                    {
                        "ticker": ticker,
                        "settlement_date": row["settlement_date"],
                        "days_to_cover": row["days_to_cover"],
                        "short_interest": row["short_interest"],
                        "avg_daily_volume": row["avg_daily_volume"],
                        "dtc_z": row["dtc_z"],
                        "linked_halt_date": hrow["visual_date"],
                        "days_from_halt": min_days,
                        "halt_visual_bucket": hrow["visual_case_bucket"],
                        "halt_events_in_visual": hrow["events_in_visual"],
                        "context_bucket": "days_to_cover_spike_near_halt" if (row["dtc_z"] if pd.notna(row["dtc_z"]) else 0) >= 2.0 or row["days_to_cover"] >= 10.0 else "high_short_interest_context",
                    }
                )
    linked = pd.DataFrame(rows)
    if linked.empty:
        summary = pd.DataFrame(columns=["context_bucket", "cases", "tickers", "mean_days_to_cover", "median_days_from_halt"])
    else:
        summary = linked.groupby("context_bucket", as_index=False).agg(
            cases=("ticker", "size"),
            tickers=("ticker", "nunique"),
            mean_days_to_cover=("days_to_cover", "mean"),
            median_days_from_halt=("days_from_halt", "median"),
        )
    return linked, summary


def build(args: argparse.Namespace) -> None:
    out_root: Path = args.out_root
    ensure_dir(out_root)
    ensure_dir(out_root / "cache_v2")

    universe = read_universe(args.universe_parquet)

    poly_si_root = Path(args.polygon_short_root) / "short_interest"
    poly_sv_root = Path(args.polygon_short_root) / "short_volume"
    fin_si_root = Path(args.finra_short_root) / "normalized" / "short_interest"
    fin_sv_root = Path(args.finra_short_root) / "normalized" / "short_volume"

    poly_si = collect_inventory(poly_si_root, "polygon", "short_interest", "settlement_date")
    poly_sv = collect_inventory(poly_sv_root, "polygon", "short_volume", "date")
    fin_si = collect_inventory(fin_si_root, "finra", "short_interest", "settlement_date")
    fin_sv = collect_inventory(fin_sv_root, "finra", "short_volume", "date")

    for df in (poly_si, poly_sv, fin_si, fin_sv):
        df["in_lt1b_universe"] = df["ticker"].isin(universe)

    provider_inventory = pd.concat([poly_si, poly_sv, fin_si, fin_sv], ignore_index=True)
    provider_inventory.to_parquet(out_root / "cache_v2" / "short_provider_inventory.parquet", index=False)

    cmp_si = compare_inventory(poly_si, fin_si)
    cmp_sv = compare_inventory(poly_sv, fin_sv)
    cmp_si["dataset"] = "short_interest"
    cmp_sv["dataset"] = "short_volume"
    cmp = pd.concat([cmp_si, cmp_sv], ignore_index=True)
    cmp["in_lt1b_universe"] = cmp["ticker"].isin(universe)
    cmp.to_parquet(out_root / "cache_v2" / "short_provider_comparison_summary.parquet", index=False)
    cmp[cmp["only_polygon"]].to_parquet(out_root / "cache_v2" / "short_only_polygon_tickers.parquet", index=False)
    cmp[cmp["only_finra"]].to_parquet(out_root / "cache_v2" / "short_only_finra_tickers.parquet", index=False)

    poly_si_chk = arithmetic_checks_short_interest(poly_si_root, "polygon")
    fin_si_chk = arithmetic_checks_short_interest(fin_si_root, "finra")
    si_chk = pd.concat([poly_si_chk, fin_si_chk], ignore_index=True)
    si_chk.to_parquet(out_root / "cache_v2" / "short_interest_arithmetic_checks.parquet", index=False)

    poly_sv_chk = arithmetic_checks_short_volume(poly_sv_root, "polygon")
    fin_sv_chk = arithmetic_checks_short_volume(fin_sv_root, "finra")
    sv_chk = pd.concat([poly_sv_chk, fin_sv_chk], ignore_index=True)
    sv_chk.to_parquet(out_root / "cache_v2" / "short_volume_arithmetic_checks.parquet", index=False)

    ident, listing, remap, events = load_reference_identity(args.reference_cache_root)
    ref_sum = build_reference_identity_summary(ident, listing, remap, events)
    ref_sum.to_parquet(out_root / "cache_v2" / "short_reference_identity_summary.parquet", index=False)

    only_poly = cmp[cmp["only_polygon"]].copy()
    identity_links = classify_identity_links(only_poly, ref_sum)
    identity_links.to_parquet(out_root / "cache_v2" / "short_identity_links.parquet", index=False)
    identity_links[identity_links["identity_link_bucket"].str.contains("reuse|life_window|transient|ticker_change", na=False)].to_parquet(
        out_root / "cache_v2" / "short_possible_reuse_mix.parquet", index=False
    )
    identity_links[identity_links["identity_link_bucket"].str.contains("life_window", na=False)].to_parquet(
        out_root / "cache_v2" / "short_outside_life_window.parquet", index=False
    )

    causal_all, halt_links, causal_summary = build_short_volume_causal_links(
        finra_short_volume_all=args.finra_short_root / "artifacts" / "short_volume_all_daily_finra.parquet",
        halts_visual_cases=args.halts_cache_root / "halts_quotes_trades_visual_cases.parquet",
        quotes_current=args.quotes_current_parquet,
        trades_current=args.trades_current_parquet,
    )
    causal_all.to_parquet(out_root / "cache_v2" / "short_volume_market_link_candidates.parquet", index=False)
    halt_links.to_parquet(out_root / "cache_v2" / "short_volume_halt_link_candidates.parquet", index=False)
    causal_summary.to_parquet(out_root / "cache_v2" / "short_causal_alignment_summary.parquet", index=False)

    si_context, si_context_summary = build_short_interest_context(
        finra_short_interest_all=args.finra_short_root / "artifacts" / "short_interest_all_biweekly_finra.parquet",
        halts_visual_cases=args.halts_cache_root / "halts_quotes_trades_visual_cases.parquet",
    )
    si_context.to_parquet(out_root / "cache_v2" / "short_interest_market_context_candidates.parquet", index=False)
    si_context_summary.to_parquet(out_root / "cache_v2" / "short_interest_context_summary.parquet", index=False)

    summary = {
        "polygon_short_interest_files": int(len(poly_si)),
        "polygon_short_volume_files": int(len(poly_sv)),
        "finra_short_interest_files": int(len(fin_si)),
        "finra_short_volume_files": int(len(fin_sv)),
        "only_polygon_short_interest": int(cmp_si["only_polygon"].sum()),
        "only_polygon_short_volume": int(cmp_sv["only_polygon"].sum()),
        "only_finra_short_interest": int(cmp_si["only_finra"].sum()),
        "only_finra_short_volume": int(cmp_sv["only_finra"].sum()),
        "identity_links_rows": int(len(identity_links)),
        "short_volume_causal_rows": int(len(causal_all)),
        "short_interest_context_rows": int(len(si_context)),
    }
    (out_root / "cache_v2" / "short_build_manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-root", type=Path, required=True)
    ap.add_argument("--universe-parquet", type=Path, required=True)
    ap.add_argument("--polygon-short-root", type=Path, default=Path(r"C:\TSIS_Data\data\short"))
    ap.add_argument("--finra-short-root", type=Path, default=Path(r"C:\TSIS_Data\data\short_review\finra_short"))
    ap.add_argument("--reference-cache-root", type=Path, default=Path(r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2"))
    ap.add_argument("--halts-cache-root", type=Path, default=Path(r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\cache_v2"))
    ap.add_argument("--quotes-current-parquet", type=Path, default=Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_cd_merged\quotes_current.parquet"))
    ap.add_argument("--trades-current-parquet", type=Path, default=Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\trades_current.parquet"))
    args = ap.parse_args()
    build(args)


if __name__ == "__main__":
    main()
