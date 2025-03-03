import shortuuid

from db.data_repo import Pagination
from src.dto import canvas_course_dto
from src.models.canvas_course import CanvasCourse
from src.proxies.canvas_proxy_provider import CanvasProxyProvider
from src.repositories.canvas_course_repo import CanvasCourseRepo
from src.repositories.canvas_user_repo import CanvasUserRepo


class CanvasCourseService:
    def __init__(
        self,
        canvas_course_repo: CanvasCourseRepo,
        canvas_user_repo: CanvasUserRepo,
        canvas_proxy_provider_cls=CanvasProxyProvider,
    ):
        self._canvas_course_repo = canvas_course_repo
        self._canvas_user_repo = canvas_user_repo
        self._canvas_proxy_provider = canvas_proxy_provider_cls()

    def _set_canvas_course_filter_params(
        self, query, filter_params: canvas_course_dto.FilterParams
    ):
        if filter_params.canvas_user_id:
            query = self._canvas_course_repo.filter_by_canvas_user_id(
                filter_params.canvas_user_id, query=query
            )
        return query

    def list_courses(
        self,
        page=1,
        page_size=10,
        order_by="id",
        asc=True,
        filter_params: canvas_course_dto.FilterParams = None,
    ) -> Pagination[canvas_course_dto.ListRead]:
        with self._canvas_course_repo.session():
            query = self._canvas_course_repo.order_by(order_by=order_by, asc=asc)
            if filter_params is not None:
                query = self._set_canvas_course_filter_params(query, filter_params)
            courses = self._canvas_course_repo.list_paged(
                page=page, page_size=page_size, query=query
            )
        return Pagination(
            page=courses.page,
            page_size=courses.page_size,
            total=courses.total,
            items=[
                canvas_course_dto.ListRead.from_dbmodel(course)
                for course in courses.items
            ],
        )

    async def load_courses(
        self, dto: canvas_course_dto.LoadCourse
    ) -> canvas_course_dto.ListRead:
        canvas_courses: list[canvas_course_dto.Read] = (
            await self._canvas_proxy_provider.get_courses(dto.canvas_auth_data)
        )
        created_courses = []
        with self._canvas_course_repo.session():
            for course in canvas_courses:
                # check if course already exists
                existing_course = self._canvas_course_repo.get_by_canvas_course_id(
                    canvas_course_id=course.course_id
                )
                if existing_course is not None:
                    continue
                canvas_course = CanvasCourse(
                    web_id=shortuuid.uuid(),
                    long_name=course.long_name,
                    short_name=course.short_name,
                    original_name=course.original_name,
                    course_code=course.course_code,
                    canvas_course_id=course.course_id,
                    canvas_user_id=dto.canvas_user_id,
                )
                created_courses.append(
                    self._canvas_course_repo.save_or_update(canvas_course)
                )
        return [
            canvas_course_dto.ListRead.from_dbmodel(course)
            for course in created_courses
        ]
