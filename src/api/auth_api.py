"""Authentication endpoints."""
from flask import Blueprint, jsonify, request

import repositories
from database import get_db
from security import generate_token, verify_password
from validation import require_email, require_json_object, require_string

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    payload = require_json_object(request.get_json(silent=True))
    email = require_email(payload)
    password = require_string(payload, "password")

    customer = repositories.find_customer_for_login(get_db(), email)
    if customer is None or not verify_password(customer["password_hash"], password):
        return jsonify({"error": "invalid credentials"}), 401

    return jsonify(
        {
            "token": generate_token(),
            "user": {
                "id": customer["id"],
                "name": customer["name"],
                "email": customer["email"],
            },
        }
    )
