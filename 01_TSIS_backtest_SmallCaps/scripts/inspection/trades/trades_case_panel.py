from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import ipywidgets as widgets
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Image, Markdown, clear_output, display


TRADES_HISTORICAL_ASSETS_DIR = Path(
    r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\trades\evidence_assets\historical_assets"
)
TRADES_FILE_ACCEPTANCE_CACHE_DIR = Path(
    r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b"
)


@dataclass(frozen=True)
class TradesCaseEntry:
    layer: str
    bucket: str
    case_id: str
    title: str
    image_name: str
    what_it_shows: str
    why_it_matters: str
    pipeline_impact: str
    caution: str


CASE_CATALOG: list[TradesCaseEntry] = [
    TradesCaseEntry(
        layer="population",
        bucket="acceptance_label_state",
        case_id="00_current_policy_distribution",
        title="Current shard policy distribution",
        image_name="00_current_policy_distribution_from_raw_shards.png",
        what_it_shows=(
            "Distribucion agregada de `acceptance_label` en el estado historico `full_clean` parcial. "
            "Sirve para ver que la masa no esta dominada por `bad_data`, sino por `review`, "
            "`reference_scale_mismatch` y `review_microstructure`."
        ),
        why_it_matters=(
            "Evita la lectura ingenua de que casi todo `review` equivale a tape roto. "
            "La consecuencia institucional es que `trades` necesita estados finales mas ricos que un simple `good/bad`."
        ),
        pipeline_impact=(
            "Afecta a governance, triage metodologico y a como se define `recoverable_with_flag` "
            "para backtest extendido y ML informado."
        ),
        caution=(
            "No expresa estados finales de certificacion. Expresa labels tecnicos de una capa historica parcial."
        ),
    ),
    TradesCaseEntry(
        layer="population",
        bucket="d_full_final_bucket",
        case_id="11_d_full_final_bucket_distribution",
        title="D full final bucket distribution",
        image_name="11_d_full_final_bucket_distribution.png",
        what_it_shows=(
            "Reparto del residuo `D full` por buckets finales viejos. "
            "Demuestra que el residuo duro existe, pero tampoco es homogeneo."
        ),
        why_it_matters=(
            "Permite separar ruptura confirmada por `1m`, duplicacion severa y sospecha pura de escala. "
            "Evita llamar `bad` a todo el residuo duro por costumbre."
        ),
        pipeline_impact=(
            "Afecta a decisiones de muestreo forense, a la priorizacion de rematerializaciones "
            "y a la politica de recuperacion de buckets."
        ),
        caution=(
            "No debe usarse solo como politica certificadora final; necesita reinterpretacion por `file_acceptance`."
        ),
    ),
    TradesCaseEntry(
        layer="population",
        bucket="scale_contamination",
        case_id="12_d_full_scale_contamination",
        title="Scale contamination by bucket",
        image_name="12_d_full_scale_contamination_by_bucket.png",
        what_it_shows=(
            "Cruce entre buckets residuales y firmas de escala (`near 1x`, `far from 1x`, `extreme scale`, `VWAP diff >= 20%`)."
        ),
        why_it_matters=(
            "Prueba que la escala no es ruido cosmetico. Es una firma estructural que cambia por bucket y obliga "
            "a separar `reference_scale_mismatch` de `bad_data` puro."
        ),
        pipeline_impact=(
            "Afecta a reconciliacion externa, a vistas `split_normalized/adjusted_proxy` "
            "y a cualquier uso de `trades_raw` contra arbitros diarios o `1m`."
        ),
        caution=(
            "Una barra alta en `extreme scale` no prueba por si sola corrupcion del tape; prueba conflicto de comparabilidad."
        ),
    ),
    TradesCaseEntry(
        layer="case_pack",
        bucket="reference_scale_mismatch",
        case_id="01_sga_2009_01_05",
        title="Reference scale mismatch | SGA 2009-01-05",
        image_name="01_reference_scale_mismatch_sga_2009_01_05.png",
        what_it_shows=(
            "Caso representativo donde `trades` y los arbitros viven en escalas distintas. "
            "La forma del tape puede ser internamente coherente aunque choque violentamente con `daily` o `1m`."
        ),
        why_it_matters=(
            "Demuestra que no todo conflicto severo contra referencia es `bad_data`. "
            "Aqui la decision correcta es mantener el caso en `review` mientras no exista reconciliacion de escala validada."
        ),
        pipeline_impact=(
            "Afecta sobre todo a reconciliacion, QA y feature engineering si alguien mezcla `trades_raw` con precios ya normalizados."
        ),
        caution=(
            "No debe promoverse a `good`; pero tampoco debe confundirse automaticamente con tape roto."
        ),
    ),
    TradesCaseEntry(
        layer="case_pack",
        bucket="reference_scale_mismatch",
        case_id="02_lpcn_2014_07_07",
        title="Reference scale mismatch | LPCN 2014-07-07",
        image_name="02_reference_scale_mismatch_lpcn_2014_07_07.png",
        what_it_shows=(
            "Segundo ejemplo de conflicto de escala donde la ruptura principal vive frente al arbitro, no necesariamente dentro del propio flujo de prints."
        ),
        why_it_matters=(
            "Refuerza que `reference_scale_mismatch` es una familia estable y no un ticker raro aislado."
        ),
        pipeline_impact=(
            "Importa para cualquier pipeline que quiera reconciliar `trades`, `daily` y `1m` sin declarar la semantica de precio."
        ),
        caution=(
            "Si se consume sin flags, contamina labels y comparaciones externas."
        ),
    ),
    TradesCaseEntry(
        layer="case_pack",
        bucket="review_microstructure",
        case_id="03_qrteb_2019_07_24",
        title="Review microstructure | QRTEB 2019-07-24",
        image_name="03_review_microstructure_qrteb_2019_07_24.png",
        what_it_shows=(
            "Caso donde el conflicto se concentra en la textura microestructural del tape: odd-lots, dispersion fina o estructura de ejecucion."
        ),
        why_it_matters=(
            "Prueba que hay una masa donde el problema no es corrupcion bruta, sino compatibilidad imperfecta con el arbitro al mirar el tape fino."
        ),
        pipeline_impact=(
            "Afecta a microstructure ML, simulacion de ejecucion y a cualquier uso que dependa del tape fino mas que del retorno diario."
        ),
        caution=(
            "No es `good`, pero puede ser `recoverable_with_flag` segun uso y regla final."
        ),
    ),
    TradesCaseEntry(
        layer="case_pack",
        bucket="review_microstructure",
        case_id="04_czfs_2022_08_11",
        title="Review microstructure | CZFS 2022-08-11",
        image_name="04_review_microstructure_czfs_2022_08_11.png",
        what_it_shows=(
            "Otro ejemplo de conflicto dominado por microestructura y comparabilidad fina."
        ),
        why_it_matters=(
            "Evita tratar toda divergencia como error de escala o `bad_data`; prueba que existe una familia intermedia metodologicamente distinta."
        ),
        pipeline_impact=(
            "Especialmente relevante para ejecucion, odd-lot handling y filtros de tape limpio."
        ),
        caution=(
            "No debe reciclarse como verdad economica diaria sin flags."
        ),
    ),
    TradesCaseEntry(
        layer="case_pack",
        bucket="review_1m_reference_alignment",
        case_id="05_relv_2018_06_07",
        title="Review 1m reference alignment | RELV 2018-06-07",
        image_name="05_review_1m_reference_alignment_relv_2018_06_07.png",
        what_it_shows=(
            "Caso donde `daily` y `VWAP` pueden parecer alineados, pero la comparacion contra `1m` revela el conflicto central."
        ),
        why_it_matters=(
            "Prueba que `1m` no es decorativo; cambia la clasificacion del caso. "
            "Evita promover a `good` algo que solo parece limpio desde un arbitro demasiado grueso."
        ),
        pipeline_impact=(
            "Importa para reconciliacion y para backtests que pretendan apoyarse en consistencia intradia."
        ),
        caution=(
            "El hecho de que `daily` no proteste no basta para absolver el caso."
        ),
    ),
    TradesCaseEntry(
        layer="case_pack",
        bucket="review_1m_reference_alignment",
        case_id="06_metc_2021_03_22",
        title="Review 1m reference alignment | METC 2021-03-22",
        image_name="06_review_1m_reference_alignment_metc_2021_03_22.png",
        what_it_shows=(
            "Segundo ejemplo donde el arbitro `1m` rompe una aparente normalidad a resolucion mas gruesa."
        ),
        why_it_matters=(
            "Confirma que este bucket no es anecdotico y que la resolucion del arbitro cambia la verdad del caso."
        ),
        pipeline_impact=(
            "Afecta a QA de agregaciones intradia y a la confianza en labels derivados de vistas mas agregadas."
        ),
        caution=(
            "No mezclar con `review_no_1m_reference`; aqui el problema existe precisamente porque `1m` si esta presente."
        ),
    ),
    TradesCaseEntry(
        layer="case_pack",
        bucket="bad_data",
        case_id="07_bwl_a_2009_03_26",
        title="Bad data | BWL.A 2009-03-26",
        image_name="07_bad_data_bwl_a_2009_03_26.png",
        what_it_shows=(
            "Caso de dano duro donde el tape deja de ser economicamente defendible frente a cualquier arbitro razonable."
        ),
        why_it_matters=(
            "Marca la frontera semantica real del bloque: aqui ya no hablamos de comparabilidad fina, sino de flujo de trades inaceptable."
        ),
        pipeline_impact=(
            "Inhabilita ejecucion simulada, backtest, labels y reconciliacion salvo uso puramente forense."
        ),
        caution=(
            "No debe rehabilitarse por analogia con otros buckets `review`."
        ),
    ),
    TradesCaseEntry(
        layer="case_pack",
        bucket="bad_data",
        case_id="08_anda_2012_05_10",
        title="Bad data | ANDA 2012-05-10",
        image_name="08_bad_data_anda_2012_05_10.png",
        what_it_shows=(
            "Segundo ejemplo duro de `bad_data`, util para separar la cola realmente rota del resto del residuo."
        ),
        why_it_matters=(
            "Refuerza que `bad_data` existe como cola pequena pero real, y no debe diluirse por el hecho de que la masa dominante este en `review`."
        ),
        pipeline_impact=(
            "Solo conserva valor para control de calidad, stress forense o tareas de etiquetado de dano severo."
        ),
        caution=(
            "No usar para aprendizaje de comportamiento normal del tape."
        ),
    ),
    TradesCaseEntry(
        layer="case_pack",
        bucket="review_no_1m_reference",
        case_id="09_glbl_2024_09_19",
        title="Review no 1m reference | GLBL 2024-09-19",
        image_name="09_review_no_1m_reference_glbl_2024_09_19.png",
        what_it_shows=(
            "Caso donde hay conflicto con referencias mas gruesas pero falta el arbitro `1m` para cerrar la disputa con mas precision."
        ),
        why_it_matters=(
            "Demuestra que ausencia de `1m` no equivale ni a absolucion ni a condena total. "
            "Obliga a mantener estado intermedio disciplinado."
        ),
        pipeline_impact=(
            "Afecta a politicas de recuperacion con flag, especialmente en research extendido y analisis forense."
        ),
        caution=(
            "No mezclar con `bad_data`; aqui la incertidumbre de arbitro es parte del problema."
        ),
    ),
    TradesCaseEntry(
        layer="case_pack",
        bucket="review_generic",
        case_id="10_tof_2010_06_21",
        title="Generic review | TOF 2010-06-21",
        image_name="10_review_tof_2010_06_21.png",
        what_it_shows=(
            "Caso residual donde el conflicto existe, pero no encaja limpiamente en un bucket mas especifico ya rehabilitado."
        ),
        why_it_matters=(
            "Recuerda que `review` no es una caja vacia: es el residuo que todavia no debe inflarse a `good` ni degradarse sin mas a `bad`."
        ),
        pipeline_impact=(
            "Afecta al calculo de masa realmente recuperable y a la necesidad de rematerializar la regla de rehabilitacion sobre `57f`."
        ),
        caution=(
            "La lectura de este bucket no debe cerrarse sin recalcular la rehabilitacion final sobre el cache completo."
        ),
    ),
    TradesCaseEntry(
        layer="case_pack",
        bucket="good",
        case_id="13_dmys_2022_09_06",
        title="Good tail | DMYS 2022-09-06",
        image_name="13_good_dmys_2022_09_06.png",
        what_it_shows=(
            "Ejemplo de la cola `good` donde `trades`, `daily` y `1m` alinean limpiamente."
        ),
        why_it_matters=(
            "Prueba que `good` existe como firma real del tape limpio. "
            "Tambien demuestra por contraste lo exigente que es la entrada a este bucket."
        ),
        pipeline_impact=(
            "Sirve como patron de referencia para QA y para calibrar que significa un file pristine."
        ),
        caution=(
            "No sobrerrepresentarlo: la propia certificacion historica lo declara minusculo y sesgado a files muy pequenos."
        ),
    ),
    TradesCaseEntry(
        layer="case_pack",
        bucket="good",
        case_id="14_clsn_2016_05_16",
        title="Good tail | CLSN 2016-05-16",
        image_name="14_good_clsn_2016_05_16.png",
        what_it_shows=(
            "Segundo ejemplo `good` para fijar visualmente como luce una alineacion casi impecable."
        ),
        why_it_matters=(
            "Refuerza que el bucket no es imaginario, pero sigue sin medir por si mismo la masa util del bloque."
        ),
        pipeline_impact=(
            "Util para comparacion didactica contra buckets recuperables y contra `bad_data`."
        ),
        caution=(
            "No usar su rareza para concluir que todo lo no-`good` es inservible."
        ),
    ),
]

