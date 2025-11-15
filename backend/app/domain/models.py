from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    name: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Input model for updating users - all fields optional"""

    name: Optional[str] = None
    password: Optional[str] = None
