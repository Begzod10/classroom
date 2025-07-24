from backend.models.basic_model import ExerciseTypes, SubjectLevel, Subject, Exercise, File, ExerciseAnswers, \
    StudentExercise, ExerciseBlock, ExerciseBlockImages, Component
from app import request, db, jsonify, current_app
from backend.models.settings import iterate_models, delete_list_models
from backend.basics.settings import check_img_remove, del_msg, edit_msg, create_msg, add_file
import json
from pprint import pprint
from flask_jwt_extended import jwt_required
from flask import Blueprint

from flasgger import swag_from

exercise_bp = Blueprint('exercise_folder', __name__)


@exercise_bp.route(f'/crud/', defaults={'pk': None}, methods=['POST', 'PUT', 'GET', 'DELETE'])
@exercise_bp.route(f'/crud/<pk>/', methods=['POST', 'PUT', 'GET', 'DELETE'])
@swag_from({"tags": ["Exercise"]},
           methods=['POST', 'PUT', 'GET', 'DELETE'])
@jwt_required()
def crud(pk):
    if request.method == "POST":
        exercise = Exercise(name='unnamed')
        exercise.add_commit()
        return create_msg('unnamed', status=True, data=exercise.convert_json())
    elif request.method == "PUT":

        get_json = request.get_json()
        random_status = False

        if 'random' in get_json:
            random_status = get_json['random']
        selected_level = get_json['level']
        selected_subject = get_json['subject']
        name = get_json['title']
        exercise_type = get_json['type']
        get_exercise_type = ExerciseTypes.query.filter(ExerciseTypes.id == exercise_type).first()
        get_level = SubjectLevel.query.filter(SubjectLevel.id == selected_level).first()
        get_subject = Subject.query.filter(Subject.id == selected_subject).first()
        exercise = Exercise.query.filter(Exercise.id == pk).first()
        exercise.name = name
        exercise.random_status = random_status
        if get_level:
            exercise.level_id = get_level.id
        if get_exercise_type:
            exercise.type_id = get_exercise_type.id
        if get_subject:
            exercise.subject_id = get_subject.id
        db.session.commit()
        return edit_msg(name, True, exercise.convert_json())
    elif request.method == "GET":
        if pk:
            exercise = Exercise.query.filter(Exercise.id == pk).first()
            return jsonify({
                "data": exercise.convert_json()
            })
        else:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 50))
            search = request.args.get('search', '').strip()
            subject_id = request.args.get('subject', '').strip()
            type_id = request.args.get('type', '').strip()
            level_id = request.args.get('level', '').strip()

            query = Exercise.query
            if search:
                query = query.filter(Exercise.name.ilike(f"%{search}%"))

            if subject_id and subject_id != "all":
                query = query.filter(Exercise.subject_id == subject_id)

            if type_id and type_id != "all":
                query = query.filter(Exercise.type_id == type_id)

            if level_id and level_id != "all":
                query = query.filter(Exercise.level_id == level_id)

            exercises = query.order_by(Exercise.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

            return jsonify({
                "data": iterate_models(exercises.items, entire=True),
                "total": exercises.total,
                "page": exercises.page,
                "pages": exercises.pages,
                "per_page": exercises.per_page,
                "has_next": exercises.has_next,
                "has_prev": exercises.has_prev
            })
    elif request.method == "DELETE":
        exercise = Exercise.query.filter(Exercise.id == pk).first()
        blocks = ExerciseBlock.query.filter(ExerciseBlock.exercise_id == exercise.id).all()
        for block in blocks:
            block_img = ExerciseBlockImages.query.filter(ExerciseBlockImages.block_id == block.id).all()
            for img in block_img:
                check_img_remove(img.img_id, File=File)
                img.delete_commit()
        exercise_answers = ExerciseAnswers.query.filter(ExerciseAnswers.exercise_id == exercise.id).all()
        donelessons = StudentExercise.query.filter(StudentExercise.exercise_id == exercise.id).all()

        delete_list_models(blocks, File, type="double")
        delete_list_models(exercise_answers, File)
        delete_list_models(donelessons, File)
        exercise.delete_commit()
        return del_msg(exercise.name, True)


@exercise_bp.route(f'block/text/editor/', defaults={"pk": None}, methods=['POST', "PUT", "DELETE"])
@exercise_bp.route(f'block/text/editor/<pk>/', methods=['POST', "PUT", "DELETE"])
@jwt_required()
@swag_from({"tags": ["Exercise"],
            "methods": ["POST", "PUT", "DELETE"]})
def block_text_editor(pk):
    if request.method == "POST" or request.method == "PUT":
        exercise = Exercise.query.filter(Exercise.id == request.get_json()['exc_id']).first()
        if request.method == "PUT":
            clone = request.get_json()['editorState']
            text = request.get_json()['text']
            component = Component.query.filter(Component.name == "textEditor").first()
            exercise_block = ExerciseBlock.query.filter(ExerciseBlock.id == pk).first()
            exercise_block.desc = text
            exercise_block.clone = clone
            exercise_block.component_id = component.id
            exercise_block.add_commit()
            return jsonify(exercise_block.convert_json())
        elif request.method == "POST":
            clone = request.get_json()['editorState']
            text = request.get_json()['text']
            component = Component.query.filter(Component.name == "text").first()
            last_block = ExerciseBlock.query.filter(ExerciseBlock.exercise_id == exercise.id).order_by(
                ExerciseBlock.order.desc()).first()
            order = last_block.order + 1 if last_block else 1
            add_exe = ExerciseBlock(desc=text, exercise_id=exercise.id, component_id=component.id, clone=clone,
                                    order=order)
            add_exe.add_commit()
            return jsonify(add_exe.convert_json())
    elif request.method == "DELETE":
        exercise_block = ExerciseBlock.query.filter(ExerciseBlock.id == pk).first()
        exercise_block.delete_commit()
        return del_msg("block", True)


@exercise_bp.route('block/text/', defaults={"pk": None}, methods=['POST', 'PUT', 'DELETE'])
@exercise_bp.route('block/text/<pk>/', methods=['POST', 'PUT', 'DELETE'])
@jwt_required()
@swag_from({"tags": ["Exercise"], "methods": ["POST", "PUT", "DELETE"]})
def block_text(pk):
    method = request.method

    if method in ("POST", "PUT"):
        data = request.get_json()
        exercise = Exercise.query.get(data.get('exc_id'))
        component = Component.query.filter_by(name="text").first()
        text = data.get('text')
        words = data.get('words', [])
        editor_state = data.get('editorState')

        if not exercise or not component:
            return jsonify({"success": False, "msg": "Invalid exercise or component"}), 400

        subject = Subject.query.get(exercise.subject_id)
        level = SubjectLevel.query.get(exercise.level_id)
        exercise_type = ExerciseTypes.query.get(exercise.type_id)

        if not subject or not level or not exercise_type:
            return jsonify({"success": False, "msg": "Invalid subject, level, or type"}), 400

        if method == "PUT":
            exercise_block = ExerciseBlock.query.get(pk)
            if not exercise_block:
                return jsonify({"success": False, "msg": "Exercise block not found"}), 404

            exercise_block.desc = text
            exercise_block.component_id = component.id
            exercise_block.clone = editor_state
            exercise_block.for_words = words
            exercise_block.add_commit()

            # Update or preserve answers
            existing_answers = {a.order: a for a in ExerciseAnswers.query.filter_by(block_id=pk).all()}
            updated_orders = []

            for word in words:
                word_text = word.get('text', [''])[0]
                word_index = word.get('index')

                if word_index in existing_answers:
                    answer = existing_answers[word_index]
                    answer.desc = word_text
                    # Mark as reused
                    updated_orders.append(word_index)
                else:
                    # New answer
                    answer = ExerciseAnswers(
                        exercise_id=exercise.id,
                        block_id=exercise_block.id,
                        desc=word_text,
                        order=word_index,
                        type_id=exercise_type.id,
                        subject_id=subject.id,
                        level_id=level.id
                    )
                    db.session.add(answer)

            # Delete only unused old answers
            for order, old_answer in existing_answers.items():
                if order not in updated_orders:
                    db.session.delete(old_answer)

        else:  # POST
            last_block = ExerciseBlock.query.filter(ExerciseBlock.exercise_id == exercise.id).order_by(
                ExerciseBlock.order.desc()).first()
            order = last_block.order + 1 if last_block else 1
            exercise_block = ExerciseBlock(
                desc=text,
                exercise_id=exercise.id,
                component_id=component.id,
                order=order,
                clone=editor_state,
                for_words=words
            )
            exercise_block.add_commit()

            for word in words:
                answer = ExerciseAnswers(
                    exercise_id=exercise.id,
                    block_id=exercise_block.id,
                    desc=word.get('text', [''])[0],
                    order=word.get('index'),
                    type_id=exercise_type.id,
                    subject_id=subject.id,
                    level_id=level.id
                )
                db.session.add(answer)

        db.session.commit()
        return jsonify(exercise_block.convert_json())

    elif method == "DELETE":
        exercise_block = ExerciseBlock.query.get(pk)
        if not exercise_block:
            return jsonify({"success": False, "msg": "Exercise block not found"}), 404

        answers = ExerciseAnswers.query.filter_by(block_id=pk).all()
        delete_list_models(answers, File)
        exercise_block.delete_commit()
        return del_msg("block", True)


@exercise_bp.route('block/question/', defaults={"pk": None}, methods=['POST', 'PUT', 'DELETE'])
@exercise_bp.route('block/question/<pk>/', methods=['POST', 'PUT', 'DELETE'])
@jwt_required()
def block_question(pk):
    method = request.method

    # === DELETE ===
    if method == "DELETE":
        exercise_block = ExerciseBlock.query.get(pk)
        if not exercise_block:
            return jsonify({"success": False, "msg": "Exercise block not found"}), 404
        answers = ExerciseAnswers.query.filter_by(block_id=pk).all()
        delete_list_models(answers, File)
        if exercise_block.img_info:
            check_img_remove(exercise_block.img_info, File=File)
        exercise_block.delete_commit()
        return del_msg("block", True)

    # === POST or PUT ===
    info = request.form.get('info')
    if not info:
        return jsonify({"success": False, "msg": "Missing 'info' in request"}), 400

    data = json.loads(info)
    exc_id = data.get('exc_id')
    exercise = Exercise.query.get(exc_id)
    if not exercise:
        return jsonify({"success": False, "msg": "Exercise not found"}), 404

    text = data.get('text')
    clone = data.get('clone')
    inner_type = data.get('innerType')
    component = Component.query.filter_by(name="question").first()
    if not component:
        return jsonify({"success": False, "msg": "Component not found"}), 404

    subject = Subject.query.get(exercise.subject_id)
    level = SubjectLevel.query.get(exercise.level_id)
    exercise_type = ExerciseTypes.query.get(exercise.type_id)

    img_info = None
    if 'img' in request.files:
        img_info = add_file(request.files['img'], type_file="img", app=current_app, File=File)

    if method == "POST":
        last_block = ExerciseBlock.query.filter_by(exercise_id=exercise.id).order_by(
            ExerciseBlock.order.desc()).first()
        order = last_block.order + 1 if last_block else 1
        exercise_block = ExerciseBlock(
            desc=text,
            exercise_id=exercise.id,
            component_id=component.id,
            clone=clone,
            img_info=img_info,
            inner_type=inner_type,
            order=order
        )
        exercise_block.add_commit()

    elif method == "PUT":
        exercise_block = ExerciseBlock.query.get(pk)
        if not exercise_block:
            return jsonify({"success": False, "msg": "Exercise block not found"}), 404

        exercise_block.desc = text
        exercise_block.component_id = component.id
        exercise_block.inner_type = inner_type
        exercise_block.clone = clone
        if img_info:
            # remove previous block image if new one uploaded
            if exercise_block.img_info:
                check_img_remove(exercise_block.img_info, File=File)
            exercise_block.img_info = img_info

        exercise_block.add_commit()
    variant_data = data.get('variants', {})
    variant_type = variant_data.get('type')

    if method == "PUT":
        old_answers = {a.order: a for a in ExerciseAnswers.query.filter_by(block_id=exercise_block.id).all()}
        new_indices = {opt.get('index') for opt in variant_data.get('options', [])}
        for old_index, old_answer in old_answers.items():
            if old_index not in new_indices:
                check_img_remove(old_answer.file_id, File=File)
                db.session.delete(old_answer)

    if variant_type == "select":
        for option in variant_data.get('options', []):
            option_text = option.get('text', '')
            option_index = option.get('index')
            option_true = option.get('isTrue', False)
            option_inner_type = option.get('innerType')
            file_key = f'img-index-{option_index}'

            file_id = None
            type_img = ''

            if option_inner_type != "text" and file_key in request.files:
                # New image uploaded — remove old image if any
                if method == "PUT" and option_index in old_answers and old_answers[option_index].file_id:
                    check_img_remove(old_answers[option_index].file_id, File=File)
                file_id = add_file(request.files[file_key], type_file="img", app=current_app, File=File)
                type_img = "variant_img"
            elif method == "PUT" and option_index in old_answers:
                # Reuse old file_id and type_img
                file_id = old_answers[option_index].file_id
                type_img = old_answers[option_index].type_img

            if method == "PUT" and option_index in old_answers:
                # Update existing answer
                answer = old_answers[option_index]
                answer.desc = option_text
                answer.status = option_true
                answer.file_id = file_id
                answer.type_img = type_img
            else:
                # Create new answer
                answer = ExerciseAnswers(
                    exercise_id=exercise.id,
                    subject_id=subject.id,
                    level_id=level.id,
                    desc=option_text,
                    file_id=file_id,
                    status=option_true,
                    type_id=exercise_type.id if exercise_type else None,
                    order=option_index,
                    type_img=type_img,
                    block_id=exercise_block.id
                )
                db.session.add(answer)

    elif variant_type == "input":
        answer_text = variant_data.get('answer', '')

        if method == "PUT":
            # Delete old answers (assuming only one for input)
            delete_list_models(ExerciseAnswers.query.filter_by(block_id=exercise_block.id).all(), File=File)

        answer = ExerciseAnswers(
            exercise_id=exercise.id,
            subject_id=subject.id,
            level_id=level.id,
            desc=answer_text,
            type_id=exercise_type.id,
            status=True,
            type_img='',
            block_id=exercise_block.id
        )
        db.session.add(answer)

    db.session.commit()
    return jsonify(exercise_block.convert_json())


@exercise_bp.route('block/image/', defaults={"pk": None}, methods=['POST', 'PUT', 'DELETE'])
@exercise_bp.route('block/image/<pk>/', methods=['POST', 'PUT', 'DELETE'])
@swag_from({"tags": ["Exercise"],
            "methods": ["POST", "PUT", "DELETE"]})
def block_image(pk):
    method = request.method
    component = Component.query.filter_by(name="image").first()
    if not component:
        component = Component(name="image")
        db.session.add(component)
    if method in ("POST", "PUT"):
        info = request.form.get('info')
        if not info:
            return jsonify({"success": False, "msg": "Missing 'info' in request"}), 400

        data = json.loads(info)
        exc_id = data.get('exc_id')
        exercise = Exercise.query.get(exc_id)
        if not exercise:
            return jsonify({"success": False, "msg": "Exercise not found"}), 404

        img_info = None
        if 'img' in request.files:
            img_info = add_file(request.files['img'], type_file="img", app=current_app, File=File)
        if request.method == "PUT":
            exercise_block = ExerciseBlock.query.get(pk)
            if not exercise_block:
                return jsonify({"success": False, "msg": "Exercise block not found"}), 404
            exercise_block.img_info = img_info
            exercise_block.add_commit()
        else:
            last_block = ExerciseBlock.query.filter(ExerciseBlock.exercise_id == exercise.id).order_by(
                ExerciseBlock.order.desc()).first()
            order = last_block.order + 1 if last_block else 1
            exercise_block = ExerciseBlock(
                exercise_id=exercise.id,
                img_info=img_info,
                order=order,
                component_id=component.id
            )
            exercise_block.add_commit()
        return jsonify(exercise_block.convert_json())
    elif method == "DELETE":
        exercise_block = ExerciseBlock.query.get(pk)
        if not exercise_block:
            return jsonify({"success": False, "msg": "Exercise block not found"}), 404
        exercise_block.delete_commit()
        return jsonify({"success": True})


@exercise_bp.route('block/audio/', defaults={"pk": None}, methods=['POST', 'PUT', 'DELETE'])
@exercise_bp.route('block/audio/<pk>/', methods=['POST', 'PUT', 'DELETE'])
@swag_from({"tags": ["Exercise"],
            "methods": ["POST", "PUT", "DELETE"]})
def block_audio(pk):
    method = request.method
    component = Component.query.filter_by(name="audio").first()
    if not component:
        component = Component(name="audio")
        db.session.add(component)
    if method in ("POST", "PUT"):

        info = request.form.get('info')
        if not info:
            return jsonify({"success": False, "msg": "Missing 'info' in request"}), 400

        data = json.loads(info)
        exc_id = data.get('exc_id')
        exercise = Exercise.query.get(exc_id)
        if not exercise:
            return jsonify({"success": False, "msg": "Exercise not found"}), 404

        audio_info = None
        if 'audio' in request.files:
            audio_info = add_file(request.files['audio'], type_file="audio", app=current_app, File=File)
        if request.method == "PUT":
            exercise_block = ExerciseBlock.query.get(pk)
            if not exercise_block:
                return jsonify({"success": False, "msg": "Exercise block not found"}), 404
            exercise_block.audio_info = audio_info
            exercise_block.add_commit()
        else:
            last_block = ExerciseBlock.query.filter(ExerciseBlock.exercise_id == exercise.id).order_by(
                ExerciseBlock.order.desc()).first()
            order = last_block.order + 1 if last_block else 1
            exercise_block = ExerciseBlock(
                exercise_id=exercise.id,
                audio_info=audio_info,
                order=order,
                component_id=component.id
            )
            exercise_block.add_commit()
        return jsonify(exercise_block.convert_json())
    elif method == "DELETE":
        exercise_block = ExerciseBlock.query.get(pk)
        if not exercise_block:
            return jsonify({"success": False, "msg": "Exercise block not found"}), 404
        exercise_block.delete_commit()
        return jsonify({"success": True})


@exercise_bp.route('block/code/', defaults={"pk": None}, methods=['POST', 'PUT', 'DELETE'])
@exercise_bp.route('block/code/<pk>/', methods=['POST', 'PUT', 'DELETE'])
@swag_from({"tags": ["Exercise"],
            "methods": ["POST", "PUT", "DELETE"]})
def block_code(pk):
    method = request.method

    if method in ("POST", "PUT"):
        info = request.get_json()

        if not info:
            return jsonify({"success": False, "msg": "Missing 'info' in request"}), 400

        exc_id = info.get('exc_id')
        inner_type = info.get('innerType')
        text = info.get('text')
        component = Component.query.filter_by(name=info.get('type')).first()
        if not component:
            component = Component(name=info.get('type'))
            db.session.add(component)
        exercise = Exercise.query.get(exc_id)
        if not exercise:
            return jsonify({"success": False, "msg": "Exercise not found"}), 404

        if request.method == "PUT":
            exercise_block = ExerciseBlock.query.get(pk)
            if not exercise_block:
                return jsonify({"success": False, "msg": "Exercise block not found"}), 404
            exercise_block.inner_type = inner_type
            exercise_block.desc = text
            exercise_block.add_commit()
        else:
            last_block = ExerciseBlock.query.filter(ExerciseBlock.exercise_id == exercise.id).order_by(
                ExerciseBlock.order.desc()).first()
            order = last_block.order + 1 if last_block else 1
            exercise_block = ExerciseBlock(
                exercise_id=exercise.id,
                inner_type=inner_type,
                desc=text,
                order=order,
                component_id=component.id
            )
            exercise_block.add_commit()
        return jsonify(exercise_block.convert_json())
    elif method == "DELETE":
        exercise_block = ExerciseBlock.query.get(pk)
        if not exercise_block:
            return jsonify({"success": False, "msg": "Exercise block not found"}), 404
        exercise_block.delete_commit()
        return jsonify({"success": True})


@exercise_bp.route('block/order/', defaults={"pk": None}, methods=['POST', 'PUT', 'DELETE'])
@swag_from({"tags": ["Exercise"],
            "methods": ["POST", "PUT", "DELETE"]})
def block_order(pk):
    if request.method == "POST":
        pprint(request.get_json())