_SAMPLE_POLICY_CACHE: pd.DataFrame | None = None
_SAMPLE_INDEX_CACHE: pd.DataFrame | None = None


def _safe_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if pd.isna(value):
        return []
    return [value]


def _has_token(value, token: str) -> bool:
    return token in [str(x) for x in _safe_list(value)]


def _fmt_pct(value) -> str:
    try:
        x = float(value)
    except Exception:
        return "nan%"
    if not np.isfinite(x):
        return "nan%"
    return f"{x:.2f}%"


def _fmt_num(value) -> str:
    try:
        x = float(value)
    except Exception:
        return "nan"
    if not np.isfinite(x):
        return "nan"
    return f"{x:.2f}"


def _case_visual_subfamily(case_row: pd.Series) -> str:
    bucket = str(case_row.get("acceptance_label", ""))
    if bucket != "bad_data":
        return "generic"
    issues = _safe_list(case_row.get("issues_list"))
    warns = _safe_list(case_row.get("warns_list"))
    scale_vw = str(case_row.get("scale_bucket_vw", ""))
    outside_daily = pd.to_numeric(case_row.get("outside_daily_regular_pct", np.nan), errors="coerce")
    outside_1m = pd.to_numeric(case_row.get("outside_1m_regular_pct", np.nan), errors="coerce")
    n_trades = int(case_row.get("n_trades", case_row.get("rows_after_parse", 0)) or 0)

    structural = any(
        tok in [str(x) for x in issues]
        for tok in ["negative_or_zero_size_rows", "duplicate_excess_ratio_gt_hard_cap"]
    )
    daily_range = _has_token(issues, "trade_price_outside_daily_range")
    sparse = _has_token(warns, "rows_lt_10") or n_trades < 10
    collapse = (
        scale_vw == "nan"
        or (np.isfinite(outside_daily) and outside_daily >= 100.0)
        or (np.isfinite(outside_1m) and outside_1m >= 100.0)
    )

    if structural and not daily_range and not collapse:
        return "integridad_estructural"
    if structural and (daily_range or collapse):
        return "mixto_estructural_rango"
    if collapse and daily_range:
        return "colapso_escala_rango"
    if sparse:
        return "conflicto_ralo_o_sparse"
    return "conflicto_rango_local"


