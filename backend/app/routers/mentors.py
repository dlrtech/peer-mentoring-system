from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.mentor import (
    MentorProfileCreate,
    MentorProfileResponse,
    MentorCourseCreate,
    MentorCourseResponse,
)
from app.services.mentor import (
    create_profile,
    get_profile,
    add_course,
)
from app.security.dependencies import get_verified_user


router = APIRouter(
    prefix="/mentors",
    tags=["Mentors"]
)


@router.post(
    "/profile",
    response_model=MentorProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_mentor_profile(
    data: MentorProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    return create_profile(
        db,
        current_user.id,
        data
    )


@router.get(
    "/profile",
    response_model=MentorProfileResponse,
    status_code=status.HTTP_200_OK
)
def get_mentor_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    return get_profile(
        db,
        current_user.id
    )


@router.post(
    "/courses",
    response_model=MentorCourseResponse,
    status_code=status.HTTP_201_CREATED
)
def add_mentor_course(
    data: MentorCourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    return add_course(
        db,
        current_user.id,
        data
    )