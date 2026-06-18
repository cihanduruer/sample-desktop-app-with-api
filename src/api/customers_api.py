"""Customer endpoints."""
from flask import Blueprint, current_app, jsonify, request

import repositories
from database import get_db
from security import hash_password
from validation import (
    ApiError,
    parse_pagination,
    require_email,
    require_json_object,
    require_string,
)

customers_bp = Blueprint("customers", __name__)


@customers_bp.get("/customers")
def list_customers():
    _, page_size, offset = parse_pagination(
        request.args,
        current_app.config["DEFAULT_PAGE_SIZE"],
        current_app.config["MAX_PAGE_SIZE"],
    )
    return jsonify(repositories.list_customers(get_db(), page_size, offset))


@customers_bp.get("/customers/<int:customer_id>")
def get_customer(customer_id: int):
    customer = repositories.get_customer(get_db(), customer_id)
    if customer is None:
        raise ApiError("customer not found", 404)
    return jsonify(customer)


@customers_bp.post("/customers")
def create_customer():
    payload = require_json_object(request.get_json(silent=True))
    name = require_string(payload, "name")
    email = require_email(payload)
    password = require_string(payload, "password")

    connection = get_db()
    if repositories.find_customer_for_login(connection, email) is not None:
        raise ApiError("a customer with this email already exists", 409)

    customer_id = repositories.create_customer(
        connection, name, email, hash_password(password)
    )
    return jsonify({"id": customer_id, "name": name, "email": email}), 201
