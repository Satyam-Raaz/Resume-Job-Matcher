import uuid

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.matching.scorer import hybrid_score
from app.matching.vector_store import VectorStore
from app.models.schemas import MatchResult, ParsedResume
from app.parsing.extractor import extract_text
from app.parsing.structurer import extract_skills, extract_years
from app.utils.anonymize import anonymize

app = FastAPI(title="AI Resume Screening & Job Matching")
store = VectorStore()
resumes: dict[str, ParsedResume] = {}


@app.post("/resumes", response_model=ParsedResume)
async def upload_resume(file: UploadFile = File(...)):
    from app.matching.embedder import embed
    try:
        text = extract_text(file.filename, await file.read())
    except ValueError as e:
        raise HTTPException(400, str(e))
    text = anonymize(text)
    rid = uuid.uuid4().hex[:8]
    parsed = ParsedResume(
        id=rid,
        text=text,
        skills=extract_skills(text),
        years_experience=extract_years(text),
    )
    resumes[rid] = parsed
    store.add(rid, embed([text])[0])
    return parsed


@app.post("/match", response_model=list[MatchResult])
async def match(job_description: str = Form(...), required_years: float = Form(0), top_k: int = Form(10)):
    from app.matching.embedder import embed
    job_skills = extract_skills(job_description)
    hits = store.search(embed([job_description])[0], k=top_k)
    results = [
        hybrid_score(rid, sim, resumes[rid].skills, job_skills,
                     resumes[rid].years_experience, required_years)
        for rid, sim in hits
    ]
    return sorted(results, key=lambda r: r.score, reverse=True)
