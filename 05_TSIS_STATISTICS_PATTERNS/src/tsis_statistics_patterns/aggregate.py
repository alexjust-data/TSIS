from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pyarrow.parquet as pq
import yaml

from .certify import EXPECTED_KEYS
from .direct_cohorts import materialize_direct_activation_outputs
from .direct_events import materialize_direct_activation_event_statistics
from .manifest_lineage import parquet_artifact, sha256_file


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sql_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def _copy_union(con: duckdb.DuckDBPyConnection, files: list[Path], output: Path) -> None:
    if not files:
        raise ValueError(f"No parquet parts found for {output.stem}")
    file_expr = "[" + ",".join(f"'{_sql_path(path)}'" for path in files) + "]"
    con.execute(
        f"COPY (SELECT * FROM read_parquet({file_expr}, union_by_name=true)) "
        f"TO '{_sql_path(output)}' (FORMAT PARQUET, COMPRESSION ZSTD)"
    )


def aggregate_run(run_root: Path, config_path: Path) -> dict:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if tuple(float(value) for value in config["statistics"]["quantiles"]) != (
        0.10, 0.25, 0.50, 0.75, 0.90
    ):
        raise ValueError("v0.1 requires quantiles 0.10,0.25,0.50,0.75,0.90")
    if int(config["statistics"]["minimum_group_count"]) != 1:
        raise ValueError("v0.1 requires minimum_group_count=1")
    shard_roots = sorted(run_root.glob("shard=*"))
    if not shard_roots:
        raise ValueError("No shard directories found")
    certifications = [
        json.loads((root / "certification.json").read_text(encoding="utf-8"))
        for root in shard_roots
    ]
    if any(item["status"] != "pass" for item in certifications):
        raise ValueError("At least one shard certification failed")

    final_root = run_root / "final"
    final_root.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(run_root / "aggregation.duckdb"))
    counts: dict[str, int] = {}
    for table_name in EXPECTED_KEYS:
        files = sorted(run_root.glob(f"shard=*/{table_name}/*.parquet"))
        output = final_root / f"{table_name}.parquet"
        _copy_union(con, files, output)
        counts[table_name] = pq.ParquetFile(output).metadata.num_rows

    sessions = _sql_path(final_root / "session_observables.parquet")
    activations = _sql_path(final_root / "activation_labels.parquet")
    episodes = _sql_path(final_root / "episodes.parquet")
    trajectories = _sql_path(final_root / "episode_trajectories.parquet")

    con.execute(
        f"""
        COPY (
          SELECT year(date) AS year,
                 count(*) AS rows,
                 count(DISTINCT ticker) AS tickers,
                 min(date) AS min_date,
                 max(date) AS max_date
          FROM read_parquet('{sessions}')
          GROUP BY 1 ORDER BY 1
        ) TO '{_sql_path(final_root / 'coverage_by_year.parquet')}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    con.execute(
        f"""
        COPY (
          SELECT e.episode_id, e.ticker, e.anchor_date, e.complete_horizon,
                 e.right_censored, e.horizon_peak_offset,
                 string_agg(a.activation_label, ',' ORDER BY a.activation_label) AS activation_labels
          FROM read_parquet('{episodes}') e
          JOIN read_parquet('{activations}') a
            ON a.ticker=e.ticker AND a.date=e.anchor_date
          GROUP BY ALL
          ORDER BY e.ticker, e.anchor_date
        ) TO '{_sql_path(final_root / 'case_index.parquet')}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    con.execute(
        f"""
        COPY (
          SELECT a.activation_family, a.activation_label, t.offset_session,
                 count(*) AS observations,
                 count(DISTINCT t.episode_id) AS episodes,
                 count(DISTINCT t.ticker) AS tickers,
                 avg(t.close_from_anchor_pct) AS mean_close_from_anchor_pct,
                 stddev_samp(t.close_from_anchor_pct) AS std_close_from_anchor_pct,
                 quantile_cont(t.close_from_anchor_pct, 0.10) AS p10_close_from_anchor_pct,
                 quantile_cont(t.close_from_anchor_pct, 0.25) AS p25_close_from_anchor_pct,
                 quantile_cont(t.close_from_anchor_pct, 0.50) AS median_close_from_anchor_pct,
                 quantile_cont(t.close_from_anchor_pct, 0.75) AS p75_close_from_anchor_pct,
                 quantile_cont(t.close_from_anchor_pct, 0.90) AS p90_close_from_anchor_pct,
                 avg(CAST(t.is_red_candle AS INTEGER)) AS observed_share_red_candle,
                 avg(CAST(t.is_new_episode_high AS INTEGER)) AS observed_share_new_episode_high
          FROM read_parquet('{trajectories}') t
          JOIN read_parquet('{episodes}') e USING (episode_id)
          JOIN read_parquet('{activations}') a
            ON a.ticker=e.ticker AND a.date=e.anchor_date
          WHERE t.analysis_eligible
          GROUP BY 1,2,3
          ORDER BY 1,2,3
        ) TO '{_sql_path(final_root / 'cycle_cohort_statistics.parquet')}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    materialize_direct_activation_outputs(
        con, final_root, int(config["windows"]["trajectory_sessions"])
    )
    materialize_direct_activation_event_statistics(
        con, final_root, int(config["windows"]["trajectory_sessions"])
    )
    con.close()
    counts.update(
        {
            "coverage_by_year": pq.ParquetFile(final_root / "coverage_by_year.parquet").metadata.num_rows,
            "case_index": pq.ParquetFile(final_root / "case_index.parquet").metadata.num_rows,
            "cohort_statistics": pq.ParquetFile(final_root / "cohort_statistics.parquet").metadata.num_rows,
            "cycle_cohort_statistics": pq.ParquetFile(final_root / "cycle_cohort_statistics.parquet").metadata.num_rows,
            "activation_case_index": pq.ParquetFile(final_root / "activation_case_index.parquet").metadata.num_rows,
            "activation_event_statistics": pq.ParquetFile(final_root / "activation_event_statistics.parquet").metadata.num_rows,
        }
    )
    pre_manifest = json.loads((run_root / "pre_manifest.json").read_text(encoding="utf-8"))
    output_paths = {name: final_root / f"{name}.parquet" for name in counts}
    artifacts = {name: parquet_artifact(path) for name, path in output_paths.items()}
    upstream_manifest = Path(pre_manifest["upstream_audit_manifest"])
    if not upstream_manifest.exists():
        raise FileNotFoundError(upstream_manifest)
    manifest = {
        "status": "aggregated",
        "created_at": _utc_now(),
        "run_root": str(run_root.resolve()),
        "shards": len(shard_roots),
        "counts": counts,
        "outputs": {name: str(path.resolve()) for name, path in output_paths.items()},
        "artifacts": artifacts,
        "lineage": {
            "code_commit": pre_manifest["code_commit"],
            "config_path": str(config_path.resolve()),
            "config_sha256": pre_manifest["config_sha256"],
            "upstream_audit_manifest": str(upstream_manifest.resolve()),
            "upstream_audit_manifest_sha256": sha256_file(upstream_manifest),
            "canonical_raw_root": "G:/TSIS/data/ohlcv_daily",
        },
    }
    (final_root / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(aggregate_run(args.run_root.resolve(), args.config.resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
