"""Product endpoints."""
from flask import Blueprint, current_app, jsonify, request

import repositories
from database import get_db
from validation import (
    parse_pagination,
    require_int,
    require_json_object,
    require_number,
    require_string,
)

products_bp = Blueprint("products", __name__)


@products_bp.get("/products")
def list_products():
    _, page_size, offset = parse_pagination(
        request.args,
        current_app.config["DEFAULT_PAGE_SIZE"],
        current_app.config["MAX_PAGE_SIZE"],
    )
    return jsonify(repositories.list_products(get_db(), page_size, offset))


@products_bp.post("/products")
def create_product():
    payload = require_json_object(request.get_json(silent=True))
    name = require_string(payload, "name")
    price = require_number(payload, "price", minimum=0)
    stock = require_int(payload, "stock", minimum=0)

    product_id = repositories.create_product(get_db(), name, price, stock)
    return jsonify({"id": product_id, "name": name, "price": price, "stock": stock}), 201
