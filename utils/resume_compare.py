from utils.ats import analyze_resume
from utils.pdf_loader import load_pdf
from utils.chunking import create_chunks
import io


def compare_resumes(resume_files):

    comparison = []

    for resume in resume_files:

        pdf = io.BytesIO(resume.getvalue())

        pages = load_pdf(pdf)

        chunks = create_chunks(pages)

        full_resume = "\n\n".join(
            chunk["content"]
            for chunk in chunks
        )

        report = analyze_resume(full_resume)

        comparison.append(
            {
                "Resume": resume.name,
                "Report": report
            }
        )

    return comparison