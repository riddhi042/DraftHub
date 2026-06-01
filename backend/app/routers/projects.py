from fastapi import APIRouter, Depends
from psycopg import Connection
from psycopg.rows import dict_row

from app.db.database import get_connection

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get("/")
def get_projects(connection: Connection = Depends(get_connection)):
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT id, name, description, created_at
            FROM projects
            ORDER BY created_at DESC;
            """
        )

        projects = cursor.fetchall()

    return projects