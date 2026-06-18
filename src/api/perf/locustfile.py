"""Locust performance tests for the Order Management API.

Run against a live instance of the Python API (default http://localhost:5001).

Quick start (from ``src/api``)::

    .\\.venv\\Scripts\\python.exe -m pip install -r perf\\requirements.txt
    # Terminal 1 — start the API
    .\\.venv\\Scripts\\python.exe app.py
    # Terminal 2 — headless load test: 50 users, spawn 10/s, run 1 minute
    .\\.venv\\Scripts\\locust -f perf\\locustfile.py --host http://localhost:5001 \\
        --headless -u 50 -r 10 -t 1m --csv perf\\results

Or open the web UI (omit ``--headless``) at http://localhost:8089.

The task weights model a read-heavy API: browsing orders/products/customers and the
revenue report dominate, with occasional writes (login, create customer/product/order,
status update). Endpoints and payloads match the current API contract.
"""
from __future__ import annotations

import random
import uuid

from locust import HttpUser, between, task

# Seed data created by ``database.seed_if_empty`` on a fresh database.
SEEDED_CUSTOMER = {"email": "alice@example.com", "password": "password123"}
SEEDED_PRODUCT_IDS = [1, 2, 3, 4, 6]  # product 5 is intentionally out of stock
SEEDED_ORDER_IDS = [1, 2, 3, 4, 5]
ORDER_STATUSES = ["NEW", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]


def _unique_email() -> str:
    return f"perf-{uuid.uuid4().hex[:12]}@example.com"


class OrderManagementUser(HttpUser):
    """Simulated client exercising the public API endpoints."""

    # Realistic think time between requests.
    wait_time = between(0.5, 2.0)

    # ----------------------------------------------------------------- reads
    @task(10)
    def list_orders(self) -> None:
        self.client.get("/orders?page=1&page_size=50", name="GET /orders")

    @task(6)
    def get_order(self) -> None:
        order_id = random.choice(SEEDED_ORDER_IDS)
        self.client.get(f"/orders/{order_id}", name="GET /orders/[id]")

    @task(6)
    def list_products(self) -> None:
        self.client.get("/products?page=1&page_size=50", name="GET /products")

    @task(4)
    def list_customers(self) -> None:
        self.client.get("/customers?page=1&page_size=50", name="GET /customers")

    @task(4)
    def revenue_report(self) -> None:
        self.client.get("/reports/revenue", name="GET /reports/revenue")

    @task(2)
    def health(self) -> None:
        self.client.get("/health", name="GET /health")

    # ---------------------------------------------------------------- writes
    @task(3)
    def login(self) -> None:
        with self.client.post(
            "/login",
            json=SEEDED_CUSTOMER,
            name="POST /login",
            catch_response=True,
        ) as response:
            if response.status_code == 200 and "token" in response.text:
                response.success()
            else:
                response.failure(f"login failed: {response.status_code}")

    @task(1)
    def create_customer(self) -> None:
        payload = {
            "name": "Perf Tester",
            "email": _unique_email(),
            "password": "s3cret-pw",
        }
        with self.client.post(
            "/customers", json=payload, name="POST /customers", catch_response=True
        ) as response:
            # 201 created, or 409 if the random email happens to collide.
            if response.status_code in (201, 409):
                response.success()
            else:
                response.failure(f"unexpected status: {response.status_code}")

    @task(1)
    def create_product(self) -> None:
        payload = {
            "name": f"Perf Widget {uuid.uuid4().hex[:6]}",
            "price": round(random.uniform(5, 500), 2),
            "stock": random.randint(1, 100),
        }
        self.client.post("/products", json=payload, name="POST /products")

    @task(1)
    def create_order(self) -> None:
        payload = {
            "customer_id": 1,
            "items": [
                {"product_id": random.choice(SEEDED_PRODUCT_IDS), "quantity": 1}
            ],
        }
        with self.client.post(
            "/orders", json=payload, name="POST /orders", catch_response=True
        ) as response:
            # 201 created, or 409 if stock ran out during the run.
            if response.status_code in (201, 409):
                response.success()
            else:
                response.failure(f"unexpected status: {response.status_code}")

    @task(1)
    def update_order_status(self) -> None:
        order_id = random.choice(SEEDED_ORDER_IDS)
        payload = {"status": random.choice(ORDER_STATUSES)}
        self.client.put(
            f"/orders/{order_id}/status",
            json=payload,
            name="PUT /orders/[id]/status",
        )
