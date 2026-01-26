from app import cross_origin, db, request, jsonify
from backend.configs import gennis_server_url
import requests


class TaskServiceError(Exception):
    pass


def get_user_tasks(user_id, status=None):
    url = f"{gennis_server_url}/api/mobile/missions/mobile/"

    params = {"user_id": user_id}
    if status:
        params["status"] = status

    try:
        resp = requests.get(
            url,
            params=params, headers={
                'Content-Type': 'application/json'
            }
        )
    except requests.RequestException as e:
        raise TaskServiceError(str(e))

    return resp.json()


def update_task_status(task_id, status):
    url = f"{gennis_server_url}/api/mobile/missions/{task_id}/status/"

    resp = requests.patch(
        url,
        json={"status": status},
        headers={
            'Content-Type': 'application/json'
        }
    )

    return resp.json()


def add_comment(task_id, text, user_id):
    url = f"{gennis_server_url}/api/mobile/missions/{task_id}/comments/"

    params = {"user_id": user_id}
    resp = requests.post(
        url,
        params=params,
        json={"text": text},
        headers={
            'Content-Type': 'application/json'
        }
    )

    return resp.json()


def get_notifications(user_id):
    url = f"{gennis_server_url}/api/mobile/notifications/"

    params = {"user_id": user_id}
    resp = requests.get(url, params=params, headers={
        'Content-Type': 'application/json'
    })

    return resp.json()


def get_task_detail(task_id):
    url = f"{gennis_server_url}/api/missions/missions_detail/{task_id}/"

    resp = requests.get(url, headers={
        'Content-Type': 'application/json'
    }, )

    return resp.json()
