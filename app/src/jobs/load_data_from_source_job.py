import asyncio

import structlog

from celery_app.celery_config import celery_app
from db.with_db_session import with_db_session
from src.services.service_factory import service_factory

logger = structlog.getLogger(__name__)


@celery_app.task(name="load_data_from_source_job", bind=True)
def load_data_from_source_job(self, meta: dict, **kwargs):
    logger.debug("*** begin job ***", args=meta["args"])
    args = dict(**meta["args"])
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_load_data(args["user_id"]))
    logger.debug("*** end job ***")


@with_db_session
async def process_load_data(db_session, user_id: int):
    source_data_load_service = service_factory().source_data_load_service(
        db_session=db_session
    )
    result = await source_data_load_service.load_data_from_canvas(user_id=user_id)
    return result
