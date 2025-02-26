from pydantic import BaseModel


class Create(BaseModel):
    firstname: str
    lastname: str
    email: str


class Read(BaseModel):
    firstname: str
    lastname: str
    email: str
    web_id: str

    @classmethod
    def from_dbmodel(cls, item):
        return cls(
            firstname=item.firstname,
            lastname=item.lastname,
            email=item.email,
            web_id=item.web_id,
        )
