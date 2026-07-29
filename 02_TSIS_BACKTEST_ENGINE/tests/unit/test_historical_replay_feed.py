from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tsis_backtest.replay.contracts import ReplayBarEvent, ReplayContractError, ReplayGapEvent  # noqa: E402
from tsis_backtest.replay.historical_feed import HistoricalReplayFeed  # noqa: E402
from tsis_backtest.preflight.real_data_inspector import sha256_file  # noqa: E402


class HistoricalReplayFeedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.session_date = "2026-01-05"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_preflight_pass_is_required(self) -> None:
        report = self._report([], preflight_status="PREFLIGHT_FAIL", resolved=False)

        with self.assertRaises(ReplayContractError) as ctx:
            HistoricalReplayFeed(report).stream_events()

        self.assertEqual(ctx.exception.code, "REPLAY_PREFLIGHT_NOT_PASS")

    def test_physical_inspection_pass_is_required(self) -> None:
        path = self._write_file("AAA", [0])
        report = self._report([path], physical_inspection_status="PHYSICAL_INSPECTION_FAIL")

        with self.assertRaises(ReplayContractError) as ctx:
            HistoricalReplayFeed(report).stream_events()

        self.assertEqual(ctx.exception.code, "REPLAY_PHYSICAL_INSPECTION_NOT_PASS")

    def test_verify_hashes_false_is_not_allowed(self) -> None:
        with self.assertRaises(ReplayContractError) as ctx:
            HistoricalReplayFeed(self._report([]), verify_hashes=False)

        self.assertEqual(ctx.exception.code, "REPLAY_HASH_VERIFICATION_REQUIRED")

    def test_source_hash_mismatch_fails_closed(self) -> None:
        path = self._write_file("AAA", [0])
        report = self._report([path])
        report["snapshot_or_content_hashes"][str(path)] = "0" * 64

        with self.assertRaises(ReplayContractError) as ctx:
            HistoricalReplayFeed(report).stream_events()

        self.assertEqual(ctx.exception.code, "REPLAY_SOURCE_HASH_MISMATCH")

    def test_bars_emit_in_deterministic_available_at_ticker_order(self) -> None:
        bbb = self._write_file("BBB", [1, 0])
        aaa = self._write_file("AAA", [1, 0])
        report = self._report([bbb, aaa])

        events = HistoricalReplayFeed(report).stream_events()
        bar_keys = [(event.available_at.isoformat(), event.ticker) for event in events if isinstance(event, ReplayBarEvent)]

        self.assertEqual(
            bar_keys,
            [
                ("2026-01-05T14:31:00+00:00", "AAA"),
                ("2026-01-05T14:31:00+00:00", "BBB"),
                ("2026-01-05T14:32:00+00:00", "AAA"),
                ("2026-01-05T14:32:00+00:00", "BBB"),
            ],
        )

    def test_gap_precedes_bar_when_available_at_matches(self) -> None:
        path = self._write_file("AAA", [0])
        report = self._report([path], gaps_by_symbol={"AAA": ["2026-01-05T14:30:00Z"]})

        events = HistoricalReplayFeed(report).stream_events()

        self.assertIsInstance(events[0], ReplayGapEvent)
        self.assertIsInstance(events[1], ReplayBarEvent)
        self.assertEqual(events[0].available_at, events[1].available_at)

    def test_bar_available_at_is_one_minute_after_ts_start(self) -> None:
        path = self._write_file("AAA", [0])
        bar = HistoricalReplayFeed(self._report([path])).stream_bars()[0]

        self.assertEqual(bar.ts_start.isoformat(), "2026-01-05T14:30:00+00:00")
        self.assertEqual(bar.ts_end, bar.ts_start + timedelta(minutes=1))
        self.assertEqual(bar.available_at, bar.ts_end)
        self.assertFalse(bar.is_observable_at(bar.ts_start))
        self.assertTrue(bar.is_observable_at(bar.available_at))

    def test_gap_events_are_emitted_without_imputing_bars(self) -> None:
        path = self._write_file("AAA", [0, 2])
        report = self._report([path], gaps_by_symbol={"AAA": ["2026-01-05T14:31:00Z"]})

        events = HistoricalReplayFeed(report).stream_events()
        bars = [event for event in events if isinstance(event, ReplayBarEvent)]
        gaps = [event for event in events if isinstance(event, ReplayGapEvent)]

        self.assertEqual(len(bars), 2)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0].available_at.isoformat(), "2026-01-05T14:32:00+00:00")
        self.assertEqual(gaps[0].reason, "OBSERVED_MINUTE_GAP")

    def test_vendor_vw_is_not_propagated_to_bar_event(self) -> None:
        path = self._write_file("AAA", [0], include_vendor_vw=True)
        bar = HistoricalReplayFeed(self._report([path])).stream_bars()[0]

        self.assertFalse(hasattr(bar, "vw"))
        self.assertEqual(bar.open, 10.0)

    def test_summary_contains_preflight_and_event_sequence_hashes(self) -> None:
        path = self._write_file("AAA", [0, 1])

        summary = HistoricalReplayFeed(self._report([path])).summarize()

        self.assertEqual(len(summary.replay_preflight_report_sha256 or ""), 64)
        self.assertEqual(len(summary.replay_event_sequence_sha256 or ""), 64)

    def test_same_inputs_produce_same_sequence(self) -> None:
        path = self._write_file("AAA", [0, 2])
        report = self._report([path], gaps_by_symbol={"AAA": ["2026-01-05T14:31:00Z"]})

        first = [event.to_dict() for event in HistoricalReplayFeed(report).stream_events()]
        second = [event.to_dict() for event in HistoricalReplayFeed(report).stream_events()]

        self.assertEqual(first, second)

    def test_real_fixture_smoke_replay(self) -> None:
        report_path = Path(
            "C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/"
            "run_preflight_real_fixture_2026_01_05_qg5_v0_2/"
            "data_preflight_report.json"
        )
        if not report_path.exists():
            self.skipTest("local TSIS real fixture preflight report not present")

        feed = HistoricalReplayFeed.from_preflight_report(report_path)
        summary = feed.summarize()
        events = feed.stream_events()
        bars = [event for event in events if isinstance(event, ReplayBarEvent)]
        gaps = [event for event in events if isinstance(event, ReplayGapEvent)]

        self.assertEqual(summary.bar_count, 1828)
        self.assertEqual(summary.gap_count, 122)
        self.assertEqual(summary.event_count, 1950)
        self.assertEqual(len(bars), 1828)
        self.assertEqual(len(gaps), 122)
        self.assertEqual(summary.first_available_at.isoformat(), "2026-01-05T14:31:00+00:00")
        self.assertEqual(summary.last_available_at.isoformat(), "2026-01-05T21:00:00+00:00")
        self.assertFalse(hasattr(bars[0].bar, "vw"))
        self.assertEqual(len(summary.replay_preflight_report_sha256 or ""), 64)
        self.assertEqual(len(summary.replay_event_sequence_sha256 or ""), 64)

    def _write_file(self, symbol: str, minute_offsets: list[int], include_vendor_vw: bool = False) -> Path:
        path = self.root / "qg" / "year=2026" / f"ticker={symbol}" / "month=01" / "part-000.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = []
        for offset in minute_offsets:
            ts = datetime(2026, 1, 5, 14, 30, tzinfo=timezone.utc) + timedelta(minutes=offset)
            row = {
                "ticker": symbol,
                "ts_utc": ts.isoformat().replace("+00:00", "Z"),
                "o": 10.0,
                "h": 10.5,
                "l": 9.8,
                "c": 10.1,
                "v": 1000.0,
                "dataset_id": "synthetic_row_dataset",
                "build_run_id": "synthetic_build",
                "quote_guarded_repair_applied": False,
                "repair_lookup_state": "indexed_no_repair_rows",
            }
            if include_vendor_vw:
                row["vw"] = 10.2
            rows.append(row)
        pq.write_table(pa.Table.from_pylist(rows), path)
        return path

    def _report(
        self,
        source_files: list[Path],
        resolved: bool = True,
        preflight_status: str = "PREFLIGHT_PASS",
        physical_inspection_status: str = "PHYSICAL_INSPECTION_PASS",
        gaps_by_symbol: dict[str, list[str]] | None = None,
    ) -> dict:
        gaps_by_symbol = gaps_by_symbol or {}
        symbols = tuple(path.parts[-3].replace("ticker=", "") for path in source_files)
        hashes = {str(path): sha256_file(path) for path in source_files if path.exists()}
        per_ticker = []
        for path in source_files:
            symbol = path.parts[-3].replace("ticker=", "")
            per_ticker.append(
                {
                    "ticker": symbol,
                    "file": str(path),
                    "observed_minute_gaps": gaps_by_symbol.get(symbol, []),
                }
            )
        return {
            "resolved": resolved,
            "preflight_status": preflight_status,
            "physical_inspection_status": physical_inspection_status,
            "run_id": "synthetic_preflight_run",
            "dataset_id": "synthetic_dataset",
            "fixture_kind": "TSIS_REAL_DATA_FIXTURE",
            "date_range": {"date_start": self.session_date, "date_end": self.session_date},
            "session_policy": "REGULAR_ONLY",
            "timezone": "America/New_York",
            "calendar_id": "XNYS",
            "symbols_available": list(symbols),
            "source_partitions_or_files_consumed": [str(path) for path in source_files],
            "snapshot_or_content_hashes": hashes,
            "price_view_policy": {
                "signal": {"price_view": "quote_guarded_1m"},
                "execution": {"price_view": "quote_guarded_1m"},
                "valuation": {"price_view": "quote_guarded_1m"},
            },
            "physical_inspection": {
                "warning_codes": ["OBSERVED_MINUTE_GAP"] if gaps_by_symbol else [],
                "per_ticker_day_results": per_ticker,
            },
        }


if __name__ == "__main__":
    unittest.main()
