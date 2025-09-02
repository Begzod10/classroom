from flask import Blueprint, request, jsonify
from datetime import date, datetime, timedelta

from backend.flow.models import Flow
from backend.time_table.sync_service import sync_branches, sync_rooms, sync_weekdays, sync_timetable, sync_hours

from backend.room.models import Room
from backend.branch.models import Branch
from backend.time_table.models import Hours, ClassTimeTable, WeekDays, student_timetable
from backend.models.basic_model import Group, Teacher, Subject, Student, db

crud_timetable_bp = Blueprint("timetable_crud", __name__)


@crud_timetable_bp.route("/timetable-list-delete/<int:pk>", methods=["DELETE"])
def class_time_table_detail_delete(pk):
    class_time_table = ClassTimeTable.query.filter_by(turon_id=pk).first()
    if not class_time_table:
        return jsonify({"error": "Dars topilmadi"}), 404

    if request.method == "DELETE":
        db.session.execute(
            student_timetable.delete().where(
                student_timetable.c.timetable_id == class_time_table.id
            )
        )
        db.session.commit()

        db.session.delete(class_time_table)
        db.session.commit()
        return jsonify({"msg": "Dars muvaffaqiyatli o'chirildi"}), 200


@crud_timetable_bp.route('/timetable-update/<int:id>', methods=['PATCH'])
def timetable_update(id):
    instance = ClassTimeTable.query.filter_by(turon_id=id).first()

    data = request.get_json()
    if "room_id" in data:
        room = Room.query.filter_by(turon_id=data["room_id"]).first()
        instance.room_id = room.id
    if "hours_id" in data:
        hours = Hours.query.filter_by(turon_id=data["hours_id"]).first()
        instance.hours_id = hours.id

    db.session.commit()
    return {"msg": "Yangilandi"}


@crud_timetable_bp.route('/timetable-list-update/<int:pk>', methods=['PUT', 'PATCH'])
def update_timetable(pk):
    timetable = ClassTimeTable.query.filter_by(turon_id=pk).first()
    if not timetable:
        return jsonify({"msg": "Bunday dars topilmadi"}), 404

    data = request.get_json(force=True)

    try:
        if "group" in data:
            group = Group.query.filter_by(turon_id=data.get("group")).first()
            if group:
                timetable.group_id = group.id

        if "week" in data:
            week = WeekDays.query.filter_by(turon_id=data.get("week")).first()
            if week:
                timetable.week_id = week.id

        if "room" in data:
            room = Room.query.filter_by(turon_id=data.get("room")).first()
            if room:
                timetable.room_id = room.id

        if "hours" in data:
            hours = Hours.query.filter_by(turon_id=data.get("hours")).first()
            if hours:
                timetable.hours_id = hours.id

        if "branch" in data:
            branch = Branch.query.filter_by(turon_id=data.get("branch")).first()
            if branch:
                timetable.branch_id = branch.id

        if "teacher" in data:
            teacher = Teacher.query.filter_by(turon_id=data.get("teacher")).first()
            if teacher:
                timetable.teacher_id = teacher.id

        if "subject" in data:
            subject = Subject.query.filter_by(name=data.get("subject")).first()
            if subject:
                timetable.subject_id = subject.id

        if "flow" in data:
            flow = Flow.query.filter_by(turon_id=data.get("flow")).first()
            if flow:
                timetable.flow_id = flow.id
        if "name" in data:
            timetable.name = data.get("name")
        if "date" in data and data.get("date"):
            timetable.date = datetime.fromisoformat(data.get("date"))

        db.session.commit()

        return jsonify({
            "msg": "Dars muvaffaqiyatli yangilandi",
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Xatolik", "error": str(e)}), 400


@crud_timetable_bp.route("/timetable-list-create", methods=["POST"])
def create_timetable():
    data = request.get_json()

    try:
        timetable = ClassTimeTable(turon_id=data.get("id"))

        if "group" in data:
            group = Group.query.filter_by(turon_id=data.get("group")).first()
            if group:
                timetable.group_id = group.id

        if "week" in data:
            week = WeekDays.query.filter_by(turon_id=data.get("week")).first()
            if week:
                timetable.week_id = week.id

        if "room" in data:
            room = Room.query.filter_by(turon_id=data.get("room")).first()
            if room:
                timetable.room_id = room.id

        if "hours" in data:
            hours = Hours.query.filter_by(turon_id=data.get("hours")).first()
            if hours:
                timetable.hours_id = hours.id

        if "branch" in data:
            branch = Branch.query.filter_by(turon_id=data.get("branch")).first()
            if branch:
                timetable.branch_id = branch.id

        if "teacher" in data:
            teacher = Teacher.query.filter_by(turon_id=data.get("teacher")).first()
            if teacher:
                timetable.teacher_id = teacher.id

        if "subject" in data:
            subject = Subject.query.filter_by(name=data.get("subject")).first()
            if subject:
                timetable.subject_id = subject.id

        if "flow" in data:
            flow = Flow.query.filter_by(turon_id=data.get("flow")).first()
            if flow:
                timetable.flow_id = flow.id

        if "name" in data:
            timetable.name = data.get("name")

        if "date" in data and data.get("date"):
            timetable.date = datetime.fromisoformat(data.get("date"))

        db.session.add(timetable)
        db.session.commit()

        return jsonify({"msg": "Dars muvaffaqqiyatli yaratildi", "id": timetable.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
