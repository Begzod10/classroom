from app import api, app, request, jsonify, db, contains_eager, or_
from backend.models.basic_model import Teacher, User
from backend.models.settings import iterate_models


@app.route(f'{api}/update_teacher_balance/<user_id>/<system_name>')
def update_teacher_balance(user_id, system_name):
    if system_name == "gennis":
        user = User.query.filter(User.platform_id == user_id).first()
    else:
        user = User.query.filter(User.turon_id == user_id).first()
    teacher = Teacher.query.filter(Teacher.user_id == user.id).first()
    teacher.balance = request.get_json()['balance']
    db.session.commit()

    return jsonify({"msg": "Balance o'zgartirildi"})
