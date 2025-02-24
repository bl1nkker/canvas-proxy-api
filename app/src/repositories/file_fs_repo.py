import io
import os
import json
import uuid
from pathlib import Path
from typing import Optional, Tuple

from utils.custom_mimetypes import mimetypes
from fs_config import get_fs_config


class FileFsRepo:
    @staticmethod
    def get_path_for_file(content_type: Optional[str] = None):
        ext = "" if content_type is None else mimetypes.guess_extension(content_type)

        name = f"{uuid.uuid4()}{ext}"
        fs_config = get_fs_config()
        return os.path.join(fs_config.file_storage_path, name)

    @staticmethod
    def get_file_info(file_name: str) -> Optional[Tuple[str, int]]:
        fs_config = get_fs_config()
        file_path = os.path.join(fs_config.file_storage_path, file_name)
        if not os.path.exists(file_path):
            return

        return file_path, os.path.getsize(file_path)

    def save(
        self, content_type: str, stream: io.BufferedReader, media=None
    ) -> tuple[str, int]:
        fs_config = get_fs_config()
        if not os.path.exists(fs_config.file_storage_path):
            Path(fs_config.file_storage_path).mkdir(parents=True, exist_ok=True)

        file_path = self.get_path_for_file(content_type)
        size = 0

        if media is not None:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(media, file)
                size = file.tell()
        else:
            with open(file_path, "wb") as file:
                while True:
                    chunk = stream.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)
                    size += len(chunk)

        return file_path, size
