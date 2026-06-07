from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
CASEPACK_ROOT = (
    PROJECT_ROOT
    / "01_foundations"
    / "inspection_dossiers"
    / "minute"
    / "core_quality_case_evidence_packs"
)
MANIFEST_PATH = CASEPACK_ROOT / "minute_core_quality_visual_case_manifest_v0_1.csv"
POPULATION_MANIFEST_PATH = (
    CASEPACK_ROOT
    / "population_visual_overview"
    / "minute_population_visual_manifest_v0_1.csv"
)
READOUT_PATH = CASEPACK_ROOT / "minute_core_quality_visual_cases_v0_1.md"


SECTION_INTROS = {
    "core_good_vw_not_flagged": (
        "Esta seccion comprueba el supuesto mas favorable: meses `core_good` donde el closeout heredado no marca `vw`. "
        "La inspeccion visual muestra que este bucket no es uniforme: algunos casos estan practicamente limpios, mientras que otros, sobre todo `MULN`, revelan residuo `vw` recalculado que no estaba capturado por la familia heredada."
    ),
    "core_good_vw_mild_or_moderate": (
        "Esta seccion cubre meses `core_good` con `vw` mild/moderate. La lectura visual exige cuidado: varios casos son micro-files o meses muy poco densos, por lo que porcentajes altos pueden salir de denominadores pequenos. "
        "La decision no es expulsar OHLCV, sino impedir que `vw` se consuma sin declarar sensibilidad."
    ),
    "core_good_vw_bad_persistent": (
        "Esta seccion muestra la familia donde el dano de `vw` es mas claro visualmente. Los puntos rojos aparecen de forma repetida y las barras diarias suelen estar altas en muchos dias. "
        "El mensaje contractual es fuerte: OHLCV puede seguir siendo investigable, pero `vw` queda fuera del consumo limpio."
    ),
    "core_good_vw_bad_diffuse": (
        "Esta seccion muestra dano `vw` severo pero mas distribuido o irregular que la familia persistent. La serie de precio suele seguir siendo legible, pero la linea `vw` y los puntos rojos aparecen en suficientes dias para bloquear consumidores `vw`."
    ),
    "core_review_large_gap": (
        "Esta seccion no trata principalmente de `vw`. El hecho visual dominante son huecos internos largos: la linea de precio puede interpolar o unir extremos, pero las barras de cobertura revelan que el mes no tiene continuidad suficiente para consumo no marcado."
    ),
    "core_review_sparse": (
        "Esta seccion muestra meses con pocos dias activos. Algunos tienen mucha actividad intradia dentro de esos pocos dias, pero el mes completo es demasiado parcial para presentarlo como cobertura mensual limpia."
    ),
}


def fmt(value, digits: int = 2) -> str:
    try:
        value = float(value)
    except Exception:
        return "nan"
    if pd.isna(value):
        return "nan"
    return f"{value:,.{digits}f}"


def anchor(text: str) -> str:
    out = text.lower()
    for ch in [" ", "_", "|", "/", "."]:
        out = out.replace(ch, "-")
    return "".join(c for c in out if c.isalnum() or c == "-")


