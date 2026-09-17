from graph.state import SupportState


def billing_support(state: SupportState) -> dict:
    return {
        "response": (
            f"Your billing request has been received: "
            f"{state['processed_message']}"
        )
    }


def technical_support(state: SupportState) -> dict:
    return {
        "response": (
            f"Your technical support request has been received: "
            f"{state['processed_message']}"
        )
    }


def account_support(state: SupportState) -> dict:
    return {
        "response": (
            f"Your account support request has been received: "
            f"{state['processed_message']}"
        )
    }


def general_support(state: SupportState) -> dict:
    return {
        "response": (
            f"Your general question has been received: "
            f"{state['processed_message']}"
        )
    }


def fallback_support(state: SupportState) -> dict:
    return {
        "response": (
            "I'm not sure which type of support you need yet. "
            "I can help with billing and payments, technical issues, "
            "account access and passwords, or general product questions. "
            "Please describe your issue in a little more detail."
        ),
        "escalation_required": False,
    }