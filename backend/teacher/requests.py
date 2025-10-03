import requests
from backend.models.basic_model import User, Teacher, db
from flask import Blueprint

from app import request, jsonify, jwt_required, get_jwt_identity
from backend.configs import turon_server_url, gennis_server_url

requests_blueprint = Blueprint('requests', __name__)


def get_teacher_and_system(turon_id=None, teacher_id=None):
    teacher = None
    system_name = None

    if turon_id:  # Turon uchun
        teacher = Teacher.query.filter_by(turon_id=turon_id).first()
        if teacher:
            system_name = teacher.user.system_name

    elif teacher_id:  # Gennis uchun
        teacher = Teacher.query.filter_by(id=teacher_id).first()
        if teacher:
            system_name = teacher.user.system_name

    return teacher, system_name


@requests_blueprint.route("/requests", methods=["POST"])
def create_teacher_request():
    data = request.json
    turon_id = request.args.get("turon_id")

    teacher_id = request.args.get("teacher_id")

    teacher, system_name = get_teacher_and_system(turon_id, teacher_id)
    if not teacher:
        return jsonify({"error": "Teacher not found"}), 404

    if system_name == "turon":
        response = requests.post(f'{turon_server_url}/api/Teachers/teacher-requests/', json=data,
                                 params=request.args.to_dict())
        return jsonify(response.json()), response.status_code

    elif system_name == "gennis":
        response = requests.post(f"{gennis_server_url}/api/teacher/teacher-requests",
                                 json=data)
        return jsonify(response.json()), response.status_code


@requests_blueprint.route("/requests", methods=["GET"])
def get_teacher_requests():
    turon_id = request.args.get("turon_id")
    teacher_id = request.args.get("teacher_id")

    teacher, system_name = get_teacher_and_system(turon_id, teacher_id)
    if not teacher:
        return jsonify({"error": "Teacher not found"}), 404

    if system_name == "turon":
        response = requests.get(f'{turon_server_url}/api/Teachers/teacher-requests/', params=request.args.to_dict())
        return jsonify(response.json()), response.status_code

    elif system_name == "gennis":
        response = requests.get(f"{gennis_server_url}/api/teacher/teacher-requests",
                                params=request.args.to_dict())
        return jsonify(response.json()), response.status_code

    return jsonify({"error": "Invalid system_name"}), 400


@requests_blueprint.route("/requests/<int:id>", methods=["PATCH", "PUT"])
def update_teacher_request(id):
    data = request.json
    turon_id = request.args.get("turon_id")
    teacher_id = request.args.get("teacher_id")

    teacher, system_name = get_teacher_and_system(turon_id, teacher_id)

    if not teacher:
        return jsonify({"error": "Teacher not found"}), 404

    if system_name == "turon":
        response = requests.patch(f"{turon_server_url}/api/Teachers/teacher-requests/{id}/", json=data)
        return jsonify(response.json()), response.status_code
    elif system_name == "gennis":
        response = requests.patch(f"{gennis_server_url}/api/teacher/teacher-requests/{id}", json=data)
        return jsonify(response.json()), response.status_code

    return jsonify({"error": "Invalid system_name"}), 400


@requests_blueprint.route("/requests/<int:id>", methods=["DELETE"])
def delete_teacher_request(id):
    turon_id = request.args.get("turon_id")
    teacher_id = request.args.get("teacher_id")

    teacher, system_name = get_teacher_and_system(turon_id, teacher_id)

    if not teacher:
        return jsonify({"error": "Teacher not found"}), 404

    if system_name == "turon":
        response = requests.delete(f"{turon_server_url}/api/Teachers/teacher-requests/{id}/")
        if response.status_code == 204:
            return jsonify({"success": True}), 200
        return jsonify(response.json()), response.status_code
    elif system_name == "gennis":
        response = requests.delete(f"{gennis_server_url}/api/teacher/teacher-requests/{id}")
        if response.status_code == 204:
            return jsonify({"success": True}), 200
        return jsonify(response.json()), response.status_code

    return jsonify({"error": "Invalid system_name"})
