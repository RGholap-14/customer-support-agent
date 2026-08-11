from langchain_core.messages import AIMessage


def support_router(state: dict) -> dict:
    """Route the latest user message to a support intent."""
    last_message = state["messages"][-1].content if state["messages"] else ""
    last_message = last_message.lower()

    if any(keyword in last_message for keyword in ["refund", "return", "charge", "billing"]):
        intent = "refund"
    else:
        intent = "general"

    return {"intent": intent}


def support_agent(state: dict) -> dict:
    """Generate a simple customer support response."""
    last_message = state["messages"][-1].content if state["messages"] else ""
    response = (
        f"Thanks for contacting support. I can help with your request: {last_message}"
    )
    return {"messages": [AIMessage(content=response)]}
