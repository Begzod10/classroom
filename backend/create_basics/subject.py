from app import cross_origin, db, request, jsonify, current_app
from sqlalchemy import or_
from sqlalchemy.orm import contains_eager
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.basic_model import Teacher, File, Group, StudentSubject, Chapter, SubjectLevel, StudentChapter
from backend.basics.settings import edit_msg, add_file, check_file, check_img_remove, create_msg, del_msg
from backend.models.settings import User, Subject, Student, send_subject_server, iterate_models
import json
from flask import Blueprint
from backend.configs import api, gennis_server_url, turon_server_url
from flasgger import swag_from
import requests

subject_bp = Blueprint('subject_folder', __name__)



@subject_bp.route("/list/", methods=["GET", "POST"])
@cross_origin()
@jwt_required()
@swag_from({
    'tags': ['Subject'],
    "methods": ["GET"],
})
def subject_list():
    identity = get_jwt_identity()
    user = User.query.filter_by(classroom_user_id=identity).first()
    if user.role.type == "methodist":
        subjects = Subject.query.filter(
            or_(Subject.disabled == False, Subject.disabled == None, Subject.levels != None)).order_by(
            Subject.id).all()
        # requests.post(f"{gennis_server_url}/api/classroom/subjects_add", json={"subjects": iterate_models(subjects)})
        requests.post(f"{turon_server_url}/api/Subjects/subject/", json={"data": iterate_models(subjects)})

    elif user.role.type == "student":
        student = Student.query.filter(Student.user_id == user.id).first()
        groups = db.session.query(Group).join(Group.student).options(contains_eager(Group.student)).filter(
            Student.id == student.id).all()
        subject_list = []
        if user.system_name == "school":
            student_subjects = StudentSubject.query.filter(
                StudentSubject.student_id == student.id).order_by(
                StudentSubject.id).all()
            for subject in student_subjects:
                subject_list.append(subject.subject_id)
        else:
            for gr in groups:
                if gr.platform_id:
                    if gr.subject_id not in subject_list:
                        subject_list.append(gr.subject_id)
                else:
                    for sub in gr.subjects:
                        if sub.id not in subject_list:
                            subject_list.append(sub.id)

        subjects = Subject.query.filter(Subject.id.in_(sub for sub in subject_list)).order_by(Subject.id).all()
    else:
        teacher = Teacher.query.filter(Teacher.user_id == user.id).first()
        if user.system_name != "turon":

            groups = db.session.query(Group).join(Group.teacher).options(contains_eager(Group.teacher)).filter(
                Teacher.id == teacher.id).all()
            subject_list = []
            for gr in groups:
                if gr.subject_id not in subject_list:
                    subject_list.append(gr.subject_id)
            subjects = Subject.query.filter(Subject.id.in_(sub for sub in subject_list)).order_by(Subject.id).all()
        else:
            subjects = Subject.query.filter(Subject.id.in_(sub.id for sub in teacher.subjects)).order_by(
                Subject.id).all()

    return jsonify({
        "subjects": iterate_models(subjects),
    })



@subject_bp.route('/crud/', defaults={'subject_id': None}, methods=['POST'])
@subject_bp.route('/crud/<subject_id>', methods=['POST'])
@swag_from({
    'tags': ['Subject'],
    "methods": ["POST"],
})
def create_subject(subject_id):
    info = request.form.get("info")
    json_file = json.loads(info)
    name = json_file['title']
    photo = request.files.get('file')
    desc = json_file['desc']
    get_img = None
    if photo and check_file(photo.filename):
        get_img = add_file(photo, "img", File)
    if not subject_id:
        add = Subject(name=name, desc=desc, file_id=get_img)
        add.add_commit()
    else:
        get_subject = Subject.query.filter(Subject.id == subject_id).first()
        if photo and check_file(photo.filename):
            check_img_remove(get_subject.file_id, File)
            get_img = add_file(photo, "img", File)
            Subject.query.filter(Subject.id == subject_id).update({
                "name": name,
                "desc": desc,
                "file_id": get_img
            })
        else:
            Subject.query.filter(Subject.id == subject_id).update({
                "name": name,
                "desc": desc
            })
        db.session.commit()
    subjects = Subject.query.filter(or_(Subject.disabled == False, Subject.disabled == None)).order_by(
        Subject.id).all()
    return create_msg(f"{name}", status=True, data=iterate_models(subjects))


@subject_bp.route(f'/profile/<int:subject_id>')
@jwt_required()
@swag_from({
    'tags': ['Subject'],
    "methods": ["GET"],
})
def subject(subject_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()

    if user.student:
        subject_view = StudentSubject.query.filter(StudentSubject.subject_id == subject_id,
                                                   StudentSubject.student_id == user.student.id).first()
    else:
        subject_view = Subject.query.filter(Subject.id == subject_id).first()
    return jsonify({
        "data": subject_view.convert_json(),
        "status": True
    })


@subject_bp.route(f'/delete/<int:subject_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Subject'],
    "methods": ["DELETE"],
})
def del_subject(subject_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    sub_name = Subject.query.filter(Subject.id == subject_id).first()
    name = sub_name.name
    sub_name.disabled = True
    db.session.commit()
    if sub_name.file_id:
        check_img_remove(sub_name.file_id, File)
    subjects_server = Subject.query.order_by(Subject.id).all()
    send_subject_server("subject", gennis_server_url, subjects_server)
    return del_msg(item=name, status=True)


@subject_bp.route(f'{api}/classroom_subjects')
@swag_from({
    'tags': ['Subject'],
    "methods": ["GET"],
})
def classroom_subjects():
    subjects = Subject.query.order_by(Subject.id).all()
    return jsonify({
        "subjects": iterate_models(subjects)
    })
