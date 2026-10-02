# AI Resume Screening & Job Matching

An AI-powered system that parses resumes, compares them with a job description, and ranks candidates using a hybrid score (semantic similarity + skill match + experience). Built with Python, FastAPI, FastEmbed, FAISS, and Streamlit.

> **Human in the loop:** this tool ranks and assists. Final hiring decisions should always be made by a person.

---

## Features

- Upload resumes in **PDF, DOCX, or TXT**
- Text extraction with `pdfplumber` (PyMuPDF fallback for tricky PDFs)
- **Anonymization** of emails and phone numbers (privacy and bias reduction)
- Skill and years-of-experience extraction
- **Semantic matching** using sentence embeddings (`all-MiniLM-L6-v2`) and FAISS
- **Hybrid scoring** with matched and missing skills for each candidate
- REST API (FastAPI) and recruiter UI (Streamlit)

---

## How it works

```
Resume upload -> Text extraction -> Anonymize -> Skills/years parsing -> Embedding -> FAISS index
                                                                                         |
Job description -> Skills parsing -> Embedding -> Similarity search -> Hybrid score -> Ranked list
```

### Scoring formula

```
score = 0.6 x semantic      (meaning similarity between resume and job)
      + 0.3 x skill_overlap (share of required skills the resume has)
      + 0.1 x experience    (years vs. required years, capped at 1.0)
```

Weights can be changed in `app/config.py`.

---

## Project structure

```
resume-matcher/
├── app/
│   ├── main.py                 # FastAPI endpoints (/resumes, /match)
│   ├── config.py               # Settings and scoring weights
│   ├── parsing/
│   │   ├── extractor.py        # PDF/DOCX/TXT -> text
│   │   └── structurer.py       # Skills and years of experience
│   ├── matching/
│   │   ├── embedder.py         # FastEmbed embeddings
│   │   ├── vector_store.py     # FAISS index
│   │   └── scorer.py           # Hybrid scoring
│   ├── models/schemas.py       # Pydantic models
│   └── utils/anonymize.py      # Removes email/phone
├── ui/streamlit_app.py         # Recruiter UI
├── tests/test_scorer.py
├── data/resumes/ , data/jobs/
├── models_cache/               # Downloaded embedding model (created automatically)
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

---

## Requirements

- Python 3.10 or newer (3.11 recommended)
- Internet access for the first run (to download the ~90 MB embedding model once)

---

## Installation

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux

# 2. Install dependencies
pip install --default-timeout=300 --retries 10 -r requirements.txt

# 3. Create your settings file
copy .env.example .env           # Windows
# cp .env.example .env           # macOS / Linux
```

### Recommended `requirements.txt`

```
fastapi>=0.110
uvicorn[standard]>=0.29
python-multipart>=0.0.9
pydantic>=2.6
pydantic-settings>=2.2
python-dotenv>=1.0
pdfplumber>=0.11
pymupdf>=1.24
python-docx>=1.1
fastembed>=0.3
faiss-cpu>=1.8
numpy>=1.26
rank-bm25>=0.2.2
streamlit>=1.33
requests>=2.31
pytest>=8.0
```

---

## Running the project

Always run commands from the **project root** (the `resume-matcher` folder), not from inside `app/`.

### Option A: Streamlit only (simplest)

If you use the all-in-one version of `ui/streamlit_app.py` (calls the matching code directly), you need only one command:

```bash
streamlit run ui/streamlit_app.py
```

Open http://localhost:8501.

### Option B: API + UI (two terminals)

**Terminal 1: backend**

```bash
uvicorn app.main:app --reload --reload-dir app
```

Wait for `Application startup complete`, then open http://127.0.0.1:8000/docs.

**Terminal 2: UI**

```bash
streamlit run ui/streamlit_app.py
```

Keep both terminals open. If the backend is not running, the UI shows a `WinError 10061` connection error.

### Run the tests

```bash
pytest
```

---

## API endpoints

