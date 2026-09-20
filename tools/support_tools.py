import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# ==================================================
# API CONFIGURATION
# ==================================================

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    f"http://127.0.0.1:{os.getenv('PORT', '8000')}",
)

SAWANTFLIX_API_BASE_URL = os.getenv(
    "SAWANTFLIX_API_BASE_URL",
    "http://localhost:5000",
)

SAWANTFLIX_SUPPORT_API_KEY = os.getenv(
    "SAWANTFLIX_SUPPORT_API_KEY"
)


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
                "message": (
                    f"No payment found with ID {payment_id}."
                ),
            }

        return {
            "success": False,
            "message": (
                f"Payment API returned HTTP {error.code}."
            ),
        }

    except URLError:

        return {
            "success": False,
            "message": (
                "Payment service is currently unavailable."
            ),
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
                "message": (
                    f"No order found with ID {order_id}."
                ),
            }

        return {
            "success": False,
            "message": (
                f"Order API returned HTTP {error.code}."
            ),
        }

    except URLError:

        return {
            "success": False,
            "message": (
                "Order service is currently unavailable."
            ),
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
            "message": (
                f"Ticket API returned HTTP {error.code}."
            ),
        }

    except URLError:

        return {
            "success": False,
            "message": (
                "Ticket service is currently unavailable."
            ),
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
                "message": (
                    f"No ticket found with ID {ticket_id}."
                ),
            }

        return {
            "success": False,
            "message": (
                f"Ticket API returned HTTP {error.code}."
            ),
        }

    except URLError:

        return {
            "success": False,
            "message": (
                "Ticket service is currently unavailable."
            ),
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

def check_customer(firebase_uid: str) -> dict:

    # ----------------------------------------------
    # Check API key configuration
    # ----------------------------------------------

    if not SAWANTFLIX_SUPPORT_API_KEY:

        print(
            "SAWANTFLIX_SUPPORT_API_KEY is missing"
        )

        return {
            "success": False,
            "message": (
                "Sawantflix support API key is not configured."
            ),
        }

    # ----------------------------------------------
    # Build Sawantflix customer API URL
    # ----------------------------------------------

    url = (
        f"{SAWANTFLIX_API_BASE_URL}"
        f"/api/support/customer/{firebase_uid}"
    )

    # Do NOT print the API key.
    print(
        f"Calling Sawantflix customer API: "
        f"{SAWANTFLIX_API_BASE_URL}"
    )

    # We only log whether a Firebase UID was received.
    print(
        f"Firebase UID received: "
        f"{bool(firebase_uid)}"
    )

    # ----------------------------------------------
    # Create request
    # ----------------------------------------------

    request = Request(
        url,
        headers={
            "x-support-api-key": SAWANTFLIX_SUPPORT_API_KEY,
        },
        method="GET",
    )

    # ----------------------------------------------
    # Call Sawantflix backend
    # ----------------------------------------------

    try:

        with urlopen(request, timeout=5) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

            print(
                "Sawantflix customer API "
                "returned HTTP 200"
            )

            return {
                "success": True,
                "data": data,
            }

    # ----------------------------------------------
    # HTTP errors
    # ----------------------------------------------

    except HTTPError as error:

        print(
            f"Sawantflix customer API returned "
            f"HTTP {error.code}"
        )

        if error.code == 404:

            return {
                "success": False,
                "message": (
                    "Customer not found in Sawantflix."
                ),
            }

        if error.code == 401:

            return {
                "success": False,
                "message": (
                    "Unauthorized request to "
                    "Sawantflix support API."
                ),
            }

        return {
            "success": False,
            "message": (
                f"Sawantflix Customer API returned "
                f"HTTP {error.code}."
            ),
        }

    # ----------------------------------------------
    # URL / connection errors
    # ----------------------------------------------

    except URLError as error:

        print(
            "Sawantflix customer API URL error: "
            f"{error}"
        )

        return {
            "success": False,
            "message": (
                "Sawantflix customer service is "
                "currently unavailable."
            ),
        }

    # ----------------------------------------------
    # Unexpected errors
    # ----------------------------------------------

    except Exception as error:

        print(
            "Sawantflix customer API "
            f"unexpected error: {error}"
        )

        return {
            "success": False,
            "message": (
                "Unexpected Sawantflix customer API error."
            ),
        }