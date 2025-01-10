from app import api, app, request, jsonify, db, jwt_required, get_jwt_identity, platform_server, django_server
from backend.models.basic_model import User, Student, Role, Subject, Teacher, StudentSubject
import requests
from .utils import check_group_info, check_user_gennis, check_user_turon
from flask_jwt_extended import create_access_token, create_refresh_token


@app.route(f'{api}/teacher_salary', methods=['GET'])
@jwt_required()
def teacher_salary():
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    if user.system_name == "gennis":
        response = requests.get(f"{platform_server}/api/salary_info2/{user.platform_id}")
        return jsonify(
            response.json()
        )


@app.route(f'{api}/teacher_salary_inside/<int:salary_id>', methods=['GET'])
@jwt_required()
def teacher_salary_inside(salary_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    print(user)
    if user.system_name == "gennis":
        response = requests.get(f"{platform_server}/api/teacher_salary_inside/{salary_id}/{user.platform_id}")
        print(response)
        return jsonify(
            response.json()
        )
