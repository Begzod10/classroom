import datetime

from backend.models.basic_model import Student, StudentLesson, ExerciseAnswers, StudentExercise, StudentExerciseBlock, \
    User, StudentLevel, Exercise, ExerciseBlock, StudentChapter, StudentSubject, Lesson, StudentLessonArchive, Group, \
    StudentCommentForLesson
from app import api, app, db, request, jsonify, contains_eager
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.settings import iterate_models
from pprint import pprint
from .utils import update_student_datas, update_ratings
from sqlalchemy import or_
from flask import Blueprint
from flasgger import swag_from

student_lesson_bp = Blueprint('student_lesson', __name__)


@student_lesson_bp.route(f'/lesson/<int:lesson_id>/')
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


@student_lesson_bp.route(f'/complete/', methods=['POST'])
@jwt_required()
def complete_exercise():
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    answers = request.get_json()['block']
    lesson_id = request.get_json()['lessonId']
    exercise_id = request.get_json()['excId']
    student = Student.query.filter(Student.user_id == user.id).first()
    student_lesson = StudentLesson.query.filter(StudentLesson.lesson_id == lesson_id,
                                                StudentLesson.student_id == student.id).first()
    lesson = Lesson.query.filter(Lesson.id == lesson_id).first()
    student_lesson_archive = StudentLessonArchive.query.filter(StudentLessonArchive.student_id == student.id,
                                                               StudentLessonArchive.lesson_id == lesson.id,
                                                               StudentLessonArchive.student_lesson == student_lesson.id,
                                                               StudentLessonArchive.status == False).first()
    if not student_lesson_archive:
        student_lesson_archive = StudentLessonArchive(student_id=student.id, student_lesson=student_lesson.id,
                                                      lesson_id=lesson_id)
        student_lesson_archive.add_commit()
    for answer in answers:
        block = ExerciseBlock.query.filter(ExerciseBlock.id == answer['block_id']).first()
        exercise = Exercise.query.filter(Exercise.id == block.exercise_id).first()
        exist_block = StudentExerciseBlock.query.filter(StudentExerciseBlock.lesson_id == lesson_id,
                                                        StudentExerciseBlock.student_id == student.id,
                                                        StudentExerciseBlock.block_id == block.id,
                                                        StudentExerciseBlock.exercise_id == exercise.id,
                                                        StudentExerciseBlock.student_lesson_archive_id == student_lesson_archive.id,
                                                        StudentExerciseBlock.chapter_id == lesson.chapter_id).first()
        if not exist_block:
            student_exe_block = StudentExerciseBlock(student_id=student.id, block_id=block.id, exercise_id=exercise.id,
                                                     clone=answer['answers'], lesson_id=lesson_id,
                                                     student_lesson_archive_id=student_lesson_archive.id,
                                                     chapter_id=lesson.chapter_id)
            student_exe_block.add_commit()

        if answer['innerType'] == "text" and answer['type'] == "question" or answer['innerType'] == "image" and answer[
            'type'] == "question" or answer['innerType'] == "imageInText" and answer['type'] == "question":
            exercise_answer = ExerciseAnswers.query.filter(ExerciseAnswers.block_id == answer['block_id'],
                                                           ExerciseAnswers.status == True).first()
            if answer['variants']['type'] == "input":
                status = False
                if exercise_answer.desc == answer['answers']:
                    status = True
                exist_exercise = StudentExercise.query.filter(StudentExercise.student_id == student.id,
                                                              StudentExercise.lesson_id == lesson_id,
                                                              StudentExercise.exercise_id == exercise.id,
                                                              StudentExercise.answer_id == exercise_answer.id,
                                                              StudentExercise.student_chapter_id == student_lesson.self_chapter_id,
                                                              StudentExercise.chapter_id == lesson.chapter_id,
                                                              StudentExercise.student_lesson_archive_id == student_lesson_archive.id).first()
                if not exist_exercise:
                    student_exercise = StudentExercise(student_id=student.id, lesson_id=lesson_id,
                                                       exercise_id=exercise.id, subject_id=exercise.subject_id,
                                                       type_id=exercise.type_id, level_id=exercise.level_id,
                                                       boolean=status, block_id=block.id,
                                                       answer_id=exercise_answer.id, value=answer['answers'],
                                                       student_chapter_id=student_lesson.self_chapter_id,
                                                       student_lesson_archive_id=student_lesson_archive.id,
                                                       chapter_id=lesson.chapter_id)
                    student_exercise.add_commit()
            else:
                for ans in answer['answers']:
                    if ans['checked'] == True:
                        status = False
                        if exercise_answer.order == ans['index']:
                            status = True
                        else:
                            exercise_answer = ExerciseAnswers.query.filter(
                                ExerciseAnswers.block_id == answer['block_id'],
                                ExerciseAnswers.order == ans['index']).first()
                        exist_exercise = StudentExercise.query.filter(StudentExercise.student_id == student.id,
                                                                      StudentExercise.lesson_id == lesson_id,
                                                                      StudentExercise.exercise_id == exercise.id,
                                                                      StudentExercise.answer_id == exercise_answer.id,
                                                                      StudentExercise.student_chapter_id == student_lesson.self_chapter_id,
                                                                      StudentExercise.chapter_id == lesson.chapter_id,
                                                                      StudentExercise.student_lesson_archive_id == student_lesson_archive.id).first()
                        if not exist_exercise:
                            student_exercise = StudentExercise(student_id=student.id, lesson_id=lesson_id,
                                                               exercise_id=exercise.id, subject_id=exercise.subject_id,
                                                               type_id=exercise.type_id, level_id=exercise.level_id,
                                                               boolean=status, block_id=block.id,
                                                               answer_id=exercise_answer.id, value=ans['checked'],
                                                               student_chapter_id=student_lesson.self_chapter_id,
                                                               chapter_id=lesson.chapter_id,
                                                               student_lesson_archive_id=student_lesson_archive.id)
                            student_exercise.add_commit()
                        else:
                            return jsonify({
                                'msg': 'seryoz'
                            })
                update_ratings(student, lesson_id)

        elif answer['type'] == "text":
            for ans in answer['answers']:
                if ans['type'] == "matchWord":
                    exercise_answer = ExerciseAnswers.query.filter(ExerciseAnswers.block_id == answer['block_id'],
                                                                   ExerciseAnswers.order == ans['index']).first()
                    if ans['index'] == ans['item']['index']:
                        exercise_status = True
                    else:
                        exercise_status = False
                    exist_exercise = StudentExercise.query.filter(StudentExercise.student_id == student.id,
                                                                  StudentExercise.lesson_id == lesson_id,
                                                                  StudentExercise.exercise_id == exercise.id,
                                                                  StudentExercise.answer_id == exercise_answer.id,
                                                                  StudentExercise.student_chapter_id == student_lesson.self_chapter_id,
                                                                  StudentExercise.chapter_id == lesson.chapter_id,
                                                                  StudentExercise.student_lesson_archive_id == student_lesson_archive.id
                                                                  ).first()
                    if not exist_exercise:
                        student_exercise = StudentExercise(student_id=student.id, lesson_id=lesson_id,
                                                           exercise_id=exercise.id, subject_id=exercise.subject_id,
                                                           type_id=exercise.type_id, level_id=exercise.level_id,
                                                           boolean=exercise_status, block_id=block.id,
                                                           student_chapter_id=student_lesson.self_chapter_id,
                                                           chapter_id=lesson.chapter_id,
                                                           student_lesson_archive_id=student_lesson_archive.id,
                                                           answer_id=exercise_answer.id, value=ans['item'],
                                                           )
                        student_exercise.add_commit()
                    else:
                        return jsonify({
                            'msg': 'seryoz'
                        })
                else:
                    exercise_answer = ExerciseAnswers.query.filter(ExerciseAnswers.block_id == answer['block_id'],
                                                                   ExerciseAnswers.desc == ans['text']).first()
                    if ans['text'] == ans['value']:
                        exercise_status = True
                    else:
                        exercise_status = False

                    exist_exercise = StudentExercise.query.filter(StudentExercise.student_id == student.id,
                                                                  StudentExercise.lesson_id == lesson_id,
                                                                  StudentExercise.exercise_id == exercise.id,
                                                                  StudentExercise.answer_id == exercise_answer.id,
                                                                  StudentExercise.student_chapter_id == student_lesson.self_chapter_id,
                                                                  StudentExercise.chapter_id == lesson.chapter_id,
                                                                  StudentExercise.student_lesson_archive_id == student_lesson_archive.id
                                                                  ).first()
                    if not exist_exercise:
                        student_exercise = StudentExercise(student_id=student.id, lesson_id=lesson_id,
                                                           exercise_id=exercise.id, subject_id=exercise.subject_id,
                                                           type_id=exercise.type_id, level_id=exercise.level_id,
                                                           boolean=exercise_status, block_id=block.id,
                                                           answer_id=exercise_answer.id, value=ans['value'],
                                                           student_chapter_id=student_lesson.self_chapter_id,
                                                           chapter_id=lesson.chapter_id,
                                                           student_lesson_archive_id=student_lesson_archive.id
                                                           )
                        student_exercise.add_commit()
                    else:
                        return jsonify({
                            'msg': 'seryoz'
                        })
    update_student_datas(student, lesson_id)
    update_ratings(student, lesson_id)
    print(lesson_id)
    student_exercise_block = StudentExerciseBlock.query.filter(StudentExerciseBlock.lesson_id == lesson_id,
                                                               StudentExerciseBlock.student_id == student.id,
                                                               StudentExerciseBlock.exercise_id == exercise_id,
                                                               StudentExerciseBlock.student_lesson_archive_id == student_lesson_archive.id).order_by(
        StudentExerciseBlock.id).all()
    return jsonify({
        "success": True,
        "block": iterate_models(student_exercise_block),
        "archive_id": student_lesson_archive.id if student_lesson_archive else 0
    })


@student_lesson_bp.route(f'/reset/<archive_id>')
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


@student_lesson_bp.route(f'/profile/<chapter_id>/<order>/', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Lesson'],
    "methods": ["GET"],
})
def lesson_profile(chapter_id, order):
    identity = get_jwt_identity()
    user = User.query.filter(User.classroom_user_id == identity).first()
    lesson = Lesson.query.filter(Lesson.chapter_id == chapter_id, Lesson.order == order,
                                 Lesson.disabled != True).first()
    student_lesson = StudentLesson.query.filter(StudentLesson.lesson_id == lesson.id,
                                                StudentLesson.student_id == user.student.id).first()
    student_lesson_archive = StudentLessonArchive.query.filter(StudentLessonArchive.student_lesson == student_lesson.id,
                                                               StudentLessonArchive.student_id == user.student.id,
                                                               StudentLessonArchive.status == False).order_by(
        StudentLessonArchive.id.desc()).first()

    return jsonify(
        {
            "data": {
                "lesson": student_lesson.convert_json(),
                "archive": student_lesson_archive.id if student_lesson_archive else 0

            }
        })
