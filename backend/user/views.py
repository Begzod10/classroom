from .change_info import user_bp


def register_user_view(api, app):
    app.register_blueprint(user_bp, url_prefix=f"{api}/user/")
