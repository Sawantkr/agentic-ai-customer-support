from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from langgraph.types import Command

from api.database import (
    create_ticket,
    get_customer,
    get_order,
    get_payment,
    get_subscription,
    get_ticket,
    initialize_database,
)

from api.schemas import (
    ResumeRequest,
    SupportRequest,
    SupportResponse,
)

from config.checkpointer import (
    close_checkpointer,
    create_checkpointer,
)

from config.logging import configure_logging
from graph.builder import build_graph


configure_logging()


# ==================================================
# APPLICATION LIFESPAN
# ==================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    initialize_database()

    checkpointer, resource = create_checkpointer()

    app.state.graph = build_graph(
        checkpointer=checkpointer,
    )

    app.state.checkpointer_resource = resource

    yield

    close_checkpointer(resource)


# ==================================================
# FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="Customer Support Agent API",
    version="1.0.0",
    lifespan=lifespan,
)


# ==================================================
# LANGGRAPH CONFIGURATION
# ==================================================

def get_config(thread_id: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
        }
    }


# ==================================================
# BUILD SUPPORT RESPONSE
# ==================================================

def build_response(
    graph,
    thread_id: str,
    result: dict,
) -> SupportResponse:

    config = get_config(thread_id)

    snapshot = graph.get_state(config)

    if snapshot.interrupts:

        interrupt_data = snapshot.interrupts[0].value

        return SupportResponse(
            thread_id=thread_id,
            status="human_review_required",
            interrupt_data=interrupt_data,
        )

    return SupportResponse(
        thread_id=thread_id,
        status="completed",
        response=result.get("response"),
    )


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
    }


# ==================================================
# PAYMENT API
# ==================================================

@app.get("/payments/{payment_id}")
def get_payment_details(payment_id: str):

    payment = get_payment(payment_id)

    if payment is None:

        raise HTTPException(
            status_code=404,
            detail=f"No payment found with ID {payment_id}.",
        )

    return {
        "success": True,
        "payment": payment,
    }


# ==================================================
# ORDER API
# ==================================================

@app.get("/orders/{order_id}")
def get_order_details(order_id: str):

    order = get_order(order_id)

    if order is None:

        raise HTTPException(
            status_code=404,
            detail=f"No order found with ID {order_id}.",
        )

    return {
        "success": True,
        "order": order,
    }

# ==================================================
# CUSTOMER API
# ==================================================

@app.get("/customers/{customer_id}")
def get_customer_details(customer_id: str):

    customer = get_customer(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail=f"No customer found with ID {customer_id}.",
        )

    return {
        "success": True,
        "customer": customer,
    }

# ==================================================
# SUBSCRIPTION API
# ==================================================

@app.get("/subscriptions/{subscription_id}")
def get_subscription_details(subscription_id: str):

    subscription = get_subscription(subscription_id)

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail=f"No subscription found with ID {subscription_id}.",
        )

    return {
        "success": True,
        "subscription": subscription,
    }

# ==================================================
# CREATE SUPPORT TICKET
# ==================================================

@app.post("/tickets")
def create_ticket_details(
    customer_message: str,
    category: str = "general",
):

    ticket = create_ticket(
        customer_message=customer_message,
        category=category,
    )

    return {
        "success": True,
        "ticket": ticket,
    }


# ==================================================
# GET SUPPORT TICKET
# ==================================================

@app.get("/tickets/{ticket_id}")
def get_ticket_details(ticket_id: str):

    ticket = get_ticket(ticket_id)

    if ticket is None:

        raise HTTPException(
            status_code=404,
            detail=f"No ticket found with ID {ticket_id}.",
        )

    return {
        "success": True,
        "ticket": ticket,
    }


# ==================================================
# CUSTOMER SUPPORT
# ==================================================

@app.post(
    "/support",
    response_model=SupportResponse,
)
def create_support_request(request: SupportRequest):

    graph = app.state.graph

    config = get_config(request.thread_id)

    snapshot = graph.get_state(config)

    if snapshot.interrupts:

        raise HTTPException(
            status_code=409,
            detail=(
                "This conversation is waiting for human review. "
                "Resume the existing request before submitting "
                "another message."
            ),
        )

    result = graph.invoke(
        {
            "customer_message": request.message,
        },
        config=config,
    )

    return build_response(
        graph,
        request.thread_id,
        result,
    )


# ==================================================
# GET SUPPORT STATUS
# ==================================================

@app.get(
    "/support/{thread_id}",
    response_model=SupportResponse,
)
def get_support_status(thread_id: str):

    graph = app.state.graph

    config = get_config(thread_id)

    snapshot = graph.get_state(config)

    if not snapshot.values:

        raise HTTPException(
            status_code=404,
            detail="Conversation thread not found.",
        )

    if snapshot.interrupts:

        return SupportResponse(
            thread_id=thread_id,
            status="human_review_required",
            interrupt_data=snapshot.interrupts[0].value,
        )

    return SupportResponse(
        thread_id=thread_id,
        status="completed",
        response=snapshot.values.get("response"),
    )


# ==================================================
# RESUME HUMAN SUPPORT
# ==================================================

@app.post(
    "/support/resume",
    response_model=SupportResponse,
)
def resume_support_request(request: ResumeRequest):

    graph = app.state.graph

    config = get_config(request.thread_id)

    snapshot = graph.get_state(config)

    if not snapshot.values:

        raise HTTPException(
            status_code=404,
            detail="Conversation thread not found.",
        )

    if not snapshot.interrupts:

        raise HTTPException(
            status_code=409,
            detail="This conversation is not waiting for human review.",
        )

    result = graph.invoke(
        Command(resume=request.human_response),
        config=config,
    )

    return build_response(
        graph,
        request.thread_id,
        result,
    )