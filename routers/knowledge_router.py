import re

from graph.state import SupportState


# ==================================================
# BILLING / ACCOUNT SUPPORT PATTERNS
# ==================================================

BILLING_SUPPORT_PATTERNS = [
    "subscription",
    "subscription plan",
    "current plan",
    "my plan",
    "payment status",
    "payment details",
    "recent payment",
    "billing",
    "charged",
    "charge",
    "payment failed",
    "payment failure",
    "duplicate payment",
    "duplicate charge",
    "refund",
    "refund request",
]


# ==================================================
# GENERAL PRODUCT SUPPORT PATTERNS
# ==================================================

GENERAL_PRODUCT_PATTERNS = [
    "what is sawantflix",
    "what is this platform",
    "what is this product",
    "what does sawantflix do",
    "what does sawantflix offer",
    "about sawantflix",
    "tell me about sawantflix",
]


# ==================================================
# REAL-TIME TOOL PATTERNS
# ==================================================

REALTIME_TOOL_PATTERNS = [
    "check payment",
    "check order",
    "order status",
    "where is my order",
    "track my order",
    "create a ticket",
    "create a support ticket",
    "open a ticket",
    "open a support ticket",
    "raise a ticket",
    "raise a support ticket",
    "support ticket",
    "ticket status",
    "check ticket",
    "check my ticket",
]


# ==================================================
# KNOWLEDGE BASE PATTERNS
# ==================================================

KNOWLEDGE_PATTERNS = [
    "how can",
    "how do",
    "how to",
    "what is",
    "what are",
    "what does",
    "where can",
    "where do",
    "which",
    "can you explain",
    "please explain",
    "tell me about",
    "information about",
]


# ==================================================
# ROUTER
# ==================================================

def route_knowledge_question(state: SupportState) -> str:

    message = state["processed_message"].lower().strip()

    # --------------------------------------------------
    # IDs that always require real-time tools
    # --------------------------------------------------

    if re.search(r"\bpay\d+\b", message):
        return "tool"

    if re.search(r"\bord\d+\b", message):
        return "tool"

    if re.search(r"\bticket\d+\b", message):
        return "tool"

    if re.search(r"\bsub\d+\b", message):
        return "tool"

    if re.search(r"\bcus\d+\b", message):
        return "tool"

    # --------------------------------------------------
    # Billing / subscription support
    # --------------------------------------------------

    for pattern in BILLING_SUPPORT_PATTERNS:
        if pattern in message:
            return "support"

    # --------------------------------------------------
    # General product support
    # --------------------------------------------------

    for pattern in GENERAL_PRODUCT_PATTERNS:
        if pattern in message:
            return "support"

    # --------------------------------------------------
    # Other real-time support requests
    # --------------------------------------------------

    for pattern in REALTIME_TOOL_PATTERNS:
        if pattern in message:
            return "tool"

    # --------------------------------------------------
    # Knowledge-base questions
    # --------------------------------------------------

    for pattern in KNOWLEDGE_PATTERNS:
        if pattern in message:
            return "knowledge"

    # --------------------------------------------------
    # Normal support workflow
    # --------------------------------------------------

    return "support"