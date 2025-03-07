from celery import Celery
from celery.schedules import crontab
from sqlalchemy.engine import create_engine

from broker.config import get_broker_config
from db.config import get_db_config
from db.session import Session


def create_celery_app(
    db_engine,
):
    Session.configure(bind=db_engine)

    broker_config = get_broker_config()
    celery_app = Celery(__name__, include=["src.jobs.attendance_process_job"])

    celeryconfig = {}
    celeryconfig["BROKER_TRANSPORT"] = broker_config.transport
    celeryconfig["CELERY_BROKER_URL"] = broker_config.url()
    celeryconfig["BROKER_URL"] = broker_config.url()
    celeryconfig["CELERY_RESULT_BACKEND"] = broker_config.url()

    celery_app.conf.beat_schedule = {
        "run_my_task_every_minute": {
            "task": "attendance_process_job",
            "schedule": crontab(minute="*"),
        },
    }
    celery_app.config_from_object(celeryconfig)
    return celery_app


def create_app():
    db_config = get_db_config()
    db_engine = create_engine(
        db_config.app_url(),
        pool_pre_ping=True,
        pool_timeout=60 * 60,
        pool_recycle=60 * 60,
        pool_size=20,
    )
    app = create_celery_app(db_engine=db_engine)
    return app


celery_app = create_app()