def population_visual_reading(row: pd.Series) -> dict[str, str]:
    image = str(row["image"])

    if image == "00_population_core_vw_state_overview.png":
        return {
            "que_muestra": (
                "El mapa poblacional separa cuatro lecturas: calidad core, calidad `vw`, estado combinado y consumo permitido. "
                "La masa core aparece concentrada en `good` (`331,511`) frente a `review` (`3,149`), mientras `vw` concentra la deuda principal: `bad` (`212,763`), `review` (`75,245`) y solo una fraccion `good` (`46,652`). "
                "La consecuencia de consumo dominante es `ohlcv_without_vw_only` (`212,693`), no expulsion completa del OHLCV."
            ),
            "responde": (
                "Responde que el universo `ohlcv_1m_raw` no debe leerse como un bloque malo: el nucleo OHLCV es mayoritariamente aprovechable, pero `vw` no puede promocionarse como feature limpia."
            ),
            "no_responde": (
                "No responde si un ticker-month concreto es aceptable; solo fija la geometria global que debe gobernar los casos particulares."
            ),
            "consecuencia": (
                "El inspector debe empezar por esta separacion: core OHLCV, `vw` y consumo permitido son ejes distintos y no se pueden mezclar en una sola etiqueta de bueno/malo."
            ),
        }
    if image == "01_population_core_vw_matrix.png":
        return {
            "que_muestra": (
                "La matriz cruza `core_quality_state` contra `vw_quality_state`. La celda dominante es `core good / vw bad` (`212,693`), seguida de `core good / vw review` (`73,515`) y `core good / vw good` (`45,303`). "
                "El bloque `core review` es pequeno y no hay masa `core bad`."
            ),
            "responde": (
                "Responde que el problema central del 1m raw no es una rotura general de open/high/low/close, sino la promocion incorrecta de `vw` en una masa muy grande de ticker-months."
            ),
            "no_responde": (
                "No responde si `vw` puede reconstruirse o descartarse por reglas downstream; solo muestra que la decision no puede ser silenciosa."
            ),
            "consecuencia": (
                "La politica natural es conservar rutas OHLCV controladas y bloquear consumidores que dependan de `vw` salvo sensibilidad explicita."
            ),
        }
    if image == "02_population_issue_family_distributions.png":
        return {
            "que_muestra": (
                "La distribucion de familias muestra que el eje core esta dominado por `schema_readability_known_warning` (`331,511`), con colas pequenas de `large_internal_gap`, `coverage_sparse` y su interseccion. "
                "En cambio, `vw` tiene familias masivas: `vw_severe_large_mass_persistent`, `vw_severe_large_mass_diffuse`, `vw_severe_small_mass`, `vw_mild_low_ratio`, `vw_moderate_ratio`, `vw_not_flagged` y `vw_severe_tiny_base`."
            ),
            "responde": (
                "Responde que la auditoria necesita dos taxonomias: una para legibilidad/cobertura core y otra para dano semantico de `vw`."
            ),
            "no_responde": (
                "No responde si cada familia visualmente se ve igual; para eso existen los casepacks estratificados posteriores."
            ),
            "consecuencia": (
                "Las secciones de casos deben estar estratificadas por familia, porque una muestra aleatoria ocultaria las diferencias entre deuda `vw`, sparse coverage y large gaps."
            ),
        }
    if image == "03_population_coverage_and_temporal_footprint.png":
        return {
            "que_muestra": (
                "La figura muestra que muchos meses tienen `active_days` altos y `coverage_ratio` cercano a la zona 0.95-1.00, mientras `max_gap_days` concentra la masa alrededor de huecos cortos con cola larga. "
                "El footprint temporal crece con fuerza despues de 2016, alcanza maximos alrededor de 2022-2025 y cae en 2026 por ano parcial."
            ),
            "responde": (
                "Responde que las familias `large_gap` y `sparse` son colas de cobertura, no la forma dominante del dataset."
            ),
            "no_responde": (
                "No responde si la cobertura esperada por ticker deberia existir en todos los anos; eso depende del universo/membership y de reglas de disponibilidad."
            ),
            "consecuencia": (
                "La auditoria debe tratar gaps y sparse months como motivos de `review` separados de la deuda `vw`, y debe recordar que 2026 no es comparable con anos completos."
            ),
        }
    if image == "04_population_schema_only_anatomy.png":
        return {
            "que_muestra": (
                "La anatomia schema-only muestra una firma muy concentrada en `dataset_read_incompatible_schema` mas `schema_merge_conflict_ticker_encoding`. "
                "Los tickers principales incluyen nombres con sufijos o formas sensibles (`HVT.A`, `GTN.A`, `CRD.A`, entre otros), y la serie temporal muestra regimenes: bloque temprano alto, tramo medio casi nulo y repunte posterior."
            ),
            "responde": (
                "Responde que el bloque no-`vw` no es una coleccion aleatoria de fallos economicos; es principalmente una deuda estructural de lectura/esquema y codificacion de ticker."
            ),
            "no_responde": (
                "No responde que todos esos meses sean inutilizables para OHLCV; muchos pueden estar pendientes de normalizacion de lectura, no de rechazo economico."
            ),
            "consecuencia": (
                "No se debe mezclar schema-only con dano `vw`: requiere contrato de schema/readability y, si se repara, puede cambiar la frontera de consumo sin tocar el precio."
            ),
        }
    if image == "05_population_vw_not_flagged_visual_recalc_delta.png":
        return {
            "que_muestra": (
                "La comparacion entre `vw_not_flagged` heredado y recalculo visual revela que algunos casos etiquetados como no marcados si tienen residuo material. "
                "El patron visible esta concentrado en `MULN`, con barras superiores al 1% y hasta mas del 5% de minutos `vw` fuera de rango por mas de 1 bp; otros tickers quedan practicamente en cero."
            ),
            "responde": (
                "Responde que `vw_not_flagged` no equivale automaticamente a `vw` visualmente limpio en cada caso."
            ),
            "no_responde": (
                "No responde que toda la familia `vw_not_flagged` este mal; la propia figura muestra muchos casos cerca de cero."
            ),
            "consecuencia": (
                "El dossier debe conservar una advertencia explicita: los ejemplos favorables existen, pero la etiqueta heredada necesita tolerancia declarada o recalculo si `vw` se consume."
            ),
        }
    if image == "06_population_allowed_consumption_by_year.png":
        return {
            "que_muestra": (
                "La evolucion anual separa `controlled_ohlcv_research`, `flagged_research_or_sensitivity` y `ohlcv_without_vw_only`. "
                "Desde 2017 la masa `ohlcv_without_vw_only` domina claramente, con pico alrededor de 2022, mientras el consumo controlado OHLCV existe durante todo el periodo y 2026 cae por ano incompleto."
            ),
            "responde": (
                "Responde que la decision de consumo no es estatica por ano: la restriccion `sin vw` pesa especialmente en la etapa moderna de mayor cobertura."
            ),
            "no_responde": (
                "No responde si el universo objetivo de backtest debe ponderar cada ano igual; solo muestra la disponibilidad y restriccion por ticker-month."
            ),
            "consecuencia": (
                "Cualquier entrenamiento/backtest que use 1m debe declarar si consume solo OHLCV o tambien `vw`; si usa `vw`, la mayor parte de los anos modernos queda fuera o entra como sensibilidad marcada."
            ),
        }

    return {
        "que_muestra": "La imagen muestra una vista poblacional del dataset `ohlcv_1m_raw`.",
        "responde": "Responde a una pregunta global previa a los casos particulares.",
        "no_responde": "No responde por si sola la decision de cada ticker-month.",
        "consecuencia": "Debe leerse antes de los casepacks estratificados.",
    }


