import datetime

from backend.models.basic_model import Student, StudentLesson, ExerciseAnswers, StudentExercise, StudentExerciseBlock, \
    User, StudentLevel, Exercise, ExerciseBlock, StudentChapter, StudentSubject, Lesson, StudentLessonArchive, Group, \
    StudentCommentForLesson
from app import db, request, jsonify
from sqlalchemy.orm import contains_eager
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.settings import iterate_models
from pprint import pprint
from .utils import update_student_datas, update_ratings
from sqlalchemy import or_
from flask import Blueprint
from flasgger import swag_from

student_lesson_bp = Blueprint('student_lesson', __name__)


@student_lesson_bp.route(f'/finish/lesson/<int:lesson_id>/')
@jwt_required()
def finish_lesson(lesson_id):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    student = Student.query.filter(Student.user_id == user.id).first()
    student_lesson = StudentLesson.query.filter(StudentLesson.id == lesson_id,
                                                StudentLesson.student_id == student.id).first()
    update_student_datas(student, student_lesson.lesson_id)
    return jsonify({
        "status": 'success'
    })


@student_lesson_bp.route(f'/lesson/complete/', methods=['POST'])
@jwt_required()
def student_lesson_complete():
    from pprint import pprint

    def save_student_exercise(student, lesson, exercise, block, answer_data, answer_model, is_correct, archive_id,
                              value):
        exist = StudentExercise.query.filter_by(
            student_id=student.id,
            lesson_id=lesson.id,
            exercise_id=exercise.id,
            answer_id=answer_model.id,
            student_chapter_id=student_lesson.self_chapter_id,
            chapter_id=lesson.chapter_id,
            student_lesson_archive_id=archive_id
        ).first()
        if exist:
            return False

        student_ex = StudentExercise(
            student_id=student.id,
            lesson_id=lesson.id,
            exercise_id=exercise.id,
            subject_id=exercise.subject_id,
            type_id=exercise.type_id,
            level_id=exercise.level_id,
            boolean=is_correct,
            block_id=block.id,
            answer_id=answer_model.id,
            value=value,
            student_chapter_id=student_lesson.self_chapter_id,
            chapter_id=lesson.chapter_id,
            student_lesson_archive_id=archive_id
        )
        student_ex.add_commit()
        return True

    identity = get_jwt_identity()
    user = User.query.filter_by(classroom_user_id=identity).first()
    data = request.get_json()

    lesson_id = data['lessonId']
    exercise_id = data['excId']
    answers = data['block']

    student = Student.query.filter_by(user_id=user.id).first()
    lesson = Lesson.query.get(lesson_id)
    student_lesson = StudentLesson.query.filter_by(lesson_id=lesson_id, student_id=student.id).first()

    student_lesson_archive = StudentLessonArchive.query.filter_by(
        student_id=student.id,
        lesson_id=lesson.id,
        student_lesson=student_lesson.id,
        status=False
    ).first()

    if not student_lesson_archive:
        student_lesson_archive = StudentLessonArchive(
            student_id=student.id,
            student_lesson=student_lesson.id,
            lesson_id=lesson_id
        )
        student_lesson_archive.add_commit()

    for answer in answers:
        block = ExerciseBlock.query.get(answer['id'])  # or answer['block_id']
        exercise = Exercise.query.get(block.exercise_id)

        exist_block = StudentExerciseBlock.query.filter_by(
            lesson_id=lesson_id,
            student_id=student.id,
            block_id=block.id,
            exercise_id=exercise.id,
            student_lesson_archive_id=student_lesson_archive.id,
            chapter_id=lesson.chapter_id
        ).first()

        if not exist_block:
            StudentExerciseBlock(
                student_id=student.id,
                block_id=block.id,
                exercise_id=exercise.id,
                clone=answer['answers'],
                lesson_id=lesson_id,
                student_lesson_archive_id=student_lesson_archive.id,
                chapter_id=lesson.chapter_id
            ).add_commit()

        # === CASE 1: variant-based question ===
        if answer['type'] == "question" and answer['innerType'] in ["text", "image"]:
            exercise_answer = ExerciseAnswers.query.filter_by(
                block_id=block.id,
                status=True
            ).first()

            if answer['variants']['type'] == "input":
                is_correct = exercise_answer.desc == answer['answers']
                saved = save_student_exercise(
                    student, lesson, exercise, block,
                    answer, exercise_answer, is_correct,
                    student_lesson_archive.id, answer['answers']
                )
                if not saved:
                    return jsonify({'msg': 'seryoz'})
            else:
                for ans in answer['answers']:
                    if ans.get('checked'):
                        exercise_answer = ExerciseAnswers.query.filter_by(
                            block_id=block.id,
                            order=ans['index']
                        ).first()
                        is_correct = exercise_answer and exercise_answer.order == ans['index']
                        saved = save_student_exercise(
                            student, lesson, exercise, block,
                            ans, exercise_answer, is_correct,
                            student_lesson_archive.id, ans['checked']
                        )
                        if not saved:
                            return jsonify({'msg': 'seryoz'})

        # === CASE 2: text block (matchWord or input) ===
        elif answer['type'] == "text":
            for ans in answer['answers']:
                if ans['type'] == "matchWord":
                    exercise_answer = ExerciseAnswers.query.filter_by(
                        block_id=block.id,
                        order=ans['index']
                    ).first()
                    is_correct = ans['index'] == ans['item']['index']
                    saved = save_student_exercise(
                        student, lesson, exercise, block,
                        ans, exercise_answer, is_correct,
                        student_lesson_archive.id, ans['item']
                    )
                    if not saved:
                        return jsonify({'msg': 'seryoz'})
                else:
                    exercise_answer = ExerciseAnswers.query.filter_by(
                        block_id=block.id,
                        desc=ans['text'][0] if type(ans['text']) == list else ans['text']
                    ).first()

                    is_correct = ans['text'][0] == ans['value']
                    saved = save_student_exercise(
                        student, lesson, exercise, block,
                        ans, exercise_answer, is_correct,
                        student_lesson_archive.id, ans['value']
                    )
                    if not saved:
                        return jsonify({'msg': 'seryoz'})

    update_student_datas(student, lesson_id)
    update_ratings(student, lesson_id)
    exercise_blocks = ExerciseBlock.query.filter(ExerciseBlock.id.in_([answer['id'] for answer in answers])).all()
    return jsonify({
        "success": True,
        "blocks": [block.convert_json(student.id, lesson_id) for block in exercise_blocks],
        "archive_id": student_lesson_archive.id
    })


