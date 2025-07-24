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

from backend.create_basics.views import register_create_basics
from flasgger import Swagger
from backend.parent.views import register_parent_views

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
    register_pisa_views(api_prefix, app)
    register_create_basics(api_prefix, app)
    register_parent_views(api_prefix, app)

    return app


app = create_app()

api = '/api'

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
