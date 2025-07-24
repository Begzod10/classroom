from app import app, jsonify, api, request, or_
from backend.models.basic_model import db, Pisa, PisaBlockText, PisaBlockTextAnswer, PisaBlockQuestionOptions, PisaTest, \
    PisaStudent, PisaFileType, PisaBlockOptionsStudent, PisaBlockTextAnswerStudent, School, create_school, User, \
    PisaStudent, Role, Location
import pprint
from .utils import serialize_block
from backend.basics.settings import check_exist_classroom_id
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint
from flasgger import swag_from

pisa_student_bp = Blueprint("student", __name__)


@pisa_student_bp.route('/register', methods=['GET', 'POST'])
# @swag_from({
#     'tags': ['Pisa Student'],
#     'summary': 'Register a new Pisa student or fetch location list',
#     'description': 'POST to register a student, GET to fetch available locations',
#     'parameters': [],
#     'requestBody': {
#         'required': True,
#         'content': {
#             'application/json': {
#                 'example': {
#                     'username': 'student123',
#                     'name': 'Ali',
#                     'surname': 'Karimov',
#                     'language': 'uz',
#                     'location': 2,
#                     'parentPhone': '+998901234567'
#                 }
#             }
#         }
#     },
#     'responses': {
#         200: {
#             'description': 'Success response for registration or location list',
#             'content': {
#                 'application/json': {
#                     'examples': {
#                         'POST Success': {
#                             'summary': 'Registration success',
#                             'value': {
#                                 'success': True,
#                                 'msg': "Muvaffaqiyatli ro'yxatdan o'tdingiz"
#                             }
#                         },
#                         'GET Success': {
#                             'summary': 'List of locations',
#                             'value': [
#                                 {'id': 1, 'name': 'Tashkent', 'platform_id': 1},
#                                 {'id': 2, 'name': 'Samarkand', 'platform_id': 2}
#                             ]
#                         }
#                     }
#                 }
#             }
#         },
#         400: {
#             'description': 'Bad request or validation error'
#         }
#     }
# })
def register_pisa():
    create_school()

    if request.method == "POST":
        data = request.get_json()
        classroom_id = check_exist_classroom_id()
        username = data['username']
        name = data['name']
        surname = data['surname']
        language = data['language']
        location = data['location']
        parentPhone = data['parentPhone']

        role = Role.query.filter(Role.type == "student_test", Role.role == "a52v23q13").first()
        if not role:
            role = Role(type="student_test", role="a52v23q13")
            role.add_commit()

        add_user = User(
            username=username,
            name=name,
            surname=surname,
            balance=0,
            system_name="pisa",
            parent_phone=parentPhone,
            password=generate_password_hash("12345678"),
            role_id=role.id,
            location_id=location,
            classroom_user_id=classroom_id,
            education_language=language
        )
        add_user.add_commit()

        add_student = PisaStudent(user_id=add_user.id)
        add_student.add()

        return jsonify({"success": True, "msg": "Muvaffaqiyatli ro'yxatdan o'tdingiz"}), 200

    locations = Location.query.order_by(Location.platform_id).all()
    return jsonify([location.convert_json() for location in locations])


from flasgger import swag_from


@pisa_student_bp.route('/check/username', methods=['POST'])
# @swag_from({
#     'tags': ['Pisa Student'],
#     'summary': 'Check if a Pisa username exists',
#     'description': 'Checks whether a user with the given username already exists in the Pisa system.',
#     'requestBody': {
#         'required': True,
#         'content': {
#             'application/json': {
#                 'example': {
#                     'username': 'student123'
#                 }
#             }
#         }
#     },
#     'responses': {
#         200: {
#             'description': 'Username check result',
#             'content': {
#                 'application/json': {
#                     'examples': {
#                         'Exists': {
#                             'summary': 'User already exists',
#                             'value': {
#                                 'success': False,
#                                 'msg': "Bunday foydalanuvchi mavjud"
#                             }
#                         },
#                         'Not Exists': {
#                             'summary': 'User does not exist',
#                             'value': {
#                                 'success': True,
#                                 'msg': "Bunday foydalanuvchi mavjud emas"
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     }
# })
def check_username_pisa():
    username = request.get_json()['username']
    user = User.query.filter(User.username == username, User.system_name == "pisa").first()
    if user:
        return jsonify({"success": False, "msg": "Bunday foydalanuvchi mavjud"}), 200
    return jsonify({"success": True, "msg": "Bunday foydalanuvchi mavjud emas"}), 200


