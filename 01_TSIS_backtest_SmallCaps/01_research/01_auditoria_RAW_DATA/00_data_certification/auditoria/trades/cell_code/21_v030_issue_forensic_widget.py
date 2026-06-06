from __future__ import annotations

from pathlib import Path
from typing import Any

import ipywidgets as widgets
import numpy as np
import pandas as pd
from IPython.display import Markdown, clear_output, display


def build_issue_case_view(hard_v030: pd.DataFrame, issue_name: str) -> pd.DataFrame:
    x = hard_v030[hard_v030["issues_list"].map(lambda xs: issue_name in set(xs))].copy()
    x["outside_below_abs"] = (
        pd.to_numeric(x.get("m.l"), errors="coerce")
        - pd.to_numeric(x.get("m.price_min"), errors="coerce")
    ).clip(lower=0)
    x["outside_above_abs"] = (
        pd.to_numeric(x.get("m.price_max"), errors="coerce")
        - pd.to_numeric(x.get("m.h"), errors="coerce")
    ).clip(lower=0)
    x["daily_span"] = (
        pd.to_numeric(x.get("m.h"), errors="coerce")
        - pd.to_numeric(x.get("m.l"), errors="coerce")
    )
    x["outside_abs_max"] = x[["outside_below_abs", "outside_above_abs"]].max(axis=1)
    x["outside_pct_of_daily_span"] = 100.0 * x["outside_abs_max"] / x["daily_span"].replace(0, np.nan)
    x["breaks_1m_warn"] = x["warns_list"].map(lambda xs: "trade_price_outside_1m_range" in set(xs))
    return x.sort_values(["outside_pct_of_daily_span", "outside_abs_max", "ticker", "date"], ascending=[False, False, True, True]).reset_index(drop=True)


def build_issue_ticker_options(hard_v030: pd.DataFrame, issue_name: str) -> list[str]:
    x = build_issue_case_view(hard_v030, issue_name)
    tickers = sorted(x["ticker"].dropna().astype(str).unique().tolist())
    return ["__ALL__"] + tickers


def build_issue_date_options(hard_v030: pd.DataFrame, issue_name: str, ticker_name: str) -> list[str]:
    x = build_issue_case_view(hard_v030, issue_name)
    if ticker_name != "__ALL__":
        x = x[x["ticker"].astype(str) == str(ticker_name)].copy()
    dates = sorted(x["date"].dropna().astype(str).unique().tolist())
    return ["__ALL__"] + dates


def build_filtered_issue_cases(
    hard_v030: pd.DataFrame,
    issue_name: str,
    ticker_name: str = "__ALL__",
    date_value: str = "__ALL__",
) -> pd.DataFrame:
    x = build_issue_case_view(hard_v030, issue_name)
    if ticker_name != "__ALL__":
        x = x[x["ticker"].astype(str) == str(ticker_name)].copy()
    if date_value != "__ALL__":
        x = x[x["date"].astype(str) == str(date_value)].copy()
    return x.reset_index(drop=True)


def build_case_options(df: pd.DataFrame) -> list[tuple[str, int]]:
    opts: list[tuple[str, int]] = []
    for i, row in df.iterrows():
        label = (
            f"{i:04d} | {row['ticker']} | {row['date']} | "
            f"gap={row.get('outside_pct_of_daily_span', np.nan):.2f}% | "
            f"1m_break={bool(row.get('breaks_1m_warn', False))}"
        )
        opts.append((label, i))
    return opts


