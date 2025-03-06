from typing import Optional

from pydantic import BaseModel, Field


class FilterParams(BaseModel):
    canvas_user_id: Optional[int] = None


class Read(BaseModel):
    long_name: str = Field(None, validation_alias="longName")
    short_name: str = Field(None, validation_alias="shortName")
    original_name: str = Field(None, validation_alias="originalName")
    course_code: str = Field(None, validation_alias="courseCode")
    course_id: int = Field(None, validation_alias="id")

    class Config:
        populate_by_name = True
        alias_generator = None

    @classmethod
    def from_dict(cls, item):
        return cls(**item)

    @classmethod
    def from_dbmodel(cls, item):
        return cls(
            long_name=item.long_name,
            short_name=item.short_name,
            original_name=item.original_name,
            course_code=item.course_code,
            course_id=item.canvas_course_id,
        )


class ListRead(Read):
    web_id: str
    owner_username: str

    @classmethod
    def from_dbmodel(cls, item):
        return cls(
            owner_username=item.canvas_user.username,
            web_id=item.web_id,
            long_name=item.long_name,
            short_name=item.short_name,
            original_name=item.original_name,
            course_code=item.course_code,
            course_id=item.canvas_course_id,
        )


class LoadCourse(BaseModel):
    user_id: int


class CourseLink(BaseModel):
    css_class: str
    icon: str
    hidden: Optional[bool] = None
    path: str
    label: str
