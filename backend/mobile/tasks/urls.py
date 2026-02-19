from backend.mobile.parent.views import get_mobile_parent_bp
from backend.mobile.tasks.views import tasks_mobile


def register_mobile_tasks_views(api, app):
    app.register_blueprint(tasks_mobile, url_prefix=f"/{api}/mobile/")
