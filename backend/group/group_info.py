import requests
from flasgger import swag_from
from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import cross_origin, db, request, jsonify
from sqlalchemy import or_
from sqlalchemy.orm import contains_eager
from backend.configs import gennis_server_url
from backend.models.basic_model import Student, StudentLevel, Teacher, Group, SubjectLevel, User, StudentSubject, \
    Chapter, StudentChapter, StudentLesson
from backend.models.settings import iterate_models

group_bps = Blueprint('group_bps', __name__)


# from backend.basics.settings import

@group_bps.route('/get_groups')
@swag_from({'tags': ['Group'], "methods": ["GET"]})
# @app.route(f'{api}/get_groups')
@cross_origin()
@jwt_required()
def get_groups():
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    student = Student.query.filter(Student.user_id == user.id).first()
    teacher = Teacher.query.filter(Teacher.user_id == user.id).first()

    if student:
        groups = db.session.query(Group).join(Group.student).options(contains_eager(Group.student)).filter(
            Student.id == student.id).order_by(Group.platform_id).all()
        for group in groups:
            student_subject = StudentSubject.query.filter(StudentSubject.subject_id == group.subject_id,
                                                          StudentSubject.student_id == student.id).first()
            if not student_subject:
                student_subject = StudentSubject(subject_id=group.subject_id,
                                                 student_id=student.id)
                db.session.add(student_subject)
                db.session.commit()
        groups = db.session.query(Group).join(Group.student).options(contains_eager(Group.student)).filter(
            Student.id == student.id).order_by(Group.platform_id).all()

    else:
        groups = db.session.query(Group).join(Group.teacher).options(contains_eager(Group.teacher)).filter(
            Teacher.id == teacher.id).order_by(Group.id).all()
        for group in groups:
            if group.teacher_id != teacher.id:
                teacher.groups.remove(group)
                db.session.commit()

    return iterate_models(groups)


