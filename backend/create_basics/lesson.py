from backend.models.basic_model import Exercise, Lesson, LessonBlock, StudentLesson, Student, File, User, \
    StudentLessonArchive, SubjectLevel, Subject, Chapter, StudentLevel
from app import jsonify, request, db, current_app
from sqlalchemy import or_

from backend.models.settings import iterate_models
from backend.basics.settings import add_file, check_img_remove, edit_msg, create_msg, del_msg
from pprint import pprint
from flask_jwt_extended import get_jwt_identity, jwt_required
import json
from sqlalchemy import desc as teskari
from flask import Blueprint

from flasgger import swag_from

lesson_bp = Blueprint('lesson_folder', __name__)


@lesson_bp.route(f'/filter/exercise/<subject_id>/<level_id>')
@jwt_required()
@swag_from({
    'tags': ['Lesson'],
    "methods": ["GET"],
})
def filter_exercise(subject_id, level_id):
    exercises = Exercise.query.filter(Exercise.subject_id == subject_id, Exercise.level_id == level_id).order_by(
        Exercise.id).all()

    return jsonify({
        "data": [exercise.convert_json() for exercise in exercises]
    })


@lesson_bp.route(f'/info/', defaults={"pk": None}, methods=["GET", 'POST', 'DELETE', 'PUT'])
@lesson_bp.route(f'/info/<pk>/', methods=["GET", 'POST', 'DELETE', 'PUT'])
@jwt_required()
@swag_from({
    'tags': ['Lesson'],
    "methods": ["GET", "POST", "PUT", "DELETE"],
})
def info(pk):
    identity = get_jwt_identity()
    user = User.query.filter_by(user_id=identity).first()

    if request.method == "POST" or request.method == "PUT":
        get_json = request.get_json()
        if request.method == "POST":
            level_id = get_json['level_id']
            get_level = SubjectLevel.query.filter(SubjectLevel.id == level_id).first()
            get_subject = Subject.query.filter(Subject.id == get_level.subject_id).first()
            last_chapter = Chapter.query.filter(Chapter.level_id == get_level.id).order_by(Chapter.order).first()
            lesson_add = Lesson(name="undefined", level_id=level_id, subject_id=get_subject.id,
                                chapter_id=last_chapter.id, order=0, test_status=False, test_numbers=0)
            lesson_add.add_commit()
            return create_msg("Lesson", status=True, data=lesson_add.convert_json())
        else:
            name = get_json['name']
            number_test = get_json['number_test']
            test_status = True if number_test else False
            chapter = get_json['chapter']
            order = 0
            lesson_add = Lesson.query.filter(Lesson.id == pk).first()
            lesson_get = Lesson.query.filter(Lesson.level_id == lesson_add.level_id,
                                             Lesson.subject_id == lesson_add.subject_id,
                                             Lesson.chapter_id == chapter, Lesson.disabled == False).order_by(
                Lesson.order).all()
            if lesson_get:
                order = len(lesson_get)

            lesson_add.name = name
            lesson_add.chapter_id = chapter
            lesson_add.order = order
            lesson_add.test_status = test_status
            lesson_add.test_numbers = number_test
            db.session.commit()
            return edit_msg(name, True, lesson_add.convert_json())

    elif request.method == "GET":
        lesson = Lesson.query.filter(Lesson.id == pk).first()
        return jsonify({
            "data": lesson.convert_json(entire=True)
        })

    elif request.method == "DELETE":
        lesson = Lesson.query.filter(Lesson.id == pk).first()
        lesson.disabled = True
        db.session.commit()
        return del_msg("Lesson", status=True, data=lesson.convert_json())


