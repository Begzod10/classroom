import datetime

import requests

from app import api, app, cross_origin, db, request, jsonify, platform_server, django_server
from backend.models.settings import iterate_models
from backend.models.basic_model import Role, Teacher, User, Student, Location, Subject, SubjectLevel, Group, \
    StudentSubject
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from pprint import pprint
from werkzeug.security import generate_password_hash, check_password_hash
from .settings import check_exist_id, check_exist_classroom_id
import uuid
import hashlib


@app.route(f'{api}/token', methods=["POST", "GET"])
def create_token():
    json_request = request.get_json()
    username = json_request['username'].lower()
    password = json_request['password'].lower()

    if username != "test" or password != "test":
        return {"msg": "Wrong email or password"}, 401
    access_token = create_access_token(identity=username)
    response = {"access_token": access_token}
    return response


@app.route(f"{api}/refresh", methods=["POST"])
@cross_origin()
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    if user.role.type != "methodist":
        if user.system_name == "school":
            if user.teacher:
                response = requests.get(f"{django_server}/api/Teachers/get_balance/{user.turon_id}/", headers={
                    'Content-Type': 'application/json'
                })
            else:
                response = requests.get(f"{django_server}/api/Students/get_balance/{user.turon_id}/", headers={
                    'Content-Type': 'application/json'
                })
        else:
            if user.teacher:
                response = requests.get(f"{platform_server}/api/get_teacher_balance/{user.platform_id}", headers={
                    'Content-Type': 'application/json'
                })
            else:
                response = requests.get(f"{platform_server}/api/get_student_balance/{user.platform_id}", headers={
                    'Content-Type': 'application/json'
                })

        if response and response.json():
            user.balance = response.json()['balance']
            db.session.commit()
    else:
        response = None
    info = {
        "info": user.convert_json(),
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=user.classroom_user_id)
        # "img": response.json()['profile_photo'] if "profile_photo" in response.json() else None
    }
    return jsonify({
        "data": info
    })


@app.route(f'{api}/send_user/<token>')
@cross_origin()
def send_user(token):
    response = requests.get(f"{platform_server}/api/get_user", headers={
        "Authorization": "Bearer " + token,
        'Content-Type': 'application/json'
    })
    if 'data' not in response.json():
        return jsonify({
            "msg": "Not logged in"
        })
    subject_list = response.json()['subject_list']
    # users = response.json()['users']
    # for user in users:
    #     user_get = User.query.filter(User.user_id == user['user_id']).first()
    #     if user_get:
    #         user_get.username = user['username']
    #         db.session.commit()

    for sub in subject_list:
        get_subject = Subject.query.filter(Subject.name == sub['name']).first()
        if not get_subject:
            get_subject = Subject(name=sub['name'])
            get_subject.add_commit()

    item = response.json()['data']

    location_id = item['location']['id']
    location_name = item['location']['name']
    role_id = item["role"]['id']
    role_type = item['role']['name']
    role_token = item['role']['role']
    role = Role.query.filter(Role.platform_id == role_id).first()
    if not role:
        role = Role(platform_id=role_id, type=role_type, role=role_token)
        role.add_commit()
    location = Location.query.filter(Location.platform_id == location_id).first()
    if not location:
        location = Location(name=location_name, platform_id=location_id)
        location.add_commit()

    user = User.query.filter(User.username == item['username']).first()
    username = item['username']

    # if user:
    #     user.system_name = "gennis"
    #     db.session.commit()
    #     # create_status = True
    #     # if user.system_name != "gennis":
    #     #     username = item['username'] + "_center"
    #     #     response = requests.post(f"{django_server}/api/Users/username-check/", headers={
    #     #         'Content-Type': 'application/json'
    #     #     }, json={"username": username})
    #     #     if response:
    #     #         while response.json()['exists']:
    #     #             hashed_uuid = int(hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest(), 5)
    #     #             numeric_uuid = str(hashed_uuid)[:4]
    #     #             username = item['username'] + "_" + numeric_uuid
    #     #             response = requests.post(f"{django_server}/api/Users/username-check/", headers={
    #     #                 'Content-Type': 'application/json'
    #     #             }, json={"username": username})
    #     #     create_status = True
    #     # else:
    #     #     create_status = False

    if not user:
        user = User(username=username, name=item['name'], surname=item['surname'], balance=item['balance'],
                    password=item['password'], platform_id=item['id'], location_id=location.id, role_id=role.id,
                    age=item['age'], father_name=item['father_name'], born_day=item['born_day'],
                    born_month=item['born_month'], born_year=item['born_year'], user_id=item['user_id'])
        user.add_commit()
        for phone in item['phone']:
            if phone['personal']:
                user.phone = phone['phone']
            else:
                user.parent_phone = phone['phone']
            db.session.commit()
    else:
        for phone in item['phone']:
            if phone['personal']:
                user.phone = phone['phone']
            else:
                user.parent_phone = phone['phone']
            db.session.commit()
        user.born_year = item['born_year']
        user.born_month = item['born_month']
        user.born_day = item['born_day']
        user.father_name = item['father_name']
        user.age = item['age']
        user.user_id = item['user_id']
        user.system_name = "gennis"
        user.balance = item['balance']
        db.session.commit()
    if item['student']:
        student = Student.query.filter(Student.user_id == user.id).first()
        if not student:
            student = Student(user_id=user.id, debtor=item['student']['debtor'],
                              representative_name=item['student']['representative_name'],
                              representative_surname=item['student']['representative_surname'])
            student.add_commit()
        else:
            Student.query.filter(Student.user_id == user.id).update({
                "debtor": item['student']['debtor'],
                "representative_name": item['student']['representative_name'],
                "representative_surname": item['student']['representative_surname']
            })
            db.session.commit()
        for gr in item['student']['group']:
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
    if item['teacher']:
        teacher = Teacher.query.filter(Teacher.user_id == user.id).first()
        if not teacher:
            teacher = Teacher(user_id=user.id)
            teacher.add_commit()
        group_list = []
        for gr in item['teacher']['group']:
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

    access_token = create_access_token(identity=user.user_id)
    return jsonify({
        "data": {
            "info": user.convert_json(),
            "access_token": access_token,
            "refresh_token": create_refresh_token(identity=user.user_id)
        }
    })


