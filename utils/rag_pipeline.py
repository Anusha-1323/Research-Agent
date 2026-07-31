from sentence_transformers import SentenceTransformer
from utils.llm import generate_answer

model = SentenceTransformer("all-MiniLM-L6-v2")


def ask_question(question, vector_store):

    query_embedding = model.encode(
        [question],
        convert_to_numpy=True
    )

    results = vector_store.search(query_embedding)

    print("=" * 70)
    print("Retrieved Chunks")

    for i, item in enumerate(results):
        print(f"\nChunk {i+1}")
        print("Page:", item["page"])
        print("Content:")
        print(item["content"][:300])
        print("-" * 70)

    context = ""
    pages = []

    for item in results:
        context += item["content"] + "\n\n"
        pages.append(item["page"])

    print("=" * 70)
    print("Final Context Sent to LLM")
    print(context)
    print("=" * 70)
    context = ""

    pages = []

    for item in results:

        context += item["content"] + "\n\n"

        pages.append(item["page"])

    answer = generate_answer(
        context=context,
        question=question
    )

    return answer, sorted(set(pages)), results