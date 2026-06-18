"""Order endpoints."""
from flask import Blueprint, current_app, jsonify, request

import repositories
from database import get_db
from validation import (
    ApiError,
    parse_pagination,
    require_int,
    require_json_object,
    require_status,
    require_string,
    validate_order_items,
)

orders_bp = Blueprint("orders", __name__)


@orders_bp.get("/orders")
def list_orders():
    _, page_size, offset = parse_pagination(
        request.args,
        current_app.config["DEFAULT_PAGE_SIZE"],
        current_app.config["MAX_PAGE_SIZE"],
    )
    return jsonify(repositories.list_orders(get_db(), page_size, offset))


@orders_bp.get("/orders/<int:order_id>")
def get_order(order_id: int):
    order = repositories.get_order(get_db(), order_id)
    if order is None:
        raise ApiError("order not found", 404)
    return jsonify(order)


@orders_bp.post("/orders")
def create_order():
    payload = require_json_object(request.get_json(silent=True))
    customer_id = require_int(payload, "customer_id", minimum=1)
    items = validate_order_items(payload.get("items"))

    order_id = repositories.create_order(get_db(), customer_id, items)
    return jsonify({"id": order_id, "status": "NEW"}), 201


@orders_bp.put("/orders/<int:order_id>/status")
def update_status(order_id: int):
    payload = require_json_object(request.get_json(silent=True))
    status = require_status(require_string(payload, "status"))

    repositories.update_order_status(get_db(), order_id, status)
    return jsonify({"id": order_id, "status": status})
