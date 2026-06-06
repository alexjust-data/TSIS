from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

matplotlib.use("Agg")

from scripts.inspection.trades.trades_case_panel import (  # noqa: E402
    _build_sample_case_figure,
    _case_visual_subfamily,
    _case_visual_subfamily_explanation,
    _family_description,
    _family_questions,
    _load_trade_case_df,
    _sample_case_reading,
)

MANIFEST_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "trades" / "evidence_assets" / "stratified_samples"
OUT_ROOT = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "trades" / "family_case_evidence_packs"
CACHE_ROOT = PROJECT_ROOT / "runs" / "backtest" / "trades_v2_materialized" / "trades_current_cd_merged" / "root_cause_exports" / "file_acceptance_cache_lt1b_full_clean_fast_same_schema"
RAW_SHARDS_DIR = CACHE_ROOT / "raw_metrics_shards"
INDEX_SHARDS_DIR = CACHE_ROOT / "full_index_shards"


FAMILY_TITLES = {
    "review": "Trades Review Generico | muestra estratificada",
    "reference_scale_mismatch": "Trades Reference Scale Mismatch | muestra estratificada",
    "review_microstructure": "Trades Review Microstructure | muestra estratificada",
    "bad_data": "Trades Bad Data | muestra estratificada",
    "review_no_1m_reference": "Trades Review No 1m Reference | muestra estratificada",
    "review_1m_reference_alignment": "Trades Review 1m Reference Alignment | muestra estratificada",
    "good": "Trades Good | enumeracion completa",
}


def _fmt_pct(value) -> str:
    try:
        x = float(value)
    except Exception:
        return "nan%"
    if pd.isna(x):
        return "nan%"
    return f"{x:.2f}%"


def _slug(text: str) -> str:
    return (
        str(text)
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
        .replace(":", "_")
        .replace("|", "_")
    )


def _md_table(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return ["- sin filas"]
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "|" + "|".join(["---"] * len(cols)) + "|",
    ]
    for _, row in df.iterrows():
        vals = []
        for c in cols:
            v = row[c]
            if isinstance(v, (list, tuple, np.ndarray)):
                parts = []
                for x in list(v):
                    try:
                        if pd.isna(x):
                            parts.append("")
                        else:
                            parts.append(str(x))
                    except Exception:
                        parts.append(str(x))
                vals.append(", ".join(parts))
                continue
            try:
                if pd.isna(v):
                    vals.append("")
                    continue
            except Exception:
                pass
            vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return lines


def _invalid_rows_table(case_row: pd.Series) -> pd.DataFrame:
    trades = _load_trade_case_df(case_row)
    if trades.empty or "size" not in trades.columns:
        return pd.DataFrame()
    x = trades.loc[pd.to_numeric(trades["size"], errors="coerce").le(0).fillna(False)].copy()
    if x.empty:
        return x
    keep = [c for c in ["ts_ny", "price", "size", "exchange", "conditions"] if c in x.columns]
    x = x[keep].copy()
    if "ts_ny" in x.columns:
        x["ts_ny"] = x["ts_ny"].astype(str)
    return x.head(10)


def _duplicate_groups_table(case_row: pd.Series) -> pd.DataFrame:
    trades = _load_trade_case_df(case_row)
    if trades.empty:
        return pd.DataFrame()
    subset = [c for c in ["ts_ny", "price", "size"] if c in trades.columns]
    if len(subset) < 3:
        return pd.DataFrame()
    x = trades.copy()
    grp = (
        x.groupby(subset, dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["count", "ts_ny"], ascending=[False, True])
    )
    grp = grp.loc[grp["count"] > 1].head(10)
    if grp.empty:
        return grp
    grp["ts_ny"] = grp["ts_ny"].astype(str)
    return grp


