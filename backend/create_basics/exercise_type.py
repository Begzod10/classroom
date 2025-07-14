from app import request, jsonify, db
from backend.models.settings import iterate_models
from backend.models.basic_model import ExerciseTypes
from backend.basics.settings import create_msg, del_msg, edit_msg
from flask import Blueprint

exercise_type_bp = Blueprint('exercise_type_folder', __name__)


@exercise_type_bp.route(f'/crud/', defaults={'pk': None}, methods=['POST', 'PUT', 'GET', 'DELETE'])
@exercise_type_bp.route(f'/crud/<pk>', methods=['POST', 'PUT', 'GET', 'DELETE'])
def crud(pk):
    if request.method == "POST" or request.method == "PUT":
        name = request.get_json()['name']
        type_exe = request.get_json()['type']
        if not pk:
            try:
                add = ExerciseTypes(name=name, type_exercise=type_exe)
                add.add_commit()
                return create_msg(name, status=True, data=add.convert_json())
            except:
                return create_msg(name, status=False)
        else:
            exercise_type = ExerciseTypes.query.filter(ExerciseTypes.id == pk).first()
            try:

                exercise_type.name = name
                exercise_type.type_exercise = type_exe
                db.session.commit()
                return edit_msg(name, True, exercise_type.convert_json())
            except:
                return edit_msg(name, False, exercise_type.convert_json())
    elif request.method == "DELETE":
        exercise_type = ExerciseTypes.query.filter(ExerciseTypes.id == pk).first()
        try:
            exercise_type.disabled = True
            db.session.commit()
            return edit_msg(exercise_type.name, True, exercise_type.convert_json())
        except:
            return edit_msg(exercise_type.name, False, exercise_type.convert_json())
    else:
        exercise_types = ExerciseTypes.query.filter(ExerciseTypes.disabled == False).order_by(ExerciseTypes.id).all()

        return jsonify({
            "data": iterate_models(exercise_types, "exercise_types")
        })
