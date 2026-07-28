from flask import Blueprint
from flask import redirect
from flask import request
from services.upstox_service import UpstoxService
from services.portfolio_service import PortfolioService
from pprint import pprint

from config import (
    UPSTOX_CLIENT_ID,
    UPSTOX_REDIRECT_URI
)

upstox_bp = Blueprint("upstox", __name__)


@upstox_bp.route("/upstox/login")
def login():

    auth_url = (
        "https://api.upstox.com/v2/login/authorization/dialog"
        f"?response_type=code"
        f"&client_id={UPSTOX_CLIENT_ID}"
        f"&redirect_uri={UPSTOX_REDIRECT_URI}"
    )

    return redirect(auth_url)


@upstox_bp.route("/upstox/callback")
def callback():

    code = request.args.get("code")

    token_response = UpstoxService.get_access_token(code)

    access_token = token_response["access_token"]

    holdings = UpstoxService.get_holdings(access_token)
    PortfolioService.sync_holdings(
    holdings["data"]
    )

    return redirect("/")
