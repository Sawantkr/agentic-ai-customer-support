from rag.rag_chain import rag_answer


def knowledge_base_support(state):
    customer_message = state["customer_message"]

    response = rag_answer(customer_message)

    return {
        "response": response,
        "resolution_status": "resolved",
        "escalation_required": False,
    }