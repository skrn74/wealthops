from database.database import db
from datetime import datetime


class Transaction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    asset_name = db.Column(db.String(100), nullable=False)

    transaction_type = db.Column(db.String(10))   # BUY / SELL

    quantity = db.Column(db.Float)

    price = db.Column(db.Float)

    transaction_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )