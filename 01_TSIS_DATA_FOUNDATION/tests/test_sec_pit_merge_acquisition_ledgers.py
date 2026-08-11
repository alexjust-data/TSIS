import gzip
import hashlib
import json
from pathlib import Path

import pytest

from scripts.sec_pit.merge_acquisition_ledgers import merge_ledgers


def _ledger(tmp_path: Path, name: str, url: str, payload: bytes) -> Path:
    object_path = tmp_path / f"{name}.html.gz"
    with gzip.open(object_path, "wb") as handle:
        handle.write(payload)
    ledger = tmp_path / f"{name}.jsonl"
    ledger.write_text(
        json.dumps(
            {
                "url": url,
                "status": "FETCHED",
                "object_path": object_path.as_posix(),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return ledger


def test_merge_deduplicates_identical_objects(tmp_path: Path) -> None:
    first = _ledger(tmp_path, "first", "https://example.test/a", b"same")
    second = _ledger(tmp_path, "second", "https://example.test/a", b"same")
    output = merge_ledgers([first, second], tmp_path / "combined.jsonl")
    rows = output.read_text(encoding="utf-8").splitlines()
    manifest = json.loads(
        output.with_suffix(".manifest.json").read_text(encoding="utf-8")
    )
    assert len(rows) == 1
    assert manifest["duplicate_equivalent_rows"] == 1


def test_merge_rejects_conflicting_objects(tmp_path: Path) -> None:
    first = _ledger(tmp_path, "first", "https://example.test/a", b"first")
    second = _ledger(tmp_path, "second", "https://example.test/a", b"second")
    with pytest.raises(ValueError, match="conflicting immutable objects"):
        merge_ledgers([first, second], tmp_path / "combined.jsonl")
