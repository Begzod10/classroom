from app import cross_origin, db, request, jsonify
from backend.configs import gennis_server_url
import requests
from backend.parent.models import Parent
from backend.models.basic_model import User, Role
from sqlalchemy import desc
from flask import Blueprint

get_parent_bp = Blueprint('parent_get', __name__)


@get_parent_bp.route('/get_list/<int:location_id>', defaults={'deleted': False}, methods=['GET'])
@get_parent_bp.route('/get_list/<int:location_id>/<deleted>', methods=['GET'])
def parent_list(location_id, deleted):
    role = Role.query.filter(Role.type_role == 'parent').first()
    if not role:
        role = Role(role='pa21s122s', type_role='parent')
        role.add()
    parents = Parent.query.join(User).filter(User.location_id == location_id, User.deleted == deleted,
                                             User.role_id == role.id).order_by(desc(Parent.id)).all()
    parents_list = [parent.convert_json() for parent in parents]
    return jsonify(parents_list)


@get_parent_bp.route('/student_attendance_dates/<platform_id>', methods=['GET'])
def student_attendance_dates(platform_id):
    response = requests.get(f"{gennis_server_url}/api/student_attendance_dates_classroom/{platform_id}",
                            headers={
                                'Content-Type': 'application/json'
                            })
    attendance_response = response.json()
    return jsonify(attendance_response)


@get_parent_bp.route('/student_group_list/<platform_id>', methods=['GET'])
def student_group_list(platform_id):
    response = requests.get(f"{gennis_server_url}/api/get_student_group_list/{platform_id}",
                            headers={
                                'Content-Type': 'application/json'
                            })
    group_response = response.json()
    return jsonify(group_response)


@get_parent_bp.route('/student_attendance/<platform_id>/', defaults={"group_id": None, "year": None, "month": None})
@get_parent_bp.route('/student_attendance/<platform_id>/<group_id>/<year>/<month>', methods=['GET'])
def student_attendance(platform_id, group_id, year, month):
    if group_id == "None" or group_id == None:
        if year == None:
            response = requests.get(
                f"{gennis_server_url}/api/get_student_attendance_days_list/{platform_id}/",
                headers={
                    'Content-Type': 'application/json'
                })
        else:
            response = requests.get(
                f"{gennis_server_url}/api/get_student_attendance_days_list/{platform_id}/{group_id}/{year}/{month}",
                headers={
                    'Content-Type': 'application/json'
                })
    else:
        response = requests.get(
            f"{gennis_server_url}/api/get_student_attendance_days_list/{platform_id}/{group_id}/{year}/{month}",
            headers={
                'Content-Type': 'application/json'
            })
    group_response = response.json()
    return jsonify(group_response)


@get_parent_bp.route('/student_payments/<platform_id>', methods=['GET'])
def student_payments(platform_id):
    response = requests.get(
        f"{gennis_server_url}/api/student_payments_list/{platform_id}",
        headers={
            'Content-Type': 'application/json'
        })
    student_response = response.json()
    return jsonify(student_response)


@get_parent_bp.route('/student_tests_data/<int:group_id>', methods=['GET'])
def student_tests_data(group_id):
    response = requests.get(
        f"{gennis_server_url}/api/filter_datas_in_group_classroom/{group_id}",
        headers={
            'Content-Type': 'application/json'
        })
    datas_response = response.json()
    return jsonify(datas_response)


@get_parent_bp.route('/student_tests/<group_id>/<month>/<year>', methods=['GET'])
def student_tests(group_id, month, year):
    group_id = int(group_id)
    month = int(month.lstrip("0"))
    year = int(year)

    response = requests.get(
        f"{gennis_server_url}/api/filter_test_classroom/{group_id}/{month}/{year}",
        headers={'Content-Type': 'application/json'}
    )
    datas_response = response.json()
    return jsonify(datas_response)


@get_parent_bp.route('/student_payments', methods=['GET'])
def student_payments_cl():
    id = request.args.get('id', type=int)
    payment_status = request.args.get('payment', type=lambda v: v.lower() == 'true')
    response = requests.get(
        f"{gennis_server_url}/api/parent/student_payments?id={id}&payment={payment_status}",
        headers={
            'Content-Type': 'application/json'
        })
    datas_response = response.json()
    return jsonify(datas_response)
