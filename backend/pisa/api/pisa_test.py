import pprint

from app import app, db, api, request, jsonify
from backend.models.basic_model import Pisa, PisaBlockText, PisaBlockTextAnswer, PisaBlockQuestionOptions
from backend.models.settings import iterate_models


@app.route(f'{api}/crud_pisa_test', defaults={'pk': None}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route(f'{api}/crud_pisa_test/<pk>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def crud_pisa_test(pk):
    if request.method == "POST":
        pisa_test = Pisa(name="unnamed", status=False)
        pisa_test.add()
        return jsonify({"msg": "pisa muvaffaqiyatli yaratildi", "success": True, 'id': pisa_test.id})
    elif request.method == "PUT":
        pisa_test = Pisa.query.filter_by(id=pk).first()
        pisa_test.name = request.get_json()['name']
        pisa_test.status = request.get_json()['status']
        other_pisa_tests = Pisa.query.filter(Pisa.id != pisa_test.id).all()
        for other_pisa_test in other_pisa_tests:
            other_pisa_test.status = False
            db.session.commit()
        db.session.commit()
        return jsonify({"msg": "pisa muvaffaqiyatli o'zgartirildi", "success": True})
    elif request.method == "DELETE":
        pisa_test = Pisa.query.filter_by(id=pk).first()
        pisa_test.deleted = True
        db.session.commit()
        return jsonify({"msg": "pisa muvaffaqiyatli o'chirildi", "success": True})
    elif request.method == "GET":
        pisa_test = Pisa.query.filter_by(id=pk).first()
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
            'pisa_blocks_right': []
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
                'answers': [answer.convert_json() for answer in block_text_answers],
                'options': [option.convert_json() for option in block_text_options]
            }
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
                'answers': [answer.convert_json() for answer in block_text_answers],
                'options': [option.convert_json() for option in block_text_options]
            }
            info['pisa_blocks_right'].append(info_right)

        return jsonify(info)


@app.route(f'{api}/pisa_test_list/<deleted>')
def pisa_test_list(deleted):
    if deleted == 'true':
        pisa_tests = Pisa.query.filter_by(deleted=True).all()
    else:
        pisa_tests = Pisa.query.filter_by(deleted=False).all()
    return jsonify([pisa_test.convert_json() for pisa_test in pisa_tests])
