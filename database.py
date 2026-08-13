import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not configured.")

    return psycopg.connect(DATABASE_URL)


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(255)
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id VARCHAR(50) PRIMARY KEY,
                    customer_id VARCHAR(50) NOT NULL
                        REFERENCES customers(customer_id),
                    item VARCHAR(255) NOT NULL,
                    amount NUMERIC(12, 2) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    delivered_date DATE,
                    condition VARCHAR(50)
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS policies (
                    policy_id SERIAL PRIMARY KEY,
                    policy_name VARCHAR(100) NOT NULL,
                    policy_text TEXT NOT NULL
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS refunds (
                    refund_id SERIAL PRIMARY KEY,
                    order_id VARCHAR(50) NOT NULL
                        REFERENCES orders(order_id),
                    amount NUMERIC(12, 2) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    approved_by VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

        conn.commit()


def seed_data():
    with get_connection() as conn:
        with conn.cursor() as cur:

            # Customers
            cur.execute("""
                INSERT INTO customers (customer_id, name, email)
                VALUES
                    ('CUST-001', 'Rahul', 'rahul@example.com'),
                    ('CUST-002', 'Priya', 'priya@example.com'),
                    ('CUST-003', 'Amit', 'amit@example.com')
                ON CONFLICT (customer_id) DO NOTHING;
            """)

            # Orders
            cur.execute("""
                INSERT INTO orders (
                    order_id,
                    customer_id,
                    item,
                    amount,
                    status,
                    delivered_date,
                    condition
                )
                VALUES
                    (
                        'ORD-1001',
                        'CUST-001',
                        'Wireless Headphones',
                        4999.00,
                        'delivered',
                        '2026-08-08',
                        'damaged'
                    ),
                    (
                        'ORD-1002',
                        'CUST-002',
                        'Smart Watch',
                        3500.00,
                        'delivered',
                        '2026-08-09',
                        'good'
                    ),
                    (
                        'ORD-1003',
                        'CUST-003',
                        'Laptop',
                        75000.00,
                        'delivered',
                        '2026-08-08',
                        'damaged'
                    )
                ON CONFLICT (order_id) DO NOTHING;
            """)

            # Refund policy
            cur.execute("""
                INSERT INTO policies (
                    policy_name,
                    policy_text
                )
                SELECT
                    'Refund Policy',
                    $policy$
                    - Damaged products are eligible for a full refund.
                    - Customers must report damage within 7 days of delivery.
                    - Refunds below ₹5,000 can be automatically approved.
                    - Refunds of ₹5,000 or more require human approval.
                    - Products delivered in good condition are not eligible
                      for damage-based refunds.
                    $policy$
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM policies
                    WHERE policy_name = 'Refund Policy'
                );
            """)

        conn.commit()

def add_customer(customer_id: str, name: str, email: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO customers (customer_id, name, email)
                VALUES (%s, %s, %s)
                ON CONFLICT (customer_id) DO NOTHING
                """,
                (customer_id, name, email),
            )

            inserted = cur.rowcount > 0

        conn.commit()

    return inserted

def add_order(
    order_id: str,
    customer_id: str,
    item: str,
    amount: float,
    status: str,
    delivered_date: str,
    condition: str,
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders (
                    order_id,
                    customer_id,
                    item,
                    amount,
                    status,
                    delivered_date,
                    condition
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    order_id,
                    customer_id,
                    item,
                    amount,
                    status,
                    delivered_date,
                    condition,
                ),
            )
        conn.commit()

if __name__ == "__main__":
    init_db()
    seed_data()
    print("Database initialized successfully and data seeded.")