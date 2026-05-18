from __future__ import annotations

from collections import Counter
from pathlib import Path
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import seaborn as sns


SMALL_TITLE_SIZE = 11
SMALL_LABEL_SIZE = 9
SMALL_TICK_SIZE = 8


def build_hard_cd(cd_current: pd.DataFrame) -> pd.DataFrame:
    return cd_current.loc[cd_current['severity'] == 'HARD_FAIL'].copy()


def build_hard_issue_counts_cd(hard_cd: pd.DataFrame, flatten_tokens) -> pd.DataFrame:
    vals = pd.Series(flatten_tokens(hard_cd['issues_list'].tolist()), dtype='object')
    if vals.empty:
        return pd.DataFrame(columns=['issue', 'files'])
    return vals.value_counts().rename_axis('issue').reset_index(name='files')


def build_warn_counts_cd(cd_current: pd.DataFrame, flatten_tokens) -> pd.DataFrame:
    vals = pd.Series(flatten_tokens(cd_current['warns_list'].tolist()), dtype='object')
    if vals.empty:
        return pd.DataFrame(columns=['warn', 'files'])
    return vals.value_counts().rename_axis('warn').reset_index(name='files')


def build_issue_evidence_cd(hard_cd: pd.DataFrame, hard_issue_counts_cd: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for issue_name in hard_issue_counts_cd['issue'].tolist():
        x = hard_cd[hard_cd['issues_list'].map(lambda xs: issue_name in set(xs))].copy()
        rows.append(
            {
                'issue': issue_name,
                'files': int(len(x)),
                'tickers': int(x['ticker'].nunique()) if 'ticker' in x.columns else 0,
                'dates': int(x['date'].nunique()) if 'date' in x.columns else 0,
                'has_1m_warn_pct': 100.0 * x['warns_list'].map(lambda xs: 'trade_price_outside_1m_range' in set(xs)).mean() if len(x) else np.nan,
                'median_off_session_pct': pd.to_numeric(x.get('m.off_session_trade_pct'), errors='coerce').median() if len(x) else np.nan,
                'median_dup_pct': pd.to_numeric(x.get('m.duplicate_excess_ratio_pct'), errors='coerce').median() if len(x) else np.nan,
                'median_vol_vs_daily': pd.to_numeric(x.get('m.trade_volume_vs_daily_ratio'), errors='coerce').median() if len(x) else np.nan,
                'median_vol_vs_1m': pd.to_numeric(x.get('m.trade_volume_vs_1m_ratio'), errors='coerce').median() if len(x) else np.nan,
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(['files', 'has_1m_warn_pct'], ascending=[False, False]).reset_index(drop=True)


def plot_root_cause_counts_cd(
    hard_issue_counts_cd: pd.DataFrame,
    warn_counts_cd: pd.DataFrame,
    top_n: int = 15,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.8))
    sns.barplot(
        data=hard_issue_counts_cd.head(top_n),
        y='issue',
        x='files',
        color='#e76f51',
        ax=axes[0],
    )
    axes[0].set_title('Top causas de HARD_FAIL en C+D', fontsize=SMALL_TITLE_SIZE)
    axes[0].set_xlabel('files', fontsize=SMALL_LABEL_SIZE)
    axes[0].set_ylabel('')
    axes[0].tick_params(axis='both', labelsize=SMALL_TICK_SIZE)

    sns.barplot(
        data=warn_counts_cd.head(top_n),
        y='warn',
        x='files',
        color='#e9c46a',
        ax=axes[1],
    )
    axes[1].set_title('Top warnings de C+D', fontsize=SMALL_TITLE_SIZE)
    axes[1].set_xlabel('files', fontsize=SMALL_LABEL_SIZE)
    axes[1].set_ylabel('')
    axes[1].tick_params(axis='both', labelsize=SMALL_TICK_SIZE)
    plt.tight_layout()
    plt.show()


def plot_issue_evidence_cd(issue_evidence_cd: pd.DataFrame) -> None:
    if issue_evidence_cd.empty:
        return

    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.8))
    sns.barplot(data=issue_evidence_cd, y='issue', x='files', color='#d62828', ax=axes[0])
    axes[0].set_title('Peso de cada issue vivo en HARD_FAIL', fontsize=SMALL_TITLE_SIZE)
    axes[0].set_xlabel('files', fontsize=SMALL_LABEL_SIZE)
    axes[0].set_ylabel('')
    axes[0].tick_params(axis='both', labelsize=SMALL_TICK_SIZE)

    sns.barplot(
        data=issue_evidence_cd,
        y='issue',
        x='has_1m_warn_pct',
        color='#2a9d8f',
        ax=axes[1],
    )
    axes[1].set_title('Confirmacion por 1m dentro de cada issue', fontsize=SMALL_TITLE_SIZE)
    axes[1].set_xlabel('has_1m_warn_pct', fontsize=SMALL_LABEL_SIZE)
    axes[1].set_ylabel('')
    axes[1].tick_params(axis='both', labelsize=SMALL_TICK_SIZE)
    plt.tight_layout()
    plt.show()


