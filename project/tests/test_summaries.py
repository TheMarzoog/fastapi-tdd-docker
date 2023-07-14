from fastapi import Response
from fastapi.testclient import TestClient

SUMMARIES_ENDPOINT = "/summaries"


def test_create_summary(test_app_with_db: TestClient):
    response: Response = test_app_with_db.post(
        SUMMARIES_ENDPOINT, json={"url": "https://foo.bar"}
    )

    assert response.status_code == 201
    assert response.json()["url"] == "https://foo.bar"


def test_create_summary_invalid_json(test_app: TestClient):
    response: Response = test_app.post(SUMMARIES_ENDPOINT, json={})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "url"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


def test_read_summary(test_app_with_db: TestClient):
    response: Response = test_app_with_db.post(
        SUMMARIES_ENDPOINT, json={"url": "https://foo.bar"}
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.get(f"{SUMMARIES_ENDPOINT}/{summary_id}")
    response_dict = response.json()

    assert response.status_code == 200
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://foo.bar"
    assert response_dict["summary"]
    assert response_dict["created_at"]


def test_read_summary_incorrect_id(test_app_with_db: TestClient):
    response: Response = test_app_with_db.get(f"{SUMMARIES_ENDPOINT}/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_real_all_summaries(test_app_with_db: TestClient):
    response: Response = test_app_with_db.post(
        SUMMARIES_ENDPOINT, json={"url": "https://foo.bar"}
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.get(SUMMARIES_ENDPOINT)
    assert response.status_code == 200

    response_list = response.json()
    assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1

def test_remove_summary(test_app_with_db: TestClient):
    response: Response = test_app_with_db.post(
        SUMMARIES_ENDPOINT, json={"url": "https://foo.bar"}
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.delete(f"{SUMMARIES_ENDPOINT}/{summary_id}")
    assert response.status_code == 200
    assert response.json() == {"id": summary_id, "url": "https://foo.bar"}

def test_remove_summary_incorrect_id(test_app_with_db: TestClient):
    response: Response = test_app_with_db.delete(f"{SUMMARIES_ENDPOINT}/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"
