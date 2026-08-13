from langchain_core.tools import tool
from database import get_connection


@tool
def get_order(order_id: str):
    """Fetch an order from PostgreSQL using the order ID."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    order_id,
                    customer_id,
                    item,
                    amount,
                    status,
                    delivered_date,
                    condition
                FROM orders
                WHERE order_id = %s
                """,
                (order_id,),
            )

            row = cur.fetchone()

    if not row:
        return None

    return {
        "order_id": row[0],
        "customer_id": row[1],
        "item": row[2],
        "amount": float(row[3]),
        "status": row[4],
        "delivered_date": str(row[5]),
        "condition": row[6],
    }



@tool
def search_policy() -> str:
    """Fetch the refund policy from PostgreSQL."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT policy_text
                FROM policies
                WHERE policy_name = %s
                LIMIT 1
                """,
                ("Refund Policy",),
            )

            row = cur.fetchone()

    if not row:
        return "Refund policy not found."

    return row[0]

@tool
def process_refund(order_id: str, amount: float) -> str:
    """Process and record a refund in PostgreSQL."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Check that the order exists
            cur.execute(
                """
                SELECT order_id
                FROM orders
                WHERE order_id = %s
                """,
                (order_id,),
            )

            order = cur.fetchone()

            if not order:
                return f"Order {order_id} was not found."

            # Record the refund
            cur.execute(
                """
                INSERT INTO refunds (
                    order_id,
                    amount,
                    status,
                    approved_by
                )
                VALUES (%s, %s, %s, %s)
                RETURNING refund_id
                """,
                (order_id, amount, "processed", "customer_support_agent"),
            )

            refund_id = cur.fetchone()[0]

        conn.commit()

    return (
        f"Refund of ₹{amount:.2f} successfully processed "
        f"for order {order_id}. Refund ID: {refund_id}"
    )



if __name__ == "__main__":
    refund = process_refund.invoke({"order_id": "ORD-1003", "amount": 75000.0})
    print(refund)