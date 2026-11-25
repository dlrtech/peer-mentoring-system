from pydantic import BaseModel, ConfigDict


class SearchCourse(BaseModel):
    """Arama sonucunda mentorun verdiği bir ders (api-contract.md §5: id + code + name)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class MentorSearchResult(BaseModel):
    """GET /mentors/search yanıtındaki tek mentor. Yalnız sözleşmedeki alanlar döner."""

    mentor_id: int
    full_name: str
    department: str
    bio: str
    courses: list[SearchCourse]
