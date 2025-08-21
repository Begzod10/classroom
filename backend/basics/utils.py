from datetime import datetime

import requests

from backend.configs import gennis_server_url
from backend.models.basic_model import Group, Subject, db, Role, User, StudentSubject, Student, Teacher, Location
from backend.models.settings import check_exist_classroom_id
from backend.parent.models import Parent


def check_group_info(gr, type="gennis", user_id=None):
    group_filter = Group.platform_id if type == "gennis" else Group.turon_id
    group = Group.query.filter(group_filter == gr['id']).first()

    if type == "gennis":
        subject_name = gr['subjects']['name']
        subject = Subject.query.filter_by(name=subject_name).first()
    else:
        subject_name = gr['subjects'][0]['name']
        subject = Subject.query.filter_by(name=subject_name).first()

    if not group:
        group_data = {
            "name": gr['name'],
            "price": gr['price'],
            "teacher_salary": gr['teacher_salary'],
            "subject_id": subject.id if subject else None
        }

        if type == "gennis":
            group = Group(platform_id=gr['id'], **group_data)
        else:
            teacher = Teacher.query.filter_by(user_id=user_id).first()
            group = Group(turon_id=gr['id'], teacher_id=teacher.id, **group_data)

            for sub in gr['subjects']:
                subject = Subject.query.filter_by(name=sub['name']).first()
                if not subject:
                    subject = Subject(name=sub['name'])
                    db.session.add(subject)
                if subject not in group.subjects:
                    group.subjects.append(subject)

        db.session.add(group)

    else:
        group.teacher_salary = gr['teacher_salary']
        group.price = gr['price']
        group.name = gr['name']

        if type == "turon":
            teacher = Teacher.query.filter_by(user_id=user_id).first()
            print(teacher.id, group.teacher_id)
            if teacher and group.teacher_id != teacher.id:
                group.teacher_id = teacher.id

            current_subjects = []
            for sub in gr['subjects']:
                subject = Subject.query.filter_by(name=sub['name']).first()
                if not subject:
                    subject = Subject(name=sub['name'])
                    db.session.add(subject)
                current_subjects.append(subject)
                if subject not in group.subjects:
                    group.subjects.append(subject)

            for subj in list(group.subjects):
                if subj not in current_subjects:
                    group.subjects.remove(subj)

    db.session.commit()
    return group, (gr['subjects'] if type == "turon" else gr['subject'])

