"""JWT erişim token'ı üretme ve çözme (QR-02, F3-03). Sorumlu: Mert.

Ayarlar ortam değişkenlerinden okunur (backend/.env.example):
SECRET_KEY, ALGORITHM (varsayılan HS256), ACCESS_TOKEN_EXPIRE_MINUTES (varsayılan 30).
Token yalnızca kullanıcı ID'sini taşır; rol/yetki her istekte DB'den kontrol edilir.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

# İzinli algoritma → anahtarın en az bayt uzunluğu (RFC 7518 §3.2: hash çıktısı kadar).
_MIN_SECRET_BYTES = {"HS256": 32, "HS384": 48, "HS512": 64}


def _settings():
    secret = os.getenv("SECRET_KEY", "")
    algorithm = os.getenv("ALGORITHM", "HS256")
    minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    if algorithm not in _MIN_SECRET_BYTES:
        raise RuntimeError(f"ALGORITHM şunlardan biri olmalı: {sorted(_MIN_SECRET_BYTES)}")
    if len(secret.encode("utf-8")) < _MIN_SECRET_BYTES[algorithm]:
        raise RuntimeError(
            f"{algorithm} için SECRET_KEY en az {_MIN_SECRET_BYTES[algorithm]} bayt olmalı (.env dosyasını kontrol edin)."
        )
    if minutes <= 0:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES pozitif bir tam sayı olmalı.")
    return secret, algorithm, minutes


def create_access_token(user_id: int) -> str:
    """sub = kullanıcı ID'si (string), exp zorunlu."""
    secret, algorithm, minutes = _settings()
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now, "exp": now + timedelta(minutes=minutes)}
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_access_token(token: str) -> Optional[int]:
    """Geçerli token'da kullanıcı ID'sini, süresi dolmuş/imzası bozuk/eksik alanlı token'da None döndürür."""
    secret, algorithm, _ = _settings()
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm], options={"require": ["exp", "sub"]})
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None