@pisa_student_bp.route('/get/list')
@jwt_required()
# @swag_from({
#     'tags': ['Pisa Student'],
#     'summary': 'Get available Pisa test list',
#     'description': 'Returns a list of Pisa tests available to the logged-in student, including test completion status.',
#     'security': [{'BearerAuth': []}],
#     'responses': {
#         200: {
#             'description': 'List of Pisa tests',
#             'content': {
#                 'application/json': {
#                     'example': [
#                         {
#                             "id": 1,
#                             "name": "PISA 2025 Test A",
#                             "total_questions": 15,
#                             "finished": False
#                         },
#                         {
#                             "id": 2,
#                             "name": "PISA 2025 Test B",
#                             "total_questions": 20,
#                             "finished": True
#                         }
#                     ]
#                 }
#             }
#         },
#         401: {
#             'description': 'Missing or invalid JWT token'
#         }
#     }
# })
def get_pisa_list():
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    pisa_student = PisaStudent.query.filter(PisaStudent.user_id == user.id).first()

    pisa_tests = Pisa.query.filter(Pisa.status == True, Pisa.deleted == False).all()
    pisa_list = []
    for pisa in pisa_tests:
        pisa_test = PisaTest.query.filter(
            PisaTest.pisa_id == pisa.id,
            PisaTest.student_id == pisa_student.id
        ).first() if pisa_student else None

        info = {
            "id": pisa.id,
            "name": pisa.name,
            "total_questions": pisa.total_questions,
            "finished": bool(pisa_test and pisa_test.finished)
        }
        pisa_list.append(info)
    return jsonify(pisa_list)


@pisa_student_bp.route(f'/get/test/<pk>')
# @swag_from({
#     'tags': ['PISA Tests'],
#     'parameters': [
#         {
#             'name': 'pk',
#             'in': 'path',
#             'required': True,
#             'type': 'integer',
#             'description': 'PISA Test ID'
#         },
#         {
#             'name': 'Authorization',
#             'in': 'header',
#             'type': 'string',
#             'required': True,
#             'description': 'JWT access token. Format: Bearer {token}'
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'PISA test data or message if already completed',
#             'examples': {
#                 'application/json': {
#                     "pisa_id": 1,
#                     "name": "Math PISA",
#                     "status": True,
#                     "pisa_test_id": 10,
#                     "pisa_blocks_left": [
#                         {"id": 1, "index": 0, "content": "..."}
#                     ],
#                     "pisa_blocks_right": [
#                         {"id": 2, "index": 0, "content": "..."}
#                     ]
#                 }
#             }
#         },
#         404: {
#             'description': 'PISA Test or User not found'
#         }
#     },
#     'description': """
# Returns detailed PISA test blocks and student progress.
#
# - Verifies if the test is already completed by the student
# - Returns both left and right side blocks for the PISA test
# """
# })
@jwt_required()
def get_pisa_test(pk):
    pisa_test = Pisa.query.filter_by(id=pk).first_or_404()
    user = User.query.filter_by(classroom_user_id=get_jwt_identity()).first_or_404()
    pisa_student = PisaStudent.query.filter_by(user_id=user.id).first()
    pisa_test_student = PisaTest.query.filter_by(pisa_id=pk,
                                                 student_id=pisa_student.id).first() if pisa_student else None

    if pisa_test_student and pisa_test_student.finished:
        return jsonify({"success": False, "msg": "Pisa test bajarilib bo‘lgan!"}), 200

    blocks_left = PisaBlockText.query.filter_by(pisa_id=pisa_test.id, position='left').order_by(
        PisaBlockText.index).all()
    blocks_right = PisaBlockText.query.filter_by(pisa_id=pisa_test.id, position='right').order_by(
        PisaBlockText.index).all()

    return jsonify({
        'pisa_id': pisa_test.id,
        'name': pisa_test.name,
        'status': pisa_test.status,
        'pisa_test_id': pisa_test_student.id if pisa_test_student else None,
        'pisa_blocks_left': [serialize_block(b, pisa_test_student, pisa_student) for b in blocks_left],
        'pisa_blocks_right': [serialize_block(b, pisa_test_student, pisa_student) for b in blocks_right]
    })


