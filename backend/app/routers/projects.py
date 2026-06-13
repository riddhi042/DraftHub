from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import Connection
from psycopg.rows import dict_row

from app.auth.dependencies import get_current_user
from app.db.database import get_connection
from app.schemas.project import ProjectCreate

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get("/")
def get_projects(
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT id, name, description, owner_id, is_archived, created_at, updated_at
            FROM projects
            WHERE owner_id = %s
            ORDER BY created_at DESC;
            """,
            (current_user["id"],),
        )
        projects = cursor.fetchall()
    return projects


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            INSERT INTO projects (name, description, owner_id)
            VALUES (%s, %s, %s)
            RETURNING id, name, description, owner_id, is_archived, created_at, updated_at;
            """,
            (body.name, body.description, current_user["id"]),
        )
        project = cursor.fetchone()
        connection.commit()
    return project


@router.get("/{project_id}")
def get_project(
    project_id: int,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT id, name, description, owner_id, is_archived, created_at, updated_at
            FROM projects WHERE id = %s AND owner_id = %s;
            """,
            (project_id, current_user["id"]),
        )
        project = cursor.fetchone()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


@router.patch("/{project_id}")
def update_project(
    project_id: int,
    body: ProjectCreate,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            UPDATE projects SET name = %s, description = %s, updated_at = NOW()
            WHERE id = %s AND owner_id = %s
            RETURNING id, name, description, owner_id, is_archived, created_at, updated_at;
            """,
            (body.name, body.description, project_id, current_user["id"]),
        )
        project = cursor.fetchone()
        connection.commit()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "DELETE FROM projects WHERE id = %s AND owner_id = %s RETURNING id;",
            (project_id, current_user["id"]),
        )
        deleted = cursor.fetchone()
        connection.commit()
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")


@router.get("/{project_id}/activity")
def get_activity(
    project_id: int,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    with connection.cursor(row_factory=dict_row) as cursor:
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
                al.id,
                al.event_type,
                al.description,
                al.created_at,
                u.username AS actor
            FROM activity_logs al
            LEFT JOIN users u ON u.id = al.actor_id
            WHERE al.project_id = %s
            ORDER BY al.created_at DESC
            LIMIT 50;
            """,
            (project_id,),
        )
        activity = cursor.fetchall()

    return activity