def check_user_gennis(user_get):
    if user_get['student']:
        role = Role.query.filter(Role.type == "student", Role.role == "a43c33b82").first()
    elif user_get['teacher']:
        role = Role.query.filter(Role.type == "teacher", Role.role == "b00c11a31").first()
    elif user_get['parent']:
        role = Role.query.filter(Role.type == "parent", Role.role == "pa21s122s").first()
        if not role:
            role = Role(type="parent", role="pa21s122s")
            role.add_commit()
    user = User.query.filter(User.username == user_get['username'], User.system_name == "gennis").first()
    classroom_user_id = check_exist_classroom_id()
    location = Location.query.filter(Location.name == user_get['location']['name']).first()
    if not location:
        location = Location(name=user_get['location']['name'], platform_id=user_get['location']['id'])
    if not user:
        user = User(username=user_get['username'], name=user_get['name'], surname=user_get['surname'],
                    balance=user_get['balance'], password=user_get['password'], platform_id=user_get['id'],
                    role_id=role.id, system_name="gennis", classroom_user_id=classroom_user_id, age=user_get['age'],
                    father_name=user_get['father_name'], born_day=user_get['born_day'],
                    born_month=user_get['born_month'], born_year=user_get['born_year'], location_id=location.id)
        user.add_commit()
        if role.type == "parent":
            parent = Parent(user_id=user.id)
            db.session.add(parent)
            db.session.commit()

    for phone in user_get['phone']:
        if phone['personal']:
            user.phone = phone['phone']
        else:
            user.parent_phone = phone['phone']
        db.session.commit()
    user.born_year = user_get['born_year']
    user.born_month = user_get['born_month']
    user.born_day = user_get['born_day']
    user.father_name = user_get['father_name']
    user.age = user_get['age']
    user.system_name = "gennis"
    user.balance = user_get['balance']
    user.classroom_user_id = classroom_user_id
    db.session.commit()
    if user_get['student']:
        student = Student.query.filter(Student.user_id == user.id).first()
        if not student:
            student = Student(user_id=user.id, debtor=user_get['student']['debtor'],
                              representative_name=user_get['student']['representative_name'],
                              representative_surname=user_get['student']['representative_surname'])
            student.add_commit()
        else:
            Student.query.filter(Student.user_id == user.id).update({"debtor": user_get['student']['debtor'],
                                                                     "representative_name": user_get['student'][
                                                                         'representative_name'],
                                                                     "representative_surname": user_get['student'][
                                                                         'representative_surname']})
            db.session.commit()
        for gr in user_get['student']['group']:
            group, _ = check_group_info(gr)
            if group not in student.groups:
                student.groups.append(group)
                db.session.commit()
            subject = Subject.query.filter(Subject.name == gr['subjects']['name']).first()
            student_subject = StudentSubject.query.filter(StudentSubject.subject_id == subject.id,
                                                          StudentSubject.student_id == student.id).first()
            if not student_subject:
                student_subject = StudentSubject(subject_id=subject.id, student_id=student.id)
                student_subject.add_commit()
    elif user_get['teacher']:
        teacher = Teacher.query.filter(Teacher.user_id == user.id).first()
        if not teacher:
            teacher = Teacher(user_id=user.id)
            teacher.add_commit()
        group_list = []
        for gr in user_get['teacher']['group']:
            group_list.append(gr['id'])
            group, _ = check_group_info(gr)
            if group not in teacher.groups:
                teacher.groups.append(group)
                db.session.commit()
            group.teacher_id = teacher.id
            subject = Subject.query.filter(Subject.id == group.subject_id).first()
            if subject not in teacher.subjects:
                teacher.subjects.append(subject)
                db.session.commit()
            db.session.commit()
        for gr in teacher.groups:
            if gr.platform_id not in group_list:
                teacher.groups.remove(gr)
                db.session.commit()
    elif user_get['parent']:
        parent = Parent.query.filter(Parent.user_id == user.id).first()
        if not parent:
            parent = Parent(user_id=user.id)
            parent.add_commit()
        for child in user_get['parent']['children']:
            user = User.query.filter(User.platform_id == child['user']['id']).first()
            if user:
                student = Student.query.filter(Student.user_id == user.id).first()
            else:
                user_get = child['user']

                user = check_user_gennis(user_get)
                student = Student.query.filter(Student.user_id == user.id).first()
            if student:
                if student not in parent.student_get:
                    parent.student_get.append(student)
                    db.session.commit()
    return user

def check_user_turon(info):
    print(info)

    role_map = {"teacher": "b00c11a31", "student": "a43c33b82"}
    role = Role.query.filter_by(type=info['role'], role=role_map[info['role']]).first()

    classroom_user_id = check_exist_classroom_id()
    username = info['username']

    user = User.query.filter_by(username=username, system_name="turon").first()
    if not user:
        user = User(
            username=username,
            name=info['name'],
            surname=info['surname'],
            balance=info['balance'],
            turon_id=info['id'],
            role_id=role.id,
            age=datetime.now().year - int(info['birth_date'][:4]),
            father_name=info['father_name'],
            born_day=info['birth_date'][:2],
            born_month=info['birth_date'][5:7],
            born_year=info['birth_date'][:4],
            system_name="turon",
            classroom_user_id=classroom_user_id,
            parent_phone=info.get("parent_phone") or info.get("parent_number"),
            phone=info['phone_number']
        )
        db.session.add(user)
    else:
        user.classroom_user_id = classroom_user_id
        user.parent_phone = info.get("parent_phone") or info.get("parent_number")
        user.phone = info['phone_number']

    if info['role'] == "student":
        role_instance = Student.query.filter_by(user_id=user.id).first()
        if not role_instance:
            role_instance = Student(user_id=user.id)
            db.session.add(role_instance)
    else:
        role_instance = Teacher.query.filter_by(user_id=user.id).first()
        if not role_instance:
            role_instance = Teacher(user_id=user.id)
            db.session.add(role_instance)

    current_groups = []
    for gr in info['groups']:
        group, subjects = check_group_info(gr, type="turon", user_id=user.id)
        current_groups.append(group)

        if group not in role_instance.groups:
            role_instance.groups.append(group)

        if info['role'] == "student":
            current_subject_ids = []
            for sub in subjects:
                subject = Subject.query.filter_by(name=sub['name']).first()
                if subject:
                    current_subject_ids.append(subject.id)
                    exists = StudentSubject.query.filter_by(
                        subject_id=subject.id,
                        student_id=role_instance.id
                    ).first()
                    if not exists:
                        db.session.add(StudentSubject(subject_id=subject.id, student_id=role_instance.id))

            old_subjects = StudentSubject.query.filter_by(student_id=role_instance.id).all()
            for ss in old_subjects:
                if ss.subject_id not in current_subject_ids:
                    db.session.delete(ss)

        else:
            current_subjects = []
            for sub in info.get("subjects", []):
                print(sub['name'])
                subject = Subject.query.filter_by(name=sub['name']).first()
                if subject:
                    current_subjects.append(subject)
                    if subject not in role_instance.subjects:
                        role_instance.subjects.append(subject)

            for subj in list(role_instance.subjects):
                if subj not in current_subjects:
                    role_instance.subjects.remove(subj)

    for gr in list(role_instance.groups):
        if gr not in current_groups:
            role_instance.groups.remove(gr)
            if info['role'] == "student":
                student_subject = StudentSubject.query.filter_by(
                    subject_id=gr.subject_id,
                    student_id=role_instance.id
                ).first()
                if student_subject:
                    db.session.delete(student_subject)

    db.session.commit()
    return user

