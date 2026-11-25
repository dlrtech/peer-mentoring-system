"""Mentör Profili ve Ders İlişkileri API testleri (F3-01: 409, 404, 422 senaryoları).

Gerçek PostgreSQL gerekmez: get_db bağımlılığı bellek içi SQLite ile değiştirilir.
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Course, User
from app.security.token import create_access_token


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


@pytest.fixture()
def auth_headers(session_factory):
    db = session_factory()
    user = User(
        full_name="Test Mentor",
        email="mentor@university.edu.tr",
        password_hash="hashed-password",
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    db.close()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_courses(session_factory):
    db = session_factory()
    c1 = Course(code="BYM308", name="Yapay Zekaya Giriş", description=None)
    c2 = Course(code="BYM447", name="Makine Öğrenmesi", description="Temel ML")
    db.add_all([c1, c2])
    db.commit()
    db.refresh(c1)
    db.refresh(c2)
    ids = (c1.id, c2.id)
    db.close()
    return ids


def test_list_courses_returns_catalog(client, auth_headers, sample_courses):
    res = client.get("/courses", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert {item["code"] for item in data} == {"BYM308", "BYM447"}

def test_create_mentor_profile_success(client, auth_headers):
    res = client.post(
        "/mentors/profile",
        json={"bio": "Algoritmalar ve veri yapıları konusunda yardımcı olabilirim.", "department": "Bilgisayar Mühendisliği"},
        headers=auth_headers,
    )
    assert res.status_code == 201
    body = res.json()
    assert body["department"] == "Bilgisayar Mühendisliği"
    assert body["courses"] == []


def test_create_duplicate_mentor_profile_returns_409(client, auth_headers):
    payload = {"bio": "İlk profil", "department": "Yazılım Mühendisliği"}
    first = client.post("/mentors/profile", json=payload, headers=auth_headers)
    assert first.status_code == 201

    second = client.post("/mentors/profile", json=payload, headers=auth_headers)
    assert second.status_code == 409


def test_get_mentor_profile_when_missing_returns_404(client, auth_headers):
    res = client.get("/mentors/profile", headers=auth_headers)
    assert res.status_code == 404


def test_create_mentor_profile_invalid_payload_returns_422(client, auth_headers):
    # department minimum 2 karakter olmalı ve extra alan yasak
    res = client.post(
        "/mentors/profile",
        json={"bio": "", "department": "A", "extra_field": "yasak"},
        headers=auth_headers,
    )
    assert res.status_code == 422


def test_add_course_without_profile_returns_404(client, auth_headers, sample_courses):
    c1_id, _ = sample_courses
    res = client.post("/mentors/courses", json={"course_id": c1_id}, headers=auth_headers)
    assert res.status_code == 404


def test_add_nonexistent_course_returns_404(client, auth_headers):
    client.post(
        "/mentors/profile",
        json={"bio": "Mentör biyografisi", "department": "Bilgisayar Mühendisliği"},
        headers=auth_headers,
    )
    res = client.post("/mentors/courses", json={"course_id": 99999}, headers=auth_headers)
    assert res.status_code == 404


def test_add_course_success_and_duplicate_returns_409(client, auth_headers, sample_courses):
    c1_id, c2_id = sample_courses
    client.post(
        "/mentors/profile",
        json={"bio": "Mentör biyografisi", "department": "Bilgisayar Mühendisliği"},
        headers=auth_headers,
    )

    first = client.post("/mentors/courses", json={"course_id": c1_id}, headers=auth_headers)
    assert first.status_code == 201
    assert first.json()["course_id"] == c1_id

    second = client.post("/mentors/courses", json={"course_id": c2_id}, headers=auth_headers)
    assert second.status_code == 201

    # Aynı course_id tekrar eklendiğinde 409 Conflict dönmeli
    duplicate = client.post("/mentors/courses", json={"course_id": c1_id}, headers=auth_headers)
    assert duplicate.status_code == 409

    # Profil yanıtında dersler kod sırasıyla ve id/code/name alanlarıyla dönmeli
    profile_res = client.get("/mentors/profile", headers=auth_headers)
    assert profile_res.status_code == 200
    courses = profile_res.json()["courses"]
    assert [c["code"] for c in courses] == ["BYM308", "BYM447"]


def test_add_course_invalid_type_returns_422(client, auth_headers):
    res = client.post("/mentors/courses", json={"course_id": "BYM308"}, headers=auth_headers)
    assert res.status_code == 422


def test_mentor_endpoints_require_auth(client):
    res = client.get("/mentors/profile")
    assert res.status_code in (401, 403)