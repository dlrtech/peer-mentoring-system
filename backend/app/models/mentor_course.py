from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class MentorCourse(Base):
    __tablename__ = "mentor_courses"

    __table_args__ = (
        UniqueConstraint(
            "mentor_id",
            "course_id",
            name="uq_mentor_course"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    mentor_id = Column(
        Integer,
        ForeignKey("mentor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    mentor = relationship(
        "MentorProfile",
        back_populates="mentor_courses"
    )

    course = relationship(
        "Course",
        back_populates="mentor_courses"
    )