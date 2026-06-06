from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from IPython.display import Image, Markdown, display
from matplotlib import pyplot as plt

matplotlib.use("Agg")


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
CACHE_ROOT = PROJECT_ROOT / "runs" / "backtest" / "trades_v2_materialized" / "trades_current_cd_merged" / "root_cause_exports" / "file_acceptance_cache_lt1b_full_clean_fast_same_schema"
RAW_SHARDS_DIR = CACHE_ROOT / "raw_metrics_shards"
INDEX_SHARDS_DIR = CACHE_ROOT / "full_index_shards"
OUT_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "trades" / "evidence_assets" / "global_universe"
SNAPSHOT_PATH = OUT_DIR / "trades_universe_snapshot_v0_1.json"

LABEL_ORDER = [
    "review",
    "reference_scale_mismatch",
    "review_microstructure",
    "bad_data",
    "review_no_1m_reference",
    "review_1m_reference_alignment",
    "good",
]

SIGNATURE_TOKENS = [
    "trade_price_outside_daily_range",
    "negative_or_zero_size_rows",
    "duplicate_excess_ratio_gt_hard_cap",
    "duplicate_exact_trade_rows_present",
    "trade_price_outside_1m_range",
    "off_session_trades_present",
    "rows_lt_10",
]

BAD_DATA_SUBFAMILIES = [
    "colapso_escala_rango",
    "integridad_estructural",
    "mixto_estructural_rango",
    "conflicto_ralo_o_sparse",
    "conflicto_rango_local",
]

MICROSTRUCTURE_TEXTURES = [
    "odd_lot_dominante",
    "duplicacion_textura",
    "conflicto_fino_1m",
    "sparse_o_ralo",
    "mixto_microestructura",
]

REVIEW_REHAB_CATEGORIES = [
    "strict_recoverable",
    "extended_only",
    "near_1x_but_not_recoverable",
    "not_near_1x",
]

OUTSIDE_BINS = [-0.01, 0, 1, 5, 20, 99.9999, np.inf]
OUTSIDE_LABELS = ["0", "(0,1]", "(1,5]", "(5,20]", "(20,100)", "100"]
DUP_BINS = [-0.01, 0, 1, 5, 10, np.inf]
DUP_LABELS = ["0", "(0,1]", "(1,5]", "(5,10]", ">10"]
ODD_BINS = [-0.01, 0, 5, 25, 50, np.inf]
ODD_LABELS = ["0", "(0,5]", "(5,25]", "(25,50]", ">50"]


def _issue_token_set(v) -> set[str]:
    if isinstance(v, np.ndarray):
        return {str(x) for x in v.tolist()}
    if isinstance(v, (list, tuple, set)):
        return {str(x) for x in v}
    if pd.isna(v) if np.isscalar(v) else False:
        return set()
    return {str(v)}


def _empty_counter(keys: list[str]) -> dict[str, int]:
    return {str(k): 0 for k in keys}


def _init_snapshot() -> dict:
    return {
        "policy_counts": _empty_counter(LABEL_ORDER),
        "year_label_counts": {},
        "scale_bucket_by_label": {label: {} for label in LABEL_ORDER},
        "outside_daily_bins": {label: _empty_counter(OUTSIDE_LABELS) for label in LABEL_ORDER},
        "outside_1m_bins": {label: _empty_counter(OUTSIDE_LABELS) for label in LABEL_ORDER},
        "duplicate_bins": {label: _empty_counter(DUP_LABELS) for label in LABEL_ORDER},
        "odd_lot_bins": {label: _empty_counter(ODD_LABELS) for label in LABEL_ORDER},
        "has_1m_reference": {label: {"with_1m": 0, "without_1m": 0} for label in LABEL_ORDER},
        "signature_counts": {label: _empty_counter(SIGNATURE_TOKENS) for label in LABEL_ORDER},
        "bad_data_subfamilies": _empty_counter(BAD_DATA_SUBFAMILIES),
        "review_microstructure_textures": _empty_counter(MICROSTRUCTURE_TEXTURES),
        "reference_scale_mismatch_buckets": {},
        "review_rehab_categories": _empty_counter(REVIEW_REHAB_CATEGORIES),
        "review_rehabilitation": {
            "review_total": 0,
            "strict": 0,
            "extended": 0,
        },
    }


