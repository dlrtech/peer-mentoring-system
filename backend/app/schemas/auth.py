"""Kayıt ve giriş istek/yanıt şemaları (UC-1). Sorumlu: Dilara.

Alan sınırları frontend doğrulamasıyla aynıdır (Register.jsx):
ad soyad 2-100, e-posta en fazla 254, parola 8-128 karakter.
is_verified / is_admin istemciden alınmaz; bu alanlar gönderilirse 422 döner.
"""

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _normalize_email(value: str) -> str:
    email = value.strip().lower()

    if len(email) > 254 or not EMAIL_PATTERN.match(email):
        raise ValueError("Geçerli bir e-posta adresi giriniz.")

    return email


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)

    full_name: str = Field(min_length=2, max_length=100)
    email: str
    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str) -> str:
        value = " ".join(value.split())

        if len(value) < 2:
            raise ValueError("Ad soyad en az 2 karakter olmalıdır.")

        return value

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str) -> str:
        return _normalize_email(value)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str) -> str:
        return _normalize_email(value)


class UserResponse(BaseModel):
    """Kullanıcıya dönen alanlar. password_hash ve is_admin asla yanıtta yer almaz."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    is_verified: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
