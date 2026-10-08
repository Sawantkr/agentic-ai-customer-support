import os
import sqlite3
from contextlib import asynccontextmanager
from unittest.mock import patch

from fastapi.testclient import TestClient
from langgraph.checkpoint.sqlite import SqliteSaver

from api.main import app
from graph.builder import build_graph


TEST_DATABASE_PATH = "test_support_checkpoints.db"

TEST_HEADERS = {
    "Authorization": "Bearer test-token",
}


# =========================================================
# MOCK FIREBASE AUTHENTICATION
# =========================================================

def mock_firebase_token(token):
    """
    Fake Firebase token verification for automated tests.

    Production Firebase authentication remains unchanged.
    """

    if token == "test-token":
        return {
            "uid": "test-user-123",
        }

    raise Exception("Invalid test token")


# =========================================================
# TEST APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def api_test_lifespan(app):
    connection = sqlite3.connect(
        TEST_DATABASE_PATH,
        check_same_thread=False,
    )

    checkpointer = SqliteSaver(connection)

    app.state.graph = build_graph(
        checkpointer=checkpointer,
    )

    app.state.connection = connection

    try:
        yield

    finally:
        connection.close()

        if os.path.exists(TEST_DATABASE_PATH):
            os.remove(TEST_DATABASE_PATH)


app.router.lifespan_context = api_test_lifespan


# =========================================================
# HEALTH TEST
# =========================================================

def test_health_endpoint():
    with patch(
        "api.main.firebase_auth.verify_id_token",
        side_effect=mock_firebase_token,
    ):
        with TestClient(app) as client:

            response = client.get("/health")

            assert response.status_code == 200

            assert response.json() == {
                "status": "healthy",
            }


# =========================================================
# SUPPORT REQUEST TEST
# =========================================================

def test_support_completed_request():
    with patch(
        "api.main.firebase_auth.verify_id_token",
        side_effect=mock_firebase_token,
    ):
        with TestClient(app) as client:

            response = client.post(
                "/support",
                json={
                    "thread_id": "test-billing-1",
                    "message": "I was charged twice.",
                },
                headers=TEST_HEADERS,
            )

            data = response.json()

            assert response.status_code == 200

            assert data["thread_id"] == "test-billing-1"

            assert (
                data["status"]
                == "human_review_required"
            )

            assert data["response"] is None

            assert data["interrupt_data"] is not None


# =========================================================
# HUMAN REVIEW TEST
# =========================================================

def test_support_human_review_required():
    with patch(
        "api.main.firebase_auth.verify_id_token",
        side_effect=mock_firebase_token,
    ):
        with TestClient(app) as client:

            response = client.post(
                "/support",
                json={
                    "thread_id": "test-hitl-1",
                    "message": (
                        "I have a strange technical problem."
                    ),
                },
                headers=TEST_HEADERS,
            )

            data = response.json()

            assert response.status_code == 200

            assert (
                data["status"]
                == "human_review_required"
            )

            assert data["response"] is None

            assert (
                data["interrupt_data"]["intent"]
                == "technical"
            )

            assert (
                data["interrupt_data"][
                    "escalation_reason"
                ]
                == "automatic_diagnosis_failed"
            )


# =========================================================
# RESUME SUPPORT TEST
# =========================================================

def test_support_resume():
    with patch(
        "api.main.firebase_auth.verify_id_token",
        side_effect=mock_firebase_token,
    ):
        with TestClient(app) as client:

            first_response = client.post(
                "/support",
                json={
                    "thread_id": "test-resume-1",
                    "message": (
                        "I have a strange technical problem."
                    ),
                },
                headers=TEST_HEADERS,
            )

            assert first_response.status_code == 200

            assert (
                first_response.json()["status"]
                == "human_review_required"
            )

            resume_response = client.post(
                "/support/resume",
                json={
                    "thread_id": "test-resume-1",
                    "human_response": (
                        "A human engineer reviewed "
                        "your request."
                    ),
                },
                headers=TEST_HEADERS,
            )

            data = resume_response.json()

            assert resume_response.status_code == 200

            assert data["status"] == "completed"

            assert (
                data["response"]
                == "A human engineer reviewed "
                "your request."
            )

            assert data["interrupt_data"] is None


# =========================================================
# GET SUPPORT STATUS TEST
# =========================================================

def test_get_support_status():
    with patch(
        "api.main.firebase_auth.verify_id_token",
        side_effect=mock_firebase_token,
    ):
        with TestClient(app) as client:

            create_response = client.post(
                "/support",
                json={
                    "thread_id": "test-status-1",
                    "message": "I was charged twice.",
                },
                headers=TEST_HEADERS,
            )

            assert create_response.status_code == 200

            response = client.get(
                "/support/test-status-1",
                headers=TEST_HEADERS,
            )

            data = response.json()

            assert response.status_code == 200

            assert (
                data["thread_id"]
                == "test-status-1"
            )

            assert (
                data["status"]
                == "human_review_required"
            )


# =========================================================
# RESUME NON-PAUSED THREAD TEST
# =========================================================

def test_resume_non_paused_thread_returns_conflict():
    with patch(
        "api.main.firebase_auth.verify_id_token",
        side_effect=mock_firebase_token,
    ):
        with TestClient(app) as client:

            create_response = client.post(
                "/support",
                json={
                    "thread_id": "test-conflict-1",
                    "message": (
                        "What is the status of "
                        "payment PAY1001?"
                    ),
                },
                headers=TEST_HEADERS,
            )

            assert create_response.status_code == 200

            response = client.post(
                "/support/resume",
                json={
                    "thread_id": "test-conflict-1",
                    "human_response": "Reviewed.",
                },
                headers=TEST_HEADERS,
            )

            assert response.status_code == 409


# =========================================================
# UNKNOWN THREAD TEST
# =========================================================

def test_unknown_thread_returns_not_found():
    with patch(
        "api.main.firebase_auth.verify_id_token",
        side_effect=mock_firebase_token,
    ):
        with TestClient(app) as client:

            response = client.get(
                "/support/"
                "thread-that-does-not-exist",
                headers=TEST_HEADERS,
            )

            assert response.status_code == 404