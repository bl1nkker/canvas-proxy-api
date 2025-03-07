from pydantic import BaseModel, Field


class ReadCanvasUser(BaseModel):
    web_id: str
    canvas_id: int
    username: str

    @classmethod
    def from_dbmodel(cls, item):
        return cls(
            web_id=item.web_id,
            canvas_id=item.canvas_id,
            username=item.username,
        )


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
    canvas_user: ReadCanvasUser

    @classmethod
    def from_dbmodel(cls, item):
        return cls(
            username=item.username,
            web_id=item.web_id,
            canvas_user=ReadCanvasUser.from_dbmodel(item.canvas_user),
        )
