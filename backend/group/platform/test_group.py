from app import api, app, request, jsonify, db, jwt_required, platform_server
from backend.models.basic_model import Teacher, User, Group
import requests


@app.route(f'{api}/filter_test_datas/<int:group_id>', methods=["GET", "POST"])
@jwt_required()
def filter_datas_in_group(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if group.platform_id:
        if request.method == 'GET':
            response = requests.get(f"{platform_server}/api/filter_datas_in_group_classroom/{group.platform_id}")
            return jsonify(response.json())
        else:
            response = requests.post(f"{platform_server}/api/filter_datas_in_group_classroom/{group.platform_id}",
                                     json=request.get_json())
        return jsonify(response.json())


@app.route(f'{api}/filter_test_group/<int:group_id>', methods=['POST'])
@jwt_required()
def filter_test_group(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if group.platform_id:
        response = requests.post(f"{platform_server}/api/filter_test_group_classroom/{group.platform_id}",
                                 json=request.get_json())
        return jsonify(response.json())


@app.route(f'{api}/submit_test_group/<int:group_id>', methods=["POST"])
@jwt_required()
def submit_test_group(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if group.platform_id:
        response = requests.post(f"{platform_server}/api/submit_test_group_classroom/{group.platform_id}",
                                 json=request.get_json())
        return jsonify(response.json())
