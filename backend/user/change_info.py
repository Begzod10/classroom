import pprint

from backend.models.basic_model import User, File
from app import request, jsonify, db, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from backend.basics.settings import create_msg, edit_msg, del_msg, check_file, check_img_remove, add_file
import requests
from backend.configs import gennis_server_url, turon_server_url
from flask import Blueprint

user_bp = Blueprint('user_bp', __name__)


# @app.route(f'{api}/update_photo', methods=['POST'])
@user_bp.route(f'/update_photo', methods=['POST'])
@jwt_required()
def update_photo():
    indentity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == indentity).first()
    photo = request.files.get('file')
    if photo and check_file(photo.filename):
        get_img = add_file(photo, "img", File)
        check_img_remove(user.file_id, File)
        user.file_id = get_img
        db.session.commit()
        return edit_msg(f"Profil rasm", status=True, data=user.convert_json())
    else:
        return edit_msg(f"Profil rasm", status=False, data=user.convert_json())


# @app.route(f'{api}/change_pas_user', methods=['POST'])
@user_bp.route(f'/change_pas_user', methods=['POST'])
@jwt_required()
def change_pas_user():
    indentity = get_jwt_identity()
    json = request.get_json()
    type = json['type']
    user = User.query.filter(User.classroom_user_id == indentity).first()
    if type == "info":
        User.query.filter(User.classroom_user_id == indentity).update({
            "username": json['username']
        })
        db.session.commit()
        if user.system_name == "gennis":
            response = requests.post(f"{gennis_server_url}/api/change_student_classroom/{user.platform_id}", headers={
                'Content-Type': 'application/json'
            }, json={
                "username": json['username'],
            })
            return jsonify(response.json())

    else:
        password = json['password']
        hash = generate_password_hash(password, method='sha256')
        User.query.filter(User.classroom_user_id == indentity).update({'password': hash})
        db.session.commit()
        if user.system_name == "gennis":
            response = requests.post(f"{gennis_server_url}/api/change_student_password/{user.platform_id}", headers={
                'Content-Type': 'application/json'
            }, json={
                "password": password,
            })
            return jsonify(response.json())


# @app.route(f'{api}/check_password', methods=['POST'])
@user_bp.route(f'/check_password', methods=['POST'])
@jwt_required()
def check_password():
    identity = get_jwt_identity()
    body = {}
    password = request.get_json()['password']
    username = User.query.filter_by(classroom_user_id=identity).first()
    if username and check_password_hash(username.password, password):
        body['password'] = True
    else:
        body['password'] = False

    return jsonify(body)


# @app.route(f'{api}/check_username', methods=['POST'])
@user_bp.route(f'/check_username', methods=['POST'])
@jwt_required()
def check_username():
    indentity = get_jwt_identity()
    username = request.get_json()['username']
    user = User.query.filter_by(classroom_user_id=indentity).first()
    if user.system_name == "gennis":
        response = requests.post(f"{gennis_server_url}/api/check_exist_username/{user.platform_id}",
                                 json={
                                     "username": username
                                 })
        return jsonify(response.json())
    else:
        response = requests.post(f"{turon_server_url}/api/Users/username-check/", json={
            "username": username
        })
        return jsonify(response.json())
