from backend.models.basic_model import *


class Branch(db.Model):
    __tablename__ = "branch"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    number = db.Column(db.String(255), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), nullable=True)  # Location bilan FK
    location_text = db.Column(db.String(255), nullable=True)
    map_link = db.Column(db.String(255), nullable=True)
    code = db.Column(db.Integer, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    director_fio = db.Column(db.String(255), nullable=True)
    location_type = db.Column(db.String(255), nullable=True)
    district = db.Column(db.String(255), nullable=True)
    bank_sheet = db.Column(db.String(255), nullable=True)
    inn = db.Column(db.String(255), nullable=True)
    bank = db.Column(db.String(255), nullable=True)
    mfo = db.Column(db.String(50), nullable=True)
    campus_name = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Date, nullable=True)
    old_id = db.Column(db.Integer, unique=True, nullable=True)
    turon_id = db.Column(db.Integer, unique=True, nullable=True)
