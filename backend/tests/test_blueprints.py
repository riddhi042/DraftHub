# tests/test_blueprints.py
import io


def test_create_blueprint(client, auth_headers):
    # Create a project first
    project = client.post("/projects/", json={
        "name": "Blueprint Test Project",
    }, headers=auth_headers)
    project_id = project.json()["id"]

    response = client.post(f"/projects/{project_id}/blueprints",
        data={"name": "Floor Plan", "description": "Main floor"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Floor Plan"
    assert data["current_version"] == 1


def test_list_blueprints(client, auth_headers):
    project = client.post("/projects/", json={
        "name": "List Blueprint Project",
    }, headers=auth_headers)
    project_id = project.json()["id"]

    client.post(f"/projects/{project_id}/blueprints",
        data={"name": "Blueprint 1"},
        headers=auth_headers,
    )

    response = client.get(f"/projects/{project_id}/blueprints",
        headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_upload_revision(client, auth_headers):
    project = client.post("/projects/", json={
        "name": "Revision Test Project",
    }, headers=auth_headers)
    project_id = project.json()["id"]

    blueprint = client.post(f"/projects/{project_id}/blueprints",
        data={"name": "Revision Blueprint"},
        headers=auth_headers,
    )
    blueprint_id = blueprint.json()["id"]

    # Upload a fake file
    fake_file = io.BytesIO(b"fake blueprint content")
    response = client.post(f"/blueprints/{blueprint_id}/revisions",
        data={"notes": "First revision"},
        files={"file": ("test.pdf", fake_file, "application/pdf")},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["version_number"] == 2
    assert data["original_filename"] == "test.pdf"


def test_list_revisions(client, auth_headers):
    project = client.post("/projects/", json={
        "name": "List Revisions Project",
    }, headers=auth_headers)
    project_id = project.json()["id"]

    blueprint = client.post(f"/projects/{project_id}/blueprints",
        data={"name": "Rev List Blueprint"},
        headers=auth_headers,
    )
    blueprint_id = blueprint.json()["id"]

    fake_file = io.BytesIO(b"content")
    client.post(f"/blueprints/{blueprint_id}/revisions",
        data={"notes": "First"},
        files={"file": ("file.pdf", fake_file, "application/pdf")},
        headers=auth_headers,
    )

    response = client.get(f"/blueprints/{blueprint_id}/revisions",
        headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_delete_blueprint(client, auth_headers):
    project = client.post("/projects/", json={
        "name": "Delete Blueprint Project",
    }, headers=auth_headers)
    project_id = project.json()["id"]

    blueprint = client.post(f"/projects/{project_id}/blueprints",
        data={"name": "To Delete"},
        headers=auth_headers,
    )
    blueprint_id = blueprint.json()["id"]

    response = client.delete(f"/blueprints/{blueprint_id}",
        headers=auth_headers)
    assert response.status_code == 204