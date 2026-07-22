from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import pyarrow.parquet as pq
import seaborn as sns
from IPython.display import Markdown, display


SEVERITY_ORDER = ["PASS", "SOFT_FAIL", "HARD_FAIL"]
SEVERITY_PALETTE = {
    "PASS": "#2a9d8f",
    "SOFT_FAIL": "#e9c46a",
    "HARD_FAIL": "#e76f51",
}


def configure_cd_notebook_style() -> None:
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams["figure.figsize"] = (14, 7)
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False
    pd.set_option("display.max_columns", 120)
    pd.set_option("display.max_rows", 200)
    pd.set_option("display.max_colwidth", 160)


def build_cd_run_context(mod00: dict[str, Any], run_dir_cd: Path) -> dict[str, Any]:
    current_parquet = run_dir_cd / 'trades_current.parquet'

    assert run_dir_cd.exists(), run_dir_cd
    assert current_parquet.exists(), current_parquet

    cd_current = mod00['load_current_parquet'](current_parquet)

    if 'processed_at_utc' in cd_current.columns:
        cd_current['processed_at_utc'] = pd.to_datetime(cd_current['processed_at_utc'], utc=True, errors='coerce')
    if 'date' in cd_current.columns:
        cd_current['date_ts'] = pd.to_datetime(cd_current['date'], errors='coerce')
        cd_current['year'] = cd_current['date_ts'].dt.year
        cd_current['month'] = cd_current['date_ts'].dt.to_period('M').astype(str)
    if 'file' in cd_current.columns:
        cd_current['file_key'] = cd_current['file'].astype(str)

    numeric_cols = [
        'm.off_session_trade_pct',
        'm.duplicate_excess_ratio_pct',
        'm.max_trades_same_timestamp',
        'm.trade_volume_vs_daily_ratio',
        'm.trade_volume_vs_1m_ratio',
        'm.possible_price_scale_factor_vs_daily',
        'm.possible_price_scale_factor_vs_1m',
        'm.price_min',
        'm.price_max',
        'm.trade_vwap',
        'm.vw',
        'm.l',
        'm.h',
        'm.ohlcv_1m_low_min',
        'm.ohlcv_1m_high_max',
    ]
    for col in numeric_cols:
        if col in cd_current.columns:
            cd_current[col] = pd.to_numeric(cd_current[col], errors='coerce')

    if 'batch_id' in cd_current.columns:
        cd_current['batch_num'] = pd.to_numeric(
            cd_current['batch_id'].astype(str).str.extract(r'(\d+)')[0],
            errors='coerce',
        )

    return {
        'run_dir_cd': run_dir_cd,
        'current_parquet_cd': current_parquet,
        'cd_current': cd_current,
    }


def display_cd_run_header(cd_current: pd.DataFrame, current_parquet_cd: Path) -> None:
    display(
        Markdown(
            f"**full rows:** {len(cd_current):,}  \n"
            f"**source:** `C+D merged current`  \n"
            f"**current parquet:** `{current_parquet_cd}`"
        )
    )


def build_severity_counts_cd(cd_current: pd.DataFrame) -> pd.DataFrame:
    out = (
        cd_current['severity']
        .value_counts()
        .rename_axis('severity')
        .reset_index(name='files')
    )
    out['pct'] = 100.0 * out['files'] / max(len(cd_current), 1)
    out['severity'] = pd.Categorical(out['severity'], categories=SEVERITY_ORDER, ordered=True)
    return out.sort_values('severity').reset_index(drop=True)


def build_snapshot_cd(cd_current: pd.DataFrame, current_parquet_cd: Path) -> pd.DataFrame:
    return pd.DataFrame([
        {
            'source': 'trades_current_cd_merged',
            'current_parquet': str(current_parquet_cd),
            'current_rows': int(len(cd_current)),
            'hard_fail': int((cd_current['severity'] == 'HARD_FAIL').sum()),
            'soft_fail': int((cd_current['severity'] == 'SOFT_FAIL').sum()),
            'pass': int((cd_current['severity'] == 'PASS').sum()),
            'pass_rate_pct': round(100.0 * (cd_current['severity'] == 'PASS').mean(), 3),
            'hard_fail_rate_pct': round(100.0 * (cd_current['severity'] == 'HARD_FAIL').mean(), 3),
            'soft_fail_rate_pct': round(100.0 * (cd_current['severity'] == 'SOFT_FAIL').mean(), 3),
        }
    ])


