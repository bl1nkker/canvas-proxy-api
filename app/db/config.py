from typing import Callable

from pydantic import BaseModel
from typing_extensions import Protocol

from utils import generate_get_config_method


class DbConfig(BaseModel):
    host: str
    port: int

    postgres_db_user: str
    postgres_db_pass: str
    postgres_db_name: str

    app_db_user: str
    app_db_pass: str
    app_db_name: str

    def postgres_url(self, for_app_db: bool = False):
        return f"postgresql://{self.postgres_db_user}:{self.postgres_db_pass}@{self.host}:{self.port}{f'/{self.app_db_name}' if for_app_db else ''}"

    def app_url(self):
        return f"postgresql://{self.app_db_user}:{self.app_db_pass}@{self.host}:{self.port}/{self.app_db_name}"


def _get_config(_get_value: Callable[[str], str], is_test: bool) -> dict:
    prefix = "DB_TEST" if is_test else "DB"

    return dict(
        host=_get_value("DB_HOST"),
        port=_get_value("DB_PORT"),
        postgres_db_user=_get_value("DB_POSTGRES_USER"),
        postgres_db_pass=_get_value("DB_POSTGRES_PASS"),
        postgres_db_name="postgres",
        app_db_user=_get_value(f"{prefix}_USER"),
        app_db_pass=_get_value(f"{prefix}_PASS"),
        app_db_name=_get_value(f"{prefix}_NAME"),
    )


class GetDbConfigCallable(Protocol):
    def __call__(self, file: str = "app.yaml", **defaults) -> DbConfig: ...


get_db_config: GetDbConfigCallable = generate_get_config_method(DbConfig, _get_config)
