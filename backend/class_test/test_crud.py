import pprint

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required

from backend.models.basic_model import Exercise, ExerciseTypes
from backend.models.settings import iterate_models

class_test_bp = Blueprint('class_test', __name__)


@class_test_bp.route(f'/api/class_tests', methods=['POST', 'GET'])
@jwt_required()
def class_test():
    if request.method == "POST":
        pprint.pprint(request.get_json())
        return jsonify({"success": True})
    class_type = ExerciseTypes.query.filter(ExerciseTypes.name == "Turon").first()
    exercises = Exercise.query.filter(Exercise.type_id == class_type.id).order_by(Exercise.id).all()
    return jsonify({"data": iterate_models(exercises)})
