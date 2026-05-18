from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

RUN_DIR = Path(globals().get('RUN_DIR', r'C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit'))
CURRENT_CSV = Path(globals().get('CURRENT_CSV', RUN_DIR / 'download_events_current.csv'))
DAILY_ROOT = Path(globals().get('DAILY_ROOT', r'D:\ohlcv_daily'))
TOP_N = int(globals().get('TOP_N', 100))
TOP_CASES = int(globals().get('TOP_CASES', 200))


def load_daily_years(ticker: str, center_date: pd.Timestamp) -> pd.DataFrame:
    years = sorted({center_date.year - 1, center_date.year, center_date.year + 1})
    parts = []
    for year in years:
        fp = DAILY_ROOT / f'ticker={ticker}' / f'year={year:04d}' / f'day_aggs_{ticker}_{year:04d}.parquet'
        if not fp.exists():
            continue
        try:
            pf = pq.ParquetFile(fp)
            cols = [c for c in ['date', 'o', 'h', 'l', 'c', 'v'] if c in pf.schema.names]
            df = pf.read(columns=cols).to_pandas()
            parts.append(df)
        except Exception:
            continue
    if not parts:
        return pd.DataFrame()
    out = pd.concat(parts, ignore_index=True)
    out['date'] = pd.to_datetime(out['date'], errors='coerce')
    return out.dropna(subset=['date']).sort_values('date').reset_index(drop=True)


cur = pd.read_csv(CURRENT_CSV)
cur['ticker'] = cur['ticker'].astype(str).str.upper().str.strip()
cur['date'] = pd.to_datetime(cur['date'], errors='coerce')
cur = cur[cur['status'] == 'DOWNLOADED_EMPTY'].copy()
cur = cur.dropna(subset=['ticker', 'date']).reset_index(drop=True)

flags = []
for row in cur[['ticker', 'date']].itertuples(index=False):
    daily = load_daily_years(row.ticker, row.date)
    has_daily_exact = False
    if not daily.empty:
        has_daily_exact = bool((daily['date'] == row.date).any())
    flags.append(has_daily_exact)

out = cur.copy()
out['has_daily_exact'] = flags

empty_total_by_ticker = (
    cur.groupby('ticker', dropna=False)
       .size()
       .reset_index(name='empty_total')
)

suspicious = (
    out[out['has_daily_exact']]
    .groupby('ticker', dropna=False)
    .agg(
        empty_with_daily_exact=('ticker', 'size'),
        date_min=('date', 'min'),
        date_max=('date', 'max'),
    )
    .reset_index()
    .merge(empty_total_by_ticker, on='ticker', how='left')
)

suspicious['pct_empty_with_daily_exact'] = 100 * suspicious['empty_with_daily_exact'] / suspicious['empty_total'].clip(lower=1)
suspicious['review_score'] = suspicious['empty_with_daily_exact'] * suspicious['pct_empty_with_daily_exact'] / 100
suspicious = suspicious.sort_values(
    ['review_score', 'empty_with_daily_exact', 'pct_empty_with_daily_exact', 'ticker'],
    ascending=[False, False, False, True]
).reset_index(drop=True)

print('=== QUOTES EMPTY SUSPICIOUS REVIEW ===')
print({'tickers_suspicious': int(len(suspicious)), 'rows_empty_total': int(len(cur)), 'rows_empty_with_daily_exact': int(out['has_daily_exact'].sum())})

display(suspicious.head(TOP_N))

top_tickers = suspicious.head(min(10, len(suspicious)))['ticker'].tolist()
sample_cases = (
    out[(out['has_daily_exact']) & (out['ticker'].isin(top_tickers))]
    [['ticker', 'date', 'status', 'rows', 'pages', 'empty_rechecks', 'processed_at_utc']]
    .sort_values(['ticker', 'date'])
    .reset_index(drop=True)
)

print('\n=== SAMPLE CASES TOP SUSPICIOUS ===')
display(sample_cases.head(TOP_CASES))
