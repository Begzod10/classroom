from app import db, jsonify, request
from backend.models.basic_model import Student, User, Role, Location
from backend.parent.models import Parent
from werkzeug.security import generate_password_hash
from backend.basics.settings import check_exist_id
from flask import Blueprint
import pprint
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests

from backend.configs import gennis_server_url

crud_parent_bp = Blueprint('parent_crud', __name__)


@crud_parent_bp.route('/crud/', methods=['POST'])
@crud_parent_bp.route('/crud/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def parent_detail(id=None):
    role = Role.query.filter(Role.type == 'parent').first()
    if not role:
        role = Role(role='pa21s122s', type_role='parent')
        role.add()
    if request.method == 'POST':
        data = request.json
        location = Location.query.filter_by(id=data.get("location_id")).first()
        data["location_id"] = location.platform_id if location.platform_id else None
        gennis_url = f"{gennis_server_url}/api/parent/crud/"
        response = requests.post(gennis_url, json=data)
        return jsonify(response.json())

    if request.method == 'GET':
        user = User.query.get_or_404(id)
        parent = Parent.query.filter(Parent.user_id == user.id).first()
        return jsonify(parent.convert_json())
    user = User.query.get_or_404(id)
    parent = Parent.query.filter(Parent.user_id == user.id).first()

    if request.method == 'PUT':

        data = request.json
        if 'name' in data:
            user.name = data['name']
        if 'surname' in data:
            user.surname = data['surname']
        if 'phone' in data:
            user.phone[0].phone = data['phone']
        if 'address' in data:
            user.address = data['address']

        if 'born_date' in data:
            user.born_day = data['born_date'][8:10]
            user.born_month = data['born_date'][5:7]
            user.born_year = data['born_date'][0:4]
        if 'username' in data:
            user.username = data['username']
        db.session.commit()
        gennis_url = f"{gennis_server_url}/api/parent/crud/update-by-username"
        payload = {
            "username": user.username,
            **data
        }
        response = requests.put(gennis_url, json=payload)
        return jsonify(parent.convert_json())

    if request.method == 'DELETE':
        parent.students = []
        user.deleted = True
        db.session.commit()

        gennis_url = f"{gennis_server_url}/api/parent/crud/delete-by-username"
        payload = {"username": user.username}
        response = requests.delete(gennis_url, json=payload)
        return jsonify({'message': 'Parent deleted successfully'}), 204


@crud_parent_bp.route('/add_students/<int:id>', methods=['POST'])
def add_students_to_parent(id):
    parent = Parent.query.filter(Parent.id == id).first()
    data = request.json
    student_ids = data.get('student_ids', [])
    print(student_ids)
    gennis_url = f"{gennis_server_url}/api/parent/add_students/{parent.user.platform_id}"
    payload = {
        "student_ids": student_ids
    }
    response = requests.post(gennis_url, json=payload)
    db.session.commit()
    return jsonify(parent.convert_json()), 200


@crud_parent_bp.route('/remove_students/<int:id>', methods=['POST'])
def remove_students_from_parent(id):
    parent = Parent.query.filter(Parent.id == id).first()
    data = request.json
    student_id = data.get('student_id')

    student = Student.query.filter(Student.id == student_id).first()

    gennis_url = f"{gennis_server_url}/api/parent/remove_students_cl/{parent.user.platform_id}"
    payload = {
        "student_id": student.user.platform_id
    }
    response = requests.post(gennis_url, json=payload)
    db.session.commit()
    return jsonify(parent.convert_json()), 200
