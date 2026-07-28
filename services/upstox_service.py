import requests

from config import (
    UPSTOX_CLIENT_ID,
    UPSTOX_CLIENT_SECRET,
    UPSTOX_REDIRECT_URI
)


class UpstoxService:

    @staticmethod
    def get_access_token(code):

        url = "https://api.upstox.com/v2/login/authorization/token"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        payload = {
            "code": code,
            "client_id": UPSTOX_CLIENT_ID,
            "client_secret": UPSTOX_CLIENT_SECRET,
            "redirect_uri": UPSTOX_REDIRECT_URI,
            "grant_type": "authorization_code"
        }

        response = requests.post(
            url,
            headers=headers,
            data=payload
        )

        return response.json()

    # Existing get_access_token()

    @staticmethod
    def get_holdings(access_token):

        url = "https://api.upstox.com/v2/portfolio/long-term-holdings"

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(
            url,
            headers=headers
        )

        return response.json()