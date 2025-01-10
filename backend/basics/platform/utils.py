from backend.models.basic_model import Group, Subject, db, Role, User, StudentSubject, Student, Teacher
from backend.models.settings import check_exist_classroom_id
from datetime import datetime


def check_group_info(gr, type="gennis"):
    # Determine the group filter based on type
    group_filter = Group.platform_id if type == "gennis" else Group.turon_id

    group = Group.query.filter(group_filter == gr['id']).first()

    # Common logic to create or update the group
    print(gr)
    if not group:
        subject_name = gr['subjects']['name'] if type == "gennis" else None

        subject = Subject.query.filter(Subject.name == subject_name).first() if subject_name else None

        # Create a new Group with either platform_id or turon_id
        group_data = {
            "name": gr['name'],
            "price": gr['price'],
            "teacher_salary": gr['teacher_salary'],
            "subject_id": subject.id if subject else None
        }
        if type == "gennis":
            group = Group(platform_id=gr['id'], **group_data)
        else:
            group = Group(turon_id=gr['id'], **group_data)
        group.add_commit()
    else:
        # Update existing Group fields
        group_update_data = {
            "teacher_salary": gr['teacher_salary'],
            "price": gr['price'],
            "name": gr['name']
        }

        Group.query.filter(group_filter == gr['id']).update(group_update_data)
        db.session.commit()
    if type == "turon":
        subject = gr['subject']
    else:
        subject = None
    return group, subject


def check_user_gennis(user_get):
    if user_get['student']:
        role = Role.query.filter(Role.type == "student", Role.role == "a43c33b82").first()
    else:
        role = Role.query.filter(Role.type == "teacher", Role.role == "b00c11a31").first()
    print(role)
    user = User.query.filter(User.username == user_get['username'], User.system_name == "gennis").first()
    classroom_user_id = check_exist_classroom_id()
    if not user:
        user = User(username=user_get['username'], name=user_get['name'], surname=user_get['surname'],
                    balance=user_get['balance'],
                    password=user_get['password'], platform_id=user_get['id'],
                    role_id=role.id,
                    classroom_user_id=classroom_user_id,
                    age=user_get['age'], father_name=user_get['father_name'], born_day=user_get['born_day'],
                    born_month=user_get['born_month'], born_year=user_get['born_year'],
                    )
        user.add_commit()
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
            Student.query.filter(Student.user_id == user.id).update({
                "debtor": user_get['student']['debtor'],
                "representative_name": user_get['student']['representative_name'],
                "representative_surname": user_get['student']['representative_surname']
            })
            db.session.commit()
        for gr in user_get['student']['group']:
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
    if user_get['teacher']:
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
        for gr in teacher.groups:
            if gr.platform_id not in group_list:
                teacher.groups.remove(gr)
                db.session.commit()

    return user


def check_user_turon(info):
    if info['role'] == "teacher":
        role = Role.query.filter(Role.type == "teacher", Role.role == "b00c11a31").first()

    else:
        role = Role.query.filter(Role.type == "student", Role.role == "a43c33b82").first()

    classroom_user_id = check_exist_classroom_id()
    user = User.query.filter(User.username == info['username'], User.system_name == "school").first()
    username = info['username']
    if not user:
        user = User(username=username, name=info['name'], surname=info['surname'], balance=info['balance'],
                    turon_id=info['id'], role_id=role.id,
                    age=datetime.now().year - int(info['birth_date'][:4]), father_name=info['father_name'],
                    born_day=info['birth_date'][:2], system_name="school",
                    parent_phone=info['parent_phone'] if 'parent_phone' in info else None, phone=info['phone_number'],
                    born_month=info['birth_date'][5:7], born_year=info['birth_date'][:4],
                    classroom_user_id=classroom_user_id)
        user.add_commit()
    else:
        user.classroom_user_id = classroom_user_id
        user.parent_phone = info['parent_number'] if 'parent_number' in info else None
        user.phone = info['phone_number']
        db.session.commit()

    if info['role'] == "student":
        role_instance = Student.query.filter(Student.user_id == user.id).first()
        if not role_instance:
            role_instance = Student(user_id=user.id)
            role_instance.add_commit()
    else:
        role_instance = Teacher.query.filter(Teacher.user_id == user.id).first()
        if not role_instance:
            role_instance = Teacher(user_id=user.id)
            role_instance.add_commit()
    new_groups = []
    subjects = []
    for gr in info['groups']:
        group, subjects = check_group_info(gr, type="turon")
        if group not in role_instance.groups:
            role_instance.groups.append(group)
            db.session.commit()
    if info['role'] == "student":
        for sub in subjects:
            subject = Subject.query.filter(Subject.name == sub['name']).first()
            student_subject = StudentSubject.query.filter(StudentSubject.subject_id == subject.id,
                                                          StudentSubject.student_id == role_instance.id).first()
            if not student_subject:
                student_subject = StudentSubject(subject_id=subject.id, student_id=role_instance.id)
                db.session.add(student_subject)
                db.session.commit()
    else:
        subjects = info['subject']
        for sub in subjects:
            subject = Subject.query.filter(Subject.name == sub['name']).first()
            if subject not in role_instance.subjects:
                role_instance.subjects.append(subject)
                db.session.commit()
    return user

