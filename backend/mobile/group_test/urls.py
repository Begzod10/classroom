from backend.mobile.group_test.views import test_group_bp


def register_mobile_group_views(api, app):
    app.register_blueprint(test_group_bp, url_prefix=f"/{api}/mobile/")
