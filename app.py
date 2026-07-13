from flask import Flask, render_template

from database.database import db
from flask import request, redirect

app = Flask(__name__)

app.config.from_object("config")

db.init_app(app)

from models.portfolio import Portfolio

with app.app_context():

    db.create_all()

@app.route("/")
def dashboard():

    portfolio = Portfolio.query.all()

    total_value = sum(
        p.quantity * p.current_price for p in portfolio
    )

    mf_value = sum(
        p.quantity * p.current_price
        for p in portfolio
        if p.asset_type == "Mutual Fund"
    )

    stock_value = sum(
        p.quantity * p.current_price
        for p in portfolio
        if p.asset_type == "Stock"
    )

    return render_template(
        "dashboard.html",
        portfolio=portfolio,
        total_value=round(total_value, 2),
        mf_value=round(mf_value, 2),
        stock_value=round(stock_value, 2)
    )

@app.route("/portfolio", methods=["GET", "POST"])
def portfolio():

    if request.method == "POST":

        portfolio = Portfolio(

            asset_name=request.form["asset_name"],

            asset_type=request.form["asset_type"],

            quantity=float(request.form["quantity"]),

            average_price=float(request.form["average_price"]),

            current_price=float(request.form["current_price"])

        )

        db.session.add(portfolio)

        db.session.commit()

        return redirect("/portfolio")

    portfolio = Portfolio.query.all()

    return render_template(
        "portfolio.html",
        portfolio=portfolio
    )

@app.route("/goals")
def goals():
    return render_template("goals.html")

@app.route("/ai")
def ai():
    return "<h2>AI Advisor Coming Soon 🤖</h2>"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )