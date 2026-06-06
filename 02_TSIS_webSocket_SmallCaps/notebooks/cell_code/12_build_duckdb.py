from __future__ import annotations

import argparse
import json

import duckdb

from _ws_common import CURATED_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="prototype_run")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    normalized_dir = CURATED_DIR / args.label / "normalized"
    db_path = CURATED_DIR / args.label / "analytics.duckdb"

    con = duckdb.connect(str(db_path))
    report: dict[str, dict[str, object]] = {}

    for table_name in ["trades", "quotes", "minute_aggs", "second_aggs", "status"]:
        parquet_path = normalized_dir / f"{table_name}.parquet"
        if not parquet_path.exists():
            report[table_name] = {"loaded": False, "reason": "missing_parquet"}
            continue

        con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_parquet('{parquet_path.as_posix()}')")
        row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        report[table_name] = {"loaded": True, "rows": int(row_count), "path": str(parquet_path)}

    con.close()

    report_path = CURATED_DIR / args.label / "duckdb_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nDuckDB: {db_path}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
