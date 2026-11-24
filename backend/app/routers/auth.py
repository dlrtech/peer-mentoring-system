"""Kayıt ve giriş API'leri (UC-1). Sorumlu: Dilara.

POST /auth/register -> 201  yeni hesap, is_verified=false
POST /auth/login    -> 200  { access_token, token_type }

Parola hash'leme ve token üretimi Mert'in app.security modüllerinden gelir.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.security.password import hash_password, verify_password
from app.security.token import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# Kayıtlı olmayan e-postayla girişte de bir Argon2 doğrulaması yapılır; böylece
# yanıt süresinden hesabın var olup olmadığı anlaşılmaz.
_DUMMY_HASH = hash_password("dummy-password-for-timing")

DUPLICATE_EMAIL = "Email already registered"
INVALID_CREDENTIALS = "Incorrect email or password"


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=DUPLICATE_EMAIL,
        )

    # is_verified ve is_admin bilerek verilmez; modeldeki varsayılan false kullanılır.
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        # Aynı e-posta ile eşzamanlı iki kayıt: unique index ikincisini reddeder.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=DUPLICATE_EMAIL,
        )

    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))

    if user is None:
        verify_password(payload.password, _DUMMY_HASH)
        password_ok = False
    else:
        password_ok = verify_password(payload.password, user.password_hash)

    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Doğrulanmamış hesap giriş yapabilir; korumalı işlemlerde 403'ü
    # Mert'in get_verified_user() bağımlılığı verir.
    return TokenResponse(access_token=create_access_token(user.id))
