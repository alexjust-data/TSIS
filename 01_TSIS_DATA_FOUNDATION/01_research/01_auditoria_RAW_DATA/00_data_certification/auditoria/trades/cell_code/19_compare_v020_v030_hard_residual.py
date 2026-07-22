from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, display


SMALL_TITLE_SIZE = 11
SMALL_LABEL_SIZE = 9
SMALL_TICK_SIZE = 8


def flatten_token_series(series) -> list[str]:
    out: list[str] = []
    for value in series:
        if value is None:
            continue
        if isinstance(value, list):
            out.extend(str(x) for x in value if pd.notna(x))
        else:
            out.append(str(value))
    return out


def issue_counts(df: pd.DataFrame) -> pd.DataFrame:
    return (
        pd.Series(flatten_token_series(df["issues_list"]), dtype="object")
        .value_counts()
        .rename_axis("issue")
        .reset_index(name="files")
    )


def build_v020_v030_comparison(
    v020: pd.DataFrame,
    v030: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    v020 = v020.copy()
    v030 = v030.copy()

    v020["file_key"] = v020["file"].astype(str)
    v030["file_key"] = v030["file"].astype(str)

    hard020 = v020[v020["severity"] == "HARD_FAIL"].copy()
    hard030 = v030[v030["severity"] == "HARD_FAIL"].copy()

    cmp = (
        v020[["file_key", "ticker", "date", "severity", "issues_list", "warns_list"]]
        .rename(
            columns={
                "severity": "severity_v020",
                "issues_list": "issues_v020",
                "warns_list": "warns_v020",
            }
        )
        .merge(
            v030[
                ["file_key", "severity", "issues_list", "warns_list"]
                + [c for c in v030.columns if c.startswith("m.")]
            ].rename(
                columns={
                    "severity": "severity_v030",
                    "issues_list": "issues_v030",
                    "warns_list": "warns_v030",
                }
            ),
            on="file_key",
            how="inner",
        )
    )
    cmp["transition"] = cmp["severity_v020"] + " -> " + cmp["severity_v030"]
    return cmp, hard020, hard030


def build_issue_comparison(hard020: pd.DataFrame, hard030: pd.DataFrame) -> pd.DataFrame:
    issue020 = issue_counts(hard020).rename(columns={"files": "files_v020"})
    issue030 = issue_counts(hard030).rename(columns={"files": "files_v030"})

    issue_cmp = issue020.merge(issue030, on="issue", how="outer").fillna(0)
    issue_cmp["files_v020"] = issue_cmp["files_v020"].astype(int)
    issue_cmp["files_v030"] = issue_cmp["files_v030"].astype(int)
    issue_cmp["delta_v030_minus_v020"] = issue_cmp["files_v030"] - issue_cmp["files_v020"]
    issue_cmp = issue_cmp.sort_values(["files_v030", "files_v020"], ascending=False).reset_index(drop=True)
    return issue_cmp


def display_exact_requested_counts(issue_cmp: pd.DataFrame) -> None:
    count_daily_and_1m = int(
        issue_cmp.loc[
            issue_cmp["issue"] == "trade_price_outside_daily_and_1m_range",
            "files_v030",
        ].sum()
    )
    count_daily_only = int(
        issue_cmp.loc[
            issue_cmp["issue"] == "trade_price_outside_daily_range",
            "files_v030",
        ].sum()
    )

    display(
        Markdown(
            f"""
### Conteos exactos pedidos
- `trade_price_outside_daily_and_1m_range` en `v030`: `{count_daily_and_1m:,}`
- `trade_price_outside_daily_range` en `v030`: `{count_daily_only:,}`
"""
        )
    )


def plot_issue_residual_overview(issue_cmp: pd.DataFrame, top_n: int = 15) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    sns.barplot(data=issue_cmp.head(top_n), y="issue", x="files_v030", color="#d62828", ax=ax)
    ax.set_title("Causas que siguen vivas en los HARD_FAIL de v030", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("files_v030", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()

    issue_cmp_nonzero = issue_cmp[(issue_cmp["files_v020"] > 0) | (issue_cmp["files_v030"] > 0)].copy()
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    sns.barplot(
        data=issue_cmp_nonzero.head(top_n),
        y="issue",
        x="delta_v030_minus_v020",
        color="#457b9d",
        ax=ax,
    )
    ax.set_title("Cambio de causas duras: v030 - v020", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("delta_v030_minus_v020", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()


def build_transition_counts(cmp_df: pd.DataFrame) -> pd.DataFrame:
    return (
        cmp_df["transition"]
        .value_counts()
        .rename_axis("transition")
        .reset_index(name="files")
    )


def plot_transition_counts(transition_counts: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    sns.barplot(data=transition_counts, y="transition", x="files", color="#6d597a", ax=ax)
    ax.set_title("Transiciones de severidad v020 -> v030", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()


def build_v030_reality_buckets(hard030: pd.DataFrame) -> pd.DataFrame:
    hard030 = hard030.copy()

    hard030["has_daily_and_1m_issue"] = hard030["issues_list"].map(
        lambda xs: "trade_price_outside_daily_and_1m_range" in set(xs)
    )
    hard030["has_daily_only_issue"] = hard030["issues_list"].map(
        lambda xs: "trade_price_outside_daily_range" in set(xs)
    )
    hard030["has_1m_warn"] = hard030["warns_list"].map(
        lambda xs: "trade_price_outside_1m_range" in set(xs)
    )

    if "m.same_scale_context" in hard030.columns:
        hard030["same_scale_context_flag"] = hard030["m.same_scale_context"].fillna(False).astype(bool)
    else:
        pf_daily = pd.to_numeric(hard030.get("m.possible_price_scale_factor_vs_daily"), errors="coerce")
        pf_1m = pd.to_numeric(hard030.get("m.possible_price_scale_factor_vs_1m"), errors="coerce")
        hard030["same_scale_context_flag"] = (
            pf_daily.between(0.8, 1.2, inclusive="both")
            & pf_1m.between(0.8, 1.2, inclusive="both")
        )

    if "m.scale_mismatch_detected" in hard030.columns:
        hard030["scale_mismatch_flag"] = hard030["m.scale_mismatch_detected"].fillna(False).astype(bool)
    else:
        hard030["scale_mismatch_flag"] = False

    def classify_reality_bucket(row: pd.Series) -> str:
        if row["has_daily_and_1m_issue"] and row["same_scale_context_flag"] and not row["scale_mismatch_flag"]:
            return "confirmed_multi_reference_same_scale"
        if row["has_daily_only_issue"] and row["same_scale_context_flag"] and not row["scale_mismatch_flag"]:
            return "daily_only_same_scale"
        if row["scale_mismatch_flag"]:
            return "possible_scale_mismatch_still_hard"
        return "other_hard"

    hard030["reality_bucket"] = hard030.apply(classify_reality_bucket, axis=1)
    return hard030


def build_reality_counts(hard030: pd.DataFrame) -> pd.DataFrame:
    out = (
        hard030["reality_bucket"]
        .value_counts()
        .rename_axis("reality_bucket")
        .reset_index(name="files")
    )
    out["pct"] = 100.0 * out["files"] / max(len(hard030), 1)
    return out


def plot_reality_counts(reality_counts: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    sns.barplot(data=reality_counts, y="reality_bucket", x="files", color="#2a9d8f", ax=ax)
    ax.set_title("¿En qué se concentra el HARD_FAIL de v030?", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()


def plot_confirmed_residual_detail(hard030: pd.DataFrame, top_n_tickers: int = 15) -> None:
    confirmed = hard030[hard030["reality_bucket"] == "confirmed_multi_reference_same_scale"].copy()
    display(Markdown(f"### Residuo confirmado por dos referencias: `{len(confirmed):,}` files"))

    if confirmed.empty:
        return

    numeric_cols = [
        "m.off_session_trade_pct",
        "m.duplicate_excess_ratio_pct",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
    ]
    for c in numeric_cols:
        if c in confirmed.columns:
            confirmed[c] = pd.to_numeric(confirmed[c], errors="coerce")

    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    sns.boxplot(data=confirmed, x="has_1m_warn", y="m.off_session_trade_pct", ax=ax)
    ax.set_title("off_session_trade_pct dentro del residuo confirmado", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("has_1m_warn", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("off_session_trade_pct", fontsize=SMALL_LABEL_SIZE)
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()

    top_confirmed_tickers = (
        confirmed.groupby("ticker")
        .size()
        .sort_values(ascending=False)
        .head(top_n_tickers)
        .rename_axis("ticker")
        .reset_index(name="files")
    )

    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    sns.barplot(data=top_confirmed_tickers, y="ticker", x="files", color="#264653", ax=ax)
    ax.set_title("Top tickers dentro del residuo confirmado por daily+1m", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()


def display_reality_examples(hard030: pd.DataFrame, top_n: int = 10) -> None:
    decision_cols = [
        "ticker",
        "date",
        "reality_bucket",
        "issues_list",
        "warns_list",
        "m.same_scale_context",
        "m.scale_mismatch_confidence",
        "m.scale_mismatch_detected",
        "m.outside_daily_detected",
        "m.outside_1m_detected",
        "m.off_session_trade_pct",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
        "file",
    ]
    decision_cols = [c for c in decision_cols if c in hard030.columns]

    display(Markdown("### Ejemplos del residuo confirmado por dos referencias"))
    display(
        hard030[decision_cols][hard030["reality_bucket"] == "confirmed_multi_reference_same_scale"]
        .sort_values(["ticker", "date"])
        .head(top_n)
    )

    display(Markdown("### Ejemplos del residuo daily-only same-scale"))
    display(
        hard030[decision_cols][hard030["reality_bucket"] == "daily_only_same_scale"]
        .sort_values(["ticker", "date"])
        .head(top_n)
    )


def display_v030_residual_interpretation() -> None:
    display(Markdown(
        """
## Cómo leer esta celda

- Si `trade_price_outside_daily_and_1m_range` concentra gran parte del residuo:
  el `HARD_FAIL` ya está migrando a casos más reales y confirmados.

- Si `trade_price_outside_daily_range` sigue alto:
  todavía queda peso excesivo de `daily` sola y conviene una iteración adicional.

- Si `confirmed_multi_reference_same_scale` domina el residuo:
  la limpieza ya va bien y el `HARD_FAIL` restante es defendible.

- Si `daily_only_same_scale` sigue dominando:
  `daily` sigue pesando demasiado y todavía no hemos terminado.
"""
    ))
