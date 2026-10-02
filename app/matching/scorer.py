from app.config import settings
from app.models.schemas import MatchResult


def hybrid_score(
    resume_id: str,
    semantic: float,
    resume_skills: list[str],
    job_skills: list[str],
    resume_years: float,
    required_years: float = 0.0,
) -> MatchResult:
    job_set, res_set = set(job_skills), set(resume_skills)
    matched = sorted(job_set & res_set)
    missing = sorted(job_set - res_set)
    overlap = len(matched) / len(job_set) if job_set else 0.0
    exp = min(resume_years / required_years, 1.0) if required_years else 1.0

    score = (
        settings.w_semantic * max(semantic, 0)
        + settings.w_skills * overlap
        + settings.w_experience * exp
    )
    return MatchResult(
        resume_id=resume_id,
        score=round(score, 4),
        semantic=round(semantic, 4),
        skill_overlap=round(overlap, 4),
        matched_skills=matched,
        missing_skills=missing,
    )
