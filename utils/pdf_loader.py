import fitz

def load_pdf(uploaded_file):
    uploaded_file.seek(0)  # Reset file pointer

    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    pages = []

    for page_num, page in enumerate(pdf, start=1):
        text = page.get_text()

        if text.strip():
            pages.append({
                "page": page_num,
                "text": text
            })

    pdf.close()
import fitz  # PyMuPDF


def load_pdf(uploaded_file):
    """
    Extract text from a PDF while preserving page numbers.

    Returns:
        pages (list): List of dictionaries with page number and text.
    """

    pages = []

    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    for page_num, page in enumerate(pdf, start=1):

        text = page.get_text()

        if text.strip():

            pages.append(
                {
                    "page": page_num,
                    "text": text
                }
            )

    pdf.close()

    return pages