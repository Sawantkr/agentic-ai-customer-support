from langgraph.graph import END, START, StateGraph

from graph.state import SupportState

from tools.support_tools import check_customer

from nodes.account_nodes import (
    handle_account_deletion,
    handle_account_management,
    handle_login_problem,
    handle_other_account,
    handle_password_reset,
    handle_suspicious_access,
)

from routers.account_classifier import classify_account_issue
from routers.account_router import route_account_issue


ACCOUNT_PATH_MAP = {
    "login_problem": "handle_login_problem",
    "password_reset": "handle_password_reset",
    "account_management": "handle_account_management",
    "suspicious_access": "handle_suspicious_access",
    "account_deletion": "handle_account_deletion",
    "other_account": "handle_other_account",
}


def load_customer_data(state: SupportState) -> dict:

    firebase_uid = state.get("firebase_uid")

    if not firebase_uid:
        return {
            "customer_data": {
                "success": False,
                "message": "Customer identity is missing.",
            }
        }

    customer_result = check_customer(firebase_uid)

    return {
        "customer_data": customer_result,
    }


def build_account_graph():

    builder = StateGraph(SupportState)

    # --------------------------------------------------
    # Customer identity / data
    # --------------------------------------------------

    builder.add_node(
        "load_customer_data",
        load_customer_data,
    )

    # --------------------------------------------------
    # Account classification
    # --------------------------------------------------

    builder.add_node(
        "classify_account_issue",
        classify_account_issue,
    )

    # --------------------------------------------------
    # Account handlers
    # --------------------------------------------------

    builder.add_node(
        "handle_login_problem",
        handle_login_problem,
    )

    builder.add_node(
        "handle_password_reset",
        handle_password_reset,
    )

    builder.add_node(
        "handle_account_management",
        handle_account_management,
    )

    builder.add_node(
        "handle_suspicious_access",
        handle_suspicious_access,
    )

    builder.add_node(
        "handle_account_deletion",
        handle_account_deletion,
    )

    builder.add_node(
        "handle_other_account",
        handle_other_account,
    )

    # --------------------------------------------------
    # Flow
    # --------------------------------------------------

    builder.add_edge(
        START,
        "load_customer_data",
    )

    builder.add_edge(
        "load_customer_data",
        "classify_account_issue",
    )

    builder.add_conditional_edges(
        "classify_account_issue",
        route_account_issue,
        ACCOUNT_PATH_MAP,
    )

    # --------------------------------------------------
    # Endpoints
    # --------------------------------------------------

    builder.add_edge(
        "handle_login_problem",
        END,
    )

    builder.add_edge(
        "handle_password_reset",
        END,
    )

    builder.add_edge(
        "handle_account_management",
        END,
    )

    builder.add_edge(
        "handle_suspicious_access",
        END,
    )

    builder.add_edge(
        "handle_account_deletion",
        END,
    )

    builder.add_edge(
        "handle_other_account",
        END,
    )

    return builder.compile()