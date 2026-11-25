"""GET /mentors/search testleri (UC-3; T04, F3-02, T18 kısmi).

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
from app.models import Course, MentorCourse, MentorProfile, User
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
def data(session_factory):
    """Ayşe: doğrulanmış mentor (Matematik I, Matematik II, İşletim Sistemleri).
    Mehmet: doğrulanmış, mentor değil. Can: doğrulanmamış mentor (Matematik I)."""
    db = session_factory()
    mat1 = Course(code="MAT101", name="Matematik I")
    mat2 = Course(code="MAT102", name="Matematik II")
    os_ = Course(code="BIL301", name="İşletim Sistemleri")
    ayse = User(full_name="Ayşe Test", email="ayse@example.com", password_hash="x", is_verified=True)
    mehmet = User(full_name="Mehmet Test", email="mehmet@example.com", password_hash="x", is_verified=True)
    can = User(full_name="Can Test", email="can@example.com", password_hash="x", is_verified=False)
    db.add_all([mat1, mat2, os_, ayse, mehmet, can])
    db.flush()

    ayse_profile = MentorProfile(user_id=ayse.id, bio="Matematik dersi verebilirim.", department="Yazılım Mühendisliği")
    can_profile = MentorProfile(user_id=can.id, bio="Ben de veririm.", department="Yazılım Mühendisliği")
    db.add_all([ayse_profile, can_profile])
    db.flush()

    db.add_all([
        MentorCourse(mentor_id=ayse_profile.id, course_id=mat1.id),
        MentorCourse(mentor_id=ayse_profile.id, course_id=mat2.id),
        MentorCourse(mentor_id=ayse_profile.id, course_id=os_.id),
        MentorCourse(mentor_id=can_profile.id, course_id=mat1.id),
    ])
    db.commit()
    ids = {"ayse": ayse.id, "mehmet": mehmet.id, "can": can.id, "ayse_profile": ayse_profile.id}
    db.close()
    return ids


def search(client, user_id, course_name):
    headers = {"Authorization": f"Bearer {create_access_token(user_id)}"} if user_id else {}
    return client.get("/mentors/search", params={"course_name": course_name}, headers=headers)


def test_search_without_token_returns_401(client, data):
    assert search(client, None, "matematik").status_code == 401


def test_unverified_user_gets_403(client, data):
    assert search(client, data["can"], "matematik").status_code == 403


@pytest.mark.parametrize("course_name", ["", "   ", "x" * 101])
def test_invalid_course_name_returns_422(client, data, course_name):
    assert search(client, data["mehmet"], course_name).status_code == 422


def test_no_match_returns_empty_list(client, data):
    response = search(client, data["mehmet"], "olmayanders")
    assert response.status_code == 200
    assert response.json() == []


def test_match_returns_mentor_once_with_contract_fields(client, data):
    response = search(client, data["mehmet"], "matematik")
    assert response.status_code == 200
    body = response.json()
    # İki dersi eşleşse de Ayşe bir kez döner; doğrulanmamış Can hiç dönmez.
    assert len(body) == 1
    result = body[0]
    assert set(result) == {"mentor_id", "full_name", "department", "bio", "courses"}
    assert result["mentor_id"] == data["ayse_profile"]
    assert result["full_name"] == "Ayşe Test"
    assert {c["code"] for c in result["courses"]} == {"MAT101", "MAT102", "BIL301"}
    assert set(result["courses"][0]) == {"id", "code", "name"}


def test_own_profile_is_excluded(client, data):
    response = search(client, data["ayse"], "matematik")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("course_name", ["MATEMAT", "sistemleri", "SISTEMLERI", "SİSTEMLERİ", "işletim", "İŞLETİM"])
def test_case_insensitive_including_turkish_i(client, data, course_name):
    body = search(client, data["mehmet"], course_name).json()
    assert [r["full_name"] for r in body] == ["Ayşe Test"]


@pytest.mark.parametrize("course_name", ["%", "_"])
def test_like_wildcards_are_literal(client, data, course_name):
    assert search(client, data["mehmet"], course_name).json() == []
