from importlib import import_module

from src.models.assignment import Assignment
from src.models.assignment_group import AssignmentGroup
from src.models.attendance import Attendance
from src.models.canvas_course import CanvasCourse
from src.models.canvas_user import CanvasUser
from src.models.enrollment import Enrollment
from src.models.file_record import FileRecord
from src.models.recognition_history import RecognitionHistory
from src.models.student import Student
from src.models.student_vector import StudentVector
from src.models.user import User

metadata = import_module("src.models.base").Base.metadata
