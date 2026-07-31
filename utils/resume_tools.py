import io

from utils.ats import analyze_resume
from utils.pdf_loader import load_pdf
from utils.chunking import create_chunks


def analyze_uploaded_resumes(resume_files):
    """
    Analyze one or more uploaded resumes.
    Returns:
        {
            "resume1.pdf": "...ATS Report...",
            "resume2.pdf": "...ATS Report..."
        }
    """

    reports = {}

    for resume in resume_files:

        pdf = io.BytesIO(resume.getvalue())

        pages = load_pdf(pdf)

        chunks = create_chunks(pages)

        full_resume = "\n\n".join(
            chunk["content"]
            for chunk in chunks
        )

        report = analyze_resume(full_resume)

        reports[resume.name] = report

    return reports