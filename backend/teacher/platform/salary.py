from app import api, app, request, jsonify, db, jwt_required, get_jwt_identity, gennis_server_url, turon_server_url
from backend.models.basic_model import User, Student, Role, Subject, Teacher, StudentSubject, Group
import requests
from backend.basics.platform.utils import check_group_info, check_user_gennis, check_user_turon
from flask_jwt_extended import create_access_token, create_refresh_token


@app.route(f'{api}/teacher_salary_info', methods=['GET'])
@jwt_required()
def teacher_salary_info():
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()

    if user.system_name == "gennis":
        response = requests.get(f"{gennis_server_url}/api/salary_info_classroom/{user.platform_id}")
        return jsonify(
            response.json()
        )


@app.route(f"{api}/block_salary/", defaults={"location_id": None, "year_id": None}, methods=["GET"])
@app.route(f'{api}/block_salary/<location_id>/<year_id>')
@jwt_required()
def block_salary(location_id, year_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    if user.system_name == "gennis":
        response = requests.get(
            f"{gennis_server_url}/api/block_salary_classroom/{user.platform_id}/{location_id}/{year_id}")
        return jsonify(
            response.json()
        )
    else:
        response = requests.get(
            f"{turon_server_url}/api/Teacher/teacher-salary-list2/{user.turon_id}/")
        return jsonify(
            response.json()
        )


@app.route(f"{api}/teacher_salary/", defaults={"location_id": None, 'year_id': None}, methods=["GET"])
@app.route(f'{api}/teacher_salary/<int:location_id>/<int:year_id>', methods=['GET'])
@jwt_required()
def teacher_salary(location_id, year_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    if user.system_name == "gennis":
        response = requests.get(
            f"{gennis_server_url}/api/block_salary2/{user.platform_id}/{location_id}/{year_id}")
        return jsonify(
            response.json()
        )
    else:
        response = requests.get(
            f"{turon_server_url}/api/Teachers/teacher-salary-list2/{user.platform_id}/")
        return jsonify(
            response.json()
        )


@app.route(f'{api}/teacher_salary_inside/<int:salary_id>', methods=['GET'])
@jwt_required()
def teacher_salary_inside(salary_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    if user.system_name == "gennis":

        response = requests.get(f"{gennis_server_url}/api/teacher_salary_inside_classroom/{user.platform_id}/{salary_id}")

        return jsonify(
            response.json()
        )
    else:
        response = requests.get(
            f"{turon_server_url}/api/Teacher/teacher-salary-list2/{salary_id}/?status={status}")
        print(response.json())

        return jsonify(
            response.json()
        )


@app.route(f'{api}/teacher_black_salary', methods=['GET'])
@jwt_required()
def teacher_black_salary():
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    if user.system_name == "gennis":
        response = requests.get(f"{gennis_server_url}/api/black_salary_classroom/{user.platform_id}")
        return jsonify(
            response.json()
        )


@app.route(f'{api}/teacher_locations')
@jwt_required()
def teacher_locations():
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    if user.system_name == "gennis":
        response = requests.get(f"{gennis_server_url}/api/teacher_locations_classroom/{user.platform_id}")
        return jsonify(
            response.json()
        )


@app.route(f'{api}/user_time_table/', defaults={"location_id": None})
@app.route(f'{api}/user_time_table/<location_id>/')
@jwt_required()
def user_time_table(location_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    student = Student.query.filter(Student.user_id == user.id).first()
    teacher = Teacher.query.filter(Teacher.user_id == user.id).first()
    if user.system_name == "gennis":
        response = requests.get(f"{gennis_server_url}/api/user_time_table_classroom/{user.platform_id}/{location_id}")
        return jsonify(
            response.json()
        )
    else:
        if student:
            group_id = student.groups[0].id
        else:
            group_id = teacher.groups[0].id
        group = Group.query.filter(Group.id == group_id).first()
        response = requests.get(f"{turon_server_url}/api/SchoolTimeTable/time_table_mobile/{group.turon_id}")
        return jsonify(
            response.json()
        )
    pass
