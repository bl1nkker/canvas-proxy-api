from importlib import import_module

from src.models.file_record import FileRecord
from src.models.student import Student
from src.models.student_vector import StudentVector
from src.models.user import User
from src.models.canvas_user import CanvasUser

metadata = getattr(import_module("src.models.base"), "Base").metadata
