from typing import Callable

from pydantic import BaseModel
from typing_extensions import Protocol

from utils import generate_get_config_method, replace_known_dirs


class FsConfig(BaseModel):
    test_data_path: str
    file_storage_path: str


def _get_config(get_value: Callable[[str], str], is_test: bool) -> dict:
    test_data_path = replace_known_dirs(get_value("TEST_DATA_PATH"))
    file_storage_path = replace_known_dirs(
        get_value("FILE_STORAGE_PATH_TEST" if is_test else "FILE_STORAGE_PATH")
    )
    return dict(test_data_path=test_data_path, file_storage_path=file_storage_path)


class GetAppConfigCallable(Protocol):
    def __call__(self, yaml_file: str = "app.yaml", **defaults) -> FsConfig:
        ...


get_fs_config: GetAppConfigCallable = generate_get_config_method(FsConfig, _get_config)
