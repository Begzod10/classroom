import pprint
from flask import Blueprint, request, jsonify
from flasgger import swag_from

from app import db
from backend.models.basic_model import Pisa, PisaBlockText, PisaBlockTextAnswer, PisaBlockQuestionOptions

crud_test_pisa_bp = Blueprint('test_pisa', __name__)


@crud_test_pisa_bp.route('/test/crud', defaults={'pk': None}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@crud_test_pisa_bp.route('/test/crud/<pk>', methods=['GET', 'POST', 'PUT', 'DELETE'])
# @swag_from({
#     'tags': ['Pisa'],
#     'parameters': [
#         {
#             'name': 'pk',
#             'in': 'path',
#             'type': 'integer',
#             'required': False,
#             'description': 'Pisa test ID (optional for POST)'
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'Successful Pisa operation response',
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'msg': {'type': 'string'},
#                     'success': {'type': 'boolean'},
#                     'id': {'type': 'integer'}
#                 }
#             },
#             'examples': {
#                 'application/json': {
#                     'msg': 'pisa muvaffaqiyatli yaratildi',
#                     'success': True,
#                     'id': 1
#                 }
#             }
#         }
#     }
# })
def crud_pisa_test(pk):
    if request.method == "POST":
        pisa_test = Pisa(name="unnamed", status=False)
        pisa_test.add()
        return jsonify({"msg": "pisa muvaffaqiyatli yaratildi", "success": True, 'id': pisa_test.id})

    elif request.method == "PUT":
        pisa_test = Pisa.query.filter_by(id=pk).first()
        if not pisa_test:
            return jsonify({"msg": "Not found", "success": False}), 404
        data = request.get_json()
        pisa_test.name = data.get('name', pisa_test.name)
        pisa_test.status = data.get('status', pisa_test.status)
        db.session.commit()
        return jsonify({"msg": "pisa muvaffaqiyatli o'zgartirildi", "success": True})

    elif request.method == "DELETE":
        pisa_test = Pisa.query.filter_by(id=pk).first()
        if not pisa_test:
            return jsonify({"msg": "Not found", "success": False}), 404
        pisa_test.deleted = True
        db.session.commit()
        return jsonify({"msg": "pisa muvaffaqiyatli o'chirildi", "success": True})

    elif request.method == "GET":
        pisa_test = Pisa.query.filter_by(id=pk).first()
        if not pisa_test:
            return jsonify({"msg": "Not found", "success": False}), 404

        info = {
            'pisa_id': pisa_test.id,
            'name': pisa_test.name,
            'status': pisa_test.status,
            'pisa_blocks_left': [],
            'pisa_blocks_right': []
        }

        blocks = PisaBlockText.query.filter_by(pisa_id=pisa_test.id).order_by(PisaBlockText.index).all()

        for block in blocks:
            answers = PisaBlockTextAnswer.query.filter_by(pisa_block_id=block.id).order_by(
                PisaBlockTextAnswer.index).all()
            options = PisaBlockQuestionOptions.query.filter_by(pisa_block_id=block.id).order_by(
                PisaBlockQuestionOptions.index).all()

            block_info = {
                'id': block.id,
                'pisa_id': block.pisa_id,
                'text': block.text,
                'position': block.position,
                'index': block.index,
                'type': block.type_block,
                'completed': block.completed,
                'words': block.words,
                'editorState': block.editorState,
                'typeVariants': block.typeVariants,
                'type_question': block.type_question,
                'image_url': block.file.url if block.file else None,
                'file': block.file.url if block.file else None,
                'innerType': block.innerType,
                'video_url': block.video_url,
                'answers': [a.convert_json() for a in answers],
                'options': [o.convert_json() for o in options],
                'can_delete': not block.answers_students and not block.options_students
            }

            if block.position == 'left':
                info['pisa_blocks_left'].append(block_info)
            else:
                info['pisa_blocks_right'].append(block_info)

        return jsonify(info)


@crud_test_pisa_bp.route('/list/<deleted>')
# @swag_from({
#     'tags': ['Pisa'],
#     'parameters': [
#         {
#             'name': 'deleted',
#             'in': 'path',
#             'type': 'string',
#             'enum': ['true', 'false'],
#             'required': True,
#             'description': 'Filter by deletion status (true = deleted, false = active)'
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'List of Pisa tests',
#             'schema': {
#                 'type': 'array',
#                 'items': {
#                     'type': 'object',
#                     'properties': {
#                         'id': {'type': 'integer'},
#                         'name': {'type': 'string'},
#                         'status': {'type': 'boolean'},
#                         # Add more fields from convert_json() if needed
#                     }
#                 }
#             },
#             'examples': {
#                 'application/json': [
#                     {'id': 1, 'name': 'Math Test', 'status': True},
#                     {'id': 2, 'name': 'Science Test', 'status': False}
#                 ]
#             }
#         }
#     }
# })
def pisa_test_list(deleted):
    if deleted == 'true':
        pisa_tests = Pisa.query.filter_by(deleted=True).all()
    else:
        pisa_tests = Pisa.query.filter_by(deleted=False).all()

    return jsonify([test.convert_json() for test in pisa_tests])
