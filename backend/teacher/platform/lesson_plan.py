import requests
from flasgger import swag_from
from flask import Blueprint

from app import request, jsonify, jwt_required, get_jwt_identity
from backend.configs import gennis_server_url
from backend.models.basic_model import User, Group

lesson_plan_blueprint = Blueprint('lesson_plan', __name__)


@lesson_plan_blueprint.route('/lesson_plan_list/<int:group_id>', defaults={"date": None})
@lesson_plan_blueprint.route('/lesson_plan_list/<int:group_id>/<date>')
@swag_from({'tags': ['Lesson Plan'], "methods": ["GET"]})
# @app.route(f'{api}/lesson_plan_list/<int:group_id>', defaults={"date": None})
# @app.route(f'{api}/lesson_plan_list/<int:group_id>/<date>')
@jwt_required()
def lesson_plan_list(group_id, date):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    group = Group.query.filter(Group.id == group_id).first()
    if user.system_name == "gennis":
        response = requests.get(
            f"{gennis_server_url}/api/lesson_plan_list_classroom/{group.platform_id}/{date}")
        return jsonify(response.json())


@lesson_plan_blueprint.route('/get_lesson_plan/<group_id>', methods=['POST'])
# @app.route(f'{api}/get_lesson_plan/<group_id>', methods=['POST'])
@swag_from({'tags': ['Lesson Plan'], "methods": ["POST"]})
@jwt_required()
def get_lesson_plan(group_id):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    group = Group.query.filter(Group.id == group_id).first()
    if user.system_name == "gennis":
        response = requests.post(
            f"{gennis_server_url}/api/get_lesson_plan_classroom/{group.platform_id}", json=request.get_json())
        return jsonify(response.json())


@lesson_plan_blueprint.route('/change_lesson_plan/<plan_id>', methods=['POST'])
@swag_from({'tags': ['Lesson Plan'], "methods": ["POST"]})
# @app.route(f'{api}/change_lesson_plan/<plan_id>', methods=['POST'])
@jwt_required()
def change_lesson_plan(plan_id):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    if user.system_name == "gennis":
        response = requests.post(
            f"{gennis_server_url}/api/change_lesson_plan_classroom/{plan_id}", json=request.get_json())
        return jsonify(response.json())
