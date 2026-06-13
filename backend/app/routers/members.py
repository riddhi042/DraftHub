# backend/app/routers/members.py
"""
Collaborator endpoints:
  POST   /projects/{project_id}/members              — invite a user to a project
  GET    /projects/{project_id}/members              — list all members
  PATCH  /projects/{project_id}/members/{user_id}   — update a member's role
  DELETE /projects/{project_id}/members/{user_id}   — remove a member
"""

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import Connection
from psycopg.rows import dict_row
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.db.database import get_connection

router = APIRouter(tags=["Members"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class InviteMember(BaseModel):
    username: str
    role: str = "viewer"  # owner | editor | viewer


class UpdateRole(BaseModel):
    role: str  # owner | editor | viewer


# ── Helper ────────────────────────────────────────────────────────────────────

VALID_ROLES = {"owner", "editor", "viewer"}


def verify_project_owner(project_id: int, user_id: str, connection: Connection):
    """Only the project owner can manage members."""
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "SELECT id FROM projects WHERE id = %s AND owner_id = %s",
            (project_id, user_id),
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the project owner can manage members.",
            )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/projects/{project_id}/members", status_code=status.HTTP_201_CREATED)
def invite_member(
    project_id: int,
    body: InviteMember,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    verify_project_owner(project_id, current_user["id"], connection)

    if body.role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}",
        )

    with connection.cursor(row_factory=dict_row) as cursor:
        # Look up the user being invited
        cursor.execute(
            "SELECT id, username, email FROM users WHERE username = %s",
            (body.username,),
        )
        invitee = cursor.fetchone()

        if not invitee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{body.username}' not found.",
            )

        # Can't invite yourself
        if str(invitee["id"]) == str(current_user["id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot invite yourself.",
            )

        # Check if already a member
        cursor.execute(
            "SELECT id FROM project_members WHERE project_id = %s AND user_id = %s",
            (project_id, invitee["id"]),
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"'{body.username}' is already a member of this project.",
            )

        # Add member
        cursor.execute(
            """
            INSERT INTO project_members (project_id, user_id, role)
            VALUES (%s, %s, %s)
            RETURNING id, project_id, user_id, role, joined_at;
            """,
            (project_id, invitee["id"], body.role),
        )
        member = cursor.fetchone()
        connection.commit()

    # Log activity
    _log_activity(
        connection=connection,
        project_id=project_id,
        actor_id=current_user["id"],
        event_type="member_invited",
        description=f"{body.username} invited as {body.role}",
    )

    return {
        "message": f"'{body.username}' added as {body.role}.",
        "member": member,
    }


@router.get("/projects/{project_id}/members")
def list_members(
    project_id: int,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    # Any member of the project can view the member list
    with connection.cursor(row_factory=dict_row) as cursor:
        # Verify current user has access (owner or member)
        cursor.execute(
            """
            SELECT 1 FROM projects WHERE id = %s AND owner_id = %s
            UNION
            SELECT 1 FROM project_members WHERE project_id = %s AND user_id = %s
            """,
            (project_id, current_user["id"], project_id, current_user["id"]),
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this project.",
            )

        cursor.execute(
            """
            SELECT
                pm.id,
                pm.role,
                pm.joined_at,
                u.id AS user_id,
                u.username,
                u.email,
                u.full_name
            FROM project_members pm
            JOIN users u ON u.id = pm.user_id
            WHERE pm.project_id = %s
            ORDER BY pm.joined_at ASC;
            """,
            (project_id,),
        )
        members = cursor.fetchall()

    return members


@router.patch("/projects/{project_id}/members/{user_id}")
def update_member_role(
    project_id: int,
    user_id: str,
    body: UpdateRole,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    verify_project_owner(project_id, current_user["id"], connection)

    if body.role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}",
        )

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            UPDATE project_members SET role = %s
            WHERE project_id = %s AND user_id = %s
            RETURNING id, project_id, user_id, role, joined_at;
            """,
            (body.role, project_id, user_id),
        )
        member = cursor.fetchone()
        connection.commit()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this project.",
        )

    return member


@router.delete("/projects/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    project_id: int,
    user_id: str,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    verify_project_owner(project_id, current_user["id"], connection)

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            DELETE FROM project_members
            WHERE project_id = %s AND user_id = %s
            RETURNING id;
            """,
            (project_id, user_id),
        )
        deleted = cursor.fetchone()
        connection.commit()

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this project.",
        )

    _log_activity(
        connection=connection,
        project_id=project_id,
        actor_id=current_user["id"],
        event_type="member_removed",
        description=f"User {user_id} removed from project",
    )


# ── Activity log helper ───────────────────────────────────────────────────────

def _log_activity(
    connection: Connection,
    project_id: int,
    actor_id: str,
    event_type: str,
    description: str,
):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO activity_logs (project_id, actor_id, event_type, description)
                VALUES (%s, %s, %s, %s);
                """,
                (project_id, actor_id, event_type, description),
            )
            connection.commit()
    except Exception:
        pass