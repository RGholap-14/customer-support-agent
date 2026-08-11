from langchain_core.tools import tool


@tool
def get_order_details(order_id: str) -> dict:
    """Retrieve order details using an order ID."""

    orders = {
        "ORD-1001": {
            "order_id": "ORD-1001",
            "customer_id": "CUST-001",
            "status": "delivered",
            "item": "Wireless Headphones",
            "amount": 4999.0,
            "delivered_date": "2026-08-08",
            "condition": "damaged",
        },
        "ORD-1002": {
            "order_id": "ORD-1002",
            "customer_id": "CUST-002",
            "status": "delivered",
            "item": "Mechanical Keyboard",
            "amount": 7999.0,
            "delivered_date": "2026-08-05",
            "condition": "good",
        },
    }

    order = orders.get(order_id)

    if not order:
        return {
            "error": f"Order {order_id} not found."
        }

    return order


@tool
def search_policy(query: str) -> str:
    """Search the customer support policy knowledge base."""

    policies = """
    Refund Policy:
    - Damaged products are eligible for a full refund.
    - Customers must report damage within 7 days of delivery.
    - Refunds below ₹5,000 can be automatically approved.
    - Refunds of ₹5,000 or more require human approval.
    - Products that are delivered in good condition are not eligible
      for damage-based refunds.
    """

    return policies


@tool
def process_refund(order_id: str, amount: float) -> str:
    """Process a refund for an eligible order."""

    return (
        f"Refund of ₹{amount:.2f} successfully processed "
        f"for order {order_id}."
    )