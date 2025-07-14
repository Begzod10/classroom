#!/venv python3
# -*- coding: utf-8 -*-
# The above encoding declaration is required and the file must be saved as UTF-8
from flask import *
from backend.models.basic_model import *
from flask_cors import CORS, cross_origin
from pprint import pprint
from werkzeug.utils import *
import os
import json
from flask_jwt_extended import JWTManager, create_refresh_token, get_jwt_identity, create_access_token, \
    unset_jwt_cookies, jwt_required
from flask_admin import Admin
from backend.extentions import celery_init_app
from dotenv import load_dotenv
from backend.extentions import db, migrate, jwt, api, cors, admin
from backend.pisa.api.views import register_pisa_views
from backend.parent.views import register_parent_views

load_dotenv()


def create_app():
    app = Flask(
        __name__,
        static_folder="frontend/build",  # React build
        static_url_path="/"  # Serve React from root
    )
    app.config.from_object('backend.models.config')
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # api.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    admin.init_app(app)
    app.config.from_mapping(
        CELERY=dict(
            broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/2'),
            result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2'),
            task_ignore_result=True,
        ),
    )
    api = '/api'
    register_pisa_views(api, app)
    register_parent_views(api, app)
    # register_commands(app)
    # register_teacher_views(app)
    return app


app = create_app()

api = '/api'
gennis_server_url = "http://192.168.1.19:5002"
# gennis_server_url = os.getenv('GENNIS_SERVER_URL')

turon_server_url = os.getenv('TURON_SERVER_URL')

# basics
from backend.basics.views import *
# create basics
from backend.create_basics.views import *

# group
from backend.group.views import *

# student
from backend.student.views import *

# user
from backend.user.views import *

# teacher
from backend.teacher.views import *

# class test
from backend.class_test.views import *

# mobile
from backend.mobile.views import *

# pisa
# from backend.pisa.api.views import *

from backend.models.views import *


@app.route('/flask_static/<path:filename>')
def flask_admin_static(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    app.run()
