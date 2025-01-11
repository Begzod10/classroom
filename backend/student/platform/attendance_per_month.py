from app import api, app, request, jsonify, db, jwt_required, get_jwt_identity, platform_server, django_server
from backend.models.basic_model import Student, User
import requests


@app.route(f'{api}/attendance_per_month_list/<int:student_id>', methods=['GET'])
@jwt_required()
def attendance_per_month_list(student_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    if user.system_name == "gennis":
        pass
    else:
        response = requests.get(
            f"{django_server}/api/Students/missing_month2/{student_id}/")
        return jsonify(
            response.json()
        )
