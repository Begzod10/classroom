#!/venv python3
# -*- coding: utf-8 -*-
# The above encoding declaration is required and the file must be saved as UTF-8
from flask import request, jsonify, Flask, current_app

from flask_cors import CORS, cross_origin
from pprint import pprint
from werkzeug.utils import secure_filename, send_from_directory
import os
import json
from flask_jwt_extended import JWTManager, create_refresh_token, get_jwt_identity, create_access_token, \
    unset_jwt_cookies, jwt_required
from flask_admin import Admin
from backend.extentions import celery_init_app
from dotenv import load_dotenv
from backend.extentions import db, migrate, jwt, api, cors, admin
from backend.pisa.api.views import register_pisa_views
from backend.teacher.views import register_create_teacher

from backend.create_basics.views import register_create_basics
from flasgger import Swagger
from backend.parent.views import register_parent_views
from backend.mobile.parent.urls import register_mobile_parent_views
from backend.basics.views import register_views
from backend.student.views import register_student_routes
from backend.user.views import register_user_view
from backend.group.views import register_create_group
from backend.models.views import UserAdmin, SubjectAdmin, RoleAdmin

load_dotenv()


def create_app():
    app = Flask(
        __name__,
        static_folder="frontend/build",
        static_url_path="/"
    )

    app.config.from_object('backend.models.config')

    app.config['SWAGGER'] = {
        'uiversion': 3,
        'parse': False,
        'exclude_methods': []
    }

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    admin.init_app(app)

    Swagger(app, parse=False)

    api_prefix = '/api'

    register_views(api_prefix, app)
    register_pisa_views(api_prefix, app)
    register_create_basics(api_prefix, app)
    register_parent_views(api_prefix, app)
    register_mobile_parent_views(api_prefix, app)
    register_student_routes(api_prefix, app)
    register_create_teacher(api_prefix, app)
    register_user_view(api_prefix, app)
    register_create_group(api_prefix, app)

    app.config.from_mapping(
        CELERY=dict(
            broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/2'),
            result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2'),
            task_ignore_result=True,
        ),
    )
    return app


app = create_app()


@app.route('/flask_static/<path:filename>')
def flask_admin_static(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    app.run()
