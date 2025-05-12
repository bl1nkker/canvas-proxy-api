import shortuuid
import structlog

from src.dto import assignment_dto, canvas_course_dto, student_dto
from src.enums.attendance_status import AttendanceStatus
from src.errors.types import NotFoundError
from src.models.assignment import Assignment
from src.models.assignment_group import AssignmentGroup
from src.models.attendance import Attendance
from src.models.canvas_course import CanvasCourse
from src.models.canvas_user import CanvasUser
from src.models.enrollment import Enrollment
from src.models.student import Student
from src.proxies.canvas_proxy_provider import CanvasProxyProvider
from src.repositories.assignment_group_repo import AssignmentGroupRepo
from src.repositories.assignment_repo import AssignmentRepo
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.canvas_course_repo import CanvasCourseRepo
from src.repositories.canvas_user_repo import CanvasUserRepo
from src.repositories.enrollment_repo import EnrollmentRepo
from src.repositories.student_repo import StudentRepo
from src.repositories.user_repo import UserRepo


class SourceDataLoadService:
    def __init__(
        self,
        user_repo: UserRepo,
        enrollment_repo: EnrollmentRepo,
        student_repo: StudentRepo,
        canvas_user_repo: CanvasUserRepo,
        canvas_course_repo: CanvasCourseRepo,
        assignment_group_repo: AssignmentGroupRepo,
        assignment_repo: AssignmentRepo,
        attendance_repo: AttendanceRepo,
        canvas_proxy_provider_cls=CanvasProxyProvider,
    ):
        self._log = structlog.getLogger(__name__)
        self._user_repo = user_repo
        self._enrollment_repo = enrollment_repo
        self._student_repo = student_repo
        self._canvas_user_repo = canvas_user_repo
        self._canvas_course_repo = canvas_course_repo
        self._assignment_group_repo = assignment_group_repo
        self._assignment_repo = assignment_repo
        self._attendance_repo = attendance_repo
        self._canvas_proxy_provider = canvas_proxy_provider_cls()

    async def load_data_from_canvas(self, user_id: int) -> bool:
        # Get user by id
        with self._canvas_user_repo.session():
            canvas_user = self._canvas_user_repo.get_by_user_id(user_id=user_id)
            if canvas_user is None:
                raise NotFoundError(message=f"_error_msg_user_not_found:{user_id}")
            auth_data = await self._canvas_proxy_provider.get_auth_data(
                username=canvas_user.username, password=canvas_user.password
            )
            canvas_courses: list[canvas_course_dto.Read] = (
                await self._canvas_proxy_provider.get_courses(auth_data)
            )
            for canvas_course in canvas_courses:
                self._log.info(
                    "begin retrieving course data",
                    canvas_course_id=canvas_course.canvas_course_id,
                )
                students, assignments, attendances = await self._load_course_data(
                    canvas_course=canvas_course,
                    canvas_user=canvas_user,
                    auth_data=auth_data,
                )
                self._log.info(
                    "end retrieving course data",
                    canvas_course_id=canvas_course.canvas_course_id,
                    students=len(students),
                    assignments=len(assignments),
                    attendances=len(attendances),
                )
        return True

    async def _load_course_data(self, canvas_course, canvas_user, auth_data):
        students = []
        assignments = []
        attendances = []
        # Load courses from Canvas LMS -> Create Course
        course = self._create_course(
            canvas_course=canvas_course, canvas_user=canvas_user
        )
        canvas_students = await self._canvas_proxy_provider.get_course_students(
            canvas_course_id=course.canvas_course_id, cookies=auth_data
        )

        # For each course: Load students
        for canvas_student in canvas_students:
            # Create Student
            student = self._create_student(canvas_student=canvas_student)
            students.append(student)
            # Create Enrollment
            self._create_enrollment(course=course, student=student)

        # For each course: Load attendance assignment group
        canvas_assignment_group = (
            await self._canvas_proxy_provider.get_attendance_assignment_group(
                cookies=auth_data,
                canvas_course_id=course.canvas_course_id,
            )
        )
        if canvas_assignment_group is not None:
            # Create Attendance assignment group
            assignment_group = self._create_assignment_group(
                canvas_assignment_group=canvas_assignment_group, course=course
            )
            # Load student attendances from Canvas LMS
            canvas_student_attendances = (
                await self._canvas_proxy_provider.get_student_attendances(
                    canvas_course_id=course.canvas_course_id,
                    student_ids=[student.canvas_user_id for student in students],
                    cookies=auth_data,
                )
            )
            # For each of the assignments:
            for canvas_assignment in canvas_assignment_group.assignments:
                # Create Assignment
                assignment = self._create_assignment(
                    canvas_assignment=canvas_assignment,
                    assignment_group=assignment_group,
                )
                assignments.append(assignment)

            # For each canvas student
            for canvas_attendance in canvas_student_attendances:
                student = next(
                    (
                        student
                        for student in students
                        if student.canvas_user_id == canvas_attendance.id
                    ),
                    None,
                )
                if student is None:
                    continue
                # For each student submission
                for submission in canvas_attendance.submissions:
                    assignment = next(
                        (
                            assignment
                            for assignment in assignments
                            if assignment.canvas_assignment_id
                            == submission.assignment_id
                        ),
                        None,
                    )
                    if assignment is None:
                        continue
                    attendance = self._create_attendance(
                        submission=submission,
                        assignment=assignment,
                        student=student,
                    )
                    attendances.append(attendance)
        return students, assignments, attendances

    def _create_course(
        self, canvas_course: canvas_course_dto.Read, canvas_user: CanvasUser
    ) -> CanvasCourse:
        with self._canvas_course_repo.session():
            existing_course = self._canvas_course_repo.get_by_canvas_course_id(
                canvas_course_id=canvas_course.canvas_course_id
            )
            if existing_course is not None:
                return existing_course
            course = CanvasCourse(
                web_id=shortuuid.uuid(),
                long_name=canvas_course.long_name,
                short_name=canvas_course.short_name,
                original_name=canvas_course.original_name,
                course_code=canvas_course.course_code,
                canvas_course_id=canvas_course.canvas_course_id,
                canvas_user_id=canvas_user.id,
            )
            course = self._canvas_course_repo.save_or_update(course)
            return course

    def _create_student(self, canvas_student: student_dto.CanvasRead) -> Student:
        with self._student_repo.session():
            existing_student = self._student_repo.get_by_canvas_user_id(
                canvas_user_id=canvas_student.canvas_user_id
            )
            if existing_student is not None:
                return existing_student
            student = Student(
                web_id=shortuuid.uuid(),
                name=canvas_student.name,
                email=canvas_student.email,
                canvas_user_id=canvas_student.canvas_user_id,
            )
            student = self._student_repo.save_or_update(student)
            return student

    def _create_enrollment(self, student: Student, course: CanvasCourse) -> Enrollment:
        with self._enrollment_repo.session():
            existing_enrollment = self._enrollment_repo.get_by_student_and_course_id(
                student_id=student.id, course_id=course.id
            )
            if existing_enrollment is not None:
                return existing_enrollment
            enrollment = Enrollment(
                student_id=student.id, course_id=course.id, web_id=shortuuid.uuid()
            )
            enrollment = self._enrollment_repo.save_or_update(enrollment)
            return enrollment

    def _create_assignment_group(
        self,
        canvas_assignment_group: assignment_dto.AssignmentGroupCanvas,
        course: CanvasCourse,
    ) -> AssignmentGroup:
        with self._assignment_group_repo.session():
            existing_assignment_group = self._assignment_group_repo.get_by_canvas_assignment_group_id(
                canvas_assignment_group_id=canvas_assignment_group.assignment_group_id
            )
            if existing_assignment_group is not None:
                return existing_assignment_group
            assignment_group = AssignmentGroup(
                web_id=shortuuid.uuid(),
                name=canvas_assignment_group.name,
                group_weight=canvas_assignment_group.group_weight,
                course_id=course.id,
                canvas_assignment_group_id=canvas_assignment_group.assignment_group_id,
            )
            assignment_group = self._assignment_group_repo.save_or_update(
                assignment_group
            )
            return assignment_group

    def _create_assignment(
        self,
        canvas_assignment: assignment_dto.CanvasRead,
        assignment_group: AssignmentGroup,
    ) -> Assignment:
        with self._assignment_repo.session():
            existing_assignment = self._assignment_repo.get_by_canvas_assignment_id(
                canvas_assignment_id=canvas_assignment.canvas_assignment_id
            )
            if existing_assignment is not None:
                return existing_assignment
            assignment = Assignment(
                web_id=shortuuid.uuid(),
                name=canvas_assignment.name,
                assignment_group_id=assignment_group.id,
                canvas_assignment_id=canvas_assignment.canvas_assignment_id,
            )
            assignment = self._assignment_repo.save_or_update(assignment)
            return assignment

    def _create_attendance(
        self,
        submission: student_dto.CanvasSubmission,
        student: Student,
        assignment: Assignment,
    ) -> Attendance:
        with self._attendance_repo.session():
            existing_attendance = (
                self._attendance_repo.get_by_student_and_assignment_id(
                    student_id=student.id, assignment_id=assignment.id
                )
            )
            if existing_attendance is not None:
                # ? Should we syncronize this?
                # existing_attendance.value = submission.value
                # existing_attendance.status = AttendanceStatus.COMPLETED
                # existing_attendance = self._attendance_repo.save_or_update(
                #     existing_attendance
                # )
                return existing_attendance
            attendance = Attendance(
                web_id=shortuuid.uuid(),
                student_id=student.id,
                assignment_id=assignment.id,
                status=AttendanceStatus.COMPLETED,
                value=submission.value,
                failed=False,
            )
            attendance = self._attendance_repo.save_or_update(attendance)
            return attendance
