from app import app, jsonify, api, request, or_
from backend.models.basic_model import db, Pisa, PisaBlockText, PisaBlockTextAnswer, PisaBlockQuestionOptions, PisaTest, \
    PisaStudent, PisaFileType, PisaBlockOptionsStudent, PisaBlockTextAnswerStudent, School, create_school, User, \
    PisaStudent, Role
import pprint
from backend.basics.settings import check_exist_classroom_id
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route(f'{api}/pisa_student_list', methods=['GET'])
def pisa_student_list():
    pisa_students = PisaTest.query.order_by(PisaTest.id.desc()).all()

    return jsonify({'pisa_students': [pisa_student.convert_json() for pisa_student in pisa_students]}), 200
