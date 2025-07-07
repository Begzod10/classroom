from app import api, app, request, jsonify, db, jwt_required, get_jwt_identity, gennis_server_url, turon_server_url
from backend.models.basic_model import User, Student, Role, Subject, Teacher, StudentSubject
from backend.basics.settings import create_msg, edit_msg, del_msg
import requests
from pprint import pprint
from .utils import check_group_info, check_user_gennis, check_user_turon, check_exist_classroom_id, \
    add_gennis_user_data, add_parent_gennis
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash


@app.route(f'{api}/login', methods=['POST'])
def login():
    username = request.get_json()['username']
    password = request.get_json()['password']
    system_name = request.get_json()['system_name'] if "system_name" in request.get_json() else ""

    user = User.query.filter(User.username == username, system_name == system_name).first()
    if system_name and username != "metod":
        if system_name == "gennis":
            response = requests.post(f"{gennis_server_url}/api/login2", headers={
                'Content-Type': 'application/json'
            }, json={
                "username": username,
                "password": password,
            })
            user_get = response.json()['user'] if 'user' in response.json() else {}
            if not user_get:
                return {"msg": "Username yoki parol noto'g'ri", "success": False}, 200
            if not user:
                user = check_user_gennis(user_get)
        else:
            response = requests.post(f"{turon_server_url}/api/token/", headers={
                'Content-Type': 'application/json'
            }, json={
                "username": username,
                "password": password,
            })
            user_get = response.json()['user'] if 'user' in response.json() else {}
            if not user_get:
                return {"msg": "Username yoki parol noto'g'ri", "success": False}, 200
            if not user:
                user = check_user_turon(user_get)
        if user:
            # if user.role.type == "parent":
            #     response = requests.get(f"{gennis_server_url}/api/send_parent_data/{user.platform_id}", headers={
            #         'Content-Type': 'application/json'
            #     })
            #     user_get = response.json()['user']
            #     add_parent_gennis(user_get, user)
            if user.role.type != "methodist" and user.role.type != "parent":
                if system_name == "gennis":
                    response = requests.get(f"{gennis_server_url}/api/send_user_data/{user.platform_id}", headers={
                        'Content-Type': 'application/json'
                    })
                    user_get = response.json()['user']
                    add_gennis_user_data(user_get, user)

        if not user.classroom_user_id:
            classroom_user_id = check_exist_classroom_id()
            user.classroom_user_id = classroom_user_id
            db.session.commit()
        user.system_name = system_name
        db.session.commit()
    else:
        # user.classroom_user_id = "746fd4f7d00311efa46700155d96426c"
        # db.session.commit()
        if user and check_password_hash(user.password, password):
            return jsonify({
                "data": {
                    "info": user.convert_json(),
                    "access_token": create_access_token(identity=user.classroom_user_id),
                    "refresh_token": create_refresh_token(identity=user.classroom_user_id)
                }
            })
        else:
            return {"msg": "Username yoki parol noto'g'ri", "success": False}, 200

    return jsonify({
        "data": {
            "info": user.convert_json(),
            "access_token": create_access_token(identity=user.classroom_user_id),
            "refresh_token": create_refresh_token(identity=user.classroom_user_id)
        }
    })
