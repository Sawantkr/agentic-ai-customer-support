from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

from langgraph.types import Command

from firebase_admin import auth as firebase_auth

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

from config.firebase import initialize_firebase
from config.logging import configure_logging

from graph.builder import build_graph


# ==================================================
# LOGGING
# ==================================================

configure_logging()


# ==================================================
# APPLICATION LIFESPAN
# ==================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Initialize Firebase
    initialize_firebase()

    # Initialize local support database
    initialize_database()

    # Create LangGraph checkpointer
    checkpointer, resource = create_checkpointer()

    # Build LangGraph
    app.state.graph = build_graph(
        checkpointer=checkpointer,
    )

    app.state.checkpointer_resource = resource

    yield

    # Close checkpointer when application shuts down
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
# CORS CONFIGURATION
# ==================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        # Vite development server
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        # Backup Vite ports
        "http://localhost:5174",
        "http://127.0.0.1:5174",

        # Production Sawantflix frontend
        "https://sawantflix-app-1.onrender.com",
    ],

    allow_credentials=True,

    allow_methods=[
        "*",
    ],

    allow_headers=[
        "*",
    ],
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
# FIREBASE AUTHENTICATION
# ==================================================

def get_firebase_uid(
    authorization: str | None,
) -> str:

    # ----------------------------------------------
    # CHECK AUTHORIZATION HEADER
    # ----------------------------------------------

    if not authorization:

        raise HTTPException(
            status_code=401,
            detail=(
                "Missing Firebase authentication token."
            ),
        )

    # ----------------------------------------------
    # CHECK BEARER FORMAT
    # ----------------------------------------------

    if not authorization.startswith("Bearer "):

        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid authorization header."
            ),
        )

    # ----------------------------------------------
    # EXTRACT TOKEN
    # ----------------------------------------------

    token = authorization.split(
        " ",
        1,
    )[1].strip()

    if not token:

        raise HTTPException(
            status_code=401,
            detail=(
                "Missing Firebase ID token."
            ),
        )

    # ----------------------------------------------
    # VERIFY FIREBASE TOKEN
    # ----------------------------------------------

    try:

        decoded_token = firebase_auth.verify_id_token(
            token
        )

        firebase_uid = decoded_token.get(
            "uid"
        )

        if not firebase_uid:

            raise HTTPException(
                status_code=401,
                detail=(
                    "Firebase UID not found in token."
                ),
            )

        return firebase_uid

    except HTTPException:

        raise

    except Exception as error:

        print(
            "Firebase token verification failed:",
            error,
        )

        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid or expired Firebase "
                "authentication token."
            ),
        )


# ==================================================
# BUILD SUPPORT RESPONSE
# ==================================================

def build_response(
    graph,
    thread_id: str,
    result: dict,
) -> SupportResponse:

    config = get_config(
        thread_id
    )

    snapshot = graph.get_state(
        config
    )

    # ----------------------------------------------
    # HUMAN REVIEW
    # ----------------------------------------------

    if snapshot.interrupts:

        interrupt_data = (
            snapshot.interrupts[0].value
        )

        return SupportResponse(
            thread_id=thread_id,
            status="human_review_required",
            interrupt_data=interrupt_data,
        )

    # ----------------------------------------------
    # NORMAL RESPONSE
    # ----------------------------------------------

    return SupportResponse(
        thread_id=thread_id,
        status="completed",
        response=result.get(
            "response"
        ),
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
def get_payment_details(
    payment_id: str,
):

    payment = get_payment(
        payment_id
    )

    if payment is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No payment found with ID "
                f"{payment_id}."
            ),
        )

    return {
        "success": True,
        "payment": payment,
    }


# ==================================================
# ORDER API
# ==================================================

@app.get("/orders/{order_id}")
def get_order_details(
    order_id: str,
):

    order = get_order(
        order_id
    )

    if order is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No order found with ID "
                f"{order_id}."
            ),
        )

    return {
        "success": True,
        "order": order,
    }