def _bad_data_subfamily(row: pd.Series, tokens: set[str]) -> str:
    outside_daily = float(pd.to_numeric(row.get("outside_daily_regular_pct"), errors="coerce"))
    outside_1m = float(pd.to_numeric(row.get("outside_1m_regular_pct"), errors="coerce"))
    scale_bucket = str(row.get("scale_bucket_vw"))
    n_trades = pd.to_numeric(row.get("n_trades"), errors="coerce")
    n_trades = 0 if pd.isna(n_trades) else int(n_trades)
    structural = ("negative_or_zero_size_rows" in tokens) or ("duplicate_excess_ratio_gt_hard_cap" in tokens)
    daily_range = "trade_price_outside_daily_range" in tokens
    sparse = ("rows_lt_10" in tokens) or (n_trades < 10)
    scale_collapse = (scale_bucket == "nan") or (outside_daily >= 100) or (outside_1m >= 100)
    if structural and (daily_range or scale_collapse):
        return "mixto_estructural_rango"
    if structural:
        return "integridad_estructural"
    if sparse and not scale_collapse and not daily_range:
        return "conflicto_ralo_o_sparse"
    if scale_collapse or daily_range:
        return "colapso_escala_rango"
    return "conflicto_rango_local"


def _microstructure_texture(row: pd.Series, tokens: set[str]) -> str:
    odd = float(pd.to_numeric(row.get("odd_lot_trade_pct"), errors="coerce"))
    dup = float(pd.to_numeric(row.get("duplicate_exact_ratio_pct_raw"), errors="coerce"))
    out_daily = float(pd.to_numeric(row.get("outside_daily_regular_pct"), errors="coerce"))
    out_1m = float(pd.to_numeric(row.get("outside_1m_regular_pct"), errors="coerce"))
    n_trades = pd.to_numeric(row.get("n_trades"), errors="coerce")
    n_trades = 0 if pd.isna(n_trades) else int(n_trades)
    if odd > 25:
        return "odd_lot_dominante"
    if dup > 5 or "duplicate_exact_trade_rows_present" in tokens or "duplicate_excess_ratio_gt_threshold" in tokens:
        return "duplicacion_textura"
    if (out_1m > 5 and out_daily <= 1):
        return "conflicto_fino_1m"
    if ("rows_lt_10" in tokens) or (n_trades < 10):
        return "sparse_o_ralo"
    return "mixto_microestructura"


def _review_rehab_category(row: pd.Series) -> str:
    scale_ok = str(row.get("scale_bucket_vw")) in {"~1x", "near_1x"}
    vw_diff = float(pd.to_numeric(row.get("trade_vwap_vs_daily_vw_diff_pct_raw"), errors="coerce"))
    out_daily = float(pd.to_numeric(row.get("outside_daily_regular_pct"), errors="coerce"))
    out_1m = float(pd.to_numeric(row.get("outside_1m_regular_pct"), errors="coerce"))
    strict = scale_ok and (vw_diff <= 0.5) and (out_daily <= 1) and (out_1m <= 15)
    extended = scale_ok and (vw_diff <= 1.0) and (out_daily <= 2) and (out_1m <= 20)
    if strict:
        return "strict_recoverable"
    if extended:
        return "extended_only"
    if scale_ok:
        return "near_1x_but_not_recoverable"
    return "not_near_1x"


def _bucketize(series: pd.Series, bins: list[float], labels: list[str]) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce")
    return pd.cut(x, bins=bins, labels=labels, include_lowest=True, right=True).astype("object").fillna("nan")