def case_visual_reading(row: pd.Series) -> dict[str, str]:
    section = str(row["visual_section"])
    ticker = str(row["ticker"])
    ym = f"{int(row['year'])}-{int(row['month']):02d}"
    visual_ratio = float(row.get("visual_gt_1bp_vw_ratio_pct", 0) or 0)
    strict_ratio = float(row.get("recalc_strict_vw_ratio_pct", 0) or 0)
    active_days = float(row.get("m.active_days", 0) or 0)
    max_gap = float(row.get("m.max_gap_days", 0) or 0)
    rows = float(row.get("m.rows_after_parse", 0) or 0)
    inherited_vw = str(row.get("vw_issue_family", ""))
    combined = str(row.get("combined_quality_state", ""))

    if section == "core_good_vw_not_flagged":
        if visual_ratio >= 1:
            qm = (
                f"La imagen muestra una serie OHLCV densa y continua, pero tambien barras rojas de `vw` material en varios dias. "
                f"El punto sensible es que el bucket heredado dice `{inherited_vw}`, mientras el recalculo visual marca `{visual_ratio:.2f}%` de minutos `vw` fuera de rango por mas de 1 bp."
            )
            resp = (
                "Responde que el core OHLCV puede seguir siendo interpretable, pero que `vw_not_flagged` no debe leerse como ausencia visual absoluta de residuo `vw` en todos los casos."
            )
            no = (
                "No responde por si sola si el closeout heredado debe reabrirse globalmente; solo prueba que esta familia necesita lectura visual y tolerancia declarada."
            )
            cons = (
                "Mantener OHLCV en investigacion controlada, pero no usar este caso como ejemplo de `vw` perfectamente limpio sin mencionar la discrepancia recalculada."
            )
        else:
            qm = (
                "La imagen muestra precio, low-high y `vw` practicamente superpuestos, sin barras rojas materiales. La cobertura diaria aparece regular para el alcance del mes."
            )
            resp = (
                "Responde que este caso si representa bien la lectura favorable de `core_good`: OHLCV usable y sin dano `vw` visible material."
            )
            no = (
                "No responde por todos los meses `vw_not_flagged`, porque otros casos de la misma seccion si muestran residuo recalculado."
            )
            cons = (
                "Puede usarse como ejemplo positivo de consumo `controlled_ohlcv_research`, preservando la nota de que el ejemplo no promociona toda la familia sin revision."
            )
    elif section == "core_good_vw_mild_or_moderate":
        if rows < 100:
            qm = (
                f"La imagen es muy escasa: pocos puntos y barras diarias con denominadores pequenos. Por eso los porcentajes rojos pueden llegar a 100% sin demostrar por si solos una degradacion mensual robusta."
            )
        elif active_days <= 6:
            qm = (
                f"La imagen concentra actividad en pocos dias. Hay `vw` visible fuera de rango, pero la lectura esta muy condicionada por cobertura parcial del mes."
            )
        else:
            qm = (
                f"La imagen muestra una serie mas informativa: hay residuo `vw` en varios dias, pero el precio OHLCV mantiene una geometria legible y no parece roto."
            )
        resp = (
            "Responde que `vw` requiere flag o sensibilidad, pero que el core OHLCV no queda invalidado por esta familia."
        )
        no = (
            "No responde que `vw` sea apto para features; tampoco prueba limpieza mensual si el caso tiene pocos dias o pocas filas."
        )
        cons = (
            "Permitir investigacion OHLCV controlada y bloquear consumo silencioso de `vw`."
        )
    elif section == "core_good_vw_bad_persistent":
        qm = (
            "La imagen muestra puntos rojos repetidos sobre casi toda la ventana y barras diarias altas. No es un residuo local: el dano `vw` acompana buena parte del mes."
        )
        resp = (
            "Responde que la familia `vw_bad_persistent` esta visualmente justificada: `vw` no conserva semantica confiable aunque la trayectoria OHLCV sea legible."
        )
        no = (
            "No responde que open/high/low/close esten rotos. La figura separa dano `vw` de dano core."
        )
        cons = (
            "Clasificar el caso como `ohlcv_without_vw_only`: conservar OHLCV para investigacion controlada, excluir `vw` de cualquier consumidor."
        )
    elif section == "core_good_vw_bad_diffuse":
        qm = (
            "La imagen muestra dano `vw` frecuente pero menos uniforme que persistent. Hay sesiones limpias o menos afectadas junto a bloques con muchos puntos rojos."
        )
        resp = (
            "Responde que el problema no es un unico spike aislado: la frecuencia de barras rojas basta para impedir consumo limpio de `vw`."
        )
        no = (
            "No responde que el mes sea inutil para todo uso. La serie de precio sigue dando contexto OHLCV aprovechable bajo restricciones."
        )
        cons = (
            "Mantener el caso fuera de features `vw` y permitir solo rutas que declaren `ohlcv_without_vw_only`."
        )
    elif section == "core_review_large_gap":
        qm = (
            f"La imagen muestra huecos temporales largos: `max_gap_days={max_gap:.0f}`. La linea puede unir extremos, pero las barras de cobertura revelan que faltan bloques enteros del mes."
        )
        resp = (
            "Responde que la razon del `core_review` es continuidad/cobertura, no necesariamente precio roto."
        )
        no = (
            "No responde que los minutos presentes sean malos; responde que el mes no es una muestra mensual completa."
        )
        cons = (
            "Consumir solo como investigacion marcada o sensibilidad; no usar como mes completo no marcado."
        )
    elif section == "core_review_sparse":
        qm = (
            f"La imagen muestra actividad concentrada en aproximadamente `{active_days:.0f}` dias. Dentro de esos dias puede haber muchas filas, pero el mes completo queda demasiado parcial."
        )
        resp = (
            "Responde que sparse coverage es una frontera distinta de calidad de precio: el problema es representatividad mensual."
        )
        no = (
            "No responde que la accion no haya operado fuera de esos dias; solo muestra que este parquet no cubre lo bastante para consumo mensual limpio."
        )
        cons = (
            "Mantener en `flagged_research_or_sensitivity`; no usar para entrenamiento o backtest que asuma cobertura mensual plena."
        )
    else:
        qm = "La imagen requiere lectura dentro de su familia."
        resp = "Responde a la inspeccion visual local."
        no = "No responde a una promocion global."
        cons = "Mantener consumo gobernado por el manifest."

    return {
        "que_muestra": qm,
        "responde": resp,
        "no_responde": no,
        "consecuencia": cons,
    }


