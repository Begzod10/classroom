from .lesson_degree import lesson_degree
from .platform.crud import teacher_blueprint
from .platform.lesson_plan import lesson_plan_blueprint
from .platform.observation import observe_blueprint
from .platform.salary import teacher_salary_blueprints


def register_create_teacher(api, app):
    app.register_blueprint(lesson_degree, url_prefix=f"{api}/teacher")
    app.register_blueprint(observe_blueprint, url_prefix=f"{api}/teacher")
    app.register_blueprint(teacher_blueprint, url_prefix=f"{api}/teacher")
    app.register_blueprint(lesson_plan_blueprint, url_prefix=f"{api}/teacher")
    app.register_blueprint(teacher_salary_blueprints, url_prefix=f"{api}/teacher")
