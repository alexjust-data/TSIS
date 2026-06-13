from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(r"C:\TSIS_Data")
CTO = ROOT / "00_CTO"
SERSAN_ROOT = CTO / "99_REFERENCE_LIBRARY" / "SersanSistemas"
SRC_MD_REL = Path("03_only_md_revised") / "practica_15_revised.md"
SRC_MD = SERSAN_ROOT / SRC_MD_REL
WORKSHOP_REL = Path("02_workshops") / "25-practice-15"
IMAGE_DIR_REL = WORKSHOP_REL / "img"
CODE_RELS = [
    WORKSHOP_REL / "code" / "10-CURSO-RISKMSA.tsw",
    WORKSHOP_REL / "code" / "BUSCADOR E_S.ELD",
    WORKSHOP_REL / "code" / "PRACTICA 15.ELD",
    WORKSHOP_REL / "code" / "RISKMSA.ELD",
]

COG = CTO / "12_TSIS_COGNITIVE_ARCHITECTURE"
SHARED_KERNEL = COG / "00_SHARED_HARNESS_KERNEL"
SERSAN_HARNESS = COG / "20_SERSAN_DISTILLATION_HARNESS"
OUT_DIR = SERSAN_HARNESS / "sersan_distillation_artifacts" / "sersan_practice_15_revised"

