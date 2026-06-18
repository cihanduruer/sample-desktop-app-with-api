"""Order Management REST API (Flask).

A small, modular Flask application:

  * ``config``       — environment-driven configuration (no hard-coded secrets).
  * ``database``     — per-request connections, schema with constraints, seed.
  * ``security``     — password hashing and opaque tokens.
  * ``validation``   — input validators and the ``ApiError`` type.
  * ``repositories`` — parameterized data access (no SQL injection, no N+1).
  * ``*_api``        — thin blueprints, one per resource.

Run locally with ``python app.py``. Runtime settings come from ``ORDER_API_*``
environment variables (see ``config.py``).
"""
from werkzeug.exceptions import HTTPException

from flask import Flask, jsonify
from flask_cors import CORS

import database
from auth_api import auth_bp
from config import Config
from customers_api import customers_bp
from orders_api import orders_bp
from products_api import products_bp
from reports_api import reports_bp
from validation import ApiError


def create_app(config: Config | None = None) -> Flask:
    config = config or Config.from_env()

    app = Flask(__name__)
    app.secret_key = config.secret_key
    app.config["DATABASE_PATH"] = config.database_path
    app.config["DEFAULT_PAGE_SIZE"] = config.default_page_size
    app.config["MAX_PAGE_SIZE"] = config.max_page_size

    # CORS limited to known origins (not "*").
    CORS(app, resources={r"/*": {"origins": config.cors_origins}})

    database.init_app(app)
    with app.app_context():
        database.init_schema()
        database.seed_if_empty()

    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reports_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    _register_error_handlers(app)
    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        # Log the real cause server-side; never leak internals to the client.
        app.logger.exception("Unhandled error: %s", error)
        return jsonify({"error": "internal server error"}), 500


def main() -> None:
    config = Config.from_env()
    app = create_app(config)
    app.run(host=config.host, port=config.port, debug=config.debug)


# Module-level app for WSGI servers (e.g. ``waitress-serve app:app``).
app = create_app()


if __name__ == "__main__":
    main()