def _build_bad_data_population_summary() -> dict:
    policy = pd.read_parquet(CACHE_ROOT / "layer6_policy_summary_full.parquet")
    total_files = int(policy["files"].sum())
    bad_total = int(policy.loc[policy["acceptance_label"] == "bad_data", "files"].iloc[0])

    counts = {
        "trade_price_outside_daily_range": 0,
        "scale_bucket_vw_nan": 0,
        "outside_daily_100": 0,
        "outside_1m_100": 0,
        "negative_or_zero_size_rows": 0,
        "duplicate_excess_ratio_gt_hard_cap": 0,
        "structural_only": 0,
        "structural_mixed": 0,
    }

    for raw_path, idx_path in zip(sorted(RAW_SHARDS_DIR.glob("*.parquet")), sorted(INDEX_SHARDS_DIR.glob("*.parquet"))):
        raw = pd.read_parquet(
            raw_path,
            columns=["ticker", "date", "sample_stratum", "acceptance_label", "scale_bucket_vw", "outside_daily_regular_pct", "outside_1m_regular_pct"],
        )
        raw = raw.loc[raw["acceptance_label"] == "bad_data"].copy()
        if raw.empty:
            continue
        idx = pd.read_parquet(idx_path, columns=["ticker", "date", "sample_stratum", "issues_list"])
        x = raw.merge(idx, on=["ticker", "date", "sample_stratum"], how="left")

        def has_token(v, token: str) -> bool:
            if isinstance(v, np.ndarray):
                return token in [str(i) for i in v.tolist()]
            if isinstance(v, (list, tuple, set)):
                return token in [str(i) for i in v]
            if pd.isna(v) if np.isscalar(v) else False:
                return False
            return token == str(v)

        issues = x["issues_list"]
        structural_mask = issues.apply(lambda v: has_token(v, "negative_or_zero_size_rows") or has_token(v, "duplicate_excess_ratio_gt_hard_cap"))
        daily_range_mask = issues.apply(lambda v: has_token(v, "trade_price_outside_daily_range"))
        counts["trade_price_outside_daily_range"] += int(daily_range_mask.sum())
        counts["scale_bucket_vw_nan"] += int((x["scale_bucket_vw"].astype(str) == "nan").sum())
        counts["outside_daily_100"] += int(pd.to_numeric(x["outside_daily_regular_pct"], errors="coerce").ge(100).fillna(False).sum())
        counts["outside_1m_100"] += int(pd.to_numeric(x["outside_1m_regular_pct"], errors="coerce").ge(100).fillna(False).sum())
        counts["negative_or_zero_size_rows"] += int(issues.apply(lambda v: has_token(v, "negative_or_zero_size_rows")).sum())
        counts["duplicate_excess_ratio_gt_hard_cap"] += int(issues.apply(lambda v: has_token(v, "duplicate_excess_ratio_gt_hard_cap")).sum())
        counts["structural_only"] += int((structural_mask & ~daily_range_mask).sum())
        counts["structural_mixed"] += int((structural_mask & daily_range_mask).sum())

    return {
        "policy": policy,
        "total_files": total_files,
        "bad_total": bad_total,
        "counts": counts,
    }


