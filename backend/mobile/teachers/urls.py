from backend.mobile.teachers.views import teacher_salary_mobile_blueprints


def register_mobile_teachers_views(api, app):
    app.register_blueprint(teacher_salary_mobile_blueprints, url_prefix=f"/{api}/mobile/")
