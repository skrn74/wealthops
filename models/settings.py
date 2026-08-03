from database.database import db
from datetime import datetime

class Settings(db.Model):

    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)

    last_sync = db.Column(db.DateTime, default=datetime.utcnow)