| Method | Endpoint     | Description                                                                             |
| ------ | ------------ | --------------------------------------------------------------------------------------- |
| POST   | `/resumes` | Upload a resume file. Returns the parsed ID, text, skills, years.                       |
| POST   | `/match`   | Form fields:`job_description`, `required_years`, `top_k`. Returns ranked matches. |

Example response item from `/match`:

```json
{
  "resume_id": "19a0b973",
  "score": 0.67,
  "semantic": 0.62,
  "skill_overlap": 0.67,
  "matched_skills": ["java", "spring boot"],
  "missing_skills": ["docker"]
}
```

---

## Offline model setup (if downloads fail)

The embedding model downloads from Hugging Face on first use. On some networks the download stalls at 4/5 files. Fixes:

1. Remove the Xet downloader and disable it:

   ```bash
   pip uninstall -y hf_xet
   ```

   Set these **before any other import** (top of `app/matching/embedder.py`):
   ```python
   import os
   os.environ["HF_HUB_DISABLE_XET"] = "1"
   os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "600"
   ```
2. Store the model in a fixed folder so it is not downloaded again:

   ```python
   TextEmbedding(
       model_name="sentence-transformers/all-MiniLM-L6-v2",
       cache_dir=r"D:\path\to\resume-matcher\models_cache",
   )
   ```
3. If it still fails, try a mobile hotspot, turn off VPN or antivirus web shield, or download the files manually from https://huggingface.co/Qdrant/all-MiniLM-L6-v2-onnx/tree/main and use `specific_model_path`.

Once downloaded, the model works offline.

---

## Troubleshooting

| Problem                                        | Fix                                                                                                            |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `ModuleNotFoundError: No module named 'app'` | Run from the project root using`uvicorn app.main:app`, not `python main.py` inside `app/`.               |
| `WinError 10061` (connection refused)        | The backend is not running. Start it first and confirm`/docs` opens.                                         |
| `c10.dll` / `WinError 1114`                | PyTorch DLL problem. This project uses FastEmbed instead, so uninstall`torch` and `sentence-transformers`. |
| pip`Read timed out`                          | Use`--default-timeout=300 --retries 10` and re-run. Already-installed packages are skipped.                  |
| `FontBBox` warnings from PDFs                | Harmless. Silenced with`logging.getLogger("pdfminer").setLevel(logging.ERROR)`.                              |
| Server prints only the reloader line and hangs | Run`uvicorn app.main:app --reload --reload-dir app`, and load the embedder lazily inside the endpoints.      |
| Empty text from a PDF                          | The PDF may be a scanned image and needs OCR (Tesseract).                                                      |

---

## Customization

- **Skills list:** add more terms to `SKILLS` in `app/parsing/structurer.py` (for example `spring boot`, `mysql`, `rest api`, `hibernate`, `jpa`, `reactjs`) so they count toward skill overlap.
- **Scoring weights:** edit `w_semantic`, `w_skills`, `w_experience` in `app/config.py`.
- **Experience detection:** currently looks for phrases like "3 years". Add a date-range parser for resumes that list only dates.

---

## Limitations

- The vector store is **in-memory**: data resets when the app restarts. Use pgvector or Qdrant for persistence.
- Skill extraction is keyword-based and depends on the list in `structurer.py`.
- Scanned (image-only) PDFs are not supported without OCR.
- Only contact details are anonymized. Names, gender, age, and photos are not yet removed.

---

## Roadmap

- [ ] LLM-generated match explanations
- [ ] Persistent storage (PostgreSQL + pgvector)
- [ ] OCR for scanned resumes
- [ ] Cross-encoder re-ranking
- [ ] Bias audit and fairness reports
- [ ] Docker Compose deployment

---

## Fairness, privacy, and compliance

Hiring AI is regulated in many regions (for example NYC Local Law 144 and the EU AI Act). Use this project as a decision-support tool: audit results regularly, keep a human reviewer in the loop, protect candidate data, and follow applicable data protection laws such as GDPR and India's DPDP Act.

---

## License

Add your preferred license (for example MIT) here.
