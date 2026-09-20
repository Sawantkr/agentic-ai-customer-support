from graph.state import SupportState


def handle_pricing_question(state: SupportState) -> dict:

    return {
        "response": (
            "Sawantflix offers subscription plans that provide access "
            "to its streaming content. Your active subscription and "
            "payment status can be checked automatically from your "
            "logged-in account."
        ),
        "resolution_status": "resolved",
        "escalation_required": False,
    }


def handle_product_question(state: SupportState) -> dict:

    return {
        "response": (
            "Sawantflix is a streaming platform where users can "
            "browse movies and TV shows, search for content, view "
            "ratings and summaries, and manage their personal watchlist. "
            "Users can also manage their subscription and payment-related "
            "information through their account."
        ),
        "resolution_status": "resolved",
        "escalation_required": False,
    }


def handle_other_general(state: SupportState) -> dict:

    return {
        "response": (
            "We received your general support question. "
            "Please provide more details so I can assist you."
        ),
        "resolution_status": "unresolved",
        "escalation_required": False,
    }