from typing import Optional
from pydantic import BaseModel, Field

__all__ = ["Token", "TokenData", "AuthUser", "SuccessfulResponse"]

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    login: Optional[str] = None


class AuthUser(BaseModel):
    e_mail: str = Field(..., max_length=30)
    password: str = Field(..., min_length=8)


class SuccessfulResponse(BaseModel):
    details: str = Field("Выполнено", title="Статус операции")


