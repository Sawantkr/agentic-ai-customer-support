from pathlib import Path

from langchain_core.documents import Document
from qdrant_client import QdrantClient, models

from rag.loader import load_documents, split_documents


# =========================
# QDRANT CONFIGURATION
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

QDRANT_PATH = BASE_DIR / "qdrant_storage"
COLLECTION_NAME = "customer_support_knowledge"

# FastEmbed model used by Qdrant for semantic embeddings
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


_qdrant_client = None
_vector_store = None


# =========================
# QDRANT VECTOR STORE
# =========================

class QdrantVectorStore:
    def __init__(self, documents: list[Document]):
        self.documents = documents

        # Local persistent Qdrant database
        self.client = QdrantClient(
            path=str(QDRANT_PATH)
        )

        self._create_collection()
        self._index_documents()

    # -------------------------
    # Create collection
    # -------------------------

    def _create_collection(self):
        if not self.client.collection_exists(COLLECTION_NAME):
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=self.client.get_embedding_size(
                        EMBEDDING_MODEL
                    ),
                    distance=models.Distance.COSINE,
                ),
            )

    # -------------------------
    # Store documents
    # -------------------------

    def _index_documents(self):
        if not self.documents:
            return

        # Avoid rebuilding the collection every time
        collection_info = self.client.get_collection(
            collection_name=COLLECTION_NAME
        )

        existing_points = collection_info.points_count or 0

        if existing_points > 0:
            return

        ids = list(range(len(self.documents)))

        payload = []

        for document in self.documents:
            payload.append(
                {
                    "document": document.page_content,
                    "metadata": document.metadata,
                }
            )

        self.client.upload_collection(
            collection_name=COLLECTION_NAME,
            vectors=[
                models.Document(
                    text=document.page_content,
                    model=EMBEDDING_MODEL,
                )
                for document in self.documents
            ],
            payload=payload,
            ids=ids,
        )

    # -------------------------
    # Semantic similarity search
    # -------------------------

    def similarity_search(
        self,
        query: str,
        k: int = 2,
    ) -> list[Document]:

        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=models.Document(
                text=query,
                model=EMBEDDING_MODEL,
            ),
            limit=k,
            with_payload=True,
        ).points

        documents = []

        for result in results:
            payload = result.payload or {}

            documents.append(
                Document(
                    page_content=payload.get(
                        "document",
                        ""
                    ),
                    metadata=payload.get(
                        "metadata",
                        {}
                    ),
                )
            )

        return documents


# =========================
# BUILD VECTOR STORE
# =========================

def build_vector_store():
    global _vector_store

    documents = load_documents()
    chunks = split_documents(documents)

    _vector_store = QdrantVectorStore(chunks)

    return _vector_store


# =========================
# GET VECTOR STORE
# =========================

def get_vector_store():
    global _vector_store

    if _vector_store is None:
        _vector_store = build_vector_store()

    return _vector_store