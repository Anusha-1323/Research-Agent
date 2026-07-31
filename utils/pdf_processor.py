import io

from utils.pdf_loader import load_pdf
from utils.chunking import create_chunks
from utils.embeddings import create_embeddings
from utils.vector_store import VectorStore


def process_documents(uploaded_files):

    all_chunks = []

    for uploaded_file in uploaded_files:

        pdf = io.BytesIO(uploaded_file.getvalue())

        pages = load_pdf(pdf)

        chunks = create_chunks(pages)

        for chunk in chunks:
            chunk["document"] = uploaded_file.name

        all_chunks.extend(chunks)

    embeddings = create_embeddings(all_chunks)

    store = VectorStore()
    store.build_index(embeddings, all_chunks)

    return store, all_chunks