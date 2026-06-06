from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_outdir(base_outdir: str) -> Path:
    if str(base_outdir).strip():
        outdir = Path(base_outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = (
            Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit")
            / f"{stamp}_daily_missing_years_vs_universe"
        )
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def load_missing_years(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing-years parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    required = {"ticker", "missing_year"}
    if not required.issubset(df.columns):
        raise RuntimeError(f"Missing required columns in missing-years parquet: {required}")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["missing_year"] = pd.to_numeric(df["missing_year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["ticker", "missing_year"]).copy()
    df["missing_year"] = df["missing_year"].astype(int)
    return df


def load_universe(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Universe parquet not found: {path}")
    cols = [
        "ticker",
        "entity_id",
        "list_date",
        "delisted_utc",
        "first_seen_date",
        "last_seen_date",
        "primary_exchange",
        "status",
    ]
    df = pd.read_parquet(path)
    df = df[[c for c in cols if c in df.columns]].copy()
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    for c in ["list_date", "delisted_utc", "first_seen_date", "last_seen_date"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce").dt.tz_localize(None)
    return df


def load_calendar(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Calendar parquet not found: {path}")
    df = pd.read_parquet(path, columns=["session_date", "year"]).copy()
    df["session_date"] = pd.to_datetime(df["session_date"], errors="coerce").dt.normalize()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["session_date", "year"]).copy()
    df["year"] = df["year"].astype(int)
    return df


def coalesce_min(*values: pd.Timestamp | pd.NaT | None) -> pd.Timestamp | None:
    xs = [v for v in values if v is not None and not pd.isna(v)]
    if not xs:
        return None
    return min(xs)


def coalesce_max(*values: pd.Timestamp | pd.NaT | None) -> pd.Timestamp | None:
    xs = [v for v in values if v is not None and not pd.isna(v)]
    if not xs:
        return None
    return max(xs)


def build_universe_windows(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("ticker", dropna=False).agg(
        universe_rows=("ticker", "size"),
        entity_id_nunique=("entity_id", "nunique") if "entity_id" in df.columns else ("ticker", "size"),
        primary_exchange_nunique=("primary_exchange", "nunique") if "primary_exchange" in df.columns else ("ticker", "size"),
        list_date_min=("list_date", "min") if "list_date" in df.columns else ("ticker", "size"),
        delisted_utc_max=("delisted_utc", "max") if "delisted_utc" in df.columns else ("ticker", "size"),
        first_seen_date_min=("first_seen_date", "min") if "first_seen_date" in df.columns else ("ticker", "size"),
        last_seen_date_max=("last_seen_date", "max") if "last_seen_date" in df.columns else ("ticker", "size"),
        status_nunique=("status", "nunique") if "status" in df.columns else ("ticker", "size"),
    ).reset_index()

    for c in ["list_date_min", "delisted_utc_max", "first_seen_date_min", "last_seen_date_max"]:
        if c not in g.columns or pd.api.types.is_numeric_dtype(g[c]):
            g[c] = pd.NaT

    lifecycle_start = []
    lifecycle_end = []
    reference_kind = []
    for row in g.to_dict(orient="records"):
        start = coalesce_min(row.get("list_date_min"), row.get("first_seen_date_min"))
        end = coalesce_max(row.get("delisted_utc_max"), row.get("last_seen_date_max"))
        lifecycle_start.append(start)
        lifecycle_end.append(end)
        if start is None or end is None:
            reference_kind.append("no_lifecycle_window")
        elif int(row.get("entity_id_nunique", 0) or 0) > 1:
            reference_kind.append("multi_entity_ticker")
        else:
            reference_kind.append("single_entity_ticker")

    g["lifecycle_start_ref"] = lifecycle_start
    g["lifecycle_end_ref"] = lifecycle_end
    g["reference_kind"] = reference_kind
    return g


def build_calendar_index(calendar_df: pd.DataFrame) -> dict[int, pd.Series]:
    out: dict[int, pd.Series] = {}
    for year, g in calendar_df.groupby("year", dropna=False):
        out[int(year)] = g["session_date"].sort_values().reset_index(drop=True)
    return out


def classify_missing_years(
    missing_df: pd.DataFrame,
    windows_df: pd.DataFrame,
    calendar_index: dict[int, pd.Series],
) -> pd.DataFrame:
    merged = missing_df.merge(windows_df, on="ticker", how="left")

    records: list[dict] = []
    for row in merged.to_dict(orient="records"):
        ticker = str(row["ticker"])
        year = int(row["missing_year"])
        year_start = pd.Timestamp(year=year, month=1, day=1)
        year_end = pd.Timestamp(year=year, month=12, day=31)

        start_ref = row.get("lifecycle_start_ref")
        end_ref = row.get("lifecycle_end_ref")
        if pd.isna(start_ref):
            start_ref = None
        if pd.isna(end_ref):
            end_ref = None

        overlap_start = max(start_ref, year_start) if start_ref is not None else None
        overlap_end = min(end_ref, year_end) if end_ref is not None else None
        intersects = bool(
            overlap_start is not None
            and overlap_end is not None
            and overlap_start <= overlap_end
        )

        sessions = calendar_index.get(year)
        if sessions is not None and intersects:
            expected_session_count = int(((sessions >= overlap_start) & (sessions <= overlap_end)).sum())
            calendar_source = "official_xnys"
        elif year in calendar_index:
            expected_session_count = 0
            calendar_source = "official_xnys"
        else:
            expected_session_count = None
            calendar_source = "calendar_unavailable"

        if start_ref is None or end_ref is None:
            classification = "ambiguous_no_lifecycle_window"
        elif intersects and expected_session_count is None:
            classification = "unexpected_missing_calendar_unavailable"
        elif intersects and expected_session_count is not None and expected_session_count > 0:
            classification = (
                "unexpected_missing_ambiguous_ticker"
                if str(row.get("reference_kind", "")) == "multi_entity_ticker"
                else "unexpected_missing"
            )
        else:
            classification = "likely_valid_gap_outside_reference_window"

        records.append(
            {
                **row,
                "expected_year_start": overlap_start,
                "expected_year_end": overlap_end,
                "intersects_reference_window": intersects,
                "expected_session_count_in_year": expected_session_count,
                "calendar_source": calendar_source,
                "classification": classification,
            }
        )

    out = pd.DataFrame(records)
    date_cols = [
        "lifecycle_start_ref",
        "lifecycle_end_ref",
        "expected_year_start",
        "expected_year_end",
    ]
    for c in date_cols:
        if c in out.columns:
            out[c] = pd.to_datetime(out[c], errors="coerce")
    return out.sort_values(["classification", "ticker", "missing_year"], ascending=[True, True, True]).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Audit missing daily ticker-years against universe lifecycle and official calendar"
    )
    ap.add_argument("--missing-years-parquet", required=True)
    ap.add_argument("--universe-parquet", required=True)
    ap.add_argument("--calendar-parquet", required=True)
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    outdir = build_outdir(args.outdir)
    missing_df = load_missing_years(Path(args.missing_years_parquet))
    universe_df = load_universe(Path(args.universe_parquet))
    calendar_df = load_calendar(Path(args.calendar_parquet))

    windows_df = build_universe_windows(universe_df)
    calendar_index = build_calendar_index(calendar_df)
    audited = classify_missing_years(missing_df, windows_df, calendar_index)

    by_class = (
        audited["classification"]
        .value_counts(dropna=False)
        .rename_axis("classification")
        .reset_index(name="rows")
    )
    unexpected_only = audited[audited["classification"].isin(["unexpected_missing", "unexpected_missing_ambiguous_ticker", "unexpected_missing_calendar_unavailable"])].copy()

    audited_parquet = outdir / "daily_missing_years_vs_universe_calendar.parquet"
    audited_csv = outdir / "daily_missing_years_vs_universe_calendar.csv"
    class_parquet = outdir / "daily_missing_years_vs_universe_calendar_by_class.parquet"
    class_csv = outdir / "daily_missing_years_vs_universe_calendar_by_class.csv"
    unexpected_parquet = outdir / "daily_missing_years_unexpected_only.parquet"
    unexpected_csv = outdir / "daily_missing_years_unexpected_only.csv"
    summary_json = outdir / "daily_missing_years_vs_universe_calendar_summary.json"

    audited.to_parquet(audited_parquet, index=False)
    audited.to_csv(audited_csv, index=False)
    by_class.to_parquet(class_parquet, index=False)
    by_class.to_csv(class_csv, index=False)
    unexpected_only.to_parquet(unexpected_parquet, index=False)
    unexpected_only.to_csv(unexpected_csv, index=False)

    summary = {
        "audited_at_utc": utc_now(),
        "missing_rows_input": int(len(missing_df)),
        "universe_tickers": int(windows_df["ticker"].nunique()),
        "calendar_year_min": int(calendar_df["year"].min()) if len(calendar_df) else None,
        "calendar_year_max": int(calendar_df["year"].max()) if len(calendar_df) else None,
        "class_counts": {str(r["classification"]): int(r["rows"]) for r in by_class.to_dict(orient="records")},
        "unexpected_rows_total": int(len(unexpected_only)),
        "inventory_missing_unique_tickers": int(missing_df["ticker"].nunique()),
        "unexpected_unique_tickers": int(unexpected_only["ticker"].nunique()) if not unexpected_only.empty else 0,
        "inputs": {
            "missing_years_parquet": str(args.missing_years_parquet),
            "universe_parquet": str(args.universe_parquet),
            "calendar_parquet": str(args.calendar_parquet),
        },
        "outputs": {
            "audited_parquet": str(audited_parquet),
            "audited_csv": str(audited_csv),
            "by_class_parquet": str(class_parquet),
            "by_class_csv": str(class_csv),
            "unexpected_only_parquet": str(unexpected_parquet),
            "unexpected_only_csv": str(unexpected_csv),
            "summary_json": str(summary_json),
        },
        "outdir": str(outdir),
    }
    summary_json.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
