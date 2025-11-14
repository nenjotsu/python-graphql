from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    password: str
