
from .basic import basic_bp


def register_views(api, app):
    app.register_blueprint(basic_bp, url_prefix=f"{api}/")
