from backend.mobile.parent.views import get_mobile_parent_bp


def register_mobile_parent_views(api, app):
    app.register_blueprint(get_mobile_parent_bp, url_prefix=f"/{api}/mobile/parent")
