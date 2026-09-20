from graph.state import SupportState


# ==================================================
# CUSTOMER DATA HELPER
# ==================================================

def get_customer_data(state: SupportState) -> dict:
    """
    Read customer information already loaded
    by the billing workflow.
    """

    customer_data = state.get(
        "customer_data",
        {},
    )

    if not customer_data.get("success"):
        return {}

    return customer_data.get(
        "data",
        {},
    )


# ==================================================
# CUSTOMER VERIFICATION
# ==================================================

def customer_data_available(
    state: SupportState,
) -> bool:

    customer_data = state.get(
        "customer_data",
        {},
    )

    return customer_data.get(
        "success",
        False,
    )


# ==================================================
# DUPLICATE CHARGE
# ==================================================

def handle_duplicate_charge(
    state: SupportState,
) -> dict:

    if not customer_data_available(state):

        return {
            "response": (
                "I could not verify your Sawantflix account "
                "right now. Please try again."
            ),
            "resolution_status": "pending_review",
            "escalation_required": True,
        }

    data = get_customer_data(state)

    customer = data.get(
        "customer",
        {},
    )

    latest_payment = data.get(
        "latestPayment",
    )

    customer_name = (
        customer.get("name")
        or "there"
    )

    if latest_payment:

        payment_status = latest_payment.get(
            "status"
        )

        payment_amount = latest_payment.get(
            "amount"
        )

        if payment_amount is not None:

            payment_info = (
                f" Your latest payment is "
                f"₹{payment_amount} with status "
                f"{payment_status}."
            )

        else:

            payment_info = (
                f" Your latest payment status is "
                f"{payment_status}."
            )

    else:

        payment_info = (
            " I could not find a recent payment record."
        )

    return {
        "response": (
            f"Hi {customer_name}! "
            f"I found your Sawantflix account."
            f"{payment_info} "
            "Your request appears to involve a duplicate charge. "
            "The duplicate transaction will need to be reviewed."
        ),
        "resolution_status": "pending_review",
        "escalation_required": True,
    }


# ==================================================
# REFUND REQUEST
# ==================================================

def handle_refund_request(
    state: SupportState,
) -> dict:

    if not customer_data_available(state):

        return {
            "response": (
                "I could not verify your Sawantflix account "
                "right now. Please try again."
            ),
            "resolution_status": "pending_review",
            "escalation_required": True,
        }

    data = get_customer_data(state)

    customer = data.get(
        "customer",
        {},
    )

    latest_payment = data.get(
        "latestPayment",
    )

    customer_name = (
        customer.get("name")
        or "there"
    )

    if latest_payment:

        payment_status = latest_payment.get(
            "status"
        )

        payment_amount = latest_payment.get(
            "amount"
        )

        if payment_amount is not None:

            payment_info = (
                f" Your latest payment is "
                f"₹{payment_amount} with status "
                f"{payment_status}."
            )

        else:

            payment_info = (
                f" Your latest payment status is "
                f"{payment_status}."
            )

    else:

        payment_info = (
            " I could not find a recent payment record."
        )

    return {
        "response": (
            f"Hi {customer_name}! "
            f"I found your Sawantflix account."
            f"{payment_info} "
            "Your request is a refund request. "
            "Refund eligibility will need to be reviewed."
        ),
        "resolution_status": "pending_review",
        "escalation_required": True,
    }


# ==================================================
# PAYMENT FAILURE
# ==================================================

def handle_payment_failure(
    state: SupportState,
) -> dict:

    if not customer_data_available(state):

        return {
            "response": (
                "I could not verify your Sawantflix account "
                "right now. Please try again."
            ),
            "resolution_status": "pending_review",
            "escalation_required": True,
        }

    data = get_customer_data(state)

    customer = data.get(
        "customer",
        {},
    )

    latest_payment = data.get(
        "latestPayment",
    )

    customer_name = (
        customer.get("name")
        or "there"
    )

    if latest_payment:

        payment_status = latest_payment.get(
            "status"
        )

        payment_amount = latest_payment.get(
            "amount"
        )

        if payment_amount is not None:

            payment_info = (
                f" Your latest payment is "
                f"₹{payment_amount} with status "
                f"{payment_status}."
            )

        else:

            payment_info = (
                f" Your latest payment status is "
                f"{payment_status}."
            )

    else:

        payment_info = (
            " I could not find a recent payment record."
        )

    return {
        "response": (
            f"Hi {customer_name}! "
            f"I found your Sawantflix account."
            f"{payment_info} "
            "If your payment failed, please verify "
            "your payment details or try another "
            "payment method."
        ),
        "resolution_status": "resolved",
        "escalation_required": False,
    }


# ==================================================
# OTHER BILLING
# ==================================================

def handle_other_billing(
    state: SupportState,
) -> dict:

    if not customer_data_available(state):

        return {
            "response": (
                "I could not verify your Sawantflix account "
                "right now. Please try again."
            ),
            "resolution_status": "pending_review",
            "escalation_required": True,
        }

    data = get_customer_data(state)

    customer = data.get(
        "customer",
        {},
    )

    subscription = data.get(
        "subscription",
    )

    latest_payment = data.get(
        "latestPayment",
    )

    # ==================================================
    # CUSTOMER
    # ==================================================

    customer_name = (
        customer.get("name")
        or "there"
    )

    # ==================================================
    # SUBSCRIPTION
    # ==================================================

    if subscription:

        plan = subscription.get(
            "plan"
        )

        subscription_status = subscription.get(
            "status"
        )

        amount = subscription.get(
            "amount"
        )

        end_date = subscription.get(
            "end_date"
        )

        subscription_text = (
            f"Your current subscription plan is "
            f"{plan} with status "
            f"{subscription_status}."
        )

        if amount is not None:

            subscription_text += (
                f" The subscription amount is "
                f"₹{amount}."
            )

        if end_date:

            subscription_text += (
                f" It is valid until {end_date}."
            )

    else:

        subscription_text = (
            "You currently do not have "
            "a subscription record."
        )

    # ==================================================
    # PAYMENT
    # ==================================================

    if latest_payment:

        payment_status = latest_payment.get(
            "status"
        )

        payment_amount = latest_payment.get(
            "amount"
        )

        payment_id = latest_payment.get(
            "razorpay_payment_id"
        )

        payment_text = (
            f"Your latest payment status is "
            f"{payment_status}"
        )

        if payment_amount is not None:

            payment_text += (
                f" for ₹{payment_amount}"
            )

        if payment_id:

            payment_text += (
                f". Payment ID: {payment_id}"
            )

        payment_text += "."

    else:

        payment_text = (
            "No payment record was found."
        )

    # ==================================================
    # FINAL RESPONSE
    # ==================================================

    return {
        "response": (
            f"Hi {customer_name}! "
            f"{subscription_text} "
            f"{payment_text}"
        ),
        "resolution_status": "resolved",
        "escalation_required": False,
    }