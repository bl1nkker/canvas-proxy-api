from fastapi import FastAPI
from pyinstrument import Profiler
from pyinstrument.renderers.html import HTMLRenderer
from pyinstrument.renderers.speedscope import SpeedscopeRenderer
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app_config import get_app_config


class ProfilerMiddleware(BaseHTTPMiddleware):

    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        app_config = get_app_config()
        if app_config.profiling_enabled:
            profile_type_to_ext = {"html": "html", "speedscope": "speedscope.json"}
            profile_type_to_renderer = {
                "html": HTMLRenderer,
                "speedscope": SpeedscopeRenderer,
            }
            if request.query_params.get("profile", False):
                profile_type = request.query_params.get("profile_format", "html")
                with Profiler(interval=0.001, async_mode="enabled") as profiler:
                    response = await call_next(request)
                extension = profile_type_to_ext[profile_type]
                renderer = profile_type_to_renderer[profile_type]()
                with open(f"_profiles/profile.{extension}", "w") as out:
                    out.write(profiler.output(renderer=renderer))
                return response
        else:
            return await call_next(request)
