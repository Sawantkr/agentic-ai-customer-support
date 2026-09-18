import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE_URL = "http://127.0.0.1:8000"


# ==================================================
# PAYMENT TOOL
# ==================================================

def check_payment(payment_id: str) -> dict:

    url = f"{API_BASE_URL}/payments/{payment_id}"

    try:
        with urlopen(url, timeout=5) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:

        if error.code == 404:
            return {
                "success": False,
                "message": f"No payment found with ID {payment_id}.",
            }

        return {
            "success": False,
            "message": f"Payment API returned HTTP {error.code}.",
        }

    except URLError:

        return {
            "success": False,
            "message": "Payment service is currently unavailable.",
        }


# ==================================================
# ORDER TOOL
# ==================================================

def check_order(order_id: str) -> dict:

    url = f"{API_BASE_URL}/orders/{order_id}"

    try:
        with urlopen(url, timeout=5) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:

        if error.code == 404:
            return {
                "success": False,
                "message": f"No order found with ID {order_id}.",
            }

        return {
            "success": False,
            "message": f"Order API returned HTTP {error.code}.",
        }

    except URLError:

        return {
            "success": False,
            "message": "Order service is currently unavailable.",
        }


# ==================================================
# CREATE SUPPORT TICKET TOOL
# ==================================================

def create_support_ticket(
    customer_message: str,
    category: str = "general",
) -> dict:

    query = urlencode(
        {
            "customer_message": customer_message,
            "category": category,
        }
    )

    url = f"{API_BASE_URL}/tickets?{query}"

    request = Request(
        url,
        method="POST",
    )

    try:

        with urlopen(request, timeout=5) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:

        return {
            "success": False,
            "message": f"Ticket API returned HTTP {error.code}.",
        }

    except URLError:

        return {
            "success": False,
            "message": "Ticket service is currently unavailable.",
        }


# ==================================================
# TICKET STATUS TOOL
# ==================================================

def check_ticket_status(ticket_id: str) -> dict:

    url = f"{API_BASE_URL}/tickets/{ticket_id}"

    try:

        with urlopen(url, timeout=5) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:

        if error.code == 404:
            return {
                "success": False,
                "message": f"No ticket found with ID {ticket_id}.",
            }

        return {
            "success": False,
            "message": f"Ticket API returned HTTP {error.code}.",
        }

    except URLError:

        return {
            "success": False,
            "message": "Ticket service is currently unavailable.",
        }

        # ==================================================
# SUBSCRIPTION TOOL
# ==================================================

def check_subscription(subscription_id: str) -> dict:

    url = f"{API_BASE_URL}/subscriptions/{subscription_id}"

    try:

        with urlopen(url, timeout=5) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:

        if error.code == 404:
            return {
                "success": False,
                "message": (
                    f"No subscription found with ID "
                    f"{subscription_id}."
                ),
            }

        return {
            "success": False,
            "message": (
                f"Subscription API returned "
                f"HTTP {error.code}."
            ),
        }

    except URLError:

        return {
            "success": False,
            "message": (
                "Subscription service is currently unavailable."
            ),
        }

        # ==================================================
# CUSTOMER TOOL
# ==================================================

def check_customer(customer_id: str) -> dict:

    url = f"{API_BASE_URL}/customers/{customer_id}"

    try:

        with urlopen(url, timeout=5) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:

        if error.code == 404:
            return {
                "success": False,
                "message": (
                    f"No customer found with ID "
                    f"{customer_id}."
                ),
            }

        return {
            "success": False,
            "message": (
                f"Customer API returned "
                f"HTTP {error.code}."
            ),
        }

    except URLError:

        return {
            "success": False,
            "message": (
                "Customer service is currently unavailable."
            ),
        }