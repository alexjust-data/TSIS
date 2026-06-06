from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Markdown, display


CURRENT_PARQUET_CD = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\trades_current.parquet"
)
LOADER_SCRIPT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code\00_load_trades_run_artifacts.py"
)
TARGET_FILES_TOTAL = 2_328
ARTIFACT_DIR = Path(__file__).resolve().parent / "60_layer1_zero_negative_price_split_artifacts"


def _load_handle():
    mod = runpy.run_path(str(LOADER_SCRIPT))
    return mod["make_trades_audit_handle"](CURRENT_PARQUET_CD)


def _classify_file_prices(file_path: str | Path) -> dict:
    x = pd.read_parquet(Path(file_path), columns=["price"])
    s = pd.to_numeric(x["price"], errors="coerce").dropna()

    has_zero = bool((s == 0).any())
    neg = s[s < 0]
    has_negative = not neg.empty

    return {
        "has_zero": has_zero,
        "has_negative": has_negative,
        "negative_rows": int(len(neg)),
        "min_negative": float(neg.min()) if has_negative else np.nan,
        "negative_values": neg.to_numpy(dtype=float, copy=True),
    }


def build_layer1_zero_negative_price_scan(
    batch_size: int = 50_000,
    max_files: int | None = None,
    progress_every: int = 50_000,
) -> tuple[pd.DataFrame, np.ndarray]:
    handle = _load_handle()

    rows: list[dict] = []
    negative_arrays: list[np.ndarray] = []
    seen = 0

    cols = ["file", "ticker", "date", "severity", "metrics_json"]
    for batch in handle.stream(columns=cols, batch_size=batch_size, normalize=True):
        if "m.negative_or_zero_price_rows" not in batch.columns:
            continue

        sub = batch.loc[pd.to_numeric(batch["m.negative_or_zero_price_rows"], errors="coerce").fillna(0) > 0].copy()
        if sub.empty:
            continue

        for row in sub.itertuples(index=False):
            info = _classify_file_prices(row.file)
            rows.append(
                {
                    "file": row.file,
                    "ticker": getattr(row, "ticker", None),
                    "date": getattr(row, "date", None),
                    "severity": getattr(row, "severity", None),
                    "has_zero": info["has_zero"],
                    "has_negative": info["has_negative"],
                    "negative_rows": info["negative_rows"],
                    "min_negative": info["min_negative"],
                    "bucket": (
                        "both"
                        if info["has_zero"] and info["has_negative"]
                        else "zero_only"
                        if info["has_zero"]
                        else "negative_only"
                        if info["has_negative"]
                        else "unclassified"
                    ),
                }
            )
            if info["has_negative"]:
                negative_arrays.append(info["negative_values"])

            seen += 1
            if progress_every and seen % progress_every == 0:
                print(f"processed_files={seen:,}")
            if max_files is not None and seen >= int(max_files):
                break

        if max_files is not None and seen >= int(max_files):
            break

    out = pd.DataFrame(rows)
    negatives = np.concatenate(negative_arrays) if negative_arrays else np.array([], dtype=float)
    return out, negatives


def _artifact_paths() -> dict[str, Path]:
    return {
        "scan": ARTIFACT_DIR / "layer1_zero_negative_price_scan.parquet",
        "negative_values": ARTIFACT_DIR / "layer1_price_negative_values.parquet",
        "summary": ARTIFACT_DIR / "layer1_zero_negative_price_summary.parquet",
        "manifest": ARTIFACT_DIR / "manifest.json",
    }


def persist_layer1_zero_negative_price_artifacts(scan_df: pd.DataFrame, negative_values: np.ndarray) -> dict[str, Path]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    paths = _artifact_paths()

    summary = (
        scan_df.groupby("bucket", observed=False)
        .agg(
            files=("file", "size"),
            files_pct=("file", lambda s: 100.0 * len(s) / len(scan_df) if len(scan_df) else np.nan),
        )
        .reset_index()
        .sort_values("files", ascending=False)
    )
    neg_df = pd.DataFrame({"negative_value": pd.Series(negative_values, dtype=float)})

    scan_df.to_parquet(paths["scan"], index=False)
    neg_df.to_parquet(paths["negative_values"], index=False)
    summary.to_parquet(paths["summary"], index=False)

    manifest = {
        "artifact_dir": str(ARTIFACT_DIR),
        "files_classified": int(len(scan_df)),
        "target_files_total": TARGET_FILES_TOTAL,
        "negative_rows_total": int(len(negative_values)),
        "artifacts": {k: str(v) for k, v in paths.items() if k != "manifest"},
    }
    paths["manifest"].write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return paths


