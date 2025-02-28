from pydantic import BaseModel, Field


class LoginCredentials(BaseModel):
    username: str
    password: str


class LoginCookies(BaseModel):
    csrf_token: str = Field(None, alias="_csrf_token")
    legacy_normandy_session: str = Field(None, alias="_legacy_normandy_session")
    normandy_session: str = Field(None, alias="_normandy_session")
    log_session_id: str

    class Config:
        allow_population_by_field_name = True
