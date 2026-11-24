from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.mentor import MentorProfile
from app.models.course import Course
from app.models.mentor_course import MentorCourse
from app.schemas.mentor import (
    MentorProfileCreate,
    MentorProfileResponse,
    MentorCourseCreate,
)


def find_profile(
    db: Session,
    user_id: int
) -> MentorProfile | None:

    statement = (
        select(MentorProfile)
        .where(MentorProfile.user_id == user_id)
        .options(
            selectinload(MentorProfile.mentor_courses)
            .selectinload(MentorCourse.course)
        )
    )

    return db.scalar(statement)


def profile_response(
    profile: MentorProfile
) -> MentorProfileResponse:

    return MentorProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        bio=profile.bio,
        department=profile.department,
        courses=[
            {
                "id": item.course.id,
                "code": item.course.code,
                "name": item.course.name
            }
            for item in sorted(
                profile.mentor_courses,
                key=lambda item: item.course.code
            )
        ]
    )


def create_profile(
    db: Session,
    user_id: int,
    data: MentorProfileCreate
) -> MentorProfileResponse:

    if find_profile(db, user_id) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mentor profile already exists."
        )

    profile = MentorProfile(
        user_id=user_id,
        bio=data.bio,
        department=data.department
    )

    db.add(profile)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mentor profile could not be created."
        )

    db.refresh(profile)

    return profile_response(profile)


def get_profile(
    db: Session,
    user_id: int
) -> MentorProfileResponse:

    profile = find_profile(db, user_id)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor profile not found."
        )

    return profile_response(profile)


def add_course(
    db: Session,
    user_id: int,
    data: MentorCourseCreate
) -> MentorCourse:

    profile = find_profile(db, user_id)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor profile not found."
        )

    course = db.get(Course, data.course_id)

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found."
        )

    existing = db.scalar(
        select(MentorCourse).where(
            MentorCourse.mentor_id == profile.id,
            MentorCourse.course_id == data.course_id
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Course already added to mentor profile."
        )

    mentor_course = MentorCourse(
        mentor_id=profile.id,
        course_id=data.course_id
    )

    db.add(mentor_course)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Course could not be added."
        )

    db.refresh(mentor_course)

    return mentor_course