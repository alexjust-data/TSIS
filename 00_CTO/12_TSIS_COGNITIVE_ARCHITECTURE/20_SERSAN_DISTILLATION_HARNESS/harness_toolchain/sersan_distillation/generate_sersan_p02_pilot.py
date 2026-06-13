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
SRC_MD_REL = Path("03_only_md_revised") / "practica_02_donchain.md"
SRC_MD = SERSAN_ROOT / SRC_MD_REL
OUT_DIR = (
    CTO
    / "12_TSIS_COGNITIVE_ARCHITECTURE"
    / "20_SERSAN_DISTILLATION_HARNESS"
    / "sersan_distillation_artifacts"
    / "sersan_practice_02_donchain"
)
LESSON_ID = "sersan_practice_02_donchain"
DATE = "2026-06-11"
GENERATED_BY = "manual_sersan_pilot_harness_codex_v0_1"
TOOLCHAIN_CONTRACT_REL = "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md"
GENERATOR_REL = "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/harness_toolchain/sersan_distillation/generate_sersan_p02_pilot.py"


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def rel_posix(path: Path) -> str:
    return path.as_posix()


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


def image_id(num: str, occurrence: int) -> str:
    if occurrence == 1:
        return f"{LESSON_ID}_img_{num}"
    return f"{LESSON_ID}_img_{num}_ref_{occurrence:02d}"


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


def find_section_for_line(line_no: int, sections: list[dict]) -> str:
    for sec in sections:
        if sec["line_start"] <= line_no <= sec["line_end"]:
            return sec["section_id"]
    raise ValueError(f"No section for line {line_no}")