@pisa_student_bp.route(f'/complete/pisa/test/<pk>', methods=['POST'])
@jwt_required()
# @swag_from({
#     'tags': ['Pisa'],
#     'summary': 'Submit answers for a Pisa test block',
#     'parameters': [
#         {
#             'name': 'pk',
#             'in': 'path',
#             'required': True,
#             'description': 'Pisa test ID',
#             'type': 'integer'
#         },
#         {
#             'name': 'body',
#             'in': 'body',
#             'required': True,
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'block_id': {'type': 'integer'},
#                     'type': {'type': 'string', 'enum': ['select', 'input']},
#                     'answer': {
#                         'type': 'object',
#                         'properties': {
#                             'id': {'type': 'integer'},
#                             'value': {'type': 'string'},
#                             'valueId': {'type': 'integer'}
#                         }
#                     },
#                     'answers': {
#                         'type': 'array',
#                         'items': {
#                             'type': 'object',
#                             'properties': {
#                                 'id': {'type': 'integer'},
#                                 'type': {'type': 'string', 'enum': ['input', 'select']},
#                                 'value': {'type': 'string'},
#                                 'valueId': {'type': 'integer'}
#                             }
#                         }
#                     }
#                 },
#                 'example': {
#                     "block_id": 1,
#                     "type": "input",
#                     "answer": {"id": 3, "value": "Answer"}
#                 }
#             }
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'Submission result',
#             'examples': {
#                 'application/json': {
#                     "success": True,
#                     "msg": "Muvaffaqiyatli yakunlandi",
#                     "student_pisa_id": 123
#                 }
#             }
#         }
#     }
# })
def complete_pisa_test(pk):
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    pisa_student = PisaStudent.query.filter_by(user_id=user.id).first()

    if not pisa_student:
        pisa_student = PisaStudent(user_id=user.id)
        db.session.add(pisa_student)
        db.session.commit()
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
                PisaBlockQuestionOptions.answer == None,
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

    result = round(((all_true_options + all_true_inputs) / get_pisa.total_questions) * 100)

    pisa_test_exist.true_answers = all_true_options + all_true_inputs
    pisa_test_exist.false_answers = all_false_options + all_false_inputs
    pisa_test_exist.result = result
    pisa_test_exist.total_questions = get_pisa.total_questions
    db.session.commit()

    return jsonify({"success": True, "msg": "Muvaffaqiyatli yakunlandi", "student_pisa_id": pisa_test_exist.id}), 200


@pisa_student_bp.route(f'/show/result/<pisa_test_id>', methods=['GET'])
@jwt_required()
def show_results(pisa_test_id):
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()

    pisa_student = PisaStudent.query.filter(PisaStudent.user_id == user.id).first()
    pisa_test = PisaTest.query.filter(PisaTest.pisa_id == pisa_test_id, PisaTest.student_id == pisa_student.id).first()
    pisa_test.finished = True
    db.session.commit()
    return jsonify({"success": True, "msg": "Muvaffaqiyatli yakunlandi", "test": pisa_test.convert_json()}), 200


@pisa_student_bp.route('/show/results', methods=['GET'])
@jwt_required()
def show_all_results():
    location_id = request.args.get("location_id")
    test_id = request.args.get("pisa_test_id")

    users_query = User.query.join(Role).filter(Role.type == "student")

    if location_id:
        users_query = users_query.filter(User.location_id == location_id)

    users = users_query.all()

    if not users:
        return jsonify({"success": False, "msg": "Foydalanuvchilar topilmadi"}), 404

    all_results = []

    for user in users:
        pisa_student = PisaStudent.query.filter(PisaStudent.user_id == user.id).first()
        if not pisa_student:
            continue

        pisa_tests_query = PisaTest.query.filter(PisaTest.student_id == pisa_student.id)
        if test_id:
            pisa_tests_query = pisa_tests_query.filter(PisaTest.pisa_id == test_id)

        pisa_tests = pisa_tests_query.all()

        for test in pisa_tests:
            result = test.convert_json()
            result["user_id"] = user.id
            all_results.append(result)
    locations = Location.query.order_by(Location.platform_id).all()

    return jsonify({"success": True, "results": all_results,
                    "locations": [location.convert_json() for location in locations]}), 200


@pisa_student_bp.route(f'/check/pisa/test/<pk>', methods=['GET'])
@jwt_required()
def check_pisa_test(pk):
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    pisa_student = PisaStudent.query.filter(PisaStudent.user_id == user.id).first()
    pass


@pisa_student_bp.route('/list', methods=['GET', 'POST'])
def pisa_student_list():
    from sqlalchemy import or_

    if request.method == "POST":
        data = request.json or {}
        page = int(data.get('currentPage', 1))
        per_page = int(data.get('page_size', 50))

        query = PisaTest.query.join(PisaTest.student_pisa).join(PisaStudent.user).order_by(PisaTest.id.desc())

        pisa_test_id = data.get('test')
        location_id = data.get('branch')
        search = data.get('search')

        if pisa_test_id:
            query = query.filter(PisaTest.pisa_id == pisa_test_id)

        if location_id:
            query = query.filter(User.location_id == location_id)

        if search:
            query = query.filter(
                or_(
                    User.username.like(f"%{search}%"),
                    User.name.like(f"%{search}%"),
                    User.surname.like(f"%{search}%")
                )
            )
        total_students = query.count()
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [item.convert_json() for item in paginated.items]

        return jsonify({
            'pisa_students': items,
            "total_students": total_students,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': paginated.page
        }), 200

    else:
        # GET fallback (if you want to support it)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))

        query = PisaTest.query.order_by(PisaTest.id.desc())
        total_students = query.count()
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [item.convert_json() for item in paginated.items]

        return jsonify({
            'pisa_students': items,
            "total_students": total_students,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': paginated.page
        }), 200
