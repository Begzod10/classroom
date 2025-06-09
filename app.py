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

app = Flask(__name__, static_folder="frontend/build", static_url_path="/")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config.from_object('backend.models.config')
db = db_setup(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
api = '/api'
platform_server = 'https://admin.gennis.uz'
# platform_server = "http://192.168.1.15:5002"
django_server = "https://school.gennis.uz"
# django_server = "http://192.168.1.14:7622"

admin = Admin(
    app,
    name='Gennis',
    template_mode='bootstrap3',
    static_url_path='/flask_static'
)

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
from backend.pisa.api.views import *

from backend.models.views import *


@app.route('/flask_static/<path:filename>')
def flask_admin_static(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    app.run()