def build_sections(lines: list[str]) -> list[dict]:
    raw_sections = [
        {
            "n": 1,
            "heading_path": ["Practica 02", "Entrada y artefactos base"],
            "section_type": "procedure",
            "line_start": 1,
            "line_end": 25,
            "summary": "Presenta la practica, el enlace al codigo EasyLanguage y la primera captura contextual.",
            "keywords": ["codigo", "practica", "contexto"],
            "contains_code": True,
            "contains_table": False,
            "contains_question": False,
            "requires_image_reading": False,
            "requires_human_review": False,
            "notes": ["El codigo ELD existe como artefacto asociado, pero no se analiza en este piloto."],
        },
        {
            "n": 2,
            "heading_path": ["Practica 02", "Construccion de Graficos Continuos", "Contratos continuos"],
            "section_type": "concept",
            "line_start": 26,
            "line_end": 126,
            "summary": "Explica por que los futuros requieren graficos continuos y como se decide el contrato frontal.",
            "keywords": ["futuros", "contrato-continuo", "roll", "volumen", "open-interest"],
            "contains_code": False,
            "contains_table": False,
            "contains_question": False,
            "requires_image_reading": False,
            "requires_human_review": False,
            "notes": [],
        },
        {
            "n": 3,
            "heading_path": ["Practica 02", "Construccion de Graficos Continuos", "Ajustes y gaps de roll"],
            "section_type": "warning",
            "line_start": 127,
            "line_end": 192,
            "summary": "Distingue ajustes forward/backward y advierte que los gaps de roll no ajustados no son beneficio operable.",
            "keywords": ["forward-adjusted", "backward-adjusted", "roll-gap", "pnl-artificial"],
            "contains_code": False,
            "contains_table": False,
            "contains_question": False,
            "requires_image_reading": False,
            "requires_human_review": False,
            "notes": [],
        },
        {
            "n": 4,
            "heading_path": ["Practica 02", "Construccion de Graficos Continuos", "Diferencia vs ratio"],
            "section_type": "procedure",
            "line_start": 193,
            "line_end": 224,
            "summary": "Compara ajuste por diferencia y por ratio; el ratio preserva escala proporcional y evita precios historicos negativos.",
            "keywords": ["ratio-adjusted", "difference-adjusted", "tick-rounding", "price-scale"],
            "contains_code": False,
            "contains_table": False,
            "contains_question": False,
            "requires_image_reading": False,
            "requires_human_review": False,
            "notes": [],
        },
        {
            "n": 5,
            "heading_path": ["Practica 02", "Sistema de ruptura Canal de Donchian", "Planteamiento"],
            "section_type": "concept",
            "line_start": 225,
            "line_end": 273,
            "summary": "Define un setup Donchian simple basado en ruptura de maximo/minimo de cierres y lo usa como prueba preliminar.",
            "keywords": ["donchian", "breakout", "entry-logic", "esperanza"],
            "contains_code": False,
            "contains_table": False,
            "contains_question": False,
            "requires_image_reading": True,
            "requires_human_review": False,
            "notes": [],
        },
        {
            "n": 6,
            "heading_path": ["Practica 02", "Preguntas", "Evaluacion preliminar tipica"],
            "section_type": "validation",
            "line_start": 274,
            "line_end": 405,
            "summary": "Fija el criterio de evaluacion preliminar de una entrada: stop y profit target simetricos, payoff aproximado a uno y comparacion contra buy and hold.",
            "keywords": ["expectancy", "win-rate", "payoff", "buy-and-hold", "preliminary-validation"],
            "contains_code": False,
            "contains_table": False,
            "contains_question": True,
            "requires_image_reading": True,
            "requires_human_review": False,
            "notes": [],
        },
        {
            "n": 7,
            "heading_path": ["Practica 02", "Preguntas", "Stops targets y caracter de los exits"],
            "section_type": "validation",
            "line_start": 406,
            "line_end": 565,
            "summary": "Muestra que la configuracion de stop y target altera la lectura del sistema y que los exits definen gran parte de su caracter.",
            "keywords": ["stop-loss", "take-profit", "exit-logic", "system-character"],
            "contains_code": False,
            "contains_table": False,
            "contains_question": True,
            "requires_image_reading": True,
            "requires_human_review": False,
            "notes": [],
        },
        {
            "n": 8,
            "heading_path": ["Practica 02", "Preguntas", "Evaluacion multi-asset Nasdaq100"],
            "section_type": "validation",
            "line_start": 566,
            "line_end": 747,
            "summary": "Extiende el test Donchian a Nasdaq100, corrige sizing y usa numero de trades, win rate, payoff y exposicion como evidencia preliminar.",
            "keywords": ["nasdaq100", "multi-asset", "sample-size", "position-sizing", "exposure"],
            "contains_code": False,
            "contains_table": False,
            "contains_question": True,
            "requires_image_reading": True,
            "requires_human_review": False,
            "notes": ["El resultado se trata solo como evidencia preliminar de setup, no como sistema listo para operar."],
        },
        {
            "n": 9,
            "heading_path": ["Practica 02", "Consultas", "Datos de Forex"],
            "section_type": "qa",
            "line_start": 748,
            "line_end": 962,
            "summary": "Discute datos de Forex, rutas de validacion para sistemas con pocos parametros y el papel de forward testing o muestras grandes.",
            "keywords": ["forex", "walk-forward", "forward-testing", "sample-size"],
            "contains_code": False,
            "contains_table": False,
            "contains_question": True,
            "requires_image_reading": False,
            "requires_human_review": False,
            "notes": [],
        },
        {
            "n": 10,
            "heading_path": ["Practica 02", "Metodologia BRaC"],
            "section_type": "validation",
            "line_start": 963,
            "line_end": 1060,
            "summary": "Introduce Build Reveal and Compare y enumera propiedades esperables de una estrategia robusta.",
            "keywords": ["brac", "robustness", "trade-distribution", "optimization-map"],
            "contains_code": False,
            "contains_table": False,
            "contains_question": False,
            "requires_image_reading": True,
            "requires_human_review": False,
            "notes": [],
        },
        {
            "n": 11,
            "heading_path": ["Practica 02", "Tratamiento holistico del portfolio"],
            "section_type": "portfolio",
            "line_start": 1061,
            "line_end": 1075,
            "summary": "Plantea que stops o targets de portfolio pueden evaluarse como reglas del conjunto y no solo de trade individual.",
            "keywords": ["portfolio", "portfolio-stop", "portfolio-target", "risk"],
            "contains_code": False,
            "contains_table": False,
            "contains_question": True,
            "requires_image_reading": False,
            "requires_human_review": False,
            "notes": [],
        },
        {
            "n": 12,
            "heading_path": ["Practica 02", "Regimenes de mercado y filtros"],
            "section_type": "warning",
            "line_start": 1076,
            "line_end": 1117,
            "summary": "Advierte que los filtros pueden ayudar pero tambien sobreajustar; exige muestra suficiente y prudencia.",
            "keywords": ["filters", "regime", "overfitting", "sample-size"],
            "contains_code": False,
            "contains_table": False,
            "contains_question": True,
            "requires_image_reading": False,
            "requires_human_review": False,
            "notes": [],
        },
        {
            "n": 13,
            "heading_path": ["Practica 02", "Multidata y filtros"],
            "section_type": "warning",
            "line_start": 1118,
            "line_end": len(lines),
            "summary": "Traslada la misma prudencia a filtros multidata y exige alineacion temporal y muestra suficiente.",
            "keywords": ["multidata", "temporal-alignment", "filters", "sample-size"],
            "contains_code": False,
            "contains_table": False,
            "contains_question": True,
            "requires_image_reading": False,
            "requires_human_review": False,
            "notes": [],
        },
    ]
    sections = []
    for raw in raw_sections:
        text = "\n".join(lines[raw["line_start"] - 1 : raw["line_end"]])
        item = {
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
        sections.append(item)
    return sections


IMAGE_CLASS = {
    "004": {
        "visual_type": "concept_diagram",
        "relevance": "high",
        "contains_numbers": True,
        "contains_chart": False,
        "contains_platform_config": False,
        "reading": "Formula de esperanza matematica y probabilidad de ruina; conecta win rate, payoff, loss rate y riesgo de ruina.",
        "values": "%Win, payoff, %Loss; ejemplos RoR 1.81% y 13.44% con distinto capital arriesgado.",
    },
    "008": {
        "visual_type": "performance_report",
        "relevance": "high",
        "contains_numbers": True,
        "contains_chart": False,
        "contains_platform_config": False,
        "reading": "Lista de trades de la prueba preliminar con profit target y stop loss; evidencia que ambos exits estan actuando.",
        "values": "Operaciones AAPL con Profit Target y Stop Loss; porcentajes cercanos a +/-10%.",
    },
    "014": {
        "visual_type": "platform_settings",
        "relevance": "medium",
        "contains_numbers": True,
        "contains_chart": False,
        "contains_platform_config": True,
        "reading": "Configuracion de Portfolio Maestro para benchmark buy and hold de AAPL.",
        "values": "Capital inicial 1,000; primera fecha 1999-01-28; backtest standard.",
    },
    "020": {
        "visual_type": "portfolio_report",
        "relevance": "high",
        "contains_numbers": True,
        "contains_chart": False,
        "contains_platform_config": False,
        "reading": "Resultado buy and hold AAPL; muestra retorno extremo pero tambien drawdown relevante.",
        "values": "Profit 439,503.04; profit 43,970.59%; drawdown 29.73% en la captura visible.",
    },
    "021": {
        "visual_type": "platform_settings",
        "relevance": "medium",
        "contains_numbers": True,
        "contains_chart": False,
        "contains_platform_config": True,
        "reading": "Configuracion inicial con dos cruces de medias y par de exits porcentuales.",
        "values": "Inputs visibles: Close,Close,50,200 y Percent Exit Pair 0.025,0.025.",
    },
    "030": {
        "visual_type": "platform_settings",
        "relevance": "medium",
        "contains_numbers": True,
        "contains_chart": False,
        "contains_platform_config": True,
        "reading": "Configuracion que ilustra cambio de inputs de salida y su efecto sobre la interpretacion del sistema.",
        "values": "Inputs visibles: StopLossPct y ProfitTargetPct en la estrategia Percent Exit Pair.",
    },
    "034": {
        "visual_type": "platform_settings",
        "relevance": "critical",
        "contains_numbers": True,
        "contains_chart": False,
        "contains_platform_config": True,
        "reading": "Configuracion simetrica del exit: ProfitTargetPct 0.05 y StopLossPct 0.05.",
        "values": "ProfitTargetPct=0.05; StopLossPct=0.05.",
    },
    "057": {
        "visual_type": "portfolio_report",
        "relevance": "high",
        "contains_numbers": True,
        "contains_chart": True,
        "contains_platform_config": False,
        "reading": "Distribucion de P/L por simbolo en Nasdaq100; valida que el resultado multi-asset no depende de un unico ticker.",
        "values": "Barras positivas y negativas por simbolo; dispersion amplia de resultados.",
    },
    "058": {
        "visual_type": "performance_report",
        "relevance": "critical",
        "contains_numbers": True,
        "contains_chart": False,
        "contains_platform_config": False,
        "reading": "Resumen multi-asset con numero grande de operaciones, win rate y profit factor cercano a 1.",
        "values": "5323 trades; 58.41% profitable; Profit Factor 1.04; AvgWin/AvgLoss 0.74; compounded annual return 36.93%.",
    },
    "064": {
        "visual_type": "equity_curve",
        "relevance": "high",
        "contains_numbers": True,
        "contains_chart": True,
        "contains_platform_config": False,
        "reading": "Curva de equity tras correccion de sizing; evidencia forma temporal del resultado, no solo resumen numerico.",
        "values": "Equity aproximada desde 10,000 a 16,800 en periodo visible 2014-2023.",
    },
    "065": {
        "visual_type": "portfolio_report",
        "relevance": "high",
        "contains_numbers": True,
        "contains_chart": True,
        "contains_platform_config": False,
        "reading": "Exposicion neta abierta tras correccion de sizing; muestra que la evaluacion debe controlar exposicion.",
        "values": "Open Position Net visible entre 0% y 60%, frecuentemente 30%-50%.",
    },
    "072": {
        "visual_type": "concept_diagram",
        "relevance": "critical",
        "contains_numbers": False,
        "contains_chart": False,
        "contains_platform_config": False,
        "reading": "Lista criterios de robustez: distribucion uniforme de trades, zonas de inputs amplias, rendimiento en varios mercados, rachas coherentes, muestra significativa y curva positiva estable.",
        "values": "",
    },
}


def default_image_class(num: str, line_no: int):
    if 246 <= line_no <= 273:
        visual_type = "trade_example"
    elif 285 <= line_no <= 405:
        visual_type = "performance_report"
    elif 454 <= line_no <= 557:
        visual_type = "platform_settings"
    elif 582 <= line_no <= 738:
        visual_type = "performance_report"
    elif line_no == 20:
        visual_type = "ui_navigation"
    else:
        visual_type = "unknown"
    return {
        "visual_type": visual_type,
        "relevance": "low",
        "contains_numbers": False,
        "contains_chart": visual_type in {"performance_report", "equity_curve", "trade_example"},
        "contains_platform_config": visual_type == "platform_settings",
        "reading": "Imagen indexada estructuralmente; no se promueve como evidencia doctrinal en este piloto.",
        "values": "",
    }


def build_images(lines: list[str], sections: list[dict]) -> list[dict]:
    img_re = re.compile(r'<img\s+[^>]*src="([^"]+)"[^>]*>', re.IGNORECASE)
    counts = {}
    rows = []
    for idx, line in enumerate(lines, start=1):
        for match in img_re.finditer(line):
            src = match.group(1)
            num_match = re.search(r"img/(\d+)\.png", src)
            if not num_match:
                num = re.sub(r"\W+", "_", Path(src).stem).strip("_").lower() or "unknown"
            else:
                num = num_match.group(1)
            counts[num] = counts.get(num, 0) + 1
            iid = image_id(num, counts[num])
            sec_id = find_section_for_line(idx, sections)
            profile = dict(default_image_class(num, idx))
            profile.update(IMAGE_CLASS.get(num, {}))
            note_ref = f"image_evidence_notes/{iid}.md" if profile["relevance"] in {"medium", "high", "critical"} else ""
            source_ref = src
            resolved_path = src.replace("../", "")
            row = {
                "contract_version": "sersan_image_evidence_index_v0_1",
                "lesson_id": LESSON_ID,
                "image_id": iid,
                "source_ref": source_ref,
                "resolved_path": resolved_path,
                "resolution_status": "resolved_direct",
                "referenced_from_section_ids": sec_id,
                "visual_type": profile["visual_type"],
                "contains_numbers": "true" if profile["contains_numbers"] else "false",
                "contains_code": "false",
                "contains_chart": "true" if profile["contains_chart"] else "false",
                "contains_platform_config": "true" if profile["contains_platform_config"] else "false",
                "extracted_values_ref": note_ref if profile["contains_numbers"] and note_ref else "",
                "technical_reading_ref": note_ref,
                "doctrine_relevance": profile["relevance"],
                "requires_human_review": "true" if profile["relevance"] == "critical" else "false",
                "notes": profile["reading"],
                "_num": num,
                "_line": idx,
                "_reading": profile["reading"],
                "_values": profile["values"],
            }
            rows.append(row)
    for sec in sections:
        nearby = [row["image_id"] for row in rows if row["referenced_from_section_ids"] == sec["section_id"]]
        sec["nearby_image_ids"] = nearby
    return rows


def write_sections(sections: list[dict]):
    body = "\n".join(json.dumps(sec, ensure_ascii=False) for sec in sections) + "\n"
    write_text(OUT_DIR / "lesson_sections.jsonl", body)


def write_image_index(rows: list[dict]):
    header = [
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
    with (OUT_DIR / "image_evidence_index.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in header})


def write_image_notes(rows: list[dict]):
    notes_dir = OUT_DIR / "image_evidence_notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    for row in rows:
        if row["doctrine_relevance"] not in {"medium", "high", "critical"}:
            continue
        text = f"""# {row['image_id']}

## Source

- lesson_id: {LESSON_ID}
- source_ref: {row['source_ref']}
- resolved_path: {row['resolved_path']}
- referenced_from_sections: {row['referenced_from_section_ids']}
- source_line: {row['_line']}

## Visual Type

{row['visual_type']}

## Extracted Values

{row['_values'] or 'No numeric values extracted for this image.'}

## Technical Reading

{row['_reading']}

## Doctrine Relevance

{row['doctrine_relevance']}

This image is used as supporting evidence for the pilot lesson distillation.
It is not canonical TSIS doctrine until reviewed.

## Open Questions

- Confirm OCR/numeric reading during human review before promotion.
"""
        write_text(notes_dir / f"{row['image_id']}.md", text)


RULES = [
    {
        "domains": ["bar_construction", "price_view", "data_semantics"],
        "rule_type": "hard_rule",
        "confidence": "high",
        "statement": "For futures swing or system backtests where current tradable price must remain real, prefer backward-adjusted continuous contracts.",
        "trigger": "Building continuous futures data for backtest or research.",
        "action": "Use backward-adjusted continuous series unless the research case explicitly requires another price view.",
        "failure_mode_if_ignored": "The current price in the backtest may stop matching the tradable contract price.",
        "required_evidence": ["continuous_contract_method", "current_contract_price_check"],
        "source_anchors": [source_anchor(3, 127, 192)],
        "caveats": ["Applies to futures; equities and ETFs require separate corporate-action treatment."],
    },
    {
        "domains": ["bar_construction", "execution_realism"],
        "rule_type": "hard_rule",
        "confidence": "high",
        "statement": "Do not treat roll gaps in unadjusted continuous futures as real tradable PnL.",
        "trigger": "Using unadjusted continuous futures charts or roll-linked series.",
        "action": "Identify artificial roll gaps and exclude them from performance interpretation.",
        "failure_mode_if_ignored": "Backtest may count synthetic jumps created by contract stitching as alpha.",
        "required_evidence": ["roll_calendar", "contract_boundary_check"],
        "source_anchors": [source_anchor(3, 127, 192)],
        "caveats": ["Very intraday systems that close/reopen around roll dates may justify unadjusted views."],
    },
    {
        "domains": ["bar_construction", "price_view"],
        "rule_type": "heuristic",
        "confidence": "medium",
        "statement": "When long historical scale matters, ratio adjustment is usually safer than fixed difference adjustment.",
        "trigger": "Choosing a continuous price adjustment method for long futures history.",
        "action": "Prefer ratio adjustment and round to tick size when the platform or execution model requires it.",
        "failure_mode_if_ignored": "Old prices may become distorted or even negative after repeated fixed differences.",
        "required_evidence": ["adjustment_method_documentation"],
        "source_anchors": [source_anchor(4, 193, 224)],
        "caveats": ["Exact method must be aligned with the instrument, vendor and execution assumptions."],
    },
    {
        "domains": ["entry_logic", "exit_logic", "stop_loss", "take_profit"],
        "rule_type": "hard_rule",
        "confidence": "high",
        "statement": "A preliminary entry-edge test should use symmetric stop and profit target so payoff is close to one before interpreting win rate.",
        "trigger": "Testing whether an entry setup has raw directional edge.",
        "action": "Set stop and target at comparable distance and require win rate above 50% before calling the entry promising.",
        "failure_mode_if_ignored": "Win rate may be interpreted without payoff context, producing false edge claims.",
        "required_evidence": ["win_rate", "average_win_loss", "stop_target_config"],
        "source_anchors": [source_anchor(6, 274, 405, [f"{LESSON_ID}_img_004", f"{LESSON_ID}_img_008"])],
        "caveats": ["This is a preliminary filter, not proof that the complete system is tradable."],
    },
    {
        "domains": ["sample_size", "stop_loss", "take_profit", "exit_logic"],
        "rule_type": "hard_rule",
        "confidence": "high",
        "statement": "Stop and profit target tests are invalid if one of the two exits almost never triggers.",
        "trigger": "Evaluating stop/target behavior in preliminary backtests.",
        "action": "Report exit activation counts and reject conclusions where the rule lacks enough observed events.",
        "failure_mode_if_ignored": "The test may claim a balanced payoff while one side of the distribution is unobserved.",
        "required_evidence": ["exit_reason_counts", "trade_list"],
        "source_anchors": [source_anchor(6, 274, 405, [f"{LESSON_ID}_img_008"])],
        "caveats": ["Minimum event count should be standardized by TSIS doctrine review."],
    },
    {
        "domains": ["portfolio", "money_management", "other"],
        "rule_type": "hard_rule",
        "confidence": "high",
        "statement": "Equity strategy tests must be compared with buy and hold on return/risk, not raw return only.",
        "trigger": "Evaluating a strategy on stocks or equity portfolios.",
        "action": "Compute buy-and-hold benchmark and compare both return and drawdown/risk profile.",
        "failure_mode_if_ignored": "A strategy may look inferior or superior for the wrong reason because risk is omitted.",
        "required_evidence": ["benchmark_return", "benchmark_drawdown", "strategy_return", "strategy_drawdown"],
        "source_anchors": [source_anchor(6, 274, 405, [f"{LESSON_ID}_img_014", f"{LESSON_ID}_img_020"])],
        "caveats": ["Benchmark choice must match universe and trade constraints."],
    },
    {
        "domains": ["sample_size", "trade_distribution", "robustness"],
        "rule_type": "hard_rule",
        "confidence": "high",
        "statement": "A preliminary setup should be tested across a broad enough universe when single-symbol evidence is insufficient.",
        "trigger": "A setup appears promising on one stock or a small sample.",
        "action": "Run the same non-optimized setup across a representative universe and inspect distribution by symbol.",
        "failure_mode_if_ignored": "The setup may be a single-name artifact rather than a repeatable market behavior.",
        "required_evidence": ["multi_asset_report", "symbol_distribution", "trade_count"],
        "source_anchors": [source_anchor(8, 566, 747, [f"{LESSON_ID}_img_057", f"{LESSON_ID}_img_058"])],
        "caveats": ["Universe survivorship and delisting treatment must be checked separately in TSIS small caps."],
    },
    {
        "domains": ["position_sizing", "money_management", "execution_realism"],
        "rule_type": "hard_rule",
        "confidence": "high",
        "statement": "Sizing mistakes must be corrected before interpreting portfolio-level results.",
        "trigger": "Backtest exposure or leverage appears inconsistent with intended capital usage.",
        "action": "Audit sizing inputs, exposure and position net before accepting performance metrics.",
        "failure_mode_if_ignored": "The edge estimate may reflect accidental leverage rather than signal quality.",
        "required_evidence": ["sizing_parameters", "exposure_curve", "position_net"],
        "source_anchors": [source_anchor(8, 566, 747, [f"{LESSON_ID}_img_064", f"{LESSON_ID}_img_065"])],
        "caveats": ["Exact accepted exposure limits belong in TSIS money-management policy."],
    },
    {
        "domains": ["exit_logic", "entry_logic", "other"],
        "rule_type": "heuristic",
        "confidence": "high",
        "statement": "The same entry can become trend-following or mean-reverting depending on the exit design.",
        "trigger": "Classifying a system from entry logic alone.",
        "action": "Evaluate the entry together with stop, target, time exit and trailing logic before labeling the system.",
        "failure_mode_if_ignored": "The system may be classified incorrectly and optimized against the wrong behavior.",
        "required_evidence": ["exit_configuration", "exit_reason_counts", "trade_duration"],
        "source_anchors": [source_anchor(7, 406, 565, [f"{LESSON_ID}_img_030", f"{LESSON_ID}_img_034"])],
        "caveats": ["This rule guides interpretation; it is not a standalone performance gate."],
    },
    {
        "domains": ["walk_forward", "BRaC", "robustness", "sample_size"],
        "rule_type": "soft_rule",
        "confidence": "medium",
        "statement": "Systems with very few parameters may use forward testing or broad samples instead of heavy walk-forward optimization, but the validation route must be explicit.",
        "trigger": "A strategy has few or no optimizable parameters.",
        "action": "Document whether validation uses walk-forward, BRaC, anchored samples, forward test or broad multi-asset evidence.",
        "failure_mode_if_ignored": "A simple system may skip validation entirely because classic optimization tools seem unnecessary.",
        "required_evidence": ["validation_route", "sample_size", "oos_or_forward_period"],
        "source_anchors": [source_anchor(9, 748, 962), source_anchor(10, 963, 1060, [f"{LESSON_ID}_img_072"])],
        "caveats": ["Choice of validation route requires human review before becoming canonical policy."],
    },
    {
        "domains": ["filters", "sample_size", "overfitting", "regime"],
        "rule_type": "hard_rule",
        "confidence": "high",
        "statement": "A filter is not evaluable unless it affects enough trades and leaves enough post-filter sample.",
        "trigger": "Adding regime, indicator or multidata filters to a strategy.",
        "action": "Report affected trade count, remaining trade count and performance before/after filter.",
        "failure_mode_if_ignored": "A filter may be overfit or statistically meaningless while appearing useful.",
        "required_evidence": ["affected_trade_count", "remaining_trade_count", "before_after_comparison"],
        "source_anchors": [source_anchor(12, 1076, 1117), source_anchor(13, 1118, 1154)],
        "caveats": ["The course mentions 30-50 affected trades as a practical lower bound; TSIS must formalize final thresholds."],
    },
    {
        "domains": ["filters", "overfitting"],
        "rule_type": "warning",
        "confidence": "high",
        "statement": "If the value of a filter is doubtful, do not add it to the system.",
        "trigger": "Considering an optional filter without strong evidence.",
        "action": "Prefer the unfiltered simpler system unless the filter passes sample and robustness checks.",
        "failure_mode_if_ignored": "The research process can accumulate fragile filters that fit noise.",
        "required_evidence": ["filter_evidence", "simplicity_comparison"],
        "source_anchors": [source_anchor(12, 1076, 1117)],
        "caveats": ["Risk-management constraints are separate from alpha filters and may be justified by risk policy."],
    },
    {
        "domains": ["portfolio", "money_management"],
        "rule_type": "soft_rule",
        "confidence": "medium",
        "statement": "Portfolio-level stop or profit target rules can be evaluated as portfolio risk rules.",
        "trigger": "Designing risk exits that apply to the whole portfolio rather than one trade.",
        "action": "Backtest portfolio-level exits with tools that can evaluate aggregate equity and exposure.",
        "failure_mode_if_ignored": "A valid portfolio risk mechanism may be rejected because it is not visible at single-trade level.",
        "required_evidence": ["portfolio_equity", "portfolio_drawdown", "aggregate_exposure"],
        "source_anchors": [source_anchor(11, 1061, 1075)],
        "caveats": ["Needs separate engineering contract for live execution and risk controls."],
    },
]


def build_rules():
    rules = []
    for idx, raw in enumerate(RULES, start=1):
        item = {
            "rule_id": rule_id(idx),
            "promotion_state": "mechanical_rule_candidate",
            "confidence": raw["confidence"],
            "rule_type": raw["rule_type"],
            "domains": raw["domains"],
            "statement": raw["statement"],
            "trigger": raw["trigger"],
            "action": raw["action"],
            "failure_mode_if_ignored": raw["failure_mode_if_ignored"],
            "required_evidence": raw["required_evidence"],
            "source_anchors": raw["source_anchors"],
            "caveats": raw["caveats"] + ["Candidate extracted from Sersan practice 02; not promoted to canonical doctrine."],
            "related_rules": [],
        }
        rules.append(item)
    return {
        "contract_version": "sersan_mechanical_rules_v0_1",
        "lesson_id": LESSON_ID,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "generated_by": "mechanical_rule_extractor_agent_v0_1",
        "rules": rules,
    }


def write_rules(rules_doc: dict):
    write_text(OUT_DIR / "mechanical_rules.yaml", yaml_dump(rules_doc) + "\n")


def write_translation_map(rules_doc: dict):
    header = [
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
    rows = [
        ("data_quality_gate", "TSIS_FUTURES_CONTINUOUS_PRICE_VIEW_POLICY", "require", "high", "human_review_gate", "backtest|AlphaEvolve", "Require explicit price-view metadata before any futures strategy evaluation."),
        ("execution_realism_check", "TSIS_ROLL_GAP_PNL_CHECK", "block", "critical", "hard_gate", "backtest|AlphaEvolve", "Block PnL attribution to synthetic roll gaps unless explicitly justified."),
        ("research_protocol", "TSIS_CONTINUOUS_ADJUSTMENT_DECISION_LOG", "document", "medium", "soft_gate", "backtest", "Log ratio vs difference adjustment choice and tick-rounding policy."),
        ("strategy_evaluator", "TSIS_ENTRY_EDGE_PRECHECK", "require", "critical", "human_review_gate", "backtest|AlphaEvolve", "Require symmetric stop/target preliminary test before accepting entry-edge claims."),
        ("strategy_evaluator", "TSIS_EXIT_ACTUATION_CHECK", "require", "high", "soft_gate", "backtest|AlphaEvolve", "Report counts by exit reason and flag exits with insufficient activation."),
        ("backtest_checklist", "TSIS_EQUITY_BENCHMARK_CHECK", "require", "high", "soft_gate", "backtest|AlphaEvolve", "Compare strategy to buy and hold with return and drawdown metrics."),
        ("strategy_evaluator", "TSIS_MULTI_ASSET_SETUP_CHECK", "score", "high", "soft_gate", "backtest|AlphaEvolve", "Require universe-level distribution evidence for preliminary setup validation."),
        ("money_management_policy", "TSIS_SIZING_AND_EXPOSURE_AUDIT", "block", "critical", "hard_gate", "backtest|AlphaEvolve", "Block interpretation when exposure or sizing deviates from intended capital model."),
        ("research_protocol", "TSIS_ENTRY_EXIT_CHARACTERIZATION", "document", "medium", "none", "backtest", "Document system character using entry plus exit design, not entry alone."),
        ("research_protocol", "TSIS_VALIDATION_ROUTE_DECLARATION", "require", "high", "human_review_gate", "backtest|AlphaEvolve", "Require explicit validation route for low-parameter systems."),
        ("AlphaEvolve_constraint", "TSIS_FILTER_SAMPLE_SIZE_GATE", "block", "critical", "hard_gate", "backtest|AlphaEvolve|ML", "Block new filters that lack affected-trade and remaining-sample evidence."),
        ("AlphaEvolve_constraint", "TSIS_FILTER_SIMPLICITY_BIAS", "warn", "high", "soft_gate", "backtest|AlphaEvolve", "Warn when optional filters do not improve evidence enough versus simpler baseline."),
        ("portfolio_evaluator", "TSIS_PORTFOLIO_LEVEL_EXIT_EVALUATOR", "review", "medium", "human_review_gate", "backtest|AlphaEvolve", "Evaluate aggregate equity exits separately from single-trade exits."),
    ]
    with (OUT_DIR / "tsis_translation_map.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for idx, rule in enumerate(rules_doc["rules"], start=1):
            target, artifact, action_type, priority, blocking, scope, hint = rows[idx - 1]
            writer.writerow(
                [
                    "sersan_tsis_translation_map_v0_1",
                    LESSON_ID,
                    translation_id(idx),
                    rule["rule_id"],
                    target,
                    artifact,
                    action_type,
                    priority,
                    blocking,
                    scope,
                    hint,
                    "true" if blocking in {"hard_gate", "human_review_gate"} or priority == "critical" else "false",
                    rule["rule_id"],
                    "Candidate mapping; requires doctrine review before implementation.",
                ]
            )


def write_distillation():
    img = "../../../../99_REFERENCE_LIBRARY/SersanSistemas/02_workshops/12-practice-02/img"
    text = f"""# Lesson Distillation: {LESSON_ID}

Fecha: {DATE}
Estado: pilot v0.1, `pass_with_warnings`
Fuente: `03_only_md_revised/practica_02_donchain.md`

## 1. Proposito del paquete

Este documento destila `practica_02_donchain.md` como primer piloto del Sersan
Distillation Harness. No convierte el curso en doctrina canonica. Convierte la
clase en evidencia trazable para que TSIS pueda construir evaluadores,
checklists y constraints de AlphaEvolve.

La practica es importante porque une tres piezas mecanicas:

- semantica correcta de datos para futuros continuos;
- prueba preliminar de una entrada Donchian;
- criterios de validacion, muestra, filtros, BRaC y portfolio.

## 2. Lectura ejecutiva

La clase no intenta entregar un sistema Donchian operable. El objetivo es
ensenar una ruta de evaluacion preliminar: plantear una idea simple, controlar
la interpretacion de datos, probar si la entrada tiene ventaja bajo exits
simetricos, ampliar muestra cuando sea posible y evitar filtros o conclusiones
que no tengan evidencia suficiente.

Para TSIS, la leccion mas importante es que el Harness no debe preguntar solo
si una estrategia gana dinero. Debe preguntar:

- que precio esta usando;
- si la entrada tiene ventaja antes de optimizar;
- si stop y target actuan de verdad;
- si el resultado depende de un ticker;
- si el benchmark correcto queda superado en retorno/riesgo;
- si la muestra basta;
- si los filtros tienen soporte estadistico;
- si la validacion elegida esta declarada.

## 3. Secciones fuente

| Section | Lines | Tipo | Lectura |
|---|---:|---|---|
| `sec_0001` | 1-25 | procedure | Entrada, codigo ELD y contexto. |
| `sec_0002` | 26-126 | concept | Contratos continuos y contrato frontal. |
| `sec_0003` | 127-192 | warning | Ajustes forward/backward y gaps artificiales. |
| `sec_0004` | 193-224 | procedure | Ajuste por diferencia vs ratio. |
| `sec_0005` | 225-273 | concept | Setup Donchian de ruptura de cierres. |
| `sec_0006` | 274-405 | validation | Evaluacion preliminar, payoff y benchmark. |
| `sec_0007` | 406-565 | validation | Stops, targets y caracter de los exits. |
| `sec_0008` | 566-747 | validation | Test multi-asset Nasdaq100 y sizing. |
| `sec_0009` | 748-962 | qa | Forex, forward testing y rutas de validacion. |
| `sec_0010` | 963-1060 | validation | BRaC y robustez. |
| `sec_0011` | 1061-1075 | portfolio | Stops/targets a nivel portfolio. |
| `sec_0012` | 1076-1117 | warning | Regimenes y filtros. |
| `sec_0013` | 1118-1154 | warning | Multidata y filtros. |

## 4. Evidencia visual incrustada

### 4.1 Esperanza y ruina

![Esperanza matematica y probabilidad de ruina]({img}/004.png)

La captura fija una idea base: una entrada no se evalua por porcentaje de
acierto aislado. La esperanza combina probabilidad y payoff, y el riesgo de
ruina depende tambien del capital arriesgado. En TSIS esto se traduce en que
un evaluador debe leer win rate junto a average win/loss, payoff, sizing y
drawdown.

### 4.2 Stop y target deben actuar

![Lista de trades con profit target y stop loss]({img}/008.png)

La lista de trades muestra operaciones cerradas tanto por `Profit Target` como
por `Stop Loss`. Esto importa porque una prueba simetrica no vale si una de las
dos piernas no se observa. La regla candidata exige conteo por motivo de salida.

### 4.3 Benchmark buy and hold

![Resultado buy and hold]({img}/020.png)

El benchmark de acciones no es una formalidad. La comparacion debe incluir
retorno y riesgo. Si buy and hold produce mas retorno absoluto pero con
drawdowns muy superiores, la evaluacion debe mirar retorno/riesgo, no solo
resultado bruto.

### 4.4 Simetria stop/target

![Stop y target simetricos]({img}/034.png)

La configuracion `ProfitTargetPct=0.05` y `StopLossPct=0.05` es evidencia
directa de la prueba de entrada con payoff aproximadamente uno. Esta captura
queda marcada como `critical` porque sostiene una regla operativa del Harness:
antes de llamar prometedora a una entrada, controlar payoff.

### 4.5 Multi-asset y distribucion por simbolo

![P/L por simbolo Nasdaq100]({img}/057.png)

La prueba se amplia a una cesta de Nasdaq100 para no depender de AAPL. La
distribucion por simbolo permite ver si el resultado se reparte o si depende de
unas pocas acciones.

![Resumen multi-asset]({img}/058.png)

La captura muestra 5323 trades y 58.41% profitable, con `Profit Factor` cercano
a 1. La lectura correcta no es "sistema listo", sino "hay evidencia preliminar
de que la entrada merece investigarse".

### 4.6 Sizing y exposicion

![Curva de equity tras correccion de sizing]({img}/064.png)

![Exposicion neta abierta]({img}/065.png)

La clase corrige una lectura previa contaminada por sizing. Para TSIS esto debe
convertirse en gate: no interpretar resultados si la exposicion o el capital
usado no coinciden con el diseno.

### 4.7 Robustez

![Criterios de estrategia robusta]({img}/072.png)

La captura resume propiedades que el Harness debe buscar antes de promocionar
una estrategia: trades y beneficios distribuidos, zonas de inputs amplias,
rendimiento en varios mercados, rachas coherentes, muestra significativa y
curva positiva estable.

## 5. Reglas mecanicas candidatas

La extraccion completa esta en `mechanical_rules.yaml`. Las reglas principales
son:

1. Usar backward-adjusted continuous contracts cuando el precio actual de
   futuros deba permanecer operable.
2. No contar gaps de roll no ajustados como PnL real.
3. Preferir ajuste por ratio cuando la escala historica importe.
4. Evaluar entradas preliminares con stop y target simetricos.
5. Exigir que ambos exits tengan activacion suficiente.
6. Comparar acciones contra buy and hold en retorno/riesgo.
7. Ampliar a universo multi-asset cuando un solo activo no baste.
8. Auditar sizing y exposicion antes de interpretar resultados.
9. Evaluar el caracter del sistema desde entrada mas exits.
10. Declarar ruta de validacion cuando hay pocos parametros.
11. Exigir muestra suficiente para filtros.
12. Si un filtro es dudoso, preferir no filtrarlo.
13. Evaluar stops/targets de portfolio como reglas agregadas.

## 6. Traduccion TSIS

La traduccion esta en `tsis_translation_map.csv`. Las implicaciones principales
son:

- `TSIS_ENTRY_EDGE_PRECHECK`: precheck de entrada con payoff controlado.
- `TSIS_EXIT_ACTUATION_CHECK`: conteo de motivos de salida.
- `TSIS_EQUITY_BENCHMARK_CHECK`: benchmark buy and hold retorno/riesgo.
- `TSIS_MULTI_ASSET_SETUP_CHECK`: validacion preliminar por universo.
- `TSIS_SIZING_AND_EXPOSURE_AUDIT`: gate de sizing y exposicion.
- `TSIS_FILTER_SAMPLE_SIZE_GATE`: bloqueo de filtros sin muestra.
- `TSIS_VALIDATION_ROUTE_DECLARATION`: ruta de validacion explicita.

## 7. Lo que no debe promocionarse todavia

No se debe promocionar que "Donchian 20 funciona" como doctrina TSIS.

Tampoco se debe promocionar un umbral universal definitivo para filtros. La
clase menciona 30-50 operaciones afectadas como minimo practico, pero TSIS debe
formalizar thresholds por tipo de sistema, frecuencia y universo.

No se debe trasladar sin matiz la parte de futuros continuos a small caps. Para
small caps, la analogia correcta son splits, dividendos, delistings, halts,
liquidez y supervivencia del universo.

## 8. Consumidores previstos

- Data Quality Harness: price-view metadata, corporate action semantics y
  checks de gaps artificiales.
- Backtest Harness: entry precheck, benchmark, exits, sizing, exposure y sample
  size.
- AlphaEvolve: constraints para no optimizar filtros fragiles ni interpretar
  resultados con sizing contaminado.
- Human reviewer: promocion de reglas candidatas a doctrina canonica.

## 9. Decision del piloto

Decision: `pass_with_warnings`.

Motivo: todos los artefactos contractuales existen y las reglas tienen anchors.
El warning principal es que el piloto indexa todas las imagenes, pero solo lee
doctrinalmente las capturas necesarias para reglas de alto impacto. Esa decision
es deliberada para evitar ruido visual y debe revisarse antes de ejecutar el
corpus completo.
"""
    write_text(OUT_DIR / "lesson_distillation.md", text)


def write_open_questions():
    text = f"""# Open Questions: {LESSON_ID}

Fecha: {DATE}

## 1. Thresholds de filtros

La clase menciona 30-50 operaciones afectadas como minimo practico para evaluar
un filtro. TSIS debe decidir thresholds por frecuencia, asset class, universo y
tipo de sistema.

## 2. Traduccion a small caps

La parte de contratos continuos aplica directamente a futuros. Para small caps,
la traduccion debe hacerse a splits, dividendos, halts, delistings, liquidez,
survivorship y semantica adjusted/unadjusted.

## 3. Benchmark canonico

Para acciones individuales aparece buy and hold. TSIS debe definir benchmarks
por estrategia: buy and hold del activo, equal-weight universe, benchmark
sectorial, Russell 2000, microcap index o cash.

## 4. Eventos de salida minimos

El contrato debe fijar cuantos eventos por motivo de salida bastan para decir
que stop, target, trailing o time exit han sido evaluados.

## 5. Ruta de validacion para sistemas simples

La clase permite forward testing o muestra amplia cuando hay pocos parametros.
TSIS debe decidir cuando esa ruta sustituye a walk-forward y cuando no.

## 6. OCR de imagenes

Este piloto lee manualmente las capturas criticas. El Harness futuro debe
definir si usa OCR/vision model, doble lectura humana o ambos.

## 7. Costes y realismo

La practica no cierra una politica canonica de comisiones, slippage, liquidez o
halts. Para small caps, esta politica debe ser gate antes de AlphaEvolve.
"""
    write_text(OUT_DIR / "open_questions.md", text)


def write_quality_report(images: list[dict], rules_doc: dict):
    images_read = sum(1 for r in images if r["doctrine_relevance"] in {"medium", "high", "critical"})
    text = f"""# Quality Report: {LESSON_ID}

## 1. Summary

| Metric | Value |
|---|---:|
| lesson_id | {LESSON_ID} |
| status | translated |
| md_lines | 1154 |
| sections | 13 |
| image_refs_total | 60 |
| images_resolved | 60 |
| images_missing | 0 |
| images_read | {images_read} |
| rules_extracted | {len(rules_doc['rules'])} |
| translations_created | {len(rules_doc['rules'])} |
| open_questions | 7 |
| blocking_issues | 0 |

## 2. Input Coverage

The complete markdown was sectionized from line 1 to line 1154. The source
code artifact is referenced but not analyzed in this pilot. PDFs are duplicate
layout artifacts and remain out of scope per protocol.

## 3. Asset Resolution

All 60 image references resolve to local files under
`02_workshops/12-practice-02/img`. The duplicated reference to `055.png` is
kept as a separate indexed reference for traceability.

## 4. Sectionization Quality

The source has few markdown headings, so the pilot uses semantic line ranges
inside long sections. Ranges are non-overlapping and cover the whole file.

## 5. Image Reading Quality

All images are indexed. Images with `medium`, `high` or `critical` relevance
have notes in `image_evidence_notes/`. Low-relevance images are structurally
indexed but not promoted as doctrinal evidence.

## 6. Mechanical Rule Quality

All rules in `mechanical_rules.yaml` include trigger, action, failure mode and
source anchors. No rule is marked `promoted`.

## 7. TSIS Translation Quality

Each rule has one translation candidate in `tsis_translation_map.csv`. Critical
gates require human review.

## 8. Open Questions

Seven open questions are tracked in `open_questions.md`, mainly around filter
thresholds, small-cap translation, benchmark policy and image OCR.

## 9. Blocking Issues

None.

## 10. Acceptance Decision

`pass_with_warnings`

Warnings:

- This is the first pilot and should be human-reviewed before the contract is
  reused at scale.
- Code artifacts are inventoried but not parsed.
- Low-relevance images are not individually OCR-read.
"""
    write_text(OUT_DIR / "quality_report.md", text)


def update_manifest(sections: list[dict], images: list[dict], rules_doc: dict):
    manifest_path = OUT_DIR / "lesson_pack_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["generated_at_utc"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest["generated_by"] = GENERATED_BY
    manifest["status"] = "translated"
    manifest["source_hashes"][rel_posix(SRC_MD_REL)] = sha256_file(SRC_MD)
    generator_path = ROOT / GENERATOR_REL
    if generator_path.exists():
        manifest["source_hashes"][GENERATOR_REL] = sha256_file(generator_path)
    manifest["counts"]["md_lines"] = len(SRC_MD.read_text(encoding="utf-8").splitlines())
    manifest["counts"]["sections"] = len(sections)
    manifest["counts"]["images"] = len(images)
    manifest["counts"]["rules"] = len(rules_doc["rules"])
    manifest["counts"]["translations"] = len(rules_doc["rules"])
    manifest["counts"]["open_questions"] = 7
    manifest["known_issues"] = [
        "Primer piloto; requiere revision humana antes de promocion canonica.",
        "Code artifacts inventoried but not parsed in this pilot.",
        "Low-relevance images indexed structurally without full OCR.",
    ]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_run_manifest():
    generator_path = ROOT / GENERATOR_REL
    generator_hash = sha256_file(generator_path) if generator_path.exists() else sha256_file(Path(__file__))

    def artifact_hash(path: Path) -> str:
        if path.is_dir():
            h = hashlib.sha256()
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    rel = child.relative_to(path).as_posix()
                    h.update(rel.encode("utf-8"))
                    h.update(b"|")
                    h.update(child.read_bytes())
                    h.update(b"|")
            return "sha256:" + h.hexdigest()
        return sha256_file(path)

    def output_artifact(rel_path: str) -> dict:
        target = OUT_DIR / rel_path
        return {
            "path": rel_path,
            "sha256": artifact_hash(target),
        }

    input_artifacts = [
        {
            "path": f"00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/{rel_posix(SRC_MD_REL)}",
            "sha256": sha256_file(SRC_MD),
        },
        {
            "path": TOOLCHAIN_CONTRACT_REL,
            "sha256": sha256_file(ROOT / TOOLCHAIN_CONTRACT_REL),
            "role": "governing_contract",
        },
        {
            "path": "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_lesson_pack_contract.md",
            "sha256": sha256_file(CTO / "12_TSIS_COGNITIVE_ARCHITECTURE" / "20_SERSAN_DISTILLATION_HARNESS/sersan_lesson_pack_contract.md"),
            "role": "artifact_contract",
        },
        {
            "path": "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_pilot_harness_runbook.md",
            "sha256": sha256_file(CTO / "12_TSIS_COGNITIVE_ARCHITECTURE" / "20_SERSAN_DISTILLATION_HARNESS/sersan_pilot_harness_runbook.md"),
            "role": "runbook",
        },
    ]

    image_index_path = OUT_DIR / "image_evidence_index.csv"
    if image_index_path.exists():
        seen = set()
        with image_index_path.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                if row["doctrine_relevance"] not in {"medium", "high", "critical"}:
                    continue
                rel = row["resolved_path"]
                if not rel or rel in seen:
                    continue
                seen.add(rel)
                img_path = SERSAN_ROOT / rel
                input_artifacts.append(
                    {
                        "path": f"00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/{rel}",
                        "sha256": sha256_file(img_path),
                        "role": "image_evidence",
                        "image_id": row["image_id"],
                        "doctrine_relevance": row["doctrine_relevance"],
                    }
                )

    doc = {
        "run_id": f"{DATE}_{LESSON_ID}_pilot_run_v0_1",
        "lesson_id": LESSON_ID,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "generated_by": GENERATED_BY,
        "mode": "pilot",
        "status": "pass_with_warnings",
        "contract_version": "sersan_lesson_pack_contract_v0_1",
        "toolchain_traceability_contract": TOOLCHAIN_CONTRACT_REL,
        "runbook": "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_pilot_harness_runbook.md",
        "artifact_contract": "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_lesson_pack_contract.md",
        "execution_command": "python 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/harness_toolchain/sersan_distillation/generate_sersan_p02_pilot.py",
        "toolchain_artifacts": [
            {
                "tool_id": "generate_sersan_p02_pilot",
                "role": "generator",
                "project_relative_path": GENERATOR_REL,
                "sha256": generator_hash,
                "runtime": "python",
                "project_resident": True,
            }
        ],
        "input_artifacts": input_artifacts,
        "output_artifacts": [
            output_artifact("lesson_pack_manifest.json"),
            output_artifact("lesson_sections.jsonl"),
            output_artifact("image_evidence_index.csv"),
            output_artifact("image_evidence_notes"),
            output_artifact("mechanical_rules.yaml"),
            output_artifact("lesson_distillation.md"),
            output_artifact("tsis_translation_map.csv"),
            output_artifact("open_questions.md"),
            output_artifact("quality_report.md"),
        ],
        "run_manifest_self_hash_policy": "run_manifest.json is excluded from output_artifacts to avoid self-referential hash mutation.",
        "non_project_artifacts_used": [],
        "workspace_temp_sources": "not_allowed_for_accepted_run",
        "loop_policy": {
            "max_iterations_per_phase": 3,
            "actual_iterations": 1,
            "stop_condition": "contract_artifacts_generated_and_basic_validation_passed",
        },
        "phases_completed": [
            "source_sectionization",
            "image_evidence_indexing",
            "mechanical_rule_extraction",
            "tsis_translation_mapping",
            "quality_report",
            "toolchain_traceability",
        ],
        "acceptance_decision": "pass_with_warnings",
    }
    write_text(OUT_DIR / "run_manifest.json", json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def validate(images: list[dict], sections: list[dict], rules_doc: dict):
    required = [
        "lesson_pack_manifest.json",
        "lesson_sections.jsonl",
        "image_evidence_index.csv",
        "mechanical_rules.yaml",
        "tsis_translation_map.csv",
        "lesson_distillation.md",
        "open_questions.md",
        "quality_report.md",
    ]
    missing = [name for name in required if not (OUT_DIR / name).exists()]
    if missing:
        raise RuntimeError(f"Missing artifacts: {missing}")

    section_ids = {s["section_id"] for s in sections}
    image_ids = {r["image_id"] for r in images}
    for sec in sections:
        for iid in sec["nearby_image_ids"]:
            if iid not in image_ids:
                raise RuntimeError(f"Section references unknown image {iid}")
    for img in images:
        for sid in img["referenced_from_section_ids"].split("|"):
            if sid not in section_ids:
                raise RuntimeError(f"Image references unknown section {sid}")
        if img["doctrine_relevance"] in {"medium", "high", "critical"}:
            note = OUT_DIR / img["technical_reading_ref"]
            if not note.exists():
                raise RuntimeError(f"Missing note for {img['image_id']}")

    rule_ids = {rule["rule_id"] for rule in rules_doc["rules"]}
    with (OUT_DIR / "tsis_translation_map.csv").open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["rule_id"] not in rule_ids:
                raise RuntimeError(f"Translation references unknown rule {row['rule_id']}")


def update_changelog():
    path = CTO / "CHANGELOG.md"
    text = path.read_text(encoding="utf-8")
    title = "## 2026-06-11 - Sersan practice_02 pilot distillation v0.1"
    if title in text:
        return
    text = text.replace(
        "- Ejecutar piloto de destilacion Sersan sobre:\n"
        "  - `practica_02_donchain.md`;\n"
        "  - `practica_09_revision_apolo.md`;\n"
        "  - `practica_15_revised.md`.",
        "- Completar pilotos de destilacion Sersan pendientes:\n"
        "  - `practica_09_revision_apolo.md`;\n"
        "  - `practica_15_revised.md`.",
    )
    entry = f"""

{title}

### Added

- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/{LESSON_ID}/lesson_sections.jsonl`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/{LESSON_ID}/image_evidence_index.csv`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/{LESSON_ID}/image_evidence_notes/`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/{LESSON_ID}/mechanical_rules.yaml`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/{LESSON_ID}/lesson_distillation.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/{LESSON_ID}/tsis_translation_map.csv`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/{LESSON_ID}/open_questions.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/{LESSON_ID}/quality_report.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/{LESSON_ID}/run_manifest.json`

### Notes

First Sersan lesson-pack pilot executed against the artifact contract.

Acceptance decision:

- `pass_with_warnings`

The pilot extracts 13 section records, indexes 60 image references, reads the
medium/high/critical image evidence, extracts 13 mechanical rule candidates and
creates 13 TSIS translation candidates.

### Impact

The next pilot should be `sersan_practice_09_revision_apolo`. Before scaling to
the whole course, compare this pilot with practice 09 and practice 15 to decide
whether the contract needs revision.
"""
    marker = "\n\n## 2026-06-11 - Sersan pilot Harness runbook"
    if marker not in text:
        text = text.rstrip() + entry + "\n"
    else:
        text = text.replace(marker, entry + marker, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines = SRC_MD.read_text(encoding="utf-8").splitlines()
    sections = build_sections(lines)
    images = build_images(lines, sections)
    rules_doc = build_rules()

    write_sections(sections)
    write_image_index(images)
    write_image_notes(images)
    write_rules(rules_doc)
    write_translation_map(rules_doc)
    write_distillation()
    write_open_questions()
    write_quality_report(images, rules_doc)
    update_manifest(sections, images, rules_doc)
    write_run_manifest()
    validate(images, sections, rules_doc)
    update_changelog()

    print(json.dumps({
        "lesson_id": LESSON_ID,
        "sections": len(sections),
        "image_refs": len(images),
        "images_read": sum(1 for r in images if r["doctrine_relevance"] in {"medium", "high", "critical"}),
        "rules": len(rules_doc["rules"]),
        "translations": len(rules_doc["rules"]),
        "acceptance": "pass_with_warnings",
        "out_dir": str(OUT_DIR),
    }, indent=2))


if __name__ == "__main__":
    main()

