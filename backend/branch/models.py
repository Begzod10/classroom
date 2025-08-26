from backend.models.basic_model import *



class Branch(db.Model):
    __tablename__ = "branch"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    number = db.Column(db.String(255))
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), nullable=True)  # Location bilan FK
    location_text = db.Column(db.String(255))
    map_link = db.Column(db.String(255))
    code = db.Column(db.Integer)
    phone_number = db.Column(db.String(20))
    director_fio = db.Column(db.String(255))
    location_type = db.Column(db.String(255))
    district = db.Column(db.String(255))
    bank_sheet = db.Column(db.String(255))
    inn = db.Column(db.String(255))
    bank = db.Column(db.String(255))
    mfo = db.Column(db.String(50))
    campus_name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    year = db.Column(db.Date)
    old_id = db.Column(db.Integer, unique=True)
