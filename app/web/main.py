from routers import face_recognition_router

# from log import configure_logging
# from db.config import get_db_config
from web_application import create_web_application

# configure_logging()


def create_app():
    app = create_web_application()
    app.include_router(face_recognition_router.router)
    return app


app = create_app()
