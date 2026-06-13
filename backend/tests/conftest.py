# tests/conftest.py
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def auth_headers(client):
    # Register a test user
    client.post("/auth/register", json={
        "email": "pytest@example.com",
        "username": "pytestuser",
        "password": "test1234",
        "full_name": "Pytest User",
    })

    # Login and get token
    response = client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "test1234",
    })

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}