def _reservoir_append(sample: list[float], value: float, seen: int, max_size: int, rng: random.Random) -> None:
    if pd.isna(value):
        return
    if len(sample) < max_size:
        sample.append(float(value))
        return
    j = rng.randint(0, seen - 1)
    if j < max_size:
        sample[j] = float(value)


def summarize_cd_root_cause_chunked(
    current_parquet: str | Path,
    mod00: dict,
    sample_size_per_issue: int = 20_000,
    top_n_issue_evidence: int = 15,
    random_state: int = 7,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    current_parquet = Path(current_parquet)
    pf = pq.ParquetFile(current_parquet)

    parse_listish = mod00['parse_listish']
    flatten_tokens = mod00['flatten_tokens']
    parse_dictish = mod00['parse_dictish']

    warn_counter: Counter[str] = Counter()
    hard_issue_counter: Counter[str] = Counter()

    for row_group_idx in range(pf.num_row_groups):
        chunk = pf.read_row_group(
            row_group_idx,
            columns=['severity', 'issues', 'warns'],
        ).to_pandas()
        chunk['issues_list'] = chunk['issues'].map(lambda x: flatten_tokens([parse_listish(x)]))
        chunk['warns_list'] = chunk['warns'].map(lambda x: flatten_tokens([parse_listish(x)]))

        warn_counter.update(
            tok
            for xs in chunk['warns_list'].tolist()
            for tok in xs
        )
        hard_issue_counter.update(
            tok
            for xs in chunk.loc[chunk['severity'] == 'HARD_FAIL', 'issues_list'].tolist()
            for tok in xs
        )

    hard_issue_counts_cd = (
        pd.DataFrame(
            [{'issue': k, 'files': v} for k, v in hard_issue_counter.items()]
        )
        .sort_values(['files', 'issue'], ascending=[False, True])
        .reset_index(drop=True)
        if hard_issue_counter
        else pd.DataFrame(columns=['issue', 'files'])
    )
    warn_counts_cd = (
        pd.DataFrame(
            [{'warn': k, 'files': v} for k, v in warn_counter.items()]
        )
        .sort_values(['files', 'warn'], ascending=[False, True])
        .reset_index(drop=True)
        if warn_counter
        else pd.DataFrame(columns=['warn', 'files'])
    )

    focus_issues = hard_issue_counts_cd.head(top_n_issue_evidence)['issue'].tolist()
    if not focus_issues:
        return hard_issue_counts_cd, warn_counts_cd, pd.DataFrame()

    rng = random.Random(random_state)
    issue_stats = {
        issue: {
            'files': 0,
            'tickers': set(),
            'dates': set(),
            'has_1m_warn_count': 0,
            'metric_seen': {
                'm.off_session_trade_pct': 0,
                'm.duplicate_excess_ratio_pct': 0,
                'm.trade_volume_vs_daily_ratio': 0,
                'm.trade_volume_vs_1m_ratio': 0,
            },
            'metric_samples': {
                'm.off_session_trade_pct': [],
                'm.duplicate_excess_ratio_pct': [],
                'm.trade_volume_vs_daily_ratio': [],
                'm.trade_volume_vs_1m_ratio': [],
            },
        }
        for issue in focus_issues
    }

    metric_keys = [
        'off_session_trade_pct',
        'duplicate_excess_ratio_pct',
        'trade_volume_vs_daily_ratio',
        'trade_volume_vs_1m_ratio',
    ]
    metric_map = {
        'off_session_trade_pct': 'm.off_session_trade_pct',
        'duplicate_excess_ratio_pct': 'm.duplicate_excess_ratio_pct',
        'trade_volume_vs_daily_ratio': 'm.trade_volume_vs_daily_ratio',
        'trade_volume_vs_1m_ratio': 'm.trade_volume_vs_1m_ratio',
    }

    for row_group_idx in range(pf.num_row_groups):
        chunk = pf.read_row_group(
            row_group_idx,
            columns=['severity', 'issues', 'warns', 'ticker', 'date', 'metrics_json'],
        ).to_pandas()
        hard_chunk = chunk.loc[chunk['severity'] == 'HARD_FAIL'].copy()
        if hard_chunk.empty:
            continue

        hard_chunk['issues_list'] = hard_chunk['issues'].map(lambda x: flatten_tokens([parse_listish(x)]))
        hard_chunk['warns_list'] = hard_chunk['warns'].map(lambda x: flatten_tokens([parse_listish(x)]))
        hard_chunk['metrics'] = hard_chunk['metrics_json'].map(parse_dictish)

        for _, row in hard_chunk.iterrows():
            issue_set = set(row['issues_list'])
            matched = [issue for issue in focus_issues if issue in issue_set]
            if not matched:
                continue

            warn_set = set(row['warns_list'])
            metrics = row['metrics']
            for issue in matched:
                stats = issue_stats[issue]
                stats['files'] += 1
                stats['tickers'].add(str(row['ticker']))
                stats['dates'].add(str(row['date']))
                if 'trade_price_outside_1m_range' in warn_set:
                    stats['has_1m_warn_count'] += 1

                for key in metric_keys:
                    full_key = metric_map[key]
                    value = pd.to_numeric(metrics.get(key), errors='coerce')
                    if pd.isna(value):
                        continue
                    stats['metric_seen'][full_key] += 1
                    _reservoir_append(
                        stats['metric_samples'][full_key],
                        float(value),
                        stats['metric_seen'][full_key],
                        sample_size_per_issue,
                        rng,
                    )

    rows: list[dict[str, object]] = []
    for issue in focus_issues:
        stats = issue_stats[issue]
        rows.append(
            {
                'issue': issue,
                'files': int(stats['files']),
                'tickers': int(len(stats['tickers'])),
                'dates': int(len(stats['dates'])),
                'has_1m_warn_pct': 100.0 * stats['has_1m_warn_count'] / max(stats['files'], 1),
                'median_off_session_pct': float(np.median(stats['metric_samples']['m.off_session_trade_pct'])) if stats['metric_samples']['m.off_session_trade_pct'] else np.nan,
                'median_dup_pct': float(np.median(stats['metric_samples']['m.duplicate_excess_ratio_pct'])) if stats['metric_samples']['m.duplicate_excess_ratio_pct'] else np.nan,
                'median_vol_vs_daily': float(np.median(stats['metric_samples']['m.trade_volume_vs_daily_ratio'])) if stats['metric_samples']['m.trade_volume_vs_daily_ratio'] else np.nan,
                'median_vol_vs_1m': float(np.median(stats['metric_samples']['m.trade_volume_vs_1m_ratio'])) if stats['metric_samples']['m.trade_volume_vs_1m_ratio'] else np.nan,
            }
        )

    issue_evidence_cd = pd.DataFrame(rows)
    if not issue_evidence_cd.empty:
        issue_evidence_cd = issue_evidence_cd.sort_values(['files', 'has_1m_warn_pct'], ascending=[False, False]).reset_index(drop=True)

    return hard_issue_counts_cd, warn_counts_cd, issue_evidence_cd
