from flask import Blueprint
from flask import render_template

goals_bp = Blueprint("goals", __name__)


@goals_bp.route("/goals")
def goals():

    goals = [
        {
            "name": "Dream House",
            "target": 12000000,
            "current": 1850000,
            "year": 2030
        },
        {
            "name": "Retirement",
            "target": 50000000,
            "current": 1850000,
            "year": 2041
        },
        {
            "name": "Daughter Education",
            "target": 5000000,
            "current": 600000,
            "year": 2039
        }
    ]

    return render_template(
        "goals.html",
        goals=goals
    )