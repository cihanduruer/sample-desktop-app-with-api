"""Data-access functions for the API.

Every query is parameterized (no string-built SQL). List queries support pagination,
and the order/report queries use a single JOIN/GROUP BY instead of N+1 loops.
"""
import sqlite3

from validation import ApiError


# ----------------------------------------------------------------------------
# Customers
# ----------------------------------------------------------------------------
def list_customers(connection: sqlite3.Connection, limit: int, offset: int) -> list[dict]:
    rows = connection.execute(
        "SELECT id, name, email, created_at FROM customers "
        "ORDER BY id LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    return [dict(row) for row in rows]


def get_customer(connection: sqlite3.Connection, customer_id: int) -> dict | None:
    row = connection.execute(
        "SELECT id, name, email, created_at FROM customers WHERE id = ?",
        (customer_id,),
    ).fetchone()
    return dict(row) if row else None


def find_customer_for_login(connection: sqlite3.Connection, email: str) -> dict | None:
    row = connection.execute(
        "SELECT id, name, email, password_hash FROM customers WHERE email = ?",
        (email,),
    ).fetchone()
    return dict(row) if row else None


def create_customer(
    connection: sqlite3.Connection, name: str, email: str, password_hash: str
) -> int:
    with connection:
        cursor = connection.execute(
            "INSERT INTO customers (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
    return cursor.lastrowid


# ----------------------------------------------------------------------------
# Products
# ----------------------------------------------------------------------------
def list_products(connection: sqlite3.Connection, limit: int, offset: int) -> list[dict]:
    rows = connection.execute(
        "SELECT id, name, price, stock FROM products ORDER BY id LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    return [dict(row) for row in rows]


def create_product(
    connection: sqlite3.Connection, name: str, price: float, stock: int
) -> int:
    with connection:
        cursor = connection.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            (name, price, stock),
        )
    return cursor.lastrowid


# ----------------------------------------------------------------------------
# Orders
# ----------------------------------------------------------------------------
def list_orders(connection: sqlite3.Connection, limit: int, offset: int) -> list[dict]:
    rows = connection.execute(
        """
        SELECT o.id,
               o.customer_id,
               o.status,
               o.created_at,
               c.name AS customer_name,
               COUNT(oi.id) AS item_count,
               COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total
        FROM orders o
        LEFT JOIN customers c ON c.id = o.customer_id
        LEFT JOIN order_items oi ON oi.order_id = o.id
        GROUP BY o.id, o.customer_id, o.status, o.created_at, c.name
        ORDER BY o.id
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    ).fetchall()

    orders = []
    for row in rows:
        order = dict(row)
        order["customer_name"] = order["customer_name"] or "Unknown"
        order["total"] = round(order["total"], 2)
        orders.append(order)
    return orders


def get_order(connection: sqlite3.Connection, order_id: int) -> dict | None:
    order_row = connection.execute(
        "SELECT id, customer_id, status, created_at FROM orders WHERE id = ?",
        (order_id,),
    ).fetchone()
    if order_row is None:
        return None

    item_rows = connection.execute(
        "SELECT id, order_id, product_id, quantity, unit_price "
        "FROM order_items WHERE order_id = ?",
        (order_id,),
    ).fetchall()
    items = [dict(item) for item in item_rows]

    order = dict(order_row)
    order["items"] = items
    order["total"] = round(
        sum(item["quantity"] * item["unit_price"] for item in items), 2
    )
    return order


def create_order(
    connection: sqlite3.Connection, customer_id: int, items: list[dict]
) -> int:
    """Create an order and its items atomically, decrementing product stock.

    The whole operation runs in a single transaction: any failure (unknown
    customer/product, insufficient stock) rolls everything back.
    """
    with connection:
        if _customer_exists(connection, customer_id) is False:
            raise ApiError("customer not found", 404)

        cursor = connection.execute(
            "INSERT INTO orders (customer_id, status) VALUES (?, 'NEW')",
            (customer_id,),
        )
        order_id = cursor.lastrowid

        for item in items:
            product = connection.execute(
                "SELECT id, price, stock FROM products WHERE id = ?",
                (item["product_id"],),
            ).fetchone()
            if product is None:
                raise ApiError(f"product {item['product_id']} not found", 404)
            if product["stock"] < item["quantity"]:
                raise ApiError(
                    f"insufficient stock for product {item['product_id']}", 409
                )

            connection.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) "
                "VALUES (?, ?, ?, ?)",
                (order_id, item["product_id"], item["quantity"], product["price"]),
            )
            connection.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (item["quantity"], item["product_id"]),
            )

    return order_id


def update_order_status(
    connection: sqlite3.Connection, order_id: int, status: str
) -> None:
    with connection:
        cursor = connection.execute(
            "UPDATE orders SET status = ? WHERE id = ?", (status, order_id)
        )
        if cursor.rowcount == 0:
            raise ApiError("order not found", 404)


def _customer_exists(connection: sqlite3.Connection, customer_id: int) -> bool:
    row = connection.execute(
        "SELECT 1 FROM customers WHERE id = ?", (customer_id,)
    ).fetchone()
    return row is not None


# ----------------------------------------------------------------------------
# Reports
# ----------------------------------------------------------------------------
def revenue_report(connection: sqlite3.Connection) -> dict:
    rows = connection.execute(
        """
        SELECT o.status AS status,
               COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total
        FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.id
        GROUP BY o.status
        """
    ).fetchall()

    by_status = {row["status"]: round(row["total"], 2) for row in rows}
    grand_total = round(sum(by_status.values()), 2)
    return {"grand_total": grand_total, "by_status": by_status}
