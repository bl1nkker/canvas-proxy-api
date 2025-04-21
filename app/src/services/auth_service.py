import shortuuid

from src.dto import auth_dto
from src.errors.types import InvalidCredentialsError, InvalidDataError, NotFoundError
from src.models import CanvasUser, User
from src.proxies.canvas_proxy_provider import CanvasProxyProvider
from src.repositories.canvas_user_repo import CanvasUserRepo
from src.repositories.user_repo import UserRepo
from src.services.source_data_load_queue_service import SourceDataLoadQueueService


class AuthService:
    def __init__(
        self,
        user_repo: UserRepo,
        canvas_user_repo: CanvasUserRepo,
        source_data_load_queue_service: SourceDataLoadQueueService,
        canvas_proxy_provider_cls=CanvasProxyProvider,
    ):
        self._user_repo = user_repo
        self._canvas_user_repo = canvas_user_repo
        self._source_data_load_queue_service = source_data_load_queue_service
        self._canvas_proxy_provider = canvas_proxy_provider_cls()

    async def create_user(
        self, dto: auth_dto.Signup
    ) -> tuple[auth_dto.UserData, auth_dto.CanvasAuthData]:
        with self._user_repo.session():
            user = self._create_user(dto=dto)

            # TODO: IMPROVE USER CHECK BEFORE CREATING AND TEST
            auth_data = await self._get_canvas_auth_data(
                username=dto.username, password=dto.password
            )

            self._create_canvas_user(
                user_id=user.id,
                password=dto.password,
                username=dto.username,
                canvas_user_id=user.id,
            )
            self._source_data_load_queue_service.load_canvas_data(user_id=user.id)
            return auth_dto.UserData.from_dbmodel(user), auth_data

    async def signin(
        self, dto: auth_dto.LoginRequest
    ) -> tuple[auth_dto.UserData, auth_dto.CanvasAuthData]:
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

        auth_data = await self._get_canvas_auth_data(
            username=canvas_user.username, password=canvas_user.password
        )
        return (
            auth_dto.UserData.from_dbmodel(user),
            auth_data,
        )

    def _create_user(self, dto: auth_dto.Signup) -> User:
        with self._user_repo.session():
            user = self._user_repo.get_by_username(username=dto.username)
            if user is not None:
                raise InvalidDataError(
                    message=f"_error_msg_user_with_username_already_exists:{dto.username}"
                )
            user = User(username=dto.username, web_id=shortuuid.uuid())
            user.set_password(password=dto.password)
            return self._user_repo.save_or_update(user)

    def _create_canvas_user(
        self, user_id: int, password: str, username: str, canvas_user_id: int
    ) -> CanvasUser:
        with self._canvas_user_repo.session():
            canvas_user = CanvasUser(
                user_id=user_id,
                web_id=shortuuid.uuid(),
                username=username,
                canvas_id=canvas_user_id,
            )
            canvas_user.set_password(password=password)
            return self._canvas_user_repo.save_or_update(canvas_user)

    async def _get_canvas_auth_data(
        self, username: str, password: str
    ) -> auth_dto.CanvasAuthData:
        auth_data = await self._canvas_proxy_provider.get_auth_data(
            username=username, password=password
        )

        if not auth_data:
            raise NotFoundError(message=f"_error_msg_canvas_user_not_found:{username}")
        return auth_data
