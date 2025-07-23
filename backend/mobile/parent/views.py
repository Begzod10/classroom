from app import api, app, cross_origin, db, request, jsonify
from backend.basics.settings import gennis_server_url
import requests
from backend.parent.models import Parent
from backend.models.basic_model import User, Role
from sqlalchemy import desc
from flask import Blueprint

get_mobile_parent_bp = Blueprint('parent_get', __name__)


@get_mobile_parent_bp.route('/student_group_list/<username>', methods=['GET'])
def mobile_student_group_list(username):
    response = requests.get(f"{gennis_server_url}/api/mobile/student_group_list/{username}",
                            headers={
                                'Content-Type': 'application/json'
                            })
    group_response = response.json()
    return jsonify(group_response)


@get_mobile_parent_bp.route('/student_attendance/<username>/<group_id>/<year>/<month>', methods=['GET'])
def mobile_student_attendance(username, group_id, year, month):
    response = requests.get(
        f"{gennis_server_url}/api/mobile/get_student_attendance_days_list/{username}/{group_id}/{year}/{month}",
        headers={
            'Content-Type': 'application/json'
        })
    group_response = response.json()
    return jsonify(group_response)


@get_mobile_parent_bp.route('/get_student_ranking/<username>/<group_id>/<year>/<month>', methods=['GET'])
def get_student_ranking(username, group_id, year, month):
    response = requests.get(
        f"{gennis_server_url}/api/mobile/get_student_ranking/{username}/{group_id}/{year}/{month}",
        headers={
            'Content-Type': 'application/json'
        })
    group_response = response.json()
    return jsonify(group_response)


@get_mobile_parent_bp.route('/get_lesson_plan_list/<group_id>/<year>/<month>', methods=['GET'])
def get_lesson_plan_list(group_id, year, month):
    response = requests.get(
        f"{gennis_server_url}/api/mobile/get_lesson_plan_list/{group_id}/{year}/{month}",
        headers={
            'Content-Type': 'application/json'
        })
    group_response = response.json()
    return jsonify(group_response)


@get_mobile_parent_bp.route('/get_lesson_plan/<int:id>', methods=['GET'])
def get_lesson_plan_list(id):
    response = requests.get(
        f"{gennis_server_url}/api/mobile/lesson_plan_profile/{id}",
        headers={
            'Content-Type': 'application/json'
        })
    group_response = response.json()
    return jsonify(group_response)


@get_mobile_parent_bp.route('/student_profile/<username>', methods=['GET', 'PUT'])
def student_profile(username):
    user = User.query.filter_by(username=username).first()

    if request.method == "GET":
        day = str(user.born_day).zfill(2)
        month = str(user.born_month).zfill(2)

        return jsonify({
            "name": user.name,
            "surname": user.surname,
            "username": user.username,
            "balance": user.balance,
            "father_name": user.father_name,
            "born_date": f"{day}-{month}-{user.born_year}",
            "phone": user.phone,
        })

    elif request.method == "PUT":
        data = request.get_json()

        user.name = data.get('name', user.name)
        user.surname = data.get('surname', user.surname)
        user.father_name = data.get('father_name', user.father_name)
        user.phone = data.get('phone', user.phone)

        born_date = data.get('born_date')
        if born_date:
            try:
                day, month, year = map(int, born_date.split('-'))
                user.born_day = day
                user.born_month = month
                user.born_year = year
            except:
                return jsonify({"error": "Tug‘ilgan sana noto‘g‘ri formatda. To‘g‘ri format: DD-MM-YYYY"}), 400

        db.session.commit()

        response = requests.put(
            f"{gennis_server_url}/api/mobile/student_profile_edit/{username}",
            json=data,
            headers={
                'Content-Type': 'application/json'
            }
        )

        day = str(user.born_day).zfill(2)
        month = str(user.born_month).zfill(2)

        return jsonify({
            "name": user.name,
            "surname": user.surname,
            "username": user.username,
            "balance": user.balance,
            "father_name": user.father_name,
            "born_date": f"{day}-{month}-{user.born_year}",
            "phone": user.phone,
        })
