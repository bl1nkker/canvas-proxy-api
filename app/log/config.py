from typing import Callable

from pydantic.main import BaseModel
from typing_extensions import Literal, Protocol

from utils import generate_get_config_method


class LogConfig(BaseModel):
    level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]


def _get_config(_get_value: Callable[[str], str], is_test: bool) -> dict:
    return dict(level=_get_value("LOG_LEVEL"))


class GetLogConfigCallable(Protocol):
    def __call__(self, yaml_file: str = "app.yaml", **defaults) -> LogConfig: ...


get_log_config: GetLogConfigCallable = generate_get_config_method(
    LogConfig, _get_config
)
