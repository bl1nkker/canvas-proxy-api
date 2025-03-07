from importlib import import_module

from src.models.attendance import Attendance
from src.models.canvas_course import CanvasCourse
from src.models.canvas_user import CanvasUser
from src.models.enrollment import Enrollment
from src.models.file_record import FileRecord
from src.models.student import Student
from src.models.student_vector import StudentVector
from src.models.user import User

metadata = import_module("src.models.base").Base.metadata
