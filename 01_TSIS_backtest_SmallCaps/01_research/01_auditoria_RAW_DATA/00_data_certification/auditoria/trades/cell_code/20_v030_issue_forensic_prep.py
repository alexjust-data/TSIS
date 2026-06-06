from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, display


SMALL_TITLE_SIZE = 11
SMALL_LABEL_SIZE = 9
SMALL_TICK_SIZE = 8


NUMERIC_COLS_V030 = [
    "m.possible_price_scale_factor_vs_daily",
    "m.possible_price_scale_factor_vs_1m",
    "m.trade_volume_vs_daily_ratio",
    "m.trade_volume_vs_1m_ratio",
    "m.off_session_trade_pct",
    "m.duplicate_excess_ratio_pct",
    "m.ohlcv_1m_low_min",
    "m.ohlcv_1m_high_max",
    "m.price_min",
    "m.price_max",
    "m.trade_vwap",
    "m.vw",
    "m.l",
    "m.h",
    "m.scale_mismatch_confidence",
]


def flatten_token_series(series: pd.Series) -> list[str]:
    out: list[str] = []
    for value in series:
        if value is None:
            continue
        if isinstance(value, list):
            out.extend(str(x) for x in value if pd.notna(x))
        else:
            out.append(str(value))
    return out


def build_hard_v030_view(v030: pd.DataFrame) -> pd.DataFrame:
    hard_v030 = v030[v030["severity"] == "HARD_FAIL"].copy()
    for col in NUMERIC_COLS_V030:
        if col in hard_v030.columns:
            hard_v030[col] = pd.to_numeric(hard_v030[col], errors="coerce")

    if "file" in hard_v030.columns:
        hard_v030["file_key"] = hard_v030["file"].astype(str)

    hard_v030["breaks_1m_warn"] = hard_v030["warns_list"].map(
        lambda xs: "trade_price_outside_1m_range" in set(xs)
    )

    if "m.same_scale_context" in hard_v030.columns:
        hard_v030["same_scale_context_flag"] = hard_v030["m.same_scale_context"].fillna(False).astype(bool)
    else:
        hard_v030["same_scale_context_flag"] = False

    hard_v030["outside_below_abs"] = (
        pd.to_numeric(hard_v030.get("m.l"), errors="coerce")
        - pd.to_numeric(hard_v030.get("m.price_min"), errors="coerce")
    ).clip(lower=0)
    hard_v030["outside_above_abs"] = (
        pd.to_numeric(hard_v030.get("m.price_max"), errors="coerce")
        - pd.to_numeric(hard_v030.get("m.h"), errors="coerce")
    ).clip(lower=0)
    hard_v030["daily_span"] = (
        pd.to_numeric(hard_v030.get("m.h"), errors="coerce")
        - pd.to_numeric(hard_v030.get("m.l"), errors="coerce")
    )
    hard_v030["outside_abs_max"] = hard_v030[["outside_below_abs", "outside_above_abs"]].max(axis=1)
    hard_v030["outside_pct_of_daily_span"] = (
        100.0 * hard_v030["outside_abs_max"] / hard_v030["daily_span"].replace(0, np.nan)
    )
    return hard_v030


def build_issue_counts_v030(hard_v030: pd.DataFrame) -> pd.DataFrame:
    vals = pd.Series(flatten_token_series(hard_v030["issues_list"]), dtype="object")
    if vals.empty:
        return pd.DataFrame(columns=["issue", "files"])
    return vals.value_counts().rename_axis("issue").reset_index(name="files")


def build_issue_evidence(hard_v030: pd.DataFrame, issue_counts_v030: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for issue_name in issue_counts_v030["issue"].tolist():
        x = hard_v030[hard_v030["issues_list"].map(lambda xs: issue_name in set(xs))].copy()
        rows.append(
            {
                "issue": issue_name,
                "files": int(len(x)),
                "tickers": int(x["ticker"].nunique()) if "ticker" in x.columns else 0,
                "dates": int(x["date"].nunique()) if "date" in x.columns else 0,
                "same_scale_pct": 100.0 * x["same_scale_context_flag"].mean() if len(x) else np.nan,
                "has_1m_warn_pct": 100.0 * x["breaks_1m_warn"].mean() if len(x) else np.nan,
                "median_off_session_pct": pd.to_numeric(x.get("m.off_session_trade_pct"), errors="coerce").median() if len(x) else np.nan,
                "median_gap_pct_of_daily_span": pd.to_numeric(x.get("outside_pct_of_daily_span"), errors="coerce").median() if len(x) else np.nan,
                "median_scale_mismatch_confidence": pd.to_numeric(x.get("m.scale_mismatch_confidence"), errors="coerce").median() if len(x) else np.nan,
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["files", "has_1m_warn_pct", "same_scale_pct"], ascending=[False, False, False]).reset_index(drop=True)


def plot_issue_evidence(issue_evidence: pd.DataFrame, top_n: int = 12) -> None:
    if issue_evidence.empty:
        return

    plot_df = issue_evidence.head(top_n).copy()

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    sns.barplot(data=plot_df, y="issue", x="files", color="#d62828", ax=ax)
    ax.set_title("Peso de cada issue vivo en HARD_FAIL v030", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    sns.barplot(data=plot_df, y="issue", x="has_1m_warn_pct", color="#2a9d8f", ax=ax)
    ax.set_title("Confirmacion por 1m dentro de cada issue vivo", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("has_1m_warn_pct", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    sns.barplot(data=plot_df, y="issue", x="same_scale_pct", color="#457b9d", ax=ax)
    ax.set_title("Contexto de misma escala por issue vivo", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("same_scale_pct", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()


def display_issue_forensic_interpretation() -> None:
    display(Markdown(
        """
## Como leer esta preparacion

- Si una `issue` concentra muchos files y alta confirmacion por `1m`, es una buena candidata a seguir dura.
- Si una `issue` domina el residuo pero con baja confirmacion por `1m`, conviene reabrir su contrato antes de consolidarla.
- Si ademas aparece con `same_scale_pct` alto, el residuo es mas defendible como ruptura real y no como problema de escala.
- La combinacion de `median_off_session_pct` y `median_gap_pct_of_daily_span` ayuda a separar sesgo de sesion frente a rotura estructural.
"""
    ))
