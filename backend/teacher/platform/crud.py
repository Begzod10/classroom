from flask import Blueprint

from app import request, jsonify, db
from backend.models.basic_model import Teacher, User

teacher_blueprint = Blueprint('teacher', __name__)
from flasgger import swag_from


@teacher_blueprint.route('/update_teacher_balance/<user_id>/<system_name>', methods=['POST'])
@swag_from({'tags': ['Teacher'], "methods": ["POST"]})
# @app.route(f'{api}/update_teacher_balance/<user_id>/<system_name>', methods=['POST'])
def update_teacher_balance(user_id, system_name):
    if system_name == "gennis":
        user = User.query.filter(User.platform_id == user_id).first()
    else:
        user = User.query.filter(User.turon_id == user_id).first()
    if user:
        teacher = Teacher.query.filter(Teacher.user_id == user.id).first()
        teacher.balance = request.get_json()['balance']
        db.session.commit()

        return jsonify({"msg": "Balance o'zgartirildi"})
    else:
        return jsonify({"msg": "Bunday foydalanuvchi mavjud emas"})
