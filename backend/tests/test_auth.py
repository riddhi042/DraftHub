# tests/test_auth.py


def test_register_success(client):
    import uuid
    unique = uuid.uuid4().hex[:8]
    response = client.post("/auth/register", json={
        "email": f"{unique}@example.com",
        "username": unique,
        "password": "password123",
        "full_name": "New User",
    })
    assert response.status_code == 201
    data = response.json()
    assert "email" in data["user"]
    assert "username" in data["user"]

def test_register_duplicate(client):
    # Register same user twice — should fail
    client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "username": "dupuser",
        "password": "password123",
    })
    response = client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "username": "dupuser",
        "password": "password123",
    })
    assert response.status_code == 409


def test_login_success(client):
    client.post("/auth/register", json={
        "email": "logintest@example.com",
        "username": "logintest",
        "password": "password123",
    })
    response = client.post("/auth/login", data={
        "username": "logintest@example.com",
        "password": "password123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    response = client.post("/auth/login", data={
        "username": "logintest@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", data={
        "username": "nobody@example.com",
        "password": "password123",
    })
    assert response.status_code == 401