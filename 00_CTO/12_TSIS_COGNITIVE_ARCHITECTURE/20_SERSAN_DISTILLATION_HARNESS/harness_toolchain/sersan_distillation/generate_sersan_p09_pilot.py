from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"C:\TSIS_Data")
CTO = ROOT / "00_CTO"
SERSAN_ROOT = CTO / "99_REFERENCE_LIBRARY" / "SersanSistemas"
SRC_MD_REL = Path("03_only_md_revised") / "practica_09_revision_apolo.md"
SRC_MD = SERSAN_ROOT / SRC_MD_REL
WORKSHOP_REL = Path("02_workshops") / "19-practice-09"
IMAGE_DIR_REL = WORKSHOP_REL / "img"
CODE_REL = WORKSHOP_REL / "code" / "PRACTICA 09.ELD"
XLSX_REL = WORKSHOP_REL / "docs" / "MAPA ES SHORT zona 3.xlsx"

COG = CTO / "12_TSIS_COGNITIVE_ARCHITECTURE"
SHARED_KERNEL = COG / "00_SHARED_HARNESS_KERNEL"
SERSAN_HARNESS = COG / "20_SERSAN_DISTILLATION_HARNESS"
OUT_DIR = SERSAN_HARNESS / "sersan_distillation_artifacts" / "sersan_practice_09_revision_apolo"

LESSON_ID = "sersan_practice_09_revision_apolo"
DATE = "2026-06-12"
GENERATED_BY = "manual_sersan_pilot_harness_codex_v0_2"
CONTRACT_VERSION = "sersan_lesson_pack_contract_v0_1"
GENERATOR_REL = (
    "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/"
    "harness_toolchain/sersan_distillation/generate_sersan_p09_pilot.py"
)
TOOLCHAIN_CONTRACT_REL = (
    "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/"
    "harness_toolchain_traceability_contract.md"
)
ARTIFACT_CONTRACT_REL = (
    "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/"
    "sersan_lesson_pack_contract.md"
)
RUNBOOK_REL = (
    "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/"
    "sersan_pilot_harness_runbook.md"
)
SHARED_MANIFEST_REL = (
    "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/"
    "shared_run_manifest_contract.md"
)
SHARED_VALIDATION_REL = (
    "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/"
    "shared_validation_principles.md"
)


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def rel_posix(path: Path) -> str:
    return path.as_posix()


def project_rel(path: Path) -> str:
    return rel_posix(path.relative_to(ROOT))


def sersan_rel(path: Path) -> str:
    return rel_posix(path.relative_to(SERSAN_ROOT))


def yaml_quote(value):
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


def yaml_dump(value, indent=0):
    sp = " " * indent
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{sp}{key}:")
                lines.append(yaml_dump(item, indent + 2))
            else:
                lines.append(f"{sp}{key}: {yaml_quote(item)}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{sp}-")
                lines.append(yaml_dump(item, indent + 2))
            elif isinstance(item, list):
                lines.append(f"{sp}-")
                lines.append(yaml_dump(item, indent + 2))
            else:
                lines.append(f"{sp}- {yaml_quote(item)}")
        return "\n".join(lines)
    return f"{sp}{yaml_quote(value)}"


def section_id(n: int) -> str:
    return f"{LESSON_ID}_sec_{n:04d}"


def image_id(stem: str, occurrence: int) -> str:
    if occurrence == 1:
        return f"{LESSON_ID}_img_{stem}"
    return f"{LESSON_ID}_img_{stem}_ref_{occurrence:02d}"


def rule_id(n: int) -> str:
    return f"{LESSON_ID}_rule_{n:04d}"


def translation_id(n: int) -> str:
    return f"{LESSON_ID}_tr_{n:04d}"


def source_anchor(section_n, line_start, line_end, images=None):
    return {
        "lesson_id": LESSON_ID,
        "md_path": rel_posix(SRC_MD_REL),
        "section_id": section_id(section_n),
        "line_start": line_start,
        "line_end": line_end,
        "image_ids": images or [],
    }


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


