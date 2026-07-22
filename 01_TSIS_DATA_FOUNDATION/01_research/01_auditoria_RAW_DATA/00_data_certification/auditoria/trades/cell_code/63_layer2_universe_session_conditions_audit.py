from __future__ import annotations

import argparse
import json
import runpy
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import Markdown, display


CURRENT_PARQUET_CD = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\trades_current.parquet"
)
LOADER_SCRIPT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code\00_load_trades_run_artifacts.py"
)
ARTIFACT_DIR = Path(__file__).resolve().parent / "63_layer2_universe_session_conditions_audit_artifacts"


def _load_mod00():
    return runpy.run_path(str(LOADER_SCRIPT))


def _load_handle():
    mod = _load_mod00()
    return mod["make_trades_audit_handle"](CURRENT_PARQUET_CD)


def _classify_session(ts_local: pd.Timestamp) -> str:
    hm = (ts_local.hour, ts_local.minute)
    if hm < (9, 30):
        return "premarket"
    if hm < (16, 0):
        return "regular"
    return "afterhours"


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


def build_layer2_universe_session_conditions_artifacts(batch_size: int = 50_000, progress_every: int = 500_000) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    handle = _load_handle()

    session_counter = Counter()
    combo_counter = Counter()
    code_counter = Counter()
    files_total = 0
    trades_total = 0

    cols = ["timestamp", "conditions"]
    for batch in handle.stream(columns=cols, batch_size=batch_size, normalize=False):
        files_total += len(batch)
        batch["timestamp"] = pd.to_datetime(batch["timestamp"], utc=False, errors="coerce")
        if str(batch["timestamp"].dtype).startswith("datetime64[ns,"):
            ts_local = batch["timestamp"].dt.tz_convert("America/New_York")
        else:
            ts_local = batch["timestamp"].dt.tz_localize("America/New_York", nonexistent="NaT", ambiguous="NaT")
        sessions = ts_local.map(lambda x: _classify_session(x) if pd.notna(x) else "unknown")
        session_counter.update(sessions.astype(str).tolist())

        conditions_key = batch["conditions"].map(_conditions_key)
        combo_counter.update(conditions_key.astype(str).tolist())
        for xs in batch["conditions"].map(_conditions_list):
            code_counter.update(xs)

        trades_total += len(batch)
        if progress_every and trades_total % progress_every < len(batch):
            print(f"processed_trades={trades_total:,}")

    session_summary = pd.DataFrame(
        [
            {"session": k, "trades": int(v), "trade_pct": 100.0 * v / trades_total if trades_total else 0.0}
            for k, v in session_counter.items()
        ]
    ).sort_values(["trades", "session"], ascending=[False, True]).reset_index(drop=True)

    combo_summary = (
        pd.DataFrame([{"conditions_key": k, "trades": int(v)} for k, v in combo_counter.items()])
        .sort_values(["trades", "conditions_key"], ascending=[False, True])
        .reset_index(drop=True)
    )

    code_summary = (
        pd.DataFrame([{"condition_code": k, "trades": int(v)} for k, v in code_counter.items()])
        .sort_values(["trades", "condition_code"], ascending=[False, True])
        .reset_index(drop=True)
    )

    manifest = {
        "artifact_dir": str(ARTIFACT_DIR),
        "trades_total": int(trades_total),
    }
    return session_summary, combo_summary, code_summary, manifest


def persist_layer2_universe_session_conditions_artifacts(
    session_summary: pd.DataFrame,
    combo_summary: pd.DataFrame,
    code_summary: pd.DataFrame,
    manifest: dict,
) -> dict[str, Path]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    paths = {
        "session_summary": ARTIFACT_DIR / "layer2_universe_session_summary.parquet",
        "combo_summary": ARTIFACT_DIR / "layer2_universe_conditions_combo_summary.parquet",
        "code_summary": ARTIFACT_DIR / "layer2_universe_condition_code_summary.parquet",
        "manifest": ARTIFACT_DIR / "manifest.json",
    }
    session_summary.to_parquet(paths["session_summary"], index=False)
    combo_summary.to_parquet(paths["combo_summary"], index=False)
    code_summary.to_parquet(paths["code_summary"], index=False)
    paths["manifest"].write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return paths


def plot_layer2_universe_session_mix(session_summary: pd.DataFrame, figsize=(7, 4)) -> None:
    if session_summary.empty:
        return
    x = session_summary.copy()
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(x["session"], x["trade_pct"], color=["#4C72B0", "#DD8452", "#55A868", "#8C8C8C"][: len(x)])
    ax.set_title("Capa 2 | Mezcla de sesión en el universo")
    ax.set_ylabel("pct de trades")
    ax.grid(axis="y", alpha=0.2)
    for bar, value in zip(bars, x["trade_pct"]):
        ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2f}%", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    plt.show()


def render_layer2_universe_session_conditions_from_artifacts(head_rows: int = 15, top_n_codes: int = 15) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    paths = {
        "session_summary": ARTIFACT_DIR / "layer2_universe_session_summary.parquet",
        "combo_summary": ARTIFACT_DIR / "layer2_universe_conditions_combo_summary.parquet",
        "code_summary": ARTIFACT_DIR / "layer2_universe_condition_code_summary.parquet",
        "manifest": ARTIFACT_DIR / "manifest.json",
    }
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    session_summary = pd.read_parquet(paths["session_summary"])
    combo_summary = pd.read_parquet(paths["combo_summary"])
    code_summary = pd.read_parquet(paths["code_summary"])

    display(Markdown(
        "**Capa 2 | Session + Conditions en el universo**  \n"
        f"**trades_total:** `{manifest['trades_total']:,}`  \n"
        f"`session_summary`: `{paths['session_summary']}`  \n"
        f"`combo_summary`: `{paths['combo_summary']}`  \n"
        f"`code_summary`: `{paths['code_summary']}`"
    ))
    display(session_summary)
    plot_layer2_universe_session_mix(session_summary)
    display(Markdown(f"**Top `conditions_key`** `head({head_rows})`"))
    display(combo_summary.head(head_rows))
    display(Markdown(f"**Top `condition_code`** `head({top_n_codes})`"))
    display(code_summary.head(top_n_codes))
    return session_summary, combo_summary, code_summary, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=50_000)
    parser.add_argument("--progress-every", type=int, default=500_000)
    args = parser.parse_args()

    session_summary, combo_summary, code_summary, manifest = build_layer2_universe_session_conditions_artifacts(
        batch_size=args.batch_size,
        progress_every=args.progress_every,
    )
    persist_layer2_universe_session_conditions_artifacts(session_summary, combo_summary, code_summary, manifest)
    print(f"trades_total={manifest['trades_total']:,}")
    print(f"artifact_dir={ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
