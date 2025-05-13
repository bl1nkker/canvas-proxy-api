from src.repositories.assignment_group_repo import AssignmentGroupRepo
from src.repositories.assignment_repo import AssignmentRepo
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.canvas_course_repo import CanvasCourseRepo
from src.repositories.canvas_user_repo import CanvasUserRepo
from src.repositories.enrollment_repo import EnrollmentRepo
from src.repositories.file_fs_repo import FileFsRepo
from src.repositories.file_record_repo import FileRecordRepo
from src.repositories.recognition_history_repo import RecognitionHistoryRepo
from src.repositories.student_repo import StudentRepo
from src.repositories.student_vector_repo import StudentVectorRepo
from src.repositories.user_repo import UserRepo
from src.services.assignment_service import AssignmentService
from src.services.attendance_process_service import AttendanceProcessService
from src.services.attendance_service import AttendanceService
from src.services.auth_service import AuthService
from src.services.canvas_course_service import CanvasCourseService
from src.services.recognition_history_service import RecognitionHistoryService
from src.services.source_data_load_queue_service import SourceDataLoadQueueService
from src.services.source_data_load_service import SourceDataLoadService
from src.services.student_service import StudentService
from src.services.upload_service import UploadService


class ServiceFactory:

    def canvas_user_repo(self, db_session):
        return CanvasUserRepo(db_session=db_session)

    def canvas_course_repo(self, db_session):
        return CanvasCourseRepo(db_session=db_session)

    def user_repo(self, db_session):
        return UserRepo(db_session=db_session)

    def student_repo(self, db_session):
        return StudentRepo(db_session=db_session)

    def student_vector_repo(self, db_session):
        return StudentVectorRepo(db_session=db_session)

    def attendance_repo(self, db_session):
        return AttendanceRepo(db_session=db_session)

    def assignment_repo(self, db_session):
        return AssignmentRepo(db_session=db_session)

    def assignment_group_repo(self, db_session):
        return AssignmentGroupRepo(db_session=db_session)

    def file_fs_repo(self):
        return FileFsRepo()

    def file_record_repo(self, db_session):
        return FileRecordRepo(db_session=db_session)

    def enrollment_repo(self, db_session):
        return EnrollmentRepo(db_session=db_session)

    def recognition_history_repo(self, db_session):
        return RecognitionHistoryRepo(db_session=db_session)

    def upload_service(self, db_session):
        return UploadService(
            file_record_repo=self.file_record_repo(db_session=db_session),
            file_fs_repo=self.file_fs_repo(),
        )

    def student_service(self, db_session):
        return StudentService(
            student_repo=self.student_repo(db_session=db_session),
            student_vector_repo=self.student_vector_repo(db_session=db_session),
            recognition_history_service=self.recognition_history_service(
                db_session=db_session
            ),
            upload_service=self.upload_service(db_session=db_session),
            canvas_course_repo=self.canvas_course_repo(db_session=db_session),
            enrollment_repo=self.enrollment_repo(db_session=db_session),
        )

    def auth_service(self, db_session, redis_client):
        return AuthService(
            canvas_user_repo=self.canvas_user_repo(db_session),
            user_repo=self.user_repo(db_session),
            source_data_load_queue_service=SourceDataLoadQueueService(
                redis_client=redis_client
            ),
        )

    def canvas_course_service(self, db_session):
        return CanvasCourseService(
            canvas_course_repo=self.canvas_course_repo(db_session),
            canvas_user_repo=self.canvas_user_repo(db_session),
        )

    def attendance_service(self, db_session):
        return AttendanceService(
            assignment_repo=self.assignment_repo(db_session=db_session),
            attendance_repo=self.attendance_repo(db_session=db_session),
            student_repo=self.student_repo(db_session=db_session),
            canvas_course_repo=self.canvas_course_repo(db_session=db_session),
            student_service=self.student_service(db_session=db_session),
        )

    def recognition_history_service(self, db_session):
        return RecognitionHistoryService(
            recognition_history_repo=self.recognition_history_repo(
                db_session=db_session
            )
        )

    def assignment_service(self, db_session):
        return AssignmentService(
            assignment_group_repo=self.assignment_group_repo(db_session=db_session),
            assignment_repo=self.assignment_repo(db_session=db_session),
            canvas_course_repo=self.canvas_course_repo(db_session=db_session),
            attendance_service=self.attendance_service(db_session=db_session),
        )

    def attendance_process_service(self, db_session):
        return AttendanceProcessService(
            attendance_repo=self.attendance_repo(db_session=db_session),
            auth_service=self.auth_service(db_session=db_session),
            canvas_course_repo=self.canvas_course_repo(db_session=db_session),
            student_repo=self.student_repo(db_session=db_session),
        )

    def source_data_load_service(self, db_session):
        return SourceDataLoadService(
            user_repo=self.user_repo(db_session),
            enrollment_repo=self.enrollment_repo(db_session),
            student_repo=self.student_repo(db_session),
            canvas_user_repo=self.canvas_user_repo(db_session),
            canvas_course_repo=self.canvas_course_repo(db_session),
            assignment_group_repo=self.assignment_group_repo(db_session),
            assignment_repo=self.assignment_repo(db_session),
            attendance_repo=self.attendance_repo(db_session),
        )


_service_factory = ServiceFactory()


def service_factory():
    return _service_factory