@lesson_bp.route(f'/profile/<chapter_id>/<order>/', methods=['POST', 'GET', 'DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Lesson'],
    'methods': ['POST', 'GET', 'DELETE']
})
def profile(chapter_id, order):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()

    lesson = Lesson.query.filter(Lesson.chapter_id == chapter_id, Lesson.order == order,
                                 Lesson.disabled != True).first()

    lesson_id = lesson.id

    if request.method == "GET":
        next = Lesson.query.filter(Lesson.chapter_id == chapter_id, Lesson.order > lesson.order).filter(
            or_(Lesson.disabled == False, Lesson.disabled == None)).order_by(Lesson.order).first()

        prev = Lesson.query.filter(Lesson.chapter_id == chapter_id, Lesson.order < order).filter(
            or_(Lesson.disabled == False, Lesson.disabled == None)).order_by(teskari(Lesson.order)).first()
        next_order = False
        if next and next.order:
            next_order = next.order
        if prev and prev.order:
            prev_order = prev.order
        else:
            prev_order = 0
        lessons = Lesson.query.filter(Lesson.level_id == lesson.level_id, Lesson.disabled != True).order_by(
            Lesson.order).all()
        if user.student:
            student = Student.query.filter(Student.user_id == user.id).first()

            student_lesson = StudentLesson.query.filter(StudentLesson.lesson_id == lesson_id,
                                                        StudentLesson.student_id == student.id).first()
            student_lesson_archive = StudentLessonArchive.query.filter(
                StudentLessonArchive.student_lesson == student_lesson.id, StudentLessonArchive.student_id == student.id,
                StudentLessonArchive.status == False, StudentLessonArchive.lesson_id == lesson_id).first()

            return jsonify({
                "data": student_lesson.convert_json(lesson_id),
                "length": len(lessons),
                'lesson_id': student_lesson.id,
                "next": next_order,
                "prev": prev_order,
                "archive_id": student_lesson_archive.id if student_lesson_archive else None
                # "student_exercises": iterate_models(student_exercises, entire=True)
            })
        return jsonify({
            "data": lesson.convert_json(entire=True),
            "length": len(lessons),
            "next": next_order,
            "prev": prev_order,

        })
    else:
        lesson.disabled = True
        db.session.commit()
        lessons = Lesson.query.filter(Lesson.id != lesson.id, Lesson.chapter_id == lesson.chapter_id,
                                      Lesson.level_id == lesson.level_id,
                                      Lesson.subject_id == lesson.subject_id, Lesson.disabled != True).order_by(
            Lesson.order).all()
        index = 0
        for less in lessons:
            less.order = index
            db.session.commit()
            index += 1
        return del_msg(lesson.name, True)


@lesson_bp.route(f'/block/text/', defaults={"pk": None}, methods=['POST', 'GET', 'DELETE', 'PUT'])
@lesson_bp.route(f'/block/text/<int:pk>/', methods=['POST', 'GET', 'DELETE', 'PUT'])
@jwt_required()
@swag_from({
    'tags': ['Lesson'],
    "methods": ["POST", "GET", "DELETE", "PUT"],
})
def lesson_block_text(pk):
    if request.method == "POST" or request.method == "PUT":
        info = request.get_json()
        clone = info['editorState']
        text = info['text']

        if request.method == "POST":
            order = 0
            if LessonBlock.query.filter(LessonBlock.lesson_id == info['lesson_id']).all():
                order = LessonBlock.query.filter(LessonBlock.lesson_id == info['lesson_id']).count()
            add_block = LessonBlock(desc=text, lesson_id=info['lesson_id'], clone=clone, type_block=info['type'],
                                    order=order)
            add_block.add_commit()
            return jsonify(add_block.convert_json())
        elif request.method == "PUT":
            lesson_block = LessonBlock.query.filter(LessonBlock.id == pk).first()
            lesson_block.desc = text
            lesson_block.clone = clone
            lesson_block.type_block = info['type']
            lesson_block.lesson_id = info['lesson_id']
            db.session.commit()
            return jsonify(lesson_block.convert_json())
    elif request.method == "DELETE":
        lesson_block = LessonBlock.query.filter(LessonBlock.id == pk).first()
        if lesson_block.file_id:
            check_img_remove(lesson_block.file_id, File)
        lesson_block.delete_commit()
        return del_msg(item="block", status=True)


@lesson_bp.route(f'/block/video/', defaults={"pk": None}, methods=['POST', 'GET', 'DELETE', 'PUT'])
@lesson_bp.route(f'/block/video/<int:pk>/', methods=['POST', 'GET', 'DELETE', 'PUT'])
@jwt_required()
@swag_from({
    'tags': ['Lesson'],
    "methods": ["POST", "GET", "DELETE", "PUT"],
})
def lesson_block_video(pk):
    if request.method == "POST" or request.method == "PUT":
        info = request.get_json()
        video_url = info['video_link']
        if request.method == "POST":
            order = 0
            if LessonBlock.query.filter(LessonBlock.lesson_id == info['lesson_id']).all():
                order = LessonBlock.query.filter(LessonBlock.lesson_id == info['lesson_id']).count()
            add_block = LessonBlock(video_url=video_url, lesson_id=info['lesson_id'], type_block=info['type'],
                                    order=order)
            add_block.add_commit()
            return jsonify(add_block.convert_json())
        elif request.method == "PUT":
            lesson_block = LessonBlock.query.filter(LessonBlock.id == pk).first()
            lesson_block.video_url = video_url
            lesson_block.type_block = info['type']
            lesson_block.lesson_id = info['lesson_id']
            db.session.commit()
            return jsonify(lesson_block.convert_json())
    elif request.method == "DELETE":
        lesson_block = LessonBlock.query.filter(LessonBlock.id == pk).first()
        if lesson_block.file_id:
            check_img_remove(lesson_block.file_id, File)
        lesson_block.delete_commit()
        return del_msg(item="block", status=True)


