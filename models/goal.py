from database.database import db


class Goal(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    target_amount = db.Column(db.Float, nullable=False)

    current_amount = db.Column(db.Float, default=0)

    target_year = db.Column(db.Integer)

    description = db.Column(db.String(200))