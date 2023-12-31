import pytest
from fastapi import Response
from fastapi.testclient import TestClient

from app.api import summaries

SUMMARIES_ENDPOINT = "/summaries"


def test_create_summary(test_app_with_db: TestClient, monkeypatch):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

    response: Response = test_app_with_db.post(
        SUMMARIES_ENDPOINT, json={"url": "https://foo.bar"}
    )

    assert response.status_code == 201
    assert response.json()["url"] == "https://foo.bar"


def test_create_summary_invalid_json(
    test_app: TestClient, test_app_with_db: TestClient
):
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

    response = test_app_with_db.post(SUMMARIES_ENDPOINT, json={"url": "invalid://url"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "URL scheme not permitted"


def test_read_summary(test_app_with_db: TestClient, monkeypatch):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

    response: Response = test_app_with_db.post(
        SUMMARIES_ENDPOINT, json={"url": "https://foo.bar"}
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.get(f"{SUMMARIES_ENDPOINT}/{summary_id}")
    response_dict = response.json()

    assert response.status_code == 200
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://foo.bar"
    assert response_dict["summary"] == ""
    assert response_dict["created_at"]


def test_read_summary_incorrect_id(test_app_with_db: TestClient):
    response: Response = test_app_with_db.get(f"{SUMMARIES_ENDPOINT}/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"

    response = test_app_with_db.get(f"{SUMMARIES_ENDPOINT}/0/")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["path", "id"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
                "ctx": {"limit_value": 0},
            }
        ]
    }


def test_real_all_summaries(test_app_with_db: TestClient, monkeypatch):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

    response: Response = test_app_with_db.post(
        SUMMARIES_ENDPOINT, json={"url": "https://foo.bar"}
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.get(SUMMARIES_ENDPOINT)
    assert response.status_code == 200

    response_list = response.json()
    assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1


def test_remove_summary(test_app_with_db: TestClient, monkeypatch):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

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

    response = test_app_with_db.delete(f"{SUMMARIES_ENDPOINT}/0/")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["path", "id"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
                "ctx": {"limit_value": 0},
            }
        ]
    }


def test_update_summary(test_app_with_db: TestClient, monkeypatch):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

    response: Response = test_app_with_db.post(
        SUMMARIES_ENDPOINT, json={"url": "https://foo.bar"}
    )

    summary_id = response.json()["id"]
    response = test_app_with_db.put(
        f"{SUMMARIES_ENDPOINT}/{summary_id}",
        json={"url": "https://new-foo.bar", "summary": "updated!"},
    )

    assert response.status_code == 200
    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://new-foo.bar"
    assert response_dict["summary"] == "updated!"
    assert response_dict["created_at"]


@pytest.mark.parametrize(
    "summary_id, payload, status_code, detail",
    [
        [
            999,
            {"url": "https://foo.bar", "summary": "updated!"},
            404,
            "Summary not found",
        ],
        [
            0,
            {"url": "https://foo.bar", "summary": "updated!"},
            422,
            [
                {
                    "loc": ["path", "id"],
                    "msg": "ensure this value is greater than 0",
                    "type": "value_error.number.not_gt",
                    "ctx": {"limit_value": 0},
                }
            ],
        ],
        [
            1,
            {},
            422,
            [
                {
                    "loc": ["body", "url"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
                {
                    "loc": ["body", "summary"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ],
        ],
        [
            1,
            {"url": "https://foo.bar"},
            422,
            [
                {
                    "loc": ["body", "summary"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ],
        ],
    ],
)
def test_update_summary_invalid(
    test_app_with_db: TestClient, summary_id, payload, status_code, detail
):
    response: Response = test_app_with_db.put(
        f"{SUMMARIES_ENDPOINT}/{summary_id}/", json=payload
    )
    assert response.status_code == status_code
    assert response.json()["detail"] == detail


def test_update_summary_invalid_url(test_app: TestClient):
    response: Response = test_app.put(
        f"{SUMMARIES_ENDPOINT}/1/", json={"url": "invalid://url", "summary": "updated!"}
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "URL scheme not permitted"
