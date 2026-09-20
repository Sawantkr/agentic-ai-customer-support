from langgraph.graph import StateGraph, START, END

from graph.state import SupportState

from tools.support_tools import check_customer

from nodes.billing_nodes import (
    handle_duplicate_charge,
    handle_refund_request,
    handle_payment_failure,
    handle_other_billing,
)

from routers.billing_classifier import classify_billing_issue
from routers.billing_router import route_billing_issue


BILLING_PATH_MAP = {
    "duplicate_charge": "handle_duplicate_charge",
    "refund_request": "handle_refund_request",
    "payment_failure": "handle_payment_failure",
    "other_billing": "handle_other_billing",
}


def load_customer_data(state: SupportState) -> dict:
    """
    Fetch the authenticated customer's Sawantflix
    subscription and payment information.
    """

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
        "customer_data": customer_result
    }


def build_billing_graph():

    builder = StateGraph(SupportState)

    # ==============================================
    # LOAD CUSTOMER DATA
    # ==============================================

    builder.add_node(
        "load_customer_data",
        load_customer_data,
    )

    # ==============================================
    # BILLING CLASSIFIER
    # ==============================================

    builder.add_node(
        "classify_billing_issue",
        classify_billing_issue,
    )

    # ==============================================
    # BILLING HANDLERS
    # ==============================================

    builder.add_node(
        "handle_duplicate_charge",
        handle_duplicate_charge,
    )

    builder.add_node(
        "handle_refund_request",
        handle_refund_request,
    )

    builder.add_node(
        "handle_payment_failure",
        handle_payment_failure,
    )

    builder.add_node(
        "handle_other_billing",
        handle_other_billing,
    )

    # ==============================================
    # FLOW
    # ==============================================

    builder.add_edge(
        START,
        "load_customer_data",
    )

    builder.add_edge(
        "load_customer_data",
        "classify_billing_issue",
    )

    builder.add_conditional_edges(
        "classify_billing_issue",
        route_billing_issue,
        BILLING_PATH_MAP,
    )

    # ==============================================
    # END
    # ==============================================

    builder.add_edge(
        "handle_duplicate_charge",
        END,
    )

    builder.add_edge(
        "handle_refund_request",
        END,
    )

    builder.add_edge(
        "handle_payment_failure",
        END,
    )

    builder.add_edge(
        "handle_other_billing",
        END,
    )

    return builder.compile()