"""Reporting endpoints."""
from flask import Blueprint, jsonify

import repositories
from database import get_db

reports_bp = Blueprint("reports", __name__)


@reports_bp.get("/reports/revenue")
def revenue_report():
    return jsonify(repositories.revenue_report(get_db()))
