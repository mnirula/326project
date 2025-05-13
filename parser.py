import io
import fitz  # PyMuPDF for PDF parsing
import docx  # python-docx for DOCX parsing
import string
from models import Resume


class ResumeParser:
    def parse(self, file) -> Resume:
        # Determine filename from UploadFile or fallback object
        filename = file.filename if hasattr(file, "filename") else str(file)
        if not filename:
            raise ValueError("Filename not provided for resume file.")
        fname_lower = filename.lower()
        text_content = ""


        if fname_lower.endswith(".pdf"):
            # Handle PDF parsing
            try:
                file_bytes = file.file.read()  # FastAPI UploadFile
            except Exception:
                file_bytes = file.read() if hasattr(file, "read") else None
            if not file_bytes:
                raise ValueError("Failed to read PDF file content.")
            # Load PDF from bytes and extract text from all pages
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_pages = [page.get_text() for page in pdf_doc]
            text_content = "\n".join(text_pages)


        elif fname_lower.endswith(".docx"):
            # Handle DOCX parsing
            try:
                doc = docx.Document(file.file if hasattr(file, "file") else file)
            except Exception as e:
                raise ValueError(f"Failed to read DOCX file: {e}")
            paragraphs = [para.text for para in doc.paragraphs]
            text_content = "\n".join(paragraphs)


        else:
            raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")


        # Split the full text into lines to analyze structure
        lines = text_content.splitlines()


        section_indices = []  # Will store tuples of (section_name, line_index)
        for idx, line in enumerate(lines):
            if not line or not line.strip():
                continue  # Skip blank lines
            # Normalize line for heading comparison
            clean_line = line.strip().strip(string.punctuation).lower()
            if not clean_line:
                continue
            words = clean_line.split()
            # Check for standard section headers using keywords
            if "experience" in clean_line and len(words) <= 3:
                section_indices.append(("experience", idx))
            elif "education" in clean_line and len(words) <= 3:
                section_indices.append(("education", idx))
            elif "skills" in clean_line and len(words) <= 3:
                section_indices.append(("skills", idx))
            elif "project" in clean_line and len(words) <= 3:
                section_indices.append(("projects", idx))  # catch 'project(s)'


        # Remove duplicates (if sections appear more than once) and preserve order
        seen = set()
        unique_sections = []
        for name, idx in section_indices:
            if name not in seen:
                seen.add(name)
                unique_sections.append((name, idx))
        unique_sections.sort(key=lambda x: x[1])  # sort by line number


        # Create a Resume object and fill in detected sections
        resume = Resume()
        for i, (name, start_idx) in enumerate(unique_sections):
            end_idx = len(lines)
            if i < len(unique_sections) - 1:
                end_idx = unique_sections[i + 1][1]
            # Collect content lines between this section and the next
            content_lines = [l for l in lines[start_idx + 1:end_idx] if l.strip()]
            section_text = "\n".join(content_lines).strip()
            # Assign extracted text to the appropriate section in Resume
            if name == "experience":
                resume.experience.content = section_text
            elif name == "education":
                resume.education.content = section_text
            elif name == "skills":
                resume.skills.content = section_text
            elif name == "projects":
                resume.projects.content = section_text


        return resume  # Return the filled Resume object



