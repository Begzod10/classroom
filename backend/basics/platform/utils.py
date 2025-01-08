from backend.models.basic_model import Group, Subject, db, Role, User, StudentSubject, Student, Teacher


def check_group_info(gr, type="gennis"):
    # Determine the group filter based on type
    group_filter = Group.platform_id if type == "gennis" else Group.turon_id

    group = Group.query.filter(group_filter == gr['id']).first()

    # Common logic to create or update the group
    if not group:
        subject_name = gr['subjects']['name'] if type == "gennis" else gr['subject']
        subject = Subject.query.filter(Subject.name == subject_name).first()

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


def check_user_exists(user_get):
    if user_get['student']:
        role = Role.query.filter(Role.type == "student", Role.role == "a43c33b82").first()
    else:
        role = Role.query.filter(Role.type == "teacher", Role.role == "b00c11a31").first()
    user = User(username=user_get['username'], name=user_get['name'], surname=user_get['surname'],
                balance=user_get['balance'],
                password=user_get['password'], platform_id=user_get['id'],
                role_id=role.id,
                age=user_get['age'], father_name=user_get['father_name'], born_day=user_get['born_day'],
                born_month=user_get['born_month'], born_year=user_get['born_year'],
                user_id=user_get['user_id'])
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
    user.user_id = user_get['user_id']
    user.system_name = "gennis"
    user.balance = user_get['balance']
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
