from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from psycopg import Connection
from psycopg.rows import dict_row
from pydantic import BaseModel, EmailStr

from app.auth.utils import create_access_token, hash_password, verify_password
from app.db.database import get_connection

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, connection: Connection = Depends(get_connection)):
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "SELECT id FROM users WHERE email = %s OR username = %s",
            (body.email, body.username),
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with that email or username already exists.",
            )

        hashed = hash_password(body.password)
        cursor.execute(
            """
            INSERT INTO users (email, username, hashed_password, full_name)
            VALUES (%s, %s, %s, %s)
            RETURNING id, email, username, full_name, created_at
            """,
            (body.email, body.username, hashed, body.full_name),
        )
        user = cursor.fetchone()
        connection.commit()

    return {"message": "Account created.", "user": user}


@router.post("/login", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    connection: Connection = Depends(get_connection),
):
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "SELECT id, hashed_password, is_active FROM users WHERE email = %s",
            (form.username,),
        )
        user = cursor.fetchone()

    if not user or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")

    token = create_access_token({"sub": str(user["id"])})
    return {"access_token": token, "token_type": "bearer"}