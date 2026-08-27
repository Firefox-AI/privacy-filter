from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from privacy_filter.core.classes import FilterRequest
from privacy_filter.core.config import env
from privacy_filter.core.utils import authorize_request


def _client() -> TestClient:
    app = FastAPI()

    @app.post("/privacy-filter")
    async def filter_endpoint(
        req: Annotated[FilterRequest, Depends(authorize_request)],
    ) -> dict[str, object]:
        return {
            "items": req.items,
            "mask": req.mask,
            "threshold": req.threshold,
        }

    return TestClient(app)


def test_authorize_request_accepts_x_pf_api_key() -> None:
    env.MASTER_KEY = "test-secret"

    response = _client().post(
        "/privacy-filter",
        headers={"x-pf-api-key": "test-secret"},
        json={"items": ["Bob Saget is a man"]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": ["Bob Saget is a man"],
        "mask": True,
        "threshold": 0.5,
    }


def test_authorize_request_rejects_missing_x_pf_api_key() -> None:
    env.MASTER_KEY = "test-secret"

    response = _client().post("/privacy-filter", json={"items": ["Bob Saget is a man"]})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key."}


def test_authorize_request_rejects_wrong_x_pf_api_key() -> None:
    env.MASTER_KEY = "test-secret"

    response = _client().post(
        "/privacy-filter",
        headers={"x-pf-api-key": "wrong-secret"},
        json={"items": ["Bob Saget is a man"]},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key."}


def test_authorize_request_rejects_missing_master_key() -> None:
    env.MASTER_KEY = None

    response = _client().post(
        "/privacy-filter",
        headers={"x-pf-api-key": "test-secret"},
        json={"items": ["Bob Saget is a man"]},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "MASTER_KEY is not configured."}