def compute_trades_universe_snapshot(force: bool = False) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if SNAPSHOT_PATH.exists() and not force:
        return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    snapshot = _init_snapshot()
    policy = pd.read_parquet(CACHE_ROOT / "layer6_policy_summary_full.parquet")
    for _, row in policy.iterrows():
        snapshot["policy_counts"][str(row["acceptance_label"])] = int(row["files"])

    raw_paths = sorted(RAW_SHARDS_DIR.glob("*.parquet"))
    idx_paths = sorted(INDEX_SHARDS_DIR.glob("*.parquet"))

    for raw_path, idx_path in zip(raw_paths, idx_paths):
        raw = pd.read_parquet(
            raw_path,
            columns=[
                "file",
                "ticker",
                "date",
                "sample_stratum",
                "acceptance_label",
                "scale_bucket_vw",
                "outside_daily_regular_pct",
                "outside_1m_regular_pct",
                "duplicate_exact_ratio_pct_raw",
                "odd_lot_trade_pct",
                "has_1m_reference",
                "trade_vwap_vs_daily_vw_diff_pct_raw",
            ],
        )
        idx = pd.read_parquet(idx_path, columns=["file", "issues_list", "warns_list"])
        x = raw.merge(idx, on="file", how="left")
        x["year"] = pd.to_datetime(x["date"], errors="coerce").dt.year.astype("Int64").astype(str)

        # year x label counts
        year_counts = x.groupby(["year", "acceptance_label"]).size()
        for (year, label), count in year_counts.items():
            snapshot["year_label_counts"].setdefault(str(year), _empty_counter(LABEL_ORDER))
            snapshot["year_label_counts"][str(year)][str(label)] = snapshot["year_label_counts"][str(year)].get(str(label), 0) + int(count)

        # scale buckets
        scale_counts = x.groupby(["acceptance_label", "scale_bucket_vw"]).size()
        for (label, bucket), count in scale_counts.items():
            lab = str(label)
            buk = str(bucket)
            snapshot["scale_bucket_by_label"].setdefault(lab, {})
            snapshot["scale_bucket_by_label"][lab][buk] = snapshot["scale_bucket_by_label"][lab].get(buk, 0) + int(count)

        # binned metrics
        daily_bins = _bucketize(x["outside_daily_regular_pct"], OUTSIDE_BINS, OUTSIDE_LABELS)
        one_bins = _bucketize(x["outside_1m_regular_pct"], OUTSIDE_BINS, OUTSIDE_LABELS)
        dup_bins = _bucketize(x["duplicate_exact_ratio_pct_raw"], DUP_BINS, DUP_LABELS)
        odd_bins = _bucketize(x["odd_lot_trade_pct"], ODD_BINS, ODD_LABELS)
        x = x.assign(_daily_bin=daily_bins, _one_bin=one_bins, _dup_bin=dup_bins, _odd_bin=odd_bins)

        for label in LABEL_ORDER:
            sub = x.loc[x["acceptance_label"] == label]
            if sub.empty:
                continue
            for k, v in sub["_daily_bin"].value_counts(dropna=False).items():
                if k != "nan":
                    snapshot["outside_daily_bins"][label][str(k)] += int(v)
            for k, v in sub["_one_bin"].value_counts(dropna=False).items():
                if k != "nan":
                    snapshot["outside_1m_bins"][label][str(k)] += int(v)
            for k, v in sub["_dup_bin"].value_counts(dropna=False).items():
                if k != "nan":
                    snapshot["duplicate_bins"][label][str(k)] += int(v)
            for k, v in sub["_odd_bin"].value_counts(dropna=False).items():
                if k != "nan":
                    snapshot["odd_lot_bins"][label][str(k)] += int(v)
            with_1m = int(pd.to_numeric(sub["has_1m_reference"], errors="coerce").fillna(0).astype(int).eq(1).sum())
            without_1m = int(len(sub) - with_1m)
            snapshot["has_1m_reference"][label]["with_1m"] += with_1m
            snapshot["has_1m_reference"][label]["without_1m"] += without_1m

        # issue/warn signatures
        token_sets = x.apply(
            lambda r: _issue_token_set(r.get("issues_list")) | _issue_token_set(r.get("warns_list")),
            axis=1,
        )
        for label in LABEL_ORDER:
            sub_mask = x["acceptance_label"] == label
            if not sub_mask.any():
                continue
            sub_tokens = token_sets.loc[sub_mask]
            for token in SIGNATURE_TOKENS:
                snapshot["signature_counts"][label][token] += int(sub_tokens.apply(lambda s: token in s).sum())

        # fine families
        bad = x.loc[x["acceptance_label"] == "bad_data"].copy()
        if not bad.empty:
            bad_tokens = token_sets.loc[bad.index]
            for idx, row in bad.iterrows():
                fam = _bad_data_subfamily(row, bad_tokens.loc[idx])
                snapshot["bad_data_subfamilies"][fam] += 1

        micro = x.loc[x["acceptance_label"] == "review_microstructure"].copy()
        if not micro.empty:
            micro_tokens = token_sets.loc[micro.index]
            for idx, row in micro.iterrows():
                fam = _microstructure_texture(row, micro_tokens.loc[idx])
                snapshot["review_microstructure_textures"][fam] += 1

        scale = x.loc[x["acceptance_label"] == "reference_scale_mismatch", "scale_bucket_vw"].astype(str)
        if not scale.empty:
            vc = scale.value_counts()
            for bucket, count in vc.items():
                snapshot["reference_scale_mismatch_buckets"][str(bucket)] = snapshot["reference_scale_mismatch_buckets"].get(str(bucket), 0) + int(count)

        # review rehabilitation
        review = x.loc[x["acceptance_label"] == "review"].copy()
        if not review.empty:
            scale_ok = review["scale_bucket_vw"].astype(str).isin(["~1x", "near_1x"])
            vw_diff = pd.to_numeric(review["trade_vwap_vs_daily_vw_diff_pct_raw"], errors="coerce")
            out_daily = pd.to_numeric(review["outside_daily_regular_pct"], errors="coerce")
            out_1m = pd.to_numeric(review["outside_1m_regular_pct"], errors="coerce")
            strict = scale_ok & vw_diff.le(0.5) & out_daily.le(1) & out_1m.le(15)
            extended = scale_ok & vw_diff.le(1.0) & out_daily.le(2) & out_1m.le(20)
            snapshot["review_rehabilitation"]["review_total"] += int(len(review))
            snapshot["review_rehabilitation"]["strict"] += int(strict.fillna(False).sum())
            snapshot["review_rehabilitation"]["extended"] += int(extended.fillna(False).sum())
            for _, row in review.iterrows():
                snapshot["review_rehab_categories"][_review_rehab_category(row)] += 1

    SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot


