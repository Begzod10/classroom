from .test_crud import class_test_bp


def register_class_test(app):
    app.register_blueprint(class_test_bp)