def _case_visual_subfamily_explanation(subfamily: str) -> str:
    mapping = {
        "integridad_estructural": (
            "Subfamilia donde el motivo principal del rechazo no vive en la trayectoria del precio, "
            "sino en la integridad del tape: sizes no validos, duplicacion dura o estructura interna corrupta."
        ),
        "mixto_estructural_rango": (
            "Subfamilia mixta donde hay conflicto visual de rango, pero tambien senales de integridad del tape. "
            "El rechazo no debe apoyarse en una sola capa de evidencia."
        ),
        "colapso_escala_rango": (
            "Subfamilia donde el panel de precio ya demuestra por si mismo una ruptura semantica: tape y arbitros viven "
            "en escalas incompatibles o el porcentaje fuera de rango es practicamente total."
        ),
        "conflicto_ralo_o_sparse": (
            "Subfamilia donde el conflicto se apoya en muy pocas filas o en una muestra excesivamente rala. "
            "La gravedad no nace solo de la geometria del precio, sino de la imposibilidad de defender el file como tape estable."
        ),
        "conflicto_rango_local": (
            "Subfamilia donde el conflicto vive en un subconjunto relevante del rango o del arbitro intraminuto, "
            "aunque no haya colapso total de escala."
        ),
    }
    return mapping.get(subfamily, "Subfamilia sin descripcion especifica.")


