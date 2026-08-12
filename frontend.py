import streamlit as st
from dotenv import load_dotenv
from langgraph.types import Command

from graph import graph

load_dotenv()


st.set_page_config(
    page_title="Customer Support Agent",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Customer Support Agent")
st.caption("LangGraph + Tools + Human-in-the-Loop")


# --------------------------------------------------
# Session State
# --------------------------------------------------

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "waiting_for_approval" not in st.session_state:
    st.session_state.waiting_for_approval = False

if "approval_request" not in st.session_state:
    st.session_state.approval_request = None

if "result" not in st.session_state:
    st.session_state.result = None


# --------------------------------------------------
# Customer Input
# --------------------------------------------------

customer_id = st.text_input(
    "Customer ID",
    value="CUST-003",
)

order_id = st.text_input(
    "Order ID",
    value="ORD-1003",
)

user_query = st.text_area(
    "How can we help?",
    value="My order ORD-1003 arrived damaged. I want a refund.",
)


# --------------------------------------------------
# Start Workflow
# --------------------------------------------------

if st.button("Submit Request", type="primary"):

    st.session_state.thread_id = (
        f"{customer_id}-{order_id}"
    )

    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }

    initial_state = {
        "user_query": user_query,
        "customer_id": customer_id,
        "order_id": order_id,
        "messages": [],
    }

    result = graph.invoke(
        initial_state,
        config=config,
    )

    interrupts = result.get("__interrupt__")

    if interrupts:

        st.session_state.waiting_for_approval = True

        st.session_state.approval_request = (
            interrupts[0].value
        )

    else:

        st.session_state.waiting_for_approval = False
        st.session_state.result = result


# --------------------------------------------------
# Human Approval
# --------------------------------------------------

if st.session_state.waiting_for_approval:

    approval = st.session_state.approval_request

    st.warning("⚠️ Human approval required")

    st.write(
        approval.get("message")
    )

    st.write(
        f"**Order:** {approval.get('order_id')}"
    )

    st.write(
        f"**Refund Amount:** ₹{approval.get('amount'):,.2f}"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("✅ Approve Refund"):

            config = {
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            }

            result = graph.invoke(
                Command(resume="approved"),
                config=config,
            )

            st.session_state.result = result
            st.session_state.waiting_for_approval = False

            st.rerun()

    with col2:

        if st.button("❌ Reject Refund"):

            config = {
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            }

            result = graph.invoke(
                Command(resume="rejected"),
                config=config,
            )

            st.session_state.result = result
            st.session_state.waiting_for_approval = False

            st.rerun()


# --------------------------------------------------
# Final Result
# --------------------------------------------------

if st.session_state.result:

    result = st.session_state.result

    st.divider()

    st.subheader("Result")

    if result.get("refund_approved"):

        st.success(
            result.get("resolution")
        )

    else:

        st.info(
            result.get("resolution")
            or result.get("refund_reason")
            or "Request completed."
        )