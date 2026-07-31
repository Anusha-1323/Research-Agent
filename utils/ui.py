import streamlit as st


def show_sources(results):

    documents = sorted(
        set(item["document"] for item in results)
    )

    sources = []

    for item in results:

        source = f"{item['document']} (Page {item['page']})"

        if source not in sources:
            sources.append(source)

    return documents, sources