def _render_bad_data_population_assets(bucket_dir: Path) -> tuple[str, str, dict]:
    summary = _build_bad_data_population_summary()
    img_dir = bucket_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    policy = summary["policy"].copy()
    policy["pct"] = 100.0 * policy["files"] / summary["total_files"]
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    ax1.bar(policy["acceptance_label"], policy["files"], color=["#4c72b0", "#55a868", "#dd8452", "#c44e52", "#8172b2", "#937860", "#64b5cd"])
    ax1.set_title("Trades 57f | distribucion final de acceptance_label")
    ax1.set_ylabel("files")
    ax1.tick_params(axis="x", rotation=25)
    ax1.grid(axis="y", alpha=0.2)
    for i, (_, r) in enumerate(policy.iterrows()):
        ax1.text(i, r["files"], f"{int(r['files']):,}\n{r['pct']:.3f}%", ha="center", va="bottom", fontsize=9)
    img1 = img_dir / "00_trades_57f_acceptance_distribution.png"
    fig1.savefig(img1, dpi=140, bbox_inches="tight")
    plt.close(fig1)

    c = summary["counts"]
    labels = [
        "outside_daily_range",
        "scale_vw_nan",
        "outside_daily_100",
        "outside_1m_100",
        "size<=0",
        "dup_hard_cap",
        "structural_only",
        "structural_mixed",
    ]
    values = [
        c["trade_price_outside_daily_range"],
        c["scale_bucket_vw_nan"],
        c["outside_daily_100"],
        c["outside_1m_100"],
        c["negative_or_zero_size_rows"],
        c["duplicate_excess_ratio_gt_hard_cap"],
        c["structural_only"],
        c["structural_mixed"],
    ]
    fig2, ax2 = plt.subplots(figsize=(13, 5))
    ax2.bar(labels, values, color="#c44e52")
    ax2.set_title("bad_data 57f | firmas duras del universo")
    ax2.set_ylabel("files")
    ax2.tick_params(axis="x", rotation=25)
    ax2.grid(axis="y", alpha=0.2)
    for i, v in enumerate(values):
        ax2.text(i, v, f"{int(v):,}\n{(100.0*v/summary['bad_total']):.2f}%", ha="center", va="bottom", fontsize=9)
    img2 = img_dir / "01_bad_data_57f_failure_signatures.png"
    fig2.savefig(img2, dpi=140, bbox_inches="tight")
    plt.close(fig2)
    return f"./images/{img1.name}", f"./images/{img2.name}", summary


def _family_intro(bucket: str, n: int) -> str:
    responde, no_responde, consecuencia = _family_questions(bucket)
    lines = [
        f"# {FAMILY_TITLES.get(bucket, bucket)}",
        "",
        "## Rol",
        "",
        f"Este dossier documenta `{n}` casos de la muestra base del cierre real `57f/full_clean_fast_same_schema` para la familia `{bucket}`.",
        "",
        "No son ejemplos elegidos a dedo. Proceden del manifest estratificado reproducible materializado para el inspector.",
        "",
        "## Que significa esta familia",
        "",
        _family_description(bucket),
        "",
        "## Responde",
        "",
    ]
    lines.extend([f"- {x}" for x in responde] or ["- Pendiente de detalle especifico."])
    lines.extend(["", "## No responde", ""])
    lines.extend([f"- {x}" for x in no_responde] or ["- Pendiente de detalle especifico."])
    lines.extend(["", "## Consecuencia", ""])
    lines.extend([f"- {x}" for x in consecuencia] or ["- Pendiente de detalle especifico."])
    lines.extend(
        [
            "",
            "## Casos",
            "",
        ]
    )
    return "\n".join(lines)


