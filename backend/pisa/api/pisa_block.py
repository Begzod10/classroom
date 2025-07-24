import pprint

from app import current_app, db, api, request, jsonify
from backend.models.basic_model import PisaBlockText, PisaBlockTextAnswer, PisaBlockQuestionOptions, PisaFileType, desc
import os
from werkzeug.utils import secure_filename
from backend.basics.settings import img_url, img_folder, file_url, file_folder
import json
from flask import Blueprint
from backend.models.settings import iterate_models
from flasgger import swag_from
from .utils import remove_file, generate_unique_filename, ensure_dir_exists

pisa_block_bp = Blueprint("block", __name__)


@pisa_block_bp.route(f'/text/', defaults={'pk': None}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@pisa_block_bp.route(f'/text/<pk>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@swag_from({
    'tags': ['Pisa Text Blocks'],
    "methods": ["GET", "POST", "PUT", "DELETE"]
})
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


@pisa_block_bp.route('/questions/', defaults={'pk': None}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@pisa_block_bp.route('/questions/<pk>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def pisa_block_questions(pk):
    if request.method in ["POST", "PUT"]:
        info = request.form.get('info')
        info_json = json.loads(info) if info else request.get_json()
        if not info_json:
            return jsonify({"msg": "Ma'lumotlar topilmadi", "success": False}), 400
        load_json = info_json

        pisa_id = load_json['pisaId']
        img = request.files.get('img')
        file_id = None
        upload_folder = img_folder()
        current_app.config['UPLOAD_FOLDER'] = upload_folder

        if img:
            filename = generate_unique_filename(img.filename)
            url = img_url() + "/" + filename
            img.save(os.path.join(upload_folder, filename))
            file = PisaFileType(url=url, file_type='image')
            file.add()
            file_id = file.id

        index = load_json.get('index', 1)
        position = load_json['side']
        text = load_json.get('text')
        type_block = load_json['type']
        completed = load_json.get('completed', False)
        innerType = load_json.get('innerType')
        editorState = load_json.get('editorState')
        variants = load_json.get('variants', {})

        if request.method == "POST":
            exist = PisaBlockText.query.filter_by(pisa_id=pisa_id, position=position).order_by(
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
                editorState=editorState,
                typeVariants=variants.get('typeVariants'),
                type_question=variants.get('type')
            )
            pisa_block.add()

        else:  # PUT
            pisa_block = PisaBlockText.query.filter_by(id=pk).first()
            if not pisa_block:
                return jsonify({"msg": "Pisa topilmadi", "success": False}), 404
            if pisa_block.file_id and file_id:
                remove_file(pisa_block.file_id, PisaFileType)
                pisa_block.file_id = file_id

            pisa_block.pisa_id = pisa_id
            pisa_block.index = index
            pisa_block.position = position
            pisa_block.text = text
            pisa_block.type_block = type_block
            pisa_block.completed = completed
            pisa_block.editorState = editorState
            pisa_block.innerType = innerType
            pisa_block.typeVariants = variants.get('typeVariants')
            pisa_block.type_question = variants.get('type')
            db.session.commit()

            # Update options
            old_options = {opt.index: opt for opt in
                           PisaBlockQuestionOptions.query.filter_by(pisa_block_id=pisa_block.id).all()}
            new_options = {opt['index']: opt for opt in variants.get('options', [])}

            for idx, old_opt in old_options.items():
                if idx not in new_options:
                    remove_file(old_opt.file_id, PisaFileType)
                    old_opt.delete()

            for idx, new_opt in new_options.items():
                image = request.files.get(f'img-index-{idx}')
                file = None
                if image:
                    filename = generate_unique_filename(image.filename)
                    url = img_url() + "/" + filename
                    image.save(os.path.join(upload_folder, filename))
                    file = PisaFileType(url=url, file_type='image')
                    file.add()

                if idx in old_options:
                    opt = old_options[idx]
                    if image and file:
                        remove_file(opt.file_id, PisaFileType)
                        opt.file_id = file.id
                    opt.text = new_opt.get('text', '')
                    opt.innerType = new_opt.get('innerType')
                    opt.isTrue = new_opt.get('isTrue', False)
                    db.session.commit()
                else:
                    PisaBlockQuestionOptions(
                        index=idx,
                        text=new_opt.get('text', ''),
                        pisa_block_id=pisa_block.id,
                        innerType=new_opt.get('innerType'),
                        isTrue=new_opt.get('isTrue', False),
                        file_id=file.id if file else None
                    ).add()

        # POST: create options
        if request.method == "POST" and 'options' in variants:
            for idx, option in enumerate(variants['options']):
                image = request.files.get(f'img-index-{idx}')
                file = None
                if image:
                    filename = generate_unique_filename(image.filename)
                    url = img_url() + "/" + filename
                    image.save(os.path.join(upload_folder, filename))
                    file = PisaFileType(url=url, file_type='image')
                    file.add()

                PisaBlockQuestionOptions(
                    index=idx,
                    text=option.get('text', ''),
                    pisa_block_id=pisa_block.id,
                    innerType=option.get('innerType'),
                    isTrue=option.get('isTrue', False),
                    file_id=file.id if file else None
                ).add()

        # Optional answer
        if 'answer' in variants:
            PisaBlockQuestionOptions(
                answer=variants['answer'],
                pisa_block_id=pisa_block.id
            ).add()

        msg = "pisa muvaffaqiyatli qo'shildi" if request.method == "POST" else "pisa muvaffaqiyatli o'zgartirildi"
        return jsonify({"msg": msg, "success": True, 'id': pisa_block.id})

    elif request.method == "DELETE":
        pisa_block = PisaBlockText.query.filter_by(id=pk).first()
        if not pisa_block:
            return jsonify({"msg": "Pisa topilmadi", "success": False}), 404

        options = PisaBlockQuestionOptions.query.filter_by(pisa_block_id=pisa_block.id).all()
        for option in options:
            remove_file(option.file_id, PisaFileType)
            option.delete()

        if pisa_block.file_id:
            remove_file(pisa_block.file_id, PisaFileType)

        pisa_block.delete()
        return jsonify({"msg": "pisa muvaffaqiyatli o'chirildi", "success": True})

    elif request.method == "GET":
        return jsonify({"msg": "GET hali yozilmagan", "success": False})

    return jsonify({"msg": "ID yuboring", "success": False})


@pisa_block_bp.route(f'/infos', defaults={'pk': None}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@pisa_block_bp.route(f'/infos/<pk>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@swag_from({
    'tags': ['Pisa Info Blocks'],
    "methods": ["GET", "POST", "PUT", "DELETE"]
})
def pisa_block_infos(pk):
    if request.method in ["POST", "PUT"]:
        info = request.form.get('info') if 'info' in request.form else None
        load_json = json.loads(info) if info else request.get_json()
        if not load_json:
            return jsonify({"msg": "Ma'lumotlar topilmadi", "success": False}), 400

        pisa_id = load_json['pisaId']
        index = load_json['index']
        position = load_json['side']
        text = load_json.get('text')
        type_block = load_json['type']
        completed = load_json['completed']
        videoLink = load_json.get('videoLink')
        innerType = load_json.get('innerType')
        file_id = None

        # Handle image
        img = request.files.get('img')
        if img:
            current_app.config['UPLOAD_FOLDER'] = img_folder()
            filename = generate_unique_filename(img.filename)
            url = img_url() + "/" + filename
            img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            file = PisaFileType(url=url, file_type='image')
            file.add()
            file_id = file.id

        # Handle file
        file_get = request.files.get('file')
        file_id = None
        if file_get:
            current_app.config['UPLOAD_FOLDER'] = file_folder()
            ensure_dir_exists(current_app.config['UPLOAD_FOLDER'])

            filename = generate_unique_filename(file_get.filename)
            url = file_url() + "/" + filename
            file_get.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

            file = PisaFileType(url=url, file_type='file')
            file.add()
            file_id = file.id

        if request.method == "POST":
            exist = PisaBlockText.query.filter_by(pisa_id=pisa_id, position=position).order_by(
                desc(PisaBlockText.id)).first()
            index = exist.index + 1 if exist else 1
            pisa_block = PisaBlockText(
                pisa_id=pisa_id,
                index=index,
                position=position,
                text=text,
                type_block=type_block,
                file_id=file_id,
                innerType=innerType,
                completed=completed,
                video_url=videoLink
            )
            pisa_block.add()

        else:  # PUT
            pisa_block = PisaBlockText.query.filter_by(id=pk).first()
            if not pisa_block:
                return jsonify({"msg": "Pisa topilmadi", "success": False}), 404

            # Safe replace old file if a new one is uploaded
            if file_id and pisa_block.file_id:
                remove_file(pisa_block.file_id, PisaFileType)

            pisa_block.pisa_id = pisa_id
            pisa_block.index = index
            pisa_block.position = position
            pisa_block.text = text
            pisa_block.type_block = type_block
            pisa_block.completed = completed
            pisa_block.video_url = videoLink
            pisa_block.file_id = file_id or pisa_block.file_id
            pisa_block.innerType = innerType
            db.session.commit()

        msg = "pisa muvaffaqiyatli yaratildi" if request.method == "POST" else "pisa muvaffaqiyatli o'zgartirildi"
        return jsonify({
            "msg": msg,
            "success": True,
            'id': pisa_block.id,
            'pisa_test_id': pisa_block.pisa_id
        })

    elif request.method == "DELETE":
        pisa_block = PisaBlockText.query.filter_by(id=pk).first()
        if not pisa_block:
            return jsonify({"msg": "Pisa topilmadi", "success": False}), 404

        if pisa_block.file_id:
            remove_file(pisa_block.file_id, PisaFileType)

        pisa_block.delete()
        return jsonify({"msg": "pisa muvaffaqiyatli o'chirildi", "success": True})

    elif request.method == "GET":
        pisa_block = PisaBlockText.query.filter_by(id=pk).first()
        if not pisa_block:
            return jsonify({"msg": "Pisa topilmadi", "success": False}), 404
        return jsonify(pisa_block.convert_json())