@app.route('/send_datas')
@jwt_required()
def send_datas():
    subjects = Subject.query.order_by(Subject.id).order_by(Subject.id).all()
    return jsonify({
        "data": iterate_models(subjects, entire=True)
    })


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


@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    return app.send_static_file("index.html")


@app.route(f'{api}/update_user_info', methods=['POST'])
def update_user_info():
    user_get = request.get_json()['user']
    User.query.filter(User.platform_id == user_get['id']).update({
        "username": user_get['username']
    })
    db.session.commit()
    return jsonify({
        "msg": "hello"
    })


@app.route(f'{api}/turon_user/', defaults={'username': None}, methods=['POST', "GET"])
@app.route(f'{api}/turon_user/<username>', methods=['POST', "GET"])
def turon_user(username):
    if request.method == "GET":
        user = User.query.filter(User.username == username).first()
        return jsonify({
            "info": user.convert_json(),
            "access_token": create_access_token(identity=user.user_id),
            "refresh_token": create_refresh_token(identity=user.user_id)
        })

    info = request.get_json()['user']
    password = generate_password_hash(info['password'])
    if info['role'] == "teacher":
        role = Role.query.filter(Role.type == "teacher", Role.role == "b00c11a31").first()

    else:
        role = Role.query.filter(Role.type == "student", Role.role == "a43c33b82").first()

    classroom_user_id = check_exist_classroom_id()
    user = User.query.filter(User.username == info['username'], User.system_name == "school").first()
    username = info['username']
    if not user:
        user = User(username=username, name=info['name'], surname=info['surname'], balance=info['balance'],
                    password=password, turon_id=info['id'], role_id=role.id,
                    age=datetime.datetime.now().year - int(info['birth_date'][:4]), father_name=info['father_name'],
                    born_day=info['birth_date'][:2], system_name="school",
                    parent_phone=info['parent_phone'], phone=info['phone'],
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

    requests.put(f"{django_server}/api/Users/username-check/", headers={
        'Content-Type': 'application/json'
    }, json={"username": username, "user_id": user.user_id, "turon_id": user.turon_id})
    return jsonify({
        "data": {
            "username": user.username,
        }
    })


from .platform.views import *
