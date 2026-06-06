from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from time import perf_counter


SCRIPT_00 = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v1\cell_code\00_load_quotes_run_artifacts.py")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build quotes C+D notebook artifacts without loading the full parquet in Jupyter.")
    parser.add_argument("--refresh", action="store_true", help="Rebuild artifacts even if cached.")
    args = parser.parse_args()

    mod00 = runpy.run_path(str(SCRIPT_00))
    payload = mod00["load_quotes_artifacts"]()
    handle = payload["quotes_handle_cd"]

    t0 = perf_counter()
    artifacts = mod00["build_quotes_cd_artifacts"](handle, refresh=args.refresh)
    manifest = mod00["write_manifest"](handle, refresh=True)
    elapsed = perf_counter() - t0

    summary = {
        "elapsed_sec": round(elapsed, 2),
        "cache_dir": str(handle.cache_dir),
        "row_count": int(handle.row_count()),
        "snapshot_rows_total": int(artifacts["snapshot"].iloc[0]["rows_total"]),
        "top_hard_issue": None if artifacts["hard_issue_counts"].empty else str(artifacts["hard_issue_counts"].iloc[0]["issue"]),
        "top_warn": None if artifacts["warn_counts"].empty else str(artifacts["warn_counts"].iloc[0]["warn"]),
        "top_taxonomy": None if artifacts["taxonomy_summary"].empty else str(artifacts["taxonomy_summary"].iloc[0]["taxonomy"]),
        "manifest_path": str(handle.cache_path("manifest", suffix=".json")),
    }
    print(json.dumps(summary, indent=2))
    print(f"artifacts_written={len(manifest['artifacts'])}")


if __name__ == "__main__":
    main()
