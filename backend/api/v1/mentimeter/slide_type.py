from flask import Blueprint, request, jsonify
from app import db
from backend.models.basic_model import SlideType
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

slide_type_bp = Blueprint('slide_type', __name__)


@slide_type_bp.route('/create', methods=['POST'])
@swag_from({'tags': ['Slide Type'], "methods": ["POST"]})
@jwt_required()
def create_slide_type():
    data = request.get_json()
    slide_type = SlideType(name=data['name'])
    db.session.add(slide_type)
    db.session.commit()
    return slide_type.convert_json()


@slide_type_bp.route('/get/', defaults={'pk': None}, methods=['DELETE'])
@slide_type_bp.route('/get/<pk>/', methods=['GET'])
@swag_from({'tags': ['Slide Type'], "methods": ["GET"]})
@jwt_required()
def get_slide_type(pk):
    deleted = request.args.get('deleted')
    if pk is not None:
        slide_type = SlideType.query.filter(SlideType.id == pk).first()
        return slide_type.convert_json()
    if deleted is not None:
        slide_type = SlideType.query.filter(SlideType.deleted == deleted).all()
    else:
        slide_type = SlideType.query.all()
    return jsonify([slide_type.convert_json() for slide_type in slide_type])


@slide_type_bp.route('/update/<pk>', methods=['PUT'])
@swag_from({'tags': ['Slide Type'], "methods": ["PUT"]})
@jwt_required()
def update_slide_type(pk):
    data = request.get_json()
    slide_type = SlideType.query.filter(SlideType.id == pk).first()
    slide_type.name = data['name']
    db.session.commit()
    return slide_type.convert_json()


@slide_type_bp.route('/delete/<pk>', methods=['DELETE'])
@swag_from({'tags': ['Slide Type'], "methods": ["DELETE"]})
@jwt_required()
def delete_slide_type(pk):
    slide_type = SlideType.query.filter(SlideType.id == pk).first()
    slide_type.deleted = True
    db.session.commit()
    return slide_type.convert_json()
