import requests
from backend.models.basic_model import User, Teacher, db
from flask import Blueprint

from app import request, jsonify, jwt_required, get_jwt_identity
from backend.configs import turon_server_url

requests_blueprint = Blueprint('requests', __name__)


def get_teacher_and_system(turon_id):
    teacher = Teacher.query.filter_by(turon_id=turon_id).first()
    if not teacher:
        return None, None
    return teacher, teacher.user.system_name


@requests_blueprint.route("/requests", methods=["POST"])
def create_teacher_request():
    data = request.json
    turon_id = request.args.get("turon_id")
    print(turon_id)
    teacher, system_name = get_teacher_and_system(turon_id)
    if not teacher:
        return jsonify({"error": "Teacher not found"}), 404
    print(system_name)
    if system_name == "turon":
        response = requests.post(f'{turon_server_url}/api/Teachers/teacher-requests/', json=data,
                                 params=request.args.to_dict())
        return jsonify(response.json()), response.status_code

    elif system_name == "gennis":
        return jsonify({"error": "Not implemented for gennis yet"}), 400

    return jsonify({"error": "Invalid system_name"}), 400


@requests_blueprint.route("/requests", methods=["GET"])
def get_teacher_requests():
    turon_id = request.args.get("turon_id")
    teacher, system_name = get_teacher_and_system(turon_id)
    if not teacher:
        return jsonify({"error": "Teacher not found"}), 404

    if system_name == "turon":
        response = requests.get(f'{turon_server_url}/api/Teachers/teacher-requests/', params=request.args.to_dict())
        return jsonify(response.json()), response.status_code

    elif system_name == "gennis":
        return jsonify({"error": "Not implemented for gennis yet"}), 400

    return jsonify({"error": "Invalid system_name"}), 400


@requests_blueprint.route("/requests/<int:id>", methods=["PATCH", "PUT"])
def update_teacher_request(id):
    data = request.json
    turon_id = request.args.get("turon_id")
    teacher, system_name = get_teacher_and_system(turon_id)

    if not teacher:
        return jsonify({"error": "Teacher not found"}), 404

    if system_name == "turon":
        response = requests.patch(f"{turon_server_url}/api/Teachers/teacher-requests/{id}/", json=data)
        return jsonify(response.json()), response.status_code
    elif system_name == "gennis":
        return jsonify({"error": "Gennis uchun hali implement qilinmagan"}), 400

    return jsonify({"error": "Invalid system_name"}), 400


@requests_blueprint.route("/requests/<int:id>", methods=["DELETE"])
def delete_teacher_request(id):
    turon_id = request.args.get("turon_id")
    teacher, system_name = get_teacher_and_system(turon_id)

    if not teacher:
        return jsonify({"error": "Teacher not found"}), 404

    if system_name == "turon":
        response = requests.delete(f"{turon_server_url}/api/Teachers/teacher-requests/{id}/")
        if response.status_code == 204:
            return jsonify({"success": True}), 204
        return jsonify(response.json()), response.status_code
    elif system_name == "gennis":
        return jsonify({"error": "Gennis uchun hali implement qilinmagan"}), 400

    return jsonify({"error": "Invalid system_name"}), 400
