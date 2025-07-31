import pprint

from flasgger import swag_from
from flask import Blueprint
from flask_jwt_extended import jwt_required

from app import jsonify, request

from backend.models.basic_model import Exercise, SubjectLevel, StudentExercise, StudentLesson, \
    ExerciseBlock, Group, Student, Chapter, Lesson, StudentChapter, ExerciseAnswers, StudentExerciseBlock, \
    StudentLessonArchive
from backend.models.settings import iterate_models
from sqlalchemy.orm import aliased, contains_eager
from sqlalchemy import func, and_, or_, join
from app import db

lesson_degree = Blueprint('lesson_degree', __name__)


# Optimized version of the group_degree route
@lesson_degree.route('/group_degree/', methods=['POST'])
@swag_from({"tags": ["Lesson_degree"]}, methods=['POST'])
@jwt_required()
def group_degree():
    data = request.get_json()
    group_id = data.get('group_id')
    level_id = data.get('level_id')
    chapter_id = data.get('chapter_id')
    lesson_id = data.get('lesson_id')

    level = SubjectLevel.query.get(level_id)
    students = Student.query.join(Student.groups).filter(Group.id == group_id).all()

    if not students:
        return jsonify({"data": {"error": "no students"}})

    student_ids = [s.id for s in students]
    chapters_list = []

    def get_exercise_blocks(level_id, exercise_ids):
        return ExerciseBlock.query.join(ExerciseBlock.exercise).options(
            contains_eager(ExerciseBlock.exercise)
        ).filter(
            Exercise.level_id == level_id,
            ExerciseBlock.exercise_answers.any(),  # Ensure answers exist
            Exercise.lesson.any(),  # ✅ Fix: safely check for related lesson
            Exercise.id.in_(exercise_ids)
        ).all()

    if not chapter_id and not lesson_id:

        chapters = Chapter.query.filter_by(level_id=level.id).order_by(Chapter.order).all()

        for chapter in chapters:
            info = {"id": chapter.id, "name": chapter.name, "students": []}
            all_lessons = Lesson.query.filter_by(chapter_id=chapter.id).count()

            # Exercises done by all students in this chapter
            student_exercises = StudentExercise.query.filter(
                StudentExercise.chapter_id == chapter.id,
                StudentExercise.student_id.in_(student_ids)
            ).all()

            exercise_ids = list({e.exercise.id for e in student_exercises if e.exercise})
            exercise_blocks = get_exercise_blocks(level_id, exercise_ids)
            exercise_block_ids = [b.id for b in exercise_blocks]

            students_chapters = StudentChapter.query.filter(
                StudentChapter.student_id.in_(student_ids),
                StudentChapter.chapter_id == chapter.id
            ).all()

            chapter_total_finished = 0
            chapter_total_exercise = 0

            for student_chapter in students_chapters:
                student_id = student_chapter.student_id
                student_lessons = StudentLesson.query.filter(
                    StudentLesson.student_id == student_id,
                    StudentLesson.chapter_id == chapter.id
                ).all()
                lesson_ids = list(
                    {lesson.lesson_id for lesson in student_lessons if lesson.lesson_id})  # ✅ Unique lesson IDs

                subquery = (
                    db.session.query(
                        StudentLessonArchive.lesson_id,
                        func.min(StudentLessonArchive.reset_date).label("earliest_reset")
                    )
                    .filter(
                        StudentLessonArchive.student_id == student_id,
                        StudentLessonArchive.lesson_id.in_(lesson_ids),
                        StudentLessonArchive.status == True,
                        StudentLessonArchive.reset_date.isnot(None)
                    )
                    .group_by(StudentLessonArchive.lesson_id)
                    .subquery()
                )

                archive_alias = aliased(StudentLessonArchive)

                student_archive_lesson = (
                    db.session.query(archive_alias)
                    .join(
                        subquery,
                        (archive_alias.lesson_id == subquery.c.lesson_id) &
                        (archive_alias.reset_date == subquery.c.earliest_reset)
                    )
                    .all()
                )

                # Count correct answers
                true_exercises = StudentExercise.query.filter_by(
                    student_id=student_id,
                    chapter_id=chapter.id,
                    boolean=True
                ).filter(
                    StudentExercise.block_id.in_(exercise_block_ids),
                    StudentExercise.student_lesson_archive_id.in_([lesson.id for lesson in student_archive_lesson])
                ).count()

                # Lessons finished
                student_lessons_true = StudentLesson.query.filter_by(
                    student_id=student_id,
                    chapter_id=chapter.id,
                    finished=True
                ).count()

                # Total answers expected for this student
                total_exercise_answers = ExerciseAnswers.query.filter(
                    ExerciseAnswers.block_id.in_(exercise_block_ids),

                ).count()

                # Percent calculations
                finished_percent = round((student_lessons_true / all_lessons) * 100) if all_lessons else 0
                exercise_percent_value = round(
                    (true_exercises / total_exercise_answers) * 100) if total_exercise_answers else 0

                chapter_total_finished += finished_percent
                chapter_total_exercise += exercise_percent_value

                info['students'].append({
                    "id": chapter.id,
                    "student_chapter": student_chapter.id,
                    "percentage": student_chapter.percentage,
                    "student_name": student_chapter.student.user.name,
                    "student_surname": student_chapter.student.user.surname,
                    "student_id": student_id,
                    "exercises": f"{exercise_percent_value}%",
                    "finished": f"{finished_percent}%"
                })

            student_count = len(students_chapters)
            info['finished'] = f"{round(chapter_total_finished / student_count)}%" if student_count else "0%"
            info['exercises'] = f"{round(chapter_total_exercise / student_count)}%" if student_count else "0%"

            chapters_list.append(info)

        return jsonify({"data": {"all_chapters": len(chapters), "chapters_list": chapters_list}})

    elif chapter_id and not lesson_id:

        chapter = Chapter.query.get(chapter_id)
        all_lessons = Lesson.query.filter_by(chapter_id=chapter.id).order_by(Lesson.order).all()

        for lesson in all_lessons:
            info = {"id": lesson.id, "name": lesson.name, "students": []}
            student_exercises = StudentExercise.query.filter(
                StudentExercise.lesson_id == lesson.id,
                StudentExercise.student_id.in_(student_ids)
            ).all()
            exercise_ids = list({e.exercise.id for e in student_exercises if e.exercise})
            exercise_blocks = get_exercise_blocks(level_id, exercise_ids)
            exercise_block_ids = [b.id for b in exercise_blocks]

            true_exercises = StudentExercise.query.filter(
                StudentExercise.student_id.in_(student_ids),
                StudentExercise.chapter_id == chapter.id,
                StudentExercise.block_id.in_(exercise_block_ids),
                StudentExercise.boolean == True
            ).count()

            students_lessons = StudentLesson.query.filter(
                StudentLesson.lesson_id == lesson.id,
                StudentLesson.student_id.in_(student_ids)
            ).order_by(StudentLesson.order).all()

            finished_count = 0
            exercise_percent = 0

            for student_lesson in students_lessons:
                if student_lesson.finished:
                    finished_count += 1
                exercise_percent += student_lesson.percentage

                info['students'].append({
                    "student_name": student_lesson.student.user.name,
                    "student_surname": student_lesson.student.user.surname,
                    "student_id": student_lesson.student_id,
                    "exercises": f"{round(student_lesson.percentage)}%",
                    "finished": "100%" if student_lesson.finished else "0%"
                })

            info['finished'] = f"{round(finished_count / len(students) * 100)}%"
            info['exercises'] = f"{round(exercise_percent / len(students))}%"
            chapters_list.append(info)

        return jsonify({"data": {"lesson_list": chapters_list}})

    else:

        student_lessons = StudentLesson.query.filter(
            StudentLesson.lesson_id == lesson_id,
            StudentLesson.student_id.in_(student_ids)
        ).order_by(StudentLesson.order).all()

        for les in student_lessons:
            chapters_list.append({
                "percentage": les.percentage,
                "student_name": les.student.user.name,
                "student_surname": les.student.user.surname,
                "student_id": les.student_id,
                "exercises": f"{round(les.percentage)}%",
                "finished": les.finished,
                "status": les.finished is True
            })

        return jsonify({"data": {"lesson_list": chapters_list}})


@lesson_degree.route('/student_exercise_block/<lesson_id>/<student_id>', methods=['POST', 'GET'])
@swag_from({"tags": ["Lesson_degree"]}, methods=['POST'])
def student_exercise_block(lesson_id, student_id):
    lesson = Lesson.query.get(lesson_id)
    student_lesson = StudentLesson.query.filter_by(lesson_id=lesson_id, student_id=student_id).first()
    student_exercises = StudentExercise.query.filter(StudentExercise.lesson_id == lesson_id,
                                                     StudentExercise.student_id == student_id).all()
    exercise_block = Exercise.query.filter(Exercise.id.in_(
        [e.exercise_id for e in student_exercises])).order_by(
        Exercise.id).all()

    return jsonify({
        "data": {
            "lesson": {
                "id": lesson.id,
                "name": lesson.name,
                "order": lesson.order
            },
            "exercises": [b.convert_json(student_id, lesson_id) for b in exercise_block],
            "student_lesson": student_lesson.convert_json(lesson_id)

        }
    })
