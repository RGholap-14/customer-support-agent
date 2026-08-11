from langgraph.graph import StateGraph, END

from nodes import support_agent, support_router
from state import CustomerSupportState


workflow = StateGraph(CustomerSupportState)
workflow.add_node("router", support_router)
workflow.add_node("agent", support_agent)
workflow.set_entry_point("router")
workflow.add_edge("router", "agent")
workflow.add_edge("agent", END)

app_graph = workflow.compile()