LESSON_ID = "sersan_practice_15_revised"
DATE = "2026-06-12"
GENERATED_BY = "manual_sersan_pilot_harness_codex_v0_3"
CONTRACT_VERSION = "sersan_lesson_pack_contract_v0_1"
GENERATOR_REL = (
    "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/"
    "harness_toolchain/sersan_distillation/generate_sersan_p15_pilot.py"
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


def sanitize_stem(stem: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_")
    return clean or "image"


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
            if isinstance(item, (dict, list)):
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


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


RAW_SECTIONS = [
    {
        "n": 1,
        "heading_path": ["Practice 15", "Entrada e indice"],
        "section_type": "structure",
        "line_start": 1,
        "line_end": 10,
        "summary": "Portada e indice de la practica de Money Management y Position Sizing.",
        "keywords": ["practice-15", "money-management", "position-sizing"],
        "contains_code": False,
        "contains_table": False,
        "contains_question": False,
        "requires_image_reading": False,
        "requires_human_review": False,
        "notes": ["Seccion estructural; no se promociona como doctrina mecanica."],
    },
    {
        "n": 2,
        "heading_path": ["Practice 15", "Consultas", "Stops incorporados y stops manuales"],
        "section_type": "qa",
        "line_start": 11,
        "line_end": 58,
        "summary": "Aclara cuando usar stops incorporados de EasyLanguage y cuando construir salidas manuales por lado.",
        "keywords": ["SetStopLoss", "SetProfitTarget", "MarketPosition", "entry-bar-protection"],
        "contains_code": True,
        "contains_table": False,
        "contains_question": True,
        "requires_image_reading": False,
        "requires_human_review": False,
        "notes": [],
    },
    {
        "n": 3,
        "heading_path": ["Practice 15", "Consultas", "Intradias, filtros y muestra long-short"],
        "section_type": "qa",
        "line_start": 59,
        "line_end": 109,
        "summary": "Trata intradia mean reversion, filtros, estructuras de precio y lectura de muestras long/short.",
        "keywords": ["intraday", "mean-reversion", "filters", "sample-size", "long-short"],
        "contains_code": False,
        "contains_table": False,
        "contains_question": True,
        "requires_image_reading": False,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 4,
        "heading_path": ["Practice 15", "Consultas", "Costes, swaps, futuros y CFDs"],
        "section_type": "qa",
        "line_start": 110,
        "line_end": 293,
        "summary": "Define como aproximar costes y swaps, y cuando preferir futuros, CFDs o ETFs por restricciones de cartera.",
        "keywords": ["swaps", "commissions", "slippage", "futures", "CFDs", "ETFs"],
        "contains_code": False,
        "contains_table": False,
        "contains_question": True,
        "requires_image_reading": False,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 5,
        "heading_path": ["Practice 15", "Buscador E/S", "Overview"],
        "section_type": "procedure",
        "line_start": 294,
        "line_end": 372,
        "summary": "Presenta el Buscador E/S como herramienta de exploracion de 23 entradas por 35 salidas.",
        "keywords": ["entry-search", "exit-search", "Buscador E_S", "exploration-tool"],
        "contains_code": True,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 6,
        "heading_path": ["Practice 15", "Entradas", "Casos 1 a 14"],
        "section_type": "procedure",
        "line_start": 373,
        "line_end": 706,
        "summary": "Describe entradas momentum, breakout, medias, Bollinger, ATR y Donchian en el buscador.",
        "keywords": ["entries", "momentum", "breakout", "moving-average", "Bollinger", "ATR", "Donchian"],
        "contains_code": True,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 7,
        "heading_path": ["Practice 15", "Entradas", "Casos 15 a 23 y candlestick functions"],
        "section_type": "procedure",
        "line_start": 707,
        "line_end": 998,
        "summary": "Completa las entradas, incluye funciones de velas y advierte que el buscador no es el sistema final.",
        "keywords": ["RSI", "event", "news", "candlestick", "ShowMe", "not-final-system"],
        "contains_code": True,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 8,
        "heading_path": ["Practice 15", "Salidas"],
        "section_type": "procedure",
        "line_start": 999,
        "line_end": 1099,
        "summary": "Inventaria salidas del buscador y prepara workspace/inputs para exploracion.",
        "keywords": ["exits", "workspace", "inputs", "exploration"],
        "contains_code": True,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 9,
        "heading_path": ["Practice 15", "Money management", "Introduccion"],
        "section_type": "concept",
        "line_start": 1100,
        "line_end": 1180,
        "summary": "Situa el money management, rechaza martingalas sin edge y presenta Fixed Fractional.",
        "keywords": ["anti-martingale", "edge", "Fixed-Fractional", "Ralph-Vince"],
        "contains_code": False,
        "contains_table": False,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 10,
        "heading_path": ["Practice 15", "Money management", "Exportacion a MSA"],
        "section_type": "procedure",
        "line_start": 1181,
        "line_end": 1318,
        "summary": "Explica como exportar trades y riesgo a MSA con WriteTrades32 y unidad de riesgo consistente.",
        "keywords": ["MSA", "WriteTrades32", "RiskMSA", "export", "lastbaronchart"],
        "contains_code": True,
        "contains_table": False,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 11,
        "heading_path": ["Practice 15", "Money management", "Riesgo por volatilidad normalizada"],
        "section_type": "validation",
        "line_start": 1319,
        "line_end": 1450,
        "summary": "Define riesgo con Average Normalized True Range, suelo de volatilidad y conversion a riesgo en dinero.",
        "keywords": ["normalized-ATR", "volatility-floor", "risk-denominator", "BigPointValue"],
        "contains_code": True,
        "contains_table": False,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 12,
        "heading_path": ["Practice 15", "Money management", "Codigo real Apolo"],
        "section_type": "procedure",
        "line_start": 1451,
        "line_end": 1598,
        "summary": "Muestra inputs reales de Apolo para Start_Equity, MMVar, Min/Max size, RoundTo y Filt_ATR.",
        "keywords": ["Apolo", "Filt_ATR", "MMVar", "Min_Size", "Max_Size", "RoundTo"],
        "contains_code": True,
        "contains_table": False,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 13,
        "heading_path": ["Practice 15", "Money management", "Formula de sizing, redondeo y limites"],
        "section_type": "validation",
        "line_start": 1599,
        "line_end": 1779,
        "summary": "Fija formula de Trade_Long/Trade_Shrt, redondeo hacia abajo y limites minimos/maximos.",
        "keywords": ["position-size", "IntPortion", "round-down", "MinList", "MaxList", "caps"],
        "contains_code": True,
        "contains_table": False,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 14,
        "heading_path": ["Practice 15", "Money management", "Con y sin suelo de volatilidad"],
        "section_type": "validation",
        "line_start": 1780,
        "line_end": 2087,
        "summary": "Compara tamanos de contrato con y sin floor de volatilidad y analiza shocks como COVID.",
        "keywords": ["with-without-floor", "contract-oscillation", "COVID", "low-volatility-shock"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 15,
        "heading_path": ["Practice 15", "MSA", "Exportacion y position sizing"],
        "section_type": "procedure",
        "line_start": 2088,
        "line_end": 2245,
        "summary": "Carga trades en MSA, muestra metodos de position sizing y separa trades raw de sizing aplicado.",
        "keywords": ["MSA", "raw-trades", "position-sizing-methods", "Kelly", "Fixed-Risk"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 16,
        "heading_path": ["Practice 15", "MSA", "Optimizador y ratios"],
        "section_type": "validation",
        "line_start": 2246,
        "line_end": 2406,
        "summary": "Compara Kelly, Fixed Fractional, Fixed Risk y optimizaciones bajo restriccion de drawdown.",
        "keywords": ["Kelly", "Fixed-Fractional", "Fixed-Risk", "drawdown-limit", "optimizer"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 17,
        "heading_path": ["Practice 15", "MSA", "Advertencia de curvas exponenciales"],
        "section_type": "warning",
        "line_start": 2407,
        "line_end": 2471,
        "summary": "Advierte que las curvas de money management ocultan drawdowns enormes y exigen prudencia manual.",
        "keywords": ["exponential-curve", "drawdown", "visual-deception", "risk-review"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 18,
        "heading_path": ["Practice 15", "Portfolio", "Familias, correlacion e instrumentos"],
        "section_type": "portfolio",
        "line_start": 2472,
        "line_end": 2627,
        "summary": "Compara familias Apolo/Nemesis, correlacion, diversificacion y eleccion futures/CFDs/ETFs.",
        "keywords": ["portfolio", "correlation", "Apolo", "Nemesis", "diversification", "instrument-choice"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 19,
        "heading_path": ["Practice 15", "Portfolio", "Comparacion de metodos de MM"],
        "section_type": "validation",
        "line_start": 2628,
        "line_end": 2913,
        "summary": "Evalua Kelly, Fixed Fractional, Fixed Risk, Fixed Ratio, rachas y drawdowns por sistema/familia.",
        "keywords": ["method-comparison", "losing-streak", "Fixed-Ratio", "Percent-Volatility", "family-review"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": [],
    },
    {
        "n": 20,
        "heading_path": ["Practice 15", "Cierre", "Apolo, tests finales y siguiente clase"],
        "section_type": "conclusion",
        "line_start": 2914,
        "line_end": 3175,
        "summary": "Cierra con comparaciones Apolo, Percent Volatility/Fixed Risk y recordatorios de prudencia y MultiCharts.",
        "keywords": ["Apolo", "final-comparison", "Percent-Volatility", "Fixed-Risk", "MultiCharts"],
        "contains_code": False,
        "contains_table": True,
        "contains_question": False,
        "requires_image_reading": True,
        "requires_human_review": True,
        "notes": ["La incidencia de CPU/MSA se registra como limitacion operativa, no como conclusion cuantitativa."],
    },
]


IMAGE_OVERRIDES = {
    "020": {
        "visual_type": "slide",
        "doctrine_relevance": "high",
        "notes": "Portada conceptual de Fixed Fractional y fuente de Ralph Vince.",
        "technical_reading": "Situa Fixed Fractional como metodo base de la clase, no como una optimizacion aislada de curva.",
    },
    "021": {
        "visual_type": "slide",
        "doctrine_relevance": "high",
        "notes": "Define que la proporcion fija de capital debe ligarse al riesgo de cada trade.",
        "technical_reading": "El sizing no debe calcularse solo por capital disponible; necesita una medida de trade risk.",
    },
    "022": {
        "visual_type": "formula_slide",
        "doctrine_relevance": "critical",
        "contains_numbers": True,
        "notes": "Formula N = f * Equity / Trade Risk.",
        "technical_reading": "Esta formula es la regla matematica central del sizing de la practica; cualquier implementacion debe declarar f, equity y riesgo por trade.",
    },
    "034": {
        "visual_type": "volatility_chart",
        "doctrine_relevance": "critical",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Compara ATR en puntos contra Average Normalized True Range porcentual.",
        "technical_reading": "El ATR en puntos queda sesgado por el nivel de precio; el ATR normalizado permite comparar volatilidad en series historicas largas.",
    },
    "035": {
        "visual_type": "volatility_chart",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "notes": "Muestra el concepto de linea/floor sobre ATR normalizado.",
        "technical_reading": "El suelo de volatilidad limita el apalancamiento cuando la volatilidad observada cae demasiado.",
    },
    "036": {
        "visual_type": "volatility_chart",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "notes": "Senala expansiones de volatilidad tras zonas bajas.",
        "technical_reading": "La captura justifica que el sizing no debe aumentar agresivamente contratos justo antes de una expansion de volatilidad.",
    },
    "037": {
        "visual_type": "platform_dialog",
        "doctrine_relevance": "medium",
        "contains_numbers": True,
        "notes": "Dialogo para fijar linea horizontal de referencia en 1.50 sobre ATR normalizado.",
        "technical_reading": "La evidencia visual muestra el uso operativo de umbrales de volatilidad, aunque el valor final debe calibrarse por sistema.",
    },
    "038": {
        "visual_type": "volatility_chart",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "notes": "Compara ATR normalizado y ATR en puntos durante el shock 2020.",
        "technical_reading": "La normalizacion capta el shock relativo y evita que el precio absoluto contamine la lectura historica del riesgo.",
    },
    "041": {
        "visual_type": "trade_chart",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "notes": "Tramo de baja volatilidad donde el sizing podria quedar demasiado alto.",
        "technical_reading": "La clase usa este tipo de tramo para defender un floor como defensa ante shocks tras regimenes tranquilos.",
    },
    "042": {
        "visual_type": "code",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Inputs reales: Start_Equity, MMVar, Min_Size, Max_Size, RoundTo y Filt_ATR 1.75.",
        "technical_reading": "El sizing debe parametrizar capital, fraccion, limites, redondeo y floor; no deben quedar constantes ocultas.",
    },
    "043": {
        "visual_type": "code",
        "doctrine_relevance": "critical",
        "contains_numbers": True,
        "notes": "Risk = Ajuste / 100 * typicalprice * BigPointValue; alternativa nominal comentada.",
        "technical_reading": "El riesgo usado para sizing combina volatilidad normalizada con precio actual y valor nominal del contrato.",
    },
    "044": {
        "visual_type": "code",
        "doctrine_relevance": "critical",
        "contains_numbers": True,
        "notes": "Formula de Trade_Long/Trade_Shrt y redondeo con IntPortion.",
        "technical_reading": "La posicion se calcula con equity mas profits, fraccion MMVar y riesgo absoluto; despues se redondea hacia abajo y se aplican limites.",
    },
    "045": {
        "visual_type": "code",
        "doctrine_relevance": "critical",
        "contains_numbers": True,
        "notes": "Bloque de IntPortion, MaxList y MinList.",
        "technical_reading": "El orden importa: calcular tamano bruto, redondear por lote y despues aplicar minimo y maximo.",
    },
    "046": {
        "visual_type": "documentation",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Ayuda de TradeStation sobre IntPortion: 4.5 devuelve 4.",
        "technical_reading": "La captura respalda la regla de truncar/round-down para no exceder el riesgo previsto.",
    },
    "057": {
        "visual_type": "formula_slide",
        "doctrine_relevance": "critical",
        "contains_numbers": True,
        "notes": "Repite la formula Fixed Fractional y define f como agresividad/conservadurismo.",
        "technical_reading": "La variable f no es conocida por defecto; debe elegirse por analisis de riesgo y drawdown.",
    },
    "064": {
        "visual_type": "trade_chart",
        "doctrine_relevance": "medium",
        "contains_chart": True,
        "notes": "Contrato variable con Average Normalized True Range historico.",
        "technical_reading": "Muestra que el numero de contratos cambia con volatilidad y equity; el Harness debe registrar oscilacion de size.",
    },
    "065": {
        "visual_type": "trade_chart",
        "doctrine_relevance": "medium",
        "contains_chart": True,
        "notes": "Bandas/floors de volatilidad sobre NATR.",
        "technical_reading": "Permite comparar el floor aplicado frente a la volatilidad observada y su efecto en contratos.",
    },
    "066": {
        "visual_type": "trade_chart",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "notes": "Red boxes senalan tamanos de contratos bajo diferentes regimenes.",
        "technical_reading": "La evidencia ilustra como la baja volatilidad puede disparar contratos y como la volatilidad alta los reduce.",
    },
    "070": {
        "visual_type": "performance_chart",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Performance TradeStation con net profit 13.8M y profit factor 2.19 bajo una configuracion de floor.",
        "technical_reading": "Sirve como comparativa base: rentabilidad, gross loss y max loss deben leerse junto al tamano de contratos, no solo por net profit.",
    },
    "071": {
        "visual_type": "performance_chart",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Performance con net profit 20.5M pero perdidas mayores y tamanos mas agresivos.",
        "technical_reading": "Mas beneficio historico puede venir de mas oscilacion de contratos y mayor exposicion; no implica mejor sizing.",
    },
    "075": {
        "visual_type": "platform_dialog",
        "doctrine_relevance": "medium",
        "contains_numbers": True,
        "notes": "Propiedades de estrategia con inputs completos.",
        "technical_reading": "Registra que los resultados dependen de una configuracion concreta y no deben aislarse del set de inputs.",
    },
    "076": {
        "visual_type": "performance_chart",
        "doctrine_relevance": "medium",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Zoom sobre low-vol con performance summary.",
        "technical_reading": "Ayuda a auditar como el floor y el periodo ATR afectan tamano durante regimes tranquilos.",
    },
    "080": {
        "visual_type": "trade_chart",
        "doctrine_relevance": "medium",
        "contains_chart": True,
        "notes": "Tooltip de contrato alrededor de septiembre 2021 con NATR cercano al floor.",
        "technical_reading": "Muestra tamano alto en volatilidad moderada-baja; debe estresarse contra salto de volatilidad posterior.",
    },
    "084": {
        "visual_type": "trade_chart",
        "doctrine_relevance": "critical",
        "contains_chart": True,
        "notes": "Shock COVID: ATR normalizado se dispara y los contratos bajan drasticamente.",
        "technical_reading": "El sizing por volatilidad debe reducir contratos rapidamente en shocks, pero el mayor peligro esta antes del shock si el floor era demasiado bajo.",
    },
    "085": {
        "visual_type": "trade_chart",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "notes": "Tooltip de marzo 2020 con Buy 14 en alta volatilidad.",
        "technical_reading": "Evidencia concreta de reduccion de posicion durante volatilidad extrema.",
    },
    "088": {
        "visual_type": "trade_chart",
        "doctrine_relevance": "medium",
        "contains_chart": True,
        "notes": "Variante COVID con tamanos de contrato mas bajos.",
        "technical_reading": "Permite comparar sensibilidad de size ante parametrizaciones diferentes de volatilidad.",
    },
    "090": {
        "visual_type": "trade_chart",
        "doctrine_relevance": "medium",
        "contains_chart": True,
        "notes": "Ventana 2023-2024 con ATR period 15 y floor 1.75.",
        "technical_reading": "El periodo de volatilidad cambia la respuesta de contratos; debe incluirse como decision de diseno.",
    },
    "107": {
        "visual_type": "code",
        "doctrine_relevance": "critical",
        "contains_numbers": True,
        "notes": "WriteTrades32 exporta RiskMSA bajo lastbaronchart y corrige stop tras posicion cerrada.",
        "technical_reading": "El export debe ejecutarse una vez al final y mantener la misma unidad de riesgo que el P/L exportado.",
    },
    "110": {
        "visual_type": "platform_menu",
        "doctrine_relevance": "medium",
        "notes": "Menu Analysis -> Position Sizing en MSA.",
        "technical_reading": "El sizing se aplica post-export en MSA; los trades raw deben conservarse como base.",
    },
    "113": {
        "visual_type": "platform_dialog",
        "doctrine_relevance": "high",
        "notes": "Lista de metodos MSA: Kelly, Fixed Risk, Fixed Ratio, Percent Volatility, etc.",
        "technical_reading": "El Harness debe registrar que metodo se usa y no mezclar resultados de metodos distintos.",
    },
    "117": {
        "visual_type": "platform_dialog",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Kelly formula con f = 23.6897.",
        "technical_reading": "Kelly puede arrojar una fraccion agresiva; debe auditarse con drawdown y rachas.",
    },
    "118": {
        "visual_type": "equity_curve",
        "doctrine_relevance": "critical",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Kelly produce curva explosiva con max drawdown 31.16%.",
        "technical_reading": "La rentabilidad final no basta; drawdown, rachas y max loss pueden invalidar un sizing visualmente atractivo.",
    },
    "122": {
        "visual_type": "optimizer_dialog",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Optimizador MSA limita max percent drawdown a 25%.",
        "technical_reading": "La optimizacion de sizing debe incluir restriccion explicita de drawdown, no solo maximizar net profit.",
    },
    "123": {
        "visual_type": "optimizer_result",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Fixed Risk: fixed fraction 4.11 bajo drawdown maximo 25%.",
        "technical_reading": "El f optimo depende del drawdown permitido; no es una constante universal.",
    },
    "125": {
        "visual_type": "optimizer_result",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Fixed Risk: fixed fraction 2.35 bajo drawdown maximo 15%.",
        "technical_reading": "Bajar el drawdown permitido cambia fuertemente el f y el net profit; esto debe compararse sistematicamente.",
    },
    "139": {
        "visual_type": "portfolio_curve",
        "doctrine_relevance": "critical",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Portfolio con crecimiento enorme y max drawdown 50.07%.",
        "technical_reading": "Una curva de cartera espectacular puede esconder un drawdown inaceptable; el Harness debe bloquear aprobacion por curva sin metricas.",
    },
    "140": {
        "visual_type": "portfolio_curve",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Plot by trade muestra equity y size, con max drawdown 50.07%.",
        "technical_reading": "El tamano agregado de cartera tambien debe auditarse; growth y size crecen conjuntamente.",
    },
    "145": {
        "visual_type": "portfolio_curve",
        "doctrine_relevance": "critical",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Portfolio con max drawdown 28.26% incluso tras moderar exposicion.",
        "technical_reading": "Reducir agresividad mejora el DD pero no elimina el riesgo; el objetivo debe fijarse antes de elegir el sizing.",
    },
    "146": {
        "visual_type": "portfolio_zoom",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Zoom del portfolio muestra drawdown material oculto por la escala global.",
        "technical_reading": "La revision debe incluir zooms y tablas, no solo grafico completo en escala logaritmica.",
    },
    "151": {
        "visual_type": "portfolio_curve",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Portfolio solo Nemesis con plateau largo y max drawdown 17.13%.",
        "technical_reading": "Las familias deben evaluarse por separado; una familia puede aportar rentabilidad pero pasar largos tramos sin progreso.",
    },
    "153": {
        "visual_type": "portfolio_curve",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Portfolio solo Apolo con max drawdown 14.96% y tramos iniciales debiles.",
        "technical_reading": "Apolo y Nemesis tienen perfiles distintos; la mezcla debe medirse por contribucion y correlacion, no por nombre del sistema.",
    },
    "154": {
        "visual_type": "portfolio_zoom",
        "doctrine_relevance": "medium",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Zoom de Apolo con DD puntual visible en tooltip.",
        "technical_reading": "El zoom operativo revela perdidas que la curva completa disimula.",
    },
    "156": {
        "visual_type": "portfolio_setup",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Portfolio de Nemesis con 8 sistemas.",
        "technical_reading": "La cartera se compone de varios market systems; las conclusiones deben registrar composicion exacta.",
    },
    "161": {
        "visual_type": "equity_curve",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Nemesis GC set con Kelly f 11.41 y max drawdown 45.07%.",
        "technical_reading": "Kelly puede ser inaceptable por drawdown aunque la rentabilidad historica sea alta.",
    },
    "162": {
        "visual_type": "equity_curve",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Nemesis GC set con Kelly f 7.416 y max drawdown 52.18%.",
        "technical_reading": "Un f aparentemente menor tambien puede producir drawdown extremo por path dependency.",
    },
    "168": {
        "visual_type": "equity_table",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Tabla con Risk/Unit, F Value, Units, margin y drawdown.",
        "technical_reading": "La tabla permite auditar que unidades y riesgo cambian trade a trade; no basta con la curva.",
    },
    "169": {
        "visual_type": "documentation",
        "doctrine_relevance": "critical",
        "contains_numbers": True,
        "notes": "Ayuda MSA: Kelly es aproximado, no considera drawdown y se incluye para comparacion educativa.",
        "technical_reading": "TSIS no debe promover Kelly como sizing practico automatico sin filtros de drawdown, rachas y revision humana.",
    },
    "171": {
        "visual_type": "performance_table",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Performance Results destaca max consecutive losses 15.",
        "technical_reading": "Las rachas de perdidas deben formar parte del stress test de money management.",
    },
    "174": {
        "visual_type": "equity_table",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Kelly equity table muestra units superiores a 6000 y drawdowns >30%.",
        "technical_reading": "El aumento de unidades puede acelerar deterioro; hay que validar unidades maximas, margen y drawdown.",
    },
    "178": {
        "visual_type": "position_sizing_dialog",
        "doctrine_relevance": "critical",
        "contains_numbers": True,
        "notes": "Fixed Risk 5% muestra max drawdown 55.71%.",
        "technical_reading": "Un porcentaje de riesgo aparentemente simple puede ser demasiado agresivo; TSIS debe fijar limites antes de optimizar.",
    },
    "179": {
        "visual_type": "position_sizing_dialog",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Fixed Risk 1% reduce max drawdown a 17.12%.",
        "technical_reading": "La sensibilidad a f debe compararse por grid o constraint; no se elige un unico porcentaje sin curva de sensibilidad.",
    },
    "181": {
        "visual_type": "equity_table",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Tabla Fixed Risk con Risk/Unit y Units ajustadas por volatilidad.",
        "technical_reading": "La reduccion de unidades durante volatilidad alta debe validarse trade a trade.",
    },
    "193": {
        "visual_type": "optimizer_result",
        "doctrine_relevance": "medium",
        "contains_numbers": True,
        "notes": "Percent Volatility optimiza a 0.1716 con drawdown 20%.",
        "technical_reading": "Percent Volatility es otro metodo comparable, pero debe evaluarse bajo la misma restriccion de drawdown.",
    },
    "194": {
        "visual_type": "optimizer_result",
        "doctrine_relevance": "medium",
        "contains_numbers": True,
        "notes": "Fixed Ratio optimiza delta 100 con drawdown 7.78%.",
        "technical_reading": "Un metodo puede reducir drawdown y tambien producir poco net profit; el tradeoff debe registrarse.",
    },
    "195": {
        "visual_type": "optimizer_result",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Fixed Risk optimiza f 1.19 con drawdown 20%.",
        "technical_reading": "Fixed Risk gana en este caso frente a algunas alternativas, pero no debe convertirse en dogma sin evaluar por familia.",
    },
    "202": {
        "visual_type": "portfolio_setup",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Portfolio Apolo incluye 10 sistemas long/short.",
        "technical_reading": "El analisis debe registrar long y short por set; combinar lados en portfolio es parte del procedimiento.",
    },
    "203": {
        "visual_type": "equity_curve",
        "doctrine_relevance": "high",
        "contains_chart": True,
        "contains_numbers": True,
        "notes": "Sistema short Apolo con curva muy irregular y drawdown 41.40%.",
        "technical_reading": "Los lados short pueden aportar descorrelacion pero tambien perfiles de riesgo diferentes; no se mezclan sin auditoria por lado.",
    },
    "204": {
        "visual_type": "equity_curve",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Apolo long Set1 con Kelly f 23.69 y drawdown 31.16%.",
        "technical_reading": "Confirma la agresividad de Kelly en Apolo long y la necesidad de controles de DD.",
    },
    "205": {
        "visual_type": "equity_curve",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Apolo short Set1 con Kelly f 16.09 y drawdown 41.40%.",
        "technical_reading": "El lado short necesita evaluacion independiente de f, DD y rachas.",
    },
    "209": {
        "visual_type": "position_sizing_dialog",
        "doctrine_relevance": "medium",
        "contains_numbers": True,
        "notes": "Fixed Risk 3% en Apolo.",
        "technical_reading": "Parametro de comparacion antes de optimizar por drawdown.",
    },
    "210": {
        "visual_type": "optimizer_dialog",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Optimizacion Apolo Fixed Risk con limite 20%, f alrededor de 3.211.",
        "technical_reading": "La optimizacion debe reportar objetivo, limite DD, secuencia usada y mejor resultado.",
    },
    "214": {
        "visual_type": "optimizer_result",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Apolo Percent Volatility 1.38 con drawdown 20%.",
        "technical_reading": "Percent Volatility debe compararse contra Fixed Risk bajo la misma restriccion, no por valor absoluto de net profit.",
    },
    "227": {
        "visual_type": "optimizer_result",
        "doctrine_relevance": "high",
        "contains_numbers": True,
        "notes": "Apolo Fixed Risk f 3.21 con drawdown 20%.",
        "technical_reading": "En esta evidencia Fixed Risk supera a Percent Volatility a igual DD, pero queda como resultado de familia/sistema.",
    },
    "228": {
        "visual_type": "optimizer_result",
        "doctrine_relevance": "medium",
        "contains_numbers": True,
        "notes": "Detalle duplicado/zoom de Percent Volatility 1.38.",
        "technical_reading": "Se conserva para trazabilidad visual del resultado MSA.",
    },
}


RULES = [
    {
        "n": 1,
        "title": "Built-in stops must be placed at root when symmetric",
        "statement": "If the same stop or target applies to long and short, built-in EasyLanguage stops should be declared at strategy root, not gated by MarketPosition.",
        "trigger": "Strategy uses SetStopLoss, SetProfitTarget or equivalent built-in stop/target.",
        "action": "Check whether side-specific logic is truly needed; otherwise keep the built-in stop active globally so entry-bar protection remains available.",
        "failure_mode": "A stop hidden inside position logic can miss entry-bar behavior or create side-specific inconsistencies.",
        "priority": "medium",
        "section_n": 2,
        "line_start": 11,
        "line_end": 58,
        "image_stems": [],
    },
    {
        "n": 2,
        "title": "Do not use martingale to compensate absence of edge",
        "statement": "Money management must not be used to manufacture edge; martingale-style recovery is rejected as a substitute for a valid system edge.",
        "trigger": "A candidate improves equity mainly by increasing size after losses or by recovery logic.",
        "action": "Block promotion until raw edge is demonstrated without martingale compensation.",
        "failure_mode": "Sizing hides a negative or fragile expectancy and creates tail risk.",
        "priority": "critical",
        "section_n": 9,
        "line_start": 1100,
        "line_end": 1180,
        "image_stems": ["020", "021", "022"],
    },
    {
        "n": 3,
        "title": "Search tools are not final systems",
        "statement": "The Buscador E/S is an exploration tool; promising ideas must be developed and audited independently before becoming systems.",
        "trigger": "A candidate comes directly from the 23 x 35 entry/exit exploration space.",
        "action": "Require independent system implementation, cost checks and robustness review before promotion.",
        "failure_mode": "The project ships a combinatorial search artifact instead of an engineered strategy.",
        "priority": "high",
        "section_n": 5,
        "line_start": 294,
        "line_end": 998,
        "image_stems": ["011", "012"],
    },
    {
        "n": 4,
        "title": "Side sample threshold depends on degrees of freedom",
        "statement": "A weak side sample, such as few short trades, is not automatically invalid, but its significance depends on optimization intensity, degrees of freedom and mirror/joint logic.",
        "trigger": "Long and short sides have materially different trade counts.",
        "action": "Report trade counts by side, degrees of freedom and whether side logic is independent or mirrored.",
        "failure_mode": "A blunt minimum trade rule either rejects useful evidence or accepts overfit side logic.",
        "priority": "high",
        "section_n": 3,
        "line_start": 59,
        "line_end": 109,
        "image_stems": [],
    },
    {
        "n": 5,
        "title": "Friction and financing must be explicit",
        "statement": "Commissions, slippage, swaps or equivalent financing costs must be approximated before comparing systems, especially intraday or high-turnover systems.",
        "trigger": "Instrument includes CFD/swap/borrow/friction exposure or high trade count.",
        "action": "Declare cost model and stress the strategy under realistic friction assumptions.",
        "failure_mode": "A marginal edge disappears live because financing and execution costs were ignored.",
        "priority": "high",
        "section_n": 4,
        "line_start": 110,
        "line_end": 293,
        "image_stems": [],
    },
    {
        "n": 6,
        "title": "Instrument choice is a portfolio feasibility decision",
        "statement": "Futures are preferred when feasible, but diversified CFDs or ETFs can be rational if capital or instrument constraints prevent adequate futures diversification.",
        "trigger": "System universe can be implemented through futures, CFDs, ETFs or equities.",
        "action": "Compare operational feasibility, diversification breadth, frictions, liquidity and capital requirements.",
        "failure_mode": "The project chooses a theoretically superior instrument and loses portfolio robustness through under-diversification.",
        "priority": "medium",
        "section_n": 4,
        "line_start": 110,
        "line_end": 293,
        "image_stems": [],
    },
    {
        "n": 7,
        "title": "Raw trade export must be preserved before MSA sizing",
        "statement": "Trades should be exported without final money management and then sized in MSA or equivalent tooling for comparable analysis.",
        "trigger": "A lesson pack or strategy enters money-management analysis.",
        "action": "Store raw trade list, risk-per-trade field and sizing method outputs separately.",
        "failure_mode": "Sizing effects contaminate raw edge and make method comparison impossible.",
        "priority": "critical",
        "section_n": 10,
        "line_start": 1181,
        "line_end": 2245,
        "image_stems": ["107", "110", "113"],
    },
    {
        "n": 8,
        "title": "MSA export must be guarded by last bar execution",
        "statement": "WriteTrades32 or equivalent export should run once at the end of the chart, outside loops and under a lastbar guard.",
        "trigger": "Strategy exports trades or risk values to external files.",
        "action": "Validate lastbaronchart guard and check that export paths are not repeated per bar.",
        "failure_mode": "Duplicate, partial or inconsistent trade files enter MSA analysis.",
        "priority": "high",
        "section_n": 10,
        "line_start": 1181,
        "line_end": 1318,
        "image_stems": ["107"],
    },
    {
        "n": 9,
        "title": "Trade risk definition is mandatory",
        "statement": "Fixed Fractional sizing requires a declared Trade Risk; if stops are rare, distant or absent, risk must be estimated rather than assumed zero.",
        "trigger": "A strategy applies Fixed Fractional, Fixed Risk, Kelly or risk-based position sizing.",
        "action": "Check that risk source is explicit, same-unit as P/L and stable enough for sizing.",
        "failure_mode": "Position size becomes arbitrary or infinitely large when risk is undefined or too small.",
        "priority": "critical",
        "section_n": 9,
        "line_start": 1100,
        "line_end": 1318,
        "image_stems": ["021", "022", "057"],
    },
    {
        "n": 10,
        "title": "Use normalized volatility for long historical sizing",
        "statement": "Normalized volatility, such as Average Normalized True Range, is preferred over ATR in points when price level changes materially over history.",
        "trigger": "Sizing uses volatility over a long historical series or changing nominal price regime.",
        "action": "Normalize true range by price before converting back to current risk units.",
        "failure_mode": "Raw ATR points understate or overstate risk because the instrument price level changed.",
        "priority": "critical",
        "section_n": 11,
        "line_start": 1319,
        "line_end": 1450,
        "image_stems": ["034", "038"],
    },
    {
        "n": 11,
        "title": "Apply a volatility floor before using volatility as denominator",
        "statement": "When volatility drives position size, apply a floor such as MaxList(AvgNormalizedTrueRange, Filt_ATR) before dividing by risk.",
        "trigger": "Position size increases when observed volatility falls.",
        "action": "Declare and test a floor, then compare with and without floor under low-vol-to-high-vol transitions.",
        "failure_mode": "Low volatility causes overleverage immediately before a volatility expansion.",
        "priority": "critical",
        "section_n": 11,
        "line_start": 1319,
        "line_end": 2087,
        "image_stems": ["035", "036", "041", "084", "085"],
    },
    {
        "n": 12,
        "title": "Convert normalized risk back to current money risk",
        "statement": "Risk for sizing must combine normalized volatility, current price proxy and BigPointValue or equivalent nominal multiplier.",
        "trigger": "Risk is computed from percentage volatility.",
        "action": "Validate formula equivalent to Risk = normalized_vol * price * BigPointValue.",
        "failure_mode": "Sizing uses percentage volatility but fails to account for current nominal exposure.",
        "priority": "critical",
        "section_n": 11,
        "line_start": 1319,
        "line_end": 1779,
        "image_stems": ["043", "044"],
    },
    {
        "n": 13,
        "title": "Round position size down and cap it",
        "statement": "After computing raw size, round down by lot size and apply Min_Size and Max_Size caps.",
        "trigger": "Computed trade size is non-integer or larger than operational caps.",
        "action": "Use truncation/IntPortion style logic and verify min/max bounds.",
        "failure_mode": "Rounding up or missing caps exposes more risk than intended.",
        "priority": "critical",
        "section_n": 13,
        "line_start": 1599,
        "line_end": 1779,
        "image_stems": ["044", "045", "046"],
    },
    {
        "n": 14,
        "title": "F and risk jointly define aggressiveness",
        "statement": "The money-management fraction and risk definition jointly determine aggressiveness; neither can be reviewed in isolation.",
        "trigger": "A strategy reports f, MMVar, Kelly value or Fixed Risk fraction.",
        "action": "Record both fraction and risk formula, then compare at equal drawdown targets.",
        "failure_mode": "A low f with low risk denominator can be more aggressive than it appears.",
        "priority": "high",
        "section_n": 16,
        "line_start": 2246,
        "line_end": 2406,
        "image_stems": ["117", "123", "125", "195"],
    },
    {
        "n": 15,
        "title": "Profit-only optimization is not accepted for sizing",
        "statement": "Sizing optimizers must include drawdown or risk constraints; net profit alone is not an acceptance metric.",
        "trigger": "MSA or another optimizer searches sizing parameters.",
        "action": "Require max drawdown cap, sequence declaration and sensitivity comparison.",
        "failure_mode": "The optimizer selects an intolerable path because it maximizes final equity.",
        "priority": "critical",
        "section_n": 16,
        "line_start": 2246,
        "line_end": 2406,
        "image_stems": ["122", "123", "125", "210", "227"],
    },
    {
        "n": 16,
        "title": "Exponential equity curves require drawdown review",
        "statement": "Money-management curves must be reviewed with drawdown percentages, max loss, rachas and zooms, not only visual equity growth.",
        "trigger": "A sized equity curve appears strongly exponential or visually smooth.",
        "action": "Inspect max percent drawdown, max loss, losing streak and zoomed periods before approval.",
        "failure_mode": "A visually impressive curve hides 28% to 50% drawdowns.",
        "priority": "critical",
        "section_n": 17,
        "line_start": 2407,
        "line_end": 2471,
        "image_stems": ["118", "139", "140", "145", "146"],
    },
    {
        "n": 17,
        "title": "Kelly is research evidence, not production sizing by default",
        "statement": "Kelly can be calculated for comparison, but it must not be promoted automatically because it ignores drawdown and can be impractical.",
        "trigger": "A candidate uses Kelly formula or reports Kelly f.",
        "action": "Mark Kelly outputs as research unless they pass drawdown, rachas and operational cap gates.",
        "failure_mode": "Kelly f creates excessive leverage and unacceptable drawdown.",
        "priority": "critical",
        "section_n": 19,
        "line_start": 2628,
        "line_end": 2913,
        "image_stems": ["117", "118", "161", "162", "169", "204", "205"],
    },
    {
        "n": 18,
        "title": "Losing streaks are mandatory MM stress tests",
        "statement": "Maximum consecutive losses must be reviewed because equity-only or Kelly-style adjustment can react too slowly during a long losing streak.",
        "trigger": "Sizing method increases/contracts size based mainly on equity or historical f.",
        "action": "Report max consecutive losses, worst historical loss and simulated losing-streak stress.",
        "failure_mode": "The system survives average volatility but fails in realistic streak clustering.",
        "priority": "high",
        "section_n": 19,
        "line_start": 2628,
        "line_end": 2913,
        "image_stems": ["171", "174"],
    },
    {
        "n": 19,
        "title": "Evaluate MM at portfolio and family level",
        "statement": "Sizing decisions must be evaluated at system, side, family and portfolio levels; the best standalone sizing may be wrong for the combined book.",
        "trigger": "Multiple systems, sets, assets or long/short sides are combined.",
        "action": "Compare Apolo/Nemesis or equivalent families separately and together, including correlation and drawdown contribution.",
        "failure_mode": "A method overfits standalone equity and worsens portfolio risk.",
        "priority": "critical",
        "section_n": 18,
        "line_start": 2472,
        "line_end": 2913,
        "image_stems": ["139", "151", "153", "156", "202", "203"],
    },
    {
        "n": 20,
        "title": "Compare sizing methods at equal drawdown constraints",
        "statement": "Fixed Risk, Percent Volatility, Fixed Ratio, Kelly and other methods should be compared under the same drawdown or risk budget.",
        "trigger": "Multiple MSA position-sizing methods are available for a strategy.",
        "action": "Run method comparison under common max drawdown, cost and sequence assumptions.",
        "failure_mode": "A method is selected because its risk budget was looser than alternatives.",
        "priority": "high",
        "section_n": 19,
        "line_start": 2628,
        "line_end": 3175,
        "image_stems": ["193", "194", "195", "214", "227"],
    },
    {
        "n": 21,
        "title": "Measure contract oscillation with and without volatility floor",
        "statement": "Removing a volatility floor may improve historical profit but must be reviewed for contract oscillation and low-vol shock exposure.",
        "trigger": "A candidate proposes lower or no Filt_ATR floor.",
        "action": "Compare max contracts, contract path and drawdown in with-floor versus without-floor runs.",
        "failure_mode": "The system earns more historically by taking excessive size in artificially quiet regimes.",
        "priority": "critical",
        "section_n": 14,
        "line_start": 1780,
        "line_end": 2087,
        "image_stems": ["066", "070", "071", "084", "088"],
    },
    {
        "n": 22,
        "title": "Operational tooling limits are blockers, not evidence",
        "statement": "If MSA/Maestro or CPU limits prevent an optimization or portfolio review, the result must be marked blocked/needs review rather than extrapolated.",
        "trigger": "A tool fails, hangs or cannot complete a requested portfolio/MM computation.",
        "action": "Record blocker, partial evidence and next reproducible run condition.",
        "failure_mode": "A quantitative conclusion is inferred from an incomplete tool run.",
        "priority": "medium",
        "section_n": 20,
        "line_start": 2914,
        "line_end": 3175,
        "image_stems": [],
    },
    {
        "n": 23,
        "title": "AlphaEvolve must optimize under MM gates",
        "statement": "Future AlphaEvolve strategy search must treat trade risk, floor, caps, cost model, drawdown target, rachas and portfolio contribution as evaluator gates.",
        "trigger": "A generated strategy enters evolutionary search or ranking.",
        "action": "Reject candidates that optimize edge or equity without passing the Sersan MM and portfolio validation gates.",
        "failure_mode": "Evolution rewards fragile leverage, not robust edge.",
        "priority": "critical",
        "section_n": 20,
        "line_start": 2914,
        "line_end": 3175,
        "image_stems": ["139", "145", "169", "181", "227"],
    },
]


TRANSLATIONS = [
    (1, "TSIS_STOP_ORDER_PLACEMENT_POLICY", "backtest_order_semantics_gate", "gate", "medium", "warning", "Backtest Harness", "Audit built-in stops versus manual side-specific exits."),
    (2, "TSIS_NO_MARTINGALE_WITHOUT_EDGE_GATE", "strategy_edge_precondition", "gate", "critical", "blocking", "AlphaEvolve", "Reject recovery sizing as a substitute for raw edge."),
    (3, "TSIS_SEARCH_TOOL_NOT_SYSTEM_GATE", "strategy_candidate_origin_gate", "gate", "high", "blocking", "Sersan/AlphaEvolve", "Mark Buscador outputs as ideas requiring independent implementation."),
    (4, "TSIS_SIDE_SAMPLE_AND_DOF_CHECK", "side_sample_dof_report", "metric", "high", "warning", "Backtest Harness", "Report side counts with degrees of freedom and optimization pressure."),
    (5, "TSIS_COST_AND_SWAP_FRICTION_GATE", "execution_cost_model_contract", "gate", "high", "blocking", "Backtest/Data Quality", "Require friction, borrow, financing or swap assumptions before ranking."),
    (6, "TSIS_INSTRUMENT_FEASIBILITY_PORTFOLIO_POLICY", "instrument_feasibility_matrix", "policy", "medium", "warning", "Portfolio Harness", "Compare futures, CFDs, ETFs and equities by feasibility and diversification."),
    (7, "TSIS_RAW_TRADE_EXPORT_FOR_MM_ANALYSIS", "raw_trade_export_contract", "artifact", "critical", "blocking", "Backtest Harness", "Keep raw trades separate from post-export sizing results."),
    (8, "TSIS_LASTBAR_EXPORT_GUARD", "trade_export_single_execution_gate", "gate", "high", "blocking", "Backtest Harness", "Validate lastbar guard and one-time export behavior."),
    (9, "TSIS_TRADE_RISK_DEFINITION_REQUIRED", "trade_risk_field_contract", "artifact", "critical", "blocking", "Backtest/AlphaEvolve", "Require same-unit risk per trade for all risk-based sizing."),
    (10, "TSIS_NORMALIZED_VOLATILITY_RISK_POLICY", "normalized_volatility_risk_calculator", "policy", "critical", "blocking", "Backtest Harness", "Use price-normalized volatility for long histories."),
    (11, "TSIS_VOLATILITY_FLOOR_LEVERAGE_GATE", "volatility_floor_stress_gate", "gate", "critical", "blocking", "AlphaEvolve", "Compare low-vol-to-high-vol behavior with explicit floors."),
    (12, "TSIS_RISK_TO_DOLLARS_CONVERSION_CHECK", "risk_nominal_conversion_validator", "validator", "critical", "blocking", "Backtest Harness", "Validate normalized risk to price and BigPointValue conversion."),
    (13, "TSIS_ROUND_DOWN_POSITION_SIZE_RULE", "position_size_rounding_validator", "validator", "critical", "blocking", "Execution/Backtest", "Check truncation, lot size, Min_Size and Max_Size."),
    (14, "TSIS_MM_AGGRESSIVENESS_DECLARATION", "money_management_aggressiveness_manifest", "artifact", "high", "warning", "Portfolio Harness", "Record f, risk formula and caps for each run."),
    (15, "TSIS_MM_OPTIMIZATION_DRAWDOWN_CONSTRAINT", "position_sizing_optimizer_gate", "gate", "critical", "blocking", "AlphaEvolve", "Require drawdown cap and optimization objective in sizing searches."),
    (16, "TSIS_EXPONENTIAL_CURVE_DD_REVIEW_GATE", "equity_curve_visual_deception_gate", "gate", "critical", "blocking", "Portfolio Harness", "Require max DD, max loss, streaks and zoom review."),
    (17, "TSIS_KELLY_RESEARCH_ONLY_POLICY", "kelly_usage_policy", "policy", "critical", "blocking", "Portfolio Harness", "Treat Kelly as comparison unless production gates pass."),
    (18, "TSIS_LOSING_STREAK_MM_STRESS_CHECK", "losing_streak_stress_report", "metric", "high", "warning", "Backtest/Portfolio", "Stress max consecutive losses and clustered drawdowns."),
    (19, "TSIS_PORTFOLIO_LEVEL_MM_EVALUATION", "portfolio_family_mm_report", "artifact", "critical", "blocking", "Portfolio Harness", "Evaluate sizing by side, family and portfolio contribution."),
    (20, "TSIS_MM_METHOD_EQUAL_DD_COMPARISON", "sizing_method_comparison_table", "artifact", "high", "warning", "Portfolio Harness", "Compare methods under common drawdown/risk budget."),
    (21, "TSIS_WITH_WITHOUT_VOL_FLOOR_COMPARISON", "volatility_floor_ablation_report", "artifact", "critical", "blocking", "AlphaEvolve", "Require ablation for contract oscillation and shocks."),
    (22, "TSIS_MM_TOOL_RESOURCE_BLOCKER_PROTOCOL", "tool_resource_blocker_log", "protocol", "medium", "warning", "Harness Kernel", "Record incomplete MSA/Maestro runs as blockers."),
    (23, "TSIS_ALPHAEVOLVE_MM_EVALUATOR_GATE", "alphaevolve_mm_evaluator_suite", "gate", "critical", "blocking", "AlphaEvolve", "Only rank generated strategies after MM and portfolio gates pass."),
]


OPEN_QUESTIONS = [
    "What max drawdown bands should TSIS allow by product, capital base and client profile?",
    "How should Filt_ATR floors and ceilings be calibrated by instrument, timeframe and strategy family?",
    "Should TSIS use TypicalPrice, Close or another price proxy when converting normalized volatility into money risk?",
    "How should swaps, borrow, financing and locate costs be modeled for TSIS small-cap/equity backtests?",
    "Which method-comparison table is canonical when Fixed Risk, Percent Volatility, Kelly and Fixed Ratio are compared at equal drawdown?",
    "What minimum side sample should be required as a function of degrees of freedom and optimization pressure?",
    "How should AlphaEvolve stress low-vol-to-high-vol transitions and losing streak clusters during candidate search?",
    "What is the operational fallback when MSA, Maestro or another external tool cannot complete an optimization because of CPU/resource limits?",
]


def source_anchor(section_n: int, line_start: int, line_end: int, images=None):
    return {
        "lesson_id": LESSON_ID,
        "md_path": rel_posix(SRC_MD_REL),
        "section_id": section_id(section_n),
        "line_start": line_start,
        "line_end": line_end,
        "image_ids": images or [],
    }


def build_sections(lines):
    if len(lines) != 3175:
        raise ValueError(f"Unexpected source line count: {len(lines)}")
    sections = []
    previous_end = 0
    for raw in RAW_SECTIONS:
        if raw["line_start"] != previous_end + 1:
            raise ValueError(f"Section gap before {raw['n']}")
        if raw["line_end"] < raw["line_start"]:
            raise ValueError(f"Invalid section {raw['n']}")
        previous_end = raw["line_end"]
        section_text = "\n".join(lines[raw["line_start"] - 1 : raw["line_end"]])
        rec = dict(raw)
        rec["lesson_id"] = LESSON_ID
        rec["section_id"] = section_id(raw["n"])
        rec["source_md"] = rel_posix(SRC_MD_REL)
        rec["text_sha256"] = sha256_text(section_text)
        rec["image_ids"] = []
        sections.append(rec)
    if previous_end != len(lines):
        raise ValueError("Sections do not cover full source")
    return sections


def section_for_line(sections, line_no: int):
    for sec in sections:
        if sec["line_start"] <= line_no <= sec["line_end"]:
            return sec
    raise ValueError(f"No section for line {line_no}")


def extract_image_refs(lines):
    md_re = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
    html_re = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", re.IGNORECASE)
    refs = []
    for line_no, line in enumerate(lines, start=1):
        for m in md_re.finditer(line):
            refs.append({"line_no": line_no, "syntax": "markdown", "source_ref": m.group(1).strip()})
        for m in html_re.finditer(line):
            refs.append({"line_no": line_no, "syntax": "html_img", "source_ref": m.group(1).strip()})
    return refs


def resolve_image_ref(source_ref: str):
    decoded = unquote(source_ref)
    candidate_direct = (SRC_MD.parent / decoded).resolve()
    if candidate_direct.exists():
        return candidate_direct, "resolved_direct"
    fallback = SERSAN_ROOT / IMAGE_DIR_REL / Path(decoded).name
    if fallback.exists():
        return fallback, "resolved_lesson_fallback"
    return fallback, "missing"


def build_image_records(lines, sections):
    refs = extract_image_refs(lines)
    if len(refs) != 206:
        raise ValueError(f"Unexpected image reference count: {len(refs)}")
    occurrences = {}
    records = []
    for idx, ref in enumerate(refs, start=1):
        resolved_path, status = resolve_image_ref(ref["source_ref"])
        stem = sanitize_stem(resolved_path.stem)
        occurrences[stem] = occurrences.get(stem, 0) + 1
        sec = section_for_line(sections, ref["line_no"])
        override = IMAGE_OVERRIDES.get(stem, {})
        doctrine_relevance = override.get("doctrine_relevance", "low")
        contains_numbers = override.get("contains_numbers", False)
        contains_chart = override.get("contains_chart", False)
        img_id = image_id(stem, occurrences[stem])
        note_ref = ""
        if doctrine_relevance != "low":
            note_ref = f"image_evidence_notes/{img_id}.md"
        rec = {
            "contract_version": "sersan_image_evidence_index_v0_1",
            "lesson_id": LESSON_ID,
            "image_ref_index": idx,
            "image_id": img_id,
            "section_id": sec["section_id"],
            "source_line": ref["line_no"],
            "source_syntax": ref["syntax"],
            "source_ref_original": ref["source_ref"],
            "source_ref_decoded": unquote(ref["source_ref"]),
            "resolved_path": sersan_rel(resolved_path) if resolved_path.exists() else "",
            "resolution_status": status,
            "sha256": sha256_file(resolved_path) if resolved_path.exists() else "",
            "visual_type": override.get("visual_type", "unclassified"),
            "contains_numbers": str(contains_numbers).lower(),
            "contains_chart": str(contains_chart).lower(),
            "doctrine_relevance": doctrine_relevance,
            "requires_human_review": str(doctrine_relevance in {"critical", "high"}).lower(),
            "technical_reading_ref": note_ref,
            "notes": override.get("notes", "Indexed only; low doctrine relevance for this pilot."),
            "technical_reading": override.get("technical_reading", ""),
            "_path": resolved_path,
            "_stem": stem,
        }
        records.append(rec)
        sec["image_ids"].append(img_id)
    return records


def image_md_path(stem: str) -> str:
    path = SERSAN_ROOT / IMAGE_DIR_REL / f"{stem}.png"
    rel = Path(os.path.relpath(path, OUT_DIR))
    return rel_posix(rel).replace(" ", "%20")


def image_md_path_from_record(rec: dict) -> str:
    rel = Path(os.path.relpath(rec["_path"], OUT_DIR))
    return rel_posix(rel).replace(" ", "%20")


def write_sections(sections):
    with (OUT_DIR / "lesson_sections.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for sec in sections:
            out = {k: v for k, v in sec.items() if not k.startswith("_")}
            f.write(json.dumps(out, ensure_ascii=False, sort_keys=True) + "\n")


def write_image_index(image_records):
    fieldnames = [
        "contract_version",
        "lesson_id",
        "image_ref_index",
        "image_id",
        "section_id",
        "source_line",
        "source_syntax",
        "source_ref_original",
        "source_ref_decoded",
        "resolved_path",
        "resolution_status",
        "sha256",
        "visual_type",
        "contains_numbers",
        "contains_chart",
        "doctrine_relevance",
        "requires_human_review",
        "technical_reading_ref",
        "notes",
    ]
    with (OUT_DIR / "image_evidence_index.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in image_records:
            writer.writerow({k: rec[k] for k in fieldnames})


def write_image_notes(image_records):
    notes_dir = OUT_DIR / "image_evidence_notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    for old in notes_dir.glob("*.md"):
        old.unlink()
    for rec in image_records:
        if rec["doctrine_relevance"] == "low":
            continue
        body = f"""# Image Evidence: {rec['image_id']}

Lesson: `{LESSON_ID}`
Source line: `{rec['source_line']}`
Section: `{rec['section_id']}`
Resolved asset: `{rec['resolved_path']}`
Relevance: `{rec['doctrine_relevance']}`
Visual type: `{rec['visual_type']}`

![Evidence]({image_md_path_from_record(rec)})

## Technical Reading

{rec['technical_reading']}

## Notes

{rec['notes']}
"""
        write_text(OUT_DIR / rec["technical_reading_ref"], body)


def write_rules(generated_at: str):
    rules_out = []
    image_lookup = {}
    for stem, override in IMAGE_OVERRIDES.items():
        image_lookup.setdefault(stem, f"{LESSON_ID}_img_{stem}")
    for rule in RULES:
        image_ids = [image_lookup[s] for s in rule["image_stems"] if s in image_lookup]
        rules_out.append(
            {
                "rule_id": rule_id(rule["n"]),
                "title": rule["title"],
                "status": "candidate",
                "priority": rule["priority"],
                "statement": rule["statement"],
                "trigger": rule["trigger"],
                "required_action": rule["action"],
                "failure_mode_if_ignored": rule["failure_mode"],
                "source_anchor": source_anchor(rule["section_n"], rule["line_start"], rule["line_end"], image_ids),
                "promotion_requirement": "Human doctrine review plus implementation-specific validation before canonical TSIS promotion.",
            }
        )
    payload = {
        "contract_version": "sersan_mechanical_rules_v0_1",
        "lesson_id": LESSON_ID,
        "generated_at_utc": generated_at,
        "promotion_status": "candidate_only",
        "rules": rules_out,
    }
    write_text(OUT_DIR / "mechanical_rules.yaml", yaml_dump(payload) + "\n")


def write_translation_map():
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
    with (OUT_DIR / "tsis_translation_map.csv").open("w", encoding="utf-8", newline="") as f:
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


def write_lesson_distillation(sections):
    table_rows = []
    for sec in sections:
        short_id = sec["section_id"].replace(f"{LESSON_ID}_", "")
        table_rows.append(
            f"| `{short_id}` | {sec['line_start']}-{sec['line_end']} | {sec['section_type']} | {sec['summary']} |"
        )
    rules_summary = "\n".join(f"{idx}. {rule['statement']}" for idx, rule in enumerate(RULES, start=1))
    translation_summary = "\n".join(
        f"- `{artifact}` -> {hint}" for _, _, artifact, _, _, _, _, hint in TRANSLATIONS
    )
    body = f"""# Lesson Distillation: {LESSON_ID}

Fecha: {DATE}
Estado: pilot v0.3, `pass_with_warnings`
Fuente: `03_only_md_revised/practica_15_revised.md`

## 1. Proposito del paquete

Este paquete destila la practica 15 como tercer piloto del Sersan Distillation
Harness. La clase es critica para TSIS porque convierte Money Management y
Position Sizing en reglas operativas: definir trade risk, normalizar
volatilidad, aplicar floors, limitar contratos, redondear hacia abajo, exportar
trades raw a MSA y evaluar el resultado a nivel sistema, familia y portfolio.

El objetivo no es adoptar todos los parametros de Apolo o Nemesis. El objetivo
es extraer gates que impidan que futuros agentes o AlphaEvolve premien curvas
bonitas construidas por apalancamiento fragil.

## 2. Lectura ejecutiva

La tesis central de la clase es:

1. primero se prueba edge;
2. despues se define riesgo por trade;
3. luego se estudia sizing bajo restricciones explicitas;
4. finalmente se revisa cartera, drawdown, rachas y correlacion.

Money Management no arregla sistemas sin edge. Una martingala o una fraccion
excesiva puede transformar un backtest en una curva impresionante, pero tambien
puede introducir drawdowns inaceptables. Por eso el Harness debe transformar
esta clase en validadores, no solo en resumen.

## 3. Secciones fuente

| Section | Lines | Tipo | Lectura |
|---|---:|---|---|
{chr(10).join(table_rows)}

## 4. Evidencia visual incrustada

### 4.1 Formula base de Fixed Fractional

![Fixed Fractional formula]({image_md_path("022")})

La formula `N = f * Equity / Trade Risk` es el centro matematico de la clase.
El sizing no se puede auditar si falta cualquiera de sus tres piezas: fraccion
`f`, equity y riesgo por trade.

### 4.2 Volatilidad normalizada y floor

![ATR points versus normalized volatility]({image_md_path("034")})

El ATR en puntos queda contaminado por el nivel de precio historico. La clase
usa Average Normalized True Range para comparar volatilidad relativa y despues
convertirla de vuelta a riesgo monetario actual.

![Volatility floor]({image_md_path("035")})

El floor de volatilidad evita que una volatilidad observada demasiado baja
dispare el numero de contratos. En TSIS esto debe ser un gate de leverage, no
una preferencia visual.

### 4.3 Codigo de riesgo y sizing

![Risk conversion]({image_md_path("043")})

La regla operativa es convertir volatilidad normalizada en riesgo monetario
con precio actual y `BigPointValue`. Esto conecta porcentaje de volatilidad con
dinero real por contrato.

![Round down and caps]({image_md_path("045")})

Despues del calculo bruto, el tamano se redondea hacia abajo con `IntPortion`
y se limita con `Min_Size` y `Max_Size`. Redondear hacia arriba invalida el
presupuesto de riesgo.

![IntPortion documentation]({image_md_path("046")})

La ayuda de TradeStation confirma que `IntPortion(4.5)` devuelve `4`. Este
detalle justifica convertir el redondeo hacia abajo en validador reproducible.

### 4.4 Comparativa con y sin floor

![Floor baseline performance]({image_md_path("070")})

![More aggressive sizing comparison]({image_md_path("071")})

Una configuracion puede ganar mas dinero historicamente y ser peor para TSIS si
lo logra aumentando oscilacion de contratos o exposicion en baja volatilidad.
El Harness debe comparar beneficio, gross loss, max loss, contratos y drawdown.

![COVID shock contract reduction]({image_md_path("084")})

La volatilidad alta reduce contratos. El riesgo principal, sin embargo, esta en
el periodo previo: baja volatilidad puede inflar el size justo antes de un
shock.

### 4.5 Exportacion y MSA

![WriteTrades32 export]({image_md_path("107")})

`RiskMSA` se exporta bajo `lastbaronchart`. Los trades raw y el riesgo deben
salir en unidades consistentes para que MSA compare metodos de sizing sin
contaminar la edge original.

![MSA position sizing methods]({image_md_path("113")})

MSA permite Kelly, Fixed Risk, Fixed Ratio, Percent Volatility y otros metodos.
El Harness debe registrar el metodo exacto y compararlo bajo las mismas
restricciones.

### 4.6 Kelly y drawdown

![Kelly curve drawdown]({image_md_path("118")})

Kelly puede producir crecimiento enorme y aun asi drawdown de 31.16%. La
rentabilidad final no valida el sizing.

![MSA Kelly help]({image_md_path("169")})

La propia ayuda de MSA avisa que Kelly es aproximado, no considera drawdown y
se incluye para comparacion educativa. En TSIS queda como herramienta de
analisis, no como sizing automatico por defecto.

### 4.7 Portfolio y engano visual

![Portfolio with 50 percent drawdown]({image_md_path("139")})

Una cartera puede parecer extraordinaria y aun asi tener max drawdown de
50.07%. Esta imagen justifica un gate explicito contra aprobar curvas por
apariencia.

![Portfolio reduced but still risky]({image_md_path("145")})

Incluso con menor agresividad, el portfolio mostrado mantiene 28.26% de
drawdown. El objetivo de riesgo debe fijarse antes de optimizar.

### 4.8 Metodo contra metodo

![Fixed Risk 5 percent]({image_md_path("178")})

Fixed Risk al 5% llega a 55.71% de max drawdown en la evidencia inspeccionada.

![Fixed Risk 1 percent]({image_md_path("179")})

Fixed Risk al 1% baja el drawdown a 17.12%. La sensibilidad a la fraccion es
una prueba obligatoria.

![Fixed Risk optimized]({image_md_path("227")})

En esta evidencia Apolo, Fixed Risk optimizado a igual drawdown supera a
Percent Volatility, pero se registra como resultado de esa familia/sistema, no
como ley universal.

## 5. Reglas mecanicas candidatas

La extraccion completa esta en `mechanical_rules.yaml`. Las reglas principales
son:

{rules_summary}

## 6. Traduccion TSIS

La traduccion completa esta en `tsis_translation_map.csv`. Las piezas mas
importantes para TSIS son:

{translation_summary}

## 7. Lo que no debe promocionarse todavia

No se debe promocionar Kelly como sizing de produccion por defecto.

No se debe promocionar un valor universal de `Filt_ATR`, `MMVar`, Fixed Risk o
Percent Volatility. La clase muestra metodologia, no constantes canonicas.

No se debe elegir un metodo de sizing por net profit sin normalizar por
drawdown, rachas, max loss, contratos maximos y contribucion a cartera.

No se debe extrapolar resultados incompletos si MSA, Maestro o CPU impiden
terminar una optimizacion.

## 8. Mejora del Harness frente a pilotos 02 y 09

Este tercer piloto completa el triangulo inicial:

- practice_02: reglas de sistema y validacion basica;
- practice_09: revision de optimizacion y robustez por mapas;
- practice_15: money management, risk sizing y cartera.

Con este paquete el Harness ya puede definir una primera suite de evaluadores
para AlphaEvolve: edge bruto, costes, overfit, trade risk, sizing, drawdown,
rachas, floors de volatilidad y contribucion de portfolio.

## 9. Consumidores previstos

- Sersan Distillation Harness: doctrina candidata de MM y portfolio.
- Backtest Harness: contrato de trade risk, raw exports y risk metrics.
- AlphaEvolve: gates contra leverage fragil y profit-only optimization.
- Portfolio Harness futuro: comparativa por familia, lado, metodo y drawdown.
- Data Quality Harness: analogias para fricciones, halts y realismo de
  ejecucion cuando haya data live.

## 10. Estado

`pass_with_warnings`

El paquete esta listo como tercer piloto comparativo. Requiere revision humana
antes de promocionar reglas a doctrina canonica TSIS.
"""
    write_text(OUT_DIR / "lesson_distillation.md", body)


def write_quality_report(lines, sections, image_records):
    promoted = [r for r in image_records if r["doctrine_relevance"] != "low"]
    missing = [r for r in image_records if r["resolution_status"] == "missing"]
    fallback = [r for r in image_records if r["resolution_status"] == "resolved_lesson_fallback"]
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
| images_resolved_lesson_fallback | {len(fallback)} |
| images_missing | {len(missing)} |
| images_read | {len(promoted)} |
| code_artifacts | {len([p for p in CODE_RELS if (SERSAN_ROOT / p).exists()])} |
| rules_extracted | {len(RULES)} |
| translations_created | {len(TRANSLATIONS)} |
| open_questions | {len(OPEN_QUESTIONS)} |
| blocking_issues | 0 |

## 2. Input Coverage

The complete markdown was sectionized from line 1 to line {len(lines)}. The
four EasyLanguage/TradeStation code artifacts are inventoried as associated
artifacts. PDFs are duplicate layout artifacts and subtitles/video are out of
scope per project instruction.

## 3. Asset Resolution

All {len(image_records)} image references resolve to local files under
`02_workshops/25-practice-15/img`. The source markdown uses `../img/...`
references, so all local assets are recorded as `resolved_lesson_fallback`.
The resolver URL-decodes refs such as `008%20-%20copia.png` before matching the
local file.

## 4. Sectionization Quality

The source has a small number of formal headings and long teaching segments.
This pilot uses semantic line ranges that are non-overlapping and cover the
whole file.

## 5. Image Reading Quality

All images are indexed. Images with `medium`, `high` or `critical` doctrine
relevance have notes in `image_evidence_notes/`. Low-relevance images are
structurally indexed but not individually OCR-read.

## 6. Mechanical Rule Quality

All rules in `mechanical_rules.yaml` include trigger, action, failure mode and
source anchors. No rule is marked `promoted`.

## 7. TSIS Translation Quality

Each rule has one translation candidate in `tsis_translation_map.csv`. Critical
and high-priority gates require human review before implementation.

## 8. Open Questions

Eight open questions are tracked in `open_questions.md`, mainly around
drawdown bands, volatility floors, risk conversion, costs/borrow, method
comparison and AlphaEvolve stress tests.

## 9. Blocking Issues

None.

## 10. Acceptance Decision

`pass_with_warnings`

Warnings:

- Code artifacts are inventoried but not compiled or semantically parsed.
- Low-relevance images are not individually OCR-read.
- Money-management rules are candidate doctrine until human review.
- Numeric examples come from the course context and should not be promoted as
  universal TSIS constants.
"""
    write_text(OUT_DIR / "quality_report.md", body)


def write_manifest(generated_at, lines, image_records):
    missing = [r for r in image_records if r["resolution_status"] == "missing"]
    fallback = [r for r in image_records if r["resolution_status"] == "resolved_lesson_fallback"]
    images_read = [r for r in image_records if r["doctrine_relevance"] != "low"]
    generator_path = ROOT / GENERATOR_REL
    manifest = {
        "contract_version": CONTRACT_VERSION,
        "generated_at_utc": generated_at,
        "generated_by": GENERATED_BY,
        "lesson_id": LESSON_ID,
        "practice_number": 15,
        "title": "Practice 15 - Money Management y Position Sizing",
        "status": "translated",
        "source_md": rel_posix(SRC_MD_REL),
        "workshop_dir": rel_posix(WORKSHOP_REL),
        "image_dir": rel_posix(IMAGE_DIR_REL),
        "pdf_role": "duplicate_md_or_layout_artifact",
        "video_role": "out_of_scope",
        "asset_resolution": {
            "resolver_version": "lesson_pack_resolver_v0_3",
            "image_refs_total": len(image_records),
            "resolved_direct": len([r for r in image_records if r["resolution_status"] == "resolved_direct"]),
            "resolved_lesson_fallback": len(fallback),
            "external_reference": 0,
            "missing": len(missing),
            "needs_human_review": len([r for r in image_records if r["requires_human_review"] == "true"]),
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
            "code_artifacts": len([p for p in CODE_RELS if (SERSAN_ROOT / p).exists()]),
            "xlsx_artifacts": 0,
            "rules": len(RULES),
            "translations": len(TRANSLATIONS),
            "open_questions": len(OPEN_QUESTIONS),
        },
        "known_issues": [
            "Third pilot; requires human review before canonical promotion.",
            "Code artifacts inventoried but not compiled or parsed in this pilot.",
            "Low-relevance images indexed structurally without full OCR.",
            "Numeric sizing examples are evidence, not universal TSIS constants.",
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
        {"path": project_rel(SRC_MD), "sha256": sha256_file(SRC_MD), "role": "source_markdown"},
        {"path": TOOLCHAIN_CONTRACT_REL, "sha256": sha256_file(ROOT / TOOLCHAIN_CONTRACT_REL), "role": "governing_contract"},
        {"path": SHARED_MANIFEST_REL, "sha256": sha256_file(ROOT / SHARED_MANIFEST_REL), "role": "shared_manifest_contract"},
        {"path": SHARED_VALIDATION_REL, "sha256": sha256_file(ROOT / SHARED_VALIDATION_REL), "role": "shared_validation_principles"},
        {"path": ARTIFACT_CONTRACT_REL, "sha256": sha256_file(ROOT / ARTIFACT_CONTRACT_REL), "role": "artifact_contract"},
        {"path": RUNBOOK_REL, "sha256": sha256_file(ROOT / RUNBOOK_REL), "role": "runbook"},
    ]
    for rel in CODE_RELS:
        artifact = SERSAN_ROOT / rel
        if artifact.exists():
            input_artifacts.append({"path": project_rel(artifact), "sha256": sha256_file(artifact), "role": "code_artifact"})
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
        "run_id": "2026-06-12_sersan_practice_15_revised_pilot_run_v0_3",
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
                "tool_id": "generate_sersan_p15_pilot",
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
            "Code artifacts are inventoried but not compiled or parsed.",
            "Low-relevance images are structurally indexed without full OCR.",
            "Candidate rules are not promoted doctrine.",
            "Numeric examples are evidence, not universal constants.",
        ],
    }
    write_text(OUT_DIR / "run_manifest.json", json.dumps(run_manifest, ensure_ascii=False, indent=2) + "\n")


def validate_outputs(lines, sections, image_records):
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
    if len(sections) != 20:
        raise ValueError("Unexpected section count")
    if sections[0]["line_start"] != 1 or sections[-1]["line_end"] != len(lines):
        raise ValueError("Section coverage failure")
    unresolved = [r for r in image_records if r["resolution_status"] == "missing"]
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
    validate_outputs(lines, sections, image_records)
    summary = {
        "lesson_id": LESSON_ID,
        "status": "pass_with_warnings",
        "sections": len(sections),
        "image_refs": len(image_records),
        "images_read": len([r for r in image_records if r["doctrine_relevance"] != "low"]),
        "resolved_lesson_fallback": len([r for r in image_records if r["resolution_status"] == "resolved_lesson_fallback"]),
        "rules": len(RULES),
        "translations": len(TRANSLATIONS),
        "out_dir": project_rel(OUT_DIR),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