def build_markdown(df: pd.DataFrame, population_df: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append("# Minute Core Quality Visual Cases v0.1")
    lines.append("")
    lines.append("Fecha de referencia: 2026-06-07.")
    lines.append("")
    lines.append(
        "Este dossier visual corrige el cierre incompleto del paquete moderno de `minute`: no basta con notebooks y manifests. "
        "Cada imagen esta exportada como PNG estable, incrustada aqui y leida bajo la regla contractual `Que muestra / Responde / No responde / Consecuencia`."
    )
    lines.append("")
    lines.append("## Alcance")
    lines.append("")
    lines.append("- dataset: `ohlcv_1m_raw_v0_1`")
    lines.append("- universo: `<1B>` segun el manifest activo de `minute`")
    lines.append("- unidad visual: `ticker-month`")
    lines.append("- visuales poblacionales exportados: `7`")
    lines.append("- imagenes de caso exportadas: `60`")
    lines.append("- total de imagenes incrustadas: `67`")
    lines.append("- secciones de casos: `6`")
    lines.append("- builder poblacional: `scripts/inspection/minute/export_minute_population_visuals.py`")
    lines.append("- builder de imagenes: `scripts/inspection/minute/export_minute_core_quality_casepacks.py`")
    lines.append("- manifest poblacional: `population_visual_overview/minute_population_visual_manifest_v0_1.csv`")
    lines.append("- manifest visual: `minute_core_quality_visual_case_manifest_v0_1.csv`")
    lines.append("")
    lines.append("## Regla De Lectura")
    lines.append("")
    lines.append("La imagen no decide sola si el dataset completo es bueno o malo.")
    lines.append("")
    lines.append("Cada caso separa:")
    lines.append("")
    lines.append("- calidad core OHLCV;")
    lines.append("- deuda `vw`;")
    lines.append("- cobertura/gaps;")
    lines.append("- y consumo permitido.")
    lines.append("")
    lines.append("Una barra roja en `vw` no invalida automaticamente OHLCV. Un mes con pocos dias activos no demuestra precio roto, pero tampoco permite tratarlo como mes completo limpio.")
    lines.append("")
    lines.append("## Mapa Poblacional Visual")
    lines.append("")
    lines.append(
        "Estas imagenes son obligatorias antes de leer los casos particulares. Situan el universo completo por estado core, estado `vw`, familias de issues, cobertura, deuda schema-only y consumo permitido."
    )
    lines.append("")
    for _, row in population_df.iterrows():
        lines.append(f"### {row['title']}")
        lines.append("")
        lines.append(f"Pregunta: {row['question']}")
        lines.append("")
        lines.append(f"![{row['title']}](./population_visual_overview/{row['image']})")
        lines.append("")
        reading = population_visual_reading(row)
        lines.append("**Que muestra**")
        lines.append("")
        lines.append(f"- {reading['que_muestra']}")
        lines.append("")
        lines.append("**Responde**")
        lines.append("")
        lines.append(f"- {reading['responde']}")
        lines.append("")
        lines.append("**No responde**")
        lines.append("")
        lines.append(f"- {reading['no_responde']}")
        lines.append("")
        lines.append("**Consecuencia**")
        lines.append("")
        lines.append(f"- {reading['consecuencia']}")
        lines.append("")
    lines.append("## Menu")
    lines.append("")
    lines.append("- [Mapa Poblacional Visual](#mapa-poblacional-visual)")
    for section, g in df.groupby("visual_section", sort=False):
        title = str(g["visual_section_title"].iloc[0])
        lines.append(f"- [{title}](#{anchor(title)})")
    lines.append("")

    for section, g in df.groupby("visual_section", sort=False):
        title = str(g["visual_section_title"].iloc[0])
        lines.append(f"## {title}")
        lines.append("")
        lines.append(SECTION_INTROS.get(section, ""))
        lines.append("")
        for _, row in g.sort_values("visual_rank").iterrows():
            ticker = row["ticker"]
            ym = f"{int(row['year'])}-{int(row['month']):02d}"
            lines.append(f"### {int(row['visual_rank']):02d}. {ticker} {ym}")
            lines.append("")
            lines.append(f"ticker: `{ticker}`  ")
            lines.append(f"year: `{int(row['year'])}`  ")
            lines.append(f"month: `{int(row['month'])}`  ")
            lines.append(f"core_quality_state: `{row['core_quality_state']}`  ")
            lines.append(f"vw_quality_state: `{row['vw_quality_state']}`  ")
            lines.append(f"combined_quality_state: `{row['combined_quality_state']}`  ")
            lines.append(f"allowed_consumption: `{row['allowed_consumption']}`  ")
            lines.append(f"core_issue_family: `{row['core_issue_family']}`  ")
            lines.append(f"vw_issue_family: `{row['vw_issue_family']}`  ")
            lines.append(f"rows_after_parse: `{fmt(row['m.rows_after_parse'], 0)}`  ")
            lines.append(f"active_days: `{fmt(row['m.active_days'], 0)}`  ")
            lines.append(f"coverage_ratio: `{fmt(row['m.coverage_ratio_vs_active_days_est'], 3)}`  ")
            lines.append(f"max_gap_days: `{fmt(row['m.max_gap_days'], 0)}`  ")
            lines.append(f"inherited_vw_ratio_pct: `{fmt(row.get('vw_ratio_pct'), 3)}`  ")
            lines.append(f"visual_gt_1bp_vw_ratio_pct: `{fmt(row.get('visual_gt_1bp_vw_ratio_pct'), 3)}`  ")
            lines.append(f"file: `{row['file']}`")
            lines.append("")
            lines.append(f"![{ticker} {ym}](./{row['image']})")
            lines.append("")
            reading = case_visual_reading(row)
            lines.append("**Que muestra**")
            lines.append("")
            lines.append(f"- {reading['que_muestra']}")
            lines.append("")
            lines.append("**Responde**")
            lines.append("")
            lines.append(f"- {reading['responde']}")
            lines.append("")
            lines.append("**No responde**")
            lines.append("")
            lines.append(f"- {reading['no_responde']}")
            lines.append("")
            lines.append("**Consecuencia**")
            lines.append("")
            lines.append(f"- {reading['consecuencia']}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(MANIFEST_PATH)
    if not POPULATION_MANIFEST_PATH.exists():
        raise FileNotFoundError(POPULATION_MANIFEST_PATH)
    df = pd.read_csv(MANIFEST_PATH)
    population_df = pd.read_csv(POPULATION_MANIFEST_PATH)
    text = build_markdown(df, population_df)
    READOUT_PATH.write_text(text, encoding="utf-8", newline="\n")
    print(READOUT_PATH)
    print(f"cases={len(df)}")
    print(f"population_visuals={len(population_df)}")


if __name__ == "__main__":
    main()
