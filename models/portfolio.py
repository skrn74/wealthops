from database.database import db

class Portfolio(db.Model):

    __tablename__ = "portfolio"

    id = db.Column(db.Integer, primary_key=True)

    asset_name = db.Column(db.String(100), nullable=False)

    asset_type = db.Column(db.String(50), nullable=False)

    quantity = db.Column(db.Float, nullable=False)

    average_price = db.Column(db.Float, nullable=False)

    current_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return self.asset_name