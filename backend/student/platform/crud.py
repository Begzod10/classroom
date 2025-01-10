from app import api, app, request, jsonify, db
from backend.models.basic_model import Student, User


@app.route(f'{api}/update_student_balance/<user_id>/<system_name>')
def update_student_balance(user_id, system_name):
    if system_name == "gennis":
        user = User.query.filter(User.platform_id == user_id).first()
    else:
        user = User.query.filter(User.turon_id == user_id).first()
    student = Student.query.filter(Student.user_id == user.id).first()
    student.balance = request.get_json()['balance']
    db.session.commit()

    return jsonify({"msg": "Balance o'zgartirildi"})
