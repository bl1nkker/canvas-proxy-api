import shortuuid

from src.dto import auth_dto
from src.errors.types import InvalidCredentialsError, InvalidDataError, NotFoundError
from src.models import CanvasUser, User
from src.proxies.canvas_proxy_provider import CanvasProxyProvider
from src.repositories.canvas_user_repo import CanvasUserRepo
from src.repositories.user_repo import UserRepo


class AuthService:
    def __init__(
        self,
        user_repo: UserRepo,
        canvas_user_repo: CanvasUserRepo,
        canvas_proxy_provider_cls=CanvasProxyProvider,
    ):
        self._user_repo = user_repo
        self._canvas_user_repo = canvas_user_repo
        self._canvas_proxy_provider = canvas_proxy_provider_cls()

    async def create_user(self, dto: auth_dto.LoginRequest) -> auth_dto.UserData:
        with self._user_repo.session():
            user = self._user_repo.get_by_username(username=dto.username)
            if user is not None:
                raise InvalidDataError(
                    message=f"_error_msg_user_with_username_already_exists:{dto.username}"
                )
            user = User(username=dto.username, web_id=shortuuid.uuid())
            user.set_password(password=dto.password)
            user = self._user_repo.save_or_update(user)

        # check if user exists inside Canvas
        auth_data = await self._canvas_proxy_provider.get_auth_data(
            username=dto.username, password=dto.password
        )

        if not auth_data:
            raise NotFoundError(
                message=f"_error_msg_canvas_user_not_found:{user.username}"
            )

        with self._canvas_user_repo.session():
            canvas_user = CanvasUser(
                user_id=user.id,
                web_id=shortuuid.uuid(),
                username=dto.username,
                canvas_id=user.id,
            )
            canvas_user.set_password(password=dto.password)
            self._canvas_user_repo.save_or_update(canvas_user)
        return auth_dto.UserData(
            username=user.username, web_id=user.web_id, canvas_auth_data=auth_data
        )

    async def get_canvas_auth_data(
        self, dto: auth_dto.LoginRequest
    ) -> auth_dto.UserData:
        with self._user_repo.session():
            user = self._user_repo.get_by_username(username=dto.username)
            if not user or not user.check_password(dto.password):
                raise InvalidCredentialsError()

        with self._canvas_user_repo.session():
            canvas_user = self._canvas_user_repo.get_by_user_id(user_id=user.id)
            if not canvas_user:
                raise NotFoundError(
                    message=f"_error_msg_canvas_user_not_found:{user.username}"
                )

        auth_data: auth_dto.CanvasAuthData = (
            await self._canvas_proxy_provider.get_auth_data(
                username=canvas_user.username, password=canvas_user.password
            )
        )
        return auth_dto.UserData(
            username=user.username, web_id=user.web_id, canvas_auth_data=auth_data
        )

    # async def get_courses(self, dto: auth_dto.LoginRequest) -> canvas_dto.Course:
    #     courses = await self._canvas_proxy_provider.get_courses(cookies=dto)
    #     return courses
