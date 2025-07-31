from flasgger import swag_from
from flask import Blueprint

from app import jsonify, db
from sqlalchemy import or_
from sqlalchemy.orm import contains_eager
from backend.models.basic_model import Group, Student, Teacher, User

group_bp = Blueprint('group_bp', __name__)


@group_bp.route('/delete_student_from_group/<user_id>/<group_id>/<system_name>', methods=['DELETE'])
# @app.route(f'{api}/delete_student_from_group/<user_id>/<group_id>/<system_name>', methods=['DELETE'])
@swag_from({'tags': ['Group'], "methods": ["DELETE"]})
def delete_student_from_group(user_id, group_id, system_name):
    if system_name == "gennis":
        user = User.query.filter(User.platform_id == user_id).first()
        group = Group.query.filter(Group.platform_id == group_id).first()
    else:
        user = User.query.filter(User.turon_id == user_id).first()
        group = Group.query.filter(Group.turon_id == group_id).first()
    student = Student.query.filter(Student.user_id == user.id).first()
    group.students.remove(student)
    db.session.commit()
    return jsonify({"msg": "O'chirildi"})


@group_bp.route('/delete_teacher_from_group/<user_id>/<group_id>/<system_name>', methods=['DELETE'])
# @app.route(f'{api}/delete_teacher_from_group/<user_id>/<group_id>/<system_name>', methods=['DELETE'])
@swag_from({'tags': ['Group'], "methods": ["DELETE"]})
def delete_teacher_from_group(user_id, group_id, system_name):
    if system_name == "gennis":
        user = User.query.filter(User.platform_id == user_id).first()
        group = Group.query.filter(Group.platform_id == group_id).first()
    else:
        user = User.query.filter(User.turon_id == user_id).first()
        group = Group.query.filter(Group.turon_id == group_id).first()
    teacher = Teacher.query.filter(Teacher.user_id == user.id).first()
    group.teachers.remove(teacher)
    db.session.commit()
    return jsonify({"msg": "O'chirildi"})


@group_bp.route('/delete_group/<group_id>/<system_name>', methods=['DELETE'])
@swag_from({'tags': ['Group'], "methods": ["DELETE"]})
# @app.route(f'{api}/delete_group/<group_id>/<system_name>', methods=['DELETE'])
def delete_group(group_id, system_name):
    if system_name == "gennis":
        group = Group.query.filter(Group.platform_id == group_id).first()
    else:
        group = Group.query.filter(Group.turon_id == group_id).first()
    students = db.session.query(Student).join(Student.groups).options(contains_eager(Student.groups)).filter(
        Group.id == group.id).all()
    teacher = Teacher.query.filter(Teacher.id == group.teacher_id).first()
    group.teachers.remove(teacher)
    for student in students:
        student.groups.remove(group)
    db.session.delete(group)
    db.session.commit()
    return jsonify({"msg": "O'chirildi"})