def _load_sample_policy_examples() -> pd.DataFrame:
    global _SAMPLE_POLICY_CACHE
    if _SAMPLE_POLICY_CACHE is None:
        path = TRADES_FILE_ACCEPTANCE_CACHE_DIR / "layer6_policy_examples.parquet"
        _SAMPLE_POLICY_CACHE = pd.read_parquet(path) if path.exists() else pd.DataFrame()
    return _SAMPLE_POLICY_CACHE.copy()


def _load_sample_index() -> pd.DataFrame:
    global _SAMPLE_INDEX_CACHE
    if _SAMPLE_INDEX_CACHE is None:
        path = TRADES_FILE_ACCEPTANCE_CACHE_DIR / "sample_index.parquet"
        _SAMPLE_INDEX_CACHE = pd.read_parquet(path) if path.exists() else pd.DataFrame()
    return _SAMPLE_INDEX_CACHE.copy()


def _grouped_options(values: list[str]) -> list[tuple[str, str]]:
    return [(value, value) for value in values]


def _entries_for_layer(layer: str) -> list[TradesCaseEntry]:
    return [entry for entry in CASE_CATALOG if entry.layer == layer]


def _entries_for_bucket(layer: str, bucket: str) -> list[TradesCaseEntry]:
    return [entry for entry in CASE_CATALOG if entry.layer == layer and entry.bucket == bucket]


def _sample_policy_bucket_values() -> list[str]:
    df = _load_sample_policy_examples()
    if df.empty or "acceptance_label" not in df.columns:
        return []
    return sorted(df["acceptance_label"].dropna().astype(str).unique().tolist())


def _sample_policy_cases(bucket: str) -> pd.DataFrame:
    df = _load_sample_policy_examples()
    if df.empty:
        return df
    x = df.loc[df["acceptance_label"].astype(str) == str(bucket)].copy()
    sample_index = _load_sample_index()
    if not sample_index.empty:
        merge_cols = [
            "file",
            "issues_list",
            "warns_list",
            "m.ohlcv_1m_path",
            "m.ohlcv_daily_path",
            "m.l",
            "m.h",
            "m.vw",
            "m.price_min",
            "m.price_max",
            "m.trade_vwap",
        ]
        keep = [c for c in merge_cols if c in sample_index.columns]
        x = x.merge(sample_index[keep], on="file", how="left")
    if "ticker" in x.columns:
        x["ticker"] = x["ticker"].astype(str)
    if "date" in x.columns:
        x["date"] = pd.to_datetime(x["date"], errors="coerce")
        x["date_str"] = x["date"].dt.strftime("%Y-%m-%d")
    else:
        x["date_str"] = ""
    if "outside_1m_regular_pct" in x.columns:
        x["outside_1m_regular_pct"] = pd.to_numeric(x["outside_1m_regular_pct"], errors="coerce")
    if "trade_vwap_vs_daily_vw_diff_pct_raw" in x.columns:
        x["trade_vwap_vs_daily_vw_diff_pct_raw"] = pd.to_numeric(
            x["trade_vwap_vs_daily_vw_diff_pct_raw"], errors="coerce"
        )
    x["case_label"] = (
        x["ticker"].fillna("").astype(str)
        + " | "
        + x["date_str"].fillna("").astype(str)
        + " | outside_1m="
        + x["outside_1m_regular_pct"].round(2).astype(str)
        + "%"
    )
    return x.reset_index(drop=True)


def _sample_policy_row(bucket: str, row_idx: int) -> pd.Series:
    df = _sample_policy_cases(bucket)
    if df.empty:
        raise IndexError("No sample policy cases available")
    return df.iloc[int(row_idx)]


def _sample_file_preview(case_row: pd.Series, n_rows: int = 12) -> pd.DataFrame:
    file_path = Path(str(case_row.get("file", "")))
    if not file_path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(file_path).head(n_rows)
    except Exception:
        return pd.DataFrame()


def _to_ny(ts: pd.Series) -> pd.Series:
    x = pd.to_datetime(ts, errors="coerce", utc=True)
    return x.dt.tz_convert("America/New_York").dt.tz_localize(None)


def _load_trade_case_df(case_row: pd.Series) -> pd.DataFrame:
    file_path = Path(str(case_row.get("file", "")))
    if not file_path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_parquet(file_path)
    except Exception:
        return pd.DataFrame()
    if "timestamp" in df.columns:
        df["ts_ny"] = _to_ny(df["timestamp"])
        df["minute_ny"] = df["ts_ny"].dt.floor("min")
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    if "size" in df.columns:
        df["size"] = pd.to_numeric(df["size"], errors="coerce")
    return df


def _load_daily_ref_row(case_row: pd.Series) -> pd.Series | None:
    p = Path(str(case_row.get("m.ohlcv_daily_path", "")))
    if not p.exists():
        return None
    try:
        df = pd.read_parquet(p)
    except Exception:
        return None
    x = df.loc[df["date"].astype(str) == str(case_row.get("date_str", ""))]
    if x.empty:
        return None
    return x.iloc[0]


def _load_1m_ref_df(case_row: pd.Series) -> pd.DataFrame:
    p = Path(str(case_row.get("m.ohlcv_1m_path", "")))
    if not p.exists():
        return pd.DataFrame()
    try:
        df = pd.read_parquet(p)
    except Exception:
        return pd.DataFrame()
    x = df.loc[df["date"].astype(str) == str(case_row.get("date_str", ""))].copy()
    if x.empty:
        return x
    x["ts_ny"] = _to_ny(x["ts_utc"])
    x["minute_ny"] = x["ts_ny"].dt.floor("min")
    for c in ["o", "h", "l", "c", "vw", "v"]:
        if c in x.columns:
            x[c] = pd.to_numeric(x[c], errors="coerce")
    return x


