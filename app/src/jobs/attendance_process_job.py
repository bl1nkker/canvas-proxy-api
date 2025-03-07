import asyncio

import structlog

from celery_app.celery_config import celery_app
from db.with_db_session import with_db_session
from src.services.service_factory import service_factory

logger = structlog.getLogger(__name__)


@celery_app.task(name="attendance_process_job")
def attendance_process_job():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_attendances())


@with_db_session
async def process_attendances(db_session):
    attendance_process_service = service_factory().attendance_process_service(
        db_session=db_session
    )
    logger.debug('"attendance_process_job" called')
    await attendance_process_service.process_attendances()
    logger.debug('returning from "attendance_process_job"')
