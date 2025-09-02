from backend.time_table.get import get_timetable_bp
from backend.time_table.crud import crud_timetable_bp


def register_create_time_table(api, app):
    app.register_blueprint(get_timetable_bp, url_prefix=f"{api}/time_table")
    app.register_blueprint(crud_timetable_bp, url_prefix=f"{api}/time_table")
