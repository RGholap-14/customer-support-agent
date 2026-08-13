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
    placeholder="Example: CUST-003",
)

order_id = st.text_input(
    "Order ID",
    placeholder="Example: ORD-1003",
)

user_query = st.text_area(
    "How can we help?",
    placeholder="Example: My order ORD-1003 arrived damaged. I want a refund.",
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

    if result.get("refund_approved") is True:

        st.success(
            result.get("resolution")
            or "Refund approved and processed successfully."
        )

    elif result.get("refund_approved") is False:

        st.error(
            result.get("resolution")
            or "Refund request was rejected."
        )

    else:

        st.info(
            result.get("resolution")
            or result.get("refund_reason")
            or "Request completed."
        )


st.sidebar.header("Admin")

admin_action = st.sidebar.selectbox(
    "Choose action",
    ["None", "Add Customer", "Add Order"],
)

if admin_action == "Add Customer":

    st.sidebar.subheader("Add Customer")

    new_customer_id = st.sidebar.text_input(
        "Customer ID",
        placeholder="Example: CUST-004",
    )

    new_customer_name = st.sidebar.text_input(
        "Name",
        placeholder="Example: Rutuja",
    )

    new_customer_email = st.sidebar.text_input(
        "Email",
        placeholder="Example: user@example.com",
    )

    if st.sidebar.button("Add Customer"):

        if not new_customer_id.strip():
            st.sidebar.error("Customer ID is required.")

        elif not new_customer_name.strip():
            st.sidebar.error("Customer name is required.")

        else:
            from database import add_customer

            success = add_customer(
                new_customer_id.strip(),
                new_customer_name.strip(),
                new_customer_email.strip(),
            )

            if success:
                st.sidebar.success("Customer added successfully.")
            else:
                st.sidebar.warning(
                    f"Customer {new_customer_id} already exists."
                )

if admin_action == "Add Order":

    st.sidebar.subheader("Add Order")

    new_order_id = st.sidebar.text_input(
        "Order ID",
        placeholder="Example: ORD-1004",
    )

    new_order_customer_id = st.sidebar.text_input(
        "Customer ID",
        placeholder="Example: CUST-004",
    )

    new_item = st.sidebar.text_input(
        "Item",
        placeholder="Example: Smartphone",
    )

    new_amount = st.sidebar.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=100.0,
    )

    new_status = st.sidebar.selectbox(
        "Status",
        ["delivered", "shipped", "processing"],
    )

    new_delivery_date = st.sidebar.date_input(
        "Delivery Date",
    )

    new_condition = st.sidebar.selectbox(
        "Condition",
        ["good", "damaged"],
    )

    if st.sidebar.button("Add Order"):

        if not new_order_id.strip():
            st.sidebar.error("Order ID is required.")

        elif not new_order_customer_id.strip():
            st.sidebar.error("Customer ID is required.")

        elif not new_item.strip():
            st.sidebar.error("Item is required.")

        else:
            from database import add_order

            add_order(
                new_order_id.strip(),
                new_order_customer_id.strip(),
                new_item.strip(),
                new_amount,
                new_status,
                new_delivery_date,
                new_condition,
            )

            st.sidebar.success("Order added successfully.")