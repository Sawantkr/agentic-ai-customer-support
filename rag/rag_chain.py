from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm


load_dotenv()


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a customer support assistant.

Answer the customer's question using ONLY the provided knowledge base.

If the answer is not available in the knowledge base, say that you
do not have enough information and ask the customer for more details.

Do not invent policies, instructions, prices, or facts.

Knowledge Base:
{context}
""",
        ),
        ("human", "{question}"),
    ]
)


def rag_answer(question: str) -> str:
    from rag.vector_store import get_vector_store

    vector_store = get_vector_store()

    documents = vector_store.similarity_search(
        question,
        k=2,
    )

    context = "\n\n".join(
        document.page_content for document in documents
    )

    llm = get_llm()

    chain = RAG_PROMPT | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    return response.content