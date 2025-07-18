from app import db, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from backend.models.basic_model import User, SubjectLevel, StudentLevel, Student
from backend.basics.settings import create_msg, edit_msg, del_msg
from backend.models.settings import iterate_models, send_subject_server
import requests
from backend.configs import gennis_server_url
from flask import Blueprint

level_bp = Blueprint('level_folder', __name__)


@level_bp.route(f'/info/<int:subject_id>', methods=['POST', 'GET'])
@jwt_required()
def info_level(subject_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    subject_levels = SubjectLevel.query.filter(SubjectLevel.subject_id == subject_id,
                                               SubjectLevel.disabled == False).order_by(SubjectLevel.id).all()
    server_levels = SubjectLevel.query.order_by(
        SubjectLevel.id).all()
    if user.student:
        student = Student.query.filter(Student.user_id == user.id).first()
        student_level = StudentLevel.query.filter(StudentLevel.subject_id == subject_id,
                                                  StudentLevel.student_id == student.id).join(SubjectLevel).order_by(
            SubjectLevel.id).all()
        return jsonify({
            "data": iterate_models(student_level)
        })
    if request.method == "POST":
        get_json = request.get_json()
        name = get_json['name']
        desc = get_json['desc']
        try:
            add = SubjectLevel(name=name, desc=desc, subject_id=subject_id)
            add.add_commit()
            subject_levels = SubjectLevel.query.filter(SubjectLevel.subject_id == subject_id,
                                                       SubjectLevel.disabled == False).order_by(
                SubjectLevel.id).all()
            server_levels = SubjectLevel.query.order_by(
                SubjectLevel.id).all()
            send_subject_server("levels", gennis_server_url, server_levels)
            return create_msg(f"{name}", status=True, data=iterate_models(subject_levels))

        except:
            return create_msg(f"{name}", status=False, data=iterate_models(subject_levels))

    else:
        return jsonify({
            "data": iterate_models(subject_levels)
        })


@level_bp.route(f'/deleted/<int:subject_id>')
@jwt_required()
def deleted_levels(subject_id):
    subject_levels = SubjectLevel.query.filter(SubjectLevel.subject_id == subject_id,
                                               SubjectLevel.disabled == True).order_by(SubjectLevel.id).all()
    return jsonify({
        "data": iterate_models(subject_levels)
    })


@level_bp.route(f'/profile/<int:level_id>')
@jwt_required()
def profile(level_id):
    level_get = SubjectLevel.query.filter(SubjectLevel.id == level_id).first()
    return jsonify({
        "data": level_get.convert_json()
    })


@level_bp.route(f'/crud/<int:level_id>', methods=['POST', 'DELETE'])
@jwt_required()
def crud(level_id):
    if request.method == "POST":
        get_json = request.get_json()
        name = get_json['name']
        desc = get_json['desc']
        level = SubjectLevel.query.filter(SubjectLevel.id == level_id).first()
        try:
            SubjectLevel.query.filter(SubjectLevel.id == level_id).update({
                "name": name,
                "desc": desc
            })
            db.session.commit()
            server_levels = SubjectLevel.query.order_by(
                SubjectLevel.id).all()
            send_subject_server("levels", gennis_server_url, server_levels)
            return edit_msg(f"{name}", status=True, data=level.convert_json())
        except:
            return edit_msg(f"{name}", status=False, data=level.convert_json())
    else:
        level_name = SubjectLevel.query.filter(SubjectLevel.id == level_id).first()
        name = level_name.name
        if level_name.disabled:
            level_name.disabled = False
            db.session.commit()
            server_levels = SubjectLevel.query.order_by(
                SubjectLevel.id).all()
            send_subject_server("levels", gennis_server_url, server_levels)
            return edit_msg(f"{name}", status=True)
        else:
            level_name.disabled = True
            db.session.commit()
            server_levels = SubjectLevel.query.order_by(
                SubjectLevel.id).all()
            send_subject_server("levels", gennis_server_url, server_levels)
            return del_msg(item=name, status=True)
