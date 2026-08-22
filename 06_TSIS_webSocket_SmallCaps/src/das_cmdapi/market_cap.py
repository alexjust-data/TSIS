"""Market-cap reference loading for DAS screener v0."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MARKET_CAP_REFERENCE_PATH = Path(
    "C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/backtest/market_cap_last_observed_cutoff/"
    "20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active_inactive.csv"
)


@dataclass(frozen=True)
class MarketCapRecord:
    ticker: str
    market_cap_usd: float
    asof_date: str | None
    source: str
    status_rebuilt: str | None = None
    classification_1b: str | None = None


@dataclass(frozen=True)
class MarketCapReference:
    path: Path | None
    records: dict[str, MarketCapRecord]
    error: str | None = None

    def get(self, symbol: str) -> MarketCapRecord | None:
        return self.records.get(symbol.upper())


def _float_or_none(value: str | None) -> float | None:
    if value is None or value == "" or value.lower() == "nan":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def load_market_cap_reference(path: Path | None) -> MarketCapReference:
    selected = path or DEFAULT_MARKET_CAP_REFERENCE_PATH
    if not selected.exists():
        return MarketCapReference(path=selected, records={}, error=f"market_cap_reference_missing:{selected}")
    records: dict[str, MarketCapRecord] = {}
    try:
        if selected.suffix.lower() == ".csv":
            with selected.open("r", encoding="utf-8-sig", newline="") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    ticker = (row.get("ticker") or "").upper().strip()
                    if not ticker:
                        continue
                    market_cap = _float_or_none(row.get("market_cap_t"))
                    if market_cap is None:
                        market_cap = _float_or_none(row.get("market_cap_t_last_row"))
                    if market_cap is None:
                        continue
                    asof = row.get("anchor_date_used") or row.get("last_row_date") or row.get("last_observed_date")
                    records[ticker] = MarketCapRecord(
                        ticker=ticker,
                        market_cap_usd=market_cap,
                        asof_date=asof,
                        source=str(selected),
                        status_rebuilt=(row.get("status_rebuilt") or None),
                        classification_1b=(row.get("classification_1b") or None),
                    )
        else:
            import pandas as pd  # type: ignore

            df = pd.read_parquet(selected)
            for row in df.to_dict("records"):
                ticker = str(row.get("ticker") or "").upper().strip()
                if not ticker:
                    continue
                market_cap = row.get("market_cap_t")
                if market_cap is None:
                    market_cap = row.get("market_cap_t_last_row")
                if market_cap is None:
                    continue
                try:
                    market_cap_value = float(market_cap)
                except (TypeError, ValueError):
                    continue
                asof = row.get("anchor_date_used") or row.get("last_row_date") or row.get("last_observed_date")
                status_rebuilt = row.get("status_rebuilt")
                classification_1b = row.get("classification_1b")
                records[ticker] = MarketCapRecord(
                    ticker=ticker,
                    market_cap_usd=market_cap_value,
                    asof_date=str(asof) if asof is not None else None,
                    source=str(selected),
                    status_rebuilt=str(status_rebuilt) if status_rebuilt is not None else None,
                    classification_1b=str(classification_1b) if classification_1b is not None else None,
                )
    except Exception as exc:  # pragma: no cover - defensive path for local dependencies
        return MarketCapReference(path=selected, records={}, error=f"market_cap_reference_load_failed:{exc}")
    return MarketCapReference(path=selected, records=records)
