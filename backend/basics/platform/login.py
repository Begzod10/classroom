from app import api, app, request, jsonify, db, jwt_required, get_jwt_identity, platform_server, django_server
from backend.models.basic_model import User, Student, Role, Subject, Teacher, StudentSubject
from backend.basics.settings import create_msg, edit_msg, del_msg
import requests
from pprint import pprint
from .utils import check_group_info, check_user_exists


@app.route(f'{api}/login', methods=['POST'])
def login():
    pprint(request.get_json())
    username = request.get_json()['username']
    password = request.get_json()['password']
    system_name = request.get_json()['system_name']
    user_role = request.get_json()['user_role']
    exist_user = User.query.filter(User.username == username, system_name == system_name).first()
    if not exist_user:
        if system_name == "gennis":
            response = requests.post(f"{platform_server}/api/login2", headers={
                'Content-Type': 'application/json'
            }, json={
                "username": username,
                "password": password,
                "user_role": user_role
            })
            user_get = response.json()['user']
            user = check_user_exists(user_get)
        else:
            response = requests.post(f"{django_server}/api/login", headers={
                'Content-Type': 'application/json'
            }, json={
                "username": username,
                "password": password,
                "system_name": system_name,
                "user_role": user_role
            })
            user_get = response.json()['user']
            user = check_user_exists(user_get)
    else:
        pass

    return jsonify({
        "data": "success"
    })
