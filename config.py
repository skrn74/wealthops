import os
from dotenv import load_dotenv

load_dotenv()
SQLALCHEMY_DATABASE_URI = "postgresql://wealthuser:wealth123@postgres:5432/wealthops"

SQLALCHEMY_TRACK_MODIFICATIONS = False

UPSTOX_CLIENT_ID =  os.getenv("UPSTOX_CLIENT_ID")
UPSTOX_CLIENT_SECRET = os.getenv("UPSTOX_CLIENT_SECRET")
UPSTOX_REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI")

UPSTOX_BASE_URL = os.getenv("UPSTOX_BASE_URL")