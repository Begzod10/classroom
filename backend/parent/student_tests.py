from flask import Blueprint, jsonify, request
from backend.configs import gennis_server_url
import requests
from backend.models.basic_model import User

parent_students_test_bp = Blueprint('parent_test_get', __name__)


@parent_students_test_bp.route('/students/test/dates/<platform_id>', methods=['GET'])
def get_students_test_dates(platform_id):
    response = requests.get(f"{gennis_server_url}/api/parent/test/dates/{platform_id}",
                            headers={
                                'Content-Type': 'application/json'
                            })
    dates_response = response.json()
    return jsonify(dates_response)


@parent_students_test_bp.route('/students/test/results/<int:platform_id>', methods=['POST'])
def student_tests_results(platform_id):
    data = request.get_json()
    response = requests.post(f"{gennis_server_url}/api/parent/test/results/{platform_id}", json=data)
    return jsonify(response.json())
