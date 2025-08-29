from backend.models.basic_model import *


class Hours(db.Model):
    __tablename__ = "hours"
    id = db.Column(db.Integer, primary_key=True)
    turon_id = db.Column(db.Integer, unique=True, nullable=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    name = db.Column(db.String(255))
    order = db.Column(db.Integer)


class WeekDays(db.Model):
    __tablename__ = "weekdays"
    id = db.Column(db.Integer, primary_key=True)
    turon_id = db.Column(db.Integer, unique=True, nullable=True)
    name_en = db.Column(db.String(255))
    name_uz = db.Column(db.String(255))
    order = db.Column(db.Integer)


student_timetable = db.Table(
    "student_timetable",
    db.Column("student_id", db.Integer, db.ForeignKey("student.id"), primary_key=True),
    db.Column("timetable_id", db.Integer, db.ForeignKey("class_time_table.id"), primary_key=True)
)


class ClassTimeTable(db.Model):
    __tablename__ = "class_time_table"
    id = db.Column(db.Integer, primary_key=True)
    turon_id = db.Column(db.Integer, unique=True, nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    week_id = db.Column(db.Integer, db.ForeignKey("weekdays.id"))
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"))
    hours_id = db.Column(db.Integer, db.ForeignKey("hours.id"))
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"))
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"))
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))
    flow_id = db.Column(db.Integer, db.ForeignKey("flow.id"))
    date = db.Column(db.Date)

    group = db.relationship("Group", backref="timetables")
    flow = db.relationship("Flow", backref="timetables")
    teacher = db.relationship("Teacher", backref="timetables")
    subject = db.relationship("Subject", backref="timetables")
    hours = db.relationship("Hours", backref="timetables")
    room = db.relationship("Room", backref="timetables")
    week_day = db.relationship("WeekDays", backref="timetables")
    branch = db.relationship("Branch", backref="timetables")

    students = db.relationship(
        "Student",
        secondary=student_timetable,
        backref=db.backref("class_time_tables", lazy="dynamic"),
        cascade="all, delete"
    )
