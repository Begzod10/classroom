from app import request, jsonify
from backend.mobile.tasks.func import get_user_tasks, TaskServiceError, update_task_status, add_comment, \
    get_notifications, get_task_detail, update_notifications
from flask import Blueprint

tasks_mobile = Blueprint('tasks_mobile', __name__)


@tasks_mobile.route("/my-tasks/", methods=["GET"])
def my_tasks():
    print('acasa')
    user_id = request.args.get("user_id")
    status = request.args.get("status")

    try:
        tasks = get_user_tasks(user_id, status)
    except TaskServiceError as e:
        return jsonify({"detail": str(e)}), 502

    return jsonify(tasks), 200


@tasks_mobile.route("/tasks/<int:task_id>/", methods=["GET"])
def mobile_task_detail(task_id):
    data = get_task_detail(task_id)
    return jsonify(data), 200


@tasks_mobile.route("/tasks/<int:task_id>/status/", methods=["PATCH"])
def update_status(task_id):
    status = request.json.get("status")

    try:
        data = update_task_status(task_id, status)
    except TaskServiceError as e:
        return jsonify({"detail": str(e)}), 502

    return jsonify(data), 200


@tasks_mobile.route("/tasks/<int:task_id>/comments/", methods=["POST"])
def mobile_add_comment(task_id):
    user_id = request.args.get("user_id")
    text = request.json.get("text")

    if not text:
        return jsonify({"detail": "text required"}), 400

    try:
        data = add_comment(task_id, text, user_id)
    except TaskServiceError as e:
        return jsonify({"detail": str(e)}), 502

    return jsonify(data), 201


@tasks_mobile.route("/notifications/", methods=["GET"])
def mobile_notifications():
    user_id = request.args.get("user_id")

    try:
        data = get_notifications(user_id)
    except TaskServiceError as e:
        return jsonify({"detail": str(e)}), 502

    return jsonify(data), 200


@tasks_mobile.route("/notifications/<int:id>/", methods=["PATCH"])
def mobile_notifications_update(id):
    try:
        data = update_notifications(id)
    except TaskServiceError as e:
        return jsonify({"detail": str(e)}), 502

    return jsonify(data), 200
