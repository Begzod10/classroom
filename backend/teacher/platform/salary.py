from app import api, app, request, jsonify, db, jwt_required, get_jwt_identity, platform_server, django_server
from backend.models.basic_model import User, Student, Role, Subject, Teacher, StudentSubject
import requests
from backend.basics.platform.utils import check_group_info, check_user_gennis, check_user_turon
from flask_jwt_extended import create_access_token, create_refresh_token


@app.route(f'{api}/teacher_salary_info', methods=['GET'])
@jwt_required()
def teacher_salary_info():
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()

    if user.system_name == "gennis":
        response = requests.get(f"{platform_server}/api/salary_info_classroom/{user.platform_id}")
        print(response.json())
        return jsonify(
            response.json()
        )
    else:
        response = requests.get(
            f"{django_server}/api/Teachers/teacher-salary-info/{user.platform_id}/")
        print(response.json())
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
            f"{platform_server}/api/block_salary_classroom/{user.platform_id}/{location_id}/{year_id}")
        return jsonify(
            response.json()
        )
    else:
        response = requests.get(
            f"{django_server}/api/Teacher/teacher-salary-list2/{user.platform_id}/")
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
            f"{platform_server}/api/block_salary2/{user.platform_id}/{location_id}/{year_id}")
        return jsonify(
            response.json()
        )
    else:
        response = requests.get(
            f"{django_server}/api/Teachers/teacher-salary-list2/{user.platform_id}/")
        print(response.json())
        return jsonify(
            response.json()
        )


@app.route(f"{api}/teacher_salary_inside/", defaults={"status": False}, methods=["GET"])
@app.route(f'{api}/teacher_salary_inside/<int:salary_id>/<status>', methods=['GET'])
@jwt_required()
def teacher_salary_inside(salary_id, status):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    if user.system_name == "gennis":
        response = requests.get(f"{platform_server}/api/teacher_salary_inside2/{salary_id}/{user.platform_id}")
        return jsonify(
            response.json()
        )
    else:
        response = requests.get(
            f"{django_server}/api/Teacher/teacher-salary-list2/{salary_id}/?status={status}")
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
        response = requests.get(f"{platform_server}/api/black_salary2/{user.platform_id}")
        return jsonify(
            response.json()
        )