@student_lesson_bp.route(f'/lesson/reset/<archive_id>/')
@jwt_required()
def reset_lesson(archive_id):
    student_lesson_archive = StudentLessonArchive.query.filter(StudentLessonArchive.id == archive_id).first()
    student_lesson_archive.status = True
    student_lesson_archive.reset_date = datetime.datetime.now()
    db.session.commit()

    lesson = Lesson.query.filter(Lesson.id == student_lesson_archive.lesson_id).first()

    return jsonify({
        "success": True,
        "data": lesson.convert_json(entire=True)
    })


@student_lesson_bp.route(f'/add/comment', methods=['POST'])
def add_comment():
    # Parse JSON request data
    data = request.get_json()

    # Validate required fields
    required_fields = ["student_id", "lesson_id", "comment"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Extract data fields
    student_id = data.get("student_id")
    lesson_id = data.get("lesson_id")
    student = Student.query.filter(Student.user_id == student_id).first()
    student_lesson = StudentLesson.query.filter(StudentLesson.student_id == student.id,
                                                StudentLesson.lesson_id == lesson_id).first()
    comment = data.get("comment")
    ball = data.get("ball", 0)  # default to 0 if not provided
    date = data.get("date", datetime.datetime.now())  # default to current datetime if not provided
    lesson = Lesson.query.filter(Lesson.id == lesson_id).first()
    group = db.session.query(Student).join(Student.groups).filter(Student.id == student.id,
                                                                  Group.subject_id == lesson.subject_id).first()
    # Create new comment object
    new_comment = StudentCommentForLesson(
        student_id=student.id,
        lesson_id=lesson_id,
        group_id=group.id,
        student_lesson_id=student_lesson.id,
        comment=comment,
        ball=ball,
        date=date
    )
    try:
        new_comment.add()
        return jsonify({"message": "Comment added successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
