from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb


DEFAULT_FINAL = Path(
    r"C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001"
    r"\runs\20260825_full_v0_1\final"
)
DEFAULT_OUTPUT = Path(
    r"C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001"
)


def rows(con: duckdb.DuckDBPyConnection, sql: str) -> list[dict]:
    columns = [item[0] for item in con.execute(sql).description]
    return [dict(zip(columns, record, strict=True)) for record in con.fetchall()]


def parquet(final_root: Path, name: str) -> str:
    path = final_root / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(path)
    return path.as_posix().replace("'", "''")


def format_percent(value: float | None) -> str:
    return "NA" if value is None else f"{100 * value:.2f}%"


def format_offset(value: float | None) -> str:
    return "NA" if value is None else f"D+{value:g}"


def build(final_root: Path) -> dict:
    manifest = json.loads((final_root / "run_manifest.json").read_text(encoding="utf-8"))
    certification = json.loads(
        (final_root / "terminal_certification.json").read_text(encoding="utf-8")
    )
    variable_audit = json.loads(
        (final_root / "probe_variable_audit_v0_1.json").read_text(encoding="utf-8")
    )
    operation_final = json.loads(
        (final_root.parent / "operation_final_manifest.json").read_text(encoding="utf-8")
    )
    con = duckdb.connect()
    try:
        label_summary = rows(
            con,
            f"""
            SELECT activation_family, activation_label,
                   count(*) AS label_rows,
                   count(DISTINCT ticker) AS tickers
            FROM read_parquet('{parquet(final_root, 'activation_labels')}')
            GROUP BY 1,2 ORDER BY label_rows DESC, activation_label
            """,
        )
        coverage_by_year = rows(
            con,
            f"SELECT year, rows, tickers, CAST(min_date AS DATE) AS min_date, "
            f"CAST(max_date AS DATE) AS max_date FROM "
            f"read_parquet('{parquet(final_root, 'coverage_by_year')}') ORDER BY year",
        )
        episode_summary = rows(
            con,
            f"""
            SELECT count(*) AS episodes,
                   count(DISTINCT ticker) AS tickers,
                   round(100 * avg(complete_horizon::INTEGER), 4) AS complete_share_pct,
                   round(100 * avg(right_censored::INTEGER), 4) AS right_censored_share_pct,
                   median(observed_sessions) AS median_observed_sessions
            FROM read_parquet('{parquet(final_root, 'episodes')}')
            """,
        )[0]
        event_summary = rows(
            con,
            f"""
            SELECT event_label, count(*) AS event_rows,
                   count(DISTINCT episode_id) AS episodes
            FROM read_parquet('{parquet(final_root, 'episode_events')}')
            GROUP BY 1 ORDER BY event_rows DESC, event_label
            """,
        )
        selected_cohorts = rows(
            con,
            f"""
            SELECT activation_label, offset_session, observations, activation_cases, tickers,
                   mean_close_from_anchor_pct, median_close_from_anchor_pct,
                   p10_close_from_anchor_pct, p25_close_from_anchor_pct,
                   p75_close_from_anchor_pct, p90_close_from_anchor_pct,
                   observed_share_red_candle
            FROM read_parquet('{parquet(final_root, 'cohort_statistics')}')
            WHERE activation_label IN (
                'gap_ge_30pct', 'gap_ge_50pct',
                'high_breakout_previous_day', 'high_breakout_previous_week',
                'high_breakout_previous_month'
            ) AND offset_session IN (0, 1, 3, 5, 10, 20)
            ORDER BY activation_label, offset_session
            """,
        )
        selected_event_timings = rows(
            con,
            f"""
            SELECT activation_label, event_label, activation_cases, event_observed,
                   median_offset, p25_offset, p75_offset, p90_offset
            FROM read_parquet('{parquet(final_root, 'activation_event_statistics')}')
            WHERE activation_label IN (
                'gap_ge_30pct', 'gap_ge_50pct',
                'high_breakout_previous_day', 'high_breakout_previous_week',
                'high_breakout_previous_month'
            )
            ORDER BY activation_label, event_label
            """,
        )
        cohort_scope_comparison = rows(
            con,
            f"""
            SELECT d.activation_label,
                   d.activation_cases AS all_activation_cases,
                   c.episodes AS cooldown_cycle_cases,
                   round(100.0 * c.episodes / d.activation_cases, 4) AS cooldown_share_pct
            FROM read_parquet('{parquet(final_root, 'cohort_statistics')}') d
            JOIN read_parquet('{parquet(final_root, 'cycle_cohort_statistics')}') c
              USING (activation_family, activation_label, offset_session)
            WHERE d.offset_session=0 AND d.activation_label IN (
                'gap_ge_30pct', 'gap_ge_50pct',
                'high_breakout_previous_day', 'high_breakout_previous_week',
                'high_breakout_previous_month'
            )
            ORDER BY d.activation_label
            """,
        )
    finally:
        con.close()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if all(
            item.get("status") == "pass"
            for item in (certification, variable_audit, operation_final)
        ) else "fail",
        "mode": certification["mode"],
        "certification_status": certification["status"],
        "independent_audit_status": variable_audit["status"],
        "operation_status": operation_final["status"],
        "scope": certification["checks"]["scope"],
        "counts": manifest["counts"],
        "episode_summary": episode_summary,
        "activation_labels": label_summary,
        "events": event_summary,
        "coverage_by_year": coverage_by_year,
        "selected_cohorts": selected_cohorts,
        "selected_event_timings": selected_event_timings,
        "cohort_scope_comparison": cohort_scope_comparison,
        "interpretation_boundary": (
            "Descriptive observed census only; no inference, signal, execution or PnL claim."
        ),
    }


