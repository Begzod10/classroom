from app import api, app, request, jsonify, db, jwt_required, get_jwt_identity, gennis_server_url, turon_server_url
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
            f"{turon_server_url}/api/Students/missing_month2/{student_id}/")
        return jsonify(
            response.json()
        )


@app.route(f'{api}/student_group_dates/<int:student_id>', methods=['GET', 'POST'])
@jwt_required()
def student_group_dates(student_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()

    if request.method == "GET":
        response = requests.get(f'{gennis_server_url}/api/student_group_dates2_classroom/{user.platform_id}/')
        return jsonify(response.json())


@app.route(f'{api}/combined_attendances2/<int:student_id>', methods=['GET', 'POST'])
@jwt_required()
def combined_attendances2(student_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()

    if request.method == "GET":
        response = requests.get(f'{gennis_server_url}/api/combined_attendances_classroom/{user.platform_id}/')
        return jsonify(response.json())
    else:
        response = requests.post(f'{gennis_server_url}/api/combined_attendances_classroom/{user.platform_id}/',
                                 json=request.get_json())
        return jsonify(response.json())