def _policy_df(snapshot: dict) -> pd.DataFrame:
    return pd.DataFrame(
        [{"acceptance_label": k, "files": v} for k, v in snapshot["policy_counts"].items()]
    ).sort_values("files", ascending=False)


def _year_label_df(snapshot: dict) -> pd.DataFrame:
    rows = []
    for year, labels in snapshot["year_label_counts"].items():
        row = {"year": year}
        row.update(labels)
        rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["year_int"] = pd.to_numeric(df["year"], errors="coerce")
    return df.sort_values("year_int").drop(columns=["year_int"])


def _matrix_from_nested(nested: dict[str, dict[str, int]], labels: list[str]) -> pd.DataFrame:
    rows = []
    keys = set()
    for values in nested.values():
        keys.update(values.keys())
    for label in labels:
        row = {"acceptance_label": label}
        row.update({k: int(nested.get(label, {}).get(k, 0)) for k in sorted(keys)})
        rows.append(row)
    return pd.DataFrame(rows).set_index("acceptance_label")


def _normalize_rows(df: pd.DataFrame) -> pd.DataFrame:
    denom = df.sum(axis=1).replace(0, np.nan)
    return df.div(denom, axis=0).fillna(0.0)


def render_trades_universe_assets(force: bool = False) -> dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot = compute_trades_universe_snapshot(force=force)
    paths: dict[str, str] = {}

    # 00 distribution
    policy = _policy_df(snapshot)
    policy["pct"] = 100.0 * policy["files"] / policy["files"].sum()
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(policy["acceptance_label"], policy["files"], color=["#4c72b0", "#55a868", "#dd8452", "#c44e52", "#8172b2", "#937860", "#64b5cd"])
    ax.set_title("Trades 57f | distribucion final por acceptance_label")
    ax.set_ylabel("files")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.2)
    for i, (_, r) in enumerate(policy.iterrows()):
        ax.text(i, r["files"], f"{int(r['files']):,}\n{r['pct']:.3f}%", ha="center", va="bottom", fontsize=9)
    p = OUT_DIR / "00_acceptance_distribution.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["acceptance_distribution"] = str(p)

    # 01 yearly mix
    yearly = _year_label_df(snapshot)
    if not yearly.empty:
        plot_df = yearly.set_index("year")[[c for c in LABEL_ORDER if c in yearly.columns]]
        fig, ax = plt.subplots(figsize=(14, 6))
        plot_df.plot(kind="bar", stacked=True, ax=ax, width=0.9)
        ax.set_title("Trades 57f | mezcla anual de acceptance_label")
        ax.set_ylabel("files")
        ax.set_xlabel("year")
        ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
        ax.grid(axis="y", alpha=0.2)
        p = OUT_DIR / "01_yearly_acceptance_mix.png"
        fig.savefig(p, dpi=140, bbox_inches="tight")
        plt.close(fig)
        paths["yearly_acceptance_mix"] = str(p)

    # 02 scale buckets
    scale = _matrix_from_nested(snapshot["scale_bucket_by_label"], LABEL_ORDER)
    top_scale = scale.sum(axis=0).sort_values(ascending=False).head(8).index.tolist()
    fig, ax = plt.subplots(figsize=(13, 6))
    _normalize_rows(scale[top_scale]).plot(kind="bar", stacked=True, ax=ax, width=0.9)
    ax.set_title("Trades 57f | mezcla relativa de scale_bucket_vw por label")
    ax.set_ylabel("fraccion dentro del label")
    ax.set_xlabel("acceptance_label")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
    ax.grid(axis="y", alpha=0.2)
    p = OUT_DIR / "02_scale_bucket_mix_by_label.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["scale_bucket_mix_by_label"] = str(p)

    # 03 signatures matrix
    signatures = _matrix_from_nested(snapshot["signature_counts"], LABEL_ORDER)
    fig, ax = plt.subplots(figsize=(13, 6))
    _normalize_rows(signatures[SIGNATURE_TOKENS]).plot(kind="bar", stacked=True, ax=ax, width=0.9)
    ax.set_title("Trades 57f | mezcla relativa de firmas duras por label")
    ax.set_ylabel("fraccion dentro del label")
    ax.set_xlabel("acceptance_label")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
    ax.grid(axis="y", alpha=0.2)
    p = OUT_DIR / "03_signature_mix_by_label.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["signature_mix_by_label"] = str(p)

    # 04 outside daily bins
    daily_bins = _matrix_from_nested(snapshot["outside_daily_bins"], LABEL_ORDER)
    fig, ax = plt.subplots(figsize=(13, 6))
    _normalize_rows(daily_bins[OUTSIDE_LABELS]).plot(kind="bar", stacked=True, ax=ax, width=0.9)
    ax.set_title("Trades 57f | severidad outside_daily_regular_pct por label")
    ax.set_ylabel("fraccion dentro del label")
    ax.set_xlabel("acceptance_label")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
    ax.grid(axis="y", alpha=0.2)
    p = OUT_DIR / "04_outside_daily_severity_by_label.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["outside_daily_severity_by_label"] = str(p)

    # 05 outside 1m bins
    one_bins = _matrix_from_nested(snapshot["outside_1m_bins"], LABEL_ORDER)
    fig, ax = plt.subplots(figsize=(13, 6))
    _normalize_rows(one_bins[OUTSIDE_LABELS]).plot(kind="bar", stacked=True, ax=ax, width=0.9)
    ax.set_title("Trades 57f | severidad outside_1m_regular_pct por label")
    ax.set_ylabel("fraccion dentro del label")
    ax.set_xlabel("acceptance_label")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
    ax.grid(axis="y", alpha=0.2)
    p = OUT_DIR / "05_outside_1m_severity_by_label.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["outside_1m_severity_by_label"] = str(p)

    # 06 duplicate bins
    dup = _matrix_from_nested(snapshot["duplicate_bins"], LABEL_ORDER)
    fig, ax = plt.subplots(figsize=(13, 6))
    _normalize_rows(dup[DUP_LABELS]).plot(kind="bar", stacked=True, ax=ax, width=0.9)
    ax.set_title("Trades 57f | severidad de duplicacion exacta por label")
    ax.set_ylabel("fraccion dentro del label")
    ax.set_xlabel("acceptance_label")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
    ax.grid(axis="y", alpha=0.2)
    p = OUT_DIR / "06_duplicate_severity_by_label.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["duplicate_severity_by_label"] = str(p)

    # 07 odd lot bins
    odd = _matrix_from_nested(snapshot["odd_lot_bins"], LABEL_ORDER)
    fig, ax = plt.subplots(figsize=(13, 6))
    _normalize_rows(odd[ODD_LABELS]).plot(kind="bar", stacked=True, ax=ax, width=0.9)
    ax.set_title("Trades 57f | severidad de odd_lot_trade_pct por label")
    ax.set_ylabel("fraccion dentro del label")
    ax.set_xlabel("acceptance_label")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
    ax.grid(axis="y", alpha=0.2)
    p = OUT_DIR / "07_odd_lot_severity_by_label.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["odd_lot_severity_by_label"] = str(p)

    # 08 has_1m
    has_1m = pd.DataFrame(snapshot["has_1m_reference"]).T.reindex(LABEL_ORDER)
    fig, ax = plt.subplots(figsize=(12, 5))
    _normalize_rows(has_1m[["with_1m", "without_1m"]]).plot(kind="bar", stacked=True, ax=ax, width=0.9, color=["#4c72b0", "#c44e52"])
    ax.set_title("Trades 57f | cobertura de arbitro 1m por label")
    ax.set_ylabel("fraccion dentro del label")
    ax.set_xlabel("acceptance_label")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
    ax.grid(axis="y", alpha=0.2)
    p = OUT_DIR / "08_has_1m_reference_by_label.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["has_1m_reference_by_label"] = str(p)

    # 09 rehabilitation waterfall
    rr = snapshot["review_rehabilitation"]
    review_total = rr["review_total"]
    strict = rr["strict"]
    extended = rr["extended"]
    remaining_strict = review_total - strict
    extra_extended = extended - strict
    remaining_extended = review_total - extended
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = [review_total, strict, remaining_strict, extra_extended, remaining_extended]
    labels = ["review total", "strict recoverable", "strict non-rehab", "extra extended", "extended non-rehab"]
    colors = ["#4c72b0", "#55a868", "#c44e52", "#8172b2", "#dd8452"]
    ax.bar(labels, bars, color=colors)
    ax.set_title("Trades 57f | rehabilitacion de review")
    ax.set_ylabel("files")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.2)
    for i, v in enumerate(bars):
        pct = 100.0 * v / review_total if review_total else 0.0
        ax.text(i, v, f"{v:,}\n{pct:.2f}%", ha="center", va="bottom", fontsize=9)
    p = OUT_DIR / "09_review_rehabilitation_waterfall.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["review_rehabilitation_waterfall"] = str(p)

    # 10 bad_data visual subfamilies
    bad_sub = pd.Series(snapshot["bad_data_subfamilies"]).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(bad_sub.index, bad_sub.values, color="#c44e52")
    ax.set_title("Trades 57f | `bad_data` por subfamilia visual")
    ax.set_ylabel("files")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.2)
    total_bad = max(int(snapshot["policy_counts"].get("bad_data", 0)), 1)
    for i, v in enumerate(bad_sub.values):
        ax.text(i, v, f"{int(v):,}\n{100.0*float(v)/total_bad:.2f}%", ha="center", va="bottom", fontsize=9)
    p = OUT_DIR / "10_bad_data_visual_subfamilies.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["bad_data_visual_subfamilies"] = str(p)

    # 11 review_microstructure textures
    micro = pd.Series(snapshot["review_microstructure_textures"]).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(micro.index, micro.values, color="#dd8452")
    ax.set_title("Trades 57f | `review_microstructure` por textura dominante")
    ax.set_ylabel("files")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.2)
    total_micro = max(int(snapshot["policy_counts"].get("review_microstructure", 0)), 1)
    for i, v in enumerate(micro.values):
        ax.text(i, v, f"{int(v):,}\n{100.0*float(v)/total_micro:.2f}%", ha="center", va="bottom", fontsize=9)
    p = OUT_DIR / "11_review_microstructure_textures.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["review_microstructure_textures"] = str(p)

    # 12 reference scale buckets detail
    ref_scale = pd.Series(snapshot["reference_scale_mismatch_buckets"]).sort_values(ascending=False)
    top_ref_scale = ref_scale.head(10)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(top_ref_scale.index, top_ref_scale.values, color="#55a868")
    ax.set_title("Trades 57f | `reference_scale_mismatch` por bucket de escala")
    ax.set_ylabel("files")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.2)
    total_ref = max(int(snapshot["policy_counts"].get("reference_scale_mismatch", 0)), 1)
    for i, v in enumerate(top_ref_scale.values):
        ax.text(i, v, f"{int(v):,}\n{100.0*float(v)/total_ref:.2f}%", ha="center", va="bottom", fontsize=9)
    p = OUT_DIR / "12_reference_scale_mismatch_buckets.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["reference_scale_mismatch_buckets"] = str(p)

    # 13 review rehabilitation categories
    review_cats = pd.Series(snapshot["review_rehab_categories"]).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(review_cats.index, review_cats.values, color="#8172b2")
    ax.set_title("Trades 57f | `review` por severidad interna de rehabilitacion")
    ax.set_ylabel("files")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.2)
    total_review = max(int(snapshot["policy_counts"].get("review", 0)), 1)
    for i, v in enumerate(review_cats.values):
        ax.text(i, v, f"{int(v):,}\n{100.0*float(v)/total_review:.2f}%", ha="center", va="bottom", fontsize=9)
    p = OUT_DIR / "13_review_rehabilitation_categories.png"
    fig.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    paths["review_rehabilitation_categories"] = str(p)

    return paths


