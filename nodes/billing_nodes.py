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
    """
    Handle billing questions that do not belong
    to duplicate charge, refund, or payment failure.

    The response is selected according to the
    customer's exact question so that we do not
    return unrelated subscription/payment data.
    """

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

    customer_name = (
        customer.get("name")
        or "there"
    )

    # ==================================================
    # READ THE ORIGINAL USER QUESTION
    # ==================================================

    message = (
        state.get(
            "processed_message",
            "",
        )
        or state.get(
            "customer_message",
            "",
        )
    ).lower().strip()

    # ==================================================
    # CURRENT PLAN
    # ==================================================

    current_plan_question = any(
        phrase in message
        for phrase in (
            "what is my current plan",
            "what's my current plan",
            "what is my plan",
            "what's my plan",
            "my current plan",
            "my plan",
            "which plan am i on",
            "which plan am i subscribed to",
        )
    )

    if current_plan_question:

        if not subscription:

            return {
                "response": (
                    "You currently do not have "
                    "an active subscription."
                ),
                "resolution_status": "resolved",
                "escalation_required": False,
            }

        plan = subscription.get("plan")
        status = subscription.get("status")

        if plan:

            return {
                "response": (
                    f"Your current Sawantflix plan is "
                    f"{plan}. Your subscription status is "
                    f"{status}."
                ),
                "resolution_status": "resolved",
                "escalation_required": False,
            }

        return {
            "response": (
                "Your Sawantflix subscription plan "
                "could not be determined."
            ),
            "resolution_status": "resolved",
            "escalation_required": False,
        }

    # ==================================================
    # SUBSCRIPTION STATUS
    # ==================================================

    subscription_status_question = any(
        phrase in message
        for phrase in (
            "is my subscription active",
            "is my subscription still active",
            "is my subscription active?",
            "subscription status",
            "what is my subscription status",
            "what's my subscription status",
            "am i subscribed",
            "am i currently subscribed",
        )
    )

    if subscription_status_question:

        if not subscription:

            return {
                "response": (
                    "You currently do not have "
                    "a subscription record."
                ),
                "resolution_status": "resolved",
                "escalation_required": False,
            }

        status = subscription.get(
            "status"
        )

        if status:

            return {
                "response": (
                    f"Your Sawantflix subscription is "
                    f"{status}."
                ),
                "resolution_status": "resolved",
                "escalation_required": False,
            }

        return {
            "response": (
                "I could not determine your "
                "subscription status."
            ),
            "resolution_status": "resolved",
            "escalation_required": False,
        }

    # ==================================================
    # SUBSCRIPTION EXPIRY
    # ==================================================

    expiry_question = any(
        phrase in message
        for phrase in (
            "when does my subscription expire",
            "when will my subscription expire",
            "when is my subscription expiring",
            "subscription expiry",
            "subscription expiration",
            "when does my plan expire",
            "when will my plan expire",
            "when is my plan expiring",
            "when does my subscription end",
            "when will my subscription end",
        )
    )

    if expiry_question:

        if not subscription:

            return {
                "response": (
                    "You currently do not have "
                    "a subscription record."
                ),
                "resolution_status": "resolved",
                "escalation_required": False,
            }

        end_date = subscription.get(
            "end_date"
        )

        if end_date:

            return {
                "response": (
                    f"Your Sawantflix subscription is "
                    f"valid until {end_date}."
                ),
                "resolution_status": "resolved",
                "escalation_required": False,
            }

        return {
            "response": (
                "I could not determine your "
                "subscription expiry date."
            ),
            "resolution_status": "resolved",
            "escalation_required": False,
        }

    # ==================================================
    # LATEST PAYMENT
    # ==================================================

    latest_payment_question = any(
        phrase in message
        for phrase in (
            "what is my latest payment",
            "what's my latest payment",
            "show my latest payment",
            "my latest payment",
            "what is my last payment",
            "what's my last payment",
            "show my last payment",
            "my last payment",
            "what was my recent payment",
            "what is my recent payment",
            "show my recent payment",
            "recent payment",
        )
    )

    if latest_payment_question:

        if not latest_payment:

            return {
                "response": (
                    "I could not find a payment record "
                    "for your Sawantflix account."
                ),
                "resolution_status": "resolved",
                "escalation_required": False,
            }

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
            "Your latest payment"
        )

        if payment_amount is not None:

            payment_text += (
                f" was ₹{payment_amount}"
            )

        if payment_status:

            payment_text += (
                f" and its status is "
                f"{payment_status}"
            )

        if payment_id:

            payment_text += (
                f". Payment ID: {payment_id}"
            )

        payment_text += "."

        return {
            "response": payment_text,
            "resolution_status": "resolved",
            "escalation_required": False,
        }

    # ==================================================
    # GENERIC BILLING QUESTION
    # ==================================================

    if subscription:

        plan = subscription.get(
            "plan"
        )

        status = subscription.get(
            "status"
        )

        amount = subscription.get(
            "amount"
        )

        end_date = subscription.get(
            "end_date"
        )

        subscription_text = (
            f"Your current Sawantflix plan is "
            f"{plan} with status {status}."
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

    return {
        "response": (
            f"Hi {customer_name}! "
            f"{subscription_text} "
            f"{payment_text}"
        ),
        "resolution_status": "resolved",
        "escalation_required": False,
    }