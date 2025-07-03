import pprint

from app import current_app, db, api, request, jsonify
from backend.models.basic_model import PisaBlockText, PisaBlockTextAnswer, PisaBlockQuestionOptions, PisaFileType, desc
import os
from werkzeug.utils import secure_filename
from backend.basics.settings import img_url, img_folder, file_url, file_folder
import json
from flask import Blueprint
from backend.models.settings import iterate_models

pisa_block_bp = Blueprint("block", __name__)


# @app.route(f'{api}/pisa_block_text/', defaults={'pk': None}, methods=['GET', 'POST', 'PUT', 'DELETE'])
# @app.route(f'{api}/pisa_block_text/<pk>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@pisa_block_bp.route(f'/text/', defaults={'pk': None}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@pisa_block_bp.route(f'/text/<pk>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def pisa_block_text(pk):
    if request.method == "POST":

        pisa_id = request.get_json()['pisaId']
        index = request.get_json()['index']
        position = request.get_json()['side']
        text = request.get_json()['text']
        type_block = request.get_json()['type']
        completed = request.get_json()['completed']
        words = request.get_json()['words'] if 'words' in request.get_json() else None
        exist = PisaBlockText.query.filter(PisaBlockText.pisa_id == pisa_id,
                                           PisaBlockText.position == position).order_by(
            desc(PisaBlockText.index)).first()
        innerType = request.get_json()['innerType'] if 'innerType' in request.get_json() else None
        index = exist.index + 1 if exist else 1
        pisa_block = PisaBlockText(pisa_id=pisa_id, index=index, innerType=innerType,
                                   position=position, text=text, type_block=type_block,
                                   completed=completed, editorState=request.get_json()['editorState'], words=words)
        pisa_block.add()
        if words is not None:
            for word in words:
                PisaBlockTextAnswer(index=word['index'], text=word['text'][0], statusWord=word['statusWord'],
                                    type=word['type'], wrapped=word['wrapped'], pisa_block_id=pisa_block.id).add()
        return jsonify({"msg": "pisa muvaffaqiyatli yaratildi", "success": True, 'id': pisa_block.id,
                        'pisa_test_id': pisa_block.pisa_id})
    if pk:
        if request.method == "PUT":
            pisa_block = PisaBlockText.query.filter_by(id=pk).first()
            pisa_block.pisa_id = request.get_json()['pisaId']
            pisa_block.index = request.get_json()['index']
            pisa_block.position = request.get_json()['side']
            pisa_block.text = request.get_json()['text']
            pisa_block.type_block = request.get_json()['type']
            pisa_block.completed = request.get_json()['completed']
            pisa_block.editorState = request.get_json()['editorState']
            pisa_block.innerType = request.get_json()['innerType'] if 'innerType' in request.get_json() else None
            pisa_block.words = request.get_json()['words'] if 'words' in request.get_json() else None
            db.session.commit()
            words = request.get_json()['words'] if 'words' in request.get_json() else None
            answers = PisaBlockTextAnswer.query.filter_by(pisa_block_id=pk).all()
            for answer in answers:
                answer.delete()
            if words is not None:
                for word in words:
                    PisaBlockTextAnswer(index=word['index'], text=word['text'][0], statusWord=word['statusWord'],
                                        type=word['type'], wrapped=word['wrapped'], pisa_block_id=pisa_block.id).add()
            return jsonify({"msg": "pisa muvaffaqiyatli o'zgartirildi", "success": True})
        elif request.method == "DELETE":
            pisa_block = PisaBlockText.query.filter_by(id=pk).first()
            pisa_block.delete()
            db.session.commit()
            return jsonify({"msg": "pisa muvaffaqiyatli o'chirildi", "success": True})
        elif request.method == "GET":
            pisa_block = PisaBlockText.query.filter_by(pisa_id=pk).all()
            return jsonify({"data": iterate_models(pisa_block, entire=False)})
    else:
        return jsonify({"msg": "ID yuvor suka", "success": False})


