from pydantic import BaseModel


class BaseRecord(BaseModel):
    name: str
    size: int
    content_type: str


class Read(BaseRecord):
    web_id: str


class Metadata(Read):
    path: str


class CreateMetadata(BaseModel):
    name: str
    file_name: str
    content_type: str
