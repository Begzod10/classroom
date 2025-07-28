from app import request, jsonify, db, jwt_required
from backend.models.basic_model import Student, User
import requests
from flask import Blueprint
from backend.configs import gennis_server_url, turon_server_url
from flask_jwt_extended import get_jwt_identity

payment_bp = Blueprint('payment', __name__)


@payment_bp.route(f'/student_attendance_info')
@jwt_required()
def student_attendance_info():
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    if user.system_name == "gennis":
        response = requests.get(f"{gennis_server_url}/api/student_attendance_info_classroom/{user.platform_id}")
        return jsonify(response.json())
    pass
