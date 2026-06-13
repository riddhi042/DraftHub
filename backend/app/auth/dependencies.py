from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from psycopg import Connection
from psycopg.rows import dict_row

from app.auth.utils import decode_access_token
from app.db.database import get_connection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    connection: Connection = Depends(get_connection),
) -> dict:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exc

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exc

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute("SELECT id, email, username, full_name, is_active FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

    if user is None or not user["is_active"]:
        raise credentials_exc

    return user