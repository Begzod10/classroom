from backend.models.basic_model import StudentLesson, StudentChapter, db, StudentLevel, StudentSubject, Lesson, \
    StudentExercise, StudentLessonArchive


def update_student_datas(student, lesson_id):
    # Fetch student lesson and related lesson
    student_lesson = StudentLesson.query.filter_by(
        lesson_id=lesson_id,
        student_id=student.id
    ).first()
    if not student_lesson:
        return

    lesson = student_lesson.lesson  # use relationship if defined

    # 1. Mark lesson as finished if it has no exercises
    if not lesson.exercises:
        student_lesson.finished = True
        db.session.commit()

    # 2. Check if all lessons in chapter are finished
    level_id = student_lesson.level_id
    student_lessons_true = StudentLesson.query.filter_by(
        level_id=level_id,
        student_id=student.id,
        finished=True
    ).count()

    student_lessons_total = StudentLesson.query.filter_by(
        level_id=level_id,
        student_id=student.id
    ).count()

    if student_lessons_true == student_lessons_total:
        student_chapter = StudentChapter.query.filter_by(
            student_id=student.id,
            id=student_lesson.self_chapter_id
        ).first()
        if student_chapter:
            student_chapter.finished = True
            db.session.commit()

    # 3. Check if all chapters in level are finished
    chapter_true = StudentChapter.query.filter_by(
        student_id=student.id,
        level_id=level_id,
        finished=True
    ).count()

    chapters_total = StudentChapter.query.filter_by(
        student_id=student.id,
        level_id=level_id
    ).count()

    if chapter_true == chapters_total:
        student_level = StudentLevel.query.filter_by(
            student_id=student.id,
            level_id=level_id
        ).first()
        if student_level:
            student_level.finished = True
            db.session.commit()

    # 4. Check if all levels in subject are finished
    subject_id = lesson.subject_id
    levels_true = StudentLevel.query.filter_by(
        student_id=student.id,
        subject_id=subject_id,
        finished=True
    ).count()

    levels_total = StudentLevel.query.filter_by(
        student_id=student.id,
        subject_id=subject_id
    ).count()

    if levels_true == levels_total:
        student_subject = StudentSubject.query.filter_by(
            student_id=student.id,
            subject_id=subject_id
        ).first()
        if student_subject:
            student_subject.finished = True
            db.session.commit()


def update_ratings(student, lesson_id):
    student_lesson = StudentLesson.query.filter_by(
        lesson_id=lesson_id, student_id=student.id
    ).first()
    if not student_lesson:
        return

    # === 1. Determine archive and count exercises ===
    archive = StudentLessonArchive.query.filter_by(
        student_id=student.id,
        lesson_id=lesson_id,
        status=True
    ).order_by(StudentLessonArchive.id).first()

    filters = {
        "student_id": student.id,
        "lesson_id": lesson_id,
    }

    if archive:
        filters["student_lesson_archive_id"] = archive.id

    student_exercises_true = StudentExercise.query.filter_by(**filters, boolean=True).count()
    student_exercises_total = StudentExercise.query.filter_by(**filters).count()

    # === 2. Mark lesson as finished if all exercises attempted ===
    exercise_ids = {
        ex.exercise_id for ex in StudentExercise.query.filter_by(**filters).all()
    }
    lesson = student_lesson.lesson  # assuming relationship exists

    if len(exercise_ids) == len(lesson.exercises):
        student_lesson.finished = True

    # === 3. Update lesson percentage ===
    student_lesson.percentage = round(
        (student_exercises_true / student_exercises_total) * 100
    ) if student_exercises_total else 0
    db.session.commit()

    # === 4. Update Chapter Percentage ===
    level_id = student_lesson.level_id
    chapter_id = student_lesson.self_chapter_id

    total_lessons = StudentLesson.query.filter_by(
        student_id=student.id, level_id=level_id
    ).count()
    finished_lessons = StudentLesson.query.filter_by(
        student_id=student.id, level_id=level_id, percentage=100
    ).count()

    chapter_percentage = round((finished_lessons / total_lessons) * 100) if total_lessons else 0

    student_chapter = StudentChapter.query.filter_by(
        id=chapter_id, level_id=level_id, student_id=student.id
    ).first()
    if student_chapter:
        student_chapter.percentage = chapter_percentage
        db.session.commit()

    # === 5. Update Level Percentage ===
    total_chapters = StudentChapter.query.filter_by(
        student_id=student.id, level_id=level_id
    ).count()
    finished_chapters = StudentChapter.query.filter_by(
        student_id=student.id, level_id=level_id, percentage=100
    ).count()

    level_percentage = round((finished_chapters / total_chapters) * 100) if total_chapters else 0

    student_level = StudentLevel.query.filter_by(
        level_id=level_id, student_id=student.id
    ).first()
    if student_level:
        student_level.percentage = level_percentage
        db.session.commit()

    # === 6. Update Subject Percentage ===
    subject_id = lesson.subject_id
    total_levels = StudentLevel.query.filter_by(
        student_id=student.id, subject_id=subject_id
    ).count()
    finished_levels = StudentLevel.query.filter_by(
        student_id=student.id, subject_id=subject_id, percentage=100
    ).count()

    subject_percentage = round((finished_levels / total_levels) * 100) if total_levels else 0

    student_subject = StudentSubject.query.filter_by(
        student_id=student.id, subject_id=subject_id
    ).first()
    if student_subject:
        student_subject.percentage = subject_percentage
        db.session.commit()
