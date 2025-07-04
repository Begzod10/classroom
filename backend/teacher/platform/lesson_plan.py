from app import api, app, request, jsonify, db, jwt_required, get_jwt_identity, gennis_server_url
from backend.models.basic_model import Teacher, User, Group
from backend.models.settings import iterate_models
import requests


@app.route(f'{api}/lesson_plan_list/<int:group_id>', defaults={"date": None})
@app.route(f'{api}/lesson_plan_list/<int:group_id>/<date>')
@jwt_required()
def lesson_plan_list(group_id, date):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    group = Group.query.filter(Group.id == group_id).first()
    if user.system_name == "gennis":
        response = requests.get(
            f"{gennis_server_url}/api/lesson_plan_list_classroom/{group.platform_id}/{date}")
        return jsonify(response.json())


@app.route(f'{api}/get_lesson_plan/<group_id>', methods=['POST'])
@jwt_required()
def get_lesson_plan(group_id):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    group = Group.query.filter(Group.id == group_id).first()
    if user.system_name == "gennis":
        response = requests.post(
            f"{gennis_server_url}/api/get_lesson_plan_classroom/{group.platform_id}", json=request.get_json())
        return jsonify(response.json())


@app.route(f'{api}/change_lesson_plan/<plan_id>', methods=['POST'])
@jwt_required()
def change_lesson_plan(plan_id):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    if user.system_name == "gennis":
        response = requests.post(
            f"{gennis_server_url}/api/change_lesson_plan_classroom/{plan_id}", json=request.get_json())
        return jsonify(response.json())
