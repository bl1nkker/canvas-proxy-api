from sqlalchemy.engine import create_engine

from routers import face_recognition_router, upload_router, student_router, auth_router

from log import configure_logging
from db.config import get_db_config
from web_application import create_web_application

configure_logging()


def create_app():
    db_config = get_db_config()
    db_engine = create_engine(db_config.app_url(), pool_pre_ping=True)
    app = create_web_application(db_engine=db_engine)
    app.include_router(face_recognition_router.router)
    app.include_router(upload_router.router)
    app.include_router(student_router.router)
    app.include_router(auth_router.router)
    return app


app = create_app()
