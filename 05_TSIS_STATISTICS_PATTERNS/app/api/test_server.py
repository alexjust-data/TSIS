import json
from pathlib import Path

from fastapi.testclient import TestClient

from .server_v2 import RAW_DAILY_ROOT, _raw_context, app


client = TestClient(app)


def test_meta_uses_terminal_pass_run() -> None:
    response = client.get("/api/meta")
    assert response.status_code == 200
    payload = response.json()
    final_root = Path(payload["final_root"])
    certification = json.loads(
        (final_root / "terminal_certification.json").read_text(encoding="utf-8")
    )
    assert payload["status"] == "pass"
    assert payload["mode"] == certification["mode"]
    assert payload["counts"]["session_observables"] > 0
    assert payload["counts"]["activation_case_index"] > 0
    assert certification["status"] == "pass"


def test_activation_catalog_matches_every_materialized_label() -> None:
    catalog_response = client.get("/api/activation-catalog")
    labels_response = client.get("/api/labels")
    assert catalog_response.status_code == 200
    assert labels_response.status_code == 200

    catalog = catalog_response.json()
    materialized = {row["activation_label"] for row in labels_response.json()}
    documented = {
        label
        for family in catalog["families"]
        for label in family["labels"]
    }
    assert catalog["family_count"] == 5
    assert catalog["label_count"] == 27
    assert materialized == documented
    assert all(family["definition"] and family["formula"] for family in catalog["families"])


def test_drilldown_reaches_full_ticker_lifetime_and_selected_occurrences() -> None:
    labels = client.get("/api/labels")
    assert labels.status_code == 200
    selected_label = labels.json()[0]["activation_label"]

    cases = client.get(
        "/api/cases",
        params={"activation_label": selected_label, "limit": 1},
    )
    assert cases.status_code == 200
    case = cases.json()[0]

    detail = client.get(
        f"/api/cases/{case['activation_case_id']}",
        params={"activation_label": selected_label},
    )
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["episode"]["ticker"] == case["ticker"]
    assert payload["trajectory"]
    assert payload["context"]
    assert payload["selected_activation_label"] == selected_label
    assert payload["lifetime_summary"]["observed_sessions"] == len(payload["context"])
    assert payload["lifetime_summary"]["first_observed_date"] == payload["context"][0]["date"]
    assert payload["lifetime_summary"]["last_observed_date"] == payload["context"][-1]["date"]
    assert payload["adjusted_context"]
    assert payload["adjusted_lifetime_summary"]["price_view"] == "daily_adjusted_v0_1"
    assert payload["adjusted_lifetime_summary"]["observed_sessions"] == len(
        payload["adjusted_context"]
    )
    assert payload["adjusted_context"][0]["date"] == payload["context"][0]["date"]
    assert payload["adjusted_context"][-1]["date"] == payload["context"][-1]["date"]
    assert all(row["ticker"] == case["ticker"] for row in payload["adjusted_context"])
    assert {
        "o_adjusted",
        "h_adjusted",
        "l_adjusted",
        "c_adjusted",
        "v",
        "chart_eligible",
    } <= set(payload["adjusted_context"][0])
    assert "offset_session" not in payload["adjusted_context"][0]
    assert any(row["relative_offset"] == 0 for row in payload["context"])
    assert payload["occurrences"]
    assert all(row["activation_label"] == selected_label for row in payload["occurrences"])
    assert case["anchor_date"][:10] in {row["date"][:10] for row in payload["occurrences"]}

    candle = payload["trajectory"][0]
    assert {
        "o_split_normalized",
        "h_split_normalized",
        "l_split_normalized",
        "c_split_normalized",
    } <= set(candle)
    assert all(row["knowledge_role"] == "outcome" for row in payload["trajectory"])


def test_first_chart_reads_vendor_split_adjusted_raw_daily() -> None:
    rows = _raw_context("IBG", "2026-01-30")
    assert RAW_DAILY_ROOT == Path(r"G:\TSIS\data\ohlcv_daily")
    assert rows
    before_split = next(row for row in rows if row["date"][:10] == "2026-01-29")
    split_day = next(row for row in rows if row["date"][:10] == "2026-01-30")
    assert before_split["c"] == 3.3525
    assert split_day["c"] == 3.73
    assert "c_split_normalized" not in before_split

def test_case_pagination_is_stable_and_non_overlapping() -> None:
    selected_label = client.get("/api/labels").json()[0]["activation_label"]
    first = client.get(
        "/api/cases",
        params={"activation_label": selected_label, "limit": 2, "offset": 0},
    )
    second = client.get(
        "/api/cases",
        params={"activation_label": selected_label, "limit": 2, "offset": 2},
    )
    assert first.status_code == 200
    assert second.status_code == 200
    first_ids = {row["activation_case_id"] for row in first.json()}
    second_ids = {row["activation_case_id"] for row in second.json()}
    assert len(first_ids) == 2
    assert len(second_ids) == 2
    assert first_ids.isdisjoint(second_ids)


def test_unknown_episode_and_invalid_annotation_are_rejected() -> None:
    assert client.get("/api/cases/not-a-real-episode").status_code == 404
    response = client.post(
        "/api/annotations",
        json={"episode_id": "too-short", "note": "", "tags": []},
    )
    assert response.status_code == 422
