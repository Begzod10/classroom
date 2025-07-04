from app import app
from backend.extentions import celery_init_app

celery = celery_init_app(app.app)

if __name__ == '__main__':
    celery.start()
