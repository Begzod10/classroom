from app import app, jsonify, api, request, or_
from backend.models.basic_model import db, Pisa, PisaBlockText, PisaBlockTextAnswer, PisaBlockQuestionOptions, PisaTest, \
    PisaStudent, PisaFileType, PisaBlockOptionsStudent, PisaBlockTextAnswerStudent, School, create_school, User, \
    PisaStudent, Role
import pprint
from backend.basics.settings import check_exist_classroom_id
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route(f'{api}/register_pisa', methods=['GET', 'POST'])
def register_pisa():
    create_school()
    if request.method == "POST":
        pprint.pprint(request.get_json())
        classroom_id = check_exist_classroom_id()
        username = request.get_json()['username']
        name = request.get_json()['name']
        surname = request.get_json()['surname']
        language = request.get_json()['language']
        school = request.get_json()['school']
        parentPhone = request.get_json()['parentPhone']
        get_school = School.query.filter(School.id == school).first()
        role = Role.query.filter(Role.type == "student_test", Role.role == "a52v23q13").first()
        if not role:
            role = Role(type="student_test", role="a52v23q13")
            role.add_commit()
        add_user = User(username=username, name=name, surname=surname, balance=0, system_name="pisa",
                        parent_phone=parentPhone, password=generate_password_hash("12345678"),
                        role_id=role.id,
                        classroom_user_id=classroom_id, education_language=language)
        add_user.add_commit()
        add_student = PisaStudent(user_id=add_user.id, school_id=get_school.id)
        add_student.add()
        return jsonify({"success": True, "msg": "Muvaffaqiyatli ro'yxatdan o'tdingiz"}), 200
    schools = School.query.order_by(School.number).all()
    return jsonify([school.convert_json() for school in schools])


@app.route(f'{api}/check_username_pisa', methods=['POST'])
def check_username_pisa():
    username = request.get_json()['username']
    user = User.query.filter(User.username == username, User.system_name == "pisa").first()
    if user:
        return jsonify({"success": False, "msg": "Bunday foydalanuvchi mavjud"}), 200
    return jsonify({"success": True, "msg": "Bunday foydalanuvchi mavjud emas"}), 200


@app.route(f'{api}/get_pisa_list')
@jwt_required()
def get_pisa_list():
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    pisa_student = PisaStudent.query.filter(PisaStudent.user_id == user.id).first()

    pisa_tests = Pisa.query.filter(Pisa.status == True, Pisa.deleted == False).all()
    pisa_list = []
    for pisa in pisa_tests:
        pisa_test = PisaTest.query.filter(PisaTest.pisa_id == pisa.id,
                                          PisaTest.student_id == pisa_student.id).first() if pisa_student else None

        info = {
            "id": pisa.id,
            "name": pisa.name,
            "total_questions": pisa.total_questions,
            "finished": True if pisa_test and pisa_test.finished else False
        }
        pisa_list.append(info)
    return jsonify(pisa_list)


