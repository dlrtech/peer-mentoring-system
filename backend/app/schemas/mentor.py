from pydantic import BaseModel, ConfigDict, Field

from app.schemas.course import CourseSummary


class MentorProfileCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    bio: str = Field(min_length=1, max_length=500)
    department: str = Field(min_length=2, max_length=100)


class MentorProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    bio: str
    department: str
    courses: list[CourseSummary] = Field(default_factory=list)


class MentorCourseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    course_id: int = Field(gt=0, strict=True)


class MentorCourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mentor_id: int
    course_id: int