def _family_description(bucket: str) -> str:
    mapping = {
        "reference_scale_mismatch": (
            "Familia donde el conflicto dominante no es que el tape este roto por dentro, "
            "sino que el tape y el arbitro viven en escalas distintas. Responde a la pregunta "
            "de si el dano principal es de comparabilidad frente a `daily` o `1m`."
        ),
        "review_microstructure": (
            "Familia donde el dano vive en la textura fina del flujo: odd-lots, duplicados, "
            "bursts por timestamp o comparabilidad intraminuto. Responde a la pregunta de si "
            "el tape es economicamente interpretable pero metodologicamente delicado."
        ),
        "review_no_1m_reference": (
            "Familia donde existe conflicto, pero falta el arbitro `1m`. Responde a la pregunta "
            "de si el caso debe quedarse en incertidumbre disciplinada y no ser absuelto ni condenado por reflejo."
        ),
        "review_1m_reference_alignment": (
            "Familia donde `1m` cambia la verdad del caso. Responde a la pregunta de si una vista "
            "mas fina destruye una aparente normalidad vista desde `daily`."
        ),
        "review": (
            "Residuo de revision no absorbido por una subfamilia mas especifica. Responde a la pregunta "
            "de si todavia hace falta una regla de rehabilitacion antes de consumir esta masa."
        ),
        "bad_data": (
            "Frontera semantica donde el flujo deja de ser defendible como tape de ejecucion. "
            "Responde a la pregunta de si el file conserva valor economico o solo valor forense."
        ),
        "good": (
            "Cola pristine donde `trades`, `daily` y `1m` alinean con limpieza. Responde a la pregunta "
            "de como luce una firma casi impecable del tape."
        ),
    }
    return mapping.get(bucket, "Familia sin descripcion especifica todavia.")


def _family_questions(bucket: str) -> tuple[list[str], list[str], list[str]]:
    mapping = {
        "reference_scale_mismatch": (
            [
                "si el conflicto dominante vive en la escala frente a los arbitros",
                "si el caso exige reconciliacion antes de cualquier juicio economico serio",
            ],
            [
                "si el tape quedaria limpio tras reconciliacion estable",
                "si debe promoverse ya a `recoverable_with_flag`",
            ],
            [
                "mantener prudencia institucional y no mezclarlo con `bad_data`",
                "priorizar reconciliacion semantica antes que exclusion automatica",
            ],
        ),
        "review_microstructure": (
            [
                "si el dano dominante vive en odd-lots, duplicados o textura fina del tape",
                "si el flujo sigue siendo interpretable con flag segun uso",
            ],
            [
                "si el caso es valido como referencia economica limpia",
                "si basta una normalizacion de escala para resolverlo",
            ],
            [
                "permitir usos microestructurales con flag",
                "impedir consumo ingenuo como tape pristine",
            ],
        ),
        "review_no_1m_reference": (
            [
                "si el conflicto existe aunque falte el arbitro fino `1m`",
                "si el caso debe quedarse en incertidumbre disciplinada",
            ],
            [
                "si el tape es limpio por ausencia de arbitro",
                "si debe condenarse como `bad_data` sin mas evidencia",
            ],
            [
                "mantener estado intermedio y flags de referencia incompleta",
                "evitar absolucion o condena por reflejo",
            ],
        ),
        "review_1m_reference_alignment": (
            [
                "si el arbitro `1m` cambia la verdad del caso",
                "si una aparente normalidad diaria es ilusion de agregacion",
            ],
            [
                "si el caso habria sido bueno sin arbitro fino",
                "si el problema es puramente de escala",
            ],
            [
                "proteger reconciliacion y labels intradia de falsas rehabilitaciones",
                "preservar el papel decisivo de `1m`",
            ],
        ),
        "review": (
            [
                "si el residuo generico sigue necesitando regla de rehabilitacion",
                "si la masa abierta es comparable o economicamente util con flag",
            ],
            [
                "si todo `review` es homogeneamente recuperable",
                "si el bucket esta vacio de estructura interna",
            ],
            [
                "anclar decisiones en regla explicita y no en intuicion",
                "cuantificar masa util real antes de cualquier promocion",
            ],
        ),
        "bad_data": (
            [
                "si el tape ya cruza la frontera donde deja de ser defendible economicamente",
                "si el dano es intrinseco y no simple conflicto de comparabilidad",
            ],
            [
                "si todo outside severo es automaticamente `bad_data`",
                "si el dataset completo esta muerto por tener una cola `bad`",
            ],
            [
                "excluir de ejecucion, benchmarking y labels productivos",
                "conservar solo valor forense o de deteccion de dano",
            ],
        ),
        "good": (
            [
                "como luce una firma realmente limpia del tape",
                "que patron sirve como referencia de alineacion casi impecable",
            ],
            [
                "cuanta masa util tiene todo el bloque",
                "si todo lo no-good es inservible",
            ],
            [
                "fijar el patron pristine sin sobrerrepresentarlo",
                "evitar leer `good` como proxy de utilidad total",
            ],
        ),
    }
    return mapping.get(bucket, ([], [], []))


