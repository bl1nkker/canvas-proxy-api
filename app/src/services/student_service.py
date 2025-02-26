import shortuuid

from db.data_repo import Pagination
from src.repositories.student_repo import StudentRepo
from src.repositories.student_vector_repo import StudentVectorRepo
from src.models.student import Student
from src.dto import student_dto


class StudentService:
    def __init__(
        self, student_repo: StudentRepo, student_vector_repo: StudentVectorRepo
    ):
        self._student_repo = student_repo
        self._student_vector_repo = student_vector_repo

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

    def save_student_vector(self):
        pass
