import re

# Starter list; replace with a larger taxonomy (e.g. ESCO) or LLM extraction.
SKILLS = [
    "python", "java", "javascript", "typescript", "react", "node.js", "sql",
    "postgresql", "mongodb", "docker", "kubernetes", "aws", "gcp", "azure",
    "machine learning", "deep learning", "nlp", "pytorch", "tensorflow",
    "fastapi", "django", "flask", "git", "linux", "pandas", "numpy",
]

YEARS = re.compile(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)", re.I)


def extract_skills(text: str) -> list[str]:
    low = text.lower()
    return sorted({s for s in SKILLS if re.search(rf"\b{re.escape(s)}\b", low)})


def extract_years(text: str) -> float:
    vals = [float(m) for m in YEARS.findall(text)]
    return max(vals) if vals else 0.0
