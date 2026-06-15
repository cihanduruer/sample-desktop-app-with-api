"""
Order Management REST API (Flask).

==============================================================================
 TEACHING ARTIFACT - INTENTIONALLY BAD CODE
==============================================================================
This file is the "before" state for a GitHub Copilot modernization workshop.
It deliberately contains bugs, bad practices and security holes so that the
class can find and fix them. A non-exhaustive list of planted problems:

  * SQL injection (f-string / %-formatted SQL in several endpoints).
  * Plaintext password "authentication" + hard-coded admin backdoor.
  * Hard-coded secrets / API keys in source.
  * CORS wide open to "*".
  * debug=True and host 0.0.0.0 in production run.
  * N+1 query patterns and no pagination.
  * Bare `except:` blocks that swallow everything and still return HTTP 200.
  * No input validation, no typing, giant functions.
  * Blocking time.sleep() on a hot path to simulate a slow report.

DO NOT ship anything resembling this.
==============================================================================
"""

import time
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

import database

app = Flask(__name__)

# BAD: CORS open to every origin, every method, credentials allowed.
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# BAD: secrets committed to source control.
API_KEY = "supersecret-api-key-123"
ADMIN_BACKDOOR_PASSWORD = "admin"
JWT_SIGNING_KEY = "hunter2"  # not even used securely; just sitting here

database.init_db()


def db():
    return database.get_connection()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/login", methods=["POST"])
def login():
    # BAD: no validation; trusts whatever JSON arrives.
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")

    # BAD: SQL INJECTION. email/password are interpolated straight into the query.
    # Try: {"email": "' OR '1'='1", "password": "' OR '1'='1"}
    query = (
        "SELECT * FROM customers WHERE email = '%s' AND password = '%s'"
        % (email, password)
    )
    cur = db().cursor()
    try:
        cur.execute(query)
        row = cur.fetchone()
    except Exception:
        # BAD: swallow the error, pretend everything is fine.
        row = None

    # BAD: hard-coded backdoor that bypasses the database entirely.
    if password == ADMIN_BACKDOOR_PASSWORD:
        return jsonify({"token": "admin-" + API_KEY, "user": {"id": 0, "name": "Admin"}})

    if row:
        # BAD: token is just the API key with the user id glued on. Not a real token.
        return jsonify(
            {
                "token": API_KEY + "-" + str(row["id"]),
                "user": {"id": row["id"], "name": row["name"], "email": row["email"]},
            }
        )

    # BAD: returns HTTP 200 even on failure; client must inspect the body.
    return jsonify({"error": "invalid credentials"})


@app.route("/customers", methods=["GET"])
def list_customers():
    cur = db().cursor()
    # BAD: SELECT *, returns the plaintext password column to every caller.
    cur.execute("SELECT * FROM customers")
    rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/customers/<id>", methods=["GET"])
def get_customer(id):
    cur = db().cursor()
    # BAD: SQL injection again; `id` comes straight from the URL.
    cur.execute("SELECT * FROM customers WHERE id = " + id)
    row = cur.fetchone()
    if row:
        return jsonify(dict(row))
    return jsonify({"error": "not found"})


@app.route("/customers", methods=["POST"])
def create_customer():
    data = request.get_json(force=True, silent=True) or {}
    # BAD: no validation of name/email/password; password stored in plaintext.
    name = data.get("name")
    email = data.get("email")
    password = data.get("password", "changeme")
    cur = db().cursor()
    cur.execute(
        "INSERT INTO customers (name, email, password, created_at) VALUES (?, ?, ?, datetime('now'))",
        (name, email, password),
    )
    db().commit()
    return jsonify({"id": cur.lastrowid, "name": name, "email": email})


@app.route("/products", methods=["GET"])
def list_products():
    cur = db().cursor()
    cur.execute("SELECT * FROM products")
    return jsonify([dict(r) for r in cur.fetchall()])


@app.route("/products", methods=["POST"])
def create_product():
    data = request.get_json(force=True, silent=True) or {}
    # BAD: price/stock are not validated or coerced; negative prices are accepted.
    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock")
    cur = db().cursor()
    cur.execute(
        "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
        (name, price, stock),
    )
    db().commit()
    return jsonify({"id": cur.lastrowid})


