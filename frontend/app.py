import os
import uuid

import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

SAWANTFLIX_URL = "https://sawantflix-app-1.onrender.com"

if "API_URL" in st.secrets:
    DEFAULT_API_URL = st.secrets["API_URL"]
else:
    DEFAULT_API_URL = os.getenv(
        "API_URL",
        "http://127.0.0.1:8000",
    )

# Temporary local testing:
# Put your Firebase UID in the environment variable
# SAWANTFLIX_FIREBASE_UID.
FIREBASE_UID = os.getenv(
    "SAWANTFLIX_FIREBASE_UID",
    "",
)


st.set_page_config(
    page_title="Sawantflix Customer Support",
    page_icon="🎧",
    layout="wide",
)


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* ======================================================
       SAWANTFLIX MAIN LOGO
       ====================================================== */

    .sf-logo {
        text-align: center;
        white-space: nowrap;
        overflow: visible;
        font-size: clamp(32px, 5vw, 48px);
        font-weight: 900;
        letter-spacing: -2px;
        line-height: 1.15;
        margin: 8px 0 8px 0;
    }

    .sf-logo-red {
        color: #e50914;
    }

    .sf-logo-theme {
        color: var(--text-color);
    }

    .sf-subtitle {
        text-align: center;
        color: var(--text-color);
        opacity: 0.72;
        font-size: 18px;
        font-weight: 700;
        margin-top: 8px;
    }

    .sf-description {
        text-align: center;
        color: var(--text-color);
        opacity: 0.6;
        font-size: 14px;
        margin-top: 6px;
        margin-bottom: 18px;
    }


    /* ======================================================
       CUSTOMER SUPPORT AGENT
       ====================================================== */

    .agent-title {
        text-align: center;
        color: var(--text-color);
        font-size: clamp(30px, 4vw, 40px);
        font-weight: 800;
        margin-top: 8px;
        margin-bottom: 6px;
        white-space: nowrap;
    }

    .agent-subtitle {
        text-align: center;
        color: var(--text-color);
        opacity: 0.6;
        font-size: 14px;
        margin-bottom: 22px;
    }


    /* ======================================================
       SIDEBAR LOGO
       ====================================================== */

    .sidebar-logo {
        text-align: center;
        padding: 8px 0 16px 0;
        overflow: visible;
    }

    .sidebar-logo-text {
        white-space: nowrap;
        font-size: 27px;
        font-weight: 900;
        letter-spacing: -1.5px;
        line-height: 1.2;
    }

    .sidebar-subtitle {
        color: var(--text-color);
        opacity: 0.6;
        font-size: 13px;
        margin-top: 6px;
    }


    /* ======================================================
       HELP CARD
       ====================================================== */

    .sf-help-card {
        border: 1px solid rgba(229, 9, 20, 0.4);
        border-radius: 14px;
        padding: 14px;
        margin-top: 12px;
        background: rgba(229, 9, 20, 0.06);
    }

    .sf-help-title {
        color: #e50914;
        font-weight: 800;
        font-size: 15px;
        margin-bottom: 5px;
    }

    .sf-help-text {
        color: var(--text-color);
        opacity: 0.7;
        font-size: 13px;
        line-height: 1.45;
    }


    /* ======================================================
       RESPONSIVE SUPPORT
       ====================================================== */

    @media (max-width: 700px) {

        .sf-logo {
            font-size: 32px;
        }

        .agent-title {
            white-space: normal;
            font-size: 30px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state():

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = (
            f"customer-{uuid.uuid4().hex[:8]}"
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "waiting_for_human" not in st.session_state:
        st.session_state.waiting_for_human = False

    if "interrupt_data" not in st.session_state:
        st.session_state.interrupt_data = None


# ============================================================
# API
# ============================================================

def submit_support_request(
    api_url,
    thread_id,
    message,
    firebase_uid,
):

    response = requests.post(
        f"{api_url.rstrip('/')}/support",
        json={
            "thread_id": thread_id,
            "message": message,
            "firebase_uid": firebase_uid,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def resume_support_request(
    api_url,
    thread_id,
    human_response,
):

    response = requests.post(
        f"{api_url.rstrip('/')}/support/resume",
        json={
            "thread_id": thread_id,
            "human_response": human_response,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# CONVERSATION
# ============================================================

def start_new_conversation():

    st.session_state.thread_id = (
        f"customer-{uuid.uuid4().hex[:8]}"
    )

    st.session_state.messages = []

    st.session_state.waiting_for_human = False

    st.session_state.interrupt_data = None


def process_customer_message(
    customer_message,
    api_url,
):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": customer_message,
        }
    )

    # ---------------------------------------------
    # CHECK FIREBASE UID
    # ---------------------------------------------

    if not FIREBASE_UID:

        st.error(
            "Firebase UID is not configured. "
            "Please set SAWANTFLIX_FIREBASE_UID "
            "in the environment variables."
        )

        return

    try:

        with st.spinner(
            "Processing support request..."
        ):

            result = submit_support_request(
                api_url,
                st.session_state.thread_id,
                customer_message,
                FIREBASE_UID,
            )

        if result.get("status") == "completed":

            response_text = result.get(
                "response",
                "I could not generate a response.",
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response_text,
                }
            )

        elif result.get(
            "status"
        ) == "human_review_required":

            st.session_state.waiting_for_human = True

            st.session_state.interrupt_data = (
                result.get("interrupt_data")
            )

    except requests.RequestException as exc:

        st.error(
            f"API request failed: {exc}"
        )


# ============================================================
# INITIALIZE
# ============================================================

initialize_session_state()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # SAWANTFLIX LOGO
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-logo">'
        '<div class="sidebar-logo-text">'
        '<span style="color:#e50914;">SAWANT</span>'
        '<span style="color:var(--text-color);">FLIX</span>'
        '</div>'
        '<div class="sidebar-subtitle">'
        'Customer Support Agent'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()


    # --------------------------------------------------------
    # CONVERSATION
    # --------------------------------------------------------

    st.subheader("Conversation")

    st.code(
        st.session_state.thread_id
    )

    if st.button(
        "Start New Conversation",
        use_container_width=True,
    ):

        start_new_conversation()

        st.rerun()


    st.divider()


    # --------------------------------------------------------
    # API CONNECTION
    # --------------------------------------------------------

    st.subheader("API Connection")

    api_url = st.text_input(
        "API URL",
        value=DEFAULT_API_URL,
    )


    # --------------------------------------------------------
    # CUSTOMER ID STATUS
    # --------------------------------------------------------

    st.subheader("Customer Identity")

    if FIREBASE_UID:

        st.success(
            "Firebase customer identity connected."
        )

    else:

        st.warning(
            "Firebase customer identity is not configured."
        )


    # --------------------------------------------------------
    # SAWANTFLIX LINK
    # --------------------------------------------------------

    st.link_button(
        "🎬 Open Sawantflix ↗",
        SAWANTFLIX_URL,
        use_container_width=True,
    )

    st.caption(
        "Continue streaming your favorite content."
    )


    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    st.markdown(
        '<div class="sf-help-card">'
        '<div class="sf-help-title">'
        '🎧 Need Help?'
        '</div>'
        '<div class="sf-help-text">'
        'This is the AI customer support service for Sawantflix.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN SAWANTFLIX BRANDING
# ============================================================

st.markdown(
    '<div class="sf-logo">'
    '<span class="sf-logo-red">SAWANT</span>'
    '<span class="sf-logo-theme">FLIX</span>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="sf-subtitle">'
    'Customer Support'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="sf-description">'
    'Official AI support for your Sawantflix experience.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# OPEN SAWANTFLIX
# ============================================================

left, center, right = st.columns(
    [1, 1, 1]
)

with center:

    st.link_button(
        "🎬 Open Sawantflix ↗",
        SAWANTFLIX_URL,
        use_container_width=True,
    )


st.divider()


# ============================================================
# CUSTOMER SUPPORT AGENT
# ============================================================

st.markdown(
    '<div class="agent-title">'
    '🎧 Customer Support Agent'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="agent-subtitle">'
    'LangGraph-powered customer support with hybrid routing, '
    'specialized workflows, persistence, and human escalation.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# HUMAN SUPPORT REVIEW
# ============================================================

if st.session_state.waiting_for_human:

    interrupt_data = (
        st.session_state.interrupt_data
        or {}
    )

    st.warning(
        "This request requires human support review."
    )

    with st.expander(
        "View escalation details",
        expanded=True,
    ):

        st.write(
            "Customer Message:",
            interrupt_data.get(
                "customer_message",
                "Unknown",
            ),
        )

        st.write(
            "Intent:",
            interrupt_data.get(
                "intent",
                "unknown",
            ),
        )

        st.write(
            "Escalation Reason:",
            interrupt_data.get(
                "escalation_reason",
                "unknown",
            ),
        )

        diagnostic_result = (
            interrupt_data.get(
                "diagnostic_result"
            )
        )

        if diagnostic_result:

            st.write(
                "Diagnostic Result:",
                diagnostic_result,
            )


    st.subheader(
        "Human Support Review"
    )


    human_response = st.text_area(
        "Human Support Response",
        placeholder=(
            "Enter the human support response..."
        ),
    )


    if st.button(
        "Resume Workflow",
        type="primary",
        use_container_width=True,
    ):

        if not human_response.strip():

            st.warning(
                "Enter a human support response."
            )

        else:

            try:

                with st.spinner(
                    "Resuming workflow..."
                ):

                    result = resume_support_request(
                        api_url,
                        st.session_state.thread_id,
                        human_response.strip(),
                    )

                response_text = result.get(
                    "response"
                )

                if response_text:

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response_text,
                        }
                    )

                st.session_state.waiting_for_human = False

                st.session_state.interrupt_data = None

                st.rerun()


            except requests.RequestException as exc:

                st.error(
                    f"API request failed: {exc}"
                )


# ============================================================
# QUICK SUPPORT
# ============================================================

if not st.session_state.waiting_for_human:

    st.subheader(
        "⚡ Quick Support"
    )

    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )

    selected_message = None


    # --------------------------------------------------------
    # DUPLICATE CHARGE
    # --------------------------------------------------------

    with col1:

        if st.button(
            "💳 Duplicate Charge",
            use_container_width=True,
        ):

            selected_message = (
                "I was charged twice for my subscription."
            )


    # --------------------------------------------------------
    # RESET PASSWORD
    # --------------------------------------------------------

    with col2:

        if st.button(
            "🔐 Reset Password",
            use_container_width=True,
        ):

            selected_message = (
                "I want to reset my password."
            )


    # --------------------------------------------------------
    # ACCOUNT LOCKED
    # --------------------------------------------------------

    with col3:

        if st.button(
            "🔒 Account Locked",
            use_container_width=True,
        ):

            selected_message = (
                "My account is locked and I cannot login."
            )


    # --------------------------------------------------------
    # TECHNICAL ISSUE
    # --------------------------------------------------------

    with col4:

        if st.button(
            "🛠️ Technical Issue",
            use_container_width=True,
        ):

            selected_message = (
                "My application is not working."
            )


    # --------------------------------------------------------
    # PRICING
    # --------------------------------------------------------

    with col5:

        if st.button(
            "💰 Pricing",
            use_container_width=True,
        ):

            selected_message = (
                "I have a question about pricing."
            )


    # ========================================================
    # CHAT INPUT
    # ========================================================

    customer_message = st.chat_input(
        "Describe your support issue..."
    )


    # --------------------------------------------------------
    # NORMAL CHAT
    # --------------------------------------------------------

    if customer_message:

        process_customer_message(
            customer_message,
            api_url,
        )

        st.rerun()


    # --------------------------------------------------------
    # QUICK SUPPORT
    # --------------------------------------------------------

    if selected_message:

        process_customer_message(
            selected_message,
            api_url,
        )

        st.rerun()