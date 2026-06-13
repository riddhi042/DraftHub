# tests/test_members.py


def test_invite_member(client, auth_headers):
    # Create a project
    project = client.post("/projects/", json={
        "name": "Member Test Project",
    }, headers=auth_headers)
    project_id = project.json()["id"]

    # Register a second user to invite
    client.post("/auth/register", json={
        "email": "invitee@example.com",
        "username": "invitee",
        "password": "password123",
    })

    response = client.post(f"/projects/{project_id}/members",
        json={"username": "invitee", "role": "editor"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["member"]["role"] == "editor"


def test_list_members(client, auth_headers):
    project = client.post("/projects/", json={
        "name": "List Members Project",
    }, headers=auth_headers)
    project_id = project.json()["id"]

    client.post("/auth/register", json={
        "email": "member2@example.com",
        "username": "member2",
        "password": "password123",
    })
    client.post(f"/projects/{project_id}/members",
        json={"username": "member2", "role": "viewer"},
        headers=auth_headers,
    )

    response = client.get(f"/projects/{project_id}/members",
        headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_invite_duplicate_member(client, auth_headers):
    project = client.post("/projects/", json={
        "name": "Duplicate Member Project",
    }, headers=auth_headers)
    project_id = project.json()["id"]

    client.post("/auth/register", json={
        "email": "dup_member@example.com",
        "username": "dupmember",
        "password": "password123",
    })
    client.post(f"/projects/{project_id}/members",
        json={"username": "dupmember", "role": "viewer"},
        headers=auth_headers,
    )
    # Invite same user again
    response = client.post(f"/projects/{project_id}/members",
        json={"username": "dupmember", "role": "viewer"},
        headers=auth_headers,
    )
    assert response.status_code == 409


def test_invite_nonexistent_user(client, auth_headers):
    project = client.post("/projects/", json={
        "name": "Ghost Member Project",
    }, headers=auth_headers)
    project_id = project.json()["id"]

    response = client.post(f"/projects/{project_id}/members",
        json={"username": "ghostuser", "role": "viewer"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_remove_member(client, auth_headers):
    project = client.post("/projects/", json={
        "name": "Remove Member Project",
    }, headers=auth_headers)
    project_id = project.json()["id"]

    client.post("/auth/register", json={
        "email": "removeme@example.com",
        "username": "removeme",
        "password": "password123",
    })
    invite = client.post(f"/projects/{project_id}/members",
        json={"username": "removeme", "role": "viewer"},
        headers=auth_headers,
    )
    user_id = invite.json()["member"]["user_id"]

    response = client.delete(f"/projects/{project_id}/members/{user_id}",
        headers=auth_headers)
    assert response.status_code == 204