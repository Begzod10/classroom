from backend.group.platform.test_group import external_bp
from .group_info import group_bps
from .platform.attendances import attendance_bp
from .platform.crud import group_bp


def register_create_group(api, app):
    app.register_blueprint(group_bp, url_prefix=f"{api}/group")
    app.register_blueprint(group_bps, url_prefix=f"{api}/group")
    app.register_blueprint(external_bp, url_prefix=f"{api}/group")
    app.register_blueprint(attendance_bp, url_prefix=f"{api}/group")
