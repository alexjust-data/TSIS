"""Jupyter widgets for Event Discovery."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import pandas as pd
from IPython.display import HTML, clear_output, display
import ipywidgets as widgets

from find_event_candidates import (
    AREA_ROOT,
    DEFAULT_LT1B_UNIVERSE_PATH,
    FindConfig,
    LT1B_UNIVERSE_DATASET_ID,
    LT1B_UNIVERSE_FILTER_POLICY,
    LT1B_UNIVERSE_ROWS,
    create_run_dir,
    finalize_run,
    find_candidates,
    mark_run_failed,
)
from render_event_case_panel import render_candidate


DEFAULT_DATA_ROOT = r"E:\TSIS\data\ohlcv_1m"
DEFAULT_REFERENCE_OVERVIEW_ROOT = r"E:\TSIS\data\reference\overview"
DEFAULT_RUNS_ROOT = AREA_ROOT / "runs"


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _delete_run_command(run_dir: Path) -> str:
    return f"Remove-Item -LiteralPath {_ps_quote(str(run_dir))} -Recurse -Force"


def _load_candidates_from_run(run_dir: Path) -> pd.DataFrame:
    parquet_path = run_dir / "candidate_events.parquet"
    csv_path = run_dir / "candidate_events.csv"
    partial_csv_path = run_dir / "candidate_events_partial.csv"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    for path in [csv_path, partial_csv_path]:
        if not path.exists() or path.stat().st_size <= 0:
            continue
        try:
            return pd.read_csv(path)
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
    return pd.DataFrame()


def _load_partial_candidates_from_run(run_dir: Path) -> pd.DataFrame:
    partial_csv_path = run_dir / "candidate_events_partial.csv"
    if not partial_csv_path.exists() or partial_csv_path.stat().st_size <= 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(partial_csv_path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _read_run_manifest(run_dir: Path) -> dict:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _format_run_option(run_dir: Path) -> tuple[str, str]:
    manifest = _read_run_manifest(run_dir)
    modified = datetime.fromtimestamp(run_dir.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    status = manifest.get("run_status") or "unknown"
    candidates = manifest.get("candidate_count")
    raw_candidates = manifest.get("raw_candidate_count")
    files_scanned = manifest.get("files_scanned")
    total_files = manifest.get("total_files")

    parts = [modified, status]
    if candidates is not None:
        parts.append(f"candidates={candidates}")
    if raw_candidates is not None:
        parts.append(f"raw={raw_candidates}")
    if files_scanned is not None and total_files is not None:
        parts.append(f"files={files_scanned}/{total_files}")
    parts.append(run_dir.name)
    return (" | ".join(str(x) for x in parts), str(run_dir))


def _list_run_options() -> list[tuple[str, str]]:
    runs_root = Path(DEFAULT_RUNS_ROOT)
    if not runs_root.exists():
        return []
    run_dirs = sorted((p for p in runs_root.glob("*") if p.is_dir()), key=lambda p: p.stat().st_mtime, reverse=True)
    return [_format_run_option(p) for p in run_dirs]


def _sort_candidates_for_review(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty or "push_pct" not in candidates.columns:
        return candidates
    out = candidates.copy()
    out["push_pct"] = pd.to_numeric(out["push_pct"], errors="coerce")
    sort_cols = ["push_pct"]
    ascending = [False]
    if "session_date" in out.columns:
        sort_cols.append("session_date")
        ascending.append(True)
    if "event_ts_utc" in out.columns:
        sort_cols.append("event_ts_utc")
        ascending.append(True)
    return out.sort_values(sort_cols, ascending=ascending, na_position="last").reset_index(drop=True)


def launch_event_discovery_app() -> widgets.Widget:
    data_root = widgets.Text(value=DEFAULT_DATA_ROOT, description="1m root", layout=widgets.Layout(width="95%"))
    universe_path = widgets.Text(
        value=str(DEFAULT_LT1B_UNIVERSE_PATH),
        description="Universe",
        layout=widgets.Layout(width="95%"),
    )
    universe_notice = widgets.HTML(
        value=(
            f"<b>Primary universe filter:</b> {LT1B_UNIVERSE_DATASET_ID} "
            f"({LT1B_UNIVERSE_ROWS} tickers, {LT1B_UNIVERSE_FILTER_POLICY})"
        )
    )
    tickers = widgets.Text(value="", description="Tickers", placeholder="empty = LT1B universe")
    years = widgets.Text(value="", description="Years", placeholder="e.g. 2024,2025 or 2019-2026")
    push_pct = widgets.FloatText(value=20.0, description="Push %")
    min_volume = widgets.FloatText(value=500_000.0, description="Vol >")
    min_price = widgets.FloatText(value=0.5, description="Price >")
    max_market_cap = widgets.FloatText(value=100_000_000.0, description="MCap <")
    missing_cap = widgets.Dropdown(options=["exclude", "include", "flag"], value="exclude", description="No MCap")
    session_scope = widgets.Dropdown(
        options=["premarket_regular", "full_extended", "premarket", "regular", "afterhours", "all"],
        value="premarket_regular",
        description="Session",
    )
    selection_mode = widgets.Dropdown(
        options=["first_push_of_day", "all_pushes"],
        value="first_push_of_day",
        description="Mode",
    )
    price_view = widgets.Dropdown(options=["raw", "split_normalized"], value="raw", description="Price")
    rising_highs = widgets.Checkbox(value=True, description="rising highs")
    close_above_prev_high = widgets.Checkbox(value=True, description="close > previous high")
    y_padding = widgets.BoundedFloatText(
        value=0.40,
        min=0.05,
        max=1.00,
        step=0.05,
        description="Y padding",
    )
    progress_every = widgets.BoundedIntText(value=50, min=0, max=1_000_000, step=50, description="Progress files")
    partial_flush_every = widgets.BoundedIntText(value=1, min=0, max=1_000_000, step=1, description="Flush hits")
    workers = widgets.IntText(value=1, description="Workers")
    control_help = widgets.HTML(
        value=(
            "<b>Y padding</b>: extra chart space above high and below low. "
            "<b>Progress files</b>: terminal progress print every N parquet files; 0 disables. "
            "<b>Flush hits</b>: update partial CSV every N new candidates; 0 only on progress/end."
        )
    )
    command_preview = widgets.Textarea(
        value="",
        description="Terminal",
        layout=widgets.Layout(width="95%", height="145px"),
    )
    run_dir_text = widgets.Text(value="", description="Run dir", layout=widgets.Layout(width="95%"))
    run_button = widgets.Button(description="Run in notebook", button_style="")
    run_dropdown = widgets.Dropdown(options=[], description="Runs", layout=widgets.Layout(width="95%"))
    refresh_runs_button = widgets.Button(description="Refresh runs", button_style="")
    load_selected_run_button = widgets.Button(description="Load selected run", button_style="primary")
    load_run_button = widgets.Button(description="Load run", button_style="primary")
    load_latest_button = widgets.Button(description="Load latest", button_style="")
    refresh_partial_button = widgets.Button(description="Refresh partial", button_style="")
    render_button = widgets.Button(description="Render selected", button_style="")
    candidate_dropdown = widgets.Dropdown(options=[], description="Candidate", layout=widgets.Layout(width="95%"))
    out = widgets.Output()

    state: dict[str, pd.DataFrame | Path] = {}

    def _parse_tickers(value: str) -> tuple[str, ...]:
        return tuple(x.strip().upper() for x in value.split(",") if x.strip())

    def _parse_years(value: str) -> tuple[int, ...]:
        if not value.strip():
            return ()
        parsed: list[int] = []
        for part in value.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                a, b = part.split("-", 1)
                parsed.extend(range(int(a), int(b) + 1))
            else:
                parsed.append(int(part))
        return tuple(sorted(set(parsed)))

    def _terminal_command() -> str:
        script_path = AREA_ROOT / "scripts" / "find_event_candidates.py"
        parts = [
            f"Set-Location {_ps_quote(str(AREA_ROOT))};",
            "python",
            _ps_quote(str(script_path)),
            "--data-root",
            _ps_quote(data_root.value),
            "--reference-overview-root",
            _ps_quote(DEFAULT_REFERENCE_OVERVIEW_ROOT),
            "--output-root",
            _ps_quote(str(DEFAULT_RUNS_ROOT)),
            "--universe-path",
            _ps_quote(universe_path.value),
            "--push-pct",
            str(push_pct.value),
            "--min-session-volume",
            str(min_volume.value),
            "--min-price",
            str(min_price.value),
            "--max-market-cap",
            str(max_market_cap.value),
            "--missing-market-cap-policy",
            missing_cap.value,
            "--session-scope",
            session_scope.value,
            "--selection-mode",
            selection_mode.value,
            "--price-view",
            price_view.value,
            "--progress-every",
            str(progress_every.value),
            "--partial-flush-every",
            str(partial_flush_every.value),
            "--workers",
            str(workers.value),
        ]
        if tickers.value.strip():
            parts.extend(["--tickers", _ps_quote(tickers.value.strip())])
        if years.value.strip():
            parts.extend(["--years", _ps_quote(years.value.strip())])
        if not rising_highs.value:
            parts.append("--no-rising-highs")
        if not close_above_prev_high.value:
            parts.append("--no-close-above-prev-high")
        return " ".join(parts)

    def _refresh_command(_change: dict | None = None) -> None:
        command_preview.value = _terminal_command()

    def _set_candidates(
        candidates: pd.DataFrame,
        run_dir: Path | None,
        select_latest: bool = False,
    ) -> None:
        candidates = _sort_candidates_for_review(candidates)
        state["candidates"] = candidates
        if run_dir is not None:
            state["run_dir"] = run_dir
            run_dir_text.value = str(run_dir)
        if candidates.empty:
            candidate_dropdown.options = []
            return
        options = []
        for r in candidates.itertuples(index=False):
            symbol = getattr(r, "tradingview_symbol", None)
            if symbol is None or pd.isna(symbol):
                symbol = r.ticker
            options.append((f"{symbol} {r.session_date} {r.event_ts_et} push={r.push_pct:.2f}%", r.candidate_id))
        candidate_dropdown.options = options
        if select_latest and options:
            candidate_dropdown.value = options[0][1]

    def _refresh_run_list() -> None:
        options = _list_run_options()
        run_dropdown.options = options
        if options:
            run_dropdown.value = options[0][1]

    def _run_search(_button: widgets.Button) -> None:
        with out:
            clear_output()
            config = FindConfig(
                data_root=data_root.value,
                reference_overview_root=DEFAULT_REFERENCE_OVERVIEW_ROOT,
                output_root=str(DEFAULT_RUNS_ROOT),
                universe_path=universe_path.value,
                use_lt1b_universe=True,
                tickers=_parse_tickers(tickers.value),
                years=_parse_years(years.value),
                push_pct=push_pct.value,
                min_session_volume=min_volume.value,
                min_price=min_price.value,
                max_market_cap=max_market_cap.value,
                missing_market_cap_policy=missing_cap.value,
                session_scope=session_scope.value,
                selection_mode=selection_mode.value,
                price_view=price_view.value,
                require_rising_highs=rising_highs.value,
                require_close_above_prev_high=close_above_prev_high.value,
                require_same_segment=False,
                progress_every=progress_every.value,
                partial_flush_every=partial_flush_every.value,
                workers=workers.value,
                write_outputs=True,
            )
            print("Running Event Discovery query inside Jupyter...")
            run_dir = create_run_dir(config)
            print(f"Run: {run_dir}")
            print("Status: running")
            try:
                candidates = find_candidates(config, run_dir=run_dir)
            except Exception as exc:
                mark_run_failed(run_dir, config, error=repr(exc))
                print("Status: failed")
                raise
            finalize_run(run_dir, candidates, config)
            _set_candidates(candidates, run_dir)
            print("Status: completed")
            print(f"Candidates: {len(candidates)}")
            print("Delete this run if needed:")
            print(_delete_run_command(run_dir))
            display(candidates.head(20))
            _refresh_run_list()

    def _load_run(_button: widgets.Button) -> None:
        with out:
            clear_output()
            if not run_dir_text.value.strip():
                print("Paste a run_dir first, or use Load latest.")
                return
            run_dir = Path(run_dir_text.value.strip())
            if not run_dir.exists():
                print(f"Run dir not found: {run_dir}")
                return
            candidates = _load_candidates_from_run(run_dir)
            _set_candidates(candidates, run_dir)
            print(f"Loaded run: {run_dir}")
            print(f"Candidates: {len(candidates)}")
            print("Delete this run if needed:")
            print(_delete_run_command(run_dir))
            if not candidates.empty:
                display(candidates.head(20))

    def _load_selected_run(_button: widgets.Button) -> None:
        if not run_dropdown.value:
            with out:
                clear_output()
                print("No run selected. Use Refresh runs first.")
            return
        run_dir_text.value = str(run_dropdown.value)
        _load_run(_button)

    def _load_latest_run(_button: widgets.Button) -> None:
        with out:
            clear_output()
            _refresh_run_list()
            if not run_dropdown.value:
                print(f"No runs found under {DEFAULT_RUNS_ROOT}")
                return
            run_dir_text.value = str(run_dropdown.value)
        _load_run(_button)

    def _refresh_partial(_button: widgets.Button) -> None:
        with out:
            clear_output()
            if not run_dir_text.value.strip():
                print("Paste a run_dir first, or use Load latest.")
                return
            run_dir = Path(run_dir_text.value.strip())
            if not run_dir.exists():
                print(f"Run dir not found: {run_dir}")
                return
            candidates = _load_partial_candidates_from_run(run_dir)
            _set_candidates(candidates, run_dir, select_latest=True)
            print(f"Loaded partial run: {run_dir}")
            print(f"Partial candidates: {len(candidates)}")
            if not candidates.empty:
                display(candidates.head(20))

    def _render(_button: widgets.Button) -> None:
        with out:
            if "candidates" not in state:
                print("Run a search first.")
                return
            candidates = state["candidates"]
            assert isinstance(candidates, pd.DataFrame)
            candidate_id = candidate_dropdown.value
            if not candidate_id:
                print("No candidate selected.")
                return
            row = candidates[candidates["candidate_id"].eq(candidate_id)].iloc[0].to_dict()
            clear_output()
            print(f"Rendering {candidate_id}")
            fig = render_candidate(
                row,
                data_root=data_root.value,
                reference_overview_root=DEFAULT_REFERENCE_OVERVIEW_ROOT,
                y_padding_pct=y_padding.value,
            )
            fig.show(config={"scrollZoom": True, "displaylogo": False})

    run_button.on_click(_run_search)
    refresh_runs_button.on_click(lambda _button: _refresh_run_list())
    load_selected_run_button.on_click(_load_selected_run)
    load_run_button.on_click(_load_run)
    load_latest_button.on_click(_load_latest_run)
    refresh_partial_button.on_click(_refresh_partial)
    render_button.on_click(_render)
    for control in [
        data_root,
        universe_path,
        tickers,
        years,
        push_pct,
        min_volume,
        min_price,
        max_market_cap,
        missing_cap,
        session_scope,
        selection_mode,
        price_view,
        rising_highs,
        close_above_prev_high,
        progress_every,
        partial_flush_every,
        workers,
    ]:
        control.observe(_refresh_command, names="value")
    _refresh_command()
    _refresh_run_list()

    controls = widgets.VBox(
        [
            data_root,
            universe_path,
            universe_notice,
            widgets.HBox([tickers, years]),
            widgets.HBox([push_pct, min_volume, min_price, max_market_cap, missing_cap, price_view]),
            widgets.HBox([session_scope, selection_mode]),
            widgets.HBox([rising_highs, close_above_prev_high, y_padding, progress_every, partial_flush_every, workers]),
            control_help,
            command_preview,
            widgets.HBox([refresh_runs_button, load_selected_run_button, load_latest_button]),
            run_dropdown,
            run_dir_text,
            widgets.HBox([load_run_button, refresh_partial_button, render_button, run_button]),
            candidate_dropdown,
            out,
        ]
    )
    return controls


def tradingview_widget(symbol: str = "NASDAQ:CCSC", interval: str = "1") -> HTML:
    """Return a free TradingView embed widget for notebook-side visual checking."""
    html = f"""
    <div class="tradingview-widget-container" style="height:760px;width:100%">
      <div id="tradingview_event_discovery" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{symbol}",
        "interval": "{interval}",
        "timezone": "America/New_York",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "calendar": false,
        "container_id": "tradingview_event_discovery"
      }});
      </script>
    </div>
    """
    return HTML(html)
