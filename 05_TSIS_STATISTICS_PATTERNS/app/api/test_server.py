from fastapi.testclient import TestClient

from .server_v2 import app


client = TestClient(app)


def test_meta_uses_certified_full_census() -> None:
    response = client.get("/api/meta")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "pass"
    assert payload["mode"] == "full"
    assert payload["counts"]["session_observables"] == 9_290_966
    assert payload["counts"]["activation_case_index"] > 0


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
