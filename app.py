from dotenv import load_dotenv

from graph import app_graph

load_dotenv()


def run_support_agent(user_input: str) -> dict:
    """Run the customer support workflow for a single user message."""
    return app_graph.invoke({"messages": [("user", user_input)]})


if __name__ == "__main__":
    user_input = input("Customer message: ").strip()
    if user_input:
        result = run_support_agent(user_input)
        print(result["messages"][-1].content)