def plot_zero_negative_pie(scan_df: pd.DataFrame, figsize=(4.2, 4.2)) -> None:
    counts = (
        scan_df["bucket"]
        .value_counts()
        .reindex(["zero_only", "negative_only", "both", "unclassified"], fill_value=0)
    )
    counts = counts[counts > 0]

    colors = {
        "zero_only": "#4C72B0",
        "negative_only": "#C44E52",
        "both": "#DD8452",
        "unclassified": "#8C8C8C",
    }
    labels = {
        "zero_only": "price == 0",
        "negative_only": "price < 0",
        "both": "price == 0 y price < 0",
        "unclassified": "sin clasificar",
    }

    fig, ax = plt.subplots(figsize=figsize)
    ax.pie(
        counts.values,
        labels=[labels[k] for k in counts.index],
        autopct=lambda p: f"{p:.2f}%\n({int(round(p * counts.sum() / 100.0)):,})",
        startangle=90,
        colors=[colors[k] for k in counts.index],
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    ax.set_title(f"Files con price <= 0 | total={int(counts.sum()):,}")
    plt.tight_layout()
    plt.show()


def plot_negative_distribution(negative_values: np.ndarray) -> None:
    if len(negative_values) == 0:
        display(Markdown("No hay valores `price < 0` en estos files."))
        return

    s = pd.Series(negative_values, dtype=float).dropna().sort_values()
    abs_s = (-s).sort_values().to_numpy()
    survival = 1.0 - (np.arange(1, len(abs_s) + 1) / len(abs_s))
    survival = np.clip(survival, 1e-6, None)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    axes[0].hist(s.to_numpy(), bins=min(40, max(10, len(s) // 5 if len(s) > 50 else len(s))), density=True, alpha=0.8, color="#C44E52", edgecolor="white")
    axes[0].axvline(float(s.mean()), color="black", linestyle="--", linewidth=1, label=f"mean={s.mean():.4g}")
    axes[0].set_title("Distribución de price negativos")
    axes[0].set_xlabel("price < 0")
    axes[0].set_ylabel("densidad")
    axes[0].legend()

    axes[1].plot(abs_s, survival, color="#4C72B0", linewidth=1.5)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_title("Cola de negatividad")
    axes[1].set_xlabel("|price| negativo")
    axes[1].set_ylabel("P(X > x) aprox.")
    axes[1].grid(True, alpha=0.2)

    plt.tight_layout()
    plt.show()


def run_layer1_zero_negative_price_split(
    head_rows: int = 15,
    batch_size: int = 50_000,
    max_files: int | None = None,
) -> tuple[pd.DataFrame, np.ndarray]:
    scan_df, negative_values = build_layer1_zero_negative_price_scan(
        batch_size=batch_size,
        max_files=max_files,
    )
    artifact_paths = persist_layer1_zero_negative_price_artifacts(scan_df, negative_values)

    total = len(scan_df)
    display(Markdown(
        f"**Separación global de files con `price <= 0`**  \n"
        f"**files clasificados:** `{total:,}`"
    ))

    if max_files is None and total != TARGET_FILES_TOTAL:
        display(Markdown(
            f"**Aviso:** el total clasificado es `{total:,}` y debería cerrar contra `{TARGET_FILES_TOTAL:,}`."
        ))
    display(Markdown(
        "**Artefactos numéricos generados**  \n"
        f"`scan`: `{artifact_paths['scan']}`  \n"
        f"`negative_values`: `{artifact_paths['negative_values']}`  \n"
        f"`summary`: `{artifact_paths['summary']}`  \n"
        f"`manifest`: `{artifact_paths['manifest']}`"
    ))

    plot_zero_negative_pie(scan_df)

    summary = pd.read_parquet(artifact_paths["summary"])
    display(summary)

    zero_examples = scan_df.loc[scan_df["bucket"] == "zero_only"].head(head_rows)
    neg_examples = scan_df.loc[scan_df["bucket"] == "negative_only"].head(head_rows)
    both_examples = scan_df.loc[scan_df["bucket"] == "both"].head(head_rows)

    display(Markdown(f"**Ejemplos `price == 0`** `head({head_rows})`"))
    display(zero_examples)
    display(Markdown(f"**Ejemplos `price < 0`** `head({head_rows})`"))
    display(neg_examples)
    display(Markdown(f"**Ejemplos `price == 0 y price < 0`** `head({head_rows})`"))
    display(both_examples)

    plot_negative_distribution(negative_values)

    if len(negative_values):
        neg_stats = pd.DataFrame([{
            "negative_rows_total": int(len(negative_values)),
            "mean_negative": float(np.mean(negative_values)),
            "min_negative": float(np.min(negative_values)),
            "p01": float(np.quantile(negative_values, 0.01)),
            "p50": float(np.quantile(negative_values, 0.50)),
            "p95": float(np.quantile(negative_values, 0.95)),
            "p99": float(np.quantile(negative_values, 0.99)),
            "max_negative": float(np.max(negative_values)),
        }])
        display(Markdown("**Resumen de negatividad real (`price < 0`)**"))
        display(neg_stats)

    return scan_df, negative_values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--head-rows", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=50_000)
    parser.add_argument("--max-files", type=int, default=None)
    args = parser.parse_args()

    scan_df, negative_values = run_layer1_zero_negative_price_split(
        head_rows=args.head_rows,
        batch_size=args.batch_size,
        max_files=args.max_files,
    )

    print(f"files_classified={len(scan_df):,}")
    print(f"target_files_total={TARGET_FILES_TOTAL:,}")
    print(f"negative_rows_total={len(negative_values):,}")
    print(f"artifact_dir={ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
