from dotenv import load_dotenv

from graph import graph

load_dotenv()


if __name__ == "__main__":

    initial_state = {
        "user_query": (
            "My order ORD-1003 arrived damaged. "
            "I want a refund."
        ),
        "customer_id": "CUST-003",
        "order_id": "ORD-1003",
        "messages": [],
    }

    config = {
        "configurable": {
            "thread_id": "test-customer-001"
        }
    }

    result = graph.invoke(
        initial_state,
        config=config,
    )

    print(result)