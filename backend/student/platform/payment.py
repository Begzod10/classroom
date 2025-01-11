from app import api, app, request, jsonify, db, jwt_required, get_jwt_identity, platform_server
from backend.models.basic_model import Student, User
import requests


@app.route(f'{api}/student_attendance_info')
@jwt_required()
def student_attendance_info():
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    if user.system_name == "gennis":
        response = requests.get(f"{platform_server}/api/student_attendance_info_classroom/{user.platform_id}")
        return jsonify(response.json())
    pass
