from .lesson import student_lesson_bp
# from .platform.crud import *
# from .platform.attendance_per_month import *
# from .platform.payment import *


def register_student_routes(api, app):
    app.register_blueprint(student_lesson_bp, url_prefix=f"{api}/student/")
