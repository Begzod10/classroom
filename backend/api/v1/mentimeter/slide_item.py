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

    # Determine the next order for this slide
    last_order_item = SlideItem.query.filter(
        SlideItem.slide_id == data['slide_id']
    ).order_by(SlideItem.order.desc()).first()

    order = 0 if last_order_item is None else last_order_item.order + 1

    # Create SlideItem with default structure if needed
    slide_item = SlideItem(
        slide_id=data['slide_id'],
        slide_type=data.get('slideType'),
        order=order
    )

    db.session.add(slide_item)
    db.session.commit()

    return jsonify(slide_item.convert_json()), 200


@slide_item_bp.route('/update/<int:pk>', methods=['PUT'])
@swag_from({'tags': ['Slide Item'], "methods": ["PUT"]})
@jwt_required()
def update_slide_item(pk):
    data = request.get_json()
    slide_item = SlideItem.query.filter(SlideItem.id == pk).first()

    if not slide_item:
        return {"error": "SlideItem not found"}, 404

    # Update simple fields if provided, else keep existing
    slide_item.heading = data.get('heading', slide_item.heading)
    slide_item.subheading = data.get('subheading', slide_item.subheading)
    slide_item.slide_id = data.get('slide_id', slide_item.slide_id)
    slide_item.slide_type = data.get('slideType', slide_item.slide_type_id)
    slide_item.image = data.get('image', slide_item.image)
    slide_item.video = data.get('video', slide_item.video)
    slide_item.image_type = data.get('imageType', slide_item.image_type)
    slide_item.label = data.get('label', slide_item.label)

    # Update nested JSON fields safely
    slide_item.design = data.get('design', slide_item.design)
    slide_item.extra_design = data.get('extraDesign', slide_item.extra_design)
    db.session.commit()

    return slide_item.convert_json(), 200


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


@slide_item_bp.route('/get/', defaults={'pk': None}, methods=['GET'])
@slide_item_bp.route('/get/<pk>/', methods=['GET'])
@swag_from({'tags': ['Slide Item'], "methods": ["GET"]})
@jwt_required()
def get_slide_item(pk):
    slide_item = SlideItem.query.filter(SlideItem.id == pk).first()
    return slide_item.convert_json()


@slide_item_bp.route('/list/', methods=['GET'])
@swag_from({'tags': ['Slide Item'], "methods": ["GET"]})
@jwt_required()
def get_slide_item_list():
    slide_id = request.args.get('slide_id')
    slide_item = SlideItem.query.filter(SlideItem.slide_id == slide_id).all()
    return jsonify([slide_item.convert_json() for slide_item in slide_item])
