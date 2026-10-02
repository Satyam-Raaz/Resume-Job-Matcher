import requests
import streamlit as st

API = "http://localhost:8000"
st.title("AI Resume Screening & Job Matching")

files = st.file_uploader("Upload resumes", type=["pdf", "docx", "txt"], accept_multiple_files=True)
if files and st.button("Process resumes"):
    for f in files:
        r = requests.post(f"{API}/resumes", files={"file": (f.name, f.getvalue())})
        st.write(f"{f.name} -> ID {r.json().get('id')}" if r.ok else f"{f.name}: {r.text}")

jd = st.text_area("Job description", height=200)
years = st.number_input("Required years of experience", 0.0, 40.0, 0.0)
if st.button("Find best candidates") and jd:
    r = requests.post(f"{API}/match", data={"job_description": jd, "required_years": years})
    if r.ok:
        for m in r.json():
            with st.expander(f"Resume {m['resume_id']} - score {m['score']}"):
                st.write(f"Semantic: {m['semantic']} | Skill overlap: {m['skill_overlap']}")
                st.write("Matched:", ", ".join(m["matched_skills"]) or "-")
                st.write("Missing:", ", ".join(m["missing_skills"]) or "-")
    else:
        st.error(r.text)
