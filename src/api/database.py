"""Database access: per-request connections, schema, and seed data.

Design notes (clean replacements for the original teaching artifact):
  * A connection is opened per request and stored on Flask's ``g``, then closed on
    teardown — no shared global connection across threads.
  * Foreign keys are enabled on every connection.
  * The schema declares NOT NULL/UNIQUE/CHECK constraints, foreign keys and indexes.
  * Passwords are stored hashed (never in plaintext).
"""
import sqlite3

from flask import Flask, current_app, g

from security import hash_password
from validation import VALID_ORDER_STATUSES


def get_db() -> sqlite3.Connection:
    """Return the request-scoped connection, opening one on first use."""
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE_PATH"])
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def close_db(_exception: BaseException | None = None) -> None:
    """Close the request-scoped connection if it was opened."""
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_app(app: Flask) -> None:
    """Register the teardown that closes the connection after each request."""
    app.teardown_appcontext(close_db)


_STATUS_ALLOW_LIST = ", ".join(f"'{status}'" for status in VALID_ORDER_STATUSES)

_SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS customers (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL,
        email         TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at    TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS products (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT NOT NULL,
        price REAL NOT NULL CHECK (price >= 0),
        stock INTEGER NOT NULL CHECK (stock >= 0)
    )
    """,
    f"""
    CREATE TABLE IF NOT EXISTS orders (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES customers(id),
        status      TEXT NOT NULL CHECK (status IN ({_STATUS_ALLOW_LIST})),
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS order_items (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id   INTEGER NOT NULL REFERENCES orders(id),
        product_id INTEGER NOT NULL REFERENCES products(id),
        quantity   INTEGER NOT NULL CHECK (quantity > 0),
        unit_price REAL NOT NULL CHECK (unit_price >= 0)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id)",
    "CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)",
    "CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id)",
)


def init_schema() -> None:
    """Create tables, constraints and indexes if they do not yet exist."""
    connection = get_db()
    with connection:
        for statement in _SCHEMA_STATEMENTS:
            connection.execute(statement)


def seed_if_empty() -> None:
    """Insert demo data on a fresh database only."""
    connection = get_db()
    already_seeded = connection.execute(
        "SELECT COUNT(*) AS count FROM customers"
    ).fetchone()["count"]
    if already_seeded:
        return

    with connection:
        _seed(connection)


def _seed(connection: sqlite3.Connection) -> None:
    customers = [
        ("Alice Johnson", "alice@example.com", "password123"),
        ("Bob Smith", "bob@example.com", "qwerty"),
        ("Carol Diaz", "carol@example.com", "letmein"),
        ("Admin", "admin@example.com", "admin"),
    ]
    for name, email, plaintext_password in customers:
        connection.execute(
            "INSERT INTO customers (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, hash_password(plaintext_password)),
        )

    products = [
        ("Mechanical Keyboard", 79.99, 50),
        ("Wireless Mouse", 29.50, 120),
        ('27" Monitor', 219.00, 30),
        ("USB-C Hub", 39.95, 75),
        ("Laptop Stand", 24.25, 0),
        ("Noise Cancelling Headphones", 149.99, 18),
    ]
    for name, price, stock in products:
        connection.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            (name, price, stock),
        )

    orders = [
        (1, "NEW"),
        (1, "SHIPPED"),
        (2, "PROCESSING"),
        (3, "DELIVERED"),
        (2, "CANCELLED"),
    ]
    for customer_id, status in orders:
        connection.execute(
            "INSERT INTO orders (customer_id, status) VALUES (?, ?)",
            (customer_id, status),
        )

    order_items = [
        (1, 1, 1, 79.99),
        (1, 2, 2, 29.50),
        (2, 3, 1, 219.00),
        (3, 4, 3, 39.95),
        (3, 6, 1, 149.99),
        (4, 2, 1, 29.50),
        (5, 1, 5, 79.99),
    ]
    for order_id, product_id, quantity, unit_price in order_items:
        connection.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) "
            "VALUES (?, ?, ?, ?)",
            (order_id, product_id, quantity, unit_price),
        )
