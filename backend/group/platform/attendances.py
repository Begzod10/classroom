from app import api, app, request, jsonify, db, jwt_required, platform_server, get_jwt_identity, django_server
from backend.models.basic_model import Teacher, User, Group
import requests


@app.route(f'{api}/attendance_classroom/<group_id>')
@jwt_required()
def attendance_classroom(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if group.platform_id:
        response = requests.get(f"{platform_server}/api/attendance_classroom/{group.platform_id}")
        return jsonify(response.json())
    pass


@app.route(f'{api}/make_attendance_classroom', methods=['POST'])
@jwt_required()
def make_attendance_classroom():
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    if user.system_name == "gennis":
        response = requests.post(f"{platform_server}/api/make_attendance_classroom",
                                 json=request.get_json())
        return jsonify(response.json())



@app.route(f'{api}/group_dates2/<int:group_id>')
@jwt_required()
def group_dates2(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if group.platform_id:
        response = requests.get(f"{platform_server}/api/group_dates2_classroom/{group.platform_id}")
        return jsonify(response.json())
    else:
        response = requests.get(f"{django_server}/api/Attendance/attendance-days-mobile/{group.turon_id}")
        return jsonify(response.json())
    pass


@app.route(f'{api}/attendances/<group_id>',methods=['GET','POST'])
@jwt_required()
def attendances(group_id):
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()

    group = Group.query.filter(Group.id == group_id).first()
    print(user.system_name)
    if user.system_name == "gennis":
        if request.method == 'GET':
            response = requests.get(f"{platform_server}/api/attendances_classroom/{group.platform_id}")
            return jsonify(response.json())
        else:
            response = requests.post(f"{platform_server}/api/attendances_classroom/{group.platform_id}",
                                     json=request.get_json())
            return jsonify(response.json())
    else:
        if request.method == 'GET':
            response = requests.get(f"{django_server}/api/Attendance/attendance_list_school/{group.turon_id}/")
            return jsonify(response.json())
        else:
            response = requests.post(f"{django_server}/api/Attendance/attendance_list_school/{group.turon_id}/",
                                     json=request.get_json())
        return jsonify(response.json())


@app.route(f'{api}/group_time_table2/<group_id>')
@jwt_required()
def group_time_table(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    if user.system_name == "gennis":
        response = requests.get(f"{platform_server}/api/group_time_table_classroom/{group.platform_id}")
        return jsonify(response.json())
    else:
        response = requests.get(f"{django_server}/api/SchoolTimeTable/time_table_mobile/{group.turon_id}")
        return jsonify(response.json())
    pass
