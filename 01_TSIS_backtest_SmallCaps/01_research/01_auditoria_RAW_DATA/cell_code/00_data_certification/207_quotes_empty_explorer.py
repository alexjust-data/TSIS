from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pyarrow.parquet as pq

try:
    import ipywidgets as widgets
    from IPython.display import display, clear_output
except Exception:
    widgets = None
    display = None
    clear_output = None

RUN_DIR = Path(globals().get('RUN_DIR', r'C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit'))
CURRENT_CSV = Path(globals().get('CURRENT_CSV', RUN_DIR / 'download_events_current.csv'))
OHLCV_1M_ROOT = Path(globals().get('OHLCV_1M_ROOT', r'D:\ohlcv_1m'))
DAILY_ROOT = Path(globals().get('DAILY_ROOT', r'D:\ohlcv_daily'))
CONTEXT_DAYS = int(globals().get('CONTEXT_DAYS', 20))


def load_1m_day(ticker: str, day: pd.Timestamp) -> pd.DataFrame:
    fp = OHLCV_1M_ROOT / f'ticker={ticker}' / f'year={day.year:04d}' / f'month={day.month:02d}' / f'minute_aggs_{ticker}_{day.year:04d}_{day.month:02d}.parquet'
    if not fp.exists():
        return pd.DataFrame()
    try:
        pf = pq.ParquetFile(fp)
        cols = [c for c in ['ticker', 'ts_utc', 'date', 'o', 'h', 'l', 'c', 'v', 'n'] if c in pf.schema.names]
        df = pf.read(columns=cols).to_pandas()
    except Exception:
        return pd.DataFrame()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df[df['date'] == day.normalize()].copy()
    if 'ts_utc' in df.columns:
        df['ts_utc'] = pd.to_datetime(df['ts_utc'], errors='coerce', utc=True)
    return df.sort_values('ts_utc').reset_index(drop=True)


def load_daily_context(ticker: str, center_date: pd.Timestamp) -> pd.DataFrame:
    years = sorted({center_date.year - 1, center_date.year, center_date.year + 1})
    parts = []
    for year in years:
        fp = DAILY_ROOT / f'ticker={ticker}' / f'year={year:04d}' / f'day_aggs_{ticker}_{year:04d}.parquet'
        if not fp.exists():
            continue
        try:
            pf = pq.ParquetFile(fp)
            df = pf.read().to_pandas()
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
cur = cur.dropna(subset=['ticker', 'date']).sort_values(['ticker', 'date']).reset_index(drop=True)

print('=== QUOTES EMPTY EXPLORER ===')
print({'empty_rows': int(len(cur)), 'empty_tickers': int(cur['ticker'].nunique())})


def render_case(ticker: str, date_str: str) -> None:
    d = pd.Timestamp(date_str)
    row = cur[(cur['ticker'] == ticker) & (cur['date'] == d)]
    if row.empty:
        print('Caso no encontrado.')
        return
    detail = row[['ticker', 'date', 'status', 'rows', 'pages', 'empty_rechecks', 'processed_at_utc']].head(1).T.reset_index()
    detail.columns = ['field', 'value']
    if display is not None:
        display(detail)
    else:
        print(detail.to_string(index=False))

    day1m = load_1m_day(ticker, d)
    if not day1m.empty:
        fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
        axes[0].plot(day1m['ts_utc'], day1m['c'], color='#1d3557', linewidth=1.0)
        axes[0].fill_between(day1m['ts_utc'], day1m['l'], day1m['h'], color='#a8dadc', alpha=0.4)
        axes[0].set_title(f'OHLCV 1m exacto | {ticker} | {d.date()}')
        axes[1].bar(day1m['ts_utc'], day1m['v'].fillna(0), color='#457b9d', width=0.0008)
        axes[1].set_ylabel('volume')
        plt.tight_layout()
        plt.show()
        if display is not None:
            display(day1m.head(20))
        else:
            print(day1m.head(20).to_string(index=False))
        return

    print('Sin ohlcv_1m local para la fecha exacta. Fallback a daily.')
    daily = load_daily_context(ticker, d)
    if daily.empty:
        print('Sin contexto daily local para este ticker.')
        return

    lo = d - pd.Timedelta(days=CONTEXT_DAYS)
    hi = d + pd.Timedelta(days=CONTEXT_DAYS)
    w = daily[(daily['date'] >= lo) & (daily['date'] <= hi)].copy()
    if w.empty:
        print('Sin ventana daily alrededor de la fecha seleccionada.')
        return

    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    axes[0].plot(w['date'], w['c'], marker='o', color='#2a9d8f', linewidth=1.2)
    axes[0].axvline(d, color='#e76f51', linestyle='--')
    axes[0].set_title(f'Contexto daily ?{CONTEXT_DAYS}d | {ticker} | {d.date()}')
    axes[1].bar(w['date'], w['v'].fillna(0), color='#264653')
    axes[1].axvline(d, color='#e76f51', linestyle='--')
    plt.tight_layout()
    plt.show()

    exact = daily[daily['date'] == d]
    if display is not None:
        if exact.empty:
            display(pd.DataFrame([{'ticker': ticker, 'date': d, 'note': 'selected date absent in daily context'}]))
        else:
            display(exact)
    else:
        print(exact.to_string(index=False) if not exact.empty else f'{ticker} {d.date()} absent in daily context')


if widgets is None or display is None or clear_output is None:
    print('ipywidgets no disponible')
else:
    ticker_w = widgets.Dropdown(options=sorted(cur['ticker'].unique().tolist()), description='ticker')
    date_w = widgets.Dropdown(description='date')
    out = widgets.Output()

    def refresh_dates(*_args):
        dates = cur[cur['ticker'] == ticker_w.value]['date'].dt.strftime('%Y-%m-%d').tolist()
        date_w.options = dates
        if dates:
            date_w.value = dates[0]

    def rerender(*_args):
        with out:
            clear_output(wait=True)
            if ticker_w.value and date_w.value:
                render_case(ticker_w.value, date_w.value)

    ticker_w.observe(refresh_dates, names='value')
    date_w.observe(rerender, names='value')
    refresh_dates()
    display(widgets.VBox([widgets.HBox([ticker_w, date_w]), out]))
    rerender()
