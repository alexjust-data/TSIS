from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from typing import Any

import pandas as pd
import pyarrow.parquet as pq
from pandas.errors import EmptyDataError

REQUIRED_COLS = ['ticker', 'date', 'timestamp', 'price', 'size', 'exchange', 'conditions']


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_file_parts(path_str: str) -> dict[str, Any]:
    p = Path(path_str)
    try:
        day = p.parent.name.split('day=', 1)[1]
        month = p.parent.parent.name.split('month=', 1)[1]
        year = p.parent.parent.parent.name.split('year=', 1)[1]
        ticker = p.parent.parent.parent.parent.name
        return {'ticker': ticker, 'date': day, 'year': year, 'month': month, 'session': p.stem}
    except Exception:
        return {'ticker': None, 'date': None, 'year': None, 'month': None, 'session': p.stem}


def parse_listlike(x: Any) -> list[str]:
    if isinstance(x, (list, tuple)):
        return [str(i) for i in x]
    if hasattr(x, 'tolist') and not isinstance(x, (str, bytes)):
        try:
            vals = x.tolist()
            if isinstance(vals, list):
                return [str(i) for i in vals]
        except Exception:
            pass
    if pd.isna(x):
        return []
    s = str(x).strip()
    if s in ('', '[]', 'nan', 'None'):
        return []
    try:
        v = ast.literal_eval(s)
        if isinstance(v, list):
            return [str(i) for i in v]
        return [str(v)]
    except Exception:
        return [s]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')


def _safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except EmptyDataError:
        return pd.DataFrame()
    except Exception:
        try:
            return pd.read_csv(path, engine='python', on_bad_lines='skip')
        except EmptyDataError:
            return pd.DataFrame()


def scan_file_metadata(root: Path) -> pd.DataFrame:
    rows = []
    for p in root.glob('*/*/*/*/*.parquet'):
        try:
            st = p.stat()
            rows.append({
                'file': str(p),
                'size_bytes': int(st.st_size),
                'mtime_ns': int(st.st_mtime_ns),
            })
        except FileNotFoundError:
            continue
    return pd.DataFrame(rows)


def validate_file(path: Path) -> dict[str, Any]:
    base = {'file': str(path), 'processed_at_utc': utc_now_iso()}
    base.update(parse_file_parts(str(path)))
    issues: list[str] = []
    warns: list[str] = []
    try:
        pf = pq.ParquetFile(path)
        df = pf.read().to_pandas()
    except Exception as exc:
        return {**base, 'rows': 0, 'severity': 'HARD_FAIL', 'issues': ['parquet_unreadable'], 'warns': [], 'action': 'review_queue', 'error': repr(exc)}

    rows = len(df)
    base['rows'] = int(rows)
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    base['missing_required_cols'] = ','.join(missing) if missing else ''
    if missing:
        issues.append('missing_required_cols')
    if rows == 0:
        issues.append('empty_file')

    if 'timestamp' in df.columns:
        ts = pd.to_datetime(df['timestamp'], errors='coerce')
        if ts.isna().any():
            issues.append('null_timestamp_rows')
        if ts.notna().any() and not ts.is_monotonic_increasing:
            issues.append('timestamp_not_monotonic')

    if 'price' in df.columns:
        px = pd.to_numeric(df['price'], errors='coerce')
        nonpositive = int((px <= 0).fillna(False).sum())
        base['nonpositive_price_rows'] = nonpositive
        if nonpositive > 0:
            issues.append('nonpositive_price_rows')
    else:
        base['nonpositive_price_rows'] = 0

    if 'size' in df.columns:
        sz = pd.to_numeric(df['size'], errors='coerce')
        negative = int((sz < 0).fillna(False).sum())
        base['negative_size_rows'] = negative
        if negative > 0:
            issues.append('negative_size_rows')
    else:
        base['negative_size_rows'] = 0

    if all(c in df.columns for c in ['timestamp', 'price', 'size', 'exchange']):
        work = df.copy()
        work['conditions_repr'] = work['conditions'].apply(lambda x: str(x if isinstance(x, list) else parse_listlike(x))) if 'conditions' in work.columns else '[]'
        dup_subset = ['timestamp', 'price', 'size', 'exchange', 'conditions_repr']
        duplicate_group_rows = int(work.duplicated(subset=dup_subset, keep=False).sum())
        group_sizes = work.groupby(dup_subset, dropna=False).size()
        duplicate_excess_rows = int((group_sizes[group_sizes > 1] - 1).sum())
        duplicate_group_ratio = 100 * duplicate_group_rows / max(rows, 1)
        duplicate_excess_ratio = 100 * duplicate_excess_rows / max(rows, 1)
        adjacent_exact_repeats = int((work[dup_subset] == work[dup_subset].shift(1)).all(axis=1).sum())

        base['duplicate_group_rows'] = duplicate_group_rows
        base['duplicate_group_ratio_pct'] = float(duplicate_group_ratio)
        base['duplicate_excess_rows'] = duplicate_excess_rows
        base['duplicate_excess_ratio_pct'] = float(duplicate_excess_ratio)
        base['adjacent_exact_repeats'] = adjacent_exact_repeats

        if duplicate_excess_ratio > 10.0:
            issues.append('duplicate_excess_ratio_gt_hard_cap')
        elif duplicate_excess_ratio > 3.0:
            warns.append('duplicate_excess_ratio_gt_threshold')
        elif duplicate_excess_rows > 0:
            warns.append('duplicates_present_but_under_threshold')
    else:
        base['duplicate_group_rows'] = 0
        base['duplicate_group_ratio_pct'] = 0.0
        base['duplicate_excess_rows'] = 0
        base['duplicate_excess_ratio_pct'] = 0.0
        base['adjacent_exact_repeats'] = 0

    if rows < 10:
        warns.append('rows_lt_10')

    severity = 'HARD_FAIL' if issues else ('SOFT_FAIL' if warns else 'PASS')
    return {**base, 'severity': severity, 'issues': issues, 'warns': warns, 'action': 'review_queue' if severity != 'PASS' else 'accept_raw'}


