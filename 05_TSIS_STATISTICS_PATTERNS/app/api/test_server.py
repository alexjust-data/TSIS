import json
from pathlib import Path

from fastapi.testclient import TestClient

from .server_v2 import app


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


def test_drilldown_reaches_real_daily_candles() -> None:
    labels = client.get("/api/labels")
    assert labels.status_code == 200
    assert labels.json()

    cases = client.get("/api/cases", params={"limit": 1})
    assert cases.status_code == 200
    case = cases.json()[0]

    detail = client.get(f"/api/cases/{case['activation_case_id']}")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["episode"]["ticker"] == case["ticker"]
    assert payload["trajectory"]
    candle = payload["trajectory"][0]
    assert {"o_split_normalized", "h_split_normalized", "l_split_normalized", "c_split_normalized"} <= set(candle)
    assert all(row["knowledge_role"] == "outcome" for row in payload["trajectory"])


def test_unknown_episode_and_invalid_annotation_are_rejected() -> None:
    assert client.get("/api/cases/not-a-real-episode").status_code == 404
    response = client.post(
        "/api/annotations",
        json={"episode_id": "too-short", "note": "", "tags": []},
    )
    assert response.status_code == 422