# ==================================================
# CUSTOMER API
# ==================================================

@app.get("/customers/{customer_id}")
def get_customer_details(
    customer_id: str,
):

    customer = get_customer(
        customer_id
    )

    if customer is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No customer found with ID "
                f"{customer_id}."
            ),
        )

    return {
        "success": True,
        "customer": customer,
    }


# ==================================================
# SUBSCRIPTION API
# ==================================================

@app.get(
    "/subscriptions/{subscription_id}"
)
def get_subscription_details(
    subscription_id: str,
):

    subscription = get_subscription(
        subscription_id
    )

    if subscription is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No subscription found with ID "
                f"{subscription_id}."
            ),
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

@app.get(
    "/tickets/{ticket_id}"
)
def get_ticket_details(
    ticket_id: str,
):

    ticket = get_ticket(
        ticket_id
    )

    if ticket is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No ticket found with ID "
                f"{ticket_id}."
            ),
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
def create_support_request(
    request: SupportRequest,
    authorization: str | None = Header(
        default=None
    ),
):

    # ----------------------------------------------
    # VERIFY FIREBASE USER
    # ----------------------------------------------

    firebase_uid = get_firebase_uid(
        authorization
    )

    # ----------------------------------------------
    # GET LANGGRAPH
    # ----------------------------------------------

    graph = app.state.graph

    config = get_config(
        request.thread_id
    )

    snapshot = graph.get_state(
        config
    )

    # ----------------------------------------------
    # CHECK HUMAN REVIEW STATE
    # ----------------------------------------------

    if snapshot.interrupts:

        raise HTTPException(
            status_code=409,
            detail=(
                "This conversation is waiting "
                "for human review. Resume the "
                "existing request before submitting "
                "another message."
            ),
        )

    # ----------------------------------------------
    # RUN CUSTOMER SUPPORT AGENT
    # ----------------------------------------------

    result = graph.invoke(
        {
            "customer_message": request.message,
            "firebase_uid": firebase_uid,
        },
        config=config,
    )

    # ----------------------------------------------
    # BUILD RESPONSE
    # ----------------------------------------------

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
def get_support_status(
    thread_id: str,
):

    graph = app.state.graph

    config = get_config(
        thread_id
    )

    snapshot = graph.get_state(
        config
    )

    if not snapshot.values:

        raise HTTPException(
            status_code=404,
            detail=(
                "Conversation thread not found."
            ),
        )

    # ----------------------------------------------
    # HUMAN REVIEW
    # ----------------------------------------------

    if snapshot.interrupts:

        return SupportResponse(
            thread_id=thread_id,
            status="human_review_required",
            interrupt_data=(
                snapshot.interrupts[0].value
            ),
        )

    # ----------------------------------------------
    # COMPLETED
    # ----------------------------------------------

    return SupportResponse(
        thread_id=thread_id,
        status="completed",
        response=snapshot.values.get(
            "response"
        ),
    )


# ==================================================
# RESUME HUMAN SUPPORT
# ==================================================

@app.post(
    "/support/resume",
    response_model=SupportResponse,
)
def resume_support_request(
    request: ResumeRequest,
):

    graph = app.state.graph

    config = get_config(
        request.thread_id
    )

    snapshot = graph.get_state(
        config
    )

    if not snapshot.values:

        raise HTTPException(
            status_code=404,
            detail=(
                "Conversation thread not found."
            ),
        )

    if not snapshot.interrupts:

        raise HTTPException(
            status_code=409,
            detail=(
                "This conversation is not waiting "
                "for human review."
            ),
        )

    # ----------------------------------------------
    # RESUME LANGGRAPH
    # ----------------------------------------------

    result = graph.invoke(
        Command(
            resume=request.human_response,
        ),
        config=config,
    )

    return build_response(
        graph,
        request.thread_id,
        result,
    )