from pydantic import BaseModel


class ParsedResume(BaseModel):
    id: str
    text: str
    skills: list[str]
    years_experience: float


class MatchResult(BaseModel):
    resume_id: str
    score: float
    semantic: float
    skill_overlap: float
    matched_skills: list[str]
    missing_skills: list[str]
