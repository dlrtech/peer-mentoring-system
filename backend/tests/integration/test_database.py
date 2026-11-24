from sqlalchemy import inspect, select, text

from app.database import engine, SessionLocal
from app.models import Course
from scripts.seed_courses import COURSES


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_database_encoding():
    with engine.connect() as connection:
        result = connection.execute(
            text("SHOW server_encoding")
        )

        assert result.scalar() == "UTF8"


def test_database_tables():
    inspector = inspect(engine)

    expected_tables = {
        "users",
        "mentor_profiles",
        "courses",
        "mentor_courses",
        "alembic_version"
    }

    actual_tables = set(inspector.get_table_names())

    assert expected_tables.issubset(actual_tables)


def test_seeded_courses():
    with SessionLocal() as db:
        actual_courses = set(
            db.execute(
                select(Course.code, Course.name)
            ).all()
        )

        assert set(COURSES).issubset(actual_courses)