@lesson_bp.route(f'/block/image/', defaults={"pk": None}, methods=['POST', 'GET', 'DELETE', 'PUT'])
@lesson_bp.route(f'/block/image/<int:pk>/', methods=['POST', 'GET', 'DELETE', 'PUT'])
@jwt_required()
@swag_from({
    'tags': ['Lesson'],
    "methods": ["POST", "GET", "DELETE", "PUT"],
})
def lesson_block_image(pk):
    if request.method == "POST" or request.method == "PUT":
        img = request.files['img']
        get_json = request.form.get('info')
        get_json = json.loads(get_json)
        get_img = None
        if 'img' in request.files:
            get_img = add_file(img, "img", File)
        if request.method == "POST":
            order = 0
            if LessonBlock.query.filter(LessonBlock.lesson_id == get_json['lesson_id']).all():
                order = LessonBlock.query.filter(LessonBlock.lesson_id == get_json['lesson_id']).count()
            add_block = LessonBlock(file_id=get_img, lesson_id=get_json['lesson_id'],
                                    type_block=get_json['type'], order=order)
            add_block.add_commit()
            return jsonify(add_block.convert_json())
        elif request.method == "PUT":
            lesson_block = LessonBlock.query.filter(LessonBlock.id == pk).first()

            if get_img:
                if lesson_block.file_id:
                    check_img_remove(lesson_block.file_id, File)
                lesson_block.file_id = get_img
            lesson_block.type_block = get_json['type']
            lesson_block.lesson_id = get_json['lesson_id']
            db.session.commit()
            return jsonify(lesson_block.convert_json())
    elif request.method == "DELETE":
        lesson_block = LessonBlock.query.filter(LessonBlock.id == pk).first()
        if lesson_block.file_id:
            check_img_remove(lesson_block.file_id, File)
        lesson_block.delete_commit()
        return del_msg(item="block", status=True)


@lesson_bp.route(f'/block/file/', defaults={"pk": None}, methods=['POST', 'GET', 'DELETE', 'PUT'])
@lesson_bp.route(f'/block/file/<int:pk>/', methods=['POST', 'GET', 'DELETE', 'PUT'])
@jwt_required()
@swag_from({
    'tags': ['Lesson'],
    "methods": ["POST", "GET", "DELETE", "PUT"],
})
def lesson_block_file(pk):
    if request.method == "POST" or request.method == "PUT":
        file = request.files['file']
        get_json = request.form.get('info')
        get_json = json.loads(get_json)
        get_file = None
        if 'file' in request.files:
            get_file = add_file(file, "file", File)
        if request.method == "POST":
            order = 0
            if LessonBlock.query.filter(LessonBlock.lesson_id == get_json['lesson_id']).all():
                order = LessonBlock.query.filter(LessonBlock.lesson_id == get_json['lesson_id']).count()
            add_block = LessonBlock(file_id=get_file, lesson_id=get_json['lesson_id'],
                                    type_block=get_json['type'], order=order)
            add_block.add_commit()
            return jsonify(add_block.convert_json())
        elif request.method == "PUT":
            lesson_block = LessonBlock.query.filter(LessonBlock.id == pk).first()

            if get_file:
                if lesson_block.file_id:
                    check_img_remove(lesson_block.file_id, File)
                lesson_block.file_id = get_file
            lesson_block.type_block = get_json['type']
            lesson_block.lesson_id = get_json['lesson_id']
            db.session.commit()
            return jsonify(lesson_block.convert_json())
    else:
        lesson_block = LessonBlock.query.filter(LessonBlock.id == pk).first()
        if lesson_block.file_id:
            check_img_remove(lesson_block.file_id, File)
        lesson_block.delete_commit()
        return del_msg(item="block", status=True)