@group_bps.route('/group_observer/<group_id>')
@swag_from({'tags': ['Group'], "methods": ["GET"]})
# @app.route(f'{api}/group_observer/<group_id>')
@jwt_required()
def group_observer(group_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    if user.system_name == "gennis":
        group = Group.query.filter(Group.platform_id == group_id).first()
    else:
        group = Group.query.filter(Group.turon_id == group_id).first()
    return jsonify({
        "data": group.convert_json() if group else "Group not found",
        "status": True if group else False
    })


@group_bps.route('/group_profile2/<int:group_id>')
@swag_from({'tags': ['Group'], "methods": ["GET"]})
# @app.route(f'{api}/group_profile2/<int:group_id>')
@jwt_required()
def group_profile(group_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    student = Student.query.filter(Student.user_id == user.id).first()
    group = Group.query.filter(Group.id == group_id).first()
    errors = []
    if user.system_name == "gennis":
        response = requests.get(
            f"{gennis_server_url}/api/group_classroom_profile/group_profile_classroom/{group.platform_id}", headers={
                'Content-Type': 'application/json'
            })
        user_id_list = response.json()['user_id_list']
        errors = response.json()['errors']
        users = User.query.filter(User.platform_id.in_(user_id_list)).all()
        exist_students = Student.query.filter(Student.user_id.in_([user.id for user in users])).all()
        group_students = Student.query.join(Student.groups).filter(Group.id == group_id, Student.id.notin_(
            [student.id for student in exist_students])).all()
        for st in group_students:
            st.groups.remove(group)
            db.session.commit()
    student_level = StudentLevel.query.filter(StudentLevel.group_id == group_id).all()
    levels = SubjectLevel.query.filter(SubjectLevel.id.in_([level.level_id for level in student_level])).all()
    students = Student.query.join(Student.groups).filter(Group.id == group_id).all()
    if len(students) > len(student_level):
        for level in levels:

            for student in students:
                exist_chapter = StudentLevel.query.filter(StudentLevel.group_id == group_id,
                                                          StudentLevel.student_id == student.id,
                                                          StudentLevel.level_id == level.id,
                                                          StudentLevel.subject_id == level.subject_id,
                                                          ).first()
                if not exist_chapter:
                    exist = StudentLevel(student_id=student.id, level_id=level.id, group_id=group_id,
                                         subject_id=level.subject_id, disabled=True)
                    exist.add_commit()
            chapters = Chapter.query.filter(Chapter.level_id == level.id).order_by(Chapter.order).all()
            for chapter in chapters:
                exist_chapter = StudentChapter.query.filter(StudentChapter.chapter_id == chapter.id,
                                                            StudentChapter.student_id == student.id,
                                                            StudentChapter.level_id == chapter.level_id).first()
                if not exist_chapter:
                    exist_chapter = StudentChapter(level_id=chapter.level_id, chapter_id=chapter.id,
                                                   student_id=student.id, order=chapter.order)
                    exist_chapter.add()
                else:
                    exist_chapter.order = chapter.order
                    db.session.commit()
                for lesson in chapter.lesson:
                    if not lesson.disabled:
                        student_lesson = StudentLesson.query.filter(StudentLesson.lesson_id == lesson.id,
                                                                    StudentLesson.student_id == student.id,
                                                                    StudentLesson.level_id == level.id,
                                                                    StudentLesson.self_chapter_id == exist_chapter.id,
                                                                    StudentLesson.chapter_id == chapter.id).first()
                        if not student_lesson:
                            student_lesson = StudentLesson(lesson_id=lesson.id, student_id=student.id,
                                                           level_id=level.id, self_chapter_id=exist_chapter.id,
                                                           order=lesson.order, chapter_id=chapter.id)
                            student_lesson.add_commit()
    levels = SubjectLevel.query.filter(SubjectLevel.subject_id == group.subject_id).filter(
        or_(SubjectLevel.disabled == False, SubjectLevel.disabled == None)).order_by(SubjectLevel.id).all()

    group = Group.query.filter(Group.id == group_id).first()
    if student:
        subject_level = db.session.query(StudentLevel).join(StudentLevel.subject_level).options(
            contains_eager(StudentLevel.subject_level)).filter(StudentLevel.student_id == student.id,
                                                               StudentLevel.group_id == group_id).order_by(
            SubjectLevel.id).all()
    else:
        subject_level = SubjectLevel.query.filter(SubjectLevel.subject_id == group.subject_id,
                                                  SubjectLevel.system_name == user.system_name).order_by(
            SubjectLevel.id).all()
    user = User.query.filter_by(user_id=identity).first()

    return jsonify({
        "data": group.convert_json(user=user),
        "subject_levels": iterate_models(levels),
        "curriculum": iterate_models(subject_level),
        "errors": errors
    })


@group_bps.route('/set_observer/<int:user_id>/<system_name>')
@swag_from({'tags': ['Group'], "methods": ["GET"]})
# @app.route(f'{api}/set_observer/<int:user_id>/<system_name>')
def set_observer(user_id, system_name):
    if system_name == "gennis":
        user = User.query.filter(User.platform_id == user_id).first()
    else:
        user = User.query.filter(User.turon_id == user_id).first()

    user.observer = not user.observer
    db.session.commit()

    action = "given" if user.observer else "taken"
    response_message = f"Permission was {action}"
    return jsonify({
        "msg": response_message,
        "success": True
    })


@group_bps.route('/check_level/<group_id>/<level_id>', methods=['POST', 'GET'])
@swag_from({'tags': ['Group'], "methods": ["GET", "POST"]})
@jwt_required()
def check_level(group_id, level_id):
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    subject_level = SubjectLevel.query.filter(SubjectLevel.id == level_id).first()
    if request.method == "POST":
        student_list = request.get_json()['users']
        for st in student_list:
            student = Student.query.filter(Student.user_id == st['id']).first()
            exist = StudentLevel.query.filter(StudentLevel.level_id == subject_level.id,
                                              StudentLevel.student_id == student.id,
                                              StudentLevel.group_id == group_id,
                                              StudentLevel.subject_id == subject_level.subject_id).first()
            disabled = False if st['level'] else True
            if not exist:
                exist = StudentLevel(student_id=student.id, level_id=subject_level.id, group_id=group_id,
                                     subject_id=subject_level.subject_id, disabled=disabled)
                exist.add_commit()
            else:
                exist.disabled = False if st['level'] else True
                db.session.commit()
            # chapters = Chapter.query.filter(Chapter.level_id == level_id, Chapter.status == True).order_by(
            #     Chapter.order).all()
            # for chapter in chapters:
            #     exist_chapter = StudentChapter.query.filter(StudentChapter.chapter_id == chapter.id,
            #                                                 StudentChapter.student_id == student.id,
            #                                                 StudentChapter.level_id == chapter.level_id).first()
            #     if not exist_chapter:
            #         exist_chapter = StudentChapter(level_id=chapter.level_id, chapter_id=chapter.id,
            #                                        student_id=student.id, order=chapter.order)
            #         exist_chapter.add()
            #     else:
            #         exist_chapter.order = chapter.order
            #         db.session.commit()

        return jsonify({
            "msg": f"O'zgartirildi",
            "status": 'success'
        })
    students = (
        db.session.query(Student)
        .join(Student.groups)  # student → groups
        .join(Student.user)  # student → user
        .options(contains_eager(Student.groups))
        .filter(Group.id == group_id)  # kerakli group
        .filter(User.id.isnot(None))  # user mavjud bo‘lsin
        .order_by(Student.id)
        .all()
    )

    student_list = []
    for student in students:
        exist_level = False
        exist = StudentLevel.query.filter(StudentLevel.level_id == subject_level.id,
                                          StudentLevel.student_id == student.id,
                                          StudentLevel.group_id == group_id,
                                          StudentLevel.disabled != True).first()
        if exist:
            exist_level = True
        info = student.convert_json()
        info['level'] = exist_level
        student_list.append(info)
    return jsonify({
        "students": student_list
    })
