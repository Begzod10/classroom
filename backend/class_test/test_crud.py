import pprint

from app import app, request, redirect, jsonify, api, jwt_required
from backend.models.basic_model import Exercise, ExerciseTypes
from backend.models.settings import iterate_models, delete_list_models


@app.route(f'{api}/class_tests', methods=['POST', 'GET'])
@jwt_required()
def class_test():
    if request.method == "POST":
        pprint.pprint(request.get_json())
        return jsonify({
            "success": True
        })
    class_type = ExerciseTypes.query.filter(ExerciseTypes.name == "Turon").first()
    exercises = Exercise.query.filter(Exercise.type_id == class_type.id).order_by(Exercise.id).all()
    return jsonify({
        "data": iterate_models(exercises, entire=False)
    })
