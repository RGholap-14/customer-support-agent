from typing import Any
from datetime import date
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.types import interrupt

from state import SupportState
from tools import (
    get_order_details,
    search_policy,
    process_refund,
)

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


def classify_intent(state: SupportState) -> dict[str, Any]:
    #print("➡️ Executing: classify")

    """Classify the customer's request."""

    query = state["user_query"]

    prompt = f"""
You are a customer support classifier.

Classify the following customer request into exactly one category:

- order_issue
- refund_request
- general_question

Also provide a confidence score between 0 and 1.

Customer request:
{query}

Return your answer in this format:

intent: <category>
confidence: <number>
"""

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    content = response.content

    intent = "general_question"
    confidence = 0.5

    for line in content.splitlines():
        line = line.strip()

        if line.lower().startswith("intent:"):
            intent = line.split(":", 1)[1].strip()

        elif line.lower().startswith("confidence:"):
            try:
                confidence = float(
                    line.split(":", 1)[1].strip()
                )
            except ValueError:
                confidence = 0.5

    return {
        "intent": intent,
        "confidence": confidence,
    }


def get_order_node(state: SupportState) -> dict[str, Any]:
    #print("➡️ Executing: get_order")
    """Retrieve order details."""

    order_id = state.get("order_id")

    if not order_id:
        return {
            "error": "No order ID was provided."
        }

    result = get_order_details.invoke({
        "order_id": order_id
    })

    if "error" in result:
        return {
            "error": result["error"]
        }

    return {
        "order_details": result
    }


def policy_node(state: SupportState) -> dict[str, Any]:
    #print("➡️ Executing: search_policy")
    """Search the support policy."""

    query = state["user_query"]

    result = search_policy.invoke({
        "query": query
    })

    return {
        "policy_result": result
    }


def generate_resolution(state: SupportState) -> dict[str, Any]:
    #print("➡️ Executing: resolve")
    """Generate a resolution based on collected information."""

    query = state["user_query"]
    order_details = state.get("order_details", {})
    policy = state.get("policy_result", "")

    prompt = f"""
You are a customer support resolution agent.

Customer request:
{query}

Order details:
{order_details}

Relevant policy:
{policy}

Determine the appropriate resolution.

Rules:
- Damaged products can receive a full refund.
- Damage must be reported within 7 days.
- Refunds below ₹5,000 can be automatically approved.
- Refunds of ₹5,000 or more require human approval.

Return a concise explanation of the recommended resolution.
"""

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    return {
        "resolution": response.content
    }


def route_by_intent(state: SupportState) -> str:
    """Route based on detected customer intent."""

    intent = state.get("intent", "").lower()

    if intent == "refund_request":
        return "get_order"

    return "resolve"


def refund_decision(state: SupportState) -> dict[str, Any]:
    """Apply deterministic refund business rules."""

    order = state.get("order_details", {})

    if not order:
        return {
            "refund_required": False,
            "refund_eligible": False,
            "requires_human_approval": False,
            "refund_reason": "Order details are unavailable.",
        }

    amount = float(order.get("amount", 0))
    condition = order.get("condition", "").lower()
    delivered_date_str = order.get("delivered_date")

    # Rule 1: Product must be damaged
    if condition != "damaged":
        return {
            "refund_required": False,
            "refund_eligible": False,
            "requires_human_approval": False,
            "refund_amount": 0,
            "refund_reason": (
                "Refund is not eligible because the product "
                "was not reported as damaged."
            ),
        }

    # Rule 2: Damage must be reported within 7 days
    delivered_date = date.fromisoformat(delivered_date_str)
    today = date.today()

    days_since_delivery = (today - delivered_date).days

    if days_since_delivery > 7:
        return {
            "refund_required": True,
            "refund_eligible": False,
            "requires_human_approval": False,
            "refund_amount": amount,
            "refund_reason": (
                "Refund is not eligible because the 7-day "
                "refund window has expired."
            ),
        }

    # Rule 3: Refund is eligible
    requires_human_approval = amount >= 5000

    return {
        "refund_required": True,
        "refund_eligible": True,
        "requires_human_approval": requires_human_approval,
        "refund_amount": amount,
        "refund_reason": (
            "Refund is eligible under the damaged-product "
            "policy."
        ),
    }


def process_refund_node(state: SupportState) -> dict[str, Any]:
    """Process an approved refund."""

    order_id = state.get("order_id")
    amount = state.get("refund_amount", 0)

    result = process_refund.invoke({
        "order_id": order_id,
        "amount": amount,
    })

    return {
        "refund_approved": True,
        "resolution": result,
    }


def human_approval(state: SupportState) -> dict[str, Any]:
    approval = interrupt({
        "type": "refund_approval",
        "order_id": state.get("order_id"),
        "amount": state.get("refund_amount"),
        "message": (
            f"Refund of ₹{state.get('refund_amount')} "
            "requires human approval."
        ),
    })

    return {
        "refund_approved": approval == "approved"
    }


def route_refund(state: SupportState) -> str:
    """Route the refund workflow based on eligibility."""

    if not state.get("refund_eligible", False):
        return "resolve"

    if state.get("requires_human_approval", False):
        return "human_approval"

    return "process_refund"

def route_after_approval(state: SupportState) -> str:
    """Route based on human approval decision."""

    if state.get("refund_approved", False):
        return "process_refund"

    return "refund_rejected"

def refund_rejected_node(state: SupportState) -> dict[str, Any]:
    """Handle rejected refund."""

    return {
        "resolution": (
            f"Refund request for order "
            f"{state.get('order_id')} was rejected by the "
            "human reviewer."
        )
    }