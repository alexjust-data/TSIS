from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from das_cmdapi.allowlist import is_blocked_command, redacted_command, validate_command
from das_cmdapi.capture import _candidate_symbol_list, _candidate_symbols_from_file, build_command_plan
from das_cmdapi.config import CaptureConfig, MAX_SCREENER_SYMBOLS_CONTRACT_LIMIT, ScreenerDenominator, config_to_dict, load_config
from das_cmdapi.market_cap import MarketCapRecord, MarketCapReference
from das_cmdapi.parsing import extract_price_volume_from_quote, parse_quote_line, parse_toplist_symbols
from das_cmdapi.screener import candidate_passes_denominator


class DasCmdApiContractTests(unittest.TestCase):
    def test_execution_commands_are_blocked(self) -> None:
        for command in (
            "NEWORDER 1 B ABCD SMAT 100 MKT",
            "REPLACE 123 PRICE=1.23",
            "CANCEL 123",
            "CANCEL ALL",
            "COMPLEXORDER Route=SMATL",
            "SLNEWORDER ABCD 100 TESTSL",
            "SLCANCELORDER 123",
            "SLOFFEROPERATION 123 Accept",
        ):
            with self.subTest(command=command):
                self.assertTrue(is_blocked_command(command))
                validation = validate_command(command)
                self.assertFalse(validation.allowed)
                self.assertTrue(validation.blocked)

    def test_socket_login_disabled_by_default(self) -> None:
        validation = validate_command("LOGIN user password account 0")
        self.assertFalse(validation.allowed)
        self.assertEqual(validation.reason, "socket_login_disabled_by_contract")

    def test_socket_login_can_be_enabled_and_is_redacted(self) -> None:
        validation = validate_command("LOGIN user secret account 0", socket_login_enabled=True)
        self.assertTrue(validation.allowed)
        self.assertEqual(redacted_command("LOGIN user secret account 0"), "LOGIN [REDACTED_USER] [REDACTED_PASSWORD] [REDACTED_ACCOUNT] 0")

    def test_locate_avail_query_account_is_redacted(self) -> None:
        self.assertEqual(redacted_command("SLAvailQuery 123456 OMH"), "SLAvailQuery [REDACTED_ACCOUNT] OMH")

    def test_readonly_market_commands_allowed(self) -> None:
        for command in (
            "ECHO OFF",
            "CLIENT",
            "ReturnFullLv1 YES",
            "SB SOXS Lv1",
            "UNSB SOXS Lv1",
            "SB SOXS tms",
            "SB TOPLIST",
            "GET SHORTINFO SOXS",
            "GET LDLU SOXS",
            "GET SymStatus SOXS",
            "GET BP",
            "GET AccountInfo",
            "GET ROUTESTATUS",
        ):
            with self.subTest(command=command):
                self.assertTrue(validate_command(command).allowed)

    def test_locate_inquiry_commands_require_explicit_enable(self) -> None:
        for command in (
            "SLPRICEINQUIRE SOXS 100 SAGE",
            "SLAvailQuery account SOXS",
            "SLReuseQuery ALL",
            "SLRouteMinCharge ALLROUTE",
        ):
            with self.subTest(command=command):
                disabled = validate_command(command)
                self.assertFalse(disabled.allowed)
                self.assertEqual(disabled.reason, "locate_queries_disabled_by_config")
                enabled = validate_command(command, locate_queries_enabled=True)
                self.assertTrue(enabled.allowed)

    def test_max_readonly_plan_includes_account_and_locate_queries_without_execution_commands(self) -> None:
        config = CaptureConfig(
            account_queries_enabled=True,
            locate_queries_enabled=True,
            locate_price_routes=("SAGE",),
            symbols=("SOXS",),
        )
        commands = build_command_plan(config)
        self.assertIn("GET LOCATES", commands)
        self.assertIn("SLReuseQuery ALL", commands)
        self.assertIn("SLRouteMinCharge ALLROUTE", commands)
        self.assertIn("SLAvailQuery <account> SOXS", commands)
        self.assertIn("SLPRICEINQUIRE SOXS 100 SAGE", commands)
        for command in commands:
            self.assertFalse(is_blocked_command(command), command)

    def test_candidate_symbol_list_uses_tsis_reference_when_enabled(self) -> None:
        reference = MarketCapReference(
            path=None,
            records={
                "DEAD": MarketCapRecord("DEAD", 10_000_000, "2026-01-01", "test", status_rebuilt="inactive", classification_1b="inactive_lt_1b"),
                "ABCD": MarketCapRecord("ABCD", 20_000_000, "2026-01-01", "test", status_rebuilt="active", classification_1b="active_lt_1b"),
                "EFGH": MarketCapRecord("EFGH", 30_000_000, "2026-01-01", "test", status_rebuilt="active", classification_1b="active_lt_1b"),
            },
        )
        config = CaptureConfig(
            symbols=("SOXS",),
            screener_symbol_source="seed_toplist_market_cap_reference",
            allow_large_screener_scan=True,
            max_screener_symbols=4,
        )

        symbols = _candidate_symbol_list(config, ["TOPA"], reference)

        self.assertEqual(symbols, ["SOXS", "TOPA", "ABCD", "EFGH"])
        self.assertNotIn("DEAD", symbols)

    def test_candidate_symbols_from_file_filters_pass_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "candidates.csv"
            path.write_text(
                "symbol,filter_status\nOMH,PASS\nBAD,FAIL\nVIVK,PASS\nOMH,PASS\n",
                encoding="utf-8",
            )
            symbols = _candidate_symbols_from_file(path, "PASS")
        self.assertEqual(symbols, ["OMH", "VIVK"])

    def test_screener_denominator(self) -> None:
        denominator = ScreenerDenominator()
        accepted, failures = candidate_passes_denominator(
            {
                "session": "premarket",
                "market_cap_usd": 50_000_000,
                "price_usd": 3.50,
                "volume_shares": 400_000,
            },
            denominator,
        )
        self.assertTrue(accepted)
        self.assertEqual(failures, [])

        accepted, failures = candidate_passes_denominator(
            {
                "session": "regular_market",
                "market_cap_usd": 120_000_000,
                "price_usd": 25.00,
                "volume_shares": 10_000,
            },
            denominator,
        )
        self.assertFalse(accepted)
        self.assertIn("market_cap_above_limit", failures)
        self.assertIn("price_outside_range", failures)
        self.assertIn("volume_below_min", failures)

    def test_quote_parser_extracts_price_and_volume(self) -> None:
        parsed = parse_quote_line("$Quote SOXS A:4.09 Asz:25 B:4.08 Bsz:61 V:433162487 L:4.085 VWAP:3.987")
        self.assertIsNotNone(parsed)
        price, volume, price_source = extract_price_volume_from_quote(parsed)
        self.assertEqual(price, 4.085)
        self.assertEqual(volume, 433162487)
        self.assertEqual(price_source, "das_lv1_L")

    def test_toplist_parser_extracts_symbols(self) -> None:
        symbols = parse_toplist_symbols("$TopLst NASActive YHC LUCY SOXS\n$TopLst AMEXGainers SOXS ABCD")
        self.assertEqual(symbols, ["YHC", "LUCY", "SOXS", "ABCD"])

    def test_capture_config_exports_stream_controls(self) -> None:
        config = CaptureConfig(capture_seconds=60, max_response_bytes=12345)
        payload = config_to_dict(config)
        self.assertEqual(payload["capture_seconds"], 60)
        self.assertEqual(payload["max_response_bytes"], 12345)
        self.assertEqual(payload["login_mode"], "terminal_prompt_socket_login")
        self.assertEqual(payload["max_screener_symbols"], MAX_SCREENER_SYMBOLS_CONTRACT_LIMIT)

    def test_capture_config_caps_screener_symbols_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            path.write_text(json.dumps({"max_screener_symbols": 120}), encoding="utf-8")
            config = load_config(path)
        self.assertEqual(config.max_screener_symbols, MAX_SCREENER_SYMBOLS_CONTRACT_LIMIT)

    def test_capture_config_can_allow_large_screener_scan_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "allow_large_screener_scan": True,
                        "max_screener_symbols": 120,
                        "screener_symbol_source": "seed_toplist_market_cap_reference",
                    }
                ),
                encoding="utf-8",
            )
            config = load_config(path)
        self.assertTrue(config.allow_large_screener_scan)
        self.assertEqual(config.max_screener_symbols, 120)
        self.assertEqual(config.screener_symbol_source, "seed_toplist_market_cap_reference")


if __name__ == "__main__":
    unittest.main()