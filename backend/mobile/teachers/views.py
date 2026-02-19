import requests
from flasgger import swag_from
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.configs import gennis_server_url, turon_server_url
from backend.models.basic_model import User

teacher_salary_mobile_blueprints = Blueprint('teacher_salary_mobile_blueprints', __name__)


@teacher_salary_mobile_blueprints.route('/teacher_salary_info', methods=['GET'])
@swag_from({'tags': ['Salary'], "methods": ["GET"]})
@jwt_required()
def teacher_salary_info():
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()

    if user.system_name == "gennis":
        response = requests.get(f"{gennis_server_url}/api/account/salary_info_classroom/{user.platform_id}")
        return jsonify(
            response.json()
        )


@teacher_salary_mobile_blueprints.route("/block_salary/", defaults={"location_id": None, "year_id": None},
                                        methods=["GET"])
@teacher_salary_mobile_blueprints.route('/block_salary/<location_id>/<year_id>', methods=['GET'])
@swag_from({'tags': ['Salary'], "methods": ["GET"]})
@jwt_required()
def block_salary(location_id, year_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    if user.system_name == "gennis":
        response = requests.get(
            f"{gennis_server_url}/api/account/block_salary_classroom/{user.platform_id}/{location_id}/{year_id}")
        return jsonify(
            response.json()
        )
    else:
        response = requests.get(
            f"{turon_server_url}/api/Teacher/teacher-salary-list2/{user.turon_id}/")
        return jsonify(
            response.json()
        )


@teacher_salary_mobile_blueprints.route(f'/teacher_salary_inside/<int:salary_id>', methods=['GET'])
@swag_from({'tags': ['Salary'], "methods": ["GET"]})
@jwt_required()
def teacher_salary_inside(salary_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    if user.system_name == "gennis":

        response = requests.get(
            f"{gennis_server_url}/api/account/teacher_salary_inside_classroom/{user.platform_id}/{salary_id}")

        return jsonify(
            response.json()
        )
    else:
        response = requests.get(
            f"{turon_server_url}/api/Teacher/teacher-salary-list2/{salary_id}/?status=False")
        print(response.json())

        return jsonify(
            response.json()
        )