def load_expected(expected_csv_arg: str, run_dir: Path) -> pd.DataFrame:
    candidates = []
    if expected_csv_arg:
        candidates.append(Path(expected_csv_arg))
    candidates.append(run_dir / 'expected_manifest_trades_ticks.csv')
    for p in candidates:
        if p.exists():
            df = _safe_read_csv(p)
            if df.empty:
                continue
            if 'session' not in df.columns:
                df['session'] = 'market'
            df['ticker'] = df['ticker'].astype(str).str.upper().str.strip()
            df['date'] = df['date'].astype(str).str.strip()
            if 'task_key' not in df.columns:
                df['task_key'] = df['ticker'] + '|' + df['date'] + '|' + df['session'].astype(str)
            return df
    return pd.DataFrame()


def load_download_events(run_dir: Path) -> pd.DataFrame:
    path = run_dir / 'download_events_trades_ticks_current.csv'
    df = _safe_read_csv(path)
    if df.empty:
        return df
    if 'task_key' not in df.columns and {'ticker', 'date', 'session'}.issubset(df.columns):
        df['task_key'] = df['ticker'].astype(str).str.upper().str.strip() + '|' + df['date'].astype(str).str.strip() + '|' + df['session'].astype(str).str.strip()
    if 'processed_at_utc' in df.columns:
        df['processed_at_utc'] = pd.to_datetime(df['processed_at_utc'], errors='coerce')
        df = df.sort_values('processed_at_utc').drop_duplicates('task_key', keep='last')
    return df


def load_state(path: Path) -> pd.DataFrame:
    df = _safe_read_csv(path)
    if df.empty:
        return pd.DataFrame(columns=['file', 'size_bytes', 'mtime_ns', 'validated_at_utc'])
    keep = [c for c in ['file', 'size_bytes', 'mtime_ns', 'validated_at_utc'] if c in df.columns]
    df = df[keep].copy()
    if 'file' not in df.columns:
        return pd.DataFrame(columns=['file', 'size_bytes', 'mtime_ns', 'validated_at_utc'])
    return df.drop_duplicates('file', keep='last')


def load_current_events(path: Path) -> pd.DataFrame:
    df = _safe_read_csv(path)
    if df.empty:
        return pd.DataFrame()
    if 'file' in df.columns:
        return df.drop_duplicates('file', keep='last')
    return df