def run_v030_issue_forensic_widget(
    hard_v030: pd.DataFrame,
    issue_counts_v030: pd.DataFrame,
    forensic_mod: dict[str, Any],
    ohlcv_daily_root: Path,
    ohlcv_1m_root: Path,
) -> None:
    issue_dropdown = widgets.Dropdown(
        options=issue_counts_v030["issue"].tolist(),
        value=issue_counts_v030["issue"].tolist()[0] if not issue_counts_v030.empty else None,
        description="Issue",
        layout=widgets.Layout(width="720px"),
    )
    ticker_dropdown = widgets.Dropdown(
        options=["__ALL__"],
        value="__ALL__",
        description="Ticker",
        layout=widgets.Layout(width="380px"),
    )
    date_dropdown = widgets.Dropdown(
        options=["__ALL__"],
        value="__ALL__",
        description="Date",
        layout=widgets.Layout(width="280px"),
    )
    case_dropdown = widgets.Dropdown(
        options=[],
        value=None,
        description="Caso",
        layout=widgets.Layout(width="1200px"),
    )
    controls_box = widgets.VBox([
        issue_dropdown,
        widgets.HBox([ticker_dropdown, date_dropdown]),
        case_dropdown,
    ])

    def refresh_ticker_options() -> None:
        opts = build_issue_ticker_options(hard_v030, issue_dropdown.value)
        ticker_dropdown.options = opts
        if ticker_dropdown.value not in opts:
            ticker_dropdown.value = "__ALL__"

    def refresh_date_options() -> None:
        opts = build_issue_date_options(hard_v030, issue_dropdown.value, ticker_dropdown.value)
        date_dropdown.options = opts
        if date_dropdown.value not in opts:
            date_dropdown.value = "__ALL__"

    def refresh_case_options() -> pd.DataFrame:
        df = build_filtered_issue_cases(
            hard_v030=hard_v030,
            issue_name=issue_dropdown.value,
            ticker_name=ticker_dropdown.value,
            date_value=date_dropdown.value,
        )
        opts = build_case_options(df)
        case_dropdown.options = opts
        case_dropdown.disabled = len(opts) == 0
        if len(opts) == 0:
            case_dropdown.value = None
        else:
            values = [v for _, v in opts]
            if case_dropdown.value not in values:
                case_dropdown.value = values[0]
        return df

    def render_selected_case() -> None:
        df = build_filtered_issue_cases(
            hard_v030=hard_v030,
            issue_name=issue_dropdown.value,
            ticker_name=ticker_dropdown.value,
            date_value=date_dropdown.value,
        )
        clear_output(wait=True)
        display(controls_box)

        if df.empty or case_dropdown.value is None:
            display(Markdown("## Sin casos para esta seleccion"))
            return

        row = df.iloc[int(case_dropdown.value)]
        case_ctx = forensic_mod["load_trade_daily_1m_case_refs"](
            case_row=row,
            ohlcv_daily_root=ohlcv_daily_root,
            ohlcv_1m_root=ohlcv_1m_root,
        )
        trades_df, daily_low, daily_high, daily_open, daily_close, daily_vw = forensic_mod["annotate_trade_outside_daily"](
            case_ctx["trades_df"],
            case_ctx["daily_row"],
        )
        summary_rows = forensic_mod["build_case_summary_table"](
            trades_df,
            daily_low,
            daily_high,
            daily_vw,
        )

        market_path = Path(row["file"])
        display(Markdown(
            f"""
## Seleccion
- `issue`: `{issue_dropdown.value}`
- `ticker`: `{ticker_dropdown.value}`
- `date`: `{date_dropdown.value}`
- `casos filtrados`: `{len(df):,}`

## Caso seleccionado
- `ticker`: `{case_ctx['ticker']}`
- `date`: `{case_ctx['date_str']}`
- `market.parquet`: `{market_path}`
- `daily_path`: `{case_ctx['daily_path']}`
- `m1_path`: `{case_ctx['m1_path']}`
- `outside_pct_of_daily_span`: `{row.get('outside_pct_of_daily_span', np.nan):.4f}%`
- `breaks_1m_warn`: `{bool(row.get('breaks_1m_warn', False))}`
- `off_session_trade_pct`: `{row.get('m.off_session_trade_pct', np.nan):.4f}`
- `same_scale_context`: `{row.get('same_scale_context_flag', row.get('m.same_scale_context', None))}`
- `scale_mismatch_confidence`: `{row.get('m.scale_mismatch_confidence', None)}`
- `issues`: `{row['issues_list']}`
- `warns`: `{row['warns_list']}`
"""
        ))

        forensic_mod["plot_trade_vs_daily_1m_case"](
            ticker=case_ctx["ticker"],
            date_str=case_ctx["date_str"],
            trades_df=trades_df,
            m1_day=case_ctx["m1_day"],
            daily_low=daily_low,
            daily_high=daily_high,
            daily_open=daily_open,
            daily_close=daily_close,
            daily_vw=daily_vw,
            summary_rows=summary_rows,
        )
        forensic_mod["plot_trade_vs_reference_scale_comparison"](
            trades_df=trades_df,
            m1_day=case_ctx["m1_day"],
            daily_low=daily_low,
            daily_high=daily_high,
            daily_close=daily_close,
            daily_vw=daily_vw,
        )

    def on_issue_change(change: dict[str, Any]) -> None:
        if change["name"] == "value":
            refresh_ticker_options()
            refresh_date_options()
            refresh_case_options()
            render_selected_case()

    def on_ticker_change(change: dict[str, Any]) -> None:
        if change["name"] == "value":
            refresh_date_options()
            refresh_case_options()
            render_selected_case()

    def on_date_change(change: dict[str, Any]) -> None:
        if change["name"] == "value":
            refresh_case_options()
            render_selected_case()

    def on_case_change(change: dict[str, Any]) -> None:
        if change["name"] == "value":
            render_selected_case()

    issue_dropdown.observe(on_issue_change, names="value")
    ticker_dropdown.observe(on_ticker_change, names="value")
    date_dropdown.observe(on_date_change, names="value")
    case_dropdown.observe(on_case_change, names="value")

    if not issue_counts_v030.empty:
        refresh_ticker_options()
        refresh_date_options()
        refresh_case_options()
    display(controls_box)
    render_selected_case()
