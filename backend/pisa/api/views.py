from .pisa_test import crud_test_pisa_bp
from .pisa_block import pisa_block_bp
from .student import pisa_student_bp


def register_pisa_views(api, app):
    app.register_blueprint(crud_test_pisa_bp, url_prefix=f"{api}/pisa")
    app.register_blueprint(pisa_block_bp, url_prefix=f"{api}/pisa/block")
    app.register_blueprint(pisa_student_bp, url_prefix=f"{api}/pisa/student")
