"""Mentor arama (UC-3). Sorumlu: Yusuf.

GET /mentors/search?course_name=Matematik
- Ders adında büyük/küçük harf duyarsız kısmi eşleşme (ILIKE).
- Giriş yapan kullanıcının kendi profili ve doğrulanmamış hesaplar sonuçta yer almaz.
- Aynı mentor birden fazla eşleşen ders verse bile bir kez döner.
- Sonuç yoksa [] döner.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.course import Course
from app.models.mentor import MentorProfile
from app.models.mentor_course import MentorCourse
from app.models.user import User
from app.schemas.search import MentorSearchResult, SearchCourse
from app.security.dependencies import get_verified_user

router = APIRouter(prefix="/mentors", tags=["Search"])


def _escape_like(text: str) -> str:
    """Kullanıcının yazdığı % ve _ karakterleri joker gibi davranmasın."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@router.get(
    "/search",
    response_model=list[MentorSearchResult],
    status_code=status.HTTP_200_OK,
)
def search_mentors(
    course_name: Annotated[str, Query(min_length=1, max_length=100)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user),
):
    query_text = course_name.strip()
    if not query_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ders adı boş olamaz.",
        )

    pattern = f"%{_escape_like(query_text)}%"

    # .any() alt sorgu (EXISTS) üretir; JOIN'den farklı olarak aynı mentoru tekrar döndürmez.
    statement = (
        select(MentorProfile)
        .join(MentorProfile.user)
        .where(
            User.is_verified.is_(True),
            MentorProfile.user_id != current_user.id,
            MentorProfile.mentor_courses.any(
                MentorCourse.course.has(Course.name.ilike(pattern, escape="\\"))
            ),
        )
        .options(
            selectinload(MentorProfile.user),
            selectinload(MentorProfile.mentor_courses).selectinload(MentorCourse.course),
        )
        .order_by(MentorProfile.id)
    )

    profiles = db.scalars(statement).all()

    return [
        MentorSearchResult(
            mentor_id=profile.id,
            full_name=profile.user.full_name,
            department=profile.department,
            bio=profile.bio,
            courses=[
                SearchCourse.model_validate(item.course)
                for item in sorted(profile.mentor_courses, key=lambda item: item.course.code)
            ],
        )
        for profile in profiles
    ]
