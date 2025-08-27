from backend.apps.mentimeter.models import Slide
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from flasgger import swag_from

from app import db
from flask import Blueprint, jsonify
from backend.models.basic_model import Subject, User
from pprint import pprint

slide_bp = Blueprint('slide', __name__)


@slide_bp.route('/create', methods=['POST'])
@swag_from({'tags': ['Slide'], "methods": ["POST"]})
@jwt_required()
def create_slide():
    data = request.get_json()
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    order = Slide.query.filter(Slide.subject_id == data['subject_id'], Slide.user_id == user.id).order_by(
        Slide.order.desc()).first()
    if order is None:
        order = 0
    else:
        order = order.order + 1
    level = data['level_id'] if data['level_id'] != 'no' else None
    slide = Slide(name=data['name'], subject_id=data['subject_id'], user_id=user.id, order=order, level_id=level)
    db.session.add(slide)
    db.session.commit()
    return jsonify({"data": slide.convert_json(), "msg": "Slide created"})


@slide_bp.route('/update/<pk>/', methods=['PUT'])
@swag_from({'tags': ['Slide'], "methods": ["PUT"]})
@jwt_required()
def update_slide(pk):
    data = request.get_json()
    slide = Slide.query.filter(Slide.id == pk).first()
    slide.name = data['name']
    slide.subject_id = data['subject_id']
    level = data['level_id'] if data['level_id'] != 'no' else None
    if level is not None:
        slide.level_id = level
    db.session.commit()
    return jsonify({"data": slide.convert_json()})


@slide_bp.route('/delete/<pk>/', methods=['DELETE'])
@swag_from({'tags': ['Slide'], "methods": ["DELETE"]})
@jwt_required()
def delete_slide(pk):
    slide = Slide.query.filter(Slide.id == pk).first()
    slide.deleted = True
    other_slides = Slide.query.filter(Slide.subject_id == slide.subject_id, Slide.user_id == slide.user_id,
                                      Slide.id != slide.id, Slide.order > slide.order, Slide.deleted == False).order_by(
        Slide.order).all()
    for other_slide in other_slides:
        other_slide.order -= 1

    db.session.commit()
    return jsonify({"data": slide.convert_json(), "msg": "Slide deleted"})


@slide_bp.route('/get/', defaults={'pk': None}, methods=['GET'])
@slide_bp.route('/get/<pk>/', methods=['GET'])
@swag_from({'tags': ['Slide'], "methods": ["GET"]})
@jwt_required()
def get_slide(pk):
    deleted = request.args.get('deleted')
    user = User.query.filter(User.classroom_user_id == get_jwt_identity()).first()
    if pk is not None:
        slide = Slide.query.filter(Slide.id == pk).first()
        return slide.convert_json()
    query = Slide.query
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    search = request.args.get('search', '').strip()
    subject_id = request.args.get('subject_id', '').strip()
    level_id = request.args.get('level_id', '').strip()
    if level_id and level_id != 'all':
        query = query.filter(Slide.level_id == level_id)
    if subject_id and subject_id != 'all':
        query = query.filter(Slide.subject_id == subject_id)
    if search:
        query = query.filter(Slide.name.ilike(f"%{search}%"))
    if deleted is not None:
        query = query.filter(Slide.deleted == deleted, Slide.user_id == user.id)
    else:
        query = query.filter(Slide.user_id == user.id)
    pagination = query.order_by(Slide.order).filter(Slide.deleted == False).paginate(page=page, per_page=per_page,
                                                                                     error_out=False)
    return jsonify({
        'data': [slide.convert_json() for slide in pagination.items],
        'total': pagination.total,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })
