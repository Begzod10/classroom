from backend.models.basic_model import Lesson, StudentChapter, Chapter, StudentLesson, User, Student
from app import request, db, jsonify
from sqlalchemy import desc
from pprint import pprint
from backend.models.settings import iterate_models
from flask_jwt_extended import jwt_required, get_jwt_identity

from flask import Blueprint
from flasgger import swag_from

chapter_bp = Blueprint('chapter_folder', __name__)


@chapter_bp.route(f'/info/<level_id>', methods=['POST', "GET"])
@jwt_required()
@swag_from({
    'tags': ['Chapter'],
    'methods': ['POST', 'GET']
})
def chapters_info(level_id):
    identity = get_jwt_identity()

    user = User.query.filter(User.classroom_user_id == identity).first()
    if request.method == "POST":
        name = request.get_json()['name']
        exist_chapter = Chapter.query.filter(Chapter.level_id == level_id).order_by(desc(Chapter.id)).first()
        order = 0
        if exist_chapter:
            order = order + 1
        chapter = Chapter(name=name, level_id=level_id, order=order)
        chapter.add()

        return jsonify({
            "msg": "Chapter yaratildi",
            "chapter": chapter.convert_json(),
            "status": True
        })
    else:
        chapters = Chapter.query.filter(Chapter.level_id == level_id).order_by(
            Chapter.order).all()
        if user.student:
            chapters = Chapter.query.filter(Chapter.level_id == level_id, Chapter.status == True).order_by(
                Chapter.order).all()
            student = Student.query.filter(Student.user_id == user.id).first()
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
                                                                    StudentLesson.level_id == level_id,
                                                                    StudentLesson.self_chapter_id == exist_chapter.id,
                                                                    StudentLesson.chapter_id == chapter.id).first()
                        if not student_lesson:
                            student_lesson = StudentLesson(lesson_id=lesson.id, student_id=student.id,
                                                           level_id=level_id, self_chapter_id=exist_chapter.id,
                                                           order=lesson.order, chapter_id=chapter.id)
                            student_lesson.add_commit()
                        else:
                            student_lesson.order = lesson.order
            chapters = StudentChapter.query.filter(
                StudentChapter.student_id == student.id,
                StudentChapter.level_id == level_id).order_by(
                StudentChapter.order).all()
        return jsonify({
            "chapters": iterate_models(chapters, entire=True)
        })


@chapter_bp.route('/chapters/<level_id>', methods=['GET'])
@swag_from({
    'tags': ['Chapter'],
    'methods': ['GET']
})
def chapters_only(level_id):
    chapters = Chapter.query.filter(Chapter.level_id == level_id).order_by(Chapter.order).all()
    return jsonify({
        "chapters": iterate_models(chapters)
    })


@chapter_bp.route('/crud/<chapter_id>', methods=['POST', 'DELETE'])
@swag_from({
    'tags': ['Chapter'],
    'methods': ['POST', 'DELETE']
})
def crud(chapter_id):
    chapter = Chapter.query.filter(Chapter.id == chapter_id).first()
    chapter_name = chapter.name
    if request.method == "POST":
        name = request.get_json()['name']

        status = request.get_json()['status']
        status = bool(status)
        chapter.name = name
        chapter.status = status
        db.session.commit()
        return jsonify({
            "msg": "Chapter o'zgartirildi",
            "chapter": chapter.convert_json(),
            "status": True
        })
    else:
        if not chapter.lesson:
            db.session.delete(chapter)
            db.session.commit()
            return jsonify({
                "msg": f"{chapter_name} o'chirildi",
                "status": True
            })
        else:
            return jsonify({
                "msg": f"{chapter_name} ga darsliklar kirtilgan",
                "status": False
            })


@chapter_bp.route('/change/order', methods=['POST'])
@swag_from({
    'tags': ['Chapter'],
    "methods": ["POST"],

})
def change_order():
    type_info = request.get_json()['type']
    chapter = request.get_json()['container']
    index = request.get_json()['newIndex']
    old_index = request.get_json()['oldIndex']
    if type_info == "lesson":
        lesson = request.get_json()['lesson']
        lesson = Lesson.query.filter(Lesson.id == lesson).first()
        if chapter != lesson.chapter_id:
            old_chapter_lessons = Lesson.query.filter(Lesson.id != lesson.id,
                                                      Lesson.chapter_id == lesson.chapter_id,
                                                      Lesson.order > lesson.order, Lesson.disabled == False).order_by(
                Lesson.order).all()
            for less in old_chapter_lessons:
                less.order = less.order - 1
                db.session.commit()
                if less.order < 0:
                    less.order = 0
                db.session.commit()
            new_chapters_lessons = Lesson.query.filter(Lesson.chapter_id == chapter, Lesson.order >= index,
                                                       Lesson.disabled == False).order_by(
                Lesson.order).all()
            for less in new_chapters_lessons:
                less.order = less.order + 1
                db.session.commit()
            lesson.chapter_id = chapter
            lesson.order = index
            db.session.commit()
        else:
            lesson.chapter_id = chapter
            lesson.order = index
            db.session.commit()
            if index < old_index:
                lesson_list = Lesson.query.filter(Lesson.order >= index, Lesson.order <= old_index,
                                                  Lesson.chapter_id == chapter, Lesson.id != lesson.id,
                                                  Lesson.disabled == False).order_by(
                    Lesson.order).all()
                for less in lesson_list:
                    less.order = less.order + 1

                    db.session.commit()
            else:
                lesson_list = Lesson.query.filter(Lesson.order <= index, Lesson.order >= old_index,
                                                  Lesson.chapter_id == chapter, Lesson.id != lesson.id,
                                                  Lesson.disabled == False).order_by(
                    Lesson.order).all()

                for less in lesson_list:

                    less.order = less.order - 1
                    db.session.commit()
                    if less.order < 0:
                        less.order = 0
                    db.session.commit()
    else:

        get_chapter = Chapter.query.filter(Chapter.id == chapter).first()
        get_chapter.order = index
        db.session.commit()
        if index < old_index:
            chapter_list = Chapter.query.filter(Chapter.order >= index, Chapter.order <= old_index,
                                                Chapter.id != get_chapter.id, Chapter.disabled == False).order_by(
                Chapter.order).all()

            for less in chapter_list:
                less.order = less.order + 1
                db.session.commit()

        else:
            chapter_list = Chapter.query.filter(Chapter.order <= index, Chapter.order >= old_index,
                                                Chapter.id != get_chapter.id, Chapter.disabled == False).order_by(
                Chapter.order).all()

            for less in chapter_list:
                less.order = less.order - 1
                db.session.commit()
    return jsonify({
        "msg": "Tartib soni o'zgardi",
        "status": True
    })
