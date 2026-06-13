# tests/test_projects.py


def test_create_project(client, auth_headers):
    response = client.post("/projects/", json={
        "name": "Test Project",
        "description": "A test project",
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data


def test_list_projects(client, auth_headers):
    response = client.get("/projects/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_project(client, auth_headers):
    # Create a project first
    create = client.post("/projects/", json={
        "name": "Get Test",
        "description": "For get test",
    }, headers=auth_headers)
    project_id = create.json()["id"]

    response = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == project_id


def test_update_project(client, auth_headers):
    create = client.post("/projects/", json={
        "name": "Old Name",
    }, headers=auth_headers)
    project_id = create.json()["id"]

    response = client.patch(f"/projects/{project_id}", json={
        "name": "New Name",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_delete_project(client, auth_headers):
    create = client.post("/projects/", json={
        "name": "To Delete",
    }, headers=auth_headers)
    project_id = create.json()["id"]

    response = client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 204


def test_get_project_unauthorized(client):
    response = client.get("/projects/1")
    assert response.status_code == 401