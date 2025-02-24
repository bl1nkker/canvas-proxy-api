import logging.config
from threading import RLock
from typing import Callable

import structlog

from log.config import get_log_config
from utils import with_lock

logging_configured = False
logging_lock = RLock()


@with_lock(lock=logging_lock)
def configure_logging(update_config: Callable[[dict], None] = None, force=False):
    global logging_configured

    if logging_configured and not force:
        return

    config = get_log_config()

    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    logging_config = {
        "version": 1,
        "formatters": {
            "default": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": shared_processors,
            }
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            }
        },
        "root": {
            "handlers": ["default"],
            "level": config.level,
        },
    }
    if update_config is not None:
        update_config(logging_config)
    logging.config.dictConfig(logging_config)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging_configured = True
