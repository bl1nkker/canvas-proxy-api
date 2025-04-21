import logging

import redis
import structlog
from asgi_correlation_id import correlation_id

from celery_app.celery_config import celery_app


class BaseQueueService:
    def __init__(self, redis_client: redis.Redis, app=celery_app):
        self._log: logging.Logger = structlog.getLogger(__name__)
        self._redis_client = redis_client
        self._celery_app = app

    def queue(self, args: dict, task_name: str, **kwargs) -> str:
        meta = dict(args=args)

        http_request_id = correlation_id.get()
        if http_request_id is not None:
            meta["http_request_id"] = http_request_id

        kwargs["meta"] = meta

        job = self._celery_app.send_task(task_name, args=[meta], **kwargs)
        return job.id
