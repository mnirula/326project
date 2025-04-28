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
