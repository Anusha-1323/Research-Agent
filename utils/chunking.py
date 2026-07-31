from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunks(pages):
    """
    Split extracted PDF pages into overlapping chunks.

    Args:
        pages: List of dictionaries from pdf_loader.py

    Returns:
        List of chunk dictionaries
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = []

    for page in pages:

        texts = splitter.split_text(page["text"])

        for text in texts:

            chunks.append(
                {
                    "page": page["page"],
                    "content": text
                }
            )
            print("=" * 60)
            print("Total Chunks:", len(chunks))

            for i, chunk in enumerate(chunks):
                print(f"\nChunk {i}")
                print("Page:", chunk["page"])
                print(chunk["content"][:150])

    return chunks