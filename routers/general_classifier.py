from graph.state import SupportState


GENERAL_KEYWORDS = {
    "pricing_question": (
        "pricing",
        "price",
        "cost",
        "plans",
        "plan",
        "subscription plans",
        "subscription price",
        "how much",
    ),

    "product_question": (
        "what is sawantflix",
        "what is sawantflix?",
        "what is this platform",
        "what is this product",
        "what does sawantflix do",
        "what does sawantflix offer",
        "what does the product do",
        "features",
        "feature",
        "documentation",
        "how does it work",
        "how does sawantflix work",
        "product information",
        "about sawantflix",
        "tell me about sawantflix",
    ),

    "other_general": (),
}


def classify_general_issue(state: SupportState) -> dict:

    message = state["processed_message"].lower().strip()

    for general_issue, keywords in GENERAL_KEYWORDS.items():

        if any(keyword in message for keyword in keywords):
            return {
                "general_issue": general_issue
            }

    return {
        "general_issue": "other_general"
    }