def _build_sample_case_figure(case_row: pd.Series) -> tuple[plt.Figure | None, pd.DataFrame, pd.DataFrame, pd.Series | None]:
    trades = _load_trade_case_df(case_row)
    daily_row = _load_daily_ref_row(case_row)
    ref_1m = _load_1m_ref_df(case_row)

    if trades.empty:
        return None, trades, ref_1m, daily_row

    if not ref_1m.empty:
        ref_keep = [c for c in ["minute_ny", "l", "h", "vw"] if c in ref_1m.columns]
        trades = trades.merge(ref_1m[ref_keep], on="minute_ny", how="left", suffixes=("", "_1m"))
    else:
        trades["l"] = np.nan
        trades["h"] = np.nan
        trades["vw"] = np.nan

    daily_low = float(daily_row["l"]) if daily_row is not None and "l" in daily_row.index else np.nan
    daily_high = float(daily_row["h"]) if daily_row is not None and "h" in daily_row.index else np.nan
    daily_vw = float(daily_row["vw"]) if daily_row is not None and "vw" in daily_row.index else np.nan

    trades["outside_daily"] = False
    if np.isfinite(daily_low) and np.isfinite(daily_high):
        trades["outside_daily"] = (trades["price"] < daily_low) | (trades["price"] > daily_high)
    trades["outside_1m"] = False
    if "l" in trades.columns and "h" in trades.columns:
        valid_1m = trades["l"].notna() & trades["h"].notna()
        trades.loc[valid_1m, "outside_1m"] = (
            (trades.loc[valid_1m, "price"] < trades.loc[valid_1m, "l"])
            | (trades.loc[valid_1m, "price"] > trades.loc[valid_1m, "h"])
        )
    trades["invalid_non_positive_size"] = False
    if "size" in trades.columns:
        size_numeric = pd.to_numeric(trades["size"], errors="coerce")
        trades["invalid_non_positive_size"] = size_numeric.le(0).fillna(False)

    minute_stats = (
        trades.groupby("minute_ny", dropna=True)
        .agg(
            trades_n=("price", "size"),
            volume=("size", "sum"),
            outside_daily_n=("outside_daily", "sum"),
            outside_1m_n=("outside_1m", "sum"),
        )
        .reset_index()
    )
    minute_stats["outside_daily_pct"] = 100.0 * minute_stats["outside_daily_n"] / minute_stats["trades_n"].clip(lower=1)
    minute_stats["outside_1m_pct"] = 100.0 * minute_stats["outside_1m_n"] / minute_stats["trades_n"].clip(lower=1)

    # Integrity diagnostics for cases where price geometry is not the only story.
    non_positive_size = int((trades["size"] <= 0).fillna(False).sum()) if "size" in trades.columns else 0
    missing_size = int(trades["size"].isna().sum()) if "size" in trades.columns else 0
    missing_price = int(trades["price"].isna().sum()) if "price" in trades.columns else 0
    dup_mask = trades.duplicated(subset=[c for c in ["ts_ny", "price", "size"] if c in trades.columns], keep=False)
    duplicate_rows = int(dup_mask.sum()) if len(trades) else 0

    fig, axes = plt.subplots(
        4,
        1,
        figsize=(15, 15),
        gridspec_kw={"height_ratios": [2.3, 1.2, 1.0, 1.1]},
        constrained_layout=True,
    )
    ax0, ax1, ax2, ax3 = axes

    if not ref_1m.empty:
        ax0.fill_between(ref_1m["ts_ny"], ref_1m["l"], ref_1m["h"], color="#9ecae1", alpha=0.25, label="rango 1m")
        ax0.plot(ref_1m["ts_ny"], ref_1m["vw"], color="#1f77b4", linewidth=1.1, label="vw 1m")
    ax0.scatter(trades["ts_ny"], trades["price"], s=8, color="#7f7f7f", alpha=0.55, label="prints raw")
    if trades["outside_daily"].any():
        t = trades.loc[trades["outside_daily"]]
        ax0.scatter(t["ts_ny"], t["price"], s=22, color="#d62728", alpha=0.9, label="fuera de daily")
    if trades["outside_1m"].any():
        t = trades.loc[trades["outside_1m"]]
        ax0.scatter(t["ts_ny"], t["price"], s=18, color="#ff7f0e", alpha=0.85, label="fuera de 1m")
    if trades["invalid_non_positive_size"].any():
        t = trades.loc[trades["invalid_non_positive_size"]]
        ax0.scatter(
            t["ts_ny"],
            t["price"],
            s=90,
            marker="x",
            linewidths=2.0,
            color="#b30000",
            alpha=0.95,
            label="size<=0",
            zorder=6,
        )
    if np.isfinite(daily_low):
        ax0.axhline(daily_low, linestyle="--", color="#2ca02c", linewidth=1.0, label="daily low")
    if np.isfinite(daily_high):
        ax0.axhline(daily_high, linestyle="--", color="#9467bd", linewidth=1.0, label="daily high")
    if np.isfinite(daily_vw):
        ax0.axhline(daily_vw, linestyle=":", color="#000000", linewidth=1.0, label="daily vw")
    ax0.set_title(
        f"{case_row.get('ticker','')} | {case_row.get('date_str','')} | {case_row.get('acceptance_label','')} | panel raw vs arbitros"
    )
    ax0.set_ylabel("precio")
    ax0.grid(alpha=0.2)
    ax0.legend(loc="best")
    ax0.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    if not minute_stats.empty:
        ax1.bar(minute_stats["minute_ny"], minute_stats["trades_n"], width=0.0009, color="#c7c7c7", alpha=0.7, label="trades por minuto")
        ax1b = ax1.twinx()
        ax1b.plot(minute_stats["minute_ny"], minute_stats["outside_daily_pct"], color="#d62728", linewidth=1.2, label="% outside daily")
        ax1b.plot(minute_stats["minute_ny"], minute_stats["outside_1m_pct"], color="#ff7f0e", linewidth=1.2, label="% outside 1m")
        ax1.set_ylabel("trades/min")
        ax1b.set_ylabel("% outside")
        ax1.set_title("Concentracion temporal del conflicto")
        ax1.grid(alpha=0.2)
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax1b.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, loc="upper right")
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else:
        ax1.text(0.5, 0.5, "Sin estadistica minuto a minuto.", ha="center", va="center", transform=ax1.transAxes)
        ax1.set_axis_off()

    integrity_labels = ["size<=0", "size NA", "price NA", "dup rows"]
    integrity_values = [non_positive_size, missing_size, missing_price, duplicate_rows]
    colors = ["#d62728" if v > 0 else "#c7c7c7" for v in integrity_values]
    ax2.bar(integrity_labels, integrity_values, color=colors, alpha=0.85)
    ax2.set_title("Integridad estructural del tape")
    ax2.set_ylabel("rows")
    ax2.grid(axis="y", alpha=0.2)
    for i, v in enumerate(integrity_values):
        ax2.text(i, v + max(1, max(integrity_values) * 0.02), f"{v}", ha="center", va="bottom", fontsize=9)

    ax3.axis("off")
    issues = ", ".join(map(str, _safe_list(case_row.get("issues_list")))) or "sin issues duras en sample_index"
    warns = ", ".join(map(str, _safe_list(case_row.get("warns_list")))) or "sin warns"
    subfamily = _case_visual_subfamily(case_row)
    summary_lines = [
        f"ticker: {case_row.get('ticker', '')}",
        f"fecha: {case_row.get('date_str', '')}",
        f"bucket: {case_row.get('acceptance_label', '')}",
        f"subfamilia_visual: {subfamily}",
        f"estrato: {case_row.get('sample_stratum', '')}",
        f"n_trades: {int(case_row.get('n_trades', case_row.get('rows_after_parse', 0)) or 0):,}",
        f"outside_daily_regular_pct: {float(case_row.get('outside_daily_regular_pct', np.nan)):.2f}%",
        f"outside_1m_regular_pct: {float(case_row.get('outside_1m_regular_pct', np.nan)):.2f}%",
        f"trade_vwap_vs_daily_vw_diff_pct_raw: {float(case_row.get('trade_vwap_vs_daily_vw_diff_pct_raw', np.nan)):.2f}%",
        f"duplicate_exact_ratio_pct_raw: {float(case_row.get('duplicate_exact_ratio_pct_raw', np.nan)):.2f}%",
        f"odd_lot_trade_pct: {float(case_row.get('odd_lot_trade_pct', np.nan)):.2f}%",
        f"non_positive_size_rows_raw: {non_positive_size}",
        f"duplicate_rows_exact_panel: {duplicate_rows}",
        f"issues: {issues}",
        f"warns: {warns}",
    ]
    ax3.text(0.01, 0.98, "\n".join(summary_lines), va="top", ha="left", family="monospace", fontsize=9.5)
    return fig, trades, ref_1m, daily_row


