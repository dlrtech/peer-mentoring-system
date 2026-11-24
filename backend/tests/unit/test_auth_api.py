"""POST /auth/register ve POST /auth/login testleri (T01, F3-03).

Gerçek PostgreSQL gerekmez: get_db bağımlılığı bellek içi SQLite ile değiştirilir.
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security.password import verify_password
from app.security.token import decode_access_token

PASSWORD = "GucluParola123"

VALID_USER = {
    "full_name": "Ayşe Yılmaz",
    "email": "ayse@ornek.edu.tr",
    "password": PASSWORD,
}


@pytest.fixture(autouse=True)
def token_settings(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-test-secret-key-0123456789")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")


@pytest.fixture()
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    yield sessionmaker(bind=engine, autoflush=False, autocommit=False)

    engine.dispose()


@pytest.fixture()
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


def register(client, **overrides):
    return client.post("/auth/register", json={**VALID_USER, **overrides})


def login(client, email=VALID_USER["email"], password=PASSWORD):
    return client.post("/auth/login", json={"email": email, "password": password})


# --- Kayıt ---


def test_register_creates_unverified_user(client, session_factory):
    response = register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["full_name"] == "Ayşe Yılmaz"
    assert body["email"] == "ayse@ornek.edu.tr"
    assert body["is_verified"] is False
    assert isinstance(body["id"], int)

    with session_factory() as db:
        user = db.scalar(select(User).where(User.email == "ayse@ornek.edu.tr"))
        assert user.is_verified is False
        assert user.is_admin is False


def test_register_response_has_no_sensitive_fields(client):
    body = register(client).json()

    assert "password" not in body
    assert "password_hash" not in body
    assert "is_admin" not in body
    assert set(body) == {"id", "full_name", "email", "is_verified"}


def test_register_stores_argon2_hash_not_plain_password(client, session_factory):
    register(client)

    with session_factory() as db:
        user = db.scalar(select(User))

    assert user.password_hash != PASSWORD
    assert user.password_hash.startswith("$argon2id$")
    assert verify_password(PASSWORD, user.password_hash)


def test_register_normalizes_email(client):
    response = register(client, email="  Ayse@Ornek.EDU.tr ")

    assert response.status_code == 201
    assert response.json()["email"] == "ayse@ornek.edu.tr"


def test_register_duplicate_email_returns_409(client):
    assert register(client).status_code == 201

    response = register(client)

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}


def test_register_duplicate_email_ignores_case(client):
    register(client)

    response = register(client, email="AYSE@ORNEK.EDU.TR")

    assert response.status_code == 409


@pytest.mark.parametrize(
    "email",
    ["", "ayse", "ayse@", "@ornek.edu.tr", "ayse@ornek", "ay se@ornek.edu.tr", "a" * 250 + "@o.tr"],
)
def test_register_invalid_email_returns_422(client, email):
    response = register(client, email=email)

    assert response.status_code == 422


@pytest.mark.parametrize("password", ["", "kisa123", "x" * 129])
def test_register_invalid_password_length_returns_422(client, password):
    response = register(client, password=password)

    assert response.status_code == 422


@pytest.mark.parametrize("full_name", ["", "A", "   ", "x" * 101])
def test_register_invalid_full_name_returns_422(client, full_name):
    response = register(client, full_name=full_name)

    assert response.status_code == 422


@pytest.mark.parametrize("missing", ["full_name", "email", "password"])
def test_register_missing_field_returns_422(client, missing):
    payload = {k: v for k, v in VALID_USER.items() if k != missing}

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize("field", ["is_verified", "is_admin"])
def test_register_rejects_privileged_fields_from_client(client, session_factory, field):
    response = register(client, **{field: True})

    assert response.status_code == 422

    with session_factory() as db:
        assert db.scalar(select(User)) is None


# --- Giriş ---


def test_login_returns_bearer_token_for_registered_user(client):
    user_id = register(client).json()["id"]

    response = login(client)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert decode_access_token(body["access_token"]) == user_id


def test_login_accepts_email_in_any_case(client):
    register(client)

    response = login(client, email="AYSE@Ornek.edu.tr")

    assert response.status_code == 200


def test_login_works_for_unverified_account(client):
    register(client)

    # Doğrulanmamış hesap giriş yapabilir; 403 yalnız korumalı işlemlerde döner.
    assert login(client).status_code == 200


def test_login_wrong_password_returns_401(client):
    register(client)

    response = login(client, password="YanlisParola999")

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_unknown_email_returns_same_401_as_wrong_password(client):
    register(client)

    wrong_password = login(client, password="YanlisParola999")
    unknown_email = login(client, email="yok@ornek.edu.tr")

    assert unknown_email.status_code == 401
    assert unknown_email.json() == wrong_password.json()


def test_login_response_has_no_password_hash(client):
    register(client)

    body = login(client).json()

    assert set(body) == {"access_token", "token_type"}


@pytest.mark.parametrize("payload", [{}, {"email": "ayse@ornek.edu.tr"}, {"password": PASSWORD}])
def test_login_missing_field_returns_422(client, payload):
    response = client.post("/auth/login", json=payload)

    assert response.status_code == 422


def test_login_invalid_email_format_returns_422(client):
    response = login(client, email="gecersiz")

    assert response.status_code == 422
