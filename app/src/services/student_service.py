import io
import shortuuid

from db.data_repo import Pagination
from ml import face_encoder
from src.errors.types import NotFoundError
from src.models.student_vector import StudentVector
from src.services.upload_service import UploadService
from src.repositories.student_repo import StudentRepo
from src.repositories.student_vector_repo import StudentVectorRepo
from src.models.student import Student
from src.dto import student_dto


class StudentService:

    def __init__(
        self,
        student_repo: StudentRepo,
        student_vector_repo: StudentVectorRepo,
        upload_service: UploadService,
    ):
        self._student_repo = student_repo
        self._student_vector_repo = student_vector_repo
        self._upload_service = upload_service

    def list_students(
        self, page=1, page_size=10, order_by="id", asc=True
    ) -> Pagination[student_dto.Read]:
        with self._student_repo.session():
            query = self._student_repo.order_by(order_by=order_by, asc=asc)
            students = self._student_repo.list_paged(
                page=page, page_size=page_size, query=query
            )
        return Pagination(
            page=students.page,
            page_size=students.page_size,
            total=students.total,
            items=[
                student_dto.Read.from_dbmodel(student) for student in students.items
            ],
        )

    def get_student_by_web_id(self, web_id: str) -> student_dto.Read:
        with self._student_repo.session():
            student = self._student_repo.get_by_web_id(web_id=web_id)
        return student_dto.Read.from_dbmodel(student)

    def save_student(self, dto: student_dto.Create) -> student_dto.Read:
        with self._student_repo.session():
            student = Student(
                web_id=shortuuid.uuid(),
                firstname=dto.firstname,
                lastname=dto.lastname,
                email=dto.email,
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

    def search_student_by_image(
        self, name: str, content_type: str, stream: io.BufferedReader
    ) -> student_dto.Read:
        metadata = self._upload_service.create_upload(
            name=name, content_type=content_type, stream=stream
        )
        image_embed = face_encoder.get_image_embedding(
            image_path=metadata.path, content_type=metadata.content_type
        )
        with self._student_vector_repo.session():
            image = self._student_vector_repo.search_by_embedding(embedding=image_embed)
        if not image:
            raise NotFoundError(message="_error_msg_student_not_found")
        with self._student_repo.session():
            student = self._student_repo.get_by_db_id(db_id=image.student_id)
        return student_dto.Read.from_dbmodel(student)