def _render_sample_case_panel(case_row: pd.Series) -> None:
    fig, trades, ref_1m, daily_row = _build_sample_case_figure(case_row)
    if fig is None or trades.empty:
        display(Markdown("No se pudo cargar el parquet raw del caso."))
        return
    plt.show()


def _sample_case_reading(case_row: pd.Series) -> str:
    bucket = str(case_row.get("acceptance_label", ""))
    scale_vw = str(case_row.get("scale_bucket_vw", ""))
    outside_daily = float(case_row.get("outside_daily_regular_pct", np.nan))
    outside_1m = float(case_row.get("outside_1m_regular_pct", np.nan))
    odd_lot = float(case_row.get("odd_lot_trade_pct", np.nan))
    duplicate = float(case_row.get("duplicate_exact_ratio_pct_raw", np.nan))
    issues = [str(x) for x in _safe_list(case_row.get("issues_list"))]
    warns = [str(x) for x in _safe_list(case_row.get("warns_list"))]
    subfamily = _case_visual_subfamily(case_row)

    bullets = [_family_description(bucket)]
    if bucket == "bad_data":
        bullets = [_case_visual_subfamily_explanation(subfamily)]
        if subfamily == "colapso_escala_rango":
            bullets.extend(
                [
                    "El fallo se ve de forma directa en el panel de precio: el tape y los arbitros no conviven en una misma geometria defendible.",
                    "La lectura correcta exige mirar la separacion vertical entre prints y arbitros y el hecho de que el conflicto de rango sea practicamente total.",
                    "Aqui el panel actual si responde bien a por que el file cae en `bad_data`.",
                ]
            )
        elif subfamily == "integridad_estructural":
            bullets.extend(
                [
                    "El precio puede parecer casi normal, asi que la causalidad principal no vive en la geometria del panel superior.",
                    "La lectura correcta depende del panel de integridad: sizes no validos, duplicados o rows estructuralmente invalidos.",
                    "Aqui el panel de precio por si solo no basta; el panel de integridad es el que justifica el rechazo.",
                ]
            )
        elif subfamily == "mixto_estructural_rango":
            bullets.extend(
                [
                    "El caso combina conflicto de rango con senales de integridad del tape.",
                    "La lectura correcta no es elegir una sola causa, sino reconocer que hay dano mixto: lo visual protesta y la estructura interna tambien.",
                    "La clasificacion a `bad_data` se apoya en ambas capas de evidencia y no solo en el porcentaje outside.",
                ]
            )
        elif subfamily == "conflicto_ralo_o_sparse":
            bullets.extend(
                [
                    "La gravedad nace en parte de la escasez del tape: muy pocas filas pueden romper el rango sin dejar una firma visual espectacular.",
                    "Eso obliga a leer el caso como file poco defendible, no como simple outlier bonito en un tape robusto.",
                    "El panel actual necesita leerse junto a `n_trades`, `rows_lt_10` y la concentracion del conflicto.",
                ]
            )
        else:
            bullets.extend(
                [
                    "El conflicto vive en una franja local del rango o del arbitro intraminuto, sin llegar a colapso total de escala.",
                    "Eso exige leer el panel minuto a minuto y no quedarse solo con la impresion global de la nube de precios.",
                    "La clasificacion a `bad_data` aqui depende de que el file ya no conserve una reconciliacion economica defendible.",
                ]
            )
    else:
        bullets.append(
            f"Responde a si el conflicto dominante vive en la escala (`{scale_vw}`), en la comparabilidad frente a `daily` ({outside_daily:.2f}%) o frente a `1m` ({outside_1m:.2f}%)."
        )

    if np.isfinite(odd_lot) and odd_lot >= 25:
        bullets.append(
            f"El {odd_lot:.2f}% de odd-lots empuja la lectura hacia microestructura fina; evita leer el caso como pura ruptura economica gruesa."
        )
    if np.isfinite(duplicate) and duplicate >= 5:
        bullets.append(
            f"El {duplicate:.2f}% de duplicacion exacta obliga a sospechar dano de tape o bursts mecanicos, no solo ruido visual."
        )
    if "negative_or_zero_size_rows" in issues:
        bullets.append("La presencia de `negative_or_zero_size_rows` mueve la causalidad desde el precio hacia la integridad estructural del tape.")
    if "duplicate_excess_ratio_gt_hard_cap" in issues:
        bullets.append("La marca `duplicate_excess_ratio_gt_hard_cap` indica que la duplicacion ya no es solo un warn cosmetico, sino una firma dura del rechazo.")
    if "rows_lt_10" in warns:
        bullets.append("La advertencia `rows_lt_10` limita fuertemente la defensa estadistica del file y endurece la lectura del caso.")

    if bucket == "good":
        bullets.append("La decision que justifica es que el file puede usarse como patron de tape limpio, no como medida de masa util del bloque.")
    elif bucket == "bad_data":
        bullets.append("La decision que justifica es exclusion de ejecucion simulada, labels y benchmarking; solo queda valor forense.")
    else:
        bullets.append("La decision que justifica es mantener o no el caso en `recoverable_with_flag` cuando se rematerialice la rehabilitacion sobre `57f`.")
    return "\n".join(f"- {b}" for b in bullets)


