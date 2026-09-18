import sqlite3
from pathlib import Path


DATABASE_DIR = Path("data")
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "support.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    # ==================================================
    # PAYMENTS TABLE
    # ==================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            description TEXT NOT NULL
        )
        """
    )

    # ==================================================
    # ORDERS TABLE
    # ==================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            estimated_delivery TEXT NOT NULL
        )
        """
    )

    # ==================================================
    # SUPPORT TICKETS TABLE
    # ==================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            status TEXT NOT NULL,
            customer_message TEXT NOT NULL
        )
        """
    )

    # ==================================================
    # CUSTOMERS TABLE
    # ==================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            account_status TEXT NOT NULL
        )
        """
    )

    # ==================================================
    # SUBSCRIPTIONS TABLE
    # ==================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            subscription_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            plan TEXT NOT NULL,
            status TEXT NOT NULL,
            start_date TEXT NOT NULL,
            expiry_date TEXT NOT NULL,
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
        """
    )

    # ==================================================
    # PAYMENT DATA
    # ==================================================

    payments = [
        (
            "PAY1001",
            "successful",
            999,
            "INR",
            "Monthly subscription",
        ),
        (
            "PAY1002",
            "pending",
            499,
            "INR",
            "Subscription payment",
        ),
        (
            "PAY1003",
            "failed",
            799,
            "INR",
            "Subscription payment",
        ),
    ]

    for payment in payments:
        connection.execute(
            """
            INSERT OR IGNORE INTO payments (
                payment_id,
                status,
                amount,
                currency,
                description
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            payment,
        )

    # ==================================================
    # ORDER DATA
    # ==================================================

    orders = [
        (
            "ORD1001",
            "shipped",
            "20 September 2026",
        ),
        (
            "ORD1002",
            "processing",
            "22 September 2026",
        ),
        (
            "ORD1003",
            "delivered",
            "15 September 2026",
        ),
    ]

    for order in orders:
        connection.execute(
            """
            INSERT OR IGNORE INTO orders (
                order_id,
                status,
                estimated_delivery
            )
            VALUES (?, ?, ?)
            """,
            order,
        )

    # ==================================================
    # CUSTOMER DATA
    # ==================================================

    customers = [
        (
            "CUS1001",
            "Rahul Sharma",
            "rahul@example.com",
            "active",
        ),
        (
            "CUS1002",
            "Aman Verma",
            "aman@example.com",
            "active",
        ),
        (
            "CUS1003",
            "Priya Singh",
            "priya@example.com",
            "inactive",
        ),
    ]

    for customer in customers:
        connection.execute(
            """
            INSERT OR IGNORE INTO customers (
                customer_id,
                name,
                email,
                account_status
            )
            VALUES (?, ?, ?, ?)
            """,
            customer,
        )

    # ==================================================
    # SUBSCRIPTION DATA
    # ==================================================

    subscriptions = [
        (
            "SUB1001",
            "CUS1001",
            "Premium",
            "active",
            "01 September 2026",
            "30 September 2026",
        ),
        (
            "SUB1002",
            "CUS1002",
            "Basic",
            "active",
            "05 September 2026",
            "05 October 2026",
        ),
        (
            "SUB1003",
            "CUS1003",
            "Premium",
            "expired",
            "01 August 2026",
            "31 August 2026",
        ),
    ]

    for subscription in subscriptions:
        connection.execute(
            """
            INSERT OR IGNORE INTO subscriptions (
                subscription_id,
                customer_id,
                plan,
                status,
                start_date,
                expiry_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            subscription,
        )

    connection.commit()
    connection.close()


# ==================================================
# PAYMENT
# ==================================================

def get_payment(payment_id: str):
    connection = get_connection()

    payment = connection.execute(
        """
        SELECT
            payment_id,
            status,
            amount,
            currency,
            description
        FROM payments
        WHERE payment_id = ?
        """,
        (payment_id,),
    ).fetchone()

    connection.close()

    if payment is None:
        return None

    return dict(payment)


# ==================================================
# ORDER
# ==================================================

def get_order(order_id: str):
    connection = get_connection()

    order = connection.execute(
        """
        SELECT
            order_id,
            status,
            estimated_delivery
        FROM orders
        WHERE order_id = ?
        """,
        (order_id,),
    ).fetchone()

    connection.close()

    if order is None:
        return None

    return dict(order)


# ==================================================
# CREATE TICKET
# ==================================================

def create_ticket(
    customer_message: str,
    category: str = "general",
):
    connection = get_connection()

    last_ticket = connection.execute(
        """
        SELECT ticket_id
        FROM tickets
        ORDER BY rowid DESC
        LIMIT 1
        """
    ).fetchone()

    if last_ticket is None:
        ticket_id = "TICKET1001"
    else:
        last_id = int(
            last_ticket["ticket_id"].replace("TICKET", "")
        )
        ticket_id = f"TICKET{last_id + 1}"

    connection.execute(
        """
        INSERT INTO tickets (
            ticket_id,
            category,
            status,
            customer_message
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            ticket_id,
            category,
            "open",
            customer_message,
        ),
    )

    connection.commit()

    ticket = connection.execute(
        """
        SELECT
            ticket_id,
            category,
            status,
            customer_message
        FROM tickets
        WHERE ticket_id = ?
        """,
        (ticket_id,),
    ).fetchone()

    connection.close()

    return dict(ticket)


# ==================================================
# GET TICKET
# ==================================================

def get_ticket(ticket_id: str):
    connection = get_connection()

    ticket = connection.execute(
        """
        SELECT
            ticket_id,
            category,
            status,
            customer_message
        FROM tickets
        WHERE ticket_id = ?
        """,
        (ticket_id,),
    ).fetchone()

    connection.close()

    if ticket is None:
        return None

    return dict(ticket)


# ==================================================
# CUSTOMER
# ==================================================

def get_customer(customer_id: str):
    connection = get_connection()

    customer = connection.execute(
        """
        SELECT
            customer_id,
            name,
            email,
            account_status
        FROM customers
        WHERE customer_id = ?
        """,
        (customer_id,),
    ).fetchone()

    connection.close()

    if customer is None:
        return None

    return dict(customer)


# ==================================================
# SUBSCRIPTION
# ==================================================

def get_subscription(subscription_id: str):
    connection = get_connection()

    subscription = connection.execute(
        """
        SELECT
            subscription_id,
            customer_id,
            plan,
            status,
            start_date,
            expiry_date
        FROM subscriptions
        WHERE subscription_id = ?
        """,
        (subscription_id,),
    ).fetchone()

    connection.close()

    if subscription is None:
        return None

    return dict(subscription)