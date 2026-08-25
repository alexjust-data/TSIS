from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import duckdb
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


EXPERIMENT_RUNS_ROOT = Path(
    r"C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001"
    r"\runs"
)
ADJUSTED_DAILY_ROOT = Path(
    os.environ.get("ATLAS_ADJUSTED_DAILY_ROOT", r"G:\TSIS\data\ohlcv_daily_adjusted")
)

ACTIVATION_FAMILY_CATALOG = [
    {
        "family": "close_advance",
        "title": "Subida al cierre",
        "definition": (
            "Compara el cierre de D0 con el cierre de la sesión anterior. "
            "Una sesión que supera varios umbrales conserva todas esas etiquetas."
        ),
        "formula": "(cierre D0 / cierre D-1) - 1",
        "labels": [
            "close_advance_ge_20pct",
            "close_advance_ge_30pct",
            "close_advance_ge_50pct",
            "close_advance_ge_100pct",
        ],
        "caveat": "Describe una variación observada; no representa PnL ni una entrada.",
    },
    {
        "family": "gap",
        "title": "Gap de apertura",
        "definition": (
            "Compara la apertura de D0 con el cierre de la sesión anterior usando "
            "precios normalizados por splits."
        ),
        "formula": "(apertura D0 / cierre D-1) - 1",
        "labels": [
            "gap_ge_10pct",
            "gap_ge_20pct",
            "gap_ge_30pct",
            "gap_ge_50pct",
            "gap_ge_75pct",
            "gap_ge_100pct",
            "gap_ge_150pct",
            "gap_ge_200pct",
            "gap_ge_300pct",
        ],
        "caveat": "Los umbrales son acumulativos: un gap de 120% cumple 10%, 20%, 30%, 50%, 75% y 100%.",
    },
    {
        "family": "range",
        "title": "Rango diario",
        "definition": (
            "Mide la amplitud entre el máximo y el mínimo de D0 respecto al cierre "
            "de la sesión anterior."
        ),
        "formula": "(máximo D0 - mínimo D0) / cierre D-1",
        "labels": [
            "range_ge_20pct",
            "range_ge_30pct",
            "range_ge_50pct",
            "range_ge_100pct",
        ],
        "caveat": "No indica la dirección de la vela; solo su amplitud relativa.",
    },
    {
        "family": "relative_volume",
        "title": "Volumen relativo",
        "definition": (
            "Compara el volumen de D0 con la mediana de las 20 sesiones anteriores. "
            "Requiere esas 20 observaciones previas."
        ),
        "formula": "volumen D0 / mediana(volumen D-20 … D-1)",
        "labels": [
            "relative_volume_ge_3x",
            "relative_volume_ge_5x",
            "relative_volume_ge_10x",
            "relative_volume_ge_20x",
        ],
        "caveat": "Es actividad relativa en daily; no demuestra rotación real del float.",
    },
    {
        "family": "resistance_breakout",
        "title": "Ruptura de máximo previo",
        "definition": (
            "El máximo de D0 supera el mayor máximo de una ventana formada solo por "
            "sesiones anteriores."
        ),
        "formula": "máximo D0 > máximo(máximos previos de la ventana)",
        "labels": [
            "high_breakout_previous_day",
            "high_breakout_previous_week",
            "high_breakout_previous_month",
            "high_breakout_previous_quarter",
            "high_breakout_previous_half_year",
            "high_breakout_previous_year",
        ],
        "caveat": (
            "Las ventanas son 1, 5, 21, 63, 126 y 252 observaciones daily. "
            "Se exige ruptura por el máximo, no por el cierre."
        ),
    },
]