@lesson_bp.route(f'/block/code/', defaults={"pk": None}, methods=['POST', 'GET', 'DELETE', 'PUT'])
@lesson_bp.route(f'/block/code/<int:pk>/', methods=['POST', 'GET', 'DELETE', 'PUT'])
@jwt_required()
@swag_from({
    'tags': ['Lesson'],
    "methods": ["POST", "GET", "DELETE", "PUT"],
})
def lesson_block_code(pk):
    if request.method == "POST" or request.method == "PUT":
        info = request.get_json()
        code = info['text']
        if request.method == "POST":
            order = 0
            if LessonBlock.query.filter(LessonBlock.lesson_id == info['lesson_id']).all():
                order = LessonBlock.query.filter(LessonBlock.lesson_id == info['lesson_id']).count()
            add_block = LessonBlock(desc=code, lesson_id=info['lesson_id'], type_block=info['type'],
                                    order=order, inner_type=info['innerType'])
            add_block.add_commit()
            return jsonify(add_block.convert_json())
        elif request.method == "PUT":
            lesson_block = LessonBlock.query.filter(LessonBlock.id == pk).first()
            lesson_block.desc = code
            lesson_block.type_block = info['type']
            lesson_block.lesson_id = info['lesson_id']
            lesson_block.inner_type = info['innerType']
            db.session.commit()
            return jsonify(lesson_block.convert_json())
    elif request.method == "DELETE":
        lesson_block = LessonBlock.query.filter(LessonBlock.id == pk).first()
        lesson_block.delete_commit()
        return del_msg(item="block", status=True)


@lesson_bp.route(f'/block/exercise/', defaults={"pk": None}, methods=['POST', 'GET', 'DELETE', 'PUT'])
@lesson_bp.route(f'/block/exercise/<int:pk>/', methods=['POST', 'GET', 'DELETE', 'PUT'])
@jwt_required()
@swag_from({
    'tags': ['Lesson'],
    "methods": ["POST", "GET", "DELETE", "PUT"],
})
def lesson_block_exercise(pk):
    if request.method == "POST" or request.method == "PUT":
        info = request.get_json()
        exercise_id = info['exercise_id']
        lesson_id = info['lesson_id']
        lesson = Lesson.query.filter(Lesson.id == lesson_id).first()
        get_exercise = Exercise.query.filter(Exercise.id == exercise_id).first()
        if get_exercise not in lesson.exercises:
            lesson.exercises.append(get_exercise)
        if request.method == "POST":
            order = 0
            if LessonBlock.query.filter(LessonBlock.lesson_id == info['lesson_id']).all():
                order = LessonBlock.query.filter(LessonBlock.lesson_id == info['lesson_id']).count()
            add_block = LessonBlock(exercise_id=exercise_id, lesson_id=info['lesson_id'], type_block=info['type'],
                                    order=order)
            add_block.add_commit()
            return jsonify(add_block.convert_json())
        elif request.method == "PUT":
            lesson_block = LessonBlock.query.filter(LessonBlock.id == pk).first()
            lesson_block.exercise_id = exercise_id
            lesson_block.type_block = info['type']
            lesson_block.lesson_id = info['lesson_id']
            db.session.commit()
            return jsonify(lesson_block.convert_json())

    elif request.method == "DELETE":
        lesson_block = LessonBlock.query.filter(LessonBlock.id == pk).first()
        lesson = Lesson.query.filter(Lesson.id == lesson_block.lesson_id).first()
        get_exercise = Exercise.query.filter(Exercise.id == lesson_block.exercise_id).first()
        if get_exercise in lesson.exercises:
            lesson.exercises.remove(get_exercise)
            db.session.commit()
        lesson_block.delete_commit()
        return del_msg(item="block", status=True)


@lesson_bp.route(f'/block/order/', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Lesson'],
    "methods": ["PUT"],
})
def lesson_block_order():
    active = request.get_json()['active']
    over = request.get_json()['over']
    lesson_block_active = LessonBlock.query.filter(LessonBlock.id == active['id']).first()
    lesson_block_over = LessonBlock.query.filter(LessonBlock.id == over['id']).first()
    lesson_block_active.order, lesson_block_over.order = lesson_block_over.order, lesson_block_active.order
    db.session.commit()
    return jsonify({"success": True})
