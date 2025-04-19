import pytest
from unittest.mock import patch
from app.main import app  # update based on your project structure
from app.config import settings  # update if needed


def test_token_generation_success(client):
    payload = {"client_id": settings.CLIENT_ID, "client_secret": settings.CLIENT_SECRET}

    response = client.post("/token", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["error"] is False
    assert data["code"] == "TOKEN_GENERATED"
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "Bearer"


def test_token_generation_invalid_credentials(client):
    payload = {"client_id": "wrong_id", "client_secret": "wrong_secret"}

    response = client.post("/token", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid client credentials"
