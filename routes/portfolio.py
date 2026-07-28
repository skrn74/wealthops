from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect

from services.portfolio_service import PortfolioService

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("/portfolio", methods=["GET", "POST"])
def portfolio():

    if request.method == "POST":
        PortfolioService.create_asset(request.form)
        return redirect("/portfolio")

    portfolio = PortfolioService.get_all_assets()

    return render_template(
        "portfolio.html",
        portfolio=portfolio
    )


@portfolio_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if request.method == "POST":

        PortfolioService.update_asset(
            id,
            request.form
        )

        return redirect("/portfolio")

    holding = PortfolioService.get_asset(id)

    return render_template(
        "edit.html",
        holding=holding
    )


@portfolio_bp.route("/delete/<int:id>")
def delete(id):

    PortfolioService.delete_asset(id)

    return redirect("/portfolio")