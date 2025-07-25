import io
from timeit import default_timer as timer

import numpy as np
import pandas as pd
import shortuuid

from db.data_repo import Pagination
from ml.service import MlService, RepresentResult
from src.dto import enrollment_dto, recognition_history_dto, student_dto
from src.errors.types import InvalidDataError, NotFoundError
from src.errors.utils import write_to_temp_file
from src.models.enrollment import Enrollment
from src.models.student import Student
from src.models.student_vector import StudentVector
from src.proxies.canvas_proxy_provider import CanvasProxyProvider
from src.repositories.canvas_course_repo import CanvasCourseRepo
from src.repositories.enrollment_repo import EnrollmentRepo
from src.repositories.student_repo import StudentRepo
from src.repositories.student_vector_repo import StudentVectorRepo
from src.services.recognition_history_service import RecognitionHistoryService
from src.services.upload_service import UploadService


class StudentService:

    def __init__(
        self,
        student_repo: StudentRepo,
        enrollment_repo: EnrollmentRepo,
        canvas_course_repo: CanvasCourseRepo,
        student_vector_repo: StudentVectorRepo,
        upload_service: UploadService,
        recognition_history_service: RecognitionHistoryService,
        canvas_proxy_provider=CanvasProxyProvider,
        ml_service=MlService,
    ):
        self._student_repo = student_repo
        self._student_vector_repo = student_vector_repo
        self._upload_service = upload_service
        self._canvas_course_repo = canvas_course_repo
        self._enrollment_repo = enrollment_repo
        self._recognition_history_service = recognition_history_service
        self._canvas_proxy_provider = canvas_proxy_provider()
        self._ml_service = ml_service()

    def list_students(
        self, page=1, page_size=10, order_by="id", asc=True
    ) -> Pagination[student_dto.Read]:
        with self._student_repo.session():
            query = self._student_repo.order_by(order_by=order_by, asc=asc)
            students = self._student_repo.list_paged(
                page=page, page_size=page_size, query=query
            )
            items = [
                student_dto.Read.from_dbmodel(student) for student in students.items
            ]
        return Pagination(
            page=students.page,
            page_size=students.page_size,
            total=students.total,
            items=items,
        )

    def get_student_by_web_id(self, web_id: str) -> student_dto.Read:
        with self._student_repo.session():
            student = self._student_repo.get_by_web_id(web_id=web_id)
        return student_dto.Read.from_dbmodel(student)

    def save_student(self, dto: student_dto.Create) -> student_dto.Read:
        with self._student_repo.session():
            student = Student(
                web_id=shortuuid.uuid(),
                name=dto.name,
                email=dto.email,
                canvas_user_id=dto.canvas_user_id,
            )
            self._student_repo.save_or_update(student)
        return student_dto.Read.from_dbmodel(student)

    def save_student_image(
        self,
        web_id: str,
        name: str,
        content_type: str,
        stream: io.BufferedReader,
    ) -> student_dto.Read:
        with self._student_repo.session():
            student = self._student_repo.get_by_web_id(web_id=web_id)
        if not student:
            raise NotFoundError(message=f"_error_msg_student_not_found: {web_id}")
        upload = self._upload_service.create_upload(
            name=name, content_type=content_type, stream=stream
        )
        # kinda _get_image_embedding
        preprocessed_path = self._ml_service.preprocess_image(file_path=upload.path)
        result = self._ml_service.represent(image_path=preprocessed_path)
        with self._student_vector_repo.session():
            vector = StudentVector(
                student_id=student.id,
                embedding=result.embedding,
                web_id=shortuuid.uuid(),
            )
            self._student_vector_repo.save_or_update(vector)
        return student_dto.Read.from_dbmodel(student)

    # TODO: Add tests
    def search_student_by_image(
        self,
        course_web_id: str,
        name: str,
        content_type: str,
        stream: io.BufferedReader,
    ) -> student_dto.Read:
        start_time = timer()
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=course_web_id)
            if not course:
                raise NotFoundError(
                    message=f"_error_msg_course_not_found: {course_web_id}"
                )
        with self._enrollment_repo.session():
            query = self._enrollment_repo.filter_by_course_id(course_id=course.id)
            # because of this this method always returns enrolled student
            enrollments = self._enrollment_repo.list_all(query=query)
            student_ids = [enrollment.student_id for enrollment in enrollments]
        with self._student_vector_repo.session():
            result = self._get_image_embedding(stream=stream)
            image = self._student_vector_repo.search_course_students_by_embedding(
                embedding=result.embedding, student_ids=student_ids
            )
            end_time = timer()
            recognition_details = recognition_history_dto.RecognitionDetails(
                duration=round(end_time - start_time, 2)
            )
            self._create_recognition_history_record(
                student_id=image.student.id if image else None,
                name=name,
                stream=stream,
                content_type=content_type,
                recognition_details=recognition_details,
            )
            if not image:
                raise NotFoundError(message="_error_msg_student_not_found")
            return student_dto.Read.from_dbmodel(image.student)

    def enroll_student(self, web_id: str, course_web_id: str):
        with self._student_repo.session():
            student = self._student_repo.get_by_web_id(web_id=web_id)
            if not student:
                raise NotFoundError(message=f"_error_msg_student_not_found:{web_id}")
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=course_web_id)
            if not course:
                raise NotFoundError(
                    message=f"_error_msg_course_not_found:{course_web_id}"
                )
        with self._enrollment_repo.session():
            enrollment = self._enrollment_repo.get_by_student_and_course_id(
                student_id=student.id, course_id=course.id
            )
            if enrollment:
                raise InvalidDataError(message="_error_msg_enrollment_already_exists")
        with self._enrollment_repo.session():
            enrollment = Enrollment(
                student_id=student.id, course_id=course.id, web_id=shortuuid.uuid()
            )
            self._enrollment_repo.save_or_update(enrollment)
            return enrollment_dto.Read.from_dbmodel(enrollment)

    def _read_students_from_file(
        self, file_path: str, is_old=True
    ) -> list[student_dto.StudentFile]:
        df = pd.read_excel(file_path, dtype={"Canvas ID": "Int64"})

        def cast_field_to_ndarray(field):
            if isinstance(field, str):
                try:
                    image_vector = field.strip("[]")
                    sep = ","
                    image_vector = np.fromstring(image_vector, sep=sep)
                    return image_vector
                except Exception as e:
                    raise e

        students = []
        for _, row in df.iterrows():
            image_vector512 = cast_field_to_ndarray(row.get("Image Vector512"))

            student = student_dto.StudentFile(
                name=row["Origin Name"],
                origin_name=row["Origin Name"],
                canvas_name=row["Canvas Name"],
                canvas_login=row["Canvas Login"],
                canvas_id=row["Canvas ID"],
                image_id=str(row.get("Image ID")),
                image_vector=image_vector512,
            )
            students.append(student)

        return students

    def load_students_from_excel(
        self, name: str, content_type: str, stream: io.BufferedReader
    ):
        metadata = self._upload_service.create_upload(
            name=name, content_type=content_type, stream=stream
        )
        students: list[student_dto.StudentFile] = self._read_students_from_file(
            file_path=metadata.path
        )
        with self._student_repo.session():
            for file_student in students:
                student = self._student_repo.get_by_canvas_user_id(
                    canvas_user_id=file_student.canvas_id
                )
                if not student:
                    student = Student(
                        web_id=shortuuid.uuid(),
                        name=file_student.canvas_name,
                        email=file_student.canvas_login,
                        canvas_user_id=file_student.canvas_id,
                    )
                    self._student_repo.save_or_update(student)
                vector = self._student_vector_repo.get_by_student_id(
                    student_id=student.id
                )
                if not vector:
                    vector = StudentVector(
                        student_id=student.id,
                        embedding=file_student.image_vector,
                        web_id=shortuuid.uuid(),
                    )
                    self._student_vector_repo.save_or_update(vector)
                else:
                    vector.embedding = file_student.image_vector
                    self._student_vector_repo.save_or_update(vector)
        return True

    def search_by_image(
        self,
        stream: io.BufferedReader,
    ) -> student_dto.Read:
        with self._student_vector_repo.session():
            result = self._get_image_embedding(stream=stream)
            image = self._student_vector_repo.search_by_embedding(
                embedding=result.embedding
            )
            if not image:
                raise NotFoundError(message="_error_msg_student_not_found")
            return student_dto.Read.from_dbmodel(image.student)

    def _get_image_embedding(self, stream) -> RepresentResult:
        with write_to_temp_file(stream=stream) as file_path:
            preprocessed_path = self._ml_service.preprocess_image(file_path=file_path)
            return self._ml_service.represent(image_path=preprocessed_path)

    def _create_recognition_history_record(
        self,
        name: str,
        content_type: str,
        stream: io.BufferedReader,
        recognition_details: recognition_history_dto.RecognitionDetails,
        student_id: int = None,
    ):
        upload = self._upload_service.create_upload(
            name=name, content_type=content_type, stream=stream
        )
        self._recognition_history_service.create_recognition_history(
            dto=recognition_history_dto.Create(
                student_id=student_id,
                image_file=upload,
                recognition_details=recognition_details,
            )
        )