def _terminal_pass(final_root: Path) -> dict | None:
    certification_path = final_root / "terminal_certification.json"
    if not certification_path.is_file():
        return None
    try:
        certification = json.loads(certification_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    status = str(certification.get("status", "")).casefold()
    mode = str(certification.get("mode", "")).casefold()
    return certification if status == "pass" and mode in {"full", "probe"} else None


def _certified_at_key(certification: dict) -> datetime:
    try:
        certified_at = datetime.fromisoformat(str(certification.get("certified_at", "")))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if certified_at.tzinfo is None:
        certified_at = certified_at.replace(tzinfo=timezone.utc)
    return certified_at.astimezone(timezone.utc)


def _resolve_final_root(
    runs_root: Path = EXPERIMENT_RUNS_ROOT,
    explicit_root: Path | None = None,
) -> Path | None:
    configured = explicit_root
    if configured is None and os.environ.get("ATLAS_FINAL_ROOT"):
        configured = Path(os.environ["ATLAS_FINAL_ROOT"])
    if configured is not None:
        return configured if _terminal_pass(configured) is not None else None
    if not runs_root.is_dir():
        return None

    candidates: list[tuple[int, datetime, str, Path]] = []
    for run_root in runs_root.iterdir():
        if not run_root.is_dir():
            continue
        final_root = run_root / "final"
        certification = _terminal_pass(final_root)
        if certification is None:
            continue
        mode = str(certification["mode"]).casefold()
        candidates.append(
            (
                1 if mode == "full" else 0,
                _certified_at_key(certification),
                run_root.name,
                final_root,
            )
        )
    return max(candidates)[-1] if candidates else None


FINAL_ROOT = _resolve_final_root()
ANNOTATION_DB = Path(
    os.environ.get("ATLAS_ANNOTATION_DB", Path(__file__).with_name("annotations.sqlite"))
)


def _path(name: str) -> str:
    if FINAL_ROOT is None:
        raise HTTPException(status_code=503, detail="No terminal PASS Atlas run is available")
    path = FINAL_ROOT / f"{name}.parquet"
    if not path.exists():
        raise HTTPException(status_code=503, detail=f"Atlas output unavailable: {name}")
    return path.as_posix().replace("'", "''")


def _query(sql: str, parameters: list | None = None) -> list[dict]:
    con = duckdb.connect()
    try:
        frame = con.execute(sql, parameters or []).fetch_df()
    finally:
        con.close()
    frame = frame.where(frame.notna(), None)
    for column in frame.columns:
        if str(frame[column].dtype).startswith("datetime"):
            frame[column] = frame[column].astype(str)
    return frame.to_dict("records")


def _init_annotations() -> None:
    ANNOTATION_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ANNOTATION_DB) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS annotations (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              episode_id TEXT NOT NULL,
              note TEXT NOT NULL,
              tags TEXT NOT NULL,
              created_at TEXT NOT NULL
            )
            """
        )


class AnnotationIn(BaseModel):
    episode_id: str = Field(min_length=8, max_length=64)
    note: str = Field(min_length=1, max_length=4000)
    tags: list[str] = Field(default_factory=list, max_length=20)


app = FastAPI(title="TSIS Daily Pattern Atlas", version="0.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
_init_annotations()


@app.get("/api/meta")
def meta() -> dict:
    if FINAL_ROOT is None:
        return {
            "final_root": None,
            "status": "unavailable",
            "mode": "unknown",
            "counts": {},
            "certified_at": None,
        }
    manifest_path = FINAL_ROOT / "run_manifest.json"
    certification_path = FINAL_ROOT / "terminal_certification.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    certification = (
        json.loads(certification_path.read_text(encoding="utf-8"))
        if certification_path.exists()
        else {}
    )
    return {
        "final_root": str(FINAL_ROOT),
        "status": certification.get("status", manifest.get("status", "unavailable")),
        "mode": certification.get("mode", "unknown"),
        "counts": manifest.get("counts", {}),
        "certified_at": certification.get("certified_at"),
    }


@app.get("/api/labels")
def labels() -> list[dict]:
    return _query(
        f"""
        SELECT activation_family, activation_label,
               count(*) AS label_rows, count(DISTINCT ticker) AS tickers
        FROM read_parquet('{_path('activation_labels')}')
        GROUP BY 1,2 ORDER BY 1,2
        """
    )


@app.get("/api/activation-catalog")
def activation_catalog() -> dict:
    return {
        "families": ACTIVATION_FAMILY_CATALOG,
        "family_count": len(ACTIVATION_FAMILY_CATALOG),
        "label_count": sum(len(item["labels"]) for item in ACTIVATION_FAMILY_CATALOG),
        "semantics": (
            "Todas las etiquetas son observables descriptivos de D0. Los umbrales "
            "de una misma familia son acumulativos y no son señales de trading."
        ),
    }


@app.get("/api/cohorts")
def cohorts(
    activation_label: str | None = None,
    offset_session: int | None = Query(default=None, ge=0, le=20),
    limit: int = Query(default=500, ge=1, le=5000),
) -> list[dict]:
    clauses: list[str] = []
    parameters: list = []
    if activation_label:
        clauses.append("activation_label = ?")
        parameters.append(activation_label)
    if offset_session is not None:
        clauses.append("offset_session = ?")
        parameters.append(offset_session)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    parameters.append(limit)
    return _query(
        f"SELECT * FROM read_parquet('{_path('cohort_statistics')}'){where} "
        "ORDER BY activation_family, activation_label, offset_session LIMIT ?",
        parameters,
    )


@app.get("/api/event-stats")
def event_stats(activation_label: str | None = None) -> list[dict]:
    clauses: list[str] = []
    parameters: list = []
    if activation_label:
        clauses.append("activation_label = ?")
        parameters.append(activation_label)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    return _query(
        f"SELECT * FROM read_parquet('{_path('activation_event_statistics')}'){where} "
        "ORDER BY activation_family, activation_label, event_label",
        parameters,
    )


@app.get("/api/cases")
def cases(
    activation_label: str | None = None,
    ticker: str | None = None,
    complete_horizon: bool | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    clauses: list[str] = []
    parameters: list = []
    if activation_label:
        clauses.append("list_contains(string_split(activation_labels, ','), ?)")
        parameters.append(activation_label)
    if ticker:
        clauses.append("ticker = ?")
        parameters.append(ticker.upper())
    if complete_horizon is not None:
        clauses.append("complete_horizon = ?")
        parameters.append(complete_horizon)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    parameters.extend([limit, offset])
    return _query(
        f"SELECT * FROM read_parquet('{_path('activation_case_index')}'){where} "
        "ORDER BY anchor_date DESC, ticker LIMIT ? OFFSET ?",
        parameters,
    )


def _context(ticker: str, anchor_date: str) -> list[dict]:
    return _query(
        f"""
        WITH ordered AS (
          SELECT ticker, date, o, h, l, c, v,
                 o_split_normalized, h_split_normalized,
                 l_split_normalized, c_split_normalized,
                 analysis_eligible, quality_state,
                 is_red_candle, is_lower_close, is_lower_high,
                 row_number() OVER (PARTITION BY ticker ORDER BY date) AS rn
          FROM read_parquet('{_path('session_observables')}')
          WHERE ticker = ?
        ), anchor AS (
          SELECT rn AS anchor_rn FROM ordered WHERE date = ?
        )
        SELECT o.ticker, o.date, o.o, o.h, o.l, o.c, o.v,
               o.o_split_normalized, o.h_split_normalized,
               o.l_split_normalized, o.c_split_normalized,
               o.analysis_eligible, o.quality_state,
               o.is_red_candle, o.is_lower_close, o.is_lower_high,
               CAST(o.rn - a.anchor_rn AS INTEGER) AS relative_offset
        FROM ordered o CROSS JOIN anchor a
        ORDER BY o.rn
        """,
        [ticker, anchor_date],
    )


def _adjusted_context(ticker: str, start_date: str, end_date: str) -> list[dict]:
    ticker_root = ADJUSTED_DAILY_ROOT / f"ticker={ticker}"
    if not ticker_root.is_dir():
        return []
    parquet_glob = (ticker_root / "year=*" / "*.parquet").as_posix()
    return _query(
        """
        SELECT ticker, date, o_adjusted, h_adjusted, l_adjusted, c_adjusted, v,
               materialized_price_view,
               o_adjusted > 0 AND h_adjusted > 0 AND l_adjusted > 0
                 AND c_adjusted > 0 AND v >= 0
                 AND h_adjusted >= greatest(o_adjusted, c_adjusted)
                 AND l_adjusted <= least(o_adjusted, c_adjusted)
                 AND h_adjusted >= l_adjusted AS chart_eligible
        FROM read_parquet(?, hive_partitioning=true)
        WHERE ticker = ? AND date BETWEEN ? AND ?
        ORDER BY date
        """,
        [parquet_glob, ticker, start_date, end_date],
    )


def _derive_outcomes(context: list[dict]) -> tuple[list[dict], list[dict], dict]:
    window = [
        row for row in context
        if 0 <= int(row["relative_offset"]) <= 20 and bool(row["analysis_eligible"])
    ]
    if not window:
        raise HTTPException(status_code=500, detail="Activation anchor has no eligible window")
    anchor = window[0]
    anchor_close = float(anchor["c_split_normalized"])
    anchor_high = float(anchor["h_split_normalized"])
    running_high = float("-inf")
    trajectory: list[dict] = []
    for row in window:
        high = float(row["h_split_normalized"])
        close = float(row["c_split_normalized"])
        is_new_high = high > running_high
        running_high = max(running_high, high)
        trajectory.append(
            {
                **row,
                "offset_session": int(row["relative_offset"]),
                "close_from_anchor_pct": close / anchor_close - 1.0,
                "high_from_anchor_pct": high / anchor_high - 1.0,
                "running_episode_high": running_high,
                "drawdown_from_running_high_pct": close / running_high - 1.0,
                "is_new_episode_high": is_new_high,
                "knowledge_role": "outcome",
            }
        )

    peak = max(trajectory, key=lambda row: float(row["h_split_normalized"]))
    events = [
        {
            "event_label": "horizon_peak",
            "event_date": peak["date"],
            "offset_session": peak["offset_session"],
            "knowledge_role": "outcome",
        }
    ]
    definitions = [
        ("first_red_candle", lambda row: bool(row["is_red_candle"]), 0),
        ("first_red_candle_after_d0", lambda row: bool(row["is_red_candle"]), 1),
        ("first_lower_close", lambda row: bool(row["is_lower_close"]), 0),
        ("first_lower_high", lambda row: bool(row["is_lower_high"]), 0),
        ("first_day_without_new_episode_high", lambda row: not bool(row["is_new_episode_high"]), 1),
    ]
    for label, condition, minimum_offset in definitions:
        match = next(
            (row for row in trajectory if row["offset_session"] >= minimum_offset and condition(row)),
            None,
        )
        if match:
            events.append(
                {
                    "event_label": label,
                    "event_date": match["date"],
                    "offset_session": match["offset_session"],
                    "knowledge_role": "outcome",
                }
            )
    summary = {
        "observed_sessions": len(trajectory),
        "complete_horizon": len(trajectory) == 21,
        "right_censored": len(trajectory) != 21,
        "horizon_peak_date": peak["date"],
        "horizon_peak_offset": peak["offset_session"],
    }
    return trajectory, events, summary


@app.get("/api/cases/{activation_case_id}")
def case_detail(
    activation_case_id: str,
    activation_label: str | None = None,
) -> dict:
    cases_found = _query(
        f"SELECT * FROM read_parquet('{_path('activation_case_index')}') "
        "WHERE activation_case_id = ?",
        [activation_case_id],
    )
    if not cases_found:
        raise HTTPException(status_code=404, detail="Activation case not found")
    case = cases_found[0]
    context = _context(case["ticker"], case["anchor_date"])
    adjusted_context = (
        _adjusted_context(
            case["ticker"],
            context[0]["date"],
            context[-1]["date"],
        )
        if context
        else []
    )
    trajectory, events, summary = _derive_outcomes(context)
    activations = _query(
        f"SELECT activation_family, activation_label, observed_value, threshold "
        f"FROM read_parquet('{_path('activation_labels')}') WHERE ticker = ? AND date = ? "
        "ORDER BY activation_family, activation_label",
        [case["ticker"], case["anchor_date"]],
    )
    selected_activation_label = activation_label or str(case["activation_labels"]).split(",")[0]
    occurrences = _query(
        f"SELECT date, activation_family, activation_label, observed_value, threshold "
        f"FROM read_parquet('{_path('activation_labels')}') WHERE ticker = ? "
        "AND activation_label = ? ORDER BY date",
        [case["ticker"], selected_activation_label],
    )
    with sqlite3.connect(ANNOTATION_DB) as con:
        con.row_factory = sqlite3.Row
        notes = [
            dict(row)
            for row in con.execute(
                "SELECT id, episode_id, note, tags, created_at FROM annotations "
                "WHERE episode_id=? ORDER BY id DESC",
                [activation_case_id],
            )
        ]
    for note in notes:
        note["tags"] = json.loads(note["tags"])
    episode_like = {
        "episode_id": activation_case_id,
        "ticker": case["ticker"],
        "anchor_date": case["anchor_date"],
        **summary,
    }
    lifetime_summary = {
        "first_observed_date": context[0]["date"] if context else None,
        "last_observed_date": context[-1]["date"] if context else None,
        "observed_sessions": len(context),
        "eligible_sessions": sum(bool(row["analysis_eligible"]) for row in context),
    }
    adjusted_lifetime_summary = {
        "source_root": str(ADJUSTED_DAILY_ROOT),
        "price_view": (
            adjusted_context[0]["materialized_price_view"] if adjusted_context else None
        ),
        "first_observed_date": adjusted_context[0]["date"] if adjusted_context else None,
        "last_observed_date": adjusted_context[-1]["date"] if adjusted_context else None,
        "observed_sessions": len(adjusted_context),
        "eligible_sessions": sum(bool(row["chart_eligible"]) for row in adjusted_context),
    }
    return {
        "episode": episode_like,
        "context": context,
        "lifetime_summary": lifetime_summary,
        "adjusted_context": adjusted_context,
        "adjusted_lifetime_summary": adjusted_lifetime_summary,
        "trajectory": trajectory,
        "events": events,
        "activations": activations,
        "selected_activation_label": selected_activation_label,
        "occurrences": occurrences,
        "annotations": notes,
    }


@app.post("/api/annotations")
def add_annotation(payload: AnnotationIn) -> dict:
    created_at = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(ANNOTATION_DB) as con:
        cursor = con.execute(
            "INSERT INTO annotations(episode_id,note,tags,created_at) VALUES(?,?,?,?)",
            [payload.episode_id, payload.note, json.dumps(payload.tags), created_at],
        )
        annotation_id = cursor.lastrowid
    return {"id": annotation_id, "episode_id": payload.episode_id, "created_at": created_at}
