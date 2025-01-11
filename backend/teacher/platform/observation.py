from app import api, app, request, jsonify, db, jwt_required, get_jwt_identity, platform_server
from backend.models.basic_model import Teacher, User, Group
import requests


@app.route(f'{api}/observe_info')
@jwt_required()
def observe_info():
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    if user.system_name == "gennis":
        response = requests.get(f"{platform_server}/api/observe_info_classroom")
        return jsonify(response.json())
    pass


@app.route(f'{api}/groups_to_observe', defaults={"location_id": None}, methods=['POST', 'GET'])
@app.route(f'{api}/groups_to_observe/<int:location_id>', methods=['POST', 'GET'])
@jwt_required()
def groups_to_observe(location_id):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    if user.system_name == "gennis":
        if request.method == 'POST':
            response = requests.post(
                f"{platform_server}/api/groups_to_observe_classroom/{user.platform_id}/{location_id}",
                json=request.get_json())
            return jsonify(response.json())
        else:
            response = requests.get(
                f"{platform_server}/api/groups_to_observe_classroom/{user.platform_id}/{location_id}")
            print(response)
        return jsonify(response.json())


@app.route(f'{api}/teacher_observe/<int:group_id>', methods=['POST', 'GET'])
@jwt_required()
def teacher_observe(group_id):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    if user.system_name == "gennis":
        if request.method == 'POST':
            response = requests.post(
                f"{platform_server}/api/teacher_observe_classroom/{user.platform_id}/{group_id}",
                json=request.get_json())
            return jsonify(response.json())
        else:
            response = requests.get(
                f"{platform_server}/api/teacher_observe_classroom/{user.platform_id}/{group_id}")
        return jsonify(response.json())


@app.route(f'{api}/observed_group/<int:group_id>', defaults={"date": None})
@app.route(f'{api}/observed_group/<int:group_id>/<date>')
@jwt_required()
def observed_group(group_id, date):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    group = Group.query.filter(Group.id == group_id).first()
    if user.system_name == "gennis":
        response = requests.get(
            f"{platform_server}/api/observed_group_classroom/{group.platform_id}/{date}")
        return jsonify(response.json())


@app.route(f'{api}/observed_group_info/<int:group_id>', methods=["POST"])
@jwt_required()
def observed_group_info(group_id):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    group = Group.query.filter(Group.id == group_id).first()
    if user.system_name == "gennis":
        response = requests.post(
            f"{platform_server}/api/observed_group_info_classroom/{group.platform_id}",
            json=request.get_json())
        return jsonify(response.json())