RAW_SECTIONS = [
    {
        "n": 1,
        "heading_path": ["Practice 9", "Entrada y contexto"],
        "section_type": "procedure",
        "line_start": 1,
        "line_end": 19,
        "summary": "Entrada, navegacion y contexto material de la practica.",
        "keywords": ["practice-09", "apolo", "revision"],
        "contains_code": False,
        "contains_table": False,
        "contains_question": False,
        "requires_image_reading": False,
        "requires_human_review": False,
        "notes": ["Seccion estructural; no se promueve como doctrina mecanica."],
    },
    {
        "n": 2,
        "heading_path": ["Practice 9", "Cuestiones iniciales"],
        "section_type": "qa",
        "line_start": 20,
        "line_end": 216,
        "summary": "Resuelve preguntas sobre Bollinger Bands, Open of next bar, filtros, muestra y sobreoptimizacion.",
        "keywords": ["open-next-bar", "filtros", "sample-size", "overfit", "bollinger"],
        "contains_code": False,
        "contains_table": False,
        "contains_question": True,
        "requires_image_reading": False,
        "requires_human_review": False,
        "notes": [],
    },
    {
        "n": 3,
        "heading_path": ["Practice 9", "Revision de Apolo", "Sistema y asimetria long/short"],
        "section_type": "concept",
        "line_start": 217,
        "line_end": 304,
        "summary": "Presenta Apolo como sistema real long/short y explica por que el lado short requiere parametros y exits distintos.",
        "keywords": ["apolo", "short-equity", "long-short", "take-profit", "stop-loss"],
        "contains_code": False,
        "contains_table": False,
        "contains_question": False,
        "requires_image_reading": False,
        "requires_human_review": False,
        "notes": [],
    },
    {
        "n": 4,
        "heading_path": ["Practice 9", "Protocolo de supervision y metricas"],
        "section_type": "procedure",
        "line_start": 305,
        "line_end": 392,
        "summary": "Define la supervision operativa: performance report, drawdown, equity, trade list, peores rachas y alarmas.",
        "keywords": ["supervision", "drawdown", "worst-trade", "losing-streak", "performance-report"],
        "contains_code": False,
        "contains_table": False,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": False,
        "notes": [],
    },
    {
        "n": 5,
        "heading_path": ["Practice 9", "Preparacion del mapa de optimizacion"],
        "section_type": "procedure",
        "line_start": 393,
        "line_end": 643,
        "summary": "Fija rango historico, OOS, comisiones, slippage, variables optimizables, penalizacion por halt y exportacion IS/OOS/AllData.",
        "keywords": ["optimization-map", "execution-realism", "halt", "in-sample", "out-of-sample", "fitness"],
        "contains_code": True,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": ["El codigo EasyLanguage se inventaria, pero este piloto no valida sintaxis ni ejecucion del ELD."],
    },
    {
        "n": 6,
        "heading_path": ["Practice 9", "Mapas", "Tablas dinamicas y lectura por zonas"],
        "section_type": "validation",
        "line_start": 644,
        "line_end": 1056,
        "summary": "Construye mapas mediante tablas dinamicas, desconfia de superficies 3D y lee zonas, vecinos, bordes y sensibilidad.",
        "keywords": ["pivot-table", "heatmap", "3d-surface", "neighbors", "zone-selection"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 7,
        "heading_path": ["Practice 9", "Definicion de zonas y filtrado previo"],
        "section_type": "procedure",
        "line_start": 1057,
        "line_end": 1222,
        "summary": "Delimita zonas claras de Per_01, Var_01, Var_02 y Var_03 antes de la seleccion final.",
        "keywords": ["zone-filter", "input-range", "parameter-boundary", "Var_01", "Var_02"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 8,
        "heading_path": ["Practice 9", "Mapa filtrado Var_01 vs Var_02"],
        "section_type": "validation",
        "line_start": 1223,
        "line_end": 1377,
        "summary": "Compara maximo local frente a robustez distribuida y usa el mapa filtrado para preferir parametros todoterreno.",
        "keywords": ["filtered-map", "robustness", "parameter-tolerance", "Var_01", "Var_02"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 9,
        "heading_path": ["Practice 9", "Retorno al mapa grande y reconstruccion final"],
        "section_type": "validation",
        "line_start": 1378,
        "line_end": 1685,
        "summary": "Revisa zona 2, extiende rangos cuando un optimo toca borde y reconstruye la lectura final del mapa.",
        "keywords": ["boundary-extension", "Per_01", "Var_01", "zone-2", "map-rebuild"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 10,
        "heading_path": ["Practice 9", "Limitacion de 8000 combinaciones"],
        "section_type": "warning",
        "line_start": 1686,
        "line_end": 1719,
        "summary": "Advierte que dejar elegir directamente entre las 8000 mejores combinaciones de IS es sobreoptimizar.",
        "keywords": ["overoptimization", "8000-combinations", "selection-bias", "in-sample"],
        "contains_code": False,
        "contains_table": False,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 11,
        "heading_path": ["Practice 9", "Optimizacion exhaustiva recortada de 250"],
        "section_type": "procedure",
        "line_start": 1720,
        "line_end": 1964,
        "summary": "Reduce el universo a una zona acotada, guarda 250 candidatos y compara TSI, ES, PPC y robustez en IS/OOS/AllData.",
        "keywords": ["top-250", "TSI", "expectancy-score", "PPC", "robustness", "IS-OOS"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 12,
        "heading_path": ["Practice 9", "Performance Reports y seleccion visual"],
        "section_type": "human_review",
        "line_start": 1965,
        "line_end": 2074,
        "summary": "Integra Performance Reports, revision humana independiente, ocultacion de parametros y evaluacion final a nivel portfolio.",
        "keywords": ["performance-report", "equity-curve", "human-review", "portfolio-maestro", "bias-control"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 13,
        "heading_path": ["Practice 9", "Revision de incrementos"],
        "section_type": "validation",
        "line_start": 2075,
        "line_end": 2227,
        "summary": "Fija la tecnica para detectar granularidad incorrecta: medir cuanto cambia el numero de trades por un tick de parametro.",
        "keywords": ["increment", "granularity", "parameter-step", "trade-count", "sensitivity"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 14,
        "heading_path": ["Practice 9", "Revision real y seleccion reciente"],
        "section_type": "procedure",
        "line_start": 2228,
        "line_end": 2289,
        "summary": "Describe la revision real del sistema, la lectura de alarmas y el foco reciente del Performance Report final.",
        "keywords": ["live-review", "recent-period", "alarms", "operating-set"],
        "contains_code": False,
        "contains_table": False,
        "contains_question": True,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 15,
        "heading_path": ["Practice 9", "Por que no se hace Walk-Forward para Apolo"],
        "section_type": "warning",
        "line_start": 2290,
        "line_end": 2339,
        "summary": "Justifica por que el rolling WF puede ser fragil para este short diario con pocas operaciones y money management distorsionante.",
        "keywords": ["walk-forward", "anchored-wf", "money-management", "short-equity", "sample-size"],
        "contains_code": False,
        "contains_table": False,
        "contains_question": False,
        "requires_image_reading": False,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 16,
        "heading_path": ["Practice 9", "Alfa y descorrelacion en carteras"],
        "section_type": "portfolio",
        "line_start": 2340,
        "line_end": 2400,
        "summary": "Situa los shorts de acciones como herramienta de alfa y descorrelacion, no como primera ruta de investigacion ni smart beta.",
        "keywords": ["alpha", "decorrelation", "short-equity", "portfolio", "client-product"],
        "contains_code": False,
        "contains_table": False,
        "contains_question": False,
        "requires_image_reading": False,
        "requires_human_review": True,
        "notes": [],
    },
]


IMAGE_OVERRIDES = {
    "020": {
        "visual_type": "execution_chart",
        "contains_numbers": False,
        "contains_chart": True,
        "doctrine_relevance": "critical",
        "requires_human_review": True,
        "notes": "Captura del tramo COVID/halt donde el backtest obtiene un beneficio no ejecutable; sostiene la regla de penalizar fills no realistas.",
        "technical_reading": "El circulo rojo marca una ejecucion artificialmente favorable durante un halt o discontinuidad. La clase convierte ese caso en input de penalizacion para que el optimizador no seleccione una ventaja imposible de operar.",
    },
    "038": {
        "visual_type": "optimization_heatmap",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Mapa de optimizacion Per_01 vs Var_01 con TSI/PPC y totales; evidencia de lectura por zonas y no por ranking aislado.",
        "technical_reading": "La tabla muestra concentraciones de calidad, huecos y vecinos. Debe usarse para descartar zonas fragiles y no para elegir automaticamente la celda de mayor valor.",
    },
    "040": {
        "visual_type": "optimization_surface",
        "contains_numbers": True,
        "contains_chart": True,
        "doctrine_relevance": "medium",
        "requires_human_review": True,
        "notes": "Comparacion de tabla dinamica y superficie 3D; la escala visual puede inducir conclusiones falsas.",
        "technical_reading": "La superficie 3D puede exagerar o esconder discontinuidades segun la escala. La tabla dinamica/heatmap queda como lectura primaria.",
    },
    "049": {
        "visual_type": "optimization_heatmap",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Zoom de mapa Per_01 vs Var_01; evidencia de zonas candidatas y necesidad de vecinos.",
        "technical_reading": "El zoom permite comparar una celda candidata con sus vecinos inmediatos. Un optimo local sin continuidad no debe promocionarse.",
    },
    "053": {
        "visual_type": "optimization_heatmap",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Mapa Var_02 vs Var_03; muestra tolerancia relativa del stop y sensibilidad del take profit.",
        "technical_reading": "El take profit conserva una zona util alrededor de 0.7-1.0 y se deteriora cerca de 0.5. El stop es menos sensible en la zona mostrada.",
    },
    "057": {
        "visual_type": "optimization_heatmap",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Mapa de exits con zonas remarcadas; sostiene el filtrado de Var_02/Var_03 por robustez visual.",
        "technical_reading": "Los recuadros muestran que no basta con un valor bueno: se buscan franjas que toleren vecinos y que conserven degradacion progresiva.",
    },
    "064": {
        "visual_type": "optimization_table",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Tabla de candidatos donde un cambio pequeno de Var_01 cambia unos 20 trades; evidencia de granularidad potencialmente gruesa.",
        "technical_reading": "Comparar Var_01 0.625 contra 0.600 con el resto constante muestra salto material en numero de trades. El Harness debe medir sensibilidad por tick de input.",
    },
    "066": {
        "visual_type": "optimization_heatmap",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "critical",
        "requires_human_review": True,
        "notes": "Mapa Per_01 vs Var_01 que compara una zona local fuerte contra distribucion mas amplia; base de la regla todoterreno.",
        "technical_reading": "Aunque 0.575 puede destacar en una zona, 0.600 reparte calidad a lo largo de mas periodos. La robustez se lee por distribucion, no solo por maximo.",
    },
    "090": {
        "visual_type": "optimization_heatmap",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Mapa filtrado amplio Var_01/Var_02/Per_01; evidencia de la densidad necesaria antes de cerrar zonas.",
        "technical_reading": "La captura muestra que las zonas validas deben sobrevivir en un mapa filtrado grande, no solo en un recorte favorable.",
    },
    "093": {
        "visual_type": "optimization_heatmap",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Comparacion visual de dos zonas candidatas; evidencia de tolerancia y continuidad en mapas.",
        "technical_reading": "Los recuadros permiten comparar continuidad entre grupos de parametros; la seleccion debe preferir estabilidad de zona.",
    },
    "098": {
        "visual_type": "optimization_heatmap",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Mapa con recuadros de zona robusta; refuerza la decision por region y no por celda.",
        "technical_reading": "La region magenta concentra muchos valores aceptables. Esa densidad es evidencia de tolerancia de parametros.",
    },
    "111": {
        "visual_type": "optimization_heatmap",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Extension de Per_01 hasta 30 tras detectar borde en 25; evidencia de que un optimo en borde exige ampliar rango.",
        "technical_reading": "La tabla muestra valores 23-30 y permite comprobar si el maximo original era frontera artificial. El Harness debe pedir extension antes de cerrar seleccion.",
    },
    "117": {
        "visual_type": "optimization_heatmap",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Mapa Var_02/Var_03 de TSI; muestra degradacion del take profit y tolerancia del stop.",
        "technical_reading": "La fila Var_02=0.5 queda debil frente a 0.7-1.0. Mantener vecinos malos visibles ayuda a ver transiciones y cliffs.",
    },
    "126": {
        "visual_type": "optimization_ranking",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "critical",
        "requires_human_review": True,
        "notes": "Ranking de mejores combinaciones; sostiene la advertencia de no elegir directamente entre 8000 mejores IS.",
        "technical_reading": "La tabla lista candidatos con metricas potentes, pero la clase la usa como advertencia: el ranking amplio de IS es material para mapas, no decision final.",
    },
    "127": {
        "visual_type": "optimization_comparison",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Comparacion IS/OOS/AllData y variaciones; evidencia de contraste multi-split antes de seleccionar.",
        "technical_reading": "Las columnas de robustez y variaciones muestran que un candidato puede destacar en una metrica y deteriorarse en otra. La seleccion exige lectura cruzada.",
    },
    "131": {
        "visual_type": "statistics_table",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "medium",
        "requires_human_review": True,
        "notes": "Tabla descriptiva de candidatos; evidencia del uso de media, mediana, rango y dispersion.",
        "technical_reading": "La clase mira estadisticos descriptivos para no dejarse arrastrar por outliers de la muestra de candidatos.",
    },
    "142": {
        "visual_type": "optimization_setup",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "critical",
        "requires_human_review": True,
        "notes": "Ficha de optimizacion recortada a 250 y resumen TSI/ES/PPC/Robustness.",
        "technical_reading": "La captura fija el protocolo: zona acotada, 250 guardados, costes, OOS y comparacion de fitness. ES muestra mejor robustez OOS en este caso.",
    },
    "143": {
        "visual_type": "fitness_summary",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Zoom de TSI, ES, PPC y Robustness; evidencia de que el fitness predictivo debe medirse por sistema.",
        "technical_reading": "ES muestra Robustness 86.17 frente a TSI 50.74 y PPC 71.56. No prueba una ley universal, pero si exige registrar que fitness predijo mejor el OOS.",
    },
    "151": {
        "visual_type": "performance_report",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Performance Summary de TradeStation; evidencia de revision visual y metrica final posterior a mapas.",
        "technical_reading": "El reporte permite revisar net profit, PF, trades, win rate, average trade y extremos. Es fase de seleccion humana, no sustituto de mapas.",
    },
    "158": {
        "visual_type": "optimization_table",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "critical",
        "requires_human_review": True,
        "notes": "Tabla que muestra diferencias de 20-27 trades por incremento; base directa de la regla de granularidad.",
        "technical_reading": "Con el resto de inputs constante, un paso de Var_01 produce cambios demasiado altos en numero de trades. La clase propone reducir incremento.",
    },
    "163": {
        "visual_type": "optimization_heatmap",
        "contains_numbers": True,
        "contains_chart": False,
        "doctrine_relevance": "high",
        "requires_human_review": True,
        "notes": "Mapa Per_01 vs Var_01 usado para revisar saltos y continuidad de incrementos.",
        "technical_reading": "La distribucion por filas y columnas ayuda a ver si el incremento actual crea escalones demasiado bruscos o zonas artificiales.",
    },
}


def find_section_for_line(line_no: int, sections: list[dict]) -> str:
    for sec in sections:
        if sec["line_start"] <= line_no <= sec["line_end"]:
            return sec["section_id"]
    raise ValueError(f"No section for line {line_no}")


def normalize_ref(ref: str) -> str:
    return ref.strip().split("#", 1)[0].split("?", 1)[0]


def resolve_image_ref(ref: str) -> Path:
    clean = normalize_ref(ref)
    rel = Path(clean.replace("/", "\\"))
    candidates = [
        (SRC_MD.parent / rel).resolve(),
        (SERSAN_ROOT / rel).resolve(),
        (SERSAN_ROOT / IMAGE_DIR_REL / rel.name).resolve(),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def build_sections(lines: list[str]) -> list[dict]:
    sections = []
    last_end = 0
    for raw in RAW_SECTIONS:
        if raw["line_start"] != last_end + 1:
            raise ValueError(f"Non-contiguous section at {raw['n']}")
        if raw["line_end"] > len(lines):
            raise ValueError(f"Section {raw['n']} exceeds md length {len(lines)}")
        text = "\n".join(lines[raw["line_start"] - 1 : raw["line_end"]])
        rec = {
            "contract_version": "sersan_lesson_sections_v0_1",
            "lesson_id": LESSON_ID,
            "section_id": section_id(raw["n"]),
            "heading_path": raw["heading_path"],
            "section_type": raw["section_type"],
            "line_start": raw["line_start"],
            "line_end": raw["line_end"],
            "raw_text_hash": sha256_text(text),
            "summary": raw["summary"],
            "keywords": raw["keywords"],
            "nearby_image_ids": [],
            "contains_code": raw["contains_code"],
            "contains_table": raw["contains_table"],
            "contains_question": raw["contains_question"],
            "requires_image_reading": raw["requires_image_reading"],
            "requires_human_review": raw["requires_human_review"],
            "notes": raw["notes"],
        }
        sections.append(rec)
        last_end = raw["line_end"]
    if last_end != len(lines):
        raise ValueError(f"Sections cover {last_end} lines, md has {len(lines)}")
    return sections


def build_image_records(lines: list[str], sections: list[dict]) -> list[dict]:
    md_pattern = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
    html_pattern = re.compile(r"<img\s+[^>]*src=[\"']([^\"']+)[\"']", re.IGNORECASE)
    records = []
    occurrence_by_stem = {}
    for line_no, line in enumerate(lines, start=1):
        refs = []
        for pattern in (md_pattern, html_pattern):
            refs.extend((match.start(), match.group(1)) for match in pattern.finditer(line))
        for _, ref in sorted(refs, key=lambda item: item[0]):
            resolved = resolve_image_ref(ref)
            stem = resolved.stem
            occurrence_by_stem[stem] = occurrence_by_stem.get(stem, 0) + 1
            img_id = image_id(stem, occurrence_by_stem[stem])
            sec_id = find_section_for_line(line_no, sections)
            override = IMAGE_OVERRIDES.get(stem, {})
            relevance = override.get("doctrine_relevance", "low")
            note_ref = ""
            if relevance != "low":
                note_ref = f"image_evidence_notes/{img_id}.md"
            rec = {
                "contract_version": "sersan_image_evidence_index_v0_1",
                "lesson_id": LESSON_ID,
                "image_id": img_id,
                "source_ref": ref,
                "resolved_path": sersan_rel(resolved) if resolved.exists() else "",
                "resolution_status": "resolved_direct" if resolved.exists() else "missing",
                "referenced_from_section_ids": sec_id,
                "visual_type": override.get("visual_type", "screenshot_or_slide"),
                "contains_numbers": override.get("contains_numbers", False),
                "contains_code": override.get("contains_code", False),
                "contains_chart": override.get("contains_chart", False),
                "contains_platform_config": override.get("contains_platform_config", False),
                "extracted_values_ref": note_ref,
                "technical_reading_ref": note_ref,
                "doctrine_relevance": relevance,
                "requires_human_review": override.get("requires_human_review", False),
                "notes": override.get(
                    "notes",
                    "Imagen indexada estructuralmente; no se promueve como evidencia doctrinal en este piloto.",
                ),
                "_line_no": line_no,
                "_path": resolved,
                "_technical_reading": override.get("technical_reading", ""),
            }
            records.append(rec)

    by_section = {sec["section_id"]: [] for sec in sections}
    for rec in records:
        by_section[rec["referenced_from_section_ids"]].append(rec["image_id"])
    for sec in sections:
        sec["nearby_image_ids"] = by_section.get(sec["section_id"], [])
    return records


def image_md_path(stem: str) -> str:
    ext = ".jpg" if stem == "098" else ".png"
    return f"../../../../99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/19-practice-09/img/{stem}{ext}"


def write_sections(sections: list[dict]):
    path = OUT_DIR / "lesson_sections.jsonl"
    rows = [json.dumps(sec, ensure_ascii=False) for sec in sections]
    write_text(path, "\n".join(rows) + "\n")


def write_image_index(image_records: list[dict]):
    path = OUT_DIR / "image_evidence_index.csv"
    fieldnames = [
        "contract_version",
        "lesson_id",
        "image_id",
        "source_ref",
        "resolved_path",
        "resolution_status",
        "referenced_from_section_ids",
        "visual_type",
        "contains_numbers",
        "contains_code",
        "contains_chart",
        "contains_platform_config",
        "extracted_values_ref",
        "technical_reading_ref",
        "doctrine_relevance",
        "requires_human_review",
        "notes",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in image_records:
            row = {key: rec[key] for key in fieldnames}
            writer.writerow(row)


def write_image_notes(image_records: list[dict]):
    notes_dir = OUT_DIR / "image_evidence_notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    for old in notes_dir.glob("*.md"):
        old.unlink()
    for rec in image_records:
        if rec["doctrine_relevance"] == "low":
            continue
        body = f"""# Image Evidence Note: {rec['image_id']}

Lesson: `{LESSON_ID}`
Source reference: `{rec['source_ref']}`
Resolved path: `{rec['resolved_path']}`
Source line: {rec['_line_no']}
Section: `{rec['referenced_from_section_ids']}`
Doctrine relevance: `{rec['doctrine_relevance']}`
Requires human review: `{str(rec['requires_human_review']).lower()}`

## Technical Reading

{rec['_technical_reading']}

## Harness Implication

{rec['notes']}

## Status

Candidate evidence for Sersan distillation. This note is not canonical TSIS
doctrine until reviewed and promoted.
"""
        write_text(OUT_DIR / rec["technical_reading_ref"], body)


RULES = [
    {
        "n": 1,
        "confidence": "high",
        "rule_type": "hard_rule",
        "domains": ["optimization_scope", "research_protocol"],
        "statement": "Do not optimize every input; split fixed money-management inputs, known constants and true research variables before running the optimizer.",
        "trigger": "Preparing an optimization map for a strategy revision.",
        "action": "Declare which inputs are fixed, which are inherited from prior study and which are allowed to vary.",
        "failure_mode_if_ignored": "The optimizer can fit implementation details or money-management artifacts instead of strategy mechanics.",
        "required_evidence": ["input_scope_table", "fixed_parameter_rationale", "optimizable_variable_list"],
        "source_anchors": [source_anchor(5, 393, 643, [])],
        "caveats": ["Candidate extracted from Sersan practice 09; not promoted to canonical doctrine."],
        "related_rules": [],
    },
    {
        "n": 2,
        "confidence": "high",
        "rule_type": "hard_rule",
        "domains": ["execution_realism", "optimizer_safety"],
        "statement": "If a backtest benefits from a known non-executable fill or halt artifact, encode a penalty before optimization.",
        "trigger": "A historical execution anomaly improves the backtest but could not have been traded in real time.",
        "action": "Add an explicit penalty input or correction so the optimizer cannot select the artificial benefit.",
        "failure_mode_if_ignored": "AlphaEvolve or a human optimizer may select a strategy because of impossible execution alpha.",
        "required_evidence": ["anomaly_case", "penalty_value", "before_after_performance"],
        "source_anchors": [source_anchor(5, 497, 573, [f"{LESSON_ID}_img_020"])],
        "caveats": ["The exact penalty must be justified per instrument and event."],
        "related_rules": [],
    },
    {
        "n": 3,
        "confidence": "high",
        "rule_type": "hard_rule",
        "domains": ["overoptimization", "selection_protocol"],
        "statement": "Use the 8000 best in-sample combinations to build maps, not to choose the final parameter set directly.",
        "trigger": "The platform exports a large ranked list of best IS optimization candidates.",
        "action": "Treat the list as map material, filter robust zones, then rerun a bounded exhaustive search with a much smaller final candidate set.",
        "failure_mode_if_ignored": "Final selection is dominated by in-sample ranking bias.",
        "required_evidence": ["map_from_large_sample", "bounded_zone_definition", "reduced_candidate_set"],
        "source_anchors": [source_anchor(10, 1686, 1719, [f"{LESSON_ID}_img_126"])],
        "caveats": ["The number 8000 is platform/context-specific; the principle is selection-pressure control."],
        "related_rules": [],
    },
    {
        "n": 4,
        "confidence": "high",
        "rule_type": "heuristic",
        "domains": ["optimization_map", "visual_validation"],
        "statement": "Prefer pivot-table heatmaps over 3D surfaces when reading optimization zones.",
        "trigger": "A parameter map is visualized for zone selection.",
        "action": "Use 2D heatmaps/tables as primary evidence and treat 3D surfaces as auxiliary only after checking scale.",
        "failure_mode_if_ignored": "Visual scale can exaggerate peaks or hide cliffs.",
        "required_evidence": ["heatmap", "scale_check"],
        "source_anchors": [source_anchor(6, 644, 744, [f"{LESSON_ID}_img_038", f"{LESSON_ID}_img_040"])],
        "caveats": ["3D can remain useful as orientation, not as final proof."],
        "related_rules": [],
    },
    {
        "n": 5,
        "confidence": "high",
        "rule_type": "hard_rule",
        "domains": ["robustness", "parameter_selection"],
        "statement": "Select parameter zones with neighbor support, not isolated best cells.",
        "trigger": "Choosing candidate parameters from an optimization map.",
        "action": "Require neighboring values to preserve acceptable behavior and reject cliff-like optima.",
        "failure_mode_if_ignored": "A single fragile optimum may be promoted as robust edge.",
        "required_evidence": ["neighbor_cells", "zone_continuity", "cliff_detection"],
        "source_anchors": [source_anchor(6, 744, 1056, [f"{LESSON_ID}_img_049", f"{LESSON_ID}_img_066"])],
        "caveats": ["Acceptable neighbor degradation must be calibrated by system family."],
        "related_rules": [],
    },
    {
        "n": 6,
        "confidence": "high",
        "rule_type": "hard_rule",
        "domains": ["parameter_range", "optimizer_safety"],
        "statement": "When an apparent optimum touches the edge of the tested range, extend the range before closing the selection.",
        "trigger": "Best candidates cluster at the minimum or maximum value tested.",
        "action": "Rerun or inspect an expanded range to determine whether the edge is artificial.",
        "failure_mode_if_ignored": "The chosen set may be a truncated optimum or an unexamined cliff.",
        "required_evidence": ["boundary_cluster", "expanded_range_result"],
        "source_anchors": [source_anchor(9, 1378, 1685, [f"{LESSON_ID}_img_111"])],
        "caveats": ["Expansion should stay economically and mechanically plausible."],
        "related_rules": [],
    },
    {
        "n": 7,
        "confidence": "high",
        "rule_type": "heuristic",
        "domains": ["robustness", "parameter_selection"],
        "statement": "Prefer a parameter value that works across many neighboring periods over a sharper local maximum.",
        "trigger": "Two candidate values compete, one with higher local score and another with broader map support.",
        "action": "Score tolerance and distribution across the map before final selection.",
        "failure_mode_if_ignored": "The process may choose a value that only works in a narrow pocket.",
        "required_evidence": ["distribution_map", "neighbor_score_profile"],
        "source_anchors": [source_anchor(8, 1223, 1377, [f"{LESSON_ID}_img_066", f"{LESSON_ID}_img_098"])],
        "caveats": ["A very broad but weak zone still needs absolute performance thresholds."],
        "related_rules": [],
    },
    {
        "n": 8,
        "confidence": "high",
        "rule_type": "hard_rule",
        "domains": ["fitness", "is_oos_validation"],
        "statement": "Compare candidate sets across IS, OOS and AllData using multiple normalized metrics, not a single fitness score.",
        "trigger": "Ranking candidates after an optimization pass.",
        "action": "Track TSI, expectancy, PPC and robustness, and document whether robustness is included in the combined score.",
        "failure_mode_if_ignored": "A candidate can be selected for one metric while failing stability or OOS behavior.",
        "required_evidence": ["IS_metrics", "OOS_metrics", "AllData_metrics", "normalization_method"],
        "source_anchors": [source_anchor(11, 1720, 1964, [f"{LESSON_ID}_img_127", f"{LESSON_ID}_img_142", f"{LESSON_ID}_img_143"])],
        "caveats": ["Metric weights are candidates for TSIS doctrine review."],
        "related_rules": [],
    },
    {
        "n": 9,
        "confidence": "high",
        "rule_type": "hard_rule",
        "domains": ["overoptimization", "selection_protocol"],
        "statement": "After map filtering, reduce the final decision universe to a bounded candidate set such as 250 before visual and portfolio review.",
        "trigger": "The robust zones have been defined and a final optimizer pass is required.",
        "action": "Run the bounded exhaustive optimization, save the reduced set and compare only that reduced set for final selection.",
        "failure_mode_if_ignored": "The final process still faces too many degrees of freedom and can overfit by choice.",
        "required_evidence": ["zone_bounds", "candidate_count", "reduced_optimization_manifest"],
        "source_anchors": [source_anchor(11, 1720, 1964, [f"{LESSON_ID}_img_142"])],
        "caveats": ["250 is extracted from the class case; TSIS may calibrate by strategy family."],
        "related_rules": [],
    },
    {
        "n": 10,
        "confidence": "high",
        "rule_type": "hard_rule",
        "domains": ["human_review", "performance_report"],
        "statement": "A final parameter set must pass Performance Report and equity-curve review after map validation.",
        "trigger": "Candidate sets survive the quantitative map and reduced optimization stages.",
        "action": "Inspect report metrics, equity behavior, drawdowns and trade distribution before promotion.",
        "failure_mode_if_ignored": "A map-valid set can still have unacceptable realized path behavior.",
        "required_evidence": ["performance_report", "equity_curve", "trade_distribution"],
        "source_anchors": [source_anchor(12, 1965, 2074, [f"{LESSON_ID}_img_151"])],
        "caveats": ["Visual review must not override hard risk limits."],
        "related_rules": [],
    },
    {
        "n": 11,
        "confidence": "medium",
        "rule_type": "process_rule",
        "domains": ["human_review", "bias_control"],
        "statement": "Reduce final-selection bias by reviewing reports without looking at parameter values and by comparing independent reviewer choices.",
        "trigger": "Humans visually compare candidate Performance Reports.",
        "action": "Hide parameter identities until after selection and record independent reviewer votes.",
        "failure_mode_if_ignored": "Reviewers may rationalize favored inputs instead of selecting behavior.",
        "required_evidence": ["blind_review_log", "reviewer_votes"],
        "source_anchors": [source_anchor(12, 1965, 2074, [])],
        "caveats": ["Operational feasibility depends on tooling around report export."],
        "related_rules": [],
    },
    {
        "n": 12,
        "confidence": "high",
        "rule_type": "hard_rule",
        "domains": ["portfolio", "strategy_selection"],
        "statement": "Final strategy selection must include portfolio contribution; the best standalone set is not necessarily the best portfolio set.",
        "trigger": "A strategy is intended for a multi-strategy client portfolio.",
        "action": "Evaluate correlation, diversification and portfolio-level risk/return before final deployment.",
        "failure_mode_if_ignored": "The portfolio can become more fragile even if the standalone strategy looks stronger.",
        "required_evidence": ["portfolio_correlation", "portfolio_drawdown", "allocation_effect"],
        "source_anchors": [source_anchor(12, 1965, 2074, []), source_anchor(16, 2340, 2400, [])],
        "caveats": ["Portfolio constraints may select a lower standalone score intentionally."],
        "related_rules": [],
    },
    {
        "n": 13,
        "confidence": "high",
        "rule_type": "hard_rule",
        "domains": ["parameter_granularity", "optimizer_safety"],
        "statement": "Validate optimization increment size by measuring how many trades change when a parameter moves one step.",
        "trigger": "A continuous parameter has an arbitrary optimization increment.",
        "action": "Compare adjacent rows with other inputs fixed; reduce increments that produce too-large trade-count jumps.",
        "failure_mode_if_ignored": "The optimizer may skip relevant regions or create artificial discontinuities.",
        "required_evidence": ["adjacent_parameter_rows", "trade_count_delta", "increment_rationale"],
        "source_anchors": [source_anchor(13, 2075, 2227, [f"{LESSON_ID}_img_064", f"{LESSON_ID}_img_158", f"{LESSON_ID}_img_163"])],
        "caveats": ["Acceptable trade-count delta depends on total trades and system frequency."],
        "related_rules": [],
    },
    {
        "n": 14,
        "confidence": "medium",
        "rule_type": "heuristic",
        "domains": ["recent_period_review", "sample_size"],
        "statement": "Optimize on all available history, but inspect recent-period behavior with a window appropriate to system frequency and trade count.",
        "trigger": "Final Performance Report comparison after full-history optimization.",
        "action": "For daily systems, review a recent period long enough to retain meaningful trades; for intraday, calibrate shorter windows by sample size.",
        "failure_mode_if_ignored": "The selected set may be dominated by old regimes or by too-small recent samples.",
        "required_evidence": ["full_history_report", "recent_window_report", "recent_trade_count"],
        "source_anchors": [source_anchor(14, 2228, 2289, [f"{LESSON_ID}_img_151"])],
        "caveats": ["The class suggests about 10 recent years for this daily case; not universal."],
        "related_rules": [],
    },
    {
        "n": 15,
        "confidence": "medium",
        "rule_type": "decision_rule",
        "domains": ["walk_forward", "validation_design"],
        "statement": "Do not force rolling Walk-Forward when the system structure, trade count and money-management distortion make the test misleading.",
        "trigger": "Considering WF for daily short-equity systems with few trades or money management embedded.",
        "action": "Test without money management when possible and consider anchored WF or alternative validation if rolling windows are too narrow.",
        "failure_mode_if_ignored": "A formally rigorous WF can reject or accept a system for artifacts unrelated to mechanics.",
        "required_evidence": ["trade_count_by_window", "MM_removed_variant", "validation_route_rationale"],
        "source_anchors": [source_anchor(15, 2290, 2339, [])],
        "caveats": ["This is a validation-design rule, not permission to skip OOS evidence."],
        "related_rules": [],
    },
    {
        "n": 16,
        "confidence": "high",
        "rule_type": "domain_rule",
        "domains": ["short_equity", "portfolio"],
        "statement": "Short-equity systems are primarily alpha/diversification tools and require faster exits than long-equity systems.",
        "trigger": "Designing or evaluating equity short strategies.",
        "action": "Favor quick exit logic, near take profits and portfolio-level justification; do not treat shorts as beginner smart-beta research.",
        "failure_mode_if_ignored": "The system may fight equity market drift without enough compensating alpha or diversification value.",
        "required_evidence": ["short_exit_profile", "portfolio_diversification_rationale", "holding_period_distribution"],
        "source_anchors": [source_anchor(3, 217, 304, []), source_anchor(16, 2340, 2400, [])],
        "caveats": ["Instrument universe and borrow/friction constraints must be added by TSIS before live use."],
        "related_rules": [],
    },
    {
        "n": 17,
        "confidence": "medium",
        "rule_type": "research_rule",
        "domains": ["fitness", "empirical_tracking"],
        "statement": "Track which fitness function best predicts OOS for each system family instead of assuming one universal fitness.",
        "trigger": "Multiple fitness functions rank candidates differently.",
        "action": "Record TSI, ES, PPC and robustness outcomes by lesson/system family and update family-level priors.",
        "failure_mode_if_ignored": "The research process may reuse a default fitness where another one is empirically more predictive.",
        "required_evidence": ["fitness_comparison", "OOS_predictivity_log"],
        "source_anchors": [source_anchor(11, 1720, 1964, [f"{LESSON_ID}_img_142", f"{LESSON_ID}_img_143"])],
        "caveats": ["Practice 09 suggests ES was strongest here; that is not global doctrine."],
        "related_rules": [],
    },
    {
        "n": 18,
        "confidence": "high",
        "rule_type": "hard_rule",
        "domains": ["filters", "overoptimization"],
        "statement": "A filter is researchable only when its type and parameter search are constrained before testing.",
        "trigger": "Adding filters to improve an already tested strategy.",
        "action": "Use standard/default filter parameters, compare before/after metrics and require enough affected trades.",
        "failure_mode_if_ignored": "The process can search hundreds of filters until a random in-sample improvement appears.",
        "required_evidence": ["filter_predefinition", "before_after_metrics", "affected_trade_count"],
        "source_anchors": [source_anchor(2, 20, 216, [])],
        "caveats": ["Exact significance thresholds remain an open TSIS doctrine item."],
        "related_rules": [],
    },
]


TRANSLATIONS = [
    (1, "research_protocol", "TSIS_OPTIMIZATION_INPUT_SCOPE_DECLARATION", "require", "critical", "hard_gate", "backtest|AlphaEvolve", "Require an input-scope manifest before any optimization run."),
    (2, "execution_realism_check", "TSIS_HALT_OR_NONEXECUTABLE_FILL_PENALTY_GATE", "block", "critical", "hard_gate", "backtest|AlphaEvolve", "Block or penalize candidates whose edge depends on non-executable event fills."),
    (3, "AlphaEvolve_constraint", "TSIS_NO_DIRECT_SELECTION_FROM_LARGE_IS_RANKING", "block", "critical", "hard_gate", "AlphaEvolve|backtest", "Forbid direct selection from broad IS ranking lists without zone reduction."),
    (4, "strategy_evaluator", "TSIS_OPTIMIZATION_MAP_HEATMAP_PRIMARY_REVIEW", "require", "high", "human_review_gate", "backtest|AlphaEvolve", "Require heatmap/pivot evidence for parameter-map interpretation."),
    (5, "strategy_evaluator", "TSIS_PARAMETER_ZONE_NEIGHBOR_VALIDATION", "require", "critical", "hard_gate", "backtest|AlphaEvolve", "Reject isolated peaks without neighbor support."),
    (6, "optimizer_runner", "TSIS_PARAMETER_BOUNDARY_EXTENSION_CHECK", "require", "high", "hard_gate", "backtest|AlphaEvolve", "Require extended-range check when optima touch tested boundaries."),
    (7, "strategy_evaluator", "TSIS_PARAMETER_TOLERANCE_SCORE", "document", "high", "soft_gate", "backtest|AlphaEvolve", "Score broad parameter support alongside local maxima."),
    (8, "strategy_evaluator", "TSIS_MULTI_METRIC_IS_OOS_COMPARISON", "require", "critical", "hard_gate", "backtest|AlphaEvolve", "Compare normalized TSI, ES, PPC and robustness across IS/OOS/AllData."),
    (9, "optimizer_runner", "TSIS_REDUCED_CANDIDATE_SET_AFTER_MAP_FILTER", "require", "critical", "hard_gate", "backtest|AlphaEvolve", "Require bounded candidate count after map filtering."),
    (10, "human_review_checklist", "TSIS_PERFORMANCE_REPORT_FINAL_REVIEW", "require", "high", "human_review_gate", "backtest", "Require report/equity/trade-list review after quantitative gates."),
    (11, "research_protocol", "TSIS_BLIND_PARAMETER_REPORT_REVIEW", "document", "medium", "soft_gate", "backtest", "Record whether parameter values were hidden during final human review."),
    (12, "portfolio_evaluator", "TSIS_PORTFOLIO_CONTRIBUTION_FINAL_GATE", "require", "critical", "human_review_gate", "portfolio|backtest", "Evaluate final candidate contribution to portfolio risk and diversification."),
    (13, "optimizer_runner", "TSIS_PARAMETER_INCREMENT_GRANULARITY_CHECK", "require", "critical", "hard_gate", "backtest|AlphaEvolve", "Measure adjacent-step trade-count deltas before accepting an optimization grid."),
    (14, "strategy_evaluator", "TSIS_RECENT_PERIOD_BEHAVIOR_REVIEW", "require", "medium", "human_review_gate", "backtest", "Review recent-period behavior with sample-size guardrails."),
    (15, "validation_design", "TSIS_WALK_FORWARD_ROUTE_RATIONALE", "document", "high", "human_review_gate", "backtest", "Require rationale for rolling WF, anchored WF or alternative validation route."),
    (16, "strategy_design", "TSIS_SHORT_EQUITY_EXIT_AND_PORTFOLIO_POLICY", "document", "high", "human_review_gate", "backtest|portfolio", "Document short-equity fast-exit and diversification rationale."),
    (17, "research_memory", "TSIS_FITNESS_PREDICTIVITY_TRACKER", "document", "medium", "soft_gate", "AlphaEvolve|backtest", "Track which fitness functions predict OOS by strategy family."),
    (18, "AlphaEvolve_constraint", "TSIS_FILTER_SEARCH_SPACE_CONSTRAINT", "block", "critical", "hard_gate", "AlphaEvolve|backtest", "Block unconstrained filter mining and require predeclared filter search space."),
]


OPEN_QUESTIONS = [
    "What exact trade-count delta threshold should TSIS use to label an increment too coarse by system frequency and total trades?",
    "How should TSIS formalize significance for filter before/after improvements when the filter removes both good and bad trades?",
    "Should Practice 09's 250-candidate reduction become a default, or should candidate count scale with parameter dimensionality?",
    "How should AlphaEvolve encode map-neighbor and zone-density constraints without reducing research creativity too early?",
    "Can the XLSX map be parsed into structured parameter surfaces, or should visual screenshots remain the first pilot source of truth?",
    "What portfolio-level metrics will decide when a weaker standalone set is superior for TSIS client portfolios?",
    "How should TSIS validate short-equity systems when borrow, liquidity, halts and locate constraints are added to small caps?",
    "When rolling Walk-Forward is rejected, what minimum alternative validation package is mandatory before deployment?",
]


def write_rules(generated_at: str):
    payload = {
        "contract_version": "sersan_mechanical_rules_v0_1",
        "lesson_id": LESSON_ID,
        "generated_at_utc": generated_at,
        "generated_by": "mechanical_rule_extractor_agent_v0_2",
        "rules": [],
    }
    for rule in RULES:
        rec = {
            "rule_id": rule_id(rule["n"]),
            "promotion_state": "mechanical_rule_candidate",
            "confidence": rule["confidence"],
            "rule_type": rule["rule_type"],
            "domains": rule["domains"],
            "statement": rule["statement"],
            "trigger": rule["trigger"],
            "action": rule["action"],
            "failure_mode_if_ignored": rule["failure_mode_if_ignored"],
            "required_evidence": rule["required_evidence"],
            "source_anchors": rule["source_anchors"],
            "caveats": rule["caveats"],
            "related_rules": rule["related_rules"],
        }
        payload["rules"].append(rec)
    write_text(OUT_DIR / "mechanical_rules.yaml", yaml_dump(payload) + "\n")


def write_translation_map():
    path = OUT_DIR / "tsis_translation_map.csv"
    fieldnames = [
        "contract_version",
        "lesson_id",
        "translation_id",
        "rule_id",
        "target",
        "tsis_artifact_candidate",
        "action_type",
        "priority",
        "blocking_power",
        "consumer_scope",
        "implementation_hint",
        "requires_human_review",
        "source_anchor_refs",
        "notes",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for idx, target, artifact, action, priority, blocking, scope, hint in TRANSLATIONS:
            writer.writerow(
                {
                    "contract_version": "sersan_tsis_translation_map_v0_1",
                    "lesson_id": LESSON_ID,
                    "translation_id": translation_id(idx),
                    "rule_id": rule_id(idx),
                    "target": target,
                    "tsis_artifact_candidate": artifact,
                    "action_type": action,
                    "priority": priority,
                    "blocking_power": blocking,
                    "consumer_scope": scope,
                    "implementation_hint": hint,
                    "requires_human_review": str(priority in {"critical", "high"}).lower(),
                    "source_anchor_refs": rule_id(idx),
                    "notes": "Candidate mapping; requires doctrine review before implementation.",
                }
            )


def write_open_questions():
    lines = [f"# Open Questions: {LESSON_ID}", ""]
    for idx, question in enumerate(OPEN_QUESTIONS, start=1):
        lines.append(f"{idx}. {question}")
    lines.append("")
    write_text(OUT_DIR / "open_questions.md", "\n".join(lines))


def write_lesson_distillation(sections: list[dict]):
    table_rows = []
    for sec in sections:
        short_id = sec["section_id"].replace(f"{LESSON_ID}_", "")
        table_rows.append(
            f"| `{short_id}` | {sec['line_start']}-{sec['line_end']} | {sec['section_type']} | {sec['summary']} |"
        )

    rules_summary = "\n".join(
        f"{idx}. {rule['statement']}" for idx, rule in enumerate(RULES, start=1)
    )
    translation_summary = "\n".join(
        f"- `{artifact}` -> {hint}" for _, _, artifact, _, _, _, _, hint in TRANSLATIONS
    )

    body = f"""# Lesson Distillation: {LESSON_ID}

Fecha: {DATE}
Estado: pilot v0.2, `pass_with_warnings`
Fuente: `03_only_md_revised/practica_09_revision_apolo.md`

## 1. Proposito del paquete

Este paquete destila la revision de Apolo como segundo piloto del Sersan
Distillation Harness. La practica es mas importante que `practice_02` para el
Harness de optimizacion porque muestra un proceso completo de revision:
preparar datos y costes, controlar ejecucion no realista, construir mapas,
filtrar zonas, reducir el universo de seleccion, revisar Performance Reports,
validar incrementos y decidir si Walk-Forward encaja con la estructura del
sistema.

El objetivo no es promocionar Apolo como estrategia TSIS. El objetivo es
extraer la mecanica que los agentes deben aplicar cuando auditen o generen
estrategias con AlphaEvolve.

## 2. Lectura ejecutiva

La tesis central de la clase es que la optimizacion no es elegir el mejor
numero de una tabla. Es un protocolo de control de grados de libertad.

La ruta mecanica queda asi:

1. Declarar que inputs se pueden optimizar y cuales quedan fijos.
2. Penalizar eventos no ejecutables antes de permitir que el optimizador los
   explote.
3. Usar las 8000 mejores combinaciones como materia prima para mapas, no como
   lista de seleccion final.
4. Leer mapas por zonas, vecinos, bordes y cliffs.
5. Reducir el espacio a una optimizacion acotada, por ejemplo 250 candidatos.
6. Comparar IS, OOS y AllData con varias metricas.
7. Revisar Performance Reports y curvas sin dejar que el nombre del parametro
   sesgue al revisor.
8. Validar que el incremento de cada parametro no es demasiado fino ni
   demasiado grueso.
9. Llevar la seleccion final a portfolio si la estrategia se operara dentro de
   una cartera.

## 3. Secciones fuente

| Section | Lines | Tipo | Lectura |
|---|---:|---|---|
{chr(10).join(table_rows)}

## 4. Evidencia visual incrustada

### 4.1 Ejecucion no realista y penalizacion

![Halt o fill no ejecutable]({image_md_path("020")})

La captura marca el caso de COVID/halt donde el backtest habria contado un
beneficio que no era ejecutable. La clase no lo deja como comentario: lo
convierte en un input de penalizacion (`puntosErrorTradeporHalt`). Para TSIS,
esta es una regla dura de realismo de ejecucion.

### 4.2 Mapas como herramienta de descarte y zona

![Mapa Per_01 vs Var_01]({image_md_path("038")})

![Tabla dinamica frente a superficie 3D]({image_md_path("040")})

El mapa se usa para descubrir zonas y fragilidad. La superficie 3D puede ayudar
a orientarse, pero la tabla dinamica es la lectura primaria porque permite ver
vecinos, huecos, totales y degradacion.

### 4.3 Robustez de parametros: maximo local frente a todoterreno

![Zona Per_01 vs Var_01]({image_md_path("066")})

![Mapa filtrado de zona robusta]({image_md_path("098")})

La comparacion entre valores como `0.575` y `0.600` no se resuelve solo por
quien gana en una celda. La robustez se lee por distribucion. Un valor que
funciona aceptablemente en mas zonas puede ser preferible a un maximo mas
brillante pero estrecho.

### 4.4 Fronteras e incrementos

![Extension de rango Per_01]({image_md_path("111")})

Cuando un optimo toca el borde del rango, el rango se amplia. Si no se amplia,
no sabemos si el supuesto optimo es real o solo una frontera artificial.

![Granularidad de incremento]({image_md_path("158")})

La revision de incrementos compara filas con el resto de inputs constante. Si
un paso de parametro cambia 20-27 trades en una muestra de unas 600-800
operaciones, la clase lo trata como senal de incremento demasiado grueso.

### 4.5 De 8000 combinaciones a 250 candidatos

![Ranking amplio de combinaciones]({image_md_path("126")})

Esta tabla no es el final del proceso. Es una advertencia: dejar elegir entre
8000 combinaciones es sobreoptimizar. La seleccion debe venir despues de
mapas, zonas y recorte.

![Optimizacion recortada y fitness]({image_md_path("142")})

La ficha recortada guarda 250 candidatos y compara TSI, ES, PPC y Robustness.
En este caso, ES parece tener mejor capacidad predictiva OOS que TSI o PPC,
pero el Harness debe registrarlo como evidencia por familia de sistema, no
como ley universal.

### 4.6 Performance Report y revision humana

![Performance Summary]({image_md_path("151")})

Los Performance Reports entran al final, no al principio. Sirven para revisar
trayectoria, drawdown, profit factor, trades, average trade y extremos. La
clase recomienda reducir sesgos revisando informes sin mirar parametros y
comparando revisiones independientes.

## 5. Reglas mecanicas candidatas

La extraccion completa esta en `mechanical_rules.yaml`. Las reglas principales
son:

{rules_summary}

## 6. Traduccion TSIS

La traduccion completa esta en `tsis_translation_map.csv`. Las piezas mas
importantes para TSIS son:

{translation_summary}

## 7. Lo que no debe promocionarse todavia

No se debe promocionar que los parametros concretos de Apolo sean doctrina
TSIS.

No se debe promocionar que ES sea siempre mejor que TSI o PPC. En esta practica
parece comportarse mejor para OOS, pero eso debe alimentar memoria empirica por
familia de sistema.

No se debe convertir el numero 250 en dogma sin calibrarlo. Es una buena regla
piloto para controlar grados de libertad, pero TSIS debe decidir si escala por
dimension del espacio, frecuencia, numero de trades o tipo de estrategia.

No se debe trasladar sin mas la logica de short equity a small caps live hasta
anadir borrow, liquidez, halts, spreads, delistings y reglas de localizacion.

## 8. Mejora del Harness frente al piloto 02

Este segundo piloto obliga al Harness a manejar una clase de alta densidad
visual. A partir de aqui, el Harness Sersan necesita tres capacidades que en
`practice_02` aun no eran tan exigentes:

- indexar muchas imagenes y promover solo las que sostienen doctrina;
- distinguir ranking, mapa, reporte y estadistica descriptiva como evidencias
  distintas;
- generar reglas de control del optimizador que puedan convertirse en
  constraints de AlphaEvolve.

## 9. Consumidores previstos

- Sersan Distillation Harness: contrato de lectura visual y reglas candidatas.
- Backtest Harness: gates de optimizacion, incrementos, IS/OOS y reportes.
- AlphaEvolve: constraints contra busqueda libre, overfit, rankings IS y
  parametros sin vecinos.
- Portfolio Harness futuro: evaluacion de contribucion y descorrelacion.
- Data Quality Harness: realismo de ejecucion ante halts y discontinuidades.

## 10. Estado

`pass_with_warnings`

Este paquete esta listo como segundo piloto comparativo. Requiere revision
humana antes de promocionar reglas a doctrina canonica TSIS.
"""
    write_text(OUT_DIR / "lesson_distillation.md", body)


def write_quality_report(lines, sections, image_records):
    images_read = [r for r in image_records if r["doctrine_relevance"] != "low"]
    missing = [r for r in image_records if r["resolution_status"] != "resolved_direct"]
    body = f"""# Quality Report: {LESSON_ID}

## 1. Summary

| Metric | Value |
|---|---:|
| lesson_id | {LESSON_ID} |
| status | translated |
| md_lines | {len(lines)} |
| sections | {len(sections)} |
| image_refs_total | {len(image_records)} |
| images_resolved | {len(image_records) - len(missing)} |
| images_missing | {len(missing)} |
| images_read | {len(images_read)} |
| rules_extracted | {len(RULES)} |
| translations_created | {len(TRANSLATIONS)} |
| open_questions | {len(OPEN_QUESTIONS)} |
| blocking_issues | 0 |

## 2. Input Coverage

The complete markdown was sectionized from line 1 to line {len(lines)}. The
EasyLanguage artifact and XLSX map are inventoried as associated artifacts but
are not parsed deeply in this pilot. PDFs remain duplicate layout artifacts and
subtitles/video are out of scope per project instruction.

## 3. Asset Resolution

All {len(image_records)} image references resolve to local files under
`02_workshops/19-practice-09/img`. Duplicated references are preserved as
separate indexed references for traceability.

## 4. Sectionization Quality

The source has meaningful headings but several long teaching segments. The
pilot uses semantic line ranges that are non-overlapping and cover the whole
file.

## 5. Image Reading Quality

All images are indexed. Images with `medium`, `high` or `critical` relevance
have notes in `image_evidence_notes/`. Low-relevance images are structurally
indexed but not individually OCR-read.

## 6. Mechanical Rule Quality

All rules in `mechanical_rules.yaml` include trigger, action, failure mode and
source anchors. No rule is marked `promoted`.

## 7. TSIS Translation Quality

Each rule has one translation candidate in `tsis_translation_map.csv`. Critical
and high-priority gates require human review before implementation.

## 8. Open Questions

Eight open questions are tracked in `open_questions.md`, mainly around
increment thresholds, filter significance, candidate-count scaling, portfolio
selection and validation alternatives.

## 9. Blocking Issues

None.

## 10. Acceptance Decision

`pass_with_warnings`

Warnings:

- The XLSX map is inventoried but not parsed into structured surfaces.
- Low-relevance images are not individually OCR-read.
- Short-equity live translation needs borrow, liquidity, halts and small-cap
  execution constraints before operational use.
- Candidate rules require human doctrine review before promotion.
"""
    write_text(OUT_DIR / "quality_report.md", body)


def write_manifest(generated_at, lines, image_records):
    missing = [r for r in image_records if r["resolution_status"] != "resolved_direct"]
    images_read = [r for r in image_records if r["doctrine_relevance"] != "low"]
    generator_path = ROOT / GENERATOR_REL
    manifest = {
        "contract_version": CONTRACT_VERSION,
        "generated_at_utc": generated_at,
        "generated_by": GENERATED_BY,
        "lesson_id": LESSON_ID,
        "practice_number": 9,
        "title": "Practice 9 - Revision de Apolo",
        "status": "translated",
        "source_md": rel_posix(SRC_MD_REL),
        "workshop_dir": rel_posix(WORKSHOP_REL),
        "image_dir": rel_posix(IMAGE_DIR_REL),
        "pdf_role": "duplicate_md_or_layout_artifact",
        "video_role": "out_of_scope",
        "asset_resolution": {
            "resolver_version": "lesson_pack_resolver_v0_2",
            "image_refs_total": len(image_records),
            "resolved_direct": len(image_records) - len(missing),
            "resolved_lesson_fallback": 0,
            "external_reference": 0,
            "missing": len(missing),
            "needs_human_review": len([r for r in image_records if r["requires_human_review"]]),
        },
        "source_hashes": {
            rel_posix(SRC_MD_REL): sha256_file(SRC_MD),
            GENERATOR_REL: sha256_file(generator_path),
        },
        "counts": {
            "md_lines": len(lines),
            "sections": len(RAW_SECTIONS),
            "images": len(image_records),
            "images_read": len(images_read),
            "code_artifacts": 1 if (SERSAN_ROOT / CODE_REL).exists() else 0,
            "xlsx_artifacts": 1 if (SERSAN_ROOT / XLSX_REL).exists() else 0,
            "rules": len(RULES),
            "translations": len(TRANSLATIONS),
            "open_questions": len(OPEN_QUESTIONS),
        },
        "known_issues": [
            "Segundo piloto; requiere revision humana antes de promocion canonica.",
            "XLSX map inventoried but not parsed into structured surfaces.",
            "Code artifact inventoried but not parsed in this pilot.",
            "Low-relevance images indexed structurally without full OCR.",
        ],
    }
    write_text(OUT_DIR / "lesson_pack_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def directory_hash(path: Path) -> str:
    hashes = []
    for file in sorted(path.glob("*.md")):
        hashes.append(f"{file.name}:{sha256_file(file)}")
    return sha256_text("\n".join(hashes))


def write_run_manifest(generated_at, image_records):
    selected_by_path = {}
    for rec in image_records:
        if rec["doctrine_relevance"] == "low":
            continue
        selected_by_path.setdefault(rec["_path"], rec)

    input_artifacts = [
        {"path": project_rel(SRC_MD), "sha256": sha256_file(SRC_MD)},
        {"path": TOOLCHAIN_CONTRACT_REL, "sha256": sha256_file(ROOT / TOOLCHAIN_CONTRACT_REL), "role": "governing_contract"},
        {"path": SHARED_MANIFEST_REL, "sha256": sha256_file(ROOT / SHARED_MANIFEST_REL), "role": "shared_manifest_contract"},
        {"path": SHARED_VALIDATION_REL, "sha256": sha256_file(ROOT / SHARED_VALIDATION_REL), "role": "shared_validation_principles"},
        {"path": ARTIFACT_CONTRACT_REL, "sha256": sha256_file(ROOT / ARTIFACT_CONTRACT_REL), "role": "artifact_contract"},
        {"path": RUNBOOK_REL, "sha256": sha256_file(ROOT / RUNBOOK_REL), "role": "runbook"},
    ]
    for rel, role in [(CODE_REL, "code_artifact"), (XLSX_REL, "xlsx_artifact")]:
        artifact = SERSAN_ROOT / rel
        if artifact.exists():
            input_artifacts.append({"path": project_rel(artifact), "sha256": sha256_file(artifact), "role": role})
    for path, rec in sorted(selected_by_path.items(), key=lambda item: item[1]["image_id"]):
        input_artifacts.append(
            {
                "path": project_rel(path),
                "sha256": sha256_file(path),
                "role": "image_evidence",
                "image_id": rec["image_id"],
                "doctrine_relevance": rec["doctrine_relevance"],
            }
        )

    output_files = [
        "lesson_pack_manifest.json",
        "lesson_sections.jsonl",
        "image_evidence_index.csv",
        "mechanical_rules.yaml",
        "lesson_distillation.md",
        "tsis_translation_map.csv",
        "open_questions.md",
        "quality_report.md",
    ]
    output_artifacts = []
    for name in output_files:
        p = OUT_DIR / name
        output_artifacts.append({"path": project_rel(p), "sha256": sha256_file(p)})
    output_artifacts.append(
        {
            "path": project_rel(OUT_DIR / "image_evidence_notes"),
            "sha256": directory_hash(OUT_DIR / "image_evidence_notes"),
            "role": "directory_aggregate",
        }
    )

    run_manifest = {
        "run_id": "2026-06-12_sersan_practice_09_revision_apolo_pilot_run_v0_2",
        "lesson_id": LESSON_ID,
        "generated_at_utc": generated_at,
        "generated_by": GENERATED_BY,
        "mode": "pilot",
        "status": "pass_with_warnings",
        "contract_version": CONTRACT_VERSION,
        "toolchain_traceability_contract": TOOLCHAIN_CONTRACT_REL,
        "runbook": RUNBOOK_REL,
        "artifact_contract": ARTIFACT_CONTRACT_REL,
        "execution_command": f"python {GENERATOR_REL}",
        "toolchain_artifacts": [
            {
                "tool_id": "generate_sersan_p09_pilot",
                "role": "generator",
                "project_relative_path": GENERATOR_REL,
                "sha256": sha256_file(ROOT / GENERATOR_REL),
                "runtime": "python",
                "project_resident": True,
            }
        ],
        "input_artifacts": input_artifacts,
        "output_artifacts": output_artifacts,
        "non_project_artifacts_used": [],
        "human_review_required": True,
        "warnings": [
            "XLSX map is inventoried but not parsed into structured surfaces.",
            "Low-relevance images are structurally indexed without full OCR.",
            "Candidate rules are not promoted doctrine.",
        ],
    }
    write_text(OUT_DIR / "run_manifest.json", json.dumps(run_manifest, ensure_ascii=False, indent=2) + "\n")


def validate_outputs(image_records):
    expected = [
        "lesson_pack_manifest.json",
        "lesson_sections.jsonl",
        "image_evidence_index.csv",
        "mechanical_rules.yaml",
        "lesson_distillation.md",
        "tsis_translation_map.csv",
        "open_questions.md",
        "quality_report.md",
        "run_manifest.json",
    ]
    for name in expected:
        p = OUT_DIR / name
        if not p.exists():
            raise FileNotFoundError(p)
        text = p.read_text(encoding="utf-8")
        if "C:\\Users" in text or "C:\\tmp" in text:
            raise ValueError(f"Non-project path leaked into {name}")

    unresolved = [r for r in image_records if r["resolution_status"] != "resolved_direct"]
    if unresolved:
        raise ValueError(f"Unresolved images: {len(unresolved)}")
    for rec in image_records:
        if rec["doctrine_relevance"] != "low" and not (OUT_DIR / rec["technical_reading_ref"]).exists():
            raise FileNotFoundError(rec["technical_reading_ref"])


def main():
    if not SRC_MD.exists():
        raise FileNotFoundError(SRC_MD)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = SRC_MD.read_text(encoding="utf-8").splitlines()
    sections = build_sections(lines)
    image_records = build_image_records(lines, sections)

    write_sections(sections)
    write_image_index(image_records)
    write_image_notes(image_records)
    write_rules(generated_at)
    write_translation_map()
    write_open_questions()
    write_lesson_distillation(sections)
    write_quality_report(lines, sections, image_records)
    write_manifest(generated_at, lines, image_records)
    write_run_manifest(generated_at, image_records)
    validate_outputs(image_records)

    summary = {
        "lesson_id": LESSON_ID,
        "status": "pass_with_warnings",
        "sections": len(sections),
        "image_refs": len(image_records),
        "images_read": len([r for r in image_records if r["doctrine_relevance"] != "low"]),
        "rules": len(RULES),
        "translations": len(TRANSLATIONS),
        "out_dir": str(OUT_DIR),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