def build_batch_snapshot_cd(cd_current: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if 'batch_num' not in cd_current.columns or cd_current['batch_num'].isna().all():
        empty = pd.DataFrame()
        return empty, empty, empty

    batch_mix_cd = (
        cd_current.groupby(['batch_num', 'severity'], dropna=False)
        .size()
        .rename('files')
        .reset_index()
    )
    batch_pivot_cd = (
        batch_mix_cd.pivot(index='batch_num', columns='severity', values='files')
        .fillna(0)
        .sort_index()
    )
    batch_rate_cd = batch_pivot_cd.div(batch_pivot_cd.sum(axis=1), axis=0) * 100.0
    batch_rate_roll50_cd = (
        batch_rate_cd[[c for c in SEVERITY_ORDER if c in batch_rate_cd.columns]]
        .rolling(50, min_periods=1)
        .mean()
    )
    return batch_mix_cd, batch_pivot_cd, batch_rate_roll50_cd


def plot_cd_severity_snapshot(sev_counts_cd: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    sns.barplot(
        data=sev_counts_cd,
        x='severity',
        y='files',
        hue='severity',
        palette=SEVERITY_PALETTE,
        legend=False,
        ax=axes[0],
    )
    axes[0].set_title('Conteo por severidad')
    axes[0].set_xlabel('')
    axes[0].set_ylabel('files')

    sns.barplot(
        data=sev_counts_cd,
        x='severity',
        y='pct',
        hue='severity',
        palette=SEVERITY_PALETTE,
        legend=False,
        ax=axes[1],
    )
    axes[1].set_title('Peso relativo por severidad')
    axes[1].set_xlabel('')
    axes[1].set_ylabel('pct')
    plt.tight_layout()
    plt.show()


def plot_cd_batch_snapshot(batch_pivot_cd: pd.DataFrame, batch_rate_roll50_cd: pd.DataFrame) -> None:
    if batch_pivot_cd.empty or batch_rate_roll50_cd.empty:
        display(Markdown('**batch drift:** no aplica o no esta disponible en `trades_current_cd_merged`.'))
        return

    fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True)
    batch_pivot_cd[[c for c in SEVERITY_ORDER if c in batch_pivot_cd.columns]].plot(
        ax=axes[0],
        color=SEVERITY_PALETTE,
        alpha=0.8,
    )
    axes[0].set_title('Conteo por batch')
    axes[0].set_ylabel('files')

    batch_rate_roll50_cd.plot(
        ax=axes[1],
        color=SEVERITY_PALETTE,
    )
    axes[1].set_title('Tasa por severidad suavizada (rolling 50 batches)')
    axes[1].set_ylabel('pct')
    axes[1].set_xlabel('batch_num')
    plt.tight_layout()
    plt.show()


def summarize_cd_snapshot_chunked(current_parquet: str | Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pf = pq.ParquetFile(Path(current_parquet))
    severity_frames: list[pd.DataFrame] = []
    batch_frames: list[pd.DataFrame] = []

    for row_group_idx in range(pf.num_row_groups):
        chunk = pf.read_row_group(
            row_group_idx,
            columns=['severity', 'batch_id'],
        ).to_pandas()
        if chunk.empty:
            continue

        severity_chunk = (
            chunk.groupby('severity', dropna=False)
            .size()
            .rename('files')
            .reset_index()
        )
        severity_frames.append(severity_chunk)

        batch_num = pd.to_numeric(
            chunk['batch_id'].astype(str).str.extract(r'(\d+)')[0],
            errors='coerce',
        )
        if batch_num.notna().any():
            batch_chunk = pd.DataFrame(
                {
                    'batch_num': batch_num,
                    'severity': chunk['severity'],
                }
            ).dropna(subset=['batch_num'])
            if not batch_chunk.empty:
                batch_frames.append(
                    batch_chunk.groupby(['batch_num', 'severity'], dropna=False)
                    .size()
                    .rename('files')
                    .reset_index()
                )

    sev_counts_cd = (
        pd.concat(severity_frames, ignore_index=True)
        .groupby('severity', dropna=False, as_index=False)['files']
        .sum()
        if severity_frames
        else pd.DataFrame(columns=['severity', 'files'])
    )
    total_rows = int(sev_counts_cd['files'].sum()) if not sev_counts_cd.empty else 0
    if not sev_counts_cd.empty:
        sev_counts_cd['pct'] = 100.0 * sev_counts_cd['files'] / max(total_rows, 1)
        sev_counts_cd['severity'] = pd.Categorical(
            sev_counts_cd['severity'],
            categories=SEVERITY_ORDER,
            ordered=True,
        )
        sev_counts_cd = sev_counts_cd.sort_values('severity').reset_index(drop=True)

    snapshot_cd = pd.DataFrame(
        [
            {
                'source': 'trades_current_cd_merged',
                'current_parquet': str(current_parquet),
                'current_rows': total_rows,
                'hard_fail': int(sev_counts_cd.loc[sev_counts_cd['severity'] == 'HARD_FAIL', 'files'].sum()) if not sev_counts_cd.empty else 0,
                'soft_fail': int(sev_counts_cd.loc[sev_counts_cd['severity'] == 'SOFT_FAIL', 'files'].sum()) if not sev_counts_cd.empty else 0,
                'pass': int(sev_counts_cd.loc[sev_counts_cd['severity'] == 'PASS', 'files'].sum()) if not sev_counts_cd.empty else 0,
                'pass_rate_pct': round(float(sev_counts_cd.loc[sev_counts_cd['severity'] == 'PASS', 'pct'].sum()), 3) if not sev_counts_cd.empty else 0.0,
                'hard_fail_rate_pct': round(float(sev_counts_cd.loc[sev_counts_cd['severity'] == 'HARD_FAIL', 'pct'].sum()), 3) if not sev_counts_cd.empty else 0.0,
                'soft_fail_rate_pct': round(float(sev_counts_cd.loc[sev_counts_cd['severity'] == 'SOFT_FAIL', 'pct'].sum()), 3) if not sev_counts_cd.empty else 0.0,
            }
        ]
    )

    if not batch_frames:
        empty = pd.DataFrame()
        return sev_counts_cd, snapshot_cd, empty, empty

    batch_mix_cd = (
        pd.concat(batch_frames, ignore_index=True)
        .groupby(['batch_num', 'severity'], dropna=False, as_index=False)['files']
        .sum()
        .sort_values(['batch_num', 'severity'])
        .reset_index(drop=True)
    )
    batch_pivot_cd = (
        batch_mix_cd.pivot(index='batch_num', columns='severity', values='files')
        .fillna(0)
        .sort_index()
    )
    batch_rate_cd = batch_pivot_cd.div(batch_pivot_cd.sum(axis=1), axis=0) * 100.0
    batch_rate_roll50_cd = (
        batch_rate_cd[[c for c in SEVERITY_ORDER if c in batch_rate_cd.columns]]
        .rolling(50, min_periods=1)
        .mean()
    )
    return sev_counts_cd, snapshot_cd, batch_mix_cd, batch_rate_roll50_cd
