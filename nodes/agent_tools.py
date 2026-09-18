from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from config.llm import get_llm

from tools.support_tools import (
    check_customer,
    check_order,
    check_payment,
    check_subscription,
    check_ticket_status,
    create_support_ticket,
)


# ==================================================
# LANGCHAIN TOOLS
# ==================================================

@tool
def payment_lookup(payment_id: str) -> dict:
    """Look up the status and details of a payment using its payment ID."""
    return check_payment(payment_id)


@tool
def order_lookup(order_id: str) -> dict:
    """Look up the status and estimated delivery of an order using its order ID."""
    return check_order(order_id)


@tool
def subscription_lookup(subscription_id: str) -> dict:
    """Look up the plan, status, start date and expiry date of a subscription."""
    return check_subscription(subscription_id)


@tool
def customer_lookup(customer_id: str) -> dict:
    """Look up customer account details using customer ID."""
    return check_customer(customer_id)


@tool
def support_ticket_create(
    customer_message: str,
    category: str = "general",
) -> dict:
    """Create a new customer support ticket."""
    return create_support_ticket(
        customer_message,
        category,
    )


@tool
def support_ticket_lookup(ticket_id: str) -> dict:
    """Look up an existing customer support ticket by ticket ID."""
    return check_ticket_status(ticket_id)


# ==================================================
# AVAILABLE SUPPORT TOOLS
# ==================================================

SUPPORT_TOOLS = [
    payment_lookup,
    order_lookup,
    subscription_lookup,
    customer_lookup,
    support_ticket_create,
    support_ticket_lookup,
]


# ==================================================
# AGENT TOOL NODE
# ==================================================

def agent_tool_support(state):

    customer_message = state["customer_message"]

    llm = get_llm().bind_tools(SUPPORT_TOOLS)

    response = llm.invoke(
        [
            HumanMessage(
                content=f"""
You are a customer support agent.

Decide whether you need to use one of the available support tools
to answer the customer's request.

Available tools:

- payment_lookup
  Use this when the customer asks about a payment.

- order_lookup
  Use this when the customer asks about an order.

- subscription_lookup
  Use this when the customer asks about a subscription,
  plan, subscription status, or expiry date.

- customer_lookup
  Use this when the customer asks about their customer account,
  account status, name, or registered email using a customer ID.

- support_ticket_create
  Use this when the customer wants to create or raise a support ticket.

- support_ticket_lookup
  Use this when the customer wants to check an existing support ticket.

Customer request:
{customer_message}
"""
            )
        ]
    )

    # ==================================================
    # NO TOOL REQUIRED
    # ==================================================

    if not response.tool_calls:

        return {
            "response": response.content,
            "resolution_status": "resolved",
            "escalation_required": False,
        }

    # ==================================================
    # EXECUTE TOOLS
    # ==================================================

    tool_results = []

    for tool_call in response.tool_calls:

        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        selected_tool = {
            "payment_lookup": payment_lookup,
            "order_lookup": order_lookup,
            "subscription_lookup": subscription_lookup,
            "customer_lookup": customer_lookup,
            "support_ticket_create": support_ticket_create,
            "support_ticket_lookup": support_ticket_lookup,
        }.get(tool_name)

        if selected_tool is None:
            continue

        result = selected_tool.invoke(tool_args)

        tool_results.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
            )
        )

    # ==================================================
    # GENERATE FINAL RESPONSE
    # ==================================================

    final_response = llm.invoke(
        [
            HumanMessage(
                content=f"""
You are a customer support agent.

Answer the customer's request using the tool result below.

Customer request:
{customer_message}

Tool result:
{tool_results}

Rules:
- Give a direct answer to the customer.
- Use only the information from the tool result.
- Do not invent any information.
- Keep the response concise.
"""
            )
        ]
    )

    response_text = final_response.content

    if not response_text:
        response_text = (
            "I found the customer information successfully, "
            "but I could not generate the final response."
        )

    return {
        "response": response_text,
        "resolution_status": "resolved",
        "escalation_required": False,
    }