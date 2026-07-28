from flask import Blueprint
from flask import render_template

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/ai")
def ai():

    return render_template("ai.html")