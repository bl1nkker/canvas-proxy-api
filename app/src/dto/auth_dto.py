from pydantic import BaseModel, Field


class Signup(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class CanvasAuthData(BaseModel):
    csrf_token: str = Field(alias="_csrf_token")
    legacy_normandy_session: str = Field(alias="_legacy_normandy_session")
    normandy_session: str = Field(alias="_normandy_session")
    log_session_id: str


class UserData(BaseModel):
    username: str
    web_id: str
