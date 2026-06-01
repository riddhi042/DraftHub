import psycopg

from app.core.settings import get_settings

settings = get_settings()


def get_connection():
    connection = psycopg.connect(
        user=settings.postgres_user,
        password=settings.postgres_password,
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
    )

    try:
        yield connection
    finally:
        connection.close()