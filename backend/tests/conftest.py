import pytest
import psycopg
from fastapi.testclient import TestClient
from app.main import app
from app.core.settings import get_settings

settings = get_settings()


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
    with psycopg.connect(
        user=settings.postgres_user,
        password=settings.postgres_password,
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET is_verified = TRUE WHERE email = %s",
                ("pytest@example.com",)
            )
        conn.commit()

    response = client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "test1234",
    })

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}