@app.route(f'{api}/get_pisa_test/<pk>')
@jwt_required()
def get_pisa_test(pk):
    pisa_test = Pisa.query.filter(Pisa.id == pk).first()
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    pisa_student = PisaStudent.query.filter(PisaStudent.user_id == user.id).first()
    pisa_test_student = PisaTest.query.filter(PisaTest.pisa_id == pk,
                                              PisaTest.student_id == pisa_student.id).first() if pisa_student else None
    if pisa_test_student and pisa_test_student.finished:
        return jsonify({"success": False, "msg": "Pisa test bajarilib bolingan!"}), 200
    pisa_blocks_left = PisaBlockText.query.filter(PisaBlockText.pisa_id == pisa_test.id,
                                                  PisaBlockText.position == 'left').order_by(
        PisaBlockText.index).all()
    pisa_blocks_right = PisaBlockText.query.filter(PisaBlockText.pisa_id == pisa_test.id,
                                                   PisaBlockText.position == 'right').order_by(
        PisaBlockText.index).all()
    info = {
        'pisa_id': pisa_test.id,
        'name': pisa_test.name,
        'status': pisa_test.status,
        'pisa_blocks_left': [],
        'pisa_blocks_right': [],
        'pisa_test_id': pisa_test_student.id if pisa_test_student else None
    }
    for pisa_block in pisa_blocks_left:
        block_text_answers = PisaBlockTextAnswer.query.filter_by(pisa_block_id=pisa_block.id).order_by(
            PisaBlockTextAnswer.index).all()
        block_text_options = PisaBlockQuestionOptions.query.filter_by(pisa_block_id=pisa_block.id).order_by(
            PisaBlockQuestionOptions.index).all()
        info_left = {
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
            'answers': [],
            'options': []
        }
        for answer in block_text_answers:
            student_block = {}
            if pisa_test_student:
                student_answer = PisaBlockTextAnswerStudent.query.filter(
                    PisaBlockTextAnswerStudent.pisa_test_id == pisa_test_student.id,
                    PisaBlockTextAnswerStudent.student_id == pisa_student.id,
                    PisaBlockTextAnswerStudent.text_answer_id == answer.id,
                    PisaBlockTextAnswerStudent.pisa_block_text_id == pisa_block.id).first()
                student_block = student_answer.convert_json() if student_answer else None
            info_test = {
                'id': answer.id,
                'pisa_block_id': answer.pisa_block_id,
                'text': answer.text,
                'statusWord': answer.statusWord,
                'type': answer.type,
                'wrapped': answer.wrapped,
                'index': answer.index,
                "student_block": student_block
            }
            info_left['answers'].append(info_test)
        for option in block_text_options:
            student_block = {}
            if pisa_test_student:
                student_option = PisaBlockOptionsStudent.query.filter(
                    PisaBlockOptionsStudent.pisa_test_id == pisa_test_student.id,
                    PisaBlockOptionsStudent.student_id == pisa_student.id,
                    PisaBlockOptionsStudent.pisa_block_question_options_id == option.id,
                    PisaBlockOptionsStudent.pisa_block_text_id == pisa_block.id).first()
                student_block = student_option.convert_json() if student_option else None
            info_test = {
                "id": option.id,
                "pisa_block_id": option.pisa_block_id,
                "file_id": option.file_id,
                "index": option.index,
                "image_url": option.file.url if option.file else None,
                "innerType": option.innerType,
                "isTrue": option.isTrue,
                "text": option.text,
                "answer": option.answer,
                "student_block": student_block
            }
            info_left['options'].append(info_test)
        info['pisa_blocks_left'].append(info_left)
    for pisa_block in pisa_blocks_right:
        block_text_answers = PisaBlockTextAnswer.query.filter_by(pisa_block_id=pisa_block.id).order_by(
            PisaBlockTextAnswer.index).all()
        block_text_options = PisaBlockQuestionOptions.query.filter_by(pisa_block_id=pisa_block.id).order_by(
            PisaBlockQuestionOptions.index).all()
        info_right = {
            'id': pisa_block.id,
            'pisa_id': pisa_block.pisa_id,
            'text': pisa_block.text,
            'position': pisa_block.position,
            'index': pisa_block.index,
            'type': pisa_block.type_block,
            'completed': pisa_block.completed,
            'words': pisa_block.words,
            'image_url': pisa_block.file.url if pisa_block.file else None,
            'innerType': pisa_block.innerType,
            'editorState': pisa_block.editorState,
            'typeVariants': pisa_block.typeVariants,
            'type_question': pisa_block.type_question,
            'video_url': pisa_block.video_url,
            'answers': [],
            'options': []
        }
        for answer in block_text_answers:
            student_block = {}
            if pisa_test_student:
                student_answer = PisaBlockTextAnswerStudent.query.filter(
                    PisaBlockTextAnswerStudent.pisa_test_id == pisa_test_student.id,
                    PisaBlockTextAnswerStudent.student_id == pisa_student.id,
                    PisaBlockTextAnswerStudent.text_answer_id == answer.id,
                    PisaBlockTextAnswerStudent.pisa_block_text_id == pisa_block.id).first()
                student_block = student_answer.convert_json() if student_answer else None
            info_test = {
                'id': answer.id,
                'pisa_block_id': answer.pisa_block_id,
                'text': answer.text,
                'statusWord': answer.statusWord,
                'type': answer.type,
                'wrapped': answer.wrapped,
                'index': answer.index,
                "student_block": student_block
            }
            info_right['answers'].append(info_test)
        for option in block_text_options:
            student_block = {}
            if pisa_test_student:
                student_option = PisaBlockOptionsStudent.query.filter(
                    PisaBlockOptionsStudent.pisa_test_id == pisa_test_student.id,
                    PisaBlockOptionsStudent.student_id == pisa_student.id,
                    PisaBlockOptionsStudent.question_options_id == option.id,
                    PisaBlockOptionsStudent.pisa_block_text_id == pisa_block.id).first()
                student_block = student_option.convert_json() if student_option else None
            info_test = {
                "id": option.id,
                "pisa_block_id": option.pisa_block_id,
                "file_id": option.file_id,
                "index": option.index,
                "image_url": option.file.url if option.file else None,
                "innerType": option.innerType,
                "isTrue": option.isTrue,
                "text": option.text,
                "answer": option.answer,
                "student_block": student_block
            }
            info_right['options'].append(info_test)
        info['pisa_blocks_right'].append(info_right)

    return jsonify(info)


