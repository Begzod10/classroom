import requests
from backend.branch.models import Branch
from backend.lessons.models import Subject
from backend.models.basic_model import Student, db, Group, Teacher
from backend.time_table.models import WeekDays, Hours, ClassTimeTable
from backend.room.models import Room
from backend.flow.models import Flow
from backend.configs import turon_server_url


def sync_branches():
    resp = requests.get(f"{turon_server_url}/api/Branch/branch_list-classroom/").json()
    for item in resp:
        branch = Branch.query.filter_by(turon_id=int(item["id"])).first()
        if not branch:
            branch = Branch(turon_id=int(item["id"]))
        branch.name = item.get("name")
        branch.number = item.get("number")
        branch.address = item.get("address") or item.get("location_text") or ""
        db.session.add(branch)
    db.session.commit()


def sync_rooms():
    resp = requests.get(f"{turon_server_url}/api/Rooms/rooms-classroom/").json()
    for item in resp:
        room = Room.query.filter_by(turon_id=int(item["id"])).first()
        if not room:
            room = Room(turon_id=int(item["id"]))
        room.name = item.get("name")
        room.order = item.get("order")
        room.branch_id = Branch.query.filter_by(turon_id=int(item["branch"])).first().id
        db.session.add(room)
    db.session.commit()


def sync_weekdays():
    resp = requests.get(f"{turon_server_url}/api/TimeTable/week_days-classroom/").json()
    for item in resp:
        wd = WeekDays.query.filter_by(turon_id=int(item["id"])).first()
        if not wd:
            wd = WeekDays(turon_id=int(item["id"]))
        wd.name_en = item.get("name_en")
        wd.name_uz = item.get("name_uz")
        wd.order = item.get("order")
        db.session.add(wd)
    db.session.commit()


def sync_hours():
    resp = requests.get(f"{turon_server_url}/api/SchoolTimeTable/hours-list-create/").json()
    for item in resp:
        hour = Hours.query.filter_by(turon_id=int(item["id"])).first()
        if not hour:
            hour = Hours(turon_id=int(item["id"]))
        hour.start_time = item.get("start_time")
        hour.end_time = item.get("end_time")
        hour.name = item.get("name")
        hour.order = item.get("order")
        db.session.add(hour)
    db.session.commit()


def sync_timetable(branch_id):
    resp = requests.get(
        f"{turon_server_url}/api/SchoolTimeTable/timetable-lessons/?branch={branch_id}"
    ).json()

    branch = Branch.query.filter_by(turon_id=branch_id).first()

    for item in resp.get("time_tables", []):
        week_day = WeekDays.query.filter_by(name_uz=item.get("weekday")).first()
        current_date = item.get("date")

        for room in item.get("rooms", []):
            try:
                room_obj = Room.query.filter_by(turon_id=int(room.get("id"))).first()
            except Exception as e:
                print(f"[ERROR] Roomni olishda xato: {room} | {e}")
                room_obj = None
            for lesson in room.get("lessons", []):
                try:
                    if not lesson.get("status"):
                        continue

                    tt = ClassTimeTable.query.filter_by(
                        turon_id=int(lesson.get("id"))
                    ).first()
                    if not tt:
                        tt = ClassTimeTable(turon_id=int(lesson.get("id")))

                    tt.week_id = week_day.id if week_day else None
                    tt.date = current_date
                    tt.branch_id = branch.id if branch else None
                    tt.room_id = room_obj.id if room_obj else None

                    # Hours
                    hours_obj = Hours.query.filter_by(
                        turon_id=int(lesson.get("hours"))
                    ).first()
                    if not hours_obj:
                        print(f"[WARN] Hours topilmadi: {lesson.get('hours')}")
                    tt.hours_id = hours_obj.id if hours_obj else None

                    # Subject
                    subject_obj = Subject.query.filter_by(
                        name=lesson.get("subject", {}).get("name")
                    ).first()
                    if not subject_obj:
                        print(f"[WARN] Subject topilmadi: {lesson.get('subject')}")
                    tt.subject_id = subject_obj.id if subject_obj else None

                    # Group yoki Flow
                    if lesson.get("is_flow"):
                        flow_obj = Flow.query.filter_by(
                            turon_id=int(lesson.get("group", {}).get("id"))
                        ).first()
                        if not flow_obj:
                            print(f"[WARN] Flow topilmadi: {lesson.get('group')}")
                        tt.flow_id = flow_obj.id if flow_obj else None
                    else:
                        group_obj = Group.query.filter_by(
                            turon_id=int(lesson.get("group", {}).get("id"))
                        ).first()
                        if not group_obj:
                            print(f"[WARN] Group topilmadi: {lesson.get('group')}")
                        tt.group_id = group_obj.id if group_obj else None

                    # Teacher
                    teacher_obj = Teacher.query.filter_by(
                        turon_id=int(lesson.get("teacher", {}).get("id"))
                    ).first()
                    if not teacher_obj:
                        print(f"[WARN] Teacher topilmadi: {lesson.get('teacher')}")
                    tt.teacher_id = teacher_obj.id if teacher_obj else None

                    db.session.add(tt)
                    db.session.flush()

                    # Students
                    if "students" in lesson:
                        students = Student.query.filter(
                            Student.turon_id.in_(lesson["students"])
                        ).all()
                        if not students:
                            print(f"[WARN] Studentlar topilmadi: {lesson['students']}")
                        tt.students = students

                except Exception as e:
                    print(f"[ERROR] Lessonni sync qilishda xato: {lesson} | {e}")

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[CRITICAL] Commitda xato: {e}")
