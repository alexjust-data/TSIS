from __future__ import annotations

import argparse
import json
import runpy
from collections import Counter
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
ARTIFACT_DIR = Path(__file__).resolve().parent / "61_layer1_dtype_mismatch_audit_artifacts"
TARGET_FILES_TOTAL = 24_035
EXPECTED_DTYPE_MAP = {
    "ticker": "string",
    "date": "date",
    "timestamp": "timestamp[ns]",
    "price": "float",
    "size": "int",
    "exchange": "int",
    "conditions": "list[int]",
    "year": "int",
    "month": "int",
    "day": "date/string-date",
}
MOD00 = None


def _load_mod00():
    global MOD00
    if MOD00 is None:
        MOD00 = runpy.run_path(str(LOADER_SCRIPT))
    return MOD00


def _load_handle():
    mod = _load_mod00()
    return mod["make_trades_audit_handle"](CURRENT_PARQUET_CD)


def _parse_listish(value) -> list[str]:
    mod = _load_mod00()
    return [str(x) for x in mod["parse_listish"](value)]


def _parse_mismatch_token(token: str) -> tuple[str, str]:
    s = str(token).strip()
    if ":" in s:
        col, obs = s.split(":", 1)
        return col.strip(), obs.strip()
    return s, "unknown"


def build_layer1_dtype_mismatch_artifacts(
    batch_size: int = 50_000,
    max_files: int | None = None,
    progress_every: int = 50_000,
    example_cap: int = 500,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    handle = _load_handle()

    combo_counter = Counter()
    column_counter = Counter()
    observed_counter = Counter()
    examples: list[dict] = []
    seen_files = 0

    cols = ["file", "ticker", "date", "severity", "metrics_json"]
    for batch in handle.stream(columns=cols, batch_size=batch_size, normalize=True):
        mismatch_col = "m.dtype_mismatches"
        if mismatch_col not in batch.columns:
            continue

        parsed = batch[mismatch_col].map(_parse_listish)
        sub = batch.loc[parsed.map(len) > 0].copy()
        sub["dtype_tokens"] = parsed.loc[sub.index]
        if sub.empty:
            continue

        for row in sub.itertuples(index=False):
            file_tokens = []
            for token in row.dtype_tokens:
                column, observed_signature = _parse_mismatch_token(token)
                expected_dtype = EXPECTED_DTYPE_MAP.get(column, "unknown")
                combo_counter[(column, expected_dtype, observed_signature)] += 1
                column_counter[column] += 1
                observed_counter[observed_signature] += 1
                file_tokens.append(f"{column}:{observed_signature}")

                if len(examples) < example_cap:
                    examples.append(
                        {
                            "file": row.file,
                            "ticker": row.ticker,
                            "date": row.date,
                            "severity": row.severity,
                            "column": column,
                            "expected_dtype": expected_dtype,
                            "observed_signature": observed_signature,
                            "token": token,
                        }
                    )

            seen_files += 1
            if progress_every and seen_files % progress_every == 0:
                print(f"processed_files={seen_files:,}")
            if max_files is not None and seen_files >= int(max_files):
                break

        if max_files is not None and seen_files >= int(max_files):
            break

    summary = pd.DataFrame(
        [
            {
                "column": column,
                "expected_dtype": expected_dtype,
                "observed_signature": observed_signature,
                "files": files,
                "files_pct_within_dtype_mismatch": 100.0 * files / seen_files if seen_files else np.nan,
            }
            for (column, expected_dtype, observed_signature), files in combo_counter.items()
        ]
    ).sort_values(["files", "column", "observed_signature"], ascending=[False, True, True]).reset_index(drop=True)

    column_summary = pd.DataFrame(
        [{"column": col, "files": files} for col, files in column_counter.items()]
    ).sort_values(["files", "column"], ascending=[False, True]).reset_index(drop=True)

    examples_df = pd.DataFrame(examples)
    manifest = {
        "artifact_dir": str(ARTIFACT_DIR),
        "files_classified": int(seen_files),
        "target_files_total": TARGET_FILES_TOTAL,
        "columns_affected": int(len(column_counter)),
        "observed_signatures": int(len(observed_counter)),
    }
    return summary, column_summary, examples_df, manifest


def persist_layer1_dtype_mismatch_artifacts(
    summary: pd.DataFrame,
    column_summary: pd.DataFrame,
    examples_df: pd.DataFrame,
    manifest: dict,
) -> dict[str, Path]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary": ARTIFACT_DIR / "layer1_dtype_mismatch_summary.parquet",
        "column_summary": ARTIFACT_DIR / "layer1_dtype_mismatch_column_summary.parquet",
        "examples": ARTIFACT_DIR / "layer1_dtype_mismatch_examples.parquet",
        "manifest": ARTIFACT_DIR / "manifest.json",
    }
    summary.to_parquet(paths["summary"], index=False)
    column_summary.to_parquet(paths["column_summary"], index=False)
    examples_df.to_parquet(paths["examples"], index=False)
    paths["manifest"].write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return paths


