#!/usr/bin/env python3
"""Render price-free, blind visual evidence for Wake-up RTH calibration."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from wake_up_rth_core import atomic_json, load_config, sha256_file, utc_now


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--candidate-run-root", required=True, type=Path)
    parser.add_argument("--panel-root", required=True, type=Path)
    parser.add_argument("--max-cases", type=int)
    return parser.parse_args()


def minute_view(metrics: pd.DataFrame) -> pd.DataFrame:
    indexed = metrics.set_index("decision_timestamp_utc")
    columns = [
        "trade_count",
        "dollar_volume",
        "distinct_timestamp_clusters",
        "duplicate_trade_count",
        "restricted_or_unknown_trade_count",
    ]
    return indexed[columns].resample("1min").sum()


def render_case(blind_id, row, metrics, output, prior_seconds, post_seconds) -> None:
    metrics = metrics.copy()
    metrics["decision_timestamp_utc"] = pd.to_datetime(
        metrics["decision_timestamp_utc"], utc=True
    )
    onset = pd.Timestamp(row["candidate_timestamp_utc"])
    onset = onset.tz_localize("UTC") if onset.tzinfo is None else onset.tz_convert("UTC")
    minute = minute_view(metrics)
    zoom = metrics.loc[
        (metrics["decision_timestamp_utc"] >= onset - pd.Timedelta(seconds=prior_seconds))
        & (metrics["decision_timestamp_utc"] <= onset + pd.Timedelta(seconds=post_seconds))
    ].copy()

    fig, axes = plt.subplots(
        5, 1, figsize=(16, 13), constrained_layout=True,
        gridspec_kw={"height_ratios": [1.1, 1.1, 1.25, 1.25, 0.8]},
    )
    fig.suptitle(
        f"{blind_id} - blind evidence without price\n"
        "Vertical line marks the candidate second; it is not a positive label.",
        fontsize=14,
    )
    axes[0].plot(minute.index, minute["trade_count"], color="#1f77b4", lw=1.2)
    axes[0].plot(
        minute.index, minute["distinct_timestamp_clusters"],
        color="#2ca02c", lw=1.0, alpha=0.85,
    )
    axes[0].set_ylabel("trades / clusters\nper minute")
    axes[0].legend(["trades", "clusters"], loc="upper left", ncol=2)
    axes[1].bar(
        minute.index, minute["dollar_volume"], width=0.00055,
        color="#9467bd", alpha=0.8,
    )
    axes[1].set_ylabel("dollar volume\nper minute")
    axes[2].step(
        zoom["decision_timestamp_utc"], zoom["trade_count"],
        where="mid", color="#1f77b4", lw=1.0,
    )
    axes[2].scatter(
        zoom["decision_timestamp_utc"], zoom["distinct_timestamp_clusters"],
        s=np.clip(zoom["distinct_timestamp_clusters"].to_numpy() * 5 + 5, 5, 80),
        color="#2ca02c", alpha=0.7,
    )
    axes[2].set_ylabel("zoom: trades and\nclusters / second")
    axes[3].plot(
        zoom["decision_timestamp_utc"], zoom["dollar_volume"],
        color="#9467bd", lw=1.0,
    )
    axes[3].fill_between(
        zoom["decision_timestamp_utc"], 0, zoom["dollar_volume"],
        color="#9467bd", alpha=0.2,
    )
    axes[3].set_ylabel("zoom: dollar\nvolume / second")
    quality = (
        zoom["duplicate_trade_count"].astype(float)
        + zoom["restricted_or_unknown_trade_count"].astype(float)
    )
    axes[4].bar(
        zoom["decision_timestamp_utc"], quality, width=0.000008,
        color=np.where(quality > 0, "#d62728", "#bdbdbd"),
    )
    axes[4].set_ylabel("quality flags\nper second")
    axes[4].set_xlabel("UTC")
    for axis in axes:
        axis.axvline(onset, color="#ff7f0e", lw=2.0, ls="--")
        axis.grid(True, color="#e6e6e6", lw=0.6)
        axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=onset.tzinfo))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=140)
    plt.close(fig)


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    internal = pd.read_parquet(args.panel_root / "panel_internal_manifest.parquet")
    public = pd.read_parquet(args.panel_root / "panel_blind_manifest.parquet")
    if args.max_cases is not None:
        public = public.head(args.max_cases)
    lookup = internal.set_index("blind_case_id", drop=False)
    chart_root = args.panel_root / "charts"
    chart_root.mkdir(exist_ok=True)
    rendered = []
    for row in public.itertuples(index=False):
        blind_id = row.blind_case_id
        internal_row = lookup.loc[blind_id]
        metrics_path = (
            args.candidate_run_root / "session_metrics"
            / f"{internal_row['target_file_key']}.parquet"
        )
        output = chart_root / f"{blind_id}.png"
        render_case(
            blind_id, internal_row, pd.read_parquet(metrics_path), output,
            int(config["panel"]["zoom_prior_seconds"]),
            int(config["panel"]["zoom_post_seconds"]),
        )
        rendered.append(output.name)

    cards = []
    for blind_id in public["blind_case_id"]:
        escaped = html.escape(str(blind_id))
        cards.append(
            f'<article><h2>{escaped}</h2><a href="charts/{escaped}.png">'
            f'<img loading="lazy" src="charts/{escaped}.png" alt="{escaped}"></a></article>'
        )
    document = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Wake-up RTH - panel ciego sin precio</title><style>
body{font-family:Arial,sans-serif;margin:24px;background:#f5f5f5;color:#1d2733}
header{max-width:1100px;margin:auto} article{max-width:1500px;margin:24px auto;
background:white;padding:16px;box-shadow:0 1px 6px #bbb} img{width:100%;height:auto}
.warning{background:#fff3cd;border:1px solid #e0b400;padding:12px}
</style></head><body><header><h1>Wake-up RTH - galeria ciega sin precio</h1>
<p class="warning">Candidatos y controles estan mezclados. La linea naranja no es
una etiqueta. No use precio, Binding A, Binding B ni resultados futuros.</p></header>
""" + "\n".join(cards) + "\n</body></html>\n"
    (args.panel_root / "gallery.html").write_text(
        document, encoding="utf-8", newline="\n"
    )
    atomic_json(
        args.panel_root / "gallery_manifest.json",
        {
            "status": "COMPLETE",
            "created_at_utc": utc_now(),
            "config_path": str(args.config.resolve()),
            "config_sha256": sha256_file(args.config),
            "panel_manifest_sha256": sha256_file(
                args.panel_root / "panel_manifest.json"
            ),
            "script_path": str(Path(__file__).resolve()),
            "script_sha256": sha256_file(Path(__file__)),
            "rendered_case_count": len(rendered),
            "chart_files": rendered,
            "intraday_price_path_consumed": False,
            "price_displayed": False,
            "dollar_notional_displayed": True,
            "binding_a_consumed": False,
            "binding_b_consumed": False,
            "identity_exposed_in_charts": False,
        },
    )
    print(args.panel_root / "gallery.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