# @app.route(f'{api}/pisa_block_questions/', defaults={'pk': None}, methods=['GET', 'POST', 'PUT', 'DELETE'])
# @app.route(f'{api}/pisa_block_questions/<pk>', methods=['GET', 'POST', 'PUT', 'DELETE'])

@pisa_block_bp.route(f'/questions/', defaults={'pk': None}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@pisa_block_bp.route(f'/questions/<pk>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def pisa_block_questions(pk):
    if request.method == "POST" or request.method == "PUT":
        info = request.form.get('info') if 'info' in request.form else None
        info_json = json.loads(info)
        load_json = info_json if info_json else request.get_json()
        pisa_id = load_json['pisaId']
        img = request.files.get('img')
        file_id = None
        current_app.config['UPLOAD_FOLDER'] = img_folder()

        if img:
            filename = secure_filename(img.filename)
            url = img_url() + "/" + filename
            img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            file = PisaFileType(url=url, file_type='image')
            file.add()
            file_id = file.id
        index = load_json['index']
        position = load_json['side']
        text = load_json['text'] if 'text' in load_json else None
        type_block = load_json['type']
        completed = load_json['completed']
        innerType = load_json['innerType'] if 'innerType' in load_json else None
        if request.method == "POST":
            exist = PisaBlockText.query.filter(PisaBlockText.pisa_id == pisa_id,
                                               PisaBlockText.position == position).order_by(
                desc(PisaBlockText.id)).first()
            index = exist.index + 1 if exist else 1
            pisa_block = PisaBlockText(
                pisa_id=pisa_id,
                index=index,
                position=position,
                text=text,
                file_id=file_id,
                type_block=type_block,
                innerType=innerType,
                completed=completed,
                editorState=load_json['editorState'] if 'editorState' in load_json else None,
                typeVariants=load_json['variants']['typeVariants'],
                type_question=load_json['variants']['type']
            )
            pisa_block.add()

        else:
            pisa_block = PisaBlockText.query.filter_by(id=pk).first()
            pisa_block.pisa_id = pisa_id
            pisa_block.index = index
            pisa_block.position = position
            pisa_block.text = text
            pisa_block.file_id = file_id
            pisa_block.type_block = type_block
            pisa_block.completed = completed
            pisa_block.editorState = load_json['editorState'] if 'editorState' in load_json else None
            pisa_block.typeVariants = load_json['variants']['typeVariants']
            pisa_block.type_question = load_json['variants']['type']
            pisa_block.innerType = innerType
            db.session.commit()
            options = PisaBlockQuestionOptions.query.filter_by(pisa_block_id=pisa_block.id).all()
            for option in options:
                option.delete()
        if 'options' in load_json['variants']:
            for index, option in enumerate(load_json['variants']['options']):
                image = request.files.get(f'img-index-{index}')
                if image:
                    filename = secure_filename(image.filename)
                    url = img_url() + "/" + filename
                    image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    file = PisaFileType(url=url, file_type='image')
                    file.add()
                    PisaBlockQuestionOptions(
                        index=index,  # Auto-generated index (0, 1, 2...)
                        text=option['text'],
                        pisa_block_id=pisa_block.id,
                        innerType=option['innerType'],
                        isTrue=option['isTrue'],
                        file_id=file.id
                    ).add()
                else:
                    PisaBlockQuestionOptions(
                        index=index,
                        text=option['text'],
                        pisa_block_id=pisa_block.id,
                        innerType=option['innerType'],
                        isTrue=option['isTrue']
                    ).add()
        if 'answer' in load_json['variants']:
            PisaBlockQuestionOptions(answer=load_json['variants']['answer'], pisa_block_id=pisa_block.id).add()
        if request.method == "POST":
            return jsonify({"msg": "pisa muvaffaqiyatli qo'shildi", "success": True, 'id': pisa_block.id})
        elif request.method == "PUT":
            return jsonify({"msg": "pisa muvaffaqiyatli o'zgartirildi", "success": True, 'id': pisa_block.id})
    elif request.method == "DELETE":
        pisa_block = PisaBlockText.query.filter_by(id=pk).first()
        options = PisaBlockQuestionOptions.query.filter_by(pisa_block_id=pisa_block.id).all()
        for option in options:
            option.delete()
        pisa_block.delete()
        return jsonify({"msg": "pisa muvaffaqiyatli o'chirildi", "success": True})
    elif request.method == "GET":
        pass
    else:
        return jsonify({"msg": "ID yuvor suka", "success": False})


# @app.route(f'{api}/pisa_block_infos', defaults={'pk': None}, methods=['GET', 'POST', 'PUT', 'DELETE'])
# @app.route(f'{api}/pisa_block_infos/<pk>', methods=['GET', 'POST', 'PUT', 'DELETE'])

@pisa_block_bp.route(f'/infos', defaults={'pk': None}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@pisa_block_bp.route(f'/infos/<pk>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def pisa_block_infos(pk):
    if request.method == "POST" or request.method == "PUT":
        info = request.form.get('info') if 'info' in request.form else None
        info_json = json.loads(info)

        load_json = info_json if info_json else request.get_json()
        pisa_id = load_json['pisaId']
        index = load_json['index']
        position = load_json['side']
        text = load_json['text'] if 'text' in load_json else None
        type_block = load_json['type']
        completed = load_json['completed']
        videoLink = load_json['videoLink'] if 'videoLink' in load_json else None
        img = request.files.get('img')
        file_get = request.files.get('file')
        innerType = load_json['innerType'] if 'innerType' in load_json else None
        file_id = None
        if img:
            current_app.config['UPLOAD_FOLDER'] = img_folder()
            filename = secure_filename(img.filename)
            url = img_url() + "/" + filename
            img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            file = PisaFileType(url=url, file_type='image')
            file.add()
            file_id = file.id
        if file_get:
            current_app.config['UPLOAD_FOLDER'] = file_folder()
            filename = secure_filename(file_get.filename)
            url = file_url() + "/" + filename
            file_get.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            file = PisaFileType(url=url, file_type='file')
            file.add()
            file_id = file.id

        if request.method == "POST":
            exist = PisaBlockText.query.filter(PisaBlockText.pisa_id == pisa_id,
                                               PisaBlockText.position == position).order_by(
                desc(PisaBlockText.id)).first()
            index = exist.index + 1 if exist else 1
            pisa_block = PisaBlockText(pisa_id=pisa_id, index=index, position=position, text=text,
                                       type_block=type_block, file_id=file_id, innerType=innerType,
                                       completed=completed, video_url=videoLink)
            pisa_block.add()

        else:
            pisa_block = PisaBlockText.query.filter_by(id=pk).first()
            pisa_block.pisa_id = pisa_id
            pisa_block.index = index
            pisa_block.position = position
            pisa_block.text = text
            pisa_block.type_block = type_block
            pisa_block.completed = completed
            pisa_block.video_url = videoLink
            pisa_block.file_id = file_id
            pisa_block.innerType = innerType
            db.session.commit()
        if request.method == "POST":
            return jsonify({"msg": "pisa muvaffaqiyatli yaratildi", "success": True, 'id': pisa_block.id,
                            'pisa_test_id': pisa_block.pisa_id})
        elif request.method == "PUT":
            return jsonify({"msg": "pisa muvaffaqiyatli o'zgartirildi", "success": True, 'id': pisa_block.id,
                            'pisa_test_id': pisa_block.pisa_id})
    elif request.method == "DELETE":
        pisa_block = PisaBlockText.query.filter_by(id=pk).first()
        pisa_block.delete()
        return jsonify({"msg": "pisa muvaffaqiyatli o'chirildi", "success": True})
    elif request.method == "GET":
        pisa_block = PisaBlockText.query.filter_by(id=pk).first()
        return jsonify(pisa_block.convert_json())
