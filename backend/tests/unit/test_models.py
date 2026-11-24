from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import configure_mappers

from app.database import Base
from app.models import User, MentorProfile, Course, MentorCourse


def test_required_models():
    expected_tables = {
        "users",
        "mentor_profiles",
        "courses",
        "mentor_courses"
    }

    assert expected_tables.issubset(
        Base.metadata.tables.keys()
    )


def test_model_relationships():
    configure_mappers()

    assert User.mentor_profile.property.uselist is False
    assert MentorProfile.mentor_courses.property.uselist is True
    assert Course.mentor_courses.property.uselist is True


def test_unique_user_email():
    assert User.__table__.c.email.unique is True


def test_unique_mentor_profile():
    assert MentorProfile.__table__.c.user_id.unique is True


def test_unique_course_code():
    assert Course.__table__.c.code.unique is True


def test_course_name_not_unique():
    assert not Course.__table__.c.name.unique


def test_unique_mentor_course():
    constraints = MentorCourse.__table__.constraints

    assert any(
        isinstance(constraint, UniqueConstraint)
        and set(constraint.columns.keys()) == {
            "mentor_id", "course_id"
        }
        for constraint in constraints
    )