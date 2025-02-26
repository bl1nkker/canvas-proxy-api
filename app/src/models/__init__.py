from importlib import import_module

from src.models.file_record import FileRecord
from src.models.student import Student
from src.models.student_vector import StudentVector

metadata = getattr(import_module("src.models.base"), "Base").metadata