def markdown(payload: dict, final_root: Path) -> str:
    scope = payload["scope"]
    counts = payload["counts"]
    episode = payload["episode_summary"]
    lines = [
        "# Final Census Readout v0.2",
        "",
        f"- status: `{payload['status']}`",
        f"- mode: `{payload['mode']}`",
        f"- terminal certification: `{payload['certification_status']}`",
        f"- independent audit: `{payload['independent_audit_status']}`",
        f"- operational closure: `{payload['operation_status']}`",
        f"- final root: `{final_root}`",
        f"- sessions: {counts['session_observables']:,}",
        f"- tickers: {scope['observed_tickers']:,}",
        f"- dates: {scope['min_date']} to {scope['max_date']}",
        f"- activation labels: {counts['activation_labels']:,}",
        f"- episodes: {counts['episodes']:,}",
        f"- trajectory rows: {counts['episode_trajectories']:,}",
        f"- event rows: {counts['episode_events']:,}",
        "",
        "This is an exploratory descriptive census. It contains no inference,",
        "trading signal, execution rule or PnL claim.",
        "",
        "## Episode observation",
        "",
        f"- tickers represented: {episode['tickers']:,}",
        f"- complete D0-D20 horizons: {episode['complete_share_pct']:.4f}% observed share",
        f"- right-censored horizons: {episode['right_censored_share_pct']:.4f}% observed share",
        f"- median observed sessions: {episode['median_observed_sessions']:.0f}",
        "",
        "## Activation-label census",
        "",
        "| family | label | rows | tickers |",
        "|---|---|---:|---:|",
    ]
    for item in payload["activation_labels"]:
        lines.append(
            f"| {item['activation_family']} | {item['activation_label']} | "
            f"{item['label_rows']:,} | {item['tickers']:,} |"
        )
    lines += [
        "",
        "## Event census",
        "",
        "| event | rows | episodes |",
        "|---|---:|---:|",
    ]
    for item in payload["events"]:
        lines.append(
            f"| {item['event_label']} | {item['event_rows']:,} | {item['episodes']:,} |"
        )
    lines += [
        "",
        "## Coverage by year",
        "",
        "| year | rows | tickers | min date | max date |",
        "|---:|---:|---:|---|---|",
    ]
    for item in payload["coverage_by_year"]:
        lines.append(
            f"| {item['year']} | {item['rows']:,} | {item['tickers']:,} | "
            f"{item['min_date']} | {item['max_date']} |"
        )
    lines += [
        "",
        "## Selected daily cohorts",
        "",
        "All values below are observed descriptive summaries relative to D0.",
        "",
        "| label | offset | obs. | activation cases | tickers | mean close | median close | P10 | P90 | red-candle share |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["selected_cohorts"]:
        lines.append(
            f"| {item['activation_label']} | D+{item['offset_session']} | "
            f"{item['observations']:,} | {item['activation_cases']:,} | {item['tickers']:,} | "
            f"{format_percent(item['mean_close_from_anchor_pct'])} | "
            f"{format_percent(item['median_close_from_anchor_pct'])} | "
            f"{format_percent(item['p10_close_from_anchor_pct'])} | "
            f"{format_percent(item['p90_close_from_anchor_pct'])} | "
            f"{format_percent(item['observed_share_red_candle'])} |"
        )
    lines += [
        "",
        "## Tail-shape caution",
        "",
        "Gap cohorts contain extreme right tails. Means can be orders of magnitude above medians;",
        "therefore the readout presents both and no single central statistic should be treated as",
        "a complete description of the observed distribution.",
        "",
        "## Direct event timing",
        "",
        "Offsets use the kth available ticker observation; they are not calendar days.",
        "",
        "| label | event | cases | observed | median | P25 | P75 | P90 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["selected_event_timings"]:
        lines.append(
            f"| {item['activation_label']} | {item['event_label']} | "
            f"{item['activation_cases']:,} | {item['event_observed']:,} | "
            f"{format_offset(item['median_offset'])} | {format_offset(item['p25_offset'])} | "
            f"{format_offset(item['p75_offset'])} | {format_offset(item['p90_offset'])} |"
        )
    lines += [
        "",
        "## Direct activations versus cooldown cycles",
        "",
        "Primary cohorts contain all activations. Cooldown cycles are a separate secondary view.",
        "",
        "| label | all activations | cooldown cycles | cooldown share |",
        "|---|---:|---:|---:|",
    ]
    for item in payload["cohort_scope_comparison"]:
        lines.append(
            f"| {item['activation_label']} | {item['all_activation_cases']:,} | "
            f"{item['cooldown_cycle_cases']:,} | {item['cooldown_share_pct']:.4f}% |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final-root", type=Path, default=DEFAULT_FINAL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.final_root)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "FINAL_CENSUS_READOUT_v0_2.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "FINAL_CENSUS_READOUT_v0_2.md").write_text(
        markdown(payload, args.final_root), encoding="utf-8"
    )
    print(json.dumps({"status": payload["status"], "counts": payload["counts"]}))


if __name__ == "__main__":
    main()