@app.route("/orders", methods=["GET"])
def list_orders():
    # BAD: no pagination, returns every order ever created.
    cur = db().cursor()
    cur.execute("SELECT * FROM orders")
    orders = [dict(r) for r in cur.fetchall()]

    # BAD: classic N+1. For every order we run multiple extra queries.
    result = []
    for o in orders:
        c = db().cursor()
        c.execute("SELECT name FROM customers WHERE id = " + str(o["customer_id"]))
        cust = c.fetchone()
        o["customer_name"] = cust["name"] if cust else "Unknown"

        c.execute("SELECT * FROM order_items WHERE order_id = " + str(o["id"]))
        items = [dict(x) for x in c.fetchall()]

        # BAD: total recomputed in Python on every request with a manual loop.
        total = 0
        for it in items:
            total = total + (it["quantity"] * it["unit_price"])
        o["item_count"] = len(items)
        o["total"] = total
        result.append(o)

    return jsonify(result)


@app.route("/orders/<id>", methods=["GET"])
def get_order(id):
    cur = db().cursor()
    # BAD: f-string SQL injection.
    cur.execute(f"SELECT * FROM orders WHERE id = {id}")
    order = cur.fetchone()
    if not order:
        return jsonify({"error": "not found"})
    order = dict(order)

    cur.execute(f"SELECT * FROM order_items WHERE order_id = {id}")
    items = [dict(x) for x in cur.fetchall()]
    order["items"] = items
    total = 0
    for it in items:
        total += it["quantity"] * it["unit_price"]
    order["total"] = total
    return jsonify(order)


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json(force=True, silent=True) or {}
    customer_id = data.get("customer_id")
    items = data.get("items", [])

    cur = db().cursor()
    cur.execute(
        "INSERT INTO orders (customer_id, status, created_at) VALUES (?, 'NEW', datetime('now'))",
        (customer_id,),
    )
    order_id = cur.lastrowid

    # BAD: no transaction wrapping the whole thing; if one insert fails the order is
    # left half-written. Also does not check stock or decrement it.
    for it in items:
        product_id = it.get("product_id")
        qty = it.get("quantity", 1)
        c = db().cursor()
        c.execute("SELECT price FROM products WHERE id = " + str(product_id))
        p = c.fetchone()
        unit_price = p["price"] if p else 0
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
            (order_id, product_id, qty, unit_price),
        )

    db().commit()
    return jsonify({"id": order_id, "status": "NEW"})


@app.route("/orders/<id>/status", methods=["PUT"])
def update_status(id):
    data = request.get_json(force=True, silent=True) or {}
    status = data.get("status", "NEW")
    cur = db().cursor()
    # BAD: both id and status interpolated -> injectable. No allow-list of statuses.
    cur.execute(f"UPDATE orders SET status = '{status}' WHERE id = {id}")
    db().commit()
    return jsonify({"id": id, "status": status})


@app.route("/search", methods=["GET"])
def search():
    # BAD: textbook SQL injection through a query-string parameter.
    # Try: /search?q=' UNION SELECT id,name,email,password,created_at FROM customers --
    q = request.args.get("q", "")
    cur = db().cursor()
    sql = "SELECT * FROM customers WHERE name LIKE '%" + q + "%'"
    try:
        cur.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]
    except Exception:
        rows = []
    return jsonify(rows)


@app.route("/reports/revenue", methods=["GET"])
def revenue_report():
    # BAD: deliberately slow. Loads everything, sleeps, and does O(orders*items) work
    # in Python. This is the target for the dotnet-trace / profiling exercise on the
    # .NET side (the BFF calls this endpoint).
    cur = db().cursor()
    cur.execute("SELECT * FROM orders")
    orders = [dict(r) for r in cur.fetchall()]

    by_status = {}
    grand_total = 0.0
    for o in orders:
        # BAD: artificial latency per order.
        time.sleep(0.05)
        c = db().cursor()
        c.execute("SELECT * FROM order_items WHERE order_id = " + str(o["id"]))
        items = c.fetchall()
        order_total = 0.0
        for it in items:
            order_total += it["quantity"] * it["unit_price"]
        grand_total += order_total
        by_status[o["status"]] = by_status.get(o["status"], 0.0) + order_total

    return jsonify({"grand_total": grand_total, "by_status": by_status})


if __name__ == "__main__":
    # BAD: debug=True exposes the Werkzeug debugger (remote code execution) and
    # host 0.0.0.0 binds to every interface.
    app.run(host="0.0.0.0", port=5001, debug=True)
