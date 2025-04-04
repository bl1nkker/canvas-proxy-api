import os
import shutil
from pathlib import Path

import pytest

from fs_config import FsConfig, get_fs_config
from src.repositories.file_fs_repo import FileFsRepo


class FileFixtures:
    @pytest.fixture
    def fs_config(self) -> FsConfig:
        return get_fs_config()

    @pytest.fixture
    def sample_file(self, fs_config):
        with open(os.path.join(fs_config.test_data_path, "test.csv"), "rb") as file:
            yield file

    @pytest.fixture
    def students_file(self, fs_config):
        with open(
            os.path.join(fs_config.test_data_path, "student-data.xlsx"), "rb"
        ) as file:
            yield file

    @pytest.fixture
    def sample_xlsx_file(self, fs_config):
        with open(os.path.join(fs_config.test_data_path, "test.xlsx"), "rb") as file:
            yield file

    @pytest.fixture
    def file_fs_repo(self):
        return FileFsRepo()

    @pytest.fixture
    def cleanup_files(self, fs_config):
        yield
        if os.path.exists(fs_config.file_storage_path):
            shutil.rmtree(Path(fs_config.file_storage_path))

    @pytest.fixture
    def create_test_dir(self, fs_config):
        if not os.path.exists(fs_config.file_storage_path):
            Path(fs_config.file_storage_path).mkdir(parents=True, exist_ok=True)
        if not os.path.exists(fs_config.test_data_path):
            Path(fs_config.test_data_path).mkdir(parents=True, exist_ok=True)
