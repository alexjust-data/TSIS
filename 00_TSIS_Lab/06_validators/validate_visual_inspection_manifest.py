"""Validate TSIS visual inspection evidence manifests.

This validator is intentionally strict. A chart image is not enough evidence:
TSIS requires a label-level manifest that proves which measured signal is drawn,
where the label points, and whether labels overlap.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

import pandas as pd
from PIL import Image, ImageStat


DEFAULT_REQUIRED_SIGNALS = (
    "scanner_seed",
    "first_push_high",
    "first_dip_low",
    "rebreak_confirmed",
    "first_dip_to_next_structural_high",
)

REQUIRED_COLUMNS = (
    "visual_case_id",
    "candidate_id",
    "ticker",
    "session_date",
    "image_path",
    "image_kind",
    "label_id",
    "signal_name",
    "source_field",
    "label_text",
    "anchor_x_px",
    "anchor_y_px",
    "bbox_x0_px",
    "bbox_y0_px",
    "bbox_x1_px",
    "bbox_y1_px",
    "renderer_source_path",
    "renderer_source_hash",
    "visual_evidence_status",
    "prior_close_value",
    "prior_close_source",
    "prior_close_pct_formula",
    "visual_gate_source",
    "placement_rule",
    "label_order_index",
    "prior_close_y_px",
)

NUMERIC_COLUMNS = (
    "anchor_x_px",
    "anchor_y_px",
    "bbox_x0_px",
    "bbox_y0_px",
    "bbox_x1_px",
    "bbox_y1_px",
    "prior_close_y_px",
)


class CheckResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    @property
    def passed(self) -> bool:
        return not self.errors

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def note(self, message: str) -> None:
        self.info.append(message)


def _resolve_path(value: object, base_dir: Path) -> Path:
    p = Path(str(value))
    if not p.is_absolute():
        p = base_dir / p
    return p


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_manifest(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".json", ".jsonl"}:
        if suffix == ".jsonl":
            return pd.read_json(path, lines=True)
        data = json.loads(path.read_text(encoding="utf-8"))
        return pd.DataFrame(data if isinstance(data, list) else data.get("rows", []))
    raise ValueError(f"Unsupported manifest format: {path}")


def _find_manifest(run_dir: Path, manifest_name: str) -> Path | None:
    candidates = [
        run_dir / manifest_name,
        run_dir / "chart_exports" / manifest_name,
        run_dir / "visual_inspection" / manifest_name,
    ]
    for path in candidates:
        if path.exists():
            return path
    matches = sorted(run_dir.rglob(manifest_name))
    return matches[0] if matches else None


def _bbox_overlap(left: pd.Series, right: pd.Series) -> bool:
    return not (
        float(left["bbox_x1_px"]) <= float(right["bbox_x0_px"])
        or float(right["bbox_x1_px"]) <= float(left["bbox_x0_px"])
        or float(left["bbox_y1_px"]) <= float(right["bbox_y0_px"])
        or float(right["bbox_y1_px"]) <= float(left["bbox_y0_px"])
    )


def _validate_images(df: pd.DataFrame, base_dir: Path, result: CheckResult) -> dict[str, tuple[int, int]]:
    image_sizes: dict[str, tuple[int, int]] = {}
    for image_value in sorted(df["image_path"].dropna().astype(str).unique()):
        image_path = _resolve_path(image_value, base_dir)
        if not image_path.exists():
            result.error(f"image_missing: {image_path}")
            continue
        try:
            with Image.open(image_path) as im:
                image_sizes[image_value] = im.size
                rgb = im.convert("RGB")
                stat = ImageStat.Stat(rgb)
                if max(stat.stddev) < 2.0:
                    result.error(f"image_probably_blank: {image_path}")
                result.note(
                    f"image_ok: {image_path} size={im.size[0]}x{im.size[1]} stddev="
                    f"{[round(x, 2) for x in stat.stddev]}"
                )
        except Exception as exc:  # pragma: no cover - diagnostic path
            result.error(f"image_unreadable: {image_path} error={type(exc).__name__}: {exc}")
    return image_sizes


def _validate_renderer_hashes(df: pd.DataFrame, base_dir: Path, result: CheckResult) -> None:
    pairs = df[["renderer_source_path", "renderer_source_hash"]].drop_duplicates()
    for row in pairs.itertuples(index=False):
        source_path = _resolve_path(row.renderer_source_path, base_dir)
        expected_hash = str(row.renderer_source_hash or "").strip().lower()
        if not source_path.exists():
            result.error(f"renderer_source_missing: {source_path}")
            continue
        actual_hash = _sha256(source_path)
        if not expected_hash:
            result.error(f"renderer_source_hash_missing: {source_path}")
        elif actual_hash.lower() != expected_hash:
            result.error(
                f"renderer_source_hash_mismatch: {source_path} expected={expected_hash} actual={actual_hash}"
            )


def _validate_schema(df: pd.DataFrame, required_signals: tuple[str, ...], result: CheckResult) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        result.error("missing_columns: " + ", ".join(missing))
        return
    if df.empty:
        result.error("manifest_empty")
        return
    duplicated = df["label_id"].dropna().astype(str).duplicated()
    if duplicated.any():
        ids = df.loc[duplicated, "label_id"].astype(str).head(20).tolist()
        result.error("duplicate_label_id: " + ", ".join(ids))
    for col in ("visual_case_id", "candidate_id", "image_path", "label_id", "signal_name", "source_field"):
        null_count = int(df[col].isna().sum())
        blank_count = int(df[col].astype(str).str.strip().eq("").sum())
        if null_count or blank_count:
            result.error(f"blank_required_values: column={col} null={null_count} blank={blank_count}")
    for col in NUMERIC_COLUMNS:
        coerced = pd.to_numeric(df[col], errors="coerce")
        if coerced.isna().any():
            result.error(f"non_numeric_label_geometry: column={col} rows={int(coerced.isna().sum())}")
    status_values = set(df["visual_evidence_status"].dropna().astype(str).str.lower().unique())
    bad_status = sorted(status_values - {"ok", "passed", "review", "warning"})
    if bad_status:
        result.error("invalid_visual_evidence_status: " + ", ".join(bad_status))
    observed = set(df["signal_name"].dropna().astype(str))
    missing_signals = [signal for signal in required_signals if signal not in observed]
    if missing_signals:
        result.error("missing_required_signals: " + ", ".join(missing_signals))



def _validate_label_text_contract(df: pd.DataFrame, result: CheckResult) -> None:
    for row in df.itertuples(index=False):
        label_id = str(getattr(row, "label_id"))
        signal_name = str(getattr(row, "signal_name"))
        label_text = str(getattr(row, "label_text"))
        source_field = str(getattr(row, "source_field"))
        lowered = label_text.lower()
        if "<br>" in lowered or "< br" in lowered or "br >" in lowered:
            result.error(f"legacy_html_break_in_label_text: label_id={label_id}")
        if "accu" in lowered or "< br" in lowered or "br >" in lowered:
            result.error(f"legacy_trigger_text_in_manifest: label_id={label_id}")
        if re.search(r"20\d{2}-\d{2}-\d{2}", label_text):
            result.error(f"visible_full_date_in_label_text: label_id={label_id}")
        if signal_name == "scanner_seed":
            if not label_text.startswith("momentum trigger"):
                result.error(f"momentum_trigger_label_title_missing: label_id={label_id}")
            required_terms = ["momentum trigger", "prior close ", "price $", "acc vol ", "threshold +", "mcap ", "$0.50-$20"]
            missing_terms = [term for term in required_terms if term not in lowered]
            if missing_terms:
                result.error(f"momentum_trigger_label_terms_missing: label_id={label_id} terms={','.join(missing_terms)}")
            required_sources = [
                "visual_momentum_gate_ts_utc",
                "visual_momentum_gate_price",
                "visual_momentum_gate_volume",
                "visual_momentum_gate_prior_close_value",
                "visual_momentum_gate_prior_close_source",
                "visual_momentum_gate_prior_close_pct",
                "market_cap",
                "momentum_trigger_pct_threshold",
            ]
            missing_sources = [item for item in required_sources if item not in source_field]
            if missing_sources:
                result.error(f"momentum_trigger_source_fields_missing: label_id={label_id} fields={','.join(missing_sources)}")
            prior_close_value = getattr(row, "prior_close_value", None)
            prior_close_source = str(getattr(row, "prior_close_source", "") or "").strip().lower()
            prior_close_formula = str(getattr(row, "prior_close_pct_formula", "") or "").strip()
            visual_gate_source = str(getattr(row, "visual_gate_source", "") or "").strip()
            if pd.isna(prior_close_value):
                result.error(f"momentum_trigger_prior_close_value_missing: label_id={label_id}")
            if not prior_close_source or prior_close_source == "unavailable":
                result.error(f"momentum_trigger_prior_close_source_missing: label_id={label_id}")
            if not prior_close_formula:
                result.error(f"momentum_trigger_prior_close_formula_missing: label_id={label_id}")
            if not visual_gate_source:
                result.error(f"momentum_trigger_visual_gate_source_missing: label_id={label_id}")



def _validate_label_placement_contract(df: pd.DataFrame, result: CheckResult) -> None:
    expected_order = ["scanner_seed", "first_push_high", "first_dip_low", "rebreak_confirmed", "first_dip_to_next_structural_high"]
    for (image_path, visual_case_id), group in df.groupby(["image_path", "visual_case_id"], dropna=False):
        group = group.copy()
        prior_rows = group[group["signal_name"].astype(str).isin(expected_order)].copy()
        if len(prior_rows) != len(expected_order):
            result.error(f"prior_close_row_signal_count_invalid: image={image_path} case={visual_case_id} count={len(prior_rows)}")
            continue
        for row in prior_rows.itertuples(index=False):
            label_id = str(getattr(row, "label_id"))
            placement_rule = str(getattr(row, "placement_rule"))
            if placement_rule != "above_prior_close_row":
                result.error(f"label_not_in_prior_close_row: label_id={label_id} placement_rule={placement_rule}")
            gap = float(getattr(row, "prior_close_y_px")) - float(getattr(row, "bbox_y1_px"))
            if gap < 1.0 or gap > 18.0:
                result.error(
                    f"label_not_seated_above_prior_close: label_id={label_id} gap_px={gap:.3f} bbox_y1={getattr(row, 'bbox_y1_px')} prior_close_y={getattr(row, 'prior_close_y_px')}"
                )
        ordered = prior_rows.sort_values("label_order_index")
        observed_order = ordered["signal_name"].astype(str).tolist()
        if observed_order != expected_order:
            result.error(f"prior_close_row_order_invalid: image={image_path} observed={observed_order}")
        x0s = pd.to_numeric(ordered["bbox_x0_px"], errors="coerce").tolist()
        if any(right <= left for left, right in zip(x0s, x0s[1:])):
            result.error(f"prior_close_row_x_order_invalid: image={image_path} x0s={x0s}")


def _validate_geometry(df: pd.DataFrame, image_sizes: dict[str, tuple[int, int]], result: CheckResult) -> None:
    for image_path, group in df.groupby("image_path", dropna=False):
        size = image_sizes.get(str(image_path))
        if not size:
            continue
        width, height = size
        for row in group.itertuples(index=False):
            label_id = str(getattr(row, "label_id"))
            x0 = float(getattr(row, "bbox_x0_px"))
            y0 = float(getattr(row, "bbox_y0_px"))
            x1 = float(getattr(row, "bbox_x1_px"))
            y1 = float(getattr(row, "bbox_y1_px"))
            ax = float(getattr(row, "anchor_x_px"))
            ay = float(getattr(row, "anchor_y_px"))
            if not (x1 > x0 and y1 > y0):
                result.error(f"invalid_bbox: label_id={label_id} bbox=({x0},{y0},{x1},{y1})")
            if x0 < 0 or y0 < 0 or x1 > width or y1 > height:
                result.error(
                    f"bbox_outside_image: label_id={label_id} bbox=({x0},{y0},{x1},{y1}) image={width}x{height}"
                )
            if ax < 0 or ay < 0 or ax > width or ay > height:
                result.error(f"anchor_outside_image: label_id={label_id} anchor=({ax},{ay}) image={width}x{height}")
        rows = list(group.reset_index(drop=True).iterrows())
        for i, (_, left) in enumerate(rows):
            for _, right in rows[i + 1 :]:
                if _bbox_overlap(left, right):
                    result.error(
                        "label_overlap: "
                        f"image={image_path} left={left['label_id']} right={right['label_id']}"
                    )


def validate(run_dir: Path, manifest_name: str, required_signals: tuple[str, ...]) -> tuple[CheckResult, Path | None, pd.DataFrame | None]:
    result = CheckResult()
    run_dir = run_dir.resolve()
    if not run_dir.exists():
        result.error(f"run_dir_missing: {run_dir}")
        return result, None, None
    manifest_path = _find_manifest(run_dir, manifest_name)
    if manifest_path is None:
        result.error(f"visual_inspection_manifest_missing: searched={manifest_name} under {run_dir}")
        result.warn("Existing DAS EXPORT_MANIFEST.csv is not sufficient because it is image-level, not label-level.")
        return result, None, None
    result.note(f"manifest={manifest_path}")
    try:
        df = _read_manifest(manifest_path)
    except Exception as exc:
        result.error(f"manifest_unreadable: {manifest_path} error={type(exc).__name__}: {exc}")
        return result, manifest_path, None
    _validate_schema(df, required_signals, result)
    if result.errors:
        return result, manifest_path, df
    _validate_label_text_contract(df, result)
    _validate_label_placement_contract(df, result)
    if result.errors:
        return result, manifest_path, df
    image_sizes = _validate_images(df, manifest_path.parent, result)
    _validate_renderer_hashes(df, manifest_path.parent, result)
    _validate_geometry(df, image_sizes, result)
    result.note(f"labels={len(df)} visual_cases={df['visual_case_id'].nunique()} images={df['image_path'].nunique()}")
    return result, manifest_path, df


def _write_report(result: CheckResult, output_path: Path, run_dir: Path, manifest_path: Path | None) -> None:
    lines = [
        "# Visual Inspection Manifest QC Report",
        "",
        f"run_dir: `{run_dir}`",
        f"manifest: `{manifest_path}`" if manifest_path else "manifest: `missing`",
        f"status: `{'PASS' if result.passed else 'FAIL'}`",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {item}" for item in result.errors] or ["- none"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in result.warnings] or ["- none"])
    lines.extend(["", "## Info", ""])
    lines.extend([f"- {item}" for item in result.info] or ["- none"])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_required_signals(values: Iterable[str]) -> tuple[str, ...]:
    out: list[str] = []
    for value in values:
        for part in str(value).split(","):
            clean = part.strip()
            if clean:
                out.append(clean)
    return tuple(out) if out else DEFAULT_REQUIRED_SIGNALS


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate TSIS visual inspection evidence manifest.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--manifest-name", default="visual_inspection_manifest.parquet")
    parser.add_argument("--required-signal", action="append", default=[])
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-path")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    required_signals = _parse_required_signals(args.required_signal) or DEFAULT_REQUIRED_SIGNALS
    result, manifest_path, _ = validate(run_dir, args.manifest_name, required_signals)

    print(f"status={'PASS' if result.passed else 'FAIL'}")
    for item in result.errors:
        print(f"ERROR {item}")
    for item in result.warnings:
        print(f"WARN {item}")
    for item in result.info:
        print(f"INFO {item}")

    if args.write_report:
        report_path = Path(args.report_path) if args.report_path else run_dir / "visual_qc_report.md"
        _write_report(result, report_path, run_dir, manifest_path)
        print(f"report={report_path}")

    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

