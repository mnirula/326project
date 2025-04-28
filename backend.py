"""
==============================
INSTALLATION & SETUP (REQUIREMENTS)
==============================
This project requires the following to be installed in your environment:


    Python 3.10+ recommended
    FastAPI - for building the backend API
    Uvicorn - to run the FastAPI app
    spaCy - for natural language processing
    pdfminer.six - for extracting text from PDFs
    python-docx - for extracting text from DOCX files


Install all required packages with:
    pip install fastapi uvicorn spacy pdfminer.six python-docx


You must also download the spaCy language model:
    python -m spacy download en_core_web_sm
"""


"""
==============================
HOW TO RUN
==============================
1. Create and activate a virtual environment:
    python -m venv venv
    venv\Scripts\activate     # (on Windows)


2. Install all dependencies (see above)


3. Run the FastAPI backend with:
    python -m uvicorn "name of python file":app --reload


4. Open the following address in your browser to test:
    http://127.0.0.1:8000/docs


This will open the Swagger UI to test all backend endpoints without needing a frontend.
"""




from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import io
import os
import spacy
from docx import Document
from pdfminer.high_level import extract_text


# Initialize FastAPI app and load spaCy NLP model
app = FastAPI()
nlp = spacy.load("en_core_web_sm")




# ---------- UTILITIES ----------


def extract_resume_text(file: UploadFile) -> str:
    """
    Extracts raw text from an uploaded resume file.


    Supported file types:
    - PDF: Uses pdfminer.six for parsing
    - DOCX: Uses python-docx to read paragraph text


    Returns:
        A plain string of the full resume text.
    """
    filename = file.filename
    content = file.file.read()


    if filename.endswith(".pdf"):
        with open("temp.pdf", "wb") as f:
            f.write(content)
        text = extract_text("temp.pdf")
        os.remove("temp.pdf")
        return text


    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs])


    else:
        return "Unsupported file type."




def get_keywords(text: str) -> set:
    """
    Uses spaCy to extract important keywords from a given block of text.


    It filters:
    - stopwords
    - non-alphabetic tokens
    - short words (length < 3)


    Returns:
        A set of cleaned, lemmatized keywords.
    """
    doc = nlp(text)
    return set(
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and token.is_alpha and len(token.text) > 2
    )




def check_ats_sections(text: str) -> dict:
    """
    Simulates an ATS (Applicant Tracking System) check by scanning for
    the presence of essential resume sections.


    Sections checked:
    - experience
    - education
    - skills
    - projects


    Returns:
        Dictionary containing:
        - readability flag
        - section match score (0–100)
        - feedback string listing any missing sections
    """
    required_sections = ["experience", "education", "skills", "projects"]
    text_lower = text.lower()
    found = [section for section in required_sections if section in text_lower]
    score = (len(found) / len(required_sections)) * 100
    missing = set(required_sections) - set(found)
    feedback = f"Missing sections: {', '.join(missing)}" if missing else "All required sections are present."


    return {
        "readable": True,
        "section_score": score,
        "feedback": feedback
    }


# ---------- MODELS ----------


class ResumeJobInput(BaseModel):
    """
    Request model used in both /analyze and /ats_check endpoints.


    Fields:
        resume_text: The full text of the user's resume (already extracted).
        job_description: The full job posting text.
    """
    resume_text: str
    job_description: str


# ---------- ENDPOINTS ----------


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Uploads a resume file and extracts its raw text.


    Supported file types:
    - PDF
    - DOCX


    Returns:
        JSON with 'resume_text' field containing extracted text.
    """
    text = extract_resume_text(file)
    return {"resume_text": text}




@app.post("/analyze")
async def analyze(data: ResumeJobInput):
    """
    Compares a resume with a job description to calculate a match score.


    Method:
    - Extracts keywords from both texts using spaCy
    - Calculates overlap between the sets
    - Returns missing job keywords from the resume


    Returns:
        - match_score: % of job keywords present in resume
        - missing_keywords: List of keywords missing from the resume
    """
    resume_keywords = get_keywords(data.resume_text)
    job_description = data.job_description
    job_keywords = get_keywords(job_description)


    missing_keywords = list(job_keywords - resume_keywords)
    match_score = 100 * (len(job_keywords & resume_keywords) / len(job_keywords)) if job_keywords else 0


    return {
        "match_score": round(match_score, 2),
        "missing_keywords": missing_keywords
    }




@app.post("/ats_check")
async def ats_check(data: ResumeJobInput):
    """
    Performs a basic ATS scan by checking for the presence of key resume sections.


    Sections checked:
    - experience
    - education
    - skills
    - projects


    Returns:
        - readable: Always true (assumes text was parseable)
        - section_score: % of required sections found
        - feedback: Missing sections, or all present
    """
    return check_ats_sections(data.resume_text)