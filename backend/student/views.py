from .lesson import student_lesson_bp

from .platform.attendance_per_month import attendance_per_month_bp

from .platform.payment import payment_bp



def register_student_routes(api, app):
    app.register_blueprint(student_lesson_bp, url_prefix=f"{api}/student/")
    app.register_blueprint(attendance_per_month_bp, url_prefix=f"{api}/student/")
    app.register_blueprint(payment_bp, url_prefix=f"{api}/student/")
