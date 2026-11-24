from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)

    code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    name = Column(
        String(150),
        nullable=False,
        index=True
    )

    description = Column(Text, nullable=True)

    mentor_courses = relationship(
        "MentorCourse",
        back_populates="course",
        cascade="all, delete-orphan"
    )