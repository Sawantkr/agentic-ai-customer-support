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


st.set_page_config(
    page_title="Sawantflix Customer Support",
    page_icon="🎧",
    layout="wide",
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
# API FUNCTIONS
# ============================================================

def submit_support_request(
    api_url,
    thread_id,
    message,
):
    response = requests.post(
        f"{api_url.rstrip('/')}/support",
        json={
            "thread_id": thread_id,
            "message": message,
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
# CONVERSATION FUNCTIONS
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

    try:
        with st.spinner(
            "Processing support request..."
        ):
            result = submit_support_request(
                api_url=api_url,
                thread_id=st.session_state.thread_id,
                message=customer_message,
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

        elif result.get("status") == "human_review_required":

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
        '<div style="text-align:center; padding:12px 0 18px 0;">'
        '<div style="font-size:30px; font-weight:900; '
        'letter-spacing:-1px; line-height:1.1;">'
        '<span style="color:#e50914;">SAWANT</span>'
        '<span style="color:#ffffff;">FLIX</span>'
        '</div>'
        '<div style="font-size:13px; color:#aaaaaa; '
        'margin-top:6px;">'
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


    st.divider()


    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    st.info(
        "🎧 **Need Help?**\n\n"
        "This is the AI customer support "
        "service for Sawantflix."
    )


# ============================================================
# MAIN SAWANTFLIX BRANDING
# ============================================================

st.markdown(
    '<div style="text-align:center; padding:8px 0 4px 0;">'
    '<div style="font-size:38px; font-weight:900; '
    'letter-spacing:-1.5px; line-height:1.1;">'
    '<span style="color:#e50914;">SAWANT</span>'
    '<span style="color:#ffffff;">FLIX</span>'
    '</div>'
    '<div style="font-size:18px; font-weight:600; '
    'color:#aaaaaa; margin-top:7px;">'
    'Customer Support'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)


st.markdown(
    '<div style="text-align:center; color:#aaaaaa; '
    'font-size:14px; margin-bottom:18px;">'
    'Official AI support for your Sawantflix experience.'
    '</div>',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# OPEN SAWANTFLIX
# ------------------------------------------------------------

button_col_left, button_col, button_col_right = st.columns(
    [1, 1, 1]
)

with button_col:
    st.link_button(
        "🎬 Open Sawantflix ↗",
        SAWANTFLIX_URL,
        use_container_width=True,
    )


st.divider()


# ============================================================
# CUSTOMER SUPPORT AGENT
# ============================================================

st.title(
    "🎧 Customer Support Agent"
)

st.caption(
    "LangGraph-powered customer support with hybrid routing, "
    "specialized workflows, persistence, and human escalation."
)


# ============================================================
# CONVERSATION MESSAGES
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
                        api_url=api_url,
                        thread_id=(
                            st.session_state.thread_id
                        ),
                        human_response=(
                            human_response.strip()
                        ),
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
        "Quick Support"
    )


    quick_messages = {

        "💳 Duplicate Charge":
            "I was charged twice for my subscription.",

        "🔐 Reset Password":
            "I want to reset my password.",

        "🔒 Account Locked":
            "My account is locked and I cannot login.",

        "🛠️ Technical Issue":
            "My application is not working.",

        "💰 Pricing":
            "I have a question about pricing.",
    }


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

            selected_message = quick_messages[
                "💳 Duplicate Charge"
            ]


    # --------------------------------------------------------
    # RESET PASSWORD
    # --------------------------------------------------------

    with col2:

        if st.button(
            "🔐 Reset Password",
            use_container_width=True,
        ):

            selected_message = quick_messages[
                "🔐 Reset Password"
            ]


    # --------------------------------------------------------
    # ACCOUNT LOCKED
    # --------------------------------------------------------

    with col3:

        if st.button(
            "🔒 Account Locked",
            use_container_width=True,
        ):

            selected_message = quick_messages[
                "🔒 Account Locked"
            ]


    # --------------------------------------------------------
    # TECHNICAL ISSUE
    # --------------------------------------------------------

    with col4:

        if st.button(
            "🛠️ Technical Issue",
            use_container_width=True,
        ):

            selected_message = quick_messages[
                "🛠️ Technical Issue"
            ]


    # --------------------------------------------------------
    # PRICING
    # --------------------------------------------------------

    with col5:

        if st.button(
            "💰 Pricing",
            use_container_width=True,
        ):

            selected_message = quick_messages[
                "💰 Pricing"
            ]


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
            customer_message=customer_message,
            api_url=api_url,
        )

        st.rerun()


    # --------------------------------------------------------
    # QUICK SUPPORT MESSAGE
    # --------------------------------------------------------

    if selected_message:

        process_customer_message(
            customer_message=selected_message,
            api_url=api_url,
        )

        st.rerun()