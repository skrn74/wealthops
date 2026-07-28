from database.database import db

class Portfolio(db.Model):

    __tablename__ = "portfolio"

    id = db.Column(db.Integer, primary_key=True)

    asset_name = db.Column(db.String(150), nullable=False)

    symbol = db.Column(db.String(50))

    isin = db.Column(db.String(30), unique=True)

    asset_type = db.Column(db.String(50), nullable=False)

    quantity = db.Column(db.Float, nullable=False)

    average_price = db.Column(db.Float, nullable=False)

    current_price = db.Column(db.Float, nullable=False)

    market_value = db.Column(db.Float, nullable=False)

    pnl = db.Column(db.Float, nullable=False)

    source = db.Column(db.String(50), default="Manual")

    def __repr__(self):
        return f"<Portfolio {self.asset_name}>"