"""422 yanıtlarında parola geri dönmez (F3-03; PR #7 review bulgusu).

Doğrulama, DB'ye gitmeden önce Pydantic'te başarısız olur; gerçek DB gerekmez.
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_short_password_is_not_echoed():
    password = "kisa1"

    response = client.post(
        "/auth/register",
        json={"full_name": "Ayşe Yılmaz", "email": "ayse@ornek.edu.tr", "password": password},
    )

    assert response.status_code == 422
    assert password not in response.text


def test_login_too_long_password_is_not_echoed():
    password = "GizliParola" * 12  # 132 karakter, sınır 128

    response = client.post("/auth/login", json={"email": "ayse@ornek.edu.tr", "password": password})

    assert response.status_code == 422
    assert password not in response.text


def test_validation_error_keeps_field_location_and_message():
    response = client.post(
        "/auth/register",
        json={"full_name": "Ayşe Yılmaz", "email": "ayse@ornek.edu.tr", "password": "kisa1"},
    )

    error = response.json()["detail"][0]

    assert error["loc"] == ["body", "password"]
    assert error["msg"]
    assert "input" not in error
    assert "ctx" not in error
