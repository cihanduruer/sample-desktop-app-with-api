"""
Database bootstrap + seed for the Order Management API.

NOTE (for the modernization workshop):
This module is intentionally written with bad practices. It is a teaching artifact.
Problems planted here on purpose:
  * Passwords are stored in PLAINTEXT.
  * The schema has no foreign keys / constraints / indexes.
  * Seed runs every process start and silently ignores errors.
  * A single global connection is shared across threads (not thread-safe).
Do not copy this into a real system.
"""

import os
import sqlite3

# BAD: database file path is hard-coded relative to the current working directory.
DB_PATH = os.path.join(os.path.dirname(__file__), "orders.db")

# BAD: one global connection, reused everywhere, check_same_thread disabled so Flask
# can use it from multiple threads. This is a classic source of corruption / locking bugs.
_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.row_factory = sqlite3.Row


def get_connection():
    # BAD: returns the shared global connection instead of a per-request connection.
    return _conn


def init_db():
    cur = _conn.cursor()

    # BAD: no constraints, no foreign keys, prices stored as REAL (floating point money).
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            stock INTEGER
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            status TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price REAL
        );
        """
    )
    _conn.commit()
    _seed()


def _seed():
    cur = _conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM customers")
    if cur.fetchone()["c"] > 0:
        return

    # BAD: plaintext passwords, and the "admin" password is trivially guessable.
    customers = [
        ("Alice Johnson", "alice@example.com", "password123"),
        ("Bob Smith", "bob@example.com", "qwerty"),
        ("Carol Diaz", "carol@example.com", "letmein"),
        ("Admin", "admin@example.com", "admin"),
    ]
    for name, email, pwd in customers:
        cur.execute(
            "INSERT INTO customers (name, email, password, created_at) VALUES (?, ?, ?, datetime('now'))",
            (name, email, pwd),
        )

    products = [
        ("Mechanical Keyboard", 79.99, 50),
        ("Wireless Mouse", 29.50, 120),
        ("27\" Monitor", 219.00, 30),
        ("USB-C Hub", 39.95, 75),
        ("Laptop Stand", 24.25, 0),  # out of stock on purpose
        ("Noise Cancelling Headphones", 149.99, 18),
    ]
    for name, price, stock in products:
        cur.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            (name, price, stock),
        )

    # A few orders so reports have something to chew on.
    orders = [
        (1, "NEW"),
        (1, "SHIPPED"),
        (2, "PROCESSING"),
        (3, "DELIVERED"),
        (2, "CANCELLED"),
    ]
    for customer_id, status in orders:
        cur.execute(
            "INSERT INTO orders (customer_id, status, created_at) VALUES (?, ?, datetime('now'))",
            (customer_id, status),
        )

    items = [
        (1, 1, 1, 79.99),
        (1, 2, 2, 29.50),
        (2, 3, 1, 219.00),
        (3, 4, 3, 39.95),
        (3, 6, 1, 149.99),
        (4, 2, 1, 29.50),
        (5, 1, 5, 79.99),
    ]
    for order_id, product_id, qty, unit_price in items:
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
            (order_id, product_id, qty, unit_price),
        )

    _conn.commit()
