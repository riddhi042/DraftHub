# backend/app/routers/blueprints.py
"""
Blueprint endpoints:
  POST   /projects/{project_id}/blueprints         — create a blueprint
  GET    /projects/{project_id}/blueprints         — list blueprints in project
  GET    /blueprints/{blueprint_id}                — get one blueprint
  DELETE /blueprints/{blueprint_id}                — delete blueprint

Revision endpoints:
  POST   /blueprints/{blueprint_id}/revisions      — upload a new revision
  GET    /blueprints/{blueprint_id}/revisions      — list all revisions
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from psycopg import Connection
from psycopg.rows import dict_row

from app.auth.dependencies import get_current_user
from app.db.database import get_connection
from app.services.file_storage import delete_file, save_upload

router = APIRouter(tags=["Blueprints"])


# ── Helper ────────────────────────────────────────────────────────────────────

def get_project_or_404(project_id: int, user_id: str, connection: Connection) -> dict:
    """Fetch project and verify ownership — raises 404 if not found."""
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "SELECT id FROM projects WHERE id = %s AND owner_id = %s",
            (project_id, user_id),
        )
        project = cursor.fetchone()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


# ── Blueprint endpoints ───────────────────────────────────────────────────────

@router.post("/projects/{project_id}/blueprints", status_code=status.HTTP_201_CREATED)
def create_blueprint(
    project_id: int,
    name: str = Form(...),
    description: str = Form(None),
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    get_project_or_404(project_id, current_user["id"], connection)

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            INSERT INTO blueprints (project_id, name, description)
            VALUES (%s, %s, %s)
            RETURNING id, project_id, name, description, current_version, created_at;
            """,
            (project_id, name, description),
        )
        blueprint = cursor.fetchone()
        connection.commit()

    return blueprint


@router.get("/projects/{project_id}/blueprints")
def list_blueprints(
    project_id: int,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    get_project_or_404(project_id, current_user["id"], connection)

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT id, project_id, name, description, current_version, created_at, updated_at
            FROM blueprints
            WHERE project_id = %s
            ORDER BY created_at DESC;
            """,
            (project_id,),
        )
        blueprints = cursor.fetchall()

    return blueprints


@router.get("/blueprints/{blueprint_id}")
def get_blueprint(
    blueprint_id: str,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT b.id, b.project_id, b.name, b.description,
                   b.current_version, b.created_at, b.updated_at
            FROM blueprints b
            JOIN projects p ON p.id = b.project_id
            WHERE b.id = %s AND p.owner_id = %s;
            """,
            (blueprint_id, current_user["id"]),
        )
        blueprint = cursor.fetchone()

    if not blueprint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blueprint not found.")
    return blueprint


@router.delete("/blueprints/{blueprint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blueprint(
    blueprint_id: str,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    # Get all revision file paths before deleting
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT r.file_path FROM blueprint_revisions r
            JOIN blueprints b ON b.id = r.blueprint_id
            JOIN projects p ON p.id = b.project_id
            WHERE r.blueprint_id = %s AND p.owner_id = %s;
            """,
            (blueprint_id, current_user["id"]),
        )
        revisions = cursor.fetchall()

        cursor.execute(
            """
            DELETE FROM blueprints
            WHERE id = %s AND project_id IN (
                SELECT id FROM projects WHERE owner_id = %s
            )
            RETURNING id;
            """,
            (blueprint_id, current_user["id"]),
        )
        deleted = cursor.fetchone()
        connection.commit()

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blueprint not found.")

    # Clean up files from disk
    for rev in revisions:
        delete_file(rev["file_path"])


# ── Revision endpoints ────────────────────────────────────────────────────────

@router.post("/blueprints/{blueprint_id}/revisions", status_code=status.HTTP_201_CREATED)
def upload_revision(
    blueprint_id: str,
    file: UploadFile = File(...),
    notes: str = Form(None),
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    # Verify blueprint belongs to current user's project
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT b.id, b.current_version, b.project_id
            FROM blueprints b
            JOIN projects p ON p.id = b.project_id
            WHERE b.id = %s AND p.owner_id = %s;
            """,
            (blueprint_id, current_user["id"]),
        )
        blueprint = cursor.fetchone()

    if not blueprint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blueprint not found.")

    # Save file to disk
    file_meta = save_upload(
        file=file,
        project_id=blueprint["project_id"],
        blueprint_id=blueprint_id,
    )

    new_version = blueprint["current_version"] + 1

    with connection.cursor(row_factory=dict_row) as cursor:
        # Insert revision record
        cursor.execute(
            """
            INSERT INTO blueprint_revisions
                (blueprint_id, uploader_id, version_number,
                 original_filename, stored_filename, file_path,
                 file_size_bytes, mime_type, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, blueprint_id, version_number, original_filename,
                      file_size_bytes, mime_type, notes, created_at;
            """,
            (
                blueprint_id,
                current_user["id"],
                new_version,
                file_meta["original_filename"],
                file_meta["stored_filename"],
                file_meta["file_path"],
                file_meta["file_size_bytes"],
                file_meta["mime_type"],
                notes,
            ),
        )
        revision = cursor.fetchone()

        # Update current_version on the blueprint
        cursor.execute(
            "UPDATE blueprints SET current_version = %s, updated_at = NOW() WHERE id = %s",
            (new_version, blueprint_id),
        )
        connection.commit()

    # Log activity
    _log_activity(
        connection=connection,
        project_id=blueprint["project_id"],
        actor_id=current_user["id"],
        event_type="revision_uploaded",
        description=f"Uploaded revision v{new_version} of blueprint {blueprint_id}",
    )

    return revision


@router.get("/blueprints/{blueprint_id}/revisions")
def list_revisions(
    blueprint_id: str,
    connection: Connection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT r.id, r.version_number, r.original_filename,
                   r.file_size_bytes, r.mime_type, r.notes,
                   r.created_at, u.username AS uploaded_by
            FROM blueprint_revisions r
            JOIN blueprints b ON b.id = r.blueprint_id
            JOIN projects p ON p.id = b.project_id
            LEFT JOIN users u ON u.id = r.uploader_id
            WHERE r.blueprint_id = %s AND p.owner_id = %s
            ORDER BY r.version_number ASC;
            """,
            (blueprint_id, current_user["id"]),
        )
        revisions = cursor.fetchall()

    return revisions


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
        pass  # Activity logging should never break the main request