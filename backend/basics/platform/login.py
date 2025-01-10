from app import api, app, request, jsonify, db, jwt_required, get_jwt_identity, platform_server, django_server
from backend.models.basic_model import User, Student, Role, Subject, Teacher, StudentSubject
from backend.basics.settings import create_msg, edit_msg, del_msg
import requests
from pprint import pprint
from .utils import check_group_info, check_user_gennis, check_user_turon
from flask_jwt_extended import create_access_token, create_refresh_token


@app.route(f'{api}/login', methods=['POST'])
def login():
    username = request.get_json()['username']
    password = request.get_json()['password']
    system_name = request.get_json()['system_name']
    user_role = request.get_json()['user_role']
    exist_user = User.query.filter(User.username == username, system_name == system_name).first()

    if system_name == "gennis":
        response = requests.post(f"{platform_server}/api/login2", headers={
            'Content-Type': 'application/json'
        }, json={
            "username": username,
            "password": password,
            "user_role": user_role
        })
        print(response.json())
        user_get = response.json()['user'] if 'user' in response.json() else {}
        if not user_get:
            return {"msg": "Username yoki parol noto'g'ri", "success": False}, 200
        user = check_user_gennis(user_get)
    else:
        response = requests.post(f"{django_server}/api/token/", headers={
            'Content-Type': 'application/json'
        }, json={
            "username": username,
            "password": password,
            "system_name": system_name,
            "user_role": user_role
        })
        user_get = response.json()['user'] if 'user' in response.json() else {}
        if not user_get:
            return {"msg": "Username yoki parol noto'g'ri", "success": False}, 200

        user = check_user_turon(user_get)
    return jsonify({
        "data": {
            "info": user.convert_json(),
            "access_token": create_access_token(identity=user.classroom_user_id),
            "refresh_token": create_refresh_token(identity=user.classroom_user_id)
        }
    })