def build_trades_case_selector(default_layer: str = "case_pack") -> widgets.VBox:
    layers = sorted({entry.layer for entry in CASE_CATALOG} | {"muestra_380"})
    if default_layer not in layers:
        default_layer = layers[0]

    layer_dd = widgets.Dropdown(
        options=_grouped_options(layers),
        value=default_layer,
        description="capa",
        layout=widgets.Layout(width="320px"),
    )

    bucket_dd = widgets.Dropdown(
        description="bucket",
        layout=widgets.Layout(width="380px"),
    )

    case_dd = widgets.Dropdown(
        description="caso",
        layout=widgets.Layout(width="620px"),
    )

    out = widgets.Output()

    def refresh_buckets(*_):
        if layer_dd.value == "muestra_380":
            buckets = _sample_policy_bucket_values()
        else:
            buckets = sorted({entry.bucket for entry in _entries_for_layer(layer_dd.value)})
        bucket_dd.options = _grouped_options(buckets)
        if buckets:
            bucket_dd.value = buckets[0]
        else:
            bucket_dd.options = []
            case_dd.options = []

    def refresh_cases(*_):
        if layer_dd.value == "muestra_380":
            df = _sample_policy_cases(bucket_dd.value)
            options = [(label, idx) for idx, label in enumerate(df["case_label"].tolist())]
        else:
            entries = _entries_for_bucket(layer_dd.value, bucket_dd.value)
            options = [(entry.title, entry.case_id) for entry in entries]
        case_dd.options = options
        if options:
            case_dd.value = options[0][1]

    def render(*_):
        with out:
            clear_output(wait=True)
            if layer_dd.value == "muestra_380":
                row = _sample_policy_row(bucket_dd.value, int(case_dd.value))
                display(Markdown(f"## Trades inspection | muestra_380 | {row.get('ticker', '')} {row.get('date_str', '')}"))
                display(Markdown(
                    f"**Capa**: `muestra_380`  \n"
                    f"**Bucket**: `{row.get('acceptance_label', '')}`  \n"
                    f"**Estrato**: `{row.get('sample_stratum', '')}`"
                ))
                display(Markdown("### Que familia representa"))
                display(Markdown(_family_description(str(row.get("acceptance_label", "")))))
                display(Markdown("### Panel del caso"))
                _render_sample_case_panel(row)
                display(Markdown("### Lectura analitica"))
                display(Markdown(_sample_case_reading(row)))
                preview = _sample_file_preview(row, n_rows=10)
                display(Markdown("### Preview raw del parquet"))
                if preview.empty:
                    display(Markdown("No se pudo cargar preview raw para este caso."))
                else:
                    display(preview)
                display(Markdown("### Responde"))
                display(Markdown(
                    "- que vio realmente el notebook historico al recalcular raw files;  \n"
                    "- si esta familia se sostiene mas alla de 2 o 3 ejemplos bonitos;  \n"
                    "- y que decision cambiaria si este patron domina una fraccion grande del bucket."
                ))
            else:
                selected = next(entry for entry in CASE_CATALOG if entry.case_id == case_dd.value)
                image_path = TRADES_HISTORICAL_ASSETS_DIR / selected.image_name
                display(Markdown(f"## Trades inspection | {selected.title}"))
                display(Markdown(
                    f"**Capa**: `{selected.layer}`  \n"
                    f"**Bucket**: `{selected.bucket}`  \n"
                    f"**Asset**: `{image_path.name}`"
                ))
                if image_path.exists():
                    display(Image(filename=str(image_path)))
                else:
                    display(Markdown(f"No se encuentra la imagen: `{image_path}`"))
                display(Markdown("### Que muestra"))
                display(Markdown(selected.what_it_shows))
                display(Markdown("### Por que importa"))
                display(Markdown(selected.why_it_matters))
                display(Markdown("### Impacto en pipelines"))
                display(Markdown(selected.pipeline_impact))
                display(Markdown("### Cautela"))
                display(Markdown(selected.caution))

    layer_dd.observe(refresh_buckets, names="value")
    bucket_dd.observe(refresh_cases, names="value")
    case_dd.observe(render, names="value")

    refresh_buckets()
    refresh_cases()
    render()

    controls = widgets.HBox([layer_dd, bucket_dd, case_dd])
    return widgets.VBox([controls, out])
