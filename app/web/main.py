from sqlalchemy.engine import create_engine

from db.config import get_db_config
from log import configure_logging
from web.routers import (
    admin_router,
    assignment_router,
    attendance_router,
    auth_router,
    canvas_course_router,
    student_router,
    upload_router,
)
from web.web_application import create_web_application

configure_logging()


def create_app():
    db_config = get_db_config()
    db_engine = create_engine(db_config.app_url(), pool_pre_ping=True)
    app = create_web_application(db_engine=db_engine)
    app.include_router(auth_router.router)
    app.include_router(student_router.router)
    app.include_router(canvas_course_router.router)
    app.include_router(attendance_router.router)
    app.include_router(assignment_router.router)
    app.include_router(upload_router.router)
    app.include_router(admin_router.router)
    return app


app = create_app()
