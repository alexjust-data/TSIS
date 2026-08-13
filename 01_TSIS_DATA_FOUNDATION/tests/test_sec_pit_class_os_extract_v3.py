from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy  # noqa: E402
from sec_pit.class_os_extract_v3 import extract_cover_page_class_os_v0_3  # noqa: E402


def extract(text: str):
    return extract_cover_page_class_os_v0_3(
        f"<html>{text}</html>".encode(),
        cik="1",
        accession_number="a",
        form="10-Q",
        accepted_at="2025-08-08T12:00:00Z",
        instrument_id="i",
        security_class_id="s",
        target_class_label="Common Stock",
        source_url="x",
        source_sha256="h",
        availability_policy=EdgarAvailabilityPolicy(),
    )


@pytest.mark.parametrize(
    ("text", "value", "measurement"),
    [
        (
            "Common Stock, Par Value $0.001 72,043,450 (Class) Outstanding "
            "at August 14, 2023",
            72_043_450,
            "2023-08-14",
        ),
        (
            "The number of shares outstanding of our stock at May 7, 2019 is "
            "shown below: Class Number of shares outstanding Common stock, "
            "$0.01 par value 20,415,005",
            20_415_005,
            "2019-05-07",
        ),
        (
            "At October 31, 2025, the number of shares outstanding of the "
            "registrant's common stock was 11,513,075 shares.",
            11_513_075,
            "2025-10-31",
        ),
        (
            "The number of shares outstanding of the registrant's Common Stock "
            "as of February 14, 2025: 34,932,272 shares.",
            34_932_272,
            "2025-02-14",
        ),
        (
            "The number of shares of common stock outstanding as of August 5, "
            "2025: 5,223,015",
            5_223_015,
            "2025-08-05",
        ),
        (
            "The registrant had 2,463,458 shares of its common stock outstanding "
            "as of August 9, 2024.",
            2_463_458,
            "2024-08-09",
        ),
        (
            "ANNUAL REPORT for the fiscal year ended December 31 , 2023. "
            "Indicate the number of outstanding shares of each of the issuer's "
            "classes of capital stock or common stock as of the close of the "
            "period covered by the annual report. Common stock: 1,477,785",
            1_477_785,
            "2023-12-31",
        ),
    ],
)
def test_residual_cover_layouts_are_class_and_date_bound(
    text: str, value: int, measurement: str
) -> None:
    rows = extract(text)
    assert any(row.value == value and row.measurement_at == measurement for row in rows)


def test_residual_layout_does_not_admit_authorized_shares() -> None:
    rows = extract(
        "Common Stock 750,000,000 authorized shares outstanding at August 9, 2024"
    )
    assert rows == []


def test_table_layout_does_not_capture_par_value() -> None:
    rows = extract(
        "The number of shares outstanding of our stock at May 7, 2019 is "
        "shown below: Class Number of shares outstanding Common stock, "
        "$0.01 par value 20,415,005"
    )
    assert {row.value for row in rows} == {20_415_005}
