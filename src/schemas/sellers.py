from pydantic import BaseModel, Field, field_validator, EmailStr
from pydantic_core import PydanticCustomError
from typing import List
from .books import ReturnedBook

__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedAllSellers"]



class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str
    
    @field_validator("password")  # Валидатор, проверяет что пароль не слишком короткий и содержит цифры и заглавные буквы
    @staticmethod
    def validate_password(val: str):
        if len(val) < 8:
            raise PydanticCustomError("Validation error", "Password is too short!")
        
        if not any(char.isdigit() for char in val):
            raise PydanticCustomError("Validation error", "Password must contain at least one digit!")
        
        if not any(char.isupper() for char in val):
            raise PydanticCustomError("Validation error", "Password must contain at least one uppercase letter!")

        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int
    # books: list[ReturnedBook] = Field(default=[])  # При создании у продавца пока нет книг


# Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
