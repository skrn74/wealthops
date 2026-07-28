from flask import Flask, render_template
from database.database import db
from flask import request, redirect
from flask import Flask, render_template, request, redirect, jsonify
from models.portfolio import Portfolio
from routes.dashboard import dashboard_bp
from routes.portfolio import portfolio_bp
from routes.goals import goals_bp
from models.transaction import Transaction
from routes.api import api_bp
from routes.ai import ai_bp
from routes.upstox import upstox_bp

app = Flask(__name__)
app.config.from_object("config")

db.init_app(app)

with app.app_context():

    db.create_all()

app.register_blueprint(dashboard_bp)
app.register_blueprint(portfolio_bp)
app.register_blueprint(goals_bp)
app.register_blueprint(api_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(upstox_bp)

from config import UPSTOX_CLIENT_ID

print("Client ID:", UPSTOX_CLIENT_ID)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )