import pprint

from app import api, app, request, jsonify, db, jwt_required, gennis_server_url
from backend.models.basic_model import Teacher, User, Group
import requests

# --- external_server.py ---
from flask import request, jsonify
import requests


@app.route(f'{api}/create_test/<int:group_id>', methods=["PUT", "POST", "DELETE"])
def create_test(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if not group or not group.platform_id:
        return jsonify({"success": False, "msg": "Group or platform ID not found"}), 404

    target_url = f"{gennis_server_url}/api/create_test_classroom/{group.platform_id}"

    if request.method in ['POST', 'PUT']:
        if request.content_type.startswith("multipart/form-data"):
            file = request.files.get('file')
            files = {}
            if file:
                files['file'] = (file.filename, file.stream, file.mimetype)

            data = {
                'info': request.form.get('info')
            }

            response = requests.request(
                method=request.method,
                url=target_url,
                data=data,
                files=files
            )
        else:
            response = requests.request(
                method=request.method,
                url=target_url,
                json=request.get_json()
            )

    elif request.method == 'DELETE':
        response = requests.delete(target_url, json=request.get_json())

    return jsonify(response.json())


@app.route(f'{api}/filter_test_datas/<int:group_id>', methods=["GET", "POST"])
@jwt_required()
def filter_datas_in_group(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if group.platform_id:
        if request.method == 'GET':
            response = requests.get(f"{gennis_server_url}/api/filter_datas_in_group_classroom/{group.platform_id}")
            return jsonify(response.json())
        else:
            response = requests.post(f"{gennis_server_url}/api/filter_datas_in_group_classroom/{group.platform_id}",
                                     json=request.get_json())
        return jsonify(response.json())


@app.route(f'{api}/filter_test_group/<int:group_id>', methods=['POST'])
@jwt_required()
def filter_test_group(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if group.platform_id:
        response = requests.post(f"{gennis_server_url}/api/filter_test_group_classroom/{group.platform_id}",
                                 json=request.get_json())
        return jsonify(response.json())


@app.route(f'{api}/submit_test_group/<int:group_id>', methods=["POST"])
@jwt_required()
def submit_test_group(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if group.platform_id:
        response = requests.post(f"{gennis_server_url}/api/submit_test_group_classroom/{group.platform_id}",
                                 json=request.get_json())
        return jsonify(response.json())
