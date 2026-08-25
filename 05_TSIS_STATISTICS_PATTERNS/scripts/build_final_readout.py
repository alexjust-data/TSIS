from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb


DEFAULT_FINAL = Path(
    r"C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001"
    r"\runs\20260824_full_v0_1\final"
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


def build(final_root: Path) -> dict:
    manifest = json.loads((final_root / "run_manifest.json").read_text(encoding="utf-8"))
    certification = json.loads(
        (final_root / "terminal_certification.json").read_text(encoding="utf-8")
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
            f"SELECT * FROM read_parquet('{parquet(final_root, 'coverage_by_year')}') ORDER BY year",
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
            SELECT activation_label, offset_session, observations, episodes, tickers,
                   median_close_from_anchor_pct, p25_close_from_anchor_pct,
                   p75_close_from_anchor_pct, observed_share_red_candle
            FROM read_parquet('{parquet(final_root, 'cohort_statistics')}')
            WHERE activation_label IN (
                'gap_ge_30pct', 'gap_ge_50pct',
                'high_breakout_previous_day', 'high_breakout_previous_week',
                'high_breakout_previous_month'
            ) AND offset_session IN (0, 1, 3, 5, 10, 20)
            ORDER BY activation_label, offset_session
            """,
        )
    finally:
        con.close()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": certification["status"],
        "mode": certification["mode"],
        "scope": certification["checks"]["scope"],
        "counts": manifest["counts"],
        "episode_summary": episode_summary,
        "activation_labels": label_summary,
        "events": event_summary,
        "coverage_by_year": coverage_by_year,
        "selected_cohorts": selected_cohorts,
        "interpretation_boundary": (
            "Descriptive observed census only; no inference, signal, execution or PnL claim."
        ),
    }


def markdown(payload: dict, final_root: Path) -> str:
    scope = payload["scope"]
    counts = payload["counts"]
    episode = payload["episode_summary"]
    lines = [
        "# Final Census Readout v0.1",
        "",
        f"- status: `{payload['status']}`",
        f"- mode: `{payload['mode']}`",
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
        "## Selected daily cohorts",
        "",
        "All values below are observed descriptive summaries relative to D0.",
        "",
        "| label | offset | obs. | episodes | tickers | median close | P25 | P75 | red-candle share |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["selected_cohorts"]:
        def pct(value: float | None) -> str:
            return "NA" if value is None else f"{100 * value:.2f}%"

        lines.append(
            f"| {item['activation_label']} | D+{item['offset_session']} | "
            f"{item['observations']:,} | {item['episodes']:,} | {item['tickers']:,} | "
            f"{pct(item['median_close_from_anchor_pct'])} | "
            f"{pct(item['p25_close_from_anchor_pct'])} | "
            f"{pct(item['p75_close_from_anchor_pct'])} | "
            f"{pct(item['observed_share_red_candle'])} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final-root", type=Path, default=DEFAULT_FINAL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.final_root)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "FINAL_CENSUS_READOUT_v0_1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "FINAL_CENSUS_READOUT_v0_1.md").write_text(
        markdown(payload, args.final_root), encoding="utf-8"
    )
    print(json.dumps({"status": payload["status"], "counts": payload["counts"]}))


if __name__ == "__main__":
    main()
