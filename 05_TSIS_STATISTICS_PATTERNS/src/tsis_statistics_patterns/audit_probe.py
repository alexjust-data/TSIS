from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import yaml

from .operational_certification import certify_operational_surface


def _finite_difference(actual: pd.Series, expected: pd.Series) -> float:
    mask = actual.notna() & expected.notna()
    if not mask.any():
        return 0.0
    return float(np.nanmax(np.abs(actual[mask].astype(float) - expected[mask].astype(float))))


def _safe_ratio(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a / b.where(b.ne(0))).replace([np.inf, -np.inf], np.nan)


def audit_probe(run_root: Path, config_path: Path) -> dict:
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    final_root = run_root / "final"
    sessions = pd.read_parquet(final_root / "session_observables.parquet")
    sessions = sessions.sort_values(["ticker", "date"], kind="mergesort").reset_index(drop=True)
    grouped = sessions.groupby("ticker", sort=False, observed=True)
    expected = {
        "gap_pct": _safe_ratio(sessions["o_split_normalized"], grouped["c_split_normalized"].shift(1)) - 1,
        "open_close_pct": _safe_ratio(sessions["c_split_normalized"], sessions["o_split_normalized"]) - 1,
        "close_close_pct": _safe_ratio(sessions["c_split_normalized"], grouped["c_split_normalized"].shift(1)) - 1,
        "range_pct": _safe_ratio(
            sessions["h_split_normalized"] - sessions["l_split_normalized"],
            grouped["c_split_normalized"].shift(1),
        ),
        "close_location": _safe_ratio(
            sessions["c_split_normalized"] - sessions["l_split_normalized"],
            sessions["h_split_normalized"] - sessions["l_split_normalized"],
        ),
    }
    formula_checks = {}
    for name, values in expected.items():
        max_abs_error = _finite_difference(sessions[name], values)
        formula_checks[name] = {
            "max_abs_error": max_abs_error,
            "status": "pass" if max_abs_error <= 1e-12 else "fail",
        }

    rv_n = int(cfg["windows"]["relative_volume_sessions"])
    prior_median = grouped["v"].transform(
        lambda s: s.shift(1).rolling(rv_n, min_periods=rv_n).median()
    )
    rv_error = _finite_difference(sessions["relative_volume"], _safe_ratio(sessions["v"], prior_median))
    formula_checks["relative_volume"] = {
        "max_abs_error": rv_error,
        "status": "pass" if rv_error <= 1e-12 else "fail",
    }

    for label, window in cfg["windows"]["resistance_sessions"].items():
        prior = grouped["h_split_normalized"].transform(
            lambda s, n=int(window): s.shift(1).rolling(n, min_periods=n).max()
        )
        error = _finite_difference(sessions[f"prior_high_{label}"], prior)
        formula_checks[f"prior_high_{label}"] = {
            "max_abs_error": error,
            "status": "pass" if error <= 1e-12 else "fail",
        }

    schema_checks = {}
    for table_name in (
        "session_observables",
        "activation_labels",
        "episodes",
        "episode_trajectories",
        "episode_events",
    ):
        schemas = []
        for path in sorted(run_root.glob(f"shard=*/{table_name}/*.parquet")):
            schemas.append(str(pq.ParquetFile(path).schema_arrow))
        equivalent = len(set(schemas)) == 1 and len(schemas) == int(cfg["sharding"]["count"])
        schema_checks[table_name] = {
            "observed_schemas": len(set(schemas)),
            "files": len(schemas),
            "status": "pass" if equivalent else "fail",
        }

    finite_checks = {}
    for path in sorted(final_root.glob("*.parquet")):
        frame = pd.read_parquet(path)
        numeric = frame.select_dtypes(include=[np.number])
        infinite = int(np.isinf(numeric.to_numpy(dtype=float, na_value=np.nan)).sum()) if not numeric.empty else 0
        finite_checks[path.stem] = {
            "infinite_values": infinite,
            "status": "pass" if infinite == 0 else "fail",
        }

    roles = {
        "session_observables": sorted(sessions["knowledge_role"].dropna().unique().tolist()),
        "activation_labels": sorted(
            pd.read_parquet(final_root / "activation_labels.parquet", columns=["knowledge_role"])["knowledge_role"].unique().tolist()
        ),
        "episode_trajectories": sorted(
            pd.read_parquet(final_root / "episode_trajectories.parquet", columns=["knowledge_role"])["knowledge_role"].unique().tolist()
        ),
        "episode_events": sorted(
            pd.read_parquet(final_root / "episode_events.parquet", columns=["knowledge_role"])["knowledge_role"].unique().tolist()
        ),
    }
    role_pass = roles == {
        "session_observables": ["observable"],
        "activation_labels": ["observable"],
        "episode_trajectories": ["outcome"],
        "episode_events": ["outcome"],
    }
    all_checks = [item["status"] for item in formula_checks.values()]
    all_checks += [item["status"] for item in schema_checks.values()]
    all_checks += [item["status"] for item in finite_checks.values()]
    operational_surface = certify_operational_surface(run_root, require_final=True)
    overall = (
        all(value == "pass" for value in all_checks)
        and role_pass
        and operational_surface["status"] == "pass"
    )
    sample_columns = [
        "ticker", "date", "gap_pct", "relative_volume", "range_pct",
        "close_location", "analysis_eligible", "quality_state",
    ]
    result = {
        "status": "pass" if overall else "fail",
        "audit_version": "v0_1",
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "formula_checks": formula_checks,
        "schema_checks": schema_checks,
        "finite_checks": finite_checks,
        "knowledge_roles": roles,
        "knowledge_role_status": "pass" if role_pass else "fail",
        "operational_surface": operational_surface,
        "readable_sample": sessions[sample_columns].head(20).assign(
            date=lambda x: x["date"].astype(str)
        ).to_dict("records"),
    }
    (final_root / "probe_variable_audit_v0_1.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    lines = [
        "# Probe Variable Audit v0.1", "", f"Status: `{result['status']}`", "",
        "## Formula checks", "",
    ]
    lines.extend(
        f"- `{name}`: `{check['status']}`, max_abs_error={check['max_abs_error']}"
        for name, check in formula_checks.items()
    )
    lines += ["", "## Schema checks", ""]
    lines.extend(f"- `{name}`: `{check['status']}`" for name, check in schema_checks.items())
    lines += ["", "## Finite values", ""]
    lines.extend(f"- `{name}`: `{check['status']}`" for name, check in finite_checks.items())
    lines += ["", "## Knowledge roles", "", f"- status: `{'pass' if role_pass else 'fail'}`"]
    (final_root / "probe_variable_audit_v0_1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    result = audit_probe(args.run_root.resolve(), args.config.resolve())
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
