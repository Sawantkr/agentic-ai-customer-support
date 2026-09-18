from pathlib import Path
from collections import Counter
import math
import re

from langchain_core.documents import Document

from rag.loader import load_documents, split_documents


_vector_store = None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())


def _build_vector(document: Document) -> Counter:
    return Counter(_tokenize(document.page_content))


def _cosine_similarity(
    query_vector: Counter,
    document_vector: Counter,
) -> float:
    if not query_vector or not document_vector:
        return 0.0

    common_terms = set(query_vector) & set(document_vector)

    dot_product = sum(
        query_vector[term] * document_vector[term]
        for term in common_terms
    )

    query_magnitude = math.sqrt(
        sum(value * value for value in query_vector.values())
    )

    document_magnitude = math.sqrt(
        sum(value * value for value in document_vector.values())
    )

    if query_magnitude == 0 or document_magnitude == 0:
        return 0.0

    return dot_product / (query_magnitude * document_magnitude)


class LightweightVectorStore:
    def __init__(self, documents: list[Document]):
        self.documents = documents
        self.vectors = [_build_vector(document) for document in documents]

    def similarity_search(
        self,
        query: str,
        k: int = 2,
    ) -> list[Document]:
        query_vector = Counter(_tokenize(query))

        scored_documents = []

        for document, document_vector in zip(
            self.documents,
            self.vectors,
        ):
            score = _cosine_similarity(
                query_vector,
                document_vector,
            )

            scored_documents.append((score, document))

        scored_documents.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            document
            for score, document in scored_documents[:k]
        ]


def build_vector_store():
    global _vector_store

    documents = load_documents()
    chunks = split_documents(documents)

    _vector_store = LightweightVectorStore(chunks)

    return _vector_store


def get_vector_store():
    global _vector_store

    if _vector_store is None:
        _vector_store = build_vector_store()

    return _vector_store