def _bad_data_family_intro(bucket_dir: Path, n: int) -> str:
    img1, img2, summary = _render_bad_data_population_assets(bucket_dir)
    responde, no_responde, consecuencia = _family_questions("bad_data")
    policy = summary["policy"]
    total_files = summary["total_files"]
    bad_total = summary["bad_total"]
    c = summary["counts"]
    lines = [
        f"# {FAMILY_TITLES.get('bad_data', 'bad_data')}",
        "",
        "## Rol",
        "",
        f"Este dossier documenta `{n}` casos de la muestra estratificada de `bad_data`, pero arranca con un mapa general del universo `57f` para que el inspector no lea los casos aislados sin contexto.",
        "",
        "## Que significa esta familia",
        "",
        _family_description("bad_data"),
        "",
        "## Responde",
        "",
    ]
    lines.extend([f"- {x}" for x in responde])
    lines.extend(["", "## No responde", ""])
    lines.extend([f"- {x}" for x in no_responde])
    lines.extend(["", "## Consecuencia", ""])
    lines.extend([f"- {x}" for x in consecuencia])
    lines.extend(
        [
            "",
            "## Mapa general del universo",
            "",
            f"- `57f` contiene `{total_files:,}` files en total.",
            f"- `bad_data` contiene `{bad_total:,}` files (`{100.0 * bad_total / total_files:.3f}%` del universo).",
            "",
            f"![Distribucion final 57f]({img1})",
            "",
            "**Que muestra**",
            "",
            "- La distribucion final del universo completo por `acceptance_label` en el cierre real `57f`.",
            "- Permite ver que `bad_data` es una cola pequena del universo y no la masa dominante del bloque.",
            "",
            "**Responde**",
            "",
            "- Cuanta masa total hay en `trades` y donde cae `bad_data` dentro del universo completo.",
            "- Si el inspector esta viendo una patologia dominante del dataset o una cola dura acotada.",
            "",
            "**No responde**",
            "",
            "- No responde todavia a que tipo de `bad_data` domina internamente.",
            "- No responde a por que un caso individual concreto cae en rechazo duro.",
            "",
            "**Consecuencia**",
            "",
            "- Evita leer los casos de `bad_data` como si describieran el dataset entero.",
            "",
            "## Mapa general de firmas duras dentro de `bad_data`",
            "",
            f"![Firmas duras de bad_data]({img2})",
            "",
            "**Que muestra**",
            "",
            "- La composicion interna de `bad_data` en `57f` por firmas fuertes de fallo.",
            f"- `trade_price_outside_daily_range = {c['trade_price_outside_daily_range']:,}` (`{100.0 * c['trade_price_outside_daily_range'] / bad_total:.2f}%`).",
            f"- `scale_bucket_vw = nan = {c['scale_bucket_vw_nan']:,}` (`{100.0 * c['scale_bucket_vw_nan'] / bad_total:.2f}%`).",
            f"- `outside_daily_regular_pct = 100% = {c['outside_daily_100']:,}` (`{100.0 * c['outside_daily_100'] / bad_total:.2f}%`).",
            f"- `outside_1m_regular_pct = 100% = {c['outside_1m_100']:,}` (`{100.0 * c['outside_1m_100'] / bad_total:.2f}%`).",
            f"- `negative_or_zero_size_rows = {c['negative_or_zero_size_rows']:,}` (`{100.0 * c['negative_or_zero_size_rows'] / bad_total:.2f}%`).",
            f"- `duplicate_excess_ratio_gt_hard_cap = {c['duplicate_excess_ratio_gt_hard_cap']:,}` (`{100.0 * c['duplicate_excess_ratio_gt_hard_cap'] / bad_total:.2f}%`).",
            "",
            "**Responde**",
            "",
            "- Si `bad_data` esta dominado sobre todo por colapso de escala/rango o por integridad estructural del tape.",
            "- Que parte de la cola dura se ve bien con el panel de precio actual y que parte exige paneles complementarios.",
            "",
            "**No responde**",
            "",
            "- No responde a la causalidad exacta de cada file individual.",
            "- No responde a si todos los casos con una firma dura deben leerse exactamente igual.",
            "",
            "**Consecuencia**",
            "",
            "- Justifica que `bad_data` no se trate como una sola familia visual.",
            "- Justifica por que este dossier anade panel de integridad y tablas concretas de filas invalidas cuando aplica.",
            "",
            "## Casos",
            "",
        ]
    )
    return "\n".join(lines)


