# backend/app/routers/auth.py
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from psycopg import Connection
from psycopg.rows import dict_row
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.utils import create_access_token, hash_password, verify_password
from app.db.database import get_connection
from app.services.email import send_verification_email, send_welcome_email

router = APIRouter(prefix="/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)


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
        verification_token = secrets.token_urlsafe(32)

        cursor.execute(
            """
            INSERT INTO users (email, username, hashed_password, full_name, is_verified, verification_token)
            VALUES (%s, %s, %s, %s, FALSE, %s)
            RETURNING id, email, username, full_name, created_at
            """,
            (body.email, body.username, hashed, body.full_name, verification_token),
        )
        user = cursor.fetchone()
        connection.commit()

    # Send verification email
    send_verification_email(body.email, body.username, verification_token)

    return {
        "message": "Account created. Please check your email to verify your account.",
        "user": user,
    }


@router.get("/verify")
def verify_email(token: str, connection: Connection = Depends(get_connection)):
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "SELECT id, email, username FROM users WHERE verification_token = %s",
            (token,),
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token.",
            )

        cursor.execute(
            "UPDATE users SET is_verified = TRUE, verification_token = NULL WHERE id = %s",
            (user["id"],),
        )
        connection.commit()

    send_welcome_email(user["email"], user["username"])

    return {"message": "Email verified successfully. You can now log in."}


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    connection: Connection = Depends(get_connection),
):
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "SELECT id, hashed_password, is_active, is_verified FROM users WHERE email = %s",
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    # if not user["is_verified"]:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Please verify your email before logging in.",
    #     )

    token = create_access_token({"sub": str(user["id"])})
    return {"access_token": token, "token_type": "bearer"}