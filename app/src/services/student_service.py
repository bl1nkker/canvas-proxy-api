import io

import numpy as np
import pandas as pd
import shortuuid

from db.data_repo import Pagination
from ml import face_encoder
from src.dto import auth_dto, enrollment_dto, student_dto
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
from src.services.upload_service import UploadService


class StudentService:

    def __init__(
        self,
        student_repo: StudentRepo,
        enrollment_repo: EnrollmentRepo,
        canvas_course_repo: CanvasCourseRepo,
        student_vector_repo: StudentVectorRepo,
        upload_service: UploadService,
        canvas_proxy_provider=CanvasProxyProvider,
    ):
        self._student_repo = student_repo
        self._student_vector_repo = student_vector_repo
        self._upload_service = upload_service
        self._canvas_course_repo = canvas_course_repo
        self._enrollment_repo = enrollment_repo
        self._canvas_proxy_provider = canvas_proxy_provider()

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

    async def load_students(
        self, course_web_id: str, canvas_auth_data: auth_dto.CanvasAuthData
    ) -> list[student_dto.Read]:
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=course_web_id)
        if not course:
            raise NotFoundError(message=f"_error_msg_course_not_found:{course_web_id}")
        course_students = await self._canvas_proxy_provider.get_course_students(
            canvas_course_id=course.canvas_course_id, cookies=canvas_auth_data
        )
        students = []
        with self._student_repo.session():
            for student in course_students:
                student_db = self._student_repo.get_by_canvas_user_id(
                    canvas_user_id=student.canvas_user_id
                )
                if not student_db:
                    student_db = Student(
                        web_id=shortuuid.uuid(),
                        name=student.name,
                        email=student.email,
                        canvas_user_id=student.canvas_user_id,
                    )
                    self._student_repo.save_or_update(student_db)
                students.append(student_db)

        for student in students:
            try:
                self.enroll_student(web_id=student.web_id, course_web_id=course_web_id)
            except InvalidDataError:
                # if student enrollment already exists
                pass

        return [student_dto.Read.from_dbmodel(student) for student in students]

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
        metadata = self._upload_service.create_upload(
            name=name, content_type=content_type, stream=stream
        )
        image_embed = face_encoder.get_image_embedding(
            image_path=metadata.path, content_type=metadata.content_type
        )
        with self._student_vector_repo.session():
            vector = StudentVector(
                student_id=student.id, embedding=image_embed, web_id=shortuuid.uuid()
            )
            self._student_vector_repo.save_or_update(vector)
        return student_dto.Read.from_dbmodel(student)

    # TODO: Add tests
    def search_student_by_image(
        self,
        course_web_id: str,
        stream: io.BufferedReader,
    ) -> student_dto.Read:
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=course_web_id)
            if not course:
                raise NotFoundError(
                    message=f"_error_msg_course_not_found: {course_web_id}"
                )
        with self._enrollment_repo.session():
            query = self._enrollment_repo.filter_by_course_id(course_id=course.id)
            enrollments = self._enrollment_repo.list_all(query=query)
            student_ids = [enrollment.student_id for enrollment in enrollments]
        with write_to_temp_file(stream=stream) as file_path:
            image_embed = face_encoder.get_image_embedding(image_path=file_path)
        with self._student_vector_repo.session():
            image = self._student_vector_repo.search_by_embedding(
                embedding=image_embed, student_ids=student_ids
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

    def _read_students_from_file(self, file_path: str) -> list[student_dto.StudentFile]:
        df = pd.read_excel(file_path, dtype={"Canvas ID": "Int64"})

        students = []
        for _, row in df.iterrows():
            image_vector = row.get("Image Vector")
            if isinstance(image_vector, str):
                try:
                    image_vector = image_vector.strip("[]")
                    image_vector = np.fromstring(image_vector, sep=" ")
                except Exception as e:
                    raise e

            student = student_dto.StudentFile(
                name=row["Origin Name"],
                origin_name=row["Origin Name"],
                canvas_name=row["Canvas Name"],
                canvas_login=row["Canvas Login"],
                canvas_id=row["Canvas ID"],
                image_id=row.get("Image ID"),
                image_vector=image_vector,
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
                student = Student(
                    web_id=shortuuid.uuid(),
                    name=file_student.canvas_name,
                    email=file_student.canvas_login,
                    canvas_user_id=file_student.canvas_id,
                )
                self._student_repo.save_or_update(student)
                vector = StudentVector(
                    student_id=student.id,
                    embedding=file_student.image_vector,
                    web_id=shortuuid.uuid(),
                )
                self._student_vector_repo.save_or_update(vector)
        return True
