from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.course import Course


def list_courses(db: Session) -> list[Course]:
    statement = select(Course).order_by(Course.code)

    return list(db.scalars(statement).all())