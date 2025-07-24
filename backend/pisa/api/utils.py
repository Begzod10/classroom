from backend.models.basic_model import db, Pisa, PisaBlockText, PisaBlockTextAnswer, PisaBlockQuestionOptions, PisaTest, \
    PisaStudent, PisaFileType, PisaBlockOptionsStudent, PisaBlockTextAnswerStudent, School, create_school, User, \
    PisaStudent, Role, Location
import os
from app import current_app
import uuid


def ensure_dir_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def generate_unique_filename(filename):
    ext = os.path.splitext(filename)[1]
    return f"{uuid.uuid4().hex}{ext}"


def remove_file(file_id, model):
    file = model.query.filter_by(id=file_id).first()
    if not file:
        return

    # Check if file is used elsewhere
    usage_in_blocks = PisaBlockText.query.filter(PisaBlockText.file_id == file_id).count()
    usage_in_options = PisaBlockQuestionOptions.query.filter(PisaBlockQuestionOptions.file_id == file_id).count()

    if usage_in_blocks + usage_in_options > 1:
        file.delete()  # remove only from DB, not filesystem
        return

    try:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(file.url))
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Failed to delete file: {e}")

    file.delete()


def serialize_answer(answer, student_answer=None):
    return {
        'id': answer.id,
        'pisa_block_id': answer.pisa_block_id,
        'text': answer.text,
        'statusWord': answer.statusWord,
        'type': answer.type,
        'wrapped': answer.wrapped,
        'index': answer.index,
        'student_block': student_answer.convert_json() if student_answer else None
    }


def serialize_option(option, student_option=None):
    return {
        "id": option.id,
        "pisa_block_id": option.pisa_block_id,
        "file_id": option.file_id,
        "index": option.index,
        "image_url": option.file.url if option.file else None,
        "innerType": option.innerType,
        "isTrue": option.isTrue,
        "text": option.text,
        "answer": option.answer,
        "student_block": student_option.convert_json() if student_option else None
    }


def serialize_block(pisa_block, pisa_test_student, pisa_student):
    answers = PisaBlockTextAnswer.query.filter_by(pisa_block_id=pisa_block.id).order_by(PisaBlockTextAnswer.index).all()
    options = PisaBlockQuestionOptions.query.filter_by(pisa_block_id=pisa_block.id).order_by(
        PisaBlockQuestionOptions.index).all()

    serialized_answers = []
    for a in answers:
        student_a = PisaBlockTextAnswerStudent.query.filter_by(
            pisa_test_id=pisa_test_student.id,
            student_id=pisa_student.id,
            text_answer_id=a.id,
            pisa_block_text_id=pisa_block.id
        ).first() if pisa_test_student else None
        serialized_answers.append(serialize_answer(a, student_a))

    serialized_options = []
    for o in options:
        student_o = PisaBlockOptionsStudent.query.filter_by(
            pisa_test_id=pisa_test_student.id,
            student_id=pisa_student.id,
            pisa_block_question_options_id=o.id,
            pisa_block_text_id=pisa_block.id
        ).first() if pisa_test_student else None
        serialized_options.append(serialize_option(o, student_o))

    return {
        'id': pisa_block.id,
        'pisa_id': pisa_block.pisa_id,
        'text': pisa_block.text,
        'position': pisa_block.position,
        'index': pisa_block.index,
        'type': pisa_block.type_block,
        'completed': pisa_block.completed,
        'words': pisa_block.words,
        'editorState': pisa_block.editorState,
        'typeVariants': pisa_block.typeVariants,
        'type_question': pisa_block.type_question,
        'image_url': pisa_block.file.url if pisa_block.file else None,
        'innerType': pisa_block.innerType,
        'video_url': pisa_block.video_url,
        'answers': serialized_answers,
        'options': serialized_options
    }
