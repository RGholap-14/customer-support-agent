from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state import SupportState

from nodes import (
    classify_intent,
    get_order_node,
    policy_node,
    generate_resolution,
    route_by_intent,
    refund_decision,
    process_refund_node,
    route_refund,
    human_approval,
    route_after_approval,
    refund_rejected_node,
)


def build_graph():

    builder = StateGraph(SupportState)

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------

    builder.add_node("classify", classify_intent)
    builder.add_node("get_order", get_order_node)
    builder.add_node("search_policy", policy_node)
    builder.add_node("refund_decision", refund_decision)
    builder.add_node("human_approval", human_approval)
    builder.add_node("process_refund", process_refund_node)
    builder.add_node("refund_rejected", refund_rejected_node)
    builder.add_node("resolve", generate_resolution)

    # --------------------------------------------------
    # Entry
    # --------------------------------------------------

    builder.add_edge(START, "classify")

    # --------------------------------------------------
    # Intent Routing
    # --------------------------------------------------

    builder.add_conditional_edges(
        "classify",
        route_by_intent,
        {
            "get_order": "get_order",
            "resolve": "resolve",
        },
    )

    # --------------------------------------------------
    # Order → Policy
    # --------------------------------------------------

    builder.add_edge("get_order", "search_policy")

    # --------------------------------------------------
    # Policy → Refund Decision
    # --------------------------------------------------

    builder.add_edge(
        "search_policy",
        "refund_decision",
    )

    # --------------------------------------------------
    # Refund Routing
    # --------------------------------------------------

    builder.add_conditional_edges(
        "refund_decision",
        route_refund,
        {
            "resolve": "resolve",
            "process_refund": "process_refund",
            "human_approval": "human_approval",
        },
    )

    # --------------------------------------------------
    # Human Approval Routing
    # --------------------------------------------------

    builder.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {
            "process_refund": "process_refund",
            "refund_rejected": "refund_rejected",
        },
    )

    # --------------------------------------------------
    # Final Nodes
    # --------------------------------------------------

    builder.add_edge(
        "process_refund",
        END,
    )

    builder.add_edge(
        "refund_rejected",
        END,
    )

    builder.add_edge(
        "resolve",
        END,
    )

    # --------------------------------------------------
    # Checkpointing
    # --------------------------------------------------

    checkpointer = MemorySaver()

    return builder.compile(
        checkpointer=checkpointer
    )


graph = build_graph()