def _bad_data_case_blocks(row: pd.Series) -> tuple[list[str], list[str], list[str]]:
    subfamily = _case_visual_subfamily(row)
    outside_daily = float(row.get("outside_daily_regular_pct", float("nan")))
    outside_1m = float(row.get("outside_1m_regular_pct", float("nan")))
    duplicate = float(row.get("duplicate_exact_ratio_pct_raw", float("nan")))
    issues = [str(x) for x in (row.get("issues_list") if isinstance(row.get("issues_list"), list) else list(row.get("issues_list")) if getattr(row.get("issues_list"), "tolist", None) else [])]
    warns = [str(x) for x in (row.get("warns_list") if isinstance(row.get("warns_list"), list) else list(row.get("warns_list")) if getattr(row.get("warns_list"), "tolist", None) else [])]

    if subfamily == "colapso_escala_rango":
        responde = [
            "Este caso responde a si el file esta solo algo desalineado o si vive en una escala completamente incompatible con los arbitros.",
            "El error visual se ve en la separacion vertical extrema entre los arbitros y los prints raw, y en que el conflicto de rango es practicamente total.",
            f"Los porcentajes `outside daily = {_fmt_pct(outside_daily)}` y `outside 1m = {_fmt_pct(outside_1m)}` refuerzan una lectura de ruptura semantica, no de friccion fina.",
            "Aqui el panel actual si demuestra bien la causa del rechazo: es un `bad_data` de colapso de escala o de rango.",
        ]
        no_responde = [
            "No responde a si la duplicacion es la causa principal del rechazo; puede empeorar el caso, pero no explica por si sola la geometria rota.",
            "No responde a si existiria una reconciliacion de escala defendible; el colapso ya es demasiado extremo para tratarlo como simple normalizacion.",
        ]
        consecuencia = [
            "Excluir de ejecucion simulada, labels y benchmarking.",
            "Conservar solo valor forense o de deteccion de dano severo.",
        ]
        return responde, no_responde, consecuencia

    if subfamily == "integridad_estructural":
        responde = [
            "Este caso responde a una pregunta distinta: no si el precio esta grotescamente roto, sino si el tape sigue siendo un flujo de ejecucion valido.",
            "Visualmente, el panel de precio puede parecer casi normal; la causalidad principal vive en la integridad estructural del file y no en la nube de precios.",
            f"El `duplicate_exact_ratio_pct_raw = {_fmt_pct(duplicate)}` y los `issues_list` estructurales obligan a leer el caso como dano de tape, no como simple desacople economico.",
            "La clasificacion a `bad_data` no se apoya ya solo en intuicion: la pieza decisiva es el panel de integridad junto a la tabla de filas invalidas y grupos duplicados.",
        ]
        no_responde = [
            "No responde a si una sola fila invalida bastaria siempre para condenar cualquier file; la clasificacion depende del contexto estructural total.",
            "No responde a la rehabilitacion del caso; solo justifica por que hoy sigue en la cola dura.",
        ]
        consecuencia = [
            "Mantener el caso en `bad_data` por integridad estructural del tape.",
            "Usar el panel de integridad, la `X` roja y las tablas exactas como trio minimo de prueba para esta subfamilia.",
        ]
        return responde, no_responde, consecuencia

    if subfamily == "mixto_estructural_rango":
        responde = [
            "Este caso responde a si el rechazo nace de una sola capa o de dano mixto.",
            "La imagen protesta por rango o arbitro, pero ademas el file arrastra senales de integridad del tape; no puede leerse como simple conflicto visual.",
            "La clasificacion a `bad_data` se apoya en ambas capas de evidencia: geometria rota e integridad estructural.",
        ]
        no_responde = [
            "No responde a una unica causa limpia; obliga a aceptar que hay mezcla de fenomenos.",
            "No absuelve el file aunque una de las dos capas parezca mas suave que la otra.",
        ]
        consecuencia = [
            "Excluir el file y tratarlo como rechazo duro, no como caso de reconciliacion fina.",
            "Mantener el requisito de una segunda imagen de integridad cuando se presente al inspector.",
        ]
        return responde, no_responde, consecuencia

    if subfamily == "conflicto_ralo_o_sparse":
        responde = [
            "Este caso responde a si una muestra excesivamente rala puede dejar de ser defendible aunque no exista un colapso visual espectacular.",
            "La gravedad nace en parte de la escasez del tape y de que unas pocas filas ya rompen la compatibilidad con los arbitros.",
            "Aqui la lectura correcta exige combinar geometria del panel con `n_trades`, `rows_lt_10` y concentracion temporal del conflicto.",
        ]
        no_responde = [
            "No responde a un patron estable de tape; precisamente el problema es que el file no tiene suficiente densidad para defenderlo.",
            "No debe leerse como simple ruido puntual en un tape robusto.",
        ]
        consecuencia = [
            "Mantener el file fuera de ejecucion y labels productivos.",
            "Usarlo solo como evidencia de frontera metodologica o para forense.",
        ]
        return responde, no_responde, consecuencia

    responde = [
        "Este caso responde a si existe una franja local del rango o del arbitro intraminuto donde el file deja de ser economicamente reconciliable.",
        "La lectura correcta exige mirar el panel minuto a minuto, no solo la impresion global de la nube de precios.",
        f"Aunque `outside daily = {_fmt_pct(outside_daily)}` y `outside 1m = {_fmt_pct(outside_1m)}` no sean totales, el dano sigue siendo suficiente para sacar el file de uso productivo.",
    ]
    no_responde = [
        "No responde a colapso total de escala; ese seria otro subtipo.",
        "No responde por si solo a dano estructural del tape salvo que aparezca en `issues_list` o en el panel de integridad.",
    ]
    consecuencia = [
        "Excluir el file del flujo productivo aunque el dano no sea un colapso absoluto.",
        "Conservarlo como caso forense de rango local severo.",
    ]
    return responde, no_responde, consecuencia


