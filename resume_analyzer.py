import fitz       # PyMuPDF for PDF parsing
import docx       # python-docx for DOCX parsing
import re
from collections import Counter


# Extract text content from a PDF file
def extract_text_from_pdf(path: str) -> str:
    with fitz.open(path) as doc:
        return "\n".join(page.get_text() for page in doc)


# Extract text content from a DOCX file
def extract_text_from_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


# Auto-detect file type and extract text accordingly
def extract_resume_text(path: str) -> str:
    if path.endswith(".pdf"):
        return extract_text_from_pdf(path)
    elif path.endswith(".docx"):
        return extract_text_from_docx(path)
    else:
        raise ValueError("Unsupported file type. Use .pdf or .docx")


# Extract top keywords with relative weights from the job description
def extract_keywords_simple(text: str, top_n=10) -> dict:
    text = re.sub(r"[^a-zA-Z ]", "", text).lower()  # remove punctuation and lowercase
    words = text.split()
    # Basic stopword list to ignore generic words
    stopwords = set([
        "the", "and", "for", "with", "you", "are", "has", "have", "this", "will",
        "that", "from", "such", "must", "about", "into", "their", "can", "your",
        "our", "not", "but", "all", "they", "who", "job", "role"
    ])
    # Filter words by length and stopwords
    filtered = [w for w in words if len(w) > 2 and w not in stopwords]
    counts = Counter(filtered).most_common(top_n)


    total = sum(count for _, count in counts)
    # Assign weights as percentage of total keyword frequency
    weights = {word: round((count / total) * 100, 2) for word, count in counts}
    return weights


# Check how many weighted keywords appear in resume text
def calculate_compatibility(resume_text: str, keyword_weights: dict) -> dict:
    resume_lower = resume_text.lower()
    score = 0
    found = []
    missing = []


    for keyword, weight in keyword_weights.items():
        if keyword in resume_lower:
            score += weight
            found.append(keyword)
        else:
            missing.append(keyword)


    return {
        "match_score": round(min(score, 100), 2),
        "found_keywords": found,
        "missing_keywords": missing
    }


# Command-line interface for resume and job description input
def main():
    resume_path = input("Enter path to your resume (.pdf or .docx): ").strip()
    job_description = input("Paste the job description in one paragraph:\n").strip()


    print("Analyzing...")
    resume_text = extract_resume_text(resume_path)
    keyword_weights = extract_keywords_simple(job_description, top_n=10)
    result = calculate_compatibility(resume_text, keyword_weights)


    print("\n====== RESULTS ======")
    print(f"Compatibility Score: {result['match_score']}%")
    print(f"Found Keywords: {', '.join(result['found_keywords']) or 'None'}")
    print(f"Missing Keywords: {', '.join(result['missing_keywords']) or 'None'}")
    print(f"Weighted Keywords Used: {keyword_weights}")


if __name__ == "__main__":
    main()





