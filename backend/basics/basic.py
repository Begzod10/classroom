import datetime

import requests

from app import cross_origin, db, request, jsonify, current_app
from backend.models.settings import iterate_models
from backend.models.basic_model import Role, Teacher, User, Student, Location, Subject, SubjectLevel, Group, \
    StudentSubject
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from pprint import pprint
from werkzeug.security import generate_password_hash, check_password_hash
from .settings import check_exist_id, check_exist_classroom_id
import uuid
import hashlib
from backend.configs import api, gennis_server_url, turon_server_url
from flask import Blueprint
from .utils import check_user_gennis, check_user_turon, add_gennis_user_data, check_group_info

basic_bp = Blueprint('basic', __name__)


@basic_bp.route('login/', methods=['POST'])
def login():
    username = request.get_json()['username']
    password = request.get_json()['password']
    system_name = request.get_json()['system_name'] if "system_name" in request.get_json() else ""

    user = User.query.filter(User.username == username, system_name == system_name).first()
    if system_name and username != "metod":
        if system_name == "gennis":
            response = requests.post(f"{gennis_server_url}/api/login2", headers={
                'Content-Type': 'application/json'
            }, json={
                "username": username,
                "password": password,
            })
            user_get = response.json()['user'] if 'user' in response.json() else {}
            location = response.json()['location'] if 'location' in response.json() else {}
            if location:
                exist_location = Location.query.filter(Location.platform_id == location['value']).first()
                if not exist_location:
                    exist_location = Location(name=location['name'], platform_id=location['value'])
                    exist_location.add_commit()
                if user:
                    user.location_id = exist_location.id if exist_location else None
                    db.session.commit()
            if not user_get:
                return {"msg": "Username yoki parol noto'g'ri", "success": False}, 200
            if not user:
                user = check_user_gennis(user_get)

            if user_get['parent']:
                pprint(user_get)
                check_user_gennis(user_get)
        else:
            response = requests.post(f"{turon_server_url}/api/token/", headers={
                'Content-Type': 'application/json'
            }, json={
                "username": username,
                "password": password,
            })
            user_get = response.json()['user'] if 'user' in response.json() else {}
            if not user_get:
                return {"msg": "Username yoki parol noto'g'ri", "success": False}, 200
            if not user:
                user = check_user_turon(user_get)
        if user:
            if user.role.type != "methodist" and user.role.type != "parent":
                if system_name == "gennis":
                    response = requests.get(f"{gennis_server_url}/api/send_user_data/{user.platform_id}", headers={
                        'Content-Type': 'application/json'
                    })
                    user_get = response.json()['user']
                    add_gennis_user_data(user_get, user)

        if not user.classroom_user_id:
            classroom_user_id = check_exist_classroom_id()
            user.classroom_user_id = classroom_user_id
            db.session.commit()
        user.system_name = system_name
        db.session.commit()
    else:
        if user and check_password_hash(user.password, password):
            return jsonify({
                "data": {
                    "info": user.convert_json(),
                    "access_token": create_access_token(identity=user.classroom_user_id),
                    "refresh_token": create_refresh_token(identity=user.classroom_user_id),
                    "parent": user.parent.convert_json() if user.parent else None
                }
            })
        else:
            return {"msg": "Username yoki parol noto'g'ri", "success": False}, 200
    # print(user.parent.student_get)

    return jsonify({
        "data": {
            "info": user.convert_json(),
            "access_token": create_access_token(identity=user.classroom_user_id),
            "refresh_token": create_refresh_token(identity=user.classroom_user_id),
            "parent": user.parent.convert_json() if user.parent else None
        }
    })


@basic_bp.route(f'token', methods=["POST", "GET"])
def create_token():
    json_request = request.get_json()
    username = json_request['username'].lower()
    password = json_request['password'].lower()

    if username != "test" or password != "test":
        return {"msg": "Wrong email or password"}, 401
    access_token = create_access_token(identity=username)
    response = {"access_token": access_token}
    return response


@basic_bp.route(f"refresh", methods=["POST"])
@cross_origin()
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    if user.role.type != "methodist" and user.system_name != "pisa":
        if user.system_name == "gennis":
            if user.teacher:
                response = requests.get(f"{gennis_server_url}/api/get_teacher_balance/{user.platform_id}", headers={
                    'Content-Type': 'application/json'
                })
            else:
                response = requests.get(f"{gennis_server_url}/api/get_student_balance/{user.platform_id}", headers={
                    'Content-Type': 'application/json'
                })
        else:

            if user.teacher:
                response = requests.get(f"{turon_server_url}/api/Teachers/get_balance/{user.turon_id}/", headers={
                    'Content-Type': 'application/json'
                })
            else:
                response = requests.get(f"{turon_server_url}/api/Students/get_balance/{user.turon_id}/", headers={
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


@basic_bp.route(f'send_user/<token>')
@cross_origin()
def send_user(token):
    response = requests.get(f"{gennis_server_url}/api/get_user", headers={
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


@basic_bp.route('/send_datas')
@jwt_required()
def send_datas():
    subjects = Subject.query.order_by(Subject.id).order_by(Subject.id).all()
    return jsonify({
        "data": iterate_models(subjects, entire=True)
    })


@basic_bp.errorhandler(404)
def not_found(e):
    return current_app.send_static_file('index.html')


@basic_bp.route('/', methods=['POST', 'GET'])
def index():
    return current_app.send_static_file("index.html")


@basic_bp.route(f'update_user_info', methods=['POST'])
def update_user_info():
    user_get = request.get_json()['user']
    User.query.filter(User.platform_id == user_get['id']).update({
        "username": user_get['username']
    })
    db.session.commit()
    return jsonify({
        "msg": "hello"
    })


@basic_bp.route(f'turon_user/', defaults={'username': None}, methods=['POST', "GET"])
@basic_bp.route(f'turon_user/<username>', methods=['POST', "GET"])
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

    requests.put(f"{turon_server_url}/api/Users/username-check/", headers={
        'Content-Type': 'application/json'
    }, json={"username": username, "user_id": user.user_id, "turon_id": user.turon_id})
    return jsonify({
        "data": {
            "username": user.username,
        }
    })
