from __future__ import annotations

import hashlib
import math
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
CACHE_ROOT = PROJECT_ROOT / "runs" / "backtest" / "trades_v2_materialized" / "trades_current_cd_merged" / "root_cause_exports" / "file_acceptance_cache_lt1b_full_clean_fast_same_schema"
RAW_DIR = CACHE_ROOT / "raw_metrics_shards"
INDEX_DIR = CACHE_ROOT / "full_index_shards"
OUT_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "trades" / "evidence_assets" / "stratified_samples"


USE_COLS = [
    "ticker",
    "date",
    "sample_stratum",
    "odd_lot_trade_pct",
    "duplicate_exact_ratio_pct_raw",
    "max_trades_same_timestamp_raw",
    "trade_vwap_vs_daily_vw_diff_pct_raw",
    "scale_bucket_vw",
    "scale_bucket_high",
    "outside_daily_regular_pct",
    "core_outside_daily_pct",
    "core_outside_daily_volume_pct",
    "outside_1m_regular_pct",
    "outside_1m_odd_lot_pct",
    "outside_1m_round_lot_pct",
    "core_outside_1m_pct",
    "outside_minutes_pct_active",
    "rows_after_parse",
    "acceptance_label",
]

INDEX_COLS = [
    "file",
    "ticker",
    "date",
    "issues_list",
    "warns_list",
    "m.l",
    "m.h",
    "m.vw",
    "m.price_min",
    "m.price_max",
    "m.trade_vwap",
    "m.rows_after_parse",
    "m.ohlcv_1m_found",
    "m.ohlcv_daily_found",
    "m.ohlcv_1m_path",
    "m.ohlcv_daily_path",
    "sample_stratum",
]


TARGETS = {
    "review": 60,
    "reference_scale_mismatch": 60,
    "review_microstructure": 60,
    "bad_data": 60,
    "review_no_1m_reference": 60,
    "review_1m_reference_alignment": 60,
    "good": 999999,
}


def year_from_date(date_val) -> int | None:
    if pd.isna(date_val):
        return None
    try:
        return int(str(date_val)[:4])
    except Exception:
        return None


def year_band(year: int | None) -> str:
    if year is None:
        return "year_unknown"
    if year <= 2012:
        return "early"
    if year <= 2018:
        return "mid"
    return "recent"


def is_near_1x(val: str | None) -> bool:
    return val in {"~1x", "near_1x"}


def safe_num(val, default=0.0) -> float:
    if pd.isna(val):
        return default
    try:
        return float(val)
    except Exception:
        return default


def signature_band(row: pd.Series) -> str:
    bucket = row["acceptance_label"]
    scale_vw = row.get("scale_bucket_vw")
    scale_high = row.get("scale_bucket_high")
    odd = safe_num(row.get("odd_lot_trade_pct"))
    dup = safe_num(row.get("duplicate_exact_ratio_pct_raw"))
    burst = safe_num(row.get("max_trades_same_timestamp_raw"))
    outside_1m = safe_num(row.get("outside_1m_regular_pct"))
    outside_daily = safe_num(row.get("outside_daily_regular_pct"))
    diff = safe_num(row.get("trade_vwap_vs_daily_vw_diff_pct_raw"))
    core_daily = safe_num(row.get("core_outside_daily_pct"))

    if bucket == "reference_scale_mismatch":
        return str(scale_vw or scale_high or "scale_unknown")
    if bucket == "review_microstructure":
        if odd >= 70 and dup < 5:
            return "odd_lot_dom"
        if dup >= 5 or burst >= 10:
            return "duplicate_burst"
        return "mixed_micro"
    if bucket == "review_no_1m_reference":
        if outside_daily <= 1:
            return "daily_le_1"
        if outside_daily <= 5:
            return "daily_1_5"
        return "daily_gt_5"
    if bucket == "review_1m_reference_alignment":
        if core_daily <= 1:
            return "tight_daily"
        if core_daily <= 2:
            return "mild_daily"
        return "wider_daily"
    if bucket == "review":
        if is_near_1x(scale_vw) and outside_1m <= 15:
            return "near1x_low1m"
        if outside_1m > 15:
            return "high_1m_conflict"
        if outside_daily > 1:
            return "daily_conflict"
        return "mixed_review"
    if bucket == "bad_data":
        if (not is_near_1x(scale_vw)) and diff >= 20:
            return "scale_break"
        if dup >= 10 or burst >= 20:
            return "duplicate_break"
        if outside_1m >= 50:
            return "range_break"
        return "mixed_bad"
    return "good"