def universe_overview_tables(force: bool = False) -> dict[str, pd.DataFrame]:
    snapshot = compute_trades_universe_snapshot(force=force)
    tables = {
        "policy": _policy_df(snapshot),
        "yearly": _year_label_df(snapshot),
        "scale": _matrix_from_nested(snapshot["scale_bucket_by_label"], LABEL_ORDER),
        "signatures": _matrix_from_nested(snapshot["signature_counts"], LABEL_ORDER),
        "outside_daily": _matrix_from_nested(snapshot["outside_daily_bins"], LABEL_ORDER),
        "outside_1m": _matrix_from_nested(snapshot["outside_1m_bins"], LABEL_ORDER),
        "duplicate": _matrix_from_nested(snapshot["duplicate_bins"], LABEL_ORDER),
        "odd_lot": _matrix_from_nested(snapshot["odd_lot_bins"], LABEL_ORDER),
        "has_1m": pd.DataFrame(snapshot["has_1m_reference"]).T.reindex(LABEL_ORDER),
        "review_rehabilitation": pd.DataFrame([snapshot["review_rehabilitation"]]),
        "bad_data_subfamilies": pd.DataFrame([snapshot["bad_data_subfamilies"]]),
        "review_microstructure_textures": pd.DataFrame([snapshot["review_microstructure_textures"]]),
        "reference_scale_mismatch_buckets": pd.DataFrame([snapshot["reference_scale_mismatch_buckets"]]),
        "review_rehab_categories": pd.DataFrame([snapshot["review_rehab_categories"]]),
    }
    return tables


