from flask import Blueprint
from flask import jsonify

from services.dashboard_service import DashboardService

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/dashboard")
def dashboard_api():

    data = DashboardService.get_dashboard_data()

    return jsonify({

        "total_value": data["total_value"],

        "investment": data["investment"],

        "gain": data["gain"],

        "holdings": data["holdings"]

    })