def severity_band(row: pd.Series) -> str:
    bucket = row["acceptance_label"]
    diff = safe_num(row.get("trade_vwap_vs_daily_vw_diff_pct_raw"))
    outside_1m = safe_num(row.get("outside_1m_regular_pct"))
    outside_daily = safe_num(row.get("outside_daily_regular_pct"))
    core_daily = safe_num(row.get("core_outside_daily_pct"))

    if bucket == "reference_scale_mismatch":
        if diff <= 5:
            return "sev_low"
        if diff <= 20:
            return "sev_mid"
        return "sev_high"
    if bucket == "review_microstructure":
        if outside_1m <= 15:
            return "sev_low"
        if outside_1m <= 30:
            return "sev_mid"
        return "sev_high"
    if bucket == "review_no_1m_reference":
        if outside_daily <= 1:
            return "sev_low"
        if outside_daily <= 5:
            return "sev_mid"
        return "sev_high"
    if bucket == "review_1m_reference_alignment":
        if core_daily <= 1:
            return "sev_low"
        if core_daily <= 2:
            return "sev_mid"
        return "sev_high"
    if bucket == "review":
        if outside_1m <= 15:
            return "sev_low"
        if outside_1m <= 30:
            return "sev_mid"
        return "sev_high"
    if bucket == "bad_data":
        if diff <= 20:
            return "sev_low"
        if diff <= 50:
            return "sev_mid"
        return "sev_high"
    return "pristine"


