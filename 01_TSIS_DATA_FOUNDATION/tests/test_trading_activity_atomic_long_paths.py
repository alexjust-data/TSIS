from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from trading_activity_binding_a_multisession_engine import (  # noqa: E402
    atomic_write_parquet,
)


def test_atomic_hash_sidecar_supports_long_governed_partition_path(tmp_path: Path):
    parent = tmp_path
    index = 0
    target = parent / "part-00000.parquet"
    while len(str(target)) < 227:
        parent = parent / f"governed_partition_segment_{index:02d}"
        target = parent / "part-00000.parquet"
        index += 1
    parent.mkdir(parents=True)

    result = atomic_write_parquet(pd.DataFrame({"value": [1, 2]}), target)

    assert result["rows"] == 2
    assert target.is_file()
    assert target.with_suffix(target.suffix + ".sha256").is_file()
    assert not list(parent.glob(".t*"))
