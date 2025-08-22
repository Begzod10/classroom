from .slide_type import slide_type_bp
from .slide import slide_bp
from .slide_item import slide_item_bp


def register_mentimeter_views(api, app):
    app.register_blueprint(slide_type_bp, url_prefix=f"{api}/v1/mentimeter/slide_type")
    app.register_blueprint(slide_bp, url_prefix=f"{api}/v1/mentimeter/slide")
    app.register_blueprint(slide_item_bp, url_prefix=f"{api}/v1/mentimeter/slide_item")