def stable_hash(*parts: str) -> str:
    text = "|".join(parts)
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def quota_by_stratum(counts: Counter[str], target: int) -> dict[str, int]:
    total = sum(counts.values())
    if total <= target:
        return dict(counts)
    raw = {k: (v / total) * target for k, v in counts.items()}
    floor = {k: min(counts[k], int(math.floor(v))) for k, v in raw.items()}
    assigned = sum(floor.values())
    for k in counts:
        if floor[k] == 0 and counts[k] > 0 and assigned < target:
            floor[k] = 1
            assigned += 1
    remainder = sorted(
        ((raw[k] - floor[k], k) for k in counts if floor[k] < counts[k]),
        reverse=True,
    )
    i = 0
    while assigned < target and i < len(remainder):
        _, k = remainder[i]
        if floor[k] < counts[k]:
            floor[k] += 1
            assigned += 1
        i += 1
        if i == len(remainder) and assigned < target:
            i = 0
    return floor


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shards = sorted(RAW_DIR.glob("*.parquet"))
    index_shards = sorted(INDEX_DIR.glob("*.parquet"))
    if not shards:
        raise FileNotFoundError(f"No shards found in {RAW_DIR}")
    if len(shards) != len(index_shards):
        raise RuntimeError("raw_metrics_shards and full_index_shards counts do not match")

    strata_counts: dict[str, Counter[str]] = defaultdict(Counter)
    totals: Counter[str] = Counter()

    # Pass 1: counts
    for shard in shards:
        df = pd.read_parquet(shard, columns=USE_COLS)
        for _, row in df.iterrows():
            bucket = row["acceptance_label"]
            if bucket not in TARGETS:
                continue
            yb = year_band(year_from_date(row["date"]))
            sig = signature_band(row)
            sev = severity_band(row)
            key = f"{yb}|{sig}|{sev}"
            strata_counts[bucket][key] += 1
            totals[bucket] += 1

    quotas = {
        bucket: quota_by_stratum(strata_counts[bucket], min(TARGETS[bucket], totals[bucket]))
        for bucket in TARGETS
    }

    # Pass 2: select by stable hash within quota
    selected: dict[str, dict[str, list[tuple[str, dict]]]] = {
        bucket: defaultdict(list) for bucket in TARGETS
    }
    for shard, idx_shard in zip(shards, index_shards):
        df = pd.read_parquet(shard, columns=USE_COLS)
        idx_df = pd.read_parquet(idx_shard, columns=INDEX_COLS)
        df = df.merge(idx_df, on=["ticker", "date", "sample_stratum"], how="left")
        for _, row in df.iterrows():
            bucket = row["acceptance_label"]
            if bucket not in TARGETS:
                continue
            yb = year_band(year_from_date(row["date"]))
            sig = signature_band(row)
            sev = severity_band(row)
            key = f"{yb}|{sig}|{sev}"
            quota = quotas[bucket].get(key, 0)
            if quota <= 0:
                continue
            rec = row.to_dict()
            rec["year_band"] = yb
            rec["signature_band"] = sig
            rec["severity_band"] = sev
            rec["sample_manifest"] = "57f_stratified_v0_1"
            rec["sample_hash"] = stable_hash(str(bucket), str(rec["ticker"]), str(rec["date"]))
            store = selected[bucket][key]
            store.append((rec["sample_hash"], rec))
            store.sort(key=lambda x: x[0])
            if len(store) > quota:
                del store[quota:]

    summary_rows = []
    for bucket in TARGETS:
        records = []
        for key, items in selected[bucket].items():
            for _, rec in items:
                records.append(rec)
        if not records:
            continue
        out_df = pd.DataFrame(records).sort_values(
            ["year_band", "signature_band", "severity_band", "ticker", "date"]
        )
        out_df.to_parquet(OUT_DIR / f"{bucket}_manifest.parquet", index=False)
        out_df.to_csv(OUT_DIR / f"{bucket}_manifest.csv", index=False)

        q = quotas[bucket]
        for key, quota in sorted(q.items()):
            summary_rows.append(
                {
                    "acceptance_label": bucket,
                    "stratum_key": key,
                    "population_count": int(strata_counts[bucket][key]),
                    "quota": int(quota),
                }
            )

    summary_df = pd.DataFrame(summary_rows).sort_values(
        ["acceptance_label", "stratum_key"]
    )
    summary_df.to_csv(OUT_DIR / "stratified_sample_summary.csv", index=False)

    lines = [
        "# Trades Stratified Sample Manifests v0.1",
        "",
        "## Rol",
        "",
        "Este documento resume la primera materializacion de muestras estratificadas por familia sobre el cache final `57f/full_clean_fast_same_schema`.",
        "",
        "No son ejemplos elegidos a dedo. Son manifests reproducibles para export y lectura del inspector.",
        "",
        "## Conteos por familia",
        "",
        "| familia | universo | target | seleccionado |",
        "|---|---:|---:|---:|",
    ]
    for bucket in TARGETS:
        if bucket not in totals:
            continue
        manifest = OUT_DIR / f"{bucket}_manifest.parquet"
        selected_n = len(pd.read_parquet(manifest)) if manifest.exists() else 0
        target_n = min(TARGETS[bucket], totals[bucket])
        lines.append(f"| `{bucket}` | {int(totals[bucket])} | {int(target_n)} | {int(selected_n)} |")
    lines.extend(
        [
            "",
            "## Artefactos",
            "",
            "- manifests `.parquet` y `.csv` por familia en `evidence_assets/stratified_samples/`",
            "- resumen de cuotas por estrato en `stratified_sample_summary.csv`",
            "",
            "## Nota metodologica",
            "",
            "- `good` se enumera completo mientras siga siendo pequeno.",
            "- `review_no_1m_reference` y `review_1m_reference_alignment` ya no se tratan como buckets diminutos del historico; en el cierre real tienen masa suficiente para muestreo estratificado fuerte.",
        ]
    )
    (OUT_DIR / "trades_stratified_sample_manifests_v0_1.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
