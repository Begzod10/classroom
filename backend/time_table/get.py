from flask import Blueprint, request, jsonify
from datetime import date, datetime, timedelta
from backend.time_table.sync_service import sync_branches, sync_rooms, sync_weekdays, sync_timetable, sync_hours

from backend.room.models import Room
from backend.branch.models import Branch
from backend.time_table.models import Hours, ClassTimeTable, WeekDays
from backend.models.basic_model import Group, Teacher, Subject, Student, db

get_timetable_bp = Blueprint("timetable", __name__)

WEEK_DAYS = ['Dushanba', 'Seshanba', 'Chorshanba',
             'Payshanba', 'Juma', 'Shanba', 'Yakshanba']


@get_timetable_bp.route('/week-days/', methods=['GET'])
def week_days():
    days = WeekDays.query.order_by(WeekDays.order).all()
    result = [
        {
            "id": day.id,
            "name": day.name,
            "order": day.order
        }
        for day in days
    ]
    return jsonify(result)


@get_timetable_bp.route('/timetable-lessons/', methods=['GET'])
def timetable_lessons():
    week_id = request.args.get("week")
    date_str = request.args.get("date")
    group_id = request.args.get("group")
    teacher_id = request.args.get("teacher")
    student_id = request.args.get("student")

    sync_branches()
    sync_rooms()
    sync_weekdays()
    sync_hours()
    branches = Branch.query.all()
    # for branchs in branches:
    #     sync_timetable(branchs.turon_id)
    branch = None

    if teacher_id:
        teacher = Teacher.query.get(teacher_id)
        if teacher:
            branch = teacher.user.branch

    if student_id and not branch:
        student = Student.query.get(student_id)
        if student:
            branch = student.user.branch
    if not branch:
        return jsonify({"error": "Branch not found"}), 404

    date_ls = None
    if date_str:
        try:
            date_ls = datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            pass

    if week_id:
        try:
            week_id = int(week_id)
        except ValueError:
            week_id = None

    rooms = Room.query.filter_by(branch_id=branch.id, deleted=False).all()
    hours = Hours.query.order_by(Hours.order).all()

    time_tables = []

    # ✅ faqat week_id berilsa
    if week_id and date_ls is None:
        today = date.today()
        today_weekday = today.isoweekday()
        shift_days = week_id - today_weekday
        week_day_date = today + timedelta(days=shift_days)

        weekday_name = WEEK_DAYS[week_day_date.weekday()]
        rooms_info = build_rooms_info(
            rooms, hours, week_day_date,
            branch, week_id, group_id,
            teacher_id, student_id
        )
        time_tables.append({
            "date": week_day_date.strftime("%Y-%m-%d"),
            "weekday": weekday_name,
            "rooms": rooms_info
        })

    # ✅ ham week_id, ham date bo‘lmasa → butun hafta
    elif date_ls is None and week_id is None:
        today = date.today()
        start_week = today - timedelta(days=today.weekday())  # dushanba
        for i in range(7):
            day_date = start_week + timedelta(days=i)
            weekday_name = WEEK_DAYS[day_date.weekday()]
            rooms_info = build_rooms_info(
                rooms, hours, day_date,
                branch, None,
                group_id, teacher_id, student_id
            )
            time_tables.append({
                "date": day_date.strftime("%Y-%m-%d"),
                "weekday": weekday_name,
                "rooms": rooms_info
            })

    # ✅ faqat date berilsa
    elif date_ls:
        weekday_name = WEEK_DAYS[date_ls.weekday()]
        rooms_info = build_rooms_info(
            rooms, hours, date_ls,
            branch, None,
            group_id, teacher_id, student_id
        )
        time_tables.append({
            "date": date_ls.strftime("%Y-%m-%d"),
            "weekday": weekday_name,
            "rooms": rooms_info
        })

    hours_list = [
        {
            "id": hour.id,
            "name": hour.name,
            "start_time": hour.start_time.strftime('%H:%M'),
            "end_time": hour.end_time.strftime('%H:%M'),
        }
        for hour in hours
    ]

    return jsonify({
        "time_tables": time_tables,
        "hours_list": hours_list
    })


def build_rooms_info(rooms, hours, current_date,
                     branch, week_id, group_id, teacher_id, student_id):
    rooms_info = []
    for room in rooms:
        info = {
            "id": room.id,
            "name": room.name,
            "lessons": []
        }
        for hour in hours:
            qs = ClassTimeTable.query.filter_by(
                date=current_date,
                hours_id=hour.id,
                branch_id=branch.id,
                room_id=room.id
            )

            if week_id:
                qs = qs.filter_by(week_id=week_id)
            if group_id:
                qs = qs.filter_by(group_id=group_id)
            if teacher_id:
                qs = qs.filter_by(teacher_id=teacher_id)
            if student_id:
                qs = qs.join(Group).filter(Group.students.any(id=student_id))

            lesson = (
                qs.join(Hours, ClassTimeTable.hours_id == Hours.id)
                .order_by(Hours.order)
                .first()
            )

            if lesson:
                group_info = {
                    "id": lesson.group.id,
                    "name": lesson.group.name
                } if lesson.group else None
                flow_info = {
                    "id": lesson.flow.id,
                    "name": lesson.flow.name
                } if lesson.flow else None
                teacher_info = {
                    "id": lesson.teacher.id,
                    "name": lesson.teacher.user.name,
                    "surname": lesson.teacher.user.surname,
                    "color": lesson.teacher.color
                } if lesson.teacher else None
                subject_info = {
                    "id": lesson.subject.id,
                    "name": lesson.subject.name
                } if lesson.subject else None

                info["lessons"].append({
                    "id": lesson.id,
                    "status": lesson.hours_id == hour.id,
                    "is_flow": True if lesson.flow else False,
                    "group": flow_info if lesson.group is None else group_info,
                    "room": room.id,
                    "teacher": teacher_info,
                    "subject": subject_info,
                    "hours": hour.id
                })
            else:
                info["lessons"].append({
                    "group": {},
                    "status": False,
                    "hours": hour.id,
                    "teacher": {},
                    "subject": {},
                    "room": room.id,
                    "is_flow": False,
                })
        rooms_info.append(info)
    return rooms_info
