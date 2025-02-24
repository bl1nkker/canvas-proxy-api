from importlib import import_module

from src.models.file_record import FileRecord

metadata = getattr(import_module("src.models.base"), "Base").metadata
