from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Markdown, display


CACHE_DIR = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache"
)
SAMPLE_INDEX_PATH = CACHE_DIR / "sample_index.parquet"
ARTIFACT_DIR = Path(__file__).resolve().parent / "62_layer2_session_conditions_audit_artifacts"
NY_TZ = "America/New_York"


def _conditions_key(value) -> str:
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "[]"
    return str(value)


def _conditions_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value]
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return [str(value)]


def _classify_session(ts_local: pd.Timestamp) -> str:
    hm = (ts_local.hour, ts_local.minute)
    if hm < (9, 30):
        return "premarket"
    if hm < (16, 0):
        return "regular"
    return "afterhours"


def build_layer2_session_conditions_artifacts(progress_every: int = 50) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    sample_index = pd.read_parquet(SAMPLE_INDEX_PATH)

    file_rows: list[dict] = []
    combo_counter = Counter()
    code_counter = Counter()

    for idx, row in enumerate(sample_index.itertuples(index=False), start=1):
        trades = pd.read_parquet(Path(str(row.file)), columns=["timestamp", "conditions"])
        trades["timestamp"] = pd.to_datetime(trades["timestamp"], utc=False, errors="coerce")
        if str(trades["timestamp"].dtype).startswith("datetime64[ns,"):
            ts_local = trades["timestamp"].dt.tz_convert(NY_TZ)
        else:
            ts_local = trades["timestamp"].dt.tz_localize(NY_TZ, nonexistent="NaT", ambiguous="NaT")
        trades["session"] = ts_local.map(lambda x: _classify_session(x) if pd.notna(x) else None)

        n = len(trades)
        premarket_n = int((trades["session"] == "premarket").sum())
        regular_n = int((trades["session"] == "regular").sum())
        afterhours_n = int((trades["session"] == "afterhours").sum())
        session_known_n = premarket_n + regular_n + afterhours_n

        trades["conditions_key"] = trades["conditions"].map(_conditions_key)
        for sig, count in trades["conditions_key"].value_counts().items():
            combo_counter[sig] += int(count)

        for xs in trades["conditions"].map(_conditions_list):
            for code in xs:
                code_counter[code] += 1

        file_rows.append(
            {
                "file": row.file,
                "ticker": row.ticker,
                "date": row.date,
                "sample_stratum": row.sample_stratum,
                "trades_total": int(n),
                "premarket_trades": premarket_n,
                "regular_trades": regular_n,
                "afterhours_trades": afterhours_n,
                "session_known_trades": int(session_known_n),
                "premarket_trade_pct": 100.0 * premarket_n / n if n else np.nan,
                "regular_trade_pct": 100.0 * regular_n / n if n else np.nan,
                "afterhours_trade_pct": 100.0 * afterhours_n / n if n else np.nan,
                "top_conditions_key": trades["conditions_key"].mode().iloc[0] if n else "[]",
                "conditions_combo_nunique": int(trades["conditions_key"].nunique(dropna=True)),
            }
        )

        if progress_every and idx % progress_every == 0:
            print(f"processed_files={idx:,}")

    file_metrics = pd.DataFrame(file_rows)
    session_summary = pd.DataFrame(
        [
            {"metric": "sample_files", "value": int(len(file_metrics))},
            {"metric": "median_premarket_trade_pct", "value": pd.to_numeric(file_metrics["premarket_trade_pct"], errors="coerce").median()},
            {"metric": "median_regular_trade_pct", "value": pd.to_numeric(file_metrics["regular_trade_pct"], errors="coerce").median()},
            {"metric": "median_afterhours_trade_pct", "value": pd.to_numeric(file_metrics["afterhours_trade_pct"], errors="coerce").median()},
            {"metric": "p75_premarket_trade_pct", "value": pd.to_numeric(file_metrics["premarket_trade_pct"], errors="coerce").quantile(0.75)},
            {"metric": "p75_afterhours_trade_pct", "value": pd.to_numeric(file_metrics["afterhours_trade_pct"], errors="coerce").quantile(0.75)},
        ]
    )
    combo_summary = (
        pd.DataFrame([{"conditions_key": k, "trades": v} for k, v in combo_counter.items()])
        .sort_values(["trades", "conditions_key"], ascending=[False, True])
        .reset_index(drop=True)
    )
    code_summary = (
        pd.DataFrame([{"condition_code": k, "trades": v} for k, v in code_counter.items()])
        .sort_values(["trades", "condition_code"], ascending=[False, True])
        .reset_index(drop=True)
    )
    manifest = {
        "artifact_dir": str(ARTIFACT_DIR),
        "sample_files": int(len(file_metrics)),
        "source_sample_index": str(SAMPLE_INDEX_PATH),
    }
    return session_summary, file_metrics, combo_summary, code_summary, manifest


