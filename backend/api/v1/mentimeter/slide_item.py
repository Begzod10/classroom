from flask import Blueprint, request, jsonify
from app import db
from backend.models.basic_model import SlideItem
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

slide_item_bp = Blueprint('slide_item', __name__)


@slide_item_bp.route('/create', methods=['POST'])
@jwt_required()
@swag_from({'tags': ['Slide Item'], "methods": ["POST"]})
def create_slide_item():
    data = request.get_json()
    last_order = SlideItem.query.filter(SlideItem.slide_id == data['slide_id']).order_by(SlideItem.order.desc()).first()
    if last_order is None:
        order = 0
    else:
        order = last_order.order + 1
    slide_item = SlideItem(name=data['name'], slide_id=data['slide_id'], slide_type_id=data['slide_type_id'],
                           order=order)
    db.session.add(slide_item)
    db.session.commit()
    return slide_item.convert_json()


@slide_item_bp.route('/update/<pk>', methods=['PUT'])
@swag_from({'tags': ['Slide Item'], "methods": ["PUT"]})
@jwt_required()
def update_slide_item(pk):
    data = request.get_json()
    slide_item = SlideItem.query.filter(SlideItem.id == pk).first()
    slide_item.name = data['name']
    slide_item.slide_id = data['slide_id']
    slide_item.slide_type_id = data['slide_type_id']
    db.session.commit()
    return slide_item.convert_json()


@slide_item_bp.route('/delete/<pk>', methods=['DELETE'])
@swag_from({'tags': ['Slide Item'], "methods": ["DELETE"]})
@jwt_required()
def delete_slide_item(pk):
    slide_item = SlideItem.query.filter(SlideItem.id == pk).first()
    other_slides = SlideItem.query.filter(SlideItem.slide_id == slide_item.slide_id,
                                          SlideItem.order > slide_item.order).order_by(SlideItem.order).all()
    for other_slide in other_slides:
        other_slide.order -= 1
    slide_item.delete_commit()
    return slide_item.convert_json()


@slide_item_bp.route('/get/', defaults={'pk': None}, methods=['DELETE'])
@slide_item_bp.route('/get/<pk>/', methods=['GET'])
@swag_from({'tags': ['Slide Item'], "methods": ["GET"]})
@jwt_required()
def get_slide_item(pk):
    slide_id = request.args.get('slide_id')
    if pk is not None:
        slide_item = SlideItem.query.filter(SlideItem.id == pk).first()
        return slide_item.convert_json()
    else:
        slide_item = SlideItem.query.filter(SlideItem.slide_id == slide_id).all()
    return jsonify([slide_item.convert_json() for slide_item in slide_item])
