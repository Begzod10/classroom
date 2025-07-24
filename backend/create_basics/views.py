# from .exercise import *


from .subject import subject_bp
from .chapter import chapter_bp
from .level import level_bp
from .lesson import lesson_bp
from .exercise_type import exercise_type_bp
from .exercise import exercise_bp


def register_create_basics(api, app):
    app.register_blueprint(subject_bp, url_prefix=f"{api}/subject")
    app.register_blueprint(chapter_bp, url_prefix=f"{api}/chapter")
    app.register_blueprint(level_bp, url_prefix=f"{api}/level")
    app.register_blueprint(lesson_bp, url_prefix=f"{api}/lesson")
    app.register_blueprint(exercise_type_bp, url_prefix=f"{api}/exercise/type")
    app.register_blueprint(exercise_bp, url_prefix=f"{api}/exercise")