def display_trades_universe_section(section: str = "resumen", force: bool = False) -> None:
    paths = render_trades_universe_assets(force=force)
    tables = universe_overview_tables(force=False)
    section = str(section)

    if section == "resumen":
        display(Markdown("## Resumen del universo `trades`"))
        display(Markdown("Responde a: cuanta masa hay, como se reparte, y por que `good` no mide la masa util real del bloque."))
        display(Image(paths["acceptance_distribution"]))
        display(tables["policy"])
        display(Image(paths["review_rehabilitation_waterfall"]))
        display(tables["review_rehabilitation"])
        return

    if section == "mezcla_anual":
        display(Markdown("## Mezcla anual"))
        display(Markdown("Responde a: si las familias cambian por periodo y si el problema se concentra en anos concretos o atraviesa el universo entero."))
        display(Image(paths["yearly_acceptance_mix"]))
        display(tables["yearly"].tail(15))
        return

    if section == "escala":
        display(Markdown("## Escala y comparabilidad"))
        display(Markdown("Responde a: donde domina el conflicto de escala y por que `reference_scale_mismatch` no debe confundirse con tape roto."))
        display(Image(paths["scale_bucket_mix_by_label"]))
        display(tables["scale"])
        return

    if section == "firmas_duras":
        display(Markdown("## Firmas duras"))
        display(Markdown("Responde a: que senales concretas dominan cada label y donde vive la cola de integridad estructural."))
        display(Image(paths["signature_mix_by_label"]))
        display(tables["signatures"])
        return

    if section == "outside_daily":
        display(Markdown("## Severidad frente a `daily`"))
        display(Markdown("Responde a: como de agresivo es el conflicto contra el arbitro diario dentro de cada label."))
        display(Image(paths["outside_daily_severity_by_label"]))
        display(tables["outside_daily"])
        return

    if section == "outside_1m":
        display(Markdown("## Severidad frente a `1m`"))
        display(Markdown("Responde a: como de agresivo es el conflicto contra el arbitro intradia fino dentro de cada label."))
        display(Image(paths["outside_1m_severity_by_label"]))
        display(tables["outside_1m"])
        return

    if section == "duplicacion":
        display(Markdown("## Duplicacion"))
        display(Markdown("Responde a: cuanto de la lectura vive en bursts y filas repetidas, no solo en precio."))
        display(Image(paths["duplicate_severity_by_label"]))
        display(tables["duplicate"])
        return

    if section == "odd_lot":
        display(Markdown("## Odd-lots"))
        display(Markdown("Responde a: hasta que punto la textura microestructural explica parte del conflicto."))
        display(Image(paths["odd_lot_severity_by_label"]))
        display(tables["odd_lot"])
        return

    if section == "cobertura_1m":
        display(Markdown("## Cobertura del arbitro `1m`"))
        display(Markdown("Responde a: donde el problema esta condicionado por falta de arbitro fino y donde no."))
        display(Image(paths["has_1m_reference_by_label"]))
        display(tables["has_1m"])
        return

    if section == "bad_data_subfamilias":
        display(Markdown("## `bad_data` por subfamilia visual"))
        display(Markdown("Responde a: que parte de `bad_data` se ve por colapso de escala/rango y que parte exige paneles de integridad estructural."))
        display(Image(paths["bad_data_visual_subfamilies"]))
        display(tables["bad_data_subfamilies"])
        return

    if section == "review_microstructure_texturas":
        display(Markdown("## `review_microstructure` por textura dominante"))
        display(Markdown("Responde a: si el bucket esta dominado por odd-lots, duplicacion, conflicto fino contra `1m` o sparsity."))
        display(Image(paths["review_microstructure_textures"]))
        display(tables["review_microstructure_textures"])
        return

    if section == "reference_scale_buckets":
        display(Markdown("## `reference_scale_mismatch` por bucket de escala"))
        display(Markdown("Responde a: cuales son las escalas dominantes del conflicto y si el bucket esta concentrado en unos pocos factores o disperso."))
        display(Image(paths["reference_scale_mismatch_buckets"]))
        display(tables["reference_scale_mismatch_buckets"])
        return

    if section == "review_rehab_detalle":
        display(Markdown("## `review` por severidad interna de rehabilitacion"))
        display(Markdown("Responde a: que parte de `review` cae en rehabilitacion estricta, que parte solo entra en la extendida y que masa sigue lejos de `~1x`."))
        display(Image(paths["review_rehabilitation_categories"]))
        display(tables["review_rehab_categories"])
        return

    raise ValueError(f"Seccion no soportada: {section}")
