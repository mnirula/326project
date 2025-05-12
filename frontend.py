"""
==============================
STREAMLIT FRONTEND SETUP
==============================
This is the frontend UI for the Resume Compatibility Checker project.


REQUIREMENTS:
    - Python 3.10+
    - streamlit
    - requests


Install with:
    pip install streamlit requests


Run the app with:
    python -m streamlit run frontend.py


Once running, open:
    http://localhost:8501


This frontend connects to the backend FastAPI server at:
    http://127.0.0.1:8000


Make sure the backend is running before starting the frontend:
    python -m uvicorn test:app --reload
"""


import os
import streamlit as st
import requests


# URL of the FastAPI backend
API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")




# ================================
# Streamlit UI: Header and Inputs
# ================================
st.title("Resume Compatibility Checker")


"""
Allows the user to upload a resume and paste a job description.
The resume is sent to the backend to extract text.
The text and job description are then analyzed for keyword overlap.
A compatibility score and missing keywords are displayed.
"""


# File uploader for resume (PDF or DOCX)
resume_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])


# Text area to paste the job description
job_description = st.text_area("Paste the job description here")


# ================================
# Analyze Button Logic
# ================================
if st.button("Analyze"):
    """
    When clicked:
    1. Sends resume file to `/upload_resume`
    2. Sends resume text + job description to `/analyze`
    3. Displays match score and missing keywords
    """
    if resume_file and job_description:
        # Step 1: Upload resume and extract text
        files = {"file": (resume_file.name, resume_file, resume_file.type)}
        resume_response = requests.post(f"{API_URL}/upload_resume", files=files)


        if resume_response.status_code == 200:
            resume_text = resume_response.json()["resume_text"]


            # Step 2: Analyze compatibility
            payload = {
                "resume_text": resume_text,
                "job_description": job_description
            }
            analyze_response = requests.post(f"{API_URL}/analyze", json=payload)


            if analyze_response.status_code == 200:
                result = analyze_response.json()


                # Display match score and missing keywords
                st.subheader("Match Score")
                st.metric("Compatibility", f"{result['match_score']}%")
                missing = result["missing_keywords"]
                st.text("Missing Keywords:\n" + (", ".join(missing) if missing else "None!"))
            else:
                st.error("Error analyzing resume.")
        else:
            st.error("Failed to extract text from resume.")
    else:
        st.warning("Please upload a resume and paste a job description.")