def plot_dtype_mismatch_columns(column_summary: pd.DataFrame, top_n: int = 12) -> None:
    if column_summary.empty:
        return
    x = column_summary.head(top_n).sort_values("files", ascending=True)
    fig_height = max(4.5, 0.45 * len(x) + 1.5)
    fig, ax = plt.subplots(figsize=(8.5, fig_height))
    bars = ax.barh(x["column"], x["files"], height=0.4, color="#4C72B0")
    ax.set_title("Layer 1 | Dtype mismatch por columna")
    ax.set_xlabel("files")
    ax.set_ylabel("column")
    ax.grid(axis="x", alpha=0.2)
    for bar, value in zip(bars, x["files"]):
        ax.text(value, bar.get_y() + bar.get_height() / 2, f" {int(value):,}", ha="left", va="center", fontsize=8)
    plt.tight_layout()
    plt.show()


def render_layer1_dtype_mismatch_from_artifacts(head_rows: int = 15, top_n_columns: int = 12) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    paths = {
        "summary": ARTIFACT_DIR / "layer1_dtype_mismatch_summary.parquet",
        "column_summary": ARTIFACT_DIR / "layer1_dtype_mismatch_column_summary.parquet",
        "examples": ARTIFACT_DIR / "layer1_dtype_mismatch_examples.parquet",
        "manifest": ARTIFACT_DIR / "manifest.json",
    }
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    summary = pd.read_parquet(paths["summary"])
    column_summary = pd.read_parquet(paths["column_summary"])
    examples = pd.read_parquet(paths["examples"])

    display(Markdown(
        "**Layer 1 | Dtype mismatch**  \n"
        f"**files clasificados:** `{manifest['files_classified']:,}`  \n"
        f"**columns afectadas:** `{manifest['columns_affected']}`  \n"
        f"**observed signatures:** `{manifest['observed_signatures']}`  \n"
        f"`summary`: `{paths['summary']}`  \n"
        f"`column_summary`: `{paths['column_summary']}`  \n"
        f"`examples`: `{paths['examples']}`  \n"
        f"`manifest`: `{paths['manifest']}`"
    ))

    display(summary.head(head_rows))
    plot_dtype_mismatch_columns(column_summary, top_n=top_n_columns)
    display(Markdown(f"**Detalle top `head({head_rows})`**"))
    display(summary.head(head_rows))
    display(Markdown(f"**Ejemplos `head({head_rows})`**"))
    display(examples.head(head_rows))

    top_col = column_summary.iloc[0]["column"] if not column_summary.empty else "n/a"
    top_files = int(column_summary.iloc[0]["files"]) if not column_summary.empty else 0
    display(Markdown(
        f"El mismatch dominante está concentrado en la columna `{top_col}` con `{top_files:,}` files afectados. "
        "La tabla principal separa por columna y firma observada para distinguir deuda de normalización frente a ruptura dura de contrato."
    ))
    return summary, column_summary, examples, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=50_000)
    parser.add_argument("--max-files", type=int, default=None)
    parser.add_argument("--head-rows", type=int, default=15)
    parser.add_argument("--top-n-columns", type=int, default=12)
    args = parser.parse_args()

    summary, column_summary, examples, manifest = build_layer1_dtype_mismatch_artifacts(
        batch_size=args.batch_size,
        max_files=args.max_files,
    )
    persist_layer1_dtype_mismatch_artifacts(summary, column_summary, examples, manifest)
    print(f"files_classified={manifest['files_classified']:,}")
    print(f"target_files_total={TARGET_FILES_TOTAL:,}")
    print(f"columns_affected={manifest['columns_affected']}")
    print(f"observed_signatures={manifest['observed_signatures']}")
    print(f"artifact_dir={ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
