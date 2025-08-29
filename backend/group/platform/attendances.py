import requests
from flasgger import swag_from
from flask import Blueprint

from app import request, jsonify, jwt_required, get_jwt_identity
from backend.configs import turon_server_url, gennis_server_url
from backend.models.basic_model import User, Group

attendance_bp = Blueprint('attendance_bp', __name__)


@attendance_bp.route('/attendance_classroom/<group_id>')
@swag_from({'tags': ['Attendance'], "methods": ["GET"]})
# @app.route(f'{api}/attendance_classroom/<group_id>')
@jwt_required()
def attendance_classroom(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if group.platform_id:
        response = requests.get(
            f"{gennis_server_url}/api/group_classroom_attendance/attendance_classroom/{group.platform_id}")
        return jsonify(response.json())
    pass


@attendance_bp.route('/make_attendance_classroom', methods=['POST'])
@swag_from({'tags': ['Attendance'], "methods": ["POST"]})
# @app.route(f'{api}/make_attendance_classroom', methods=['POST'])
@jwt_required()
def make_attendance_classroom():
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    if user.system_name == "gennis":
        response = requests.post(f"{gennis_server_url}/api/group_classroom_attendance/make_attendance_classroom",
                                 json=request.get_json())
        return jsonify(response.json())


@attendance_bp.route('/make_attendance_classroom_mobile', methods=['POST'])
@swag_from({'tags': ['Attendance'], "methods": ["POST"]})
# @app.route(f'{api}/make_attendance_classroom_mobile', methods=['POST'])
@jwt_required()
def make_attendance_classroom_mobile():
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    if user.system_name == "gennis":
        response = requests.post(f"{gennis_server_url}/api/group_classroom_attendance/make_attendance_classroom_mobile",
                                 json=request.get_json())
        return jsonify(response.json())


@attendance_bp.route('/delete_attendance_classroom/<int:attendance_id>/<int:student_id>/<int:group_id>',
                     methods=['GET'])
@swag_from({'tags': ['Attendance'], "methods": ["GET"]})
# @app.route(f'{api}/delete_attendance_classroom/<int:attendance_id>/<int:student_id>/<int:group_id>', methods=['GET'])
@jwt_required()
def delete_attendance_classroom(attendance_id, student_id, group_id):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    if user.system_name == "gennis":
        response = requests.get(
            f"{gennis_server_url}/api/group_classroom_attendance/delete_attendance_classroom/{attendance_id}/{student_id}/{group_id}")
        return jsonify(response.json())


@attendance_bp.route('/group_dates2/<int:group_id>')
@swag_from({'tags': ['Attendance'], "methods": ["GET"]})
# @app.route(f'{api}/group_dates2/<int:group_id>')
@jwt_required()
def group_dates2(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if group.platform_id:
        response = requests.get(
            f"{gennis_server_url}/api/group_classroom_attendance/group_dates2_classroom/{group.platform_id}")
        return jsonify(response.json())
    else:
        response = requests.get(f"{turon_server_url}/api/Attendance/attendance-days-mobile/{group.turon_id}")
        return jsonify(response.json())
    pass


@attendance_bp.route('/attendances/<group_id>', methods=['GET', 'POST'])
@swag_from({'tags': ['Attendance'], "methods": ["GET", "POST"]})
# @app.route(f'{api}/attendances/<group_id>', methods=['GET', 'POST'])
@jwt_required()
def attendances(group_id):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()

    group = Group.query.filter(Group.id == group_id).first()
    print(user.system_name)
    if user.system_name == "gennis":
        if request.method == 'GET':
            response = requests.get(
                f"{gennis_server_url}/api/group_classroom_attendance/attendances_classroom/{group.platform_id}")
            return jsonify(response.json())
        else:
            response = requests.post(
                f"{gennis_server_url}/api/group_classroom_attendance/attendances_classroom/{group.platform_id}",
                json=request.get_json())
            return jsonify(response.json())
    else:
        if request.method == 'GET':
            response = requests.get(f"{turon_server_url}/api/Attendance/attendance_list_school/{group.turon_id}/")
            return jsonify(response.json())
        else:
            response = requests.post(f"{turon_server_url}/api/Attendance/attendance_list_school/{group.turon_id}/",
                                     json=request.get_json())
        return jsonify(response.json())


@attendance_bp.route('/group_time_table2/<group_id>')
@swag_from({'tags': ['Attendance'], "methods": ["GET"]})
# @app.route(f'{api}/group_time_table2/<group_id>')
@jwt_required()
def group_time_table(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    if user.system_name == "gennis":
        response = requests.get(
            f"{gennis_server_url}/api/group_classroom_attendance/group_time_table_classroom/{group.platform_id}")
        return jsonify(response.json())
    else:
        response = requests.get(f"{turon_server_url}/api/SchoolTimeTable/time_table_mobile/{group.turon_id}")
        return jsonify(response.json())
    pass
