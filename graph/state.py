from typing import Literal, TypedDict, Annotated

from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


SupportIntent = Literal[
    "billing",
    "technical",
    "account",
    "general",
    "unknown",
]


RoutingSource = Literal[
    "deterministic",
    "llm",
    "unresolved",
]


BillingIssue = Literal[
    "duplicate_charge",
    "refund_request",
    "payment_failure",
    "other_billing",
]


TechnicalIssue = Literal[
    "application_error",
    "performance_issue",
    "feature_issue",
    "other_technical",
]


AccountIssue = Literal[
    "login_problem",
    "password_reset",
    "account_management",
    "suspicious_access",
    "account_deletion",
    "other_account",
]


ResolutionStatus = Literal[
    "resolved",
    "unresolved",
]


EscalationReason = Literal[
    "automatic_diagnosis_failed",
    "sensitive_request",
    "unsupported_request",
]


GeneralIssue = Literal[
    "pricing_question",
    "product_question",
    "other_general",
]


ErrorType = Literal[
    "llm_routing_error",
    "workflow_error",
    "unexpected_error",
]


class SupportState(TypedDict, total=False):

    # ==================================================
    # CUSTOMER
    # ==================================================

    firebase_uid: str

    customer_data: dict

    # ==================================================
    # CUSTOMER MESSAGE
    # ==================================================

    customer_message: str
    processed_message: str

    # ==================================================
    # ROUTING
    # ==================================================

    intent: SupportIntent
    routing_source: RoutingSource
    needs_llm_routing: bool

    # ==================================================
    # BILLING
    # ==================================================

    billing_issue: BillingIssue

    # ==================================================
    # TECHNICAL
    # ==================================================

    technical_issue: TechnicalIssue
    diagnostic_result: str
    resolution_status: ResolutionStatus

    # ==================================================
    # ESCALATION
    # ==================================================

    escalation_required: bool
    escalation_reason: EscalationReason

    # ==================================================
    # ACCOUNT
    # ==================================================

    account_issue: AccountIssue

    # ==================================================
    # GENERAL
    # ==================================================

    general_issue: GeneralIssue

    # ==================================================
    # ERROR HANDLING
    # ==================================================

    error_occurred: bool
    error_type: ErrorType
    error_message: str

    # ==================================================
    # MESSAGES
    # ==================================================

    messages: Annotated[list[AnyMessage], add_messages]

    # ==================================================
    # FINAL RESPONSE
    # ==================================================

    response: str