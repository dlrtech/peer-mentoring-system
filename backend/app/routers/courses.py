from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.course import CourseResponse
from app.services.course import list_courses
from app.security.dependencies import get_verified_user


router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)


@router.get(
    "",
    response_model=list[CourseResponse],
    status_code=status.HTTP_200_OK
)
def get_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    return list_courses(db)