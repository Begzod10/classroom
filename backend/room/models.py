from backend.models.basic_model import *


class Room(db.Model):
    __tablename__ = "room"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    seats_number = db.Column(db.BigInteger)
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"))
    electronic_board = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean, default=False)
    old_id = db.Column(db.Integer, unique=True)
    turon_old_id = db.Column(db.Integer, unique=True)
    turon_id = db.Column(db.Integer, unique=True, nullable=True)
    order = db.Column(db.Integer, unique=True, nullable=True)