def persist_layer2_session_conditions_artifacts(
    session_summary: pd.DataFrame,
    file_metrics: pd.DataFrame,
    combo_summary: pd.DataFrame,
    code_summary: pd.DataFrame,
    manifest: dict,
) -> dict[str, Path]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    paths = {
        "session_summary": ARTIFACT_DIR / "layer2_session_summary.parquet",
        "file_metrics": ARTIFACT_DIR / "layer2_session_file_metrics.parquet",
        "combo_summary": ARTIFACT_DIR / "layer2_conditions_combo_summary.parquet",
        "code_summary": ARTIFACT_DIR / "layer2_condition_code_summary.parquet",
        "manifest": ARTIFACT_DIR / "manifest.json",
    }
    session_summary.to_parquet(paths["session_summary"], index=False)
    file_metrics.to_parquet(paths["file_metrics"], index=False)
    combo_summary.to_parquet(paths["combo_summary"], index=False)
    code_summary.to_parquet(paths["code_summary"], index=False)
    paths["manifest"].write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return paths


def plot_layer2_session_mix(file_metrics: pd.DataFrame, figsize=(9, 4.5)) -> None:
    if file_metrics.empty:
        return
    cols = ["premarket_trade_pct", "regular_trade_pct", "afterhours_trade_pct"]
    labels = ["premarket", "regular", "afterhours"]
    medians = [pd.to_numeric(file_metrics[c], errors="coerce").median() for c in cols]
    p25 = [pd.to_numeric(file_metrics[c], errors="coerce").quantile(0.25) for c in cols]
    p75 = [pd.to_numeric(file_metrics[c], errors="coerce").quantile(0.75) for c in cols]

    x = np.arange(len(labels))
    err_low = np.array(medians) - np.array(p25)
    err_high = np.array(p75) - np.array(medians)

    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(x, medians, color=["#DD8452", "#4C72B0", "#55A868"], width=0.5)
    ax.errorbar(x, medians, yerr=[err_low, err_high], fmt="none", ecolor="black", capsize=4, linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("pct de trades por file")
    ax.set_title("Capa 2 | Mezcla de sesión en la muestra")
    ax.grid(axis="y", alpha=0.2)
    for bar, value in zip(bars, medians):
        ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2f}%", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    plt.show()


def render_layer2_session_conditions_from_artifacts(head_rows: int = 15, top_n_codes: int = 15) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    paths = {
        "session_summary": ARTIFACT_DIR / "layer2_session_summary.parquet",
        "file_metrics": ARTIFACT_DIR / "layer2_session_file_metrics.parquet",
        "combo_summary": ARTIFACT_DIR / "layer2_conditions_combo_summary.parquet",
        "code_summary": ARTIFACT_DIR / "layer2_condition_code_summary.parquet",
        "manifest": ARTIFACT_DIR / "manifest.json",
    }
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    session_summary = pd.read_parquet(paths["session_summary"])
    file_metrics = pd.read_parquet(paths["file_metrics"])
    combo_summary = pd.read_parquet(paths["combo_summary"])
    code_summary = pd.read_parquet(paths["code_summary"])

    display(Markdown(
        "**Capa 2 | Session + Conditions**  \n"
        f"**sample_files:** `{manifest['sample_files']:,}`  \n"
        f"`session_summary`: `{paths['session_summary']}`  \n"
        f"`file_metrics`: `{paths['file_metrics']}`  \n"
        f"`combo_summary`: `{paths['combo_summary']}`  \n"
        f"`code_summary`: `{paths['code_summary']}`"
    ))
    display(session_summary)
    plot_layer2_session_mix(file_metrics)
    display(Markdown(f"**Top `conditions_key`** `head({head_rows})`"))
    display(combo_summary.head(head_rows))
    display(Markdown(f"**Top `condition_code`** `head({top_n_codes})`"))
    display(code_summary.head(top_n_codes))
    display(Markdown(f"**Ejemplos file-level** `head({head_rows})`"))
    display(file_metrics.sort_values(["regular_trade_pct", "premarket_trade_pct"], ascending=[False, False]).head(head_rows))
    return session_summary, file_metrics, combo_summary, code_summary, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--progress-every", type=int, default=50)
    args = parser.parse_args()

    session_summary, file_metrics, combo_summary, code_summary, manifest = build_layer2_session_conditions_artifacts(
        progress_every=args.progress_every,
    )
    persist_layer2_session_conditions_artifacts(session_summary, file_metrics, combo_summary, code_summary, manifest)
    print(f"sample_files={manifest['sample_files']:,}")
    print(f"artifact_dir={ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