def _case_section(row: pd.Series, rel_img: str) -> str:
    ticker = row.get("ticker", "")
    date_str = row.get("date")
    date_str = pd.to_datetime(date_str, errors="coerce")
    date_fmt = date_str.strftime("%Y-%m-%d") if pd.notna(date_str) else str(row.get("date", ""))
    n_trades = int(row.get("n_trades", row.get("rows_after_parse", 0)) or 0)
    outside_daily = float(row.get("outside_daily_regular_pct", float("nan")))
    outside_1m = float(row.get("outside_1m_regular_pct", float("nan")))
    diff = float(row.get("trade_vwap_vs_daily_vw_diff_pct_raw", float("nan")))
    dup = float(row.get("duplicate_exact_ratio_pct_raw", float("nan")))
    odd = float(row.get("odd_lot_trade_pct", float("nan")))
    bucket = str(row.get("acceptance_label", ""))
    reading_lines = []
    for line in _sample_case_reading(row).splitlines():
        cleaned = line.strip()
        if cleaned.startswith("- "):
            cleaned = cleaned[2:]
        if cleaned:
            reading_lines.append(f"- {cleaned}")
    no_responde_lines: list[str] = []
    consecuencia_lines: list[str] = []
    if bucket == "bad_data":
        _, no_responde, consecuencia = _bad_data_case_blocks(row)
        no_responde_lines = [f"- {x}" for x in no_responde]
        consecuencia_lines = [f"- {x}" for x in consecuencia]
    invalid_df = _invalid_rows_table(row) if bucket == "bad_data" else pd.DataFrame()
    dup_df = _duplicate_groups_table(row) if bucket == "bad_data" else pd.DataFrame()
    return "\n".join(
        [
            f"### {ticker} | {date_fmt}",
            "",
            f"![{ticker} {date_fmt}]({rel_img})",
            "",
            "**Que muestra**",
            "",
            f"- Panel rico del tape raw frente a `daily` y `1m` para `{ticker}` el `{date_fmt}`.",
            f"- `n_trades = {n_trades:,}`, `outside_daily_regular_pct = {outside_daily:.2f}%`, `outside_1m_regular_pct = {outside_1m:.2f}%`.",
            f"- `trade_vwap_vs_daily_vw_diff_pct_raw = {diff:.2f}%`, `duplicate_exact_ratio_pct_raw = {dup:.2f}%`, `odd_lot_trade_pct = {odd:.2f}%`.",
            "",
            "**Responde**",
            "",
            *reading_lines,
            "",
            *(["**No responde**", "", *no_responde_lines, ""] if no_responde_lines else []),
            *(["**Consecuencia**", "", *consecuencia_lines, ""] if consecuencia_lines else []),
            *(["**Filas invalidas exactas (`size <= 0`)**", "", *_md_table(invalid_df), ""] if not invalid_df.empty else []),
            *(["**Grupos duplicados exactos mas relevantes**", "", *_md_table(dup_df), ""] if not dup_df.empty else []),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", default="", help="Familia unica a exportar; vacio = todas")
    parser.add_argument("--rewrite", action="store_true", help="Reescribe el dossier y vuelve a exportar las imagenes de la familia")
    args = parser.parse_args()

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_paths = sorted(MANIFEST_DIR.glob("*_manifest.parquet"))
    if not manifest_paths:
        raise FileNotFoundError(f"No manifests found in {MANIFEST_DIR}")

    index_rows = []
    for manifest_path in manifest_paths:
        bucket = manifest_path.stem.replace("_manifest", "")
        if args.bucket and bucket != args.bucket:
            continue
        df = pd.read_parquet(manifest_path)
        bucket_dir = OUT_ROOT / bucket
        img_dir = bucket_dir / "images"
        bucket_dir.mkdir(parents=True, exist_ok=True)
        img_dir.mkdir(parents=True, exist_ok=True)

        md_path = bucket_dir / f"{bucket}_cases_v0_1.md"
        intro = _bad_data_family_intro(bucket_dir, len(df)) if bucket == "bad_data" else _family_intro(bucket, len(df))
        if args.rewrite:
            for old_img in img_dir.glob("*.png"):
                old_img.unlink()
            md_path.write_text(intro + "\n", encoding="utf-8")
        elif not md_path.exists() or md_path.read_text(encoding="utf-8").strip() == "":
            md_path.write_text(intro + "\n", encoding="utf-8")
        exported = 0
        for _, row in df.iterrows():
            case_row = row.copy()
            case_row["date_str"] = pd.to_datetime(case_row["date"], errors="coerce").strftime("%Y-%m-%d") if pd.notna(pd.to_datetime(case_row["date"], errors="coerce")) else str(case_row["date"])
            name = _slug(f"{case_row.get('ticker','')}_{case_row.get('date_str','')}")
            img_path = img_dir / f"{name}.png"
            rel_img = f"./images/{img_path.name}"
            section_header = f"### {case_row.get('ticker','')} | {case_row.get('date_str','')}"
            current_md = md_path.read_text(encoding="utf-8")
            already_documented = section_header in current_md
            if not img_path.exists():
                fig, trades, ref_1m, daily_row = _build_sample_case_figure(case_row)
                if fig is None:
                    continue
                fig.savefig(img_path, dpi=140, bbox_inches="tight")
                plt.close(fig)
            if not already_documented:
                section = _case_section(case_row, rel_img)
                with md_path.open("a", encoding="utf-8") as fh:
                    fh.write("\n" + section + "\n")
            rel_img = f"./images/{img_path.name}"
            exported += 1

        index_rows.append(
            {
                "bucket": bucket,
                "manifest_rows": len(df),
                "exported_images": exported,
                "md_path": str(md_path),
            }
        )

    index_df = pd.DataFrame(index_rows).sort_values("bucket")
    index_df.to_csv(OUT_ROOT / "family_casepacks_index.csv", index=False)

    lines = [
        "# Trades Family Casepacks Index v0.1",
        "",
        "## Rol",
        "",
        "Este indice resume los casepacks amplios generados a partir de la muestra estratificada canonica de `trades`.",
        "",
        "| familia | rows manifest | imagenes exportadas | dossier |",
        "|---|---:|---:|---|",
    ]
    for _, r in index_df.iterrows():
        rel = Path(r["md_path"]).relative_to(OUT_ROOT)
        lines.append(f"| `{r['bucket']}` | {int(r['manifest_rows'])} | {int(r['exported_images'])} | [{rel.as_posix()}](./{rel.as_posix()}) |")
    (OUT_ROOT / "family_casepacks_index_v0_1.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