def add_gennis_user_data(user_get, user):
    student = Student.query.filter(Student.user_id == user.id).first()
    teacher = Teacher.query.filter(Teacher.user_id == user.id).first()
    if student:
        Student.query.filter(Student.user_id == user.id).update({"debtor": user_get['debtor'], })
        User.query.filter(User.id == user.id).update(
            {"name": user_get['name'], "surname": user_get['surname'], "father_name": user_get['father_name'], })
        db.session.commit()
        for gr in user_get['group']:
            group, _ = check_group_info(gr)
            if group not in student.groups:
                student.groups.append(group)
                db.session.commit()
            subject = Subject.query.filter(Subject.id == group.subject_id).first()
            student_subject = StudentSubject.query.filter(StudentSubject.subject_id == subject.id,
                                                          StudentSubject.student_id == student.id).first()
            if not student_subject:
                student_subject = StudentSubject(subject_id=subject.id, student_id=student.id)
                student_subject.add_commit()
        student_no_group = db.session.query(Group).join(Group.student).filter(Student.id == student.id,
                                                                              Group.platform_id.notin_(
                                                                                  [gr['id'] for gr in
                                                                                   user_get['group']])).all()

        for gr in student_no_group:
            student.groups.remove(gr)
            group_get = Group.query.filter(Group.id == gr.id).first()
            student_subject = StudentSubject.query.filter(StudentSubject.subject_id == group_get.subject_id,
                                                          StudentSubject.student_id == student.id).first()
            if student_subject:
                db.session.delete(student_subject)
                db.session.commit()
            db.session.commit()
    else:
        for gr in user_get['group']:
            group, _ = check_group_info(gr)
            if group not in teacher.groups:
                teacher.groups.append(group)
                db.session.commit()
            group.teacher_id = teacher.id
            subject = Subject.query.filter(Subject.id == group.subject_id).first()
            if subject not in teacher.subjects:
                teacher.subjects.append(subject)
                db.session.commit()

        teacher_no_group = Group.query.filter(Group.teacher_id == teacher.id,
                                              Group.platform_id.notin_([gr['id'] for gr in user_get['group']])).all()

        for gr in teacher_no_group:
            if gr in teacher.groups:
                teacher.groups.remove(gr)
                db.session.commit()


def add_parent_gennis(user_get, user):
    parent = Parent.query.filter(Parent.user_id == user.id).first()
    if parent:
        User.query.filter(User.id == user.id).update({"name": user_get['name'], "surname": user_get['surname']})
        db.session.commit()
        if parent.student_get:
            for child in parent.student_get:
                parent.student_get.remove(child)
        db.session.commit()
        if user_get['children']:
            for child in user_get['children']:
                response = requests.get(f"{gennis_server_url}/api/send_student_data/{child['user_id']}",
                                        headers={'Content-Type': 'application/json'})
                user_get = response.json()['user']
                check_user_gennis(user_get)
                add_gennis_user_data(user_get, user)
                student = Student.query.filter(Student.user_id == user.id).first()
                parent.student_get.append(student)

            db.session.commit()