@app.route(f'{api}/complete_pisa_test/<pk>', methods=['POST'])
@jwt_required()
def complete_pisa_test(pk):
    pprint.pprint(request.get_json())
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    pisa_student = PisaStudent.query.filter(PisaStudent.user_id == user.id).first()
    get_pisa = Pisa.query.filter(Pisa.id == pk).first()
    get_blocks = PisaBlockText.query.filter(PisaBlockText.pisa_id == get_pisa.id).filter(
        or_(PisaBlockText.answers != None, PisaBlockText.options != None)).count()

    get_pisa.total_questions = get_blocks
    db.session.commit()
    pisa_test_exist = PisaTest.query.filter(PisaTest.pisa_id == get_pisa.id,
                                            PisaTest.student_id == pisa_student.id).first()

    if not pisa_test_exist:
        pisa_test_exist = PisaTest(pisa_id=get_pisa.id, student_id=pisa_student.id, true_answers=0,
                                   false_answers=0, result=0)
        pisa_test_exist.add()
    type_question = request.get_json()['type'] if 'type' in request.get_json() else None
    get_block = PisaBlockText.query.filter(PisaBlockText.pisa_id == get_pisa.id,
                                           PisaBlockText.id == request.get_json()['block_id']).first()
    if type_question:
        if type_question == 'select' or type_question == 'input':

            get_pisa_options = PisaBlockQuestionOptions.query.filter(
                PisaBlockQuestionOptions.pisa_block_id == get_block.id,
                PisaBlockQuestionOptions.answer == '',
                PisaBlockQuestionOptions.id ==
                request.get_json()['answer']['id']).first() if 'id' in \
                                                               request.get_json()[
                                                                   'answer'] else None
            get_pisa_input = PisaBlockQuestionOptions.query.filter(
                PisaBlockQuestionOptions.pisa_block_id == get_block.id, PisaBlockQuestionOptions.answer != '').first()

            if get_pisa_options:
                student_options_exists = PisaBlockOptionsStudent.query.filter(
                    PisaBlockOptionsStudent.pisa_block_text_id == get_block.id,
                    PisaBlockOptionsStudent.pisa_test_id == pisa_test_exist.id,
                    PisaBlockOptionsStudent.student_id == pisa_student.id).first()
                if not student_options_exists:
                    student_options_exists = PisaBlockOptionsStudent(pisa_block_question_options_id=get_pisa_options.id,
                                                                     pisa_test_id=pisa_test_exist.id,
                                                                     text=get_pisa_options.text,
                                                                     answer=get_pisa_options.answer,
                                                                     isTrue=get_pisa_options.isTrue,
                                                                     pisa_block_text_id=get_block.id,
                                                                     student_id=pisa_student.id)
                    student_options_exists.add()
                else:
                    student_options_exists.text = get_pisa_options.text
                    student_options_exists.answer = get_pisa_options.answer
                    student_options_exists.isTrue = get_pisa_options.isTrue
                    student_options_exists.pisa_block_question_options_id = get_pisa_options.id
                    db.session.commit()

            if get_pisa_input:
                student_input_exists = PisaBlockOptionsStudent.query.filter(
                    PisaBlockOptionsStudent.pisa_block_text_id == get_block.id,
                    PisaBlockOptionsStudent.pisa_test_id == pisa_test_exist.id,
                    PisaBlockOptionsStudent.student_id == pisa_student.id).first()
                if not student_input_exists:
                    student_input_exists = PisaBlockOptionsStudent(pisa_block_question_options_id=get_pisa_input.id,
                                                                   pisa_test_id=pisa_test_exist.id,
                                                                   text=get_pisa_input.text,
                                                                   answer=get_pisa_input.answer,
                                                                   isTrue=True if request.get_json()[
                                                                                      'answer'] == get_pisa_input.answer else False,
                                                                   pisa_block_text_id=get_block.id,
                                                                   student_id=pisa_student.id)
                    student_input_exists.add()
                else:
                    student_input_exists.text = get_pisa_input.text
                    student_input_exists.answer = get_pisa_input.answer
                    student_input_exists.isTrue = True if request.get_json()[
                                                              'answer'] == get_pisa_input.answer else False
                    student_input_exists.pisa_block_question_options_id = get_pisa_input.id
                    db.session.commit()
    else:
        answers = request.get_json()['answers']
        for answer in answers:
            get_answers = PisaBlockTextAnswer.query.filter(PisaBlockTextAnswer.pisa_block_id == get_block.id,
                                                           PisaBlockTextAnswer.id == answer['id']).first()
            if answer['type'] == 'input':
                status = True if get_answers.text == answer['value'] else False
            else:
                status = True if answer['id'] == answer['valueId'] else False
            exist_answer = PisaBlockTextAnswerStudent.query.filter(
                PisaBlockTextAnswerStudent.pisa_block_text_id == get_block.id,
                PisaBlockTextAnswerStudent.pisa_test_id == pisa_test_exist.id,
                PisaBlockTextAnswerStudent.student_id == pisa_student.id).first()
            if not exist_answer:
                exist_answer = PisaBlockTextAnswerStudent(pisa_block_text_id=get_block.id,
                                                          pisa_test_id=pisa_test_exist.id,
                                                          text=get_answers.text,
                                                          statusWord=get_answers.statusWord,
                                                          type=get_answers.type,
                                                          status=status,
                                                          text_answer_id=get_answers.id,
                                                          student_id=pisa_student.id)
                exist_answer.add()
            else:
                exist_answer.text = get_answers.text
                exist_answer.statusWord = get_answers.statusWord
                exist_answer.type = get_answers.type
                exist_answer.status = status
                exist_answer.text_answer_id = get_answers.id
                db.session.commit()

    all_true_options = PisaBlockOptionsStudent.query.filter(PisaBlockOptionsStudent.pisa_test_id == pisa_test_exist.id,
                                                            PisaBlockOptionsStudent.student_id == pisa_student.id,
                                                            PisaBlockOptionsStudent.isTrue == True).count()
    all_false_options = PisaBlockOptionsStudent.query.filter(PisaBlockOptionsStudent.pisa_test_id == pisa_test_exist.id,
                                                             PisaBlockOptionsStudent.student_id == pisa_student.id,
                                                             PisaBlockOptionsStudent.isTrue == False).count()

    all_true_inputs = PisaBlockTextAnswerStudent.query.filter(
        PisaBlockTextAnswerStudent.pisa_test_id == pisa_test_exist.id,
        PisaBlockTextAnswerStudent.student_id == pisa_student.id,
        PisaBlockTextAnswerStudent.status == True).count()
    all_false_inputs = PisaBlockTextAnswerStudent.query.filter(
        PisaBlockTextAnswerStudent.pisa_test_id == pisa_test_exist.id,
        PisaBlockTextAnswerStudent.student_id == pisa_student.id,
        PisaBlockTextAnswerStudent.status == False).count()

    result = round((all_true_options + all_true_inputs / get_pisa.total_questions) * 100)

    pisa_test_exist.true_answers = all_true_options + all_true_inputs
    pisa_test_exist.false_answers = all_false_options + all_false_inputs
    pisa_test_exist.result = result
    pisa_test_exist.total_questions = get_pisa.total_questions
    db.session.commit()

    pprint.pprint(request.get_json())
    return jsonify({"success": True, "msg": "Muvaffaqiyatli yakunlandi", "student_pisa_id": pisa_test_exist.id}), 200


@app.route(f'{api}/show_results/<pisa_test_id>', methods=['GET'])
@jwt_required()
def show_results(pisa_test_id):
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()

    pisa_student = PisaStudent.query.filter(PisaStudent.user_id == user.id).first()
    pisa_test = PisaTest.query.filter(PisaTest.pisa_id == pisa_test_id, PisaTest.student_id == pisa_student.id).first()
    pisa_test.finished = True
    db.session.commit()
    return jsonify({"success": True, "msg": "Muvaffaqiyatli yakunlandi", "test": pisa_test.convert_json()}), 200


@app.route(f'{api}/check_pisa_test/<pk>', methods=['GET'])
@jwt_required()
def check_pisa_test(pk):
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    pisa_student = PisaStudent.query.filter(PisaStudent.user_id == user.id).first()
    pass
