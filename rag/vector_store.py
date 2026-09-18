from langchain_core.vectorstores import InMemoryVectorStore

from rag.loader import load_documents, split_documents


_embedding_model = None
_vector_store = None


def get_embeddings():
    global _embedding_model

    if _embedding_model is None:
        from langchain_huggingface import HuggingFaceEmbeddings

        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    return _embedding_model


def build_vector_store():
    global _vector_store

    documents = load_documents()
    chunks = split_documents(documents)

    embeddings = get_embeddings()

    _vector_store = InMemoryVectorStore(embeddings)
    _vector_store.add_documents(chunks)

    return _vector_store


def get_vector_store():
    global _vector_store

    if _vector_store is None:
        _vector_store = build_vector_store()

    return _vector_store