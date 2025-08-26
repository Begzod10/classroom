from backend.models.basic_model import *


class Hours(db.Model):
    __tablename__ = "hours"
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    name = db.Column(db.String(255))
    order = db.Column(db.Integer)


class WeekDays(db.Model):
    __tablename__ = "weekdays"
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(255))
    name_uz = db.Column(db.String(255))
    order = db.Column(db.Integer)


class ClassTimeTable(db.Model):
    __tablename__ = "class_time_table"
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    week_id = db.Column(db.Integer, db.ForeignKey("weekdays.id"))
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"))
    hours_id = db.Column(db.Integer, db.ForeignKey("hours.id"))
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"))
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"))
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))
    date = db.Column(db.Date)
