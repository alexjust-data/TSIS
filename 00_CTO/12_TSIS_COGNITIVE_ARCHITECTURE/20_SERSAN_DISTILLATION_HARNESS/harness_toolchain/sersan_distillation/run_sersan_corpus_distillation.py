from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import yaml
from PIL import Image


IMAGE_CSV_HEADER = [
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

TRANSLATION_CSV_HEADER = [
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

QUALITY_HEADINGS = [
    "# Quality Report: ",
    "## 1. Summary",
    "## 2. Input Coverage",
    "## 3. Asset Resolution",
    "## 4. Sectionization Quality",
    "## 5. Image Reading Quality",
    "## 6. Mechanical Rule Quality",
    "## 7. TSIS Translation Quality",
    "## 8. Open Questions",
    "## 9. Blocking Issues",
    "## 10. Acceptance Decision",
]

ALLOWED_DOMAINS = {
    "data_semantics",
    "price_view",
    "bar_construction",
    "setup_logic",
    "entry_logic",
    "exit_logic",
    "stop_loss",
    "take_profit",
    "filters",
    "optimization",
    "overfitting",
    "robustness",
    "BRaC",
    "walk_forward",
    "IS_OOS",
    "sample_size",
    "trade_distribution",
    "execution_realism",
    "commissions_slippage",
    "halts",
    "money_management",
    "position_sizing",
    "portfolio",
    "correlation",
    "regime",
    "market_microstructure",
    "small_caps_transfer",
    "AlphaEvolve_constraints",
    "other",
}

ALLOWED_SECTION_TYPES = {
    "concept",
    "procedure",
    "warning",
    "qa",
    "code_explanation",
    "optimization",
    "validation",
    "portfolio",
    "money_management",
    "execution_realism",
    "image_only_context",
    "unclear",
}

PROJECT_ROOT = None
SCRIPT_PATH = Path(__file__).resolve()
TOOLCHAIN_DIR = SCRIPT_PATH.parent


@dataclass
class Section:
    section_id: str
    heading_path: list[str]
    section_type: str
    line_start: int
    line_end: int
    text: str
    summary: str
    keywords: list[str]
    nearby_image_ids: list[str]
    contains_code: bool
    contains_table: bool
    contains_question: bool
    requires_image_reading: bool
    requires_human_review: bool
    notes: list[str]


@dataclass
class ImageRef:
    image_id: str
    source_ref: str
    line_number: int
    resolved_path: Path | None
    resolution_status: str
    visual_type: str
    contains_numbers: bool
    contains_code: bool
    contains_chart: bool
    contains_platform_config: bool
    doctrine_relevance: str
    requires_human_review: bool
    section_ids: list[str]
    note_ref: str
    metadata: dict[str, Any]
    notes: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def find_project_root() -> Path:
    current = SCRIPT_PATH
    for parent in [current, *current.parents]:
        if (parent / "PROJECT_RULES.md").exists() and (parent / "AGENTS.md").exists():
            return parent
    raise RuntimeError("Unable to locate TSIS project root from toolchain path")


def project_root() -> Path:
    global PROJECT_ROOT
    if PROJECT_ROOT is None:
        PROJECT_ROOT = find_project_root()
    return PROJECT_ROOT


def rel_project(path: Path) -> str:
    return path.resolve().relative_to(project_root().resolve()).as_posix()


def rel_corpus(path: Path, corpus_root: Path) -> str:
    return path.resolve().relative_to(corpus_root.resolve()).as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, payload: Any) -> None:
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def load_config() -> dict[str, Any]:
    return json.loads(read_text(TOOLCHAIN_DIR / "sersan_corpus_distillation_config.json"))


def harness_paths() -> dict[str, Path]:
    root = project_root()
    harness = root / "00_CTO" / "12_TSIS_COGNITIVE_ARCHITECTURE" / "20_SERSAN_DISTILLATION_HARNESS"
    return {
        "root": root,
        "cto": root / "00_CTO",
        "shared_kernel": root
        / "00_CTO"
        / "12_TSIS_COGNITIVE_ARCHITECTURE"
        / "00_SHARED_HARNESS_KERNEL",
        "harness": harness,
        "corpus_root": root / "00_CTO" / "99_REFERENCE_LIBRARY" / "SersanSistemas",
        "artifact_root": harness / "sersan_distillation_artifacts",
        "inventory_csv": harness
        / "sersan_distillation_artifacts"
        / "_corpus_inventory"
        / "sersan_corpus_manifest.csv",
    }


def load_inventory() -> list[dict[str, str]]:
    paths = harness_paths()
    with paths["inventory_csv"].open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def prohibited_path(path: str) -> bool:
    normalized = path.lower().replace("/", "\\")
    return (
        normalized.startswith("c:\\users\\")
        or normalized.startswith("c:\\tmp\\")
        or "\\downloads\\" in normalized
        or "\\appdata\\local\\temp\\" in normalized
    )


def git_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_root(),
            check=False,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def readiness_gate(config: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    paths = harness_paths()
    required_files = [
        paths["harness"] / "sersan_distillation_protocol.md",
        paths["harness"] / "sersan_lesson_pack_contract.md",
        paths["harness"] / "sersan_pilot_harness_runbook.md",
        paths["shared_kernel"] / "harness_toolchain_traceability_contract.md",
        paths["shared_kernel"] / "shared_run_manifest_contract.md",
        paths["shared_kernel"] / "shared_validation_principles.md",
        paths["inventory_csv"],
        SCRIPT_PATH,
        TOOLCHAIN_DIR / "validate_sersan_distillation.py",
        TOOLCHAIN_DIR / "sersan_corpus_distillation_config.json",
    ]
    errors: list[str] = []
    warnings: list[str] = []
    for path in required_files:
        if not path.exists():
            errors.append(f"missing required file: {rel_project(path) if path.is_absolute() else path}")
    if not paths["corpus_root"].exists():
        errors.append(f"missing corpus root: {paths['corpus_root']}")
    if not paths["artifact_root"].exists():
        errors.append(f"missing artifact root: {paths['artifact_root']}")

    branch = git_branch()
    if branch == "main":
        errors.append("git branch is main; TSIS rules require working branch for modifications")
    elif not branch:
        warnings.append("unable to determine git branch")

    inventory_rows: list[dict[str, str]] = []
    if paths["inventory_csv"].exists():
        inventory_rows = load_inventory()
        if len(inventory_rows) != 17:
            errors.append(f"inventory lesson_pack count is {len(inventory_rows)}; expected 17")
        for row in inventory_rows:
            source_md = paths["corpus_root"] / row["source_md"]
            if not source_md.exists():
                errors.append(f"missing source md for {row['lesson_id']}: {row['source_md']}")
            if row.get("status") == "inventory_only":
                warnings.append(f"{row['lesson_id']} is inventory_only and will be blocked locally")
            if row.get("missing") not in ("", "0", None):
                errors.append(f"{row['lesson_id']} has missing image refs in inventory: {row['missing']}")

    for path in [SCRIPT_PATH, TOOLCHAIN_DIR / "validate_sersan_distillation.py"]:
        if prohibited_path(str(path)):
            errors.append(f"toolchain path is prohibited: {path}")
        try:
            path.resolve().relative_to(project_root().resolve())
        except ValueError:
            errors.append(f"toolchain path is not project resident: {path}")

    report = {
        "generated_at_utc": utc_now(),
        "gate": "sersan_corpus_distillation_readiness_v0_1",
        "status": "fail" if errors else ("pass_with_warnings" if warnings else "pass"),
        "branch": branch,
        "lesson_packs_in_inventory": len(inventory_rows),
        "contracts_checked": [rel_project(p) for p in required_files if p.exists()],
        "errors": errors,
        "warnings": warnings,
        "decision": "continue" if not errors else "stop",
        "config": config,
    }
    return not errors, report


def write_readiness_report(report: dict[str, Any]) -> None:
    artifact_root = harness_paths()["artifact_root"]
    write_json(artifact_root / "_readiness_gate_report.json", report)
    lines = [
        "# Sersan Corpus Distillation Readiness Gate",
        "",
        f"Generated at UTC: `{report['generated_at_utc']}`",
        f"Status: `{report['status']}`",
        f"Decision: `{report['decision']}`",
        f"Branch: `{report.get('branch', '')}`",
        f"Lesson packs in inventory: `{report['lesson_packs_in_inventory']}`",
        "",
        "## Contracts Checked",
        "",
    ]
    lines.extend(f"- `{p}`" for p in report["contracts_checked"])
    lines.extend(["", "## Errors", ""])
    lines.extend(f"- {e}" for e in report["errors"]) if report["errors"] else lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {w}" for w in report["warnings"]) if report["warnings"] else lines.append("- None")
    write_text(artifact_root / "_readiness_gate_report.md", "\n".join(lines) + "\n")


def clean_heading(value: str) -> str:
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" #*-:\t\r\n")


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "untitled"


def extract_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        if line.startswith("#"):
            title = clean_heading(line)
            if title:
                return title
    return fallback


def classify_section(text: str, heading: str) -> str:
    blob = f"{heading}\n{text}".lower()
    if any(k in blob for k in ["pregunta", "consultas", "cuestiones", "dudas", "q&a"]):
        return "qa"
    if any(k in blob for k in ["money management", "position sizing", "sizing", "msa", "gestion monetaria", "capital", "risk ="]):
        return "money_management"
    if any(k in blob for k in ["portfolio", "cartera", "diversific", "correlacion", "rebalance", "frontera eficiente"]):
        return "portfolio"
    if any(k in blob for k in ["halt", "slippage", "comision", "commission", "fill", "ejecucion", "tick de apertura", "imposible operar"]):
        return "execution_realism"
    if any(k in blob for k in ["optimiz", "optimizer", "maestro", "fitness", "tsi", "ppc", "sortino", "mapa", "walk forward", "all data", "out of sample", "in sample"]):
        return "optimization"
    if any(k in blob for k in ["brac", "robust", "oos", "is/oos", "validacion", "sample", "muestra", "compare", "reveal"]):
        return "validation"
    if any(k in blob for k in ["strategy", ".eld", "function", "input:", "vars:", "setstop", "buy next bar", "sellshort", "code"]):
        return "code_explanation"
    if any(k in blob for k in ["evitar", "error", "peligro", "trampa", "sobreoptim", "overfit", "no se debe", "no deberia"]):
        return "warning"
    if any(k in blob for k in ["paso", "proceso", "implement", "configur", "aplicacion", "setup", "entrada", "salida", "filtro", "stop"]):
        return "procedure"
    return "concept" if len(blob.strip()) > 80 else "unclear"


def infer_keywords(text: str) -> list[str]:
    keys: list[str] = []
    mapping = {
        "donchian": ["donchian", "canal"],
        "orb": ["orb", "opening range", "first-hour"],
        "bollinger": ["bollinger"],
        "aberration": ["aberration"],
        "optimization": ["optimiz", "maestro", "fitness", "tsi", "ppc", "sortino"],
        "robustness": ["robust"],
        "is_oos": ["out of sample", "oos", "in sample", "all data"],
        "walk_forward": ["walk forward"],
        "brac": ["brac", "build", "reveal", "compare"],
        "execution": ["halt", "slippage", "comision", "fill", "ejecucion"],
        "money_management": ["money management", "sizing", "msa", "risk", "capital"],
        "portfolio": ["portfolio", "cartera", "diversific", "correlacion"],
        "filters": ["filtro", "filter"],
        "entry": ["entrada", "entry", "breakout", "ruptura"],
        "exit": ["salida", "exit", "stop", "profit", "trailing", "chandelier"],
        "regime": ["regimen", "vix", "cot"],
    }
    blob = text.lower()
    for key, needles in mapping.items():
        if any(n in blob for n in needles):
            keys.append(key)
    return keys[:12] or ["source_context"]


def section_summary(heading: str, text: str, section_type: str) -> str:
    compressed = re.sub(r"\s+", " ", text).strip()
    if len(compressed) > 180:
        compressed = compressed[:177].rstrip() + "..."
    heading = clean_heading(heading) or "Unheaded section"
    return f"{heading}. Section classified as {section_type}. {compressed}".strip()


def contains_code(text: str) -> bool:
    blob = text.lower()
    return "```" in text or any(k in blob for k in [".eld", "strategy", "input:", "vars:", "setstop", "buy next bar", "sellshort"])


def contains_table(text: str) -> bool:
    return "<table" in text.lower() or bool(re.search(r"^\s*\|.+\|\s*$", text, flags=re.MULTILINE))


def extract_image_refs(lines: list[str]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    md_re = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
    html_re = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.IGNORECASE)
    for idx, line in enumerate(lines, start=1):
        for match in md_re.finditer(line):
            refs.append({"source_ref": match.group(1).strip(), "line_number": idx})
        for match in html_re.finditer(line):
            refs.append({"source_ref": match.group(1).strip(), "line_number": idx})
    return refs


def resolve_image(source_ref: str, source_md_abs: Path, image_dir_abs: Path | None, corpus_root: Path) -> tuple[Path | None, str]:
    ref = unquote(source_ref.strip().strip('"').strip("'"))
    if re.match(r"^https?://", ref, flags=re.IGNORECASE):
        return None, "external_reference"
    ref = ref.split("#", 1)[0].split("?", 1)[0]
    direct = (source_md_abs.parent / ref.replace("/", "\\")).resolve()
    if direct.exists():
        return direct, "resolved_direct"
    cross_workshop = re.search(r"([0-9]{2}-practice-[0-9]{2})[\\/](.+)$", ref)
    if cross_workshop:
        candidate = (corpus_root / "02_workshops" / cross_workshop.group(1) / cross_workshop.group(2).replace("/", "\\")).resolve()
        if candidate.exists():
            return candidate, "resolved_lesson_fallback"
    if image_dir_abs is not None and image_dir_abs.exists():
        basename = Path(ref).name
        fallback = image_dir_abs / basename
        if fallback.exists():
            return fallback.resolve(), "resolved_lesson_fallback"
        numeric = re.match(r"^(\d+)(\.[A-Za-z0-9]+)$", basename)
        if numeric:
            padded = f"{int(numeric.group(1)):03d}{numeric.group(2)}"
            padded_fallback = image_dir_abs / padded
            if padded_fallback.exists():
                return padded_fallback.resolve(), "resolved_lesson_fallback"
        matches = list(image_dir_abs.rglob(basename))
        if matches:
            return matches[0].resolve(), "resolved_lesson_fallback"
        if numeric:
            padded_matches = list(image_dir_abs.rglob(padded))
            if padded_matches:
                return padded_matches[0].resolve(), "resolved_lesson_fallback"
    return None, "missing"


def get_image_metadata(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    metadata: dict[str, Any] = {
        "project_relative_path": rel_project(path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }
    try:
        with Image.open(path) as img:
            metadata.update(
                {
                    "format": img.format,
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                }
            )
    except Exception as exc:
        metadata["image_open_error"] = str(exc)
    return metadata


def classify_visual(source_ref: str, section_text: str) -> tuple[str, bool, bool, bool, bool, str, bool, str]:
    blob = f"{source_ref}\n{section_text}".lower()
    visual_type = "unknown"
    if any(k in blob for k in ["optimization", "optimiz", "mapa", "heat", "tsi", "ppc", "set", "var_", "fitness"]):
        visual_type = "optimization_map"
    elif any(k in blob for k in ["excel", "xlsx", "tabla", "pivot"]):
        visual_type = "excel_parameter_grid"
    elif any(k in blob for k in ["performance report", "report", "maestro", "metric", "net profit", "profit factor"]):
        visual_type = "performance_report"
    elif any(k in blob for k in ["equity", "curva"]):
        visual_type = "equity_curve"
    elif any(k in blob for k in ["drawdown", "dd"]):
        visual_type = "drawdown_curve"
    elif any(k in blob for k in ["portfolio", "cartera"]):
        visual_type = "portfolio_report"
    elif any(k in blob for k in ["tradestation", "multicharts", "settings", "config", "menu", "input"]):
        visual_type = "platform_settings"
    elif any(k in blob for k in ["codigo", "code", ".eld", "strategy", "function"]):
        visual_type = "code_screenshot"
    elif any(k in blob for k in ["trade", "entrada", "salida", "stop", "profit", "breakout", "ruptura"]):
        visual_type = "trade_example"
    elif any(k in blob for k in ["halt", "slippage", "fill", "comision", "ejecucion"]):
        visual_type = "execution_anomaly"

    contains_code_value = visual_type == "code_screenshot"
    contains_chart_value = visual_type in {
        "optimization_map",
        "performance_report",
        "equity_curve",
        "drawdown_curve",
        "portfolio_report",
        "trade_example",
    }
    contains_platform = visual_type in {"platform_settings", "code_screenshot"}
    contains_numbers_value = bool(re.search(r"\d", blob)) or visual_type in {
        "optimization_map",
        "excel_parameter_grid",
        "fitness_summary",
        "performance_report",
        "equity_curve",
        "drawdown_curve",
        "portfolio_report",
        "platform_settings",
        "execution_anomaly",
    }

    if any(k in blob for k in ["halt", "sobreoptim", "overfit", "drawdown", "msa", "money management", "position sizing", "imposible"]):
        relevance = "critical"
    elif visual_type in {"optimization_map", "excel_parameter_grid", "performance_report", "equity_curve", "drawdown_curve", "portfolio_report", "execution_anomaly"}:
        relevance = "high"
    elif visual_type in {"platform_settings", "code_screenshot", "trade_example"}:
        relevance = "medium"
    else:
        relevance = "low"

    requires_review = relevance in {"critical", "high"} or (contains_numbers_value and relevance in {"medium", "high", "critical"})
    note = "automated contextual image reading; numeric OCR not performed"
    return (
        visual_type,
        contains_numbers_value,
        contains_code_value,
        contains_chart_value,
        contains_platform,
        relevance,
        requires_review,
        note,
    )


def build_sections(lesson_id: str, md_text: str) -> list[Section]:
    lines = md_text.splitlines()
    heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    headings: list[tuple[int, int, str, list[str]]] = []
    stack: list[tuple[int, str]] = []
    in_fence = False
    for idx, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
        if in_fence:
            continue
        match = heading_re.match(line)
        if not match:
            continue
        level = len(match.group(1))
        title = clean_heading(match.group(2))
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        headings.append((idx, level, title, [item[1] for item in stack]))

    if not headings:
        text = "\n".join(lines)
        stype = classify_section(text, "Unheaded lesson")
        return [
            Section(
                section_id=f"{lesson_id}_sec_0001",
                heading_path=["Unheaded lesson"],
                section_type=stype,
                line_start=1,
                line_end=max(1, len(lines)),
                text=text,
                summary=section_summary("Unheaded lesson", text, stype),
                keywords=infer_keywords(text),
                nearby_image_ids=[],
                contains_code=contains_code(text),
                contains_table=contains_table(text),
                contains_question="?" in text,
                requires_image_reading=False,
                requires_human_review=stype in {"unclear", "execution_realism"},
                notes=[],
            )
        ]

    sections: list[Section] = []
    for pos, (start, _level, title, heading_path) in enumerate(headings, start=1):
        end = headings[pos][0] - 1 if pos < len(headings) else len(lines)
        text = "\n".join(lines[start - 1 : end])
        stype = classify_section(text, title)
        needs_image = bool(re.search(r"!\[|<img", text, flags=re.IGNORECASE)) or stype in {
            "optimization",
            "validation",
            "portfolio",
            "money_management",
            "execution_realism",
        }
        human = stype in {"unclear", "execution_realism"} or any(
            k in text.lower() for k in ["sobreoptim", "halt", "drawdown", "money management", "imposible", "msa"]
        )
        sections.append(
            Section(
                section_id=f"{lesson_id}_sec_{pos:04d}",
                heading_path=heading_path,
                section_type=stype if stype in ALLOWED_SECTION_TYPES else "unclear",
                line_start=start,
                line_end=end,
                text=text,
                summary=section_summary(title, text, stype),
                keywords=infer_keywords(text),
                nearby_image_ids=[],
                contains_code=contains_code(text),
                contains_table=contains_table(text),
                contains_question="?" in text or stype == "qa",
                requires_image_reading=needs_image,
                requires_human_review=human,
                notes=[],
            )
        )
    return sections


def section_for_line(sections: list[Section], line_number: int) -> Section | None:
    for section in sections:
        if section.line_start <= line_number <= section.line_end:
            return section
    return None


def build_images(
    lesson_id: str,
    refs: list[dict[str, Any]],
    sections: list[Section],
    source_md_abs: Path,
    image_dir_abs: Path | None,
    corpus_root: Path,
) -> list[ImageRef]:
    images: list[ImageRef] = []
    for idx, ref in enumerate(refs, start=1):
        image_id = f"{lesson_id}_img_{idx:04d}"
        section = section_for_line(sections, ref["line_number"])
        section_text = section.text if section else ""
        resolved, status = resolve_image(ref["source_ref"], source_md_abs, image_dir_abs, corpus_root)
        (
            visual_type,
            contains_numbers_value,
            contains_code_value,
            contains_chart_value,
            contains_platform,
            relevance,
            requires_review,
            note,
        ) = classify_visual(ref["source_ref"], section_text)
        if status == "missing":
            requires_review = True
            relevance = "high" if relevance == "low" else relevance
        section_ids = [section.section_id] if section else []
        note_ref = f"image_evidence_notes/{image_id}.md"
        images.append(
            ImageRef(
                image_id=image_id,
                source_ref=ref["source_ref"],
                line_number=ref["line_number"],
                resolved_path=resolved,
                resolution_status=status,
                visual_type=visual_type,
                contains_numbers=contains_numbers_value,
                contains_code=contains_code_value,
                contains_chart=contains_chart_value,
                contains_platform_config=contains_platform,
                doctrine_relevance=relevance,
                requires_human_review=requires_review,
                section_ids=section_ids,
                note_ref=note_ref,
                metadata=get_image_metadata(resolved),
                notes=note,
            )
        )
    section_map = {s.section_id: s for s in sections}
    for image in images:
        for section_id in image.section_ids:
            if section_id in section_map:
                section_map[section_id].nearby_image_ids.append(image.image_id)
                if image.doctrine_relevance in {"medium", "high", "critical"}:
                    section_map[section_id].requires_image_reading = True
                if image.requires_human_review:
                    section_map[section_id].requires_human_review = True
    return images


def infer_domains(section: Section) -> list[str]:
    blob = f"{' '.join(section.heading_path)}\n{section.text}".lower()
    domains: list[str] = []
    add = domains.append
    if any(k in blob for k in ["continuous", "continuo", "ajust", "roll", "contrato", "base diaria", "intradiaria", "1440"]):
        add("bar_construction")
        add("price_view")
    if any(k in blob for k in ["entrada", "entry", "breakout", "ruptura", "donchian", "orb", "bollinger", "aberration", "parabolic", "tomorrow"]):
        add("setup_logic")
        add("entry_logic")
    if any(k in blob for k in ["salida", "exit", "stop", "profit", "trailing", "chandelier", "break-even", "parabolicsar"]):
        add("exit_logic")
        if "stop" in blob:
            add("stop_loss")
        if "profit" in blob:
            add("take_profit")
    if any(k in blob for k in ["filtro", "filter", "narrow", "wide spread", "volatilidad", "atr"]):
        add("filters")
    if any(k in blob for k in ["optimiz", "maestro", "fitness", "tsi", "ppc", "sortino", "mapa", "set", "param"]):
        add("optimization")
    if any(k in blob for k in ["overfit", "sobreoptim", "8.000", "8000"]):
        add("overfitting")
    if any(k in blob for k in ["robust", "vecindad", "zona"]):
        add("robustness")
    if "brac" in blob or ("build" in blob and "reveal" in blob and "compare" in blob):
        add("BRaC")
    if any(k in blob for k in ["walk forward", "walk-forward"]):
        add("walk_forward")
    if any(k in blob for k in ["out of sample", "in sample", "all data", "oos", "is/oos"]):
        add("IS_OOS")
    if any(k in blob for k in ["muestra", "sample", "trades", "total trades"]):
        add("sample_size")
        add("trade_distribution")
    if any(k in blob for k in ["halt", "slippage", "comision", "commission", "fill", "ejecucion", "tick de apertura"]):
        add("execution_realism")
        if "halt" in blob:
            add("halts")
        if any(k in blob for k in ["slippage", "comision", "commission"]):
            add("commissions_slippage")
    if any(k in blob for k in ["money management", "position sizing", "sizing", "msa", "capital", "risk", "riesgo"]):
        add("money_management")
        add("position_sizing")
    if any(k in blob for k in ["portfolio", "cartera", "diversific", "correlacion", "rebalance", "frontera"]):
        add("portfolio")
        if "correl" in blob:
            add("correlation")
    if any(k in blob for k in ["regimen", "regime", "vix", "cot"]):
        add("regime")
    if any(k in blob for k in ["microstructure", "spread", "liquidez", "liquidity"]):
        add("market_microstructure")
    if any(k in blob for k in ["alphaevolve", "evolve", "evolut"]):
        add("AlphaEvolve_constraints")
    clean = []
    for domain in domains or ["other"]:
        if domain in ALLOWED_DOMAINS and domain not in clean:
            clean.append(domain)
    return clean[:6]


def rule_template(section: Section, domains: list[str]) -> dict[str, str | list[str]]:
    heading = " > ".join(section.heading_path)
    if any(d in domains for d in ["overfitting", "optimization", "robustness", "IS_OOS", "walk_forward", "BRaC"]):
        return {
            "statement": "Do not accept an optimized parameter or system variant from this section by rank alone; require robust-zone evidence, validation split evidence and neighboring-parameter review.",
            "trigger": "Selecting or validating parameters, filters or variants after an optimization/review workflow.",
            "action": "Record IS/OOS or comparable validation evidence, local stability and selection rationale before the candidate can feed TSIS evaluators or AlphaEvolve.",
            "failure": "The selected result may be an isolated optimum, an overfit map artifact or a visually attractive but unstable candidate.",
            "evidence": ["optimization_map", "IS_OOS_comparison", "neighbor_parameter_stability", "selection_rationale"],
        }
    if any(d in domains for d in ["execution_realism", "halts", "commissions_slippage"]):
        return {
            "statement": "Execution assumptions discussed in this section must be translated into explicit costs, halt/fill constraints or rejection checks before strategy evaluation.",
            "trigger": "A backtest, report or code path depends on fills, stops, commissions, slippage, opening ticks or halt behavior.",
            "action": "Require an execution realism check and mark impossible or non-executable fills before accepting the backtest result.",
            "failure": "The strategy may report profits from fills, prices or costs that would not exist in live trading.",
            "evidence": ["execution_assumption", "cost_model", "halt_or_fill_review"],
        }
    if any(d in domains for d in ["money_management", "position_sizing"]):
        return {
            "statement": "Money-management or sizing effects from this section must be evaluated separately from raw strategy edge and with drawdown/aggressiveness sensitivity.",
            "trigger": "A candidate changes position size, risk fraction, reinvestment, MSA parameters or capital allocation.",
            "action": "Report raw-edge metrics and sizing-adjusted metrics separately, including drawdown, worst loss, streak and risk denominator assumptions.",
            "failure": "Position sizing can make weak edge look attractive or hide unacceptable drawdown and capital risk.",
            "evidence": ["raw_trade_export", "sizing_formula", "drawdown_sensitivity", "risk_denominator"],
        }
    if any(d in domains for d in ["portfolio", "correlation"]):
        return {
            "statement": "Portfolio claims from this section must be evaluated as marginal contribution under correlation, drawdown and allocation constraints.",
            "trigger": "Combining systems, symbols, markets, families or capital allocations into a portfolio.",
            "action": "Measure diversification, correlation, marginal drawdown contribution, allocation method and rebalance assumptions before promotion.",
            "failure": "A portfolio can look robust through accidental diversification, hidden concentration or unstable allocation assumptions.",
            "evidence": ["portfolio_report", "correlation_review", "allocation_policy", "drawdown_contribution"],
        }
    if any(d in domains for d in ["exit_logic", "stop_loss", "take_profit"]):
        return {
            "statement": "Exit, stop and profit logic from this section must be declared as part of the strategy contract before comparing results.",
            "trigger": "A system variant changes stop, profit, trailing, time exit, break-even or opposite-channel exit behavior.",
            "action": "Version the exit policy and compare variants under the same data, cost and validation assumptions.",
            "failure": "Backtest comparisons may attribute edge to entries when the result is driven by untracked exit policy changes.",
            "evidence": ["exit_policy", "variant_comparison", "cost_model"],
        }
    if any(d in domains for d in ["filters", "setup_logic", "entry_logic"]):
        return {
            "statement": "Entry/setup filters from this section must be tested as explicit optional components with sample-size and robustness impact recorded.",
            "trigger": "Adding or modifying an entry, setup, filter or market-condition gate.",
            "action": "Measure before/after impact, trade-count change, stability across periods and interaction with other filters.",
            "failure": "Stacked filters can reduce sample size, overfit the lesson example or hide a non-causal proxy.",
            "evidence": ["baseline_comparison", "filter_delta", "sample_size", "robustness_check"],
        }
    if any(d in domains for d in ["bar_construction", "price_view", "data_semantics"]):
        return {
            "statement": "Data representation choices from this section must be declared before using results as strategy evidence.",
            "trigger": "A lesson uses adjusted series, continuous contracts, intraday/daily alignment, roll handling or alternate bar construction.",
            "action": "Record price view, bar construction, adjustment method and downstream limitations in the candidate evaluation.",
            "failure": "PnL, signals or labels can be contaminated by hidden data semantics such as roll gaps or mismatched bars.",
            "evidence": ["price_view", "bar_construction", "adjustment_policy"],
        }
    if section.contains_code:
        return {
            "statement": "Code shown in this section is source evidence, not TSIS production logic, until translated into project-resident code with tests.",
            "trigger": "Using lesson code, platform screenshots or EasyLanguage/TradeStation artifacts as implementation basis.",
            "action": "Preserve source behavior, translate assumptions explicitly and add tests before any TSIS implementation.",
            "failure": "Platform-specific semantics can be copied incorrectly or promoted without reproducible TSIS validation.",
            "evidence": ["source_code_artifact", "translation_notes", "tests"],
        }
    return {
        "statement": f"Treat the claim in section '{heading}' as a source observation until a reviewer maps it to a concrete TSIS evaluator, policy or checklist.",
        "trigger": "Using this lesson content as evidence for TSIS design.",
        "action": "Keep the claim anchored and require human review before promoting it beyond documentation.",
        "failure": "Contextual teaching material may be overgeneralized into project doctrine.",
        "evidence": ["source_anchor", "human_review"],
    }


def rule_type_for(domains: list[str], section: Section) -> str:
    if any(d in domains for d in ["execution_realism", "halts", "overfitting", "data_semantics", "price_view"]):
        return "hard_rule"
    if any(d in domains for d in ["money_management", "position_sizing", "portfolio", "commissions_slippage"]):
        return "warning"
    if section.section_type == "qa" or "other" in domains:
        return "heuristic"
    return "soft_rule"


def extract_rules(lesson_id: str, source_md: str, sections: list[Section], images: list[ImageRef], config: dict[str, Any]) -> list[dict[str, Any]]:
    image_by_id = {image.image_id: image for image in images}
    rules: list[dict[str, Any]] = []
    for section in sections:
        domains = infer_domains(section)
        high_value = section.section_type in {
            "optimization",
            "validation",
            "portfolio",
            "money_management",
            "execution_realism",
            "procedure",
            "warning",
            "code_explanation",
        } or any(d != "other" for d in domains)
        if not high_value:
            continue
        template = rule_template(section, domains)
        relevant_images = [
            image_id
            for image_id in section.nearby_image_ids
            if image_by_id.get(image_id) and image_by_id[image_id].doctrine_relevance in {"medium", "high", "critical"}
        ][: int(config.get("max_rule_images", 5))]
        confidence = "requires_human_review" if section.requires_human_review else ("high" if section.section_type in {"optimization", "money_management", "portfolio"} else "medium")
        rule_id = f"{lesson_id}_rule_{len(rules) + 1:04d}"
        rules.append(
            {
                "rule_id": rule_id,
                "promotion_state": "mechanical_rule_candidate",
                "confidence": confidence,
                "rule_type": rule_type_for(domains, section),
                "domains": domains,
                "statement": template["statement"],
                "trigger": template["trigger"],
                "action": template["action"],
                "failure_mode_if_ignored": template["failure"],
                "required_evidence": template["evidence"],
                "source_anchors": [
                    {
                        "lesson_id": lesson_id,
                        "md_path": source_md,
                        "section_id": section.section_id,
                        "line_start": section.line_start,
                        "line_end": section.line_end,
                        "image_ids": relevant_images,
                    }
                ],
                "caveats": [
                    "Candidate only; not promoted TSIS doctrine.",
                    "Automated extraction from revised MD and contextual image metadata; human doctrine review required before promotion.",
                ],
                "related_rules": [],
            }
        )
    return rules


def target_for_rule(rule: dict[str, Any]) -> tuple[str, str, str, str, str]:
    domains = set(rule["domains"])
    confidence = rule.get("confidence")
    if domains & {"data_semantics", "price_view", "bar_construction"}:
        return ("data_quality_gate", "TSIS_DATA_SEMANTICS_AND_PRICE_VIEW_GATE_CANDIDATE", "require", "high", "hard_gate")
    if domains & {"execution_realism", "halts", "commissions_slippage"}:
        return ("execution_realism_check", "TSIS_EXECUTION_REALISM_CHECK_CANDIDATE", "block", "critical", "hard_gate")
    if domains & {"money_management", "position_sizing"}:
        return ("money_management_policy", "TSIS_MONEY_MANAGEMENT_POLICY_CANDIDATE", "require", "high", "human_review_gate")
    if domains & {"portfolio", "correlation"}:
        return ("portfolio_evaluator", "TSIS_PORTFOLIO_EVALUATOR_CANDIDATE", "score", "high", "soft_gate")
    if domains & {"overfitting", "optimization", "robustness", "IS_OOS", "walk_forward", "BRaC"}:
        return ("strategy_evaluator", "TSIS_STRATEGY_ROBUSTNESS_EVALUATOR_CANDIDATE", "require", "critical" if "overfitting" in domains else "high", "hard_gate")
    if domains & {"setup_logic", "entry_logic", "exit_logic", "stop_loss", "take_profit", "filters"}:
        return ("backtest_checklist", "TSIS_BACKTEST_MECHANICS_CHECKLIST_CANDIDATE", "require", "medium", "soft_gate")
    if confidence == "requires_human_review":
        return ("human_review_checklist", "TSIS_SERSAN_HUMAN_REVIEW_CHECKLIST_CANDIDATE", "review", "medium", "human_review_gate")
    return ("research_protocol", "TSIS_RESEARCH_PROTOCOL_NOTE_CANDIDATE", "document", "low", "none")


def consumer_scope_for(target: str, domains: set[str]) -> str:
    if target == "data_quality_gate":
        return "backtest|ML|AlphaEvolve"
    if target == "execution_realism_check":
        return "backtest|live|AlphaEvolve"
    if target == "money_management_policy":
        return "backtest|AlphaEvolve|RL"
    if target == "portfolio_evaluator":
        return "backtest|AlphaEvolve|portfolio"
    if domains & {"optimization", "overfitting", "robustness"}:
        return "backtest|AlphaEvolve"
    return "backtest|research"


def build_translations(lesson_id: str, rules: list[dict[str, Any]]) -> list[dict[str, str]]:
    translations: list[dict[str, str]] = []
    for idx, rule in enumerate(rules, start=1):
        target, artifact, action, priority, blocking = target_for_rule(rule)
        domains = set(rule["domains"])
        if "AlphaEvolve" in consumer_scope_for(target, domains) and domains & {"overfitting", "optimization", "execution_realism", "money_management", "position_sizing", "data_semantics", "price_view"}:
            if blocking == "none":
                blocking = "soft_gate"
        translations.append(
            {
                "contract_version": "sersan_tsis_translation_map_v0_1",
                "lesson_id": lesson_id,
                "translation_id": f"{lesson_id}_tr_{idx:04d}",
                "rule_id": rule["rule_id"],
                "target": target,
                "tsis_artifact_candidate": artifact,
                "action_type": action,
                "priority": priority,
                "blocking_power": blocking,
                "consumer_scope": consumer_scope_for(target, domains),
                "implementation_hint": rule["action"],
                "requires_human_review": "true" if rule.get("confidence") == "requires_human_review" or priority in {"critical", "high"} else "false",
                "source_anchor_refs": rule["rule_id"],
                "notes": "Candidate translation; requires doctrine review before canonical promotion.",
            }
        )
    return translations


def section_to_record(lesson_id: str, section: Section) -> dict[str, Any]:
    return {
        "contract_version": "sersan_lesson_sections_v0_1",
        "lesson_id": lesson_id,
        "section_id": section.section_id,
        "heading_path": section.heading_path,
        "section_type": section.section_type,
        "line_start": section.line_start,
        "line_end": section.line_end,
        "raw_text_hash": sha256_text(section.text),
        "summary": section.summary,
        "keywords": section.keywords,
        "nearby_image_ids": section.nearby_image_ids,
        "contains_code": section.contains_code,
        "contains_table": section.contains_table,
        "contains_question": section.contains_question,
        "requires_image_reading": section.requires_image_reading,
        "requires_human_review": section.requires_human_review,
        "notes": section.notes,
    }


def write_sections(path: Path, lesson_id: str, sections: list[Section]) -> None:
    lines = [json.dumps(section_to_record(lesson_id, section), ensure_ascii=False) for section in sections]
    write_text(path, "\n".join(lines) + "\n")


def bool_str(value: bool) -> str:
    return "true" if value else "false"


def write_image_notes(lesson_dir: Path, lesson_id: str, images: list[ImageRef]) -> None:
    notes_dir = lesson_dir / "image_evidence_notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    for image in images:
        resolved = rel_project(image.resolved_path) if image.resolved_path else ""
        metadata_lines = [f"- {key}: `{value}`" for key, value in image.metadata.items()]
        text = [
            f"# {image.image_id}",
            "",
            "## Source",
            "",
            f"- lesson_id: `{lesson_id}`",
            f"- source_ref: `{image.source_ref}`",
            f"- resolved_path: `{resolved}`",
            f"- referenced_from_sections: `{ '|'.join(image.section_ids) }`",
            "",
            "## Visual Type",
            "",
            f"`{image.visual_type}`",
            "",
            "## Extracted Values",
            "",
            "Automated numeric OCR was not performed. If this image contains parameter values, equity metrics, drawdown, costs or optimization maps, it is marked for human review.",
            "",
            "## Technical Reading",
            "",
            f"- doctrine_relevance: `{image.doctrine_relevance}`",
            f"- contains_numbers: `{bool_str(image.contains_numbers)}`",
            f"- contains_code: `{bool_str(image.contains_code)}`",
            f"- contains_chart: `{bool_str(image.contains_chart)}`",
            f"- contains_platform_config: `{bool_str(image.contains_platform_config)}`",
            f"- contextual_note: {image.notes}",
            "",
            "## Doctrine Relevance",
            "",
            "This image is treated as evidence for the section-level mechanical-rule candidate only through its source anchor. It does not promote doctrine by itself.",
            "",
            "## Image Metadata",
            "",
            *(metadata_lines or ["- metadata: unavailable"]),
            "",
            "## Open Questions",
            "",
            "- Human reviewer should inspect this image if it carries optimization, risk, execution, code or portfolio evidence.",
            "",
        ]
        write_text(notes_dir / f"{image.image_id}.md", "\n".join(text))


def write_image_index(path: Path, images: list[ImageRef]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=IMAGE_CSV_HEADER)
        writer.writeheader()
        for image in images:
            writer.writerow(
                {
                    "contract_version": "sersan_image_evidence_index_v0_1",
                    "lesson_id": image.image_id.rsplit("_img_", 1)[0],
                    "image_id": image.image_id,
                    "source_ref": image.source_ref,
                    "resolved_path": rel_project(image.resolved_path) if image.resolved_path else "",
                    "resolution_status": image.resolution_status,
                    "referenced_from_section_ids": "|".join(image.section_ids),
                    "visual_type": image.visual_type,
                    "contains_numbers": bool_str(image.contains_numbers),
                    "contains_code": bool_str(image.contains_code),
                    "contains_chart": bool_str(image.contains_chart),
                    "contains_platform_config": bool_str(image.contains_platform_config),
                    "extracted_values_ref": image.note_ref if image.contains_numbers else "",
                    "technical_reading_ref": image.note_ref,
                    "doctrine_relevance": image.doctrine_relevance,
                    "requires_human_review": bool_str(image.requires_human_review),
                    "notes": image.notes,
                }
            )


def write_rules(path: Path, lesson_id: str, rules: list[dict[str, Any]]) -> None:
    payload = {
        "contract_version": "sersan_mechanical_rules_v0_1",
        "lesson_id": lesson_id,
        "generated_at_utc": utc_now(),
        "generated_by": "sersan_full_corpus_distillation_generator_v0_1",
        "rules": rules,
    }
    write_text(path, yaml.safe_dump(payload, sort_keys=False, allow_unicode=False, width=120))


def write_translations(path: Path, translations: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=TRANSLATION_CSV_HEADER)
        writer.writeheader()
        writer.writerows(translations)


def write_open_questions(path: Path, lesson_id: str, issues: list[str], images: list[ImageRef], rules: list[dict[str, Any]]) -> int:
    questions: list[str] = []
    if issues:
        questions.extend(issues)
    if any(image.requires_human_review for image in images):
        questions.append("Review high/critical or numeric images because automated OCR was not performed.")
    if not rules:
        questions.append("No mechanical rules were extracted; confirm whether the lesson is only reference/context or requires manual mapping.")
    text = [f"# Open Questions: {lesson_id}", ""]
    if questions:
        text.extend(f"- {q}" for q in questions)
    else:
        text.append("- None.")
    write_text(path, "\n".join(text) + "\n")
    return len(questions)


def write_lesson_distillation(
    path: Path,
    lesson_id: str,
    title: str,
    source_md: str,
    sections: list[Section],
    images: list[ImageRef],
    rules: list[dict[str, Any]],
    translations: list[dict[str, str]],
    config: dict[str, Any],
) -> None:
    top_images = sorted(
        images,
        key=lambda image: {"critical": 0, "high": 1, "medium": 2, "low": 3, "none": 4}.get(image.doctrine_relevance, 5),
    )[: int(config.get("max_distillation_embedded_images", 12))]
    lines = [
        f"# Lesson Distillation: {lesson_id}",
        "",
        f"Title: `{title}`",
        f"Source MD: `{source_md}`",
        "Promotion state: `mechanical_rule_candidate` only; no TSIS doctrine promoted.",
        "",
        "## What The Lesson Covers",
        "",
    ]
    for section in sections[:12]:
        lines.append(f"- `{section.section_id}` {section.summary}")
    lines.extend(["", "## Mechanical Rule Candidates", ""])
    for rule in rules:
        domains = ", ".join(rule["domains"])
        lines.append(f"- `{rule['rule_id']}` [{domains}] {rule['statement']}")
    if not rules:
        lines.append("- None extracted.")
    lines.extend(["", "## TSIS Translation Candidates", ""])
    for translation in translations:
        lines.append(
            f"- `{translation['translation_id']}` -> `{translation['target']}` / `{translation['tsis_artifact_candidate']}`"
        )
    if not translations:
        lines.append("- None created.")
    lines.extend(["", "## Key Visual Evidence", ""])
    for image in top_images:
        resolved = rel_project(image.resolved_path) if image.resolved_path else ""
        lines.extend(
            [
                f"### `{image.image_id}`",
                "",
                f"- relevance: `{image.doctrine_relevance}`",
                f"- visual_type: `{image.visual_type}`",
                f"- source_ref: `{image.source_ref}`",
                f"- resolved_path: `{resolved}`",
                f"- note: `{image.note_ref}`",
                "",
            ]
        )
        if image.resolved_path:
            rel_from_lesson = Path(rel_project(image.resolved_path)).as_posix()
            lines.append(f"![{image.image_id}](../../../../{rel_from_lesson})")
            lines.append("")
    if not top_images:
        lines.append("- No images indexed for this lesson.")
    lines.extend(
        [
            "## Warnings",
            "",
            "- This is automated corpus distillation, not final doctrine review.",
            "- Image files were opened, hashed and classified through local metadata plus nearby MD context; OCR/value extraction is not yet implemented.",
            "- Code/XLSX artifacts are inventoried through the corpus manifest but not semantically parsed in this run.",
            "",
        ]
    )
    write_text(path, "\n".join(lines))


def manifest_status(blocked: bool, rules: list[dict[str, Any]], translations: list[dict[str, str]]) -> str:
    if blocked:
        return "blocked"
    if translations:
        return "translated"
    if rules:
        return "rules_extracted"
    return "sectionized"


def write_quality_report(
    path: Path,
    lesson_id: str,
    manifest: dict[str, Any],
    sections: list[Section],
    images: list[ImageRef],
    rules: list[dict[str, Any]],
    translations: list[dict[str, str]],
    open_question_count: int,
    blocking_issues: list[str],
    warnings: list[str],
    acceptance_decision: str,
) -> None:
    images_resolved = sum(1 for image in images if image.resolution_status in {"resolved_direct", "resolved_lesson_fallback"})
    images_missing = sum(1 for image in images if image.resolution_status == "missing")
    images_read = sum(1 for image in images if image.note_ref)
    summary_rows = [
        ("lesson_id", lesson_id),
        ("status", manifest["status"]),
        ("md_lines", manifest["counts"]["md_lines"]),
        ("sections", len(sections)),
        ("image_refs_total", manifest["asset_resolution"]["image_refs_total"]),
        ("images_resolved", images_resolved),
        ("images_missing", images_missing),
        ("images_read", images_read),
        ("rules_extracted", len(rules)),
        ("translations_created", len(translations)),
        ("open_questions", open_question_count),
        ("blocking_issues", len(blocking_issues)),
    ]
    lines = [
        f"# Quality Report: {lesson_id}",
        "",
        "## 1. Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    lines.extend(f"| {key} | {value} |" for key, value in summary_rows)
    lines.extend(
        [
            "",
            "## 2. Input Coverage",
            "",
            f"- Source MD: `{manifest['source_md']}`",
            f"- Workshop dir: `{manifest.get('workshop_dir')}`",
            f"- Code artifacts inventoried: `{manifest['counts']['code_artifacts']}`",
            f"- XLSX artifacts inventoried: `{manifest['counts']['xlsx_artifacts']}`",
            "",
            "## 3. Asset Resolution",
            "",
            f"- resolved_direct: `{manifest['asset_resolution']['resolved_direct']}`",
            f"- resolved_lesson_fallback: `{manifest['asset_resolution']['resolved_lesson_fallback']}`",
            f"- external_reference: `{manifest['asset_resolution']['external_reference']}`",
            f"- missing: `{manifest['asset_resolution']['missing']}`",
            f"- needs_human_review: `{manifest['asset_resolution']['needs_human_review']}`",
            "",
            "## 4. Sectionization Quality",
            "",
            f"- Sections generated: `{len(sections)}`",
            "- Sections preserve 1-based source line ranges and raw text hashes.",
            "",
            "## 5. Image Reading Quality",
            "",
            f"- Image notes generated: `{images_read}`",
            "- Images were read as local files for hash/dimensions and interpreted through nearby MD context.",
            "- Numeric OCR was not performed; numeric/high-impact images are marked for human review.",
            "",
            "## 6. Mechanical Rule Quality",
            "",
            f"- Mechanical rules extracted: `{len(rules)}`",
            "- Rules are candidates only and include source anchors.",
            "",
            "## 7. TSIS Translation Quality",
            "",
            f"- Translation rows created: `{len(translations)}`",
            "- Translation targets use the canonical target enum from the lesson-pack contract.",
            "",
            "## 8. Open Questions",
            "",
        ]
    )
    if open_question_count:
        lines.append(f"- See `open_questions.md` for `{open_question_count}` open questions.")
    else:
        lines.append("- None.")
    lines.extend(["", "## 9. Blocking Issues", ""])
    lines.extend(f"- {issue}" for issue in blocking_issues) if blocking_issues else lines.append("- None.")
    lines.extend(["", "## 10. Acceptance Decision", ""])
    lines.append(f"Acceptance decision: `{acceptance_decision}`")
    lines.extend(["", "Warnings:", ""])
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- None.")
    write_text(path, "\n".join(lines) + "\n")


def build_toolchain_artifacts() -> list[dict[str, Any]]:
    artifacts = []
    for tool_id, role, path in [
        ("sersan_full_corpus_distillation_generator_v0_1", "generator", SCRIPT_PATH),
        ("sersan_full_corpus_distillation_validator_v0_1", "validator", TOOLCHAIN_DIR / "validate_sersan_distillation.py"),
        ("sersan_corpus_distillation_config_v0_1", "config", TOOLCHAIN_DIR / "sersan_corpus_distillation_config.json"),
    ]:
        artifacts.append(
            {
                "tool_id": tool_id,
                "role": role,
                "project_relative_path": rel_project(path),
                "sha256": sha256_file(path),
                "runtime": "python",
                "project_resident": True,
            }
        )
    return artifacts


def contract_inputs() -> list[dict[str, str]]:
    paths = harness_paths()
    files = [
        paths["harness"] / "sersan_distillation_protocol.md",
        paths["harness"] / "sersan_lesson_pack_contract.md",
        paths["harness"] / "sersan_pilot_harness_runbook.md",
        paths["shared_kernel"] / "harness_toolchain_traceability_contract.md",
        paths["shared_kernel"] / "shared_run_manifest_contract.md",
        paths["shared_kernel"] / "shared_validation_principles.md",
        paths["inventory_csv"],
    ]
    return [{"path": rel_project(path), "sha256": sha256_file(path)} for path in files if path.exists()]


def output_artifacts_for(lesson_dir: Path) -> list[dict[str, str]]:
    artifacts = []
    for path in sorted(lesson_dir.rglob("*")):
        if path.is_file() and path.name != "run_manifest.json":
            artifacts.append({"path": rel_project(path), "sha256": sha256_file(path)})
    return artifacts


def write_run_manifest(
    lesson_dir: Path,
    run_id: str,
    lesson_id: str,
    status: str,
    started_at_utc: str,
    completed_at_utc: str,
    execution_command: str,
    input_artifacts: list[dict[str, str]],
    known_limitations: list[str],
) -> None:
    manifest = {
        "run_id": run_id,
        "lesson_id_or_scope": lesson_id,
        "lesson_id": lesson_id,
        "mode": "replay",
        "status": status,
        "contract_version": "sersan_lesson_pack_contract_v0_1",
        "toolchain_traceability_contract": "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md",
        "started_at_utc": started_at_utc,
        "completed_at_utc": completed_at_utc,
        "execution_command": execution_command,
        "toolchain_artifacts": build_toolchain_artifacts(),
        "input_artifacts": input_artifacts,
        "output_artifacts": output_artifacts_for(lesson_dir),
        "non_project_artifacts_used": [],
        "known_limitations": known_limitations,
        "acceptance_decision": status,
    }
    write_json(lesson_dir / "run_manifest.json", manifest)


def process_lesson(row: dict[str, str], config: dict[str, Any], execution_command: str) -> dict[str, Any]:
    paths = harness_paths()
    corpus_root = paths["corpus_root"]
    artifact_root = paths["artifact_root"]
    lesson_id = row["lesson_id"]
    lesson_dir = artifact_root / lesson_id
    lesson_dir.mkdir(parents=True, exist_ok=True)
    started_at = utc_now()
    source_md_abs = corpus_root / row["source_md"]
    md_text = read_text(source_md_abs)
    lines = md_text.splitlines()
    blocked = row.get("status") == "inventory_only" and bool(config.get("process_inventory_only_lessons_as_blocked", True))
    blocking_issues: list[str] = []
    warnings: list[str] = [
        "Automated numeric OCR is not implemented in this run.",
        "Code artifacts are inventoried but not semantically parsed.",
        "XLSX artifacts are inventoried but not semantically parsed.",
    ]
    if blocked:
        blocking_issues.append("inventory_only lesson has no mapped workshop/practice number; kept blocked for human mapping.")
    workshop_dir = row.get("workshop_dir") or None
    image_dir = row.get("image_dir") or None
    image_dir_abs = (corpus_root / image_dir) if image_dir else None

    sections = build_sections(lesson_id, md_text)
    raw_image_refs = extract_image_refs(lines)
    images = build_images(lesson_id, raw_image_refs, sections, source_md_abs, image_dir_abs, corpus_root)
    rules = [] if blocked else extract_rules(lesson_id, row["source_md"], sections, images, config)
    translations = [] if blocked else build_translations(lesson_id, rules)

    if any(image.requires_human_review for image in images):
        warnings.append("High-impact or numeric images require human review.")
    if any(image.resolution_status == "missing" for image in images):
        blocking_issues.append("At least one referenced local image is missing.")
    if not rules and not blocked:
        warnings.append("No mechanical rules extracted.")

    manifest = {
        "contract_version": "sersan_lesson_pack_contract_v0_1",
        "generated_at_utc": utc_now(),
        "generated_by": config["generator_id"],
        "lesson_id": lesson_id,
        "practice_number": int(row["practice_number"]) if row.get("practice_number") else None,
        "title": extract_title(md_text, row.get("title") or lesson_id),
        "status": manifest_status(blocked, rules, translations),
        "source_md": row["source_md"],
        "workshop_dir": workshop_dir,
        "image_dir": image_dir,
        "pdf_role": "duplicate_md" if int(row.get("pdf_count") or 0) else "not_present",
        "video_role": "out_of_scope",
        "asset_resolution": {
            "resolver_version": "sersan_full_corpus_resolver_v0_1",
            "image_refs_total": len(images),
            "resolved_direct": sum(1 for image in images if image.resolution_status == "resolved_direct"),
            "resolved_lesson_fallback": sum(1 for image in images if image.resolution_status == "resolved_lesson_fallback"),
            "external_reference": sum(1 for image in images if image.resolution_status == "external_reference"),
            "missing": sum(1 for image in images if image.resolution_status == "missing"),
            "needs_human_review": sum(1 for image in images if image.requires_human_review),
        },
        "source_hashes": {row["source_md"]: sha256_file(source_md_abs)},
        "counts": {
            "md_lines": len(lines),
            "sections": len(sections),
            "images": len(images),
            "code_artifacts": int(row.get("code_artifacts") or 0),
            "xlsx_artifacts": int(row.get("xlsx_artifacts") or 0),
            "rules": len(rules),
            "translations": len(translations),
            "open_questions": 0,
        },
        "known_issues": [issue for issue in [row.get("known_issues", "")] if issue] + blocking_issues + warnings,
    }

    write_json(lesson_dir / "lesson_pack_manifest.json", manifest)
    write_sections(lesson_dir / "lesson_sections.jsonl", lesson_id, sections)
    write_image_notes(lesson_dir, lesson_id, images)
    write_image_index(lesson_dir / "image_evidence_index.csv", images)
    write_rules(lesson_dir / "mechanical_rules.yaml", lesson_id, rules)
    write_translations(lesson_dir / "tsis_translation_map.csv", translations)
    open_question_count = write_open_questions(lesson_dir / "open_questions.md", lesson_id, blocking_issues, images, rules)
    manifest["counts"]["open_questions"] = open_question_count
    write_json(lesson_dir / "lesson_pack_manifest.json", manifest)
    write_lesson_distillation(
        lesson_dir / "lesson_distillation.md",
        lesson_id,
        manifest["title"],
        row["source_md"],
        sections,
        images,
        rules,
        translations,
        config,
    )

    if blocking_issues and blocked:
        acceptance_decision = "needs_human_review"
        run_status = "blocked"
    elif blocking_issues:
        acceptance_decision = "fail"
        run_status = "fail"
    elif warnings:
        acceptance_decision = "pass_with_warnings"
        run_status = "pass_with_warnings"
    else:
        acceptance_decision = "pass"
        run_status = "pass"

    write_quality_report(
        lesson_dir / "quality_report.md",
        lesson_id,
        manifest,
        sections,
        images,
        rules,
        translations,
        open_question_count,
        blocking_issues,
        warnings,
        acceptance_decision,
    )

    input_artifacts = contract_inputs() + [{"path": rel_project(source_md_abs), "sha256": sha256_file(source_md_abs)}]
    completed_at = utc_now()
    run_id = f"{config['run_id_prefix']}_{lesson_id}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    write_run_manifest(
        lesson_dir,
        run_id,
        lesson_id,
        run_status,
        started_at,
        completed_at,
        execution_command,
        input_artifacts,
        warnings + blocking_issues,
    )

    return {
        "lesson_id": lesson_id,
        "status": run_status,
        "acceptance_decision": acceptance_decision,
        "sections": len(sections),
        "images": len(images),
        "images_needing_human_review": manifest["asset_resolution"]["needs_human_review"],
        "rules": len(rules),
        "translations": len(translations),
        "warnings": warnings,
        "blocking_issues": blocking_issues,
    }


def write_corpus_reports(results: list[dict[str, Any]], readiness: dict[str, Any], execution_command: str, config: dict[str, Any]) -> None:
    paths = harness_paths()
    artifact_root = paths["artifact_root"]
    status_counts: dict[str, int] = {}
    for result in results:
        status_counts[result["status"]] = status_counts.get(result["status"], 0) + 1
    summary = {
        "generated_at_utc": utc_now(),
        "run_id": f"{config['run_id_prefix']}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "readiness_status": readiness["status"],
        "lesson_packs_processed": len(results),
        "status_counts": status_counts,
        "rules_extracted": sum(result["rules"] for result in results),
        "translations_created": sum(result["translations"] for result in results),
        "images_indexed": sum(result["images"] for result in results),
        "images_needing_human_review": sum(result["images_needing_human_review"] for result in results),
        "lessons": results,
        "repeated_warnings": [
            "Automated numeric OCR not implemented.",
            "Code artifacts inventoried but not semantically parsed.",
            "XLSX artifacts inventoried but not semantically parsed.",
            "High-impact image evidence requires human review before doctrine promotion.",
        ],
        "contract_debt": [
            "Human visual review/OCR remains required for images carrying parameter, risk, optimization or execution evidence.",
            "Code and XLSX semantic parsing remain pending.",
            "Sersan outputs are mechanical-rule candidates only; no doctrine is promoted by this run.",
            "The inventory_only lesson sersan_unmapped_xxx_revised remains blocked until mapped or explicitly reclassified.",
        ],
        "promotion_recommendation": "Do not promote to canonical TSIS doctrine yet. Proceed to human doctrine review and domain consolidation after validating high-impact image evidence.",
    }
    write_json(artifact_root / "_corpus_distillation_summary.json", summary)

    lines = [
        "# Sersan Corpus-Level Distillation Report",
        "",
        f"Generated at UTC: `{summary['generated_at_utc']}`",
        f"Readiness status: `{summary['readiness_status']}`",
        f"Execution command: `{execution_command}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| lesson packs processed | {summary['lesson_packs_processed']} |",
        f"| pass | {status_counts.get('pass', 0)} |",
        f"| pass_with_warnings | {status_counts.get('pass_with_warnings', 0)} |",
        f"| blocked | {status_counts.get('blocked', 0)} |",
        f"| fail | {status_counts.get('fail', 0)} |",
        f"| needs_human_review | {status_counts.get('needs_human_review', 0)} |",
        f"| mechanical rules extracted | {summary['rules_extracted']} |",
        f"| TSIS maps created | {summary['translations_created']} |",
        f"| images indexed | {summary['images_indexed']} |",
        f"| images requiring human review | {summary['images_needing_human_review']} |",
        "",
        "## Lesson Pack Results",
        "",
        "| lesson_id | status | sections | images | rules | translations | blockers |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        lines.append(
            f"| `{result['lesson_id']}` | `{result['status']}` | {result['sections']} | {result['images']} | {result['rules']} | {result['translations']} | {len(result['blocking_issues'])} |"
        )
    lines.extend(["", "## Repeated Warnings", ""])
    lines.extend(f"- {warning}" for warning in summary["repeated_warnings"])
    lines.extend(["", "## Contract Debt", ""])
    lines.extend(f"- {debt}" for debt in summary["contract_debt"])
    lines.extend(["", "## Promotion Recommendation", "", summary["promotion_recommendation"], ""])
    write_text(artifact_root / "_corpus_distillation_report.md", "\n".join(lines))

    corpus_manifest = {
        "run_id": summary["run_id"],
        "lesson_id_or_scope": "sersan_full_corpus",
        "mode": "replay",
        "status": "pass_with_warnings" if status_counts.get("fail", 0) == 0 else "fail",
        "contract_version": "sersan_lesson_pack_contract_v0_1",
        "toolchain_traceability_contract": "00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md",
        "started_at_utc": readiness["generated_at_utc"],
        "completed_at_utc": utc_now(),
        "execution_command": execution_command,
        "toolchain_artifacts": build_toolchain_artifacts(),
        "input_artifacts": contract_inputs(),
        "output_artifacts": [
            {"path": rel_project(artifact_root / "_readiness_gate_report.json"), "sha256": sha256_file(artifact_root / "_readiness_gate_report.json")},
            {"path": rel_project(artifact_root / "_readiness_gate_report.md"), "sha256": sha256_file(artifact_root / "_readiness_gate_report.md")},
            {"path": rel_project(artifact_root / "_corpus_distillation_summary.json"), "sha256": sha256_file(artifact_root / "_corpus_distillation_summary.json")},
            {"path": rel_project(artifact_root / "_corpus_distillation_report.md"), "sha256": sha256_file(artifact_root / "_corpus_distillation_report.md")},
        ],
        "non_project_artifacts_used": [],
        "known_limitations": summary["contract_debt"],
        "acceptance_decision": "pass_with_warnings" if status_counts.get("fail", 0) == 0 else "fail",
    }
    write_json(artifact_root / "_corpus_run_manifest.json", corpus_manifest)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full Sersan corpus distillation harness.")
    parser.add_argument("--process-all", action="store_true", help="Process all lesson packs after readiness gate.")
    parser.add_argument("--readiness-only", action="store_true", help="Only run readiness gate.")
    args = parser.parse_args()

    config = load_config()
    ok, gate_report = readiness_gate(config)
    write_readiness_report(gate_report)
    print(json.dumps({"readiness": gate_report["status"], "decision": gate_report["decision"]}, indent=2))
    if not ok:
        return 2
    if args.readiness_only:
        return 0
    if not args.process_all:
        print("Use --process-all to process lesson packs after readiness gate.")
        return 0

    execution_command = "python " + rel_project(SCRIPT_PATH) + " --process-all"
    rows = load_inventory()
    results = [process_lesson(row, config, execution_command) for row in rows]
    write_corpus_reports(results, gate_report, execution_command, config)
    print(
        json.dumps(
            {
                "processed": len(results),
                "rules": sum(result["rules"] for result in results),
                "translations": sum(result["translations"] for result in results),
                "status_counts": {status: sum(1 for result in results if result["status"] == status) for status in sorted({r["status"] for r in results})},
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