def merge_current_events(prev_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
    if prev_df.empty:
        return new_df.copy()
    if new_df.empty:
        return prev_df.copy()
    out = pd.concat([prev_df[~prev_df['file'].isin(set(new_df['file']))], new_df], ignore_index=True)
    return out.drop_duplicates('file', keep='last')


def merge_state(prev_df: pd.DataFrame, processed_meta: pd.DataFrame) -> pd.DataFrame:
    if prev_df.empty:
        return processed_meta.copy()
    if processed_meta.empty:
        return prev_df.copy()
    out = pd.concat([prev_df[~prev_df['file'].isin(set(processed_meta['file']))], processed_meta], ignore_index=True)
    return out.drop_duplicates('file', keep='last')


def build_expected_vs_found(expected_df: pd.DataFrame, found_df: pd.DataFrame, download_df: pd.DataFrame, output_csv: Path) -> tuple[int | None, int | None, int | None, int | None, int | None]:
    if expected_df.empty:
        return None, None, None, None, None
    exp = expected_df.copy()

    keep_found_cols = [c for c in ['task_key', 'file', 'ticker', 'date', 'session', 'severity'] if c in found_df.columns]
    found = found_df[keep_found_cols].copy() if not found_df.empty else pd.DataFrame(columns=keep_found_cols)

    keep_dl_cols = [c for c in ['task_key', 'status', 'rows', 'file', 'error'] if c in download_df.columns]
    dload = download_df[keep_dl_cols].copy() if not download_df.empty else pd.DataFrame(columns=['task_key', 'status', 'rows', 'file', 'error'])
    if 'task_key' not in dload.columns:
        dload['task_key'] = pd.Series(dtype='string')
    dload = dload.rename(columns={'status': 'download_status', 'rows': 'download_rows', 'file': 'download_file', 'error': 'download_error'})

    merged = exp.merge(dload, on='task_key', how='left')
    merged = merged.merge(found, on='task_key', how='left', suffixes=('_expected', '_found'))
    merged['found_file_flag'] = merged['file'].notna()
    merged['download_empty_flag'] = merged['download_status'].astype(str).eq('DOWNLOADED_EMPTY')
    merged['download_fail_flag'] = merged['download_status'].astype(str).eq('DOWNLOAD_FAIL')
    merged['expected_ticker_match'] = merged['ticker_expected'].astype(str).eq(merged['ticker_found'].astype(str)) if {'ticker_expected', 'ticker_found'}.issubset(merged.columns) else merged['found_file_flag']
    merged['expected_date_match'] = merged['date_expected'].astype(str).eq(merged['date_found'].astype(str)) if {'date_expected', 'date_found'}.issubset(merged.columns) else merged['found_file_flag']
    merged['expected_file_outcome'] = merged.apply(
        lambda r: 'FOUND_FILE' if bool(r['found_file_flag']) else ('DOWNLOADED_EMPTY' if bool(r['download_empty_flag']) else ('DOWNLOAD_FAIL' if bool(r['download_fail_flag']) else 'EXPECTED_MISSING')),
        axis=1,
    )

    output_cols = [c for c in [
        'task_key', 'ticker_expected', 'date_expected', 'session_expected', 'expected_file',
        'download_status', 'download_rows', 'download_error',
        'found_file_flag', 'file', 'severity', 'expected_ticker_match', 'expected_date_match', 'expected_file_outcome'
    ] if c in merged.columns]
    merged[output_cols].to_csv(output_csv, index=False)

    validated_found_n = int(merged['found_file_flag'].fillna(False).astype(bool).sum())
    downloaded_ok_n = int(merged['download_status'].astype(str).eq('DOWNLOADED_OK').sum())
    missing_n = int((merged['expected_file_outcome'] == 'EXPECTED_MISSING').sum())
    empty_n = int(merged['download_empty_flag'].fillna(False).astype(bool).sum())
    return int(len(merged)), validated_found_n, downloaded_ok_n, missing_n, empty_n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--run-dir', required=True)
    ap.add_argument('--probe-root', required=True)
    ap.add_argument('--max-files', type=int, default=50000)
    ap.add_argument('--sleep-sec', type=int, default=15)
    ap.add_argument('--reset-state', action='store_true')
    ap.add_argument('--one-shot', action='store_true')
    ap.add_argument('--expected-csv', default='')
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    probe_root = Path(args.probe_root)

    events_current = run_dir / 'trades_ticks_agent_events_current.csv'
    events_history = run_dir / 'trades_ticks_agent_events_history.csv'
    review_current = run_dir / 'review_queue_trades_ticks_current.csv'
    expected_review_csv = run_dir / 'expected_vs_found_trades_ticks.csv'
    live_json = run_dir / 'live_status_trades_ticks_strict.json'
    run_cfg = run_dir / 'run_config_trades_ticks_strict.json'
    state_csv = run_dir / 'trades_ticks_agent_file_state_current.csv'

    if args.reset_state:
        for p in [events_current, events_history, review_current, expected_review_csv, live_json, state_csv]:
            if p.exists():
                p.unlink()

    write_json(run_cfg, {
        'run_id': args.run_id,
        'run_dir': str(run_dir),
        'probe_root': str(probe_root),
        'max_files': args.max_files,
        'policy': 'ACCEPT_ALL_RAW_DIAGNOSE_LATER',
        'mode': 'incremental_by_file_mtime_size',
    })

    expected_df = load_expected(args.expected_csv, run_dir)

    while True:
        scan_df = scan_file_metadata(probe_root)
        prev_state = load_state(state_csv)
        prev_events = load_current_events(events_current)

        if scan_df.empty:
            pending_meta = pd.DataFrame(columns=['file', 'size_bytes', 'mtime_ns'])
        else:
            cmp_df = scan_df.merge(prev_state[['file', 'size_bytes', 'mtime_ns']], on='file', how='left', suffixes=('', '_prev'))
            pending_mask = (
                cmp_df['size_bytes_prev'].isna()
                | cmp_df['mtime_ns_prev'].isna()
                | cmp_df['size_bytes'].ne(cmp_df['size_bytes_prev'])
                | cmp_df['mtime_ns'].ne(cmp_df['mtime_ns_prev'])
            )
            pending_meta = cmp_df.loc[pending_mask, ['file', 'size_bytes', 'mtime_ns']].copy()
            pending_meta = pending_meta.sort_values(['mtime_ns', 'file'], ascending=[False, True]).head(args.max_files).reset_index(drop=True)

        print(json.dumps({
            'phase': 'scan',
            'discovered_total': int(len(scan_df)),
            'pending_delta_total': int(len(cmp_df.loc[pending_mask])) if not scan_df.empty else 0,
            'processing_now': int(len(pending_meta)),
            'run_dir': str(run_dir),
        }))

        rows = [validate_file(Path(fp)) for fp in pending_meta['file'].tolist()]
        cycle_df = pd.DataFrame(rows)
        if not cycle_df.empty:
            if 'task_key' not in cycle_df.columns and {'ticker', 'date', 'session'}.issubset(cycle_df.columns):
                cycle_df['task_key'] = cycle_df['ticker'].astype(str).str.upper().str.strip() + '|' + cycle_df['date'].astype(str).str.strip() + '|' + cycle_df['session'].astype(str).str.strip()

        current_df = merge_current_events(prev_events, cycle_df)
        if not current_df.empty:
            current_df.to_csv(events_current, index=False)
        elif not events_current.exists():
            pd.DataFrame().to_csv(events_current, index=False)

        if not cycle_df.empty:
            write_header = not events_history.exists()
            cycle_df.to_csv(events_history, mode='a', header=write_header, index=False)

        review = current_df[current_df['severity'] != 'PASS'].copy() if not current_df.empty and 'severity' in current_df.columns else pd.DataFrame()
        review.to_csv(review_current, index=False)

        processed_meta = pending_meta.copy()
        if not processed_meta.empty:
            processed_meta['validated_at_utc'] = utc_now_iso()
        next_state = merge_state(prev_state, processed_meta)
        next_state.to_csv(state_csv, index=False)

        sev = Counter(current_df['severity']) if not current_df.empty and 'severity' in current_df.columns else Counter()
        causes = Counter()
        if not current_df.empty:
            for col in ['issues', 'warns']:
                if col not in current_df.columns:
                    continue
                for xs in current_df[col].fillna('[]').astype(str):
                    for item in parse_listlike(xs):
                        causes[str(item)] += 1

        download_df = load_download_events(run_dir)
        expected_total, validated_found, downloaded_ok_current, expected_missing, expected_empty = build_expected_vs_found(expected_df, current_df, download_df, expected_review_csv)

        live = {
            'updated_utc': utc_now_iso(),
            'probe_root': str(probe_root),
            'max_files': int(args.max_files),
            'files_discovered_total': int(len(scan_df)),
            'files_pending': int(len(review)),
            'files_processed_total_state': int(len(current_df)),
            'files_current_snapshot': int(len(current_df)),
            'files_pending_delta_current': int(len(pending_meta)),
            'review_queue_pending_files_current': int(len(review)),
            'retry_pending_files_current': int(len(review)),
            'severity_counts_current': dict(sev),
            'top_causes_current': dict(causes.most_common(10)),
            'expected_tasks_total': expected_total,
            'validated_found_current': validated_found,
            'downloaded_ok_current': downloaded_ok_current,
            'expected_tasks_missing_current': expected_missing,
            'expected_tasks_empty_current': expected_empty,
        }
        write_json(live_json, live)

        print(json.dumps({
            'processed_total': int(live['files_processed_total_state']),
            'pending': int(live['files_pending']),
            'pass': int(live['severity_counts_current'].get('PASS', 0)),
            'soft': int(live['severity_counts_current'].get('SOFT_FAIL', 0)),
            'hard': int(live['severity_counts_current'].get('HARD_FAIL', 0)),
            'review_queue': int(live['review_queue_pending_files_current']),
            'pending_delta': int(live['files_pending_delta_current']),
            'validated_found': validated_found,
            'downloaded_ok': downloaded_ok_current,
            'expected_empty': expected_empty,
            'expected_missing': expected_missing,
            'gate': 'N/A' if live['review_queue_pending_files_current'] == 0 else 'REVIEW_QUEUE_OPEN',
            'run_dir': str(run_dir),
        }))

        if args.one_shot:
            break
        sleep(args.sleep_sec)


if __name__ == '__main__':
    main()
