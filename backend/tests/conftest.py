import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def auth_headers(client):
    client.post("/auth/register", json={
        "email": "pytest@example.com",
        "username": "pytestuser",
        "password": "test1234",
        "full_name": "Pytest User",
    })

    # Verify user directly in DB for testing
    from app.db.database import get_connection
    conn = next(get_connection())
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET is_verified = TRUE WHERE email = %s",
            ("pytest@example.com",)
        )
        conn.commit()
    conn.close()

    response = client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "test1234",
    })

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}