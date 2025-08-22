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
        chapters = Chapter.query.filter(
            Chapter.level_id == level_id
        ).order_by(Chapter.order).all()

        # --- FIX: check for duplicates ---
        seen_orders = set()
        duplicates_found = False
        current_order = 0
        for ch in chapters:
            if ch.order in seen_orders:
                ch.order = current_order
                duplicates_found = True
            else:
                if ch.order != current_order:
                    ch.order = current_order
                    duplicates_found = True
            seen_orders.add(ch.order)
            current_order += 1

        if duplicates_found:
            db.session.commit()  # persist the repair
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
            old_order = chapter.order

            # shift orders of all chapters after the deleted one
            chapters_after = Chapter.query.filter(
                Chapter.order > old_order,
                Chapter.level_id == chapter.level_id,
                Chapter.disabled == False
            ).order_by(Chapter.order).all()
            for ch in chapters_after:
                ch.order -= 1
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
    data = request.get_json()
    type_info = data['type']
    chapter_id = data['container']
    new_index = data['newIndex']
    old_index = data['oldIndex']

    if type_info == "lesson":
        lesson_id = data['lesson']
        lesson = Lesson.query.filter_by(id=lesson_id).first()
        print("old chapter", lesson.chapter_id)
        if not lesson:
            return jsonify({"msg": "Lesson not found", "status": False}), 404

        # --- Case 1: Moving to another chapter ---
        if chapter_id != lesson.chapter_id:
            # Shift old chapter lessons back
            old_chapter_lessons = Lesson.query.filter(
                Lesson.id != lesson.id,
                Lesson.chapter_id == lesson.chapter_id,
                Lesson.order > lesson.order,
                Lesson.disabled == False
            ).order_by(Lesson.order).all()

            for less in old_chapter_lessons:
                less.order = max(0, less.order - 1)

            # Shift new chapter lessons forward
            new_chapter_lessons = Lesson.query.filter(
                Lesson.chapter_id == chapter_id,
                Lesson.order >= new_index,
                Lesson.disabled == False
            ).order_by(Lesson.order).all()

            for less in new_chapter_lessons:
                less.order += 1

            # Move lesson
            lesson.chapter_id = chapter_id
            lesson.order = new_index
            db.session.commit()
            print("new chapter", lesson.chapter_id)
        # --- Case 2: Same chapter reorder ---
        else:
            lesson.order = new_index
            if new_index < old_index:
                lesson_list = Lesson.query.filter(
                    Lesson.order >= new_index,
                    Lesson.order <= old_index,
                    Lesson.chapter_id == chapter_id,
                    Lesson.id != lesson.id,
                    Lesson.disabled == False
                ).order_by(Lesson.order).all()

                for less in lesson_list:
                    less.order += 1
            else:
                lesson_list = Lesson.query.filter(
                    Lesson.order <= new_index,
                    Lesson.order >= old_index,
                    Lesson.chapter_id == chapter_id,
                    Lesson.id != lesson.id,
                    Lesson.disabled == False
                ).order_by(Lesson.order).all()

                for less in lesson_list:
                    less.order = max(0, less.order - 1)


    else:  # Reordering chapters

        chapter = Chapter.query.filter_by(id=chapter_id).first()

        if not chapter:
            return jsonify({"msg": "Chapter not found", "status": False}), 404

        print("old order", chapter.order)

        print("move:", old_index, "->", new_index)

        if new_index < old_index:

            print('moving UP (new_index < old_index)')

            # shift down chapters in the target range

            chapter_list = Chapter.query.filter(

                Chapter.order >= new_index,

                Chapter.order < old_index,  # strictly less than old_index

                Chapter.disabled == False

            ).order_by(Chapter.order).all()

            for ch in chapter_list:
                ch.order += 1


        elif new_index > old_index:

            print('moving DOWN (new_index > old_index)')

            # shift up chapters in the target range

            chapter_list = Chapter.query.filter(

                Chapter.order <= new_index,

                Chapter.order > old_index,  # strictly greater than old_index

                Chapter.disabled == False

            ).order_by(Chapter.order).all()

            for ch in chapter_list:
                ch.order -= 1

        # finally, assign new order to the moved chapter

        chapter.order = new_index

        db.session.commit()
        print("new order", chapter.order)

    return jsonify({
        "msg": "Tartib soni o'zgardi",
        "status": True
    })
