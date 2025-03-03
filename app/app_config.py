from typing import Callable

from pydantic import BaseModel
from typing_extensions import Protocol

from utils import generate_get_config_method


class AppConfig(BaseModel):
    canvas_domain: str
    encryption_key: str


def _get_config(get_value: Callable[[str], str], is_test: bool) -> dict:
    return dict(
        canvas_domain=get_value("CANVAS_DOMAIN"),
        encryption_key=get_value("ENCRYPTION_KEY"),
    )


class GetAppConfigCallable(Protocol):
    def __call__(self, yaml_file: str = "app.yaml", **defaults) -> AppConfig: ...


get_app_config: GetAppConfigCallable = generate_get_config_method(
    AppConfig, _get_config
)
