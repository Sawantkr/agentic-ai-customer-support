from graph.state import SupportState


def get_customer_data(state: SupportState) -> dict:
    customer_data = state.get(
        "customer_data",
        {},
    )

    if not customer_data.get("success"):
        return {}

    return customer_data.get("data", {})


def customer_data_available(state: SupportState) -> bool:
    customer_data = state.get("customer_data", {})
    return customer_data.get("success", False)


def handle_login_problem(state: SupportState) -> dict:
    return {
        "response": (
            "We identified a login issue. "
            "Please verify your credentials, check your network connection, "
            "and try signing in again. "
            "If the problem continues, we can escalate it for further review."
        ),
        "resolution_status": "resolved",
        "escalation_required": False,
    }


def handle_password_reset(state: SupportState) -> dict:
    return {
        "response": (
            "We identified a password reset request. "
            "Please use the password recovery process to securely reset your password."
        ),
        "resolution_status": "resolved",
        "escalation_required": False,
    }


def handle_account_management(state: SupportState) -> dict:

    if not customer_data_available(state):
        return {
            "response": (
                "I could not verify your Sawantflix account right now. "
                "Please try again."
            ),
            "resolution_status": "unresolved",
            "escalation_required": True,
        }

    data = get_customer_data(state)

    customer = data.get("customer", {})

    customer_name = customer.get("name") or "there"
    email = customer.get("email")

    response = f"Hi {customer_name}! I found your Sawantflix account."

    if email:
        response += f" Your registered email is {email}."

    response += (
        " You can review and update supported account settings "
        "from your Sawantflix account."
    )

    return {
        "response": response,
        "resolution_status": "resolved",
        "escalation_required": False,
    }


def handle_suspicious_access(state: SupportState) -> dict:
    return {
        "response": (
            "For security reasons, your suspicious-access request "
            "requires human review. Your request has been escalated "
            "to the support team."
        ),
        "escalation_required": True,
        "escalation_reason": "sensitive_request",
        "resolution_status": "unresolved",
    }


def handle_account_deletion(state: SupportState) -> dict:
    return {
        "response": (
            "Account deletion is a sensitive request and requires "
            "human review. Your request has been escalated to the support team."
        ),
        "escalation_required": True,
        "escalation_reason": "sensitive_request",
        "resolution_status": "unresolved",
    }


def handle_other_account(state: SupportState) -> dict:

    if not customer_data_available(state):
        return {
            "response": (
                "I could not verify your Sawantflix account right now. "
                "Please try again."
            ),
            "resolution_status": "unresolved",
            "escalation_required": True,
        }

    data = get_customer_data(state)

    customer = data.get("customer", {})

    customer_name = customer.get("name") or "there"
    email = customer.get("email")

    response = f"Hi {customer_name}! I found your Sawantflix account."

    if email:
        response += f" Your registered email is {email}."

    response += (
        " Please provide a little more detail about the account issue "
        "you are facing."
    )

    return {
        "response": response,
        "resolution_status": "unresolved",
        "escalation_required": False,
    }