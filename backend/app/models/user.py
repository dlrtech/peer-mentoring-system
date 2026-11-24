from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    is_verified = Column(
        Boolean, default=False, server_default="false", nullable=False
    )

    is_admin = Column(
        Boolean, default=False, server_default="false", nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    mentor_profile = relationship(
        "MentorProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )