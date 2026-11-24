"""Kimlik bağımlılıkları (QR-02, T02, F3-03). Sorumlu: Mert.

Kullanım (router'larda):
    @router.post("/mentors/profile")
    def create_mentor_profile(..., user: User = Depends(get_verified_user)): ...

Token yalnız kullanıcı ID'si taşır; kullanıcı ve is_verified/is_admin her istekte DB'den okunur.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.security.token import decode_access_token

# auto_error=False: eksik başlıkta da FastAPI'nin varsayılanı yerine bizim 401 yanıtımız dönsün.
_bearer = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Geçersiz veya eksik kimlik bilgisi.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Token yok, geçersiz veya kullanıcı DB'de yoksa 401; aksi halde giriş yapan User."""
    if credentials is None:
        raise _unauthorized()
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise _unauthorized()
    user = db.get(User, user_id)
    if user is None:
        raise _unauthorized()
    return user


def get_verified_user(user: User = Depends(get_current_user)) -> User:
    """E-postası doğrulanmamış kullanıcıya 403 (T02)."""
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="E-posta adresi doğrulanmamış.")
    return user
