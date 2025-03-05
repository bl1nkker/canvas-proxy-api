from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class CanvasAuthData(BaseModel):
    csrf_token: str = Field(alias="_csrf_token")
    legacy_normandy_session: str = Field(alias="_legacy_normandy_session")
    normandy_session: str = Field(alias="_normandy_session")
    log_session_id: str

    class Config:
        allow_population_by_field_name = True


class UserData(BaseModel):
    username: str
    web_id: str
    id: int
    canvas_auth_data: